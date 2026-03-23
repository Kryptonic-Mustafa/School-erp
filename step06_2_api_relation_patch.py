import os
import sys

PROJECT_NAME = "school-os"

def apply_patch():
    print("====================================================")
    print("   M.A.C.DevOS PATCH: RELATIONAL INTEGRITY FIX      ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    api_path = os.path.join(project_dir, "src/app/api/face/register/route.ts")

    correct_api = """import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function POST(req: Request) {
  try {
    const { studentId, vectorData } = await req.json();

    if (!studentId || !vectorData || !Array.isArray(vectorData)) {
      return NextResponse.json({ error: 'INVALID_PAYLOAD' }, { status: 400 });
    }

    // 1. Fetch the Student to get their underlying User ID
    const student = await db.student.findUnique({
      where: { id: studentId }
    });

    if (!student) {
      return NextResponse.json({ error: 'STUDENT_NOT_FOUND' }, { status: 404 });
    }

    // 2. Write the Mathematical Vector to the Database
    const embedding = await db.faceEmbedding.create({
      data: {
        studentId,
        vectorData,
      }
    });

    // 3. Log the Action using the correct User ID to satisfy Prisma constraints
    await db.auditLog.create({
      data: {
        action: 'FACE_REGISTERED',
        userId: student.userId, 
      }
    });

    return NextResponse.json({ success: true, embeddingId: embedding.id });
  } catch (error) {
    console.error('[System Error] Face Registration:', error);
    return NextResponse.json({ error: 'DATA_WRITE_FAILED' }, { status: 500 });
  }
}
"""
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(correct_api)

    print("\n[+] API Route logic updated to satisfy TiDB foreign key constraints.")
    print("[SUCCESS] Relational Integrity Restored.")
    print("====================================================\n")

if __name__ == "__main__":
    apply_patch()