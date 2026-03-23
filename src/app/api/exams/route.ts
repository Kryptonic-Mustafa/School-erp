import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  const exams = await db.exam.findMany({ include: { subject: { include: { class: true } }, _count: { select: { grades: true } } }, orderBy: { date: 'desc' } });
  return NextResponse.json({ success: true, exams });
}

export async function POST(req: Request) {
  try {
    const { title, date, subjectId } = await req.json();
    const exam = await db.exam.create({ data: { title, date: new Date(date), subjectId } });
    return NextResponse.json({ success: true, exam });
  } catch (error) { return NextResponse.json({ error: 'Exam creation failed.' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.grade.deleteMany({ where: { examId: id! } }); // Cascade delete grades
    await db.exam.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Deletion failed' }, { status: 500 }); }
}
