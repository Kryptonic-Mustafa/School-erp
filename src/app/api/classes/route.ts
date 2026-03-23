import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';
import bcrypt from 'bcryptjs';

export async function GET() {
  const classes = await db.class.findMany({ include: { teacher: true, _count: { select: { students: true } } } });
  return NextResponse.json({ success: true, classes });
}

export async function POST(req: Request) {
  try {
    const { name } = await req.json();
    let defaultTeacher = await db.teacher.findFirst({ where: { name: 'System Auto-Teacher' } });
    if (!defaultTeacher) {
      const tUser = await db.user.create({ data: { email: `system.teacher.${Date.now()}@school.os`, password: await bcrypt.hash('teacher123', 10), role: 'TEACHER' } });
      defaultTeacher = await db.teacher.create({ data: { userId: tUser.id, name: 'System Auto-Teacher' } });
    }
    const newClass = await db.class.create({ data: { name, teacherId: defaultTeacher.id } });
    return NextResponse.json({ success: true, class: newClass });
  } catch (error) { return NextResponse.json({ error: 'Class creation failed' }, { status: 500 }); }
}

export async function PATCH(req: Request) {
  try {
    const { classIds, teacherId } = await req.json();
    
    if (!Array.isArray(classIds) || classIds.length === 0) {
      return NextResponse.json({ error: 'No classes selected.' }, { status: 400 });
    }

    // Batch Update Multiple Classes to the new Teacher
    await db.class.updateMany({
      where: { id: { in: classIds } },
      data: { teacherId }
    });

    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Batch assignment failed' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.class.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Cannot delete class with active students' }, { status: 500 }); }
}
