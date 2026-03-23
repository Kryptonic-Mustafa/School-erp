import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  try {
    const students = await db.student.findMany({
      include: { embeddings: true }
    });
    // Format for face-api.js LabeledFaceDescriptors
    const labeledData = students.filter(s => s.embeddings.length > 0).map(s => ({
      label: `${s.id}|${s.name}`,
      descriptors: s.embeddings.map(e => e.vectorData)
    }));
    return NextResponse.json({ success: true, data: labeledData });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to sync vectors' }, { status: 500 });
  }
}
