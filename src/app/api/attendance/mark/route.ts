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
