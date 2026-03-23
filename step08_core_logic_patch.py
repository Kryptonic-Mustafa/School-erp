import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Patched: {path}")

def step08_deploy():
    print("====================================================")
    print("   M.A.C.DevOS PATCH: CORE LOGIC & SILENT OPTICS    ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> DEPLOYING MISSING ATTENDANCE API KERNEL...")

    # 1. INJECT MISSING ATTENDANCE API ROUTE
    attendance_api_ts = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';
import { cosineSimilarity } from '@/lib/face_service';
import { decryptPayload } from '@/lib/crypto_engine';

export async function POST(req: Request) {
  try {
    const { encryptedData } = await req.json();
    
    // Decrypt the payload
    const rawData = decryptPayload(encryptedData);
    const { capturedEmbedding } = JSON.parse(rawData);

    // Fetch all embedded vectors from the matrix
    const students = await db.student.findMany({
      include: { embeddings: true }
    });

    let matchedStudentId = null;
    let maxConfidence = 0;

    // Vector Matching Neural Engine (Cosine Similarity)
    for (const student of students) {
      for (const record of student.embeddings) {
        const storedVector = record.vectorData as number[];
        const score = cosineSimilarity(capturedEmbedding, storedVector);
        
        // 0.93 is a strict threshold for Cosine Similarity with face-api.js 128D vectors
        if (score > 0.93 && score > maxConfidence) {
          maxConfidence = score;
          matchedStudentId = student.id;
        }
      }
    }

    if (!matchedStudentId) {
      return NextResponse.json({ error: 'UNKNOWN_ENTITY: Face not recognized in matrix.' }, { status: 401 });
    }

    // Check if already logged today to prevent duplicate records
    const startOfDay = new Date();
    startOfDay.setHours(0, 0, 0, 0);

    const existing = await db.attendance.findFirst({
      where: {
        studentId: matchedStudentId,
        date: { gte: startOfDay }
      }
    });

    if (existing) {
      return NextResponse.json({ message: 'SUBJECT_ALREADY_LOGGED_TODAY' }, { status: 200 });
    }

    // Write to Database
    await db.attendance.create({
      data: {
        studentId: matchedStudentId,
        status: 'PRESENT',
        confidence: maxConfidence
      }
    });

    return NextResponse.json({ success: true, message: 'ATTENDANCE_VERIFIED' });

  } catch (error) {
    console.error('[System Error] Attendance Scan:', error);
    return NextResponse.json({ error: 'SYSTEM_ERROR_DURING_SCAN' }, { status: 500 });
  }
}
    """
    create_file(os.path.join(project_dir, "src/app/api/attendance/mark/route.ts"), attendance_api_ts)

    print("\n>>> PATCHING UI GHOST TOASTS (SILENT UNMOUNT)...")

    # 2. PATCH BIOMETRIC REGISTRY TOAST
    register_path = os.path.join(project_dir, "src/app/admin/face-register/page.tsx")
    if os.path.exists(register_path):
        with open(register_path, "r", encoding="utf-8") as f:
            reg_content = f.read()
        
        reg_content = reg_content.replace(
            "const terminateOptics = useCallback(() => {", 
            "const terminateOptics = useCallback((showToast = true) => {"
        )
        reg_content = reg_content.replace(
            "osToast.fire({ icon: 'info', title: 'Optics Terminated' });",
            "if (showToast) osToast.fire({ icon: 'info', title: 'Optics Terminated' });"
        )
        reg_content = reg_content.replace(
            "return () => {\n      terminateOptics();\n    };",
            "return () => {\n      terminateOptics(false);\n    };"
        )
        reg_content = reg_content.replace(
            "onClick={terminateOptics}",
            "onClick={() => terminateOptics(true)}"
        )
        create_file(register_path, reg_content)

    # 3. PATCH ATTENDANCE SCANNER TOAST
    attendance_path = os.path.join(project_dir, "src/app/attendance/page.tsx")
    if os.path.exists(attendance_path):
        with open(attendance_path, "r", encoding="utf-8") as f:
            att_content = f.read()
        
        att_content = att_content.replace(
            "const terminateOptics = useCallback(() => {", 
            "const terminateOptics = useCallback((showToast = true) => {"
        )
        att_content = att_content.replace(
            "setStatus('READY');",
            "setStatus('READY');\n    if (showToast) osToast.fire({ icon: 'info', title: 'Optics Terminated' });"
        )
        att_content = att_content.replace(
            "return () => terminateOptics();",
            "return () => terminateOptics(false);"
        )
        att_content = att_content.replace(
            "terminateOptics();\n      return;",
            "terminateOptics(true);\n      return;"
        )
        create_file(attendance_path, att_content)

    print("\n====================================================")
    print(" [SUCCESS] CORE LOGIC & UI PATCH DEPLOYED.          ")
    print("====================================================\n")

if __name__ == "__main__":
    step08_deploy()