import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  const subjects = await db.subject.findMany({ include: { class: true, teacher: true, _count: { select: { exams: true } } } });
  return NextResponse.json({ success: true, subjects });
}

export async function POST(req: Request) {
  try {
    const { name, code, classId, teacherId } = await req.json();
    const subject = await db.subject.create({ data: { name, code, classId, teacherId } });
    return NextResponse.json({ success: true, subject });
  } catch (error) { return NextResponse.json({ error: 'Subject creation failed. Code must be unique.' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.subject.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Cannot delete subject with active exams' }, { status: 500 }); }
}
