import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';
import bcrypt from 'bcryptjs';

export async function GET() {
  try {
    const students = await db.student.findMany({
      include: {
        user: { select: { email: true } },
        classes: { select: { id: true, name: true } }
      },
      orderBy: { name: 'asc' }
    });
    return NextResponse.json({ success: true, students });
  } catch (error) { return NextResponse.json({ error: 'FAILED_TO_FETCH' }, { status: 500 }); }
}

export async function POST(req: Request) {
  try {
    const { name, email, password, classIds } = await req.json();

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await db.user.create({ data: { email, password: hashedPassword, role: 'STUDENT' } });

    const student = await db.student.create({ 
      data: { 
        userId: user.id, 
        name, 
        classes: { connect: (classIds || []).map((id: string) => ({ id })) } 
      } 
    });

    return NextResponse.json({ success: true, student });
  } catch (error) { return NextResponse.json({ error: 'CREATION_FAILED' }, { status: 500 }); }
}

export async function PATCH(req: Request) {
  try {
    const { id, name, classIds } = await req.json();
    await db.student.update({ 
      where: { id }, 
      data: { 
        name, 
        classes: { set: (classIds || []).map((id: string) => ({ id })) } 
      } 
    });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'UPDATE_FAILED' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    const student = await db.student.findUnique({ where: { id: id! } });
    if (!student) return NextResponse.json({ error: 'NOT_FOUND' }, { status: 404 });

    await db.faceEmbedding.deleteMany({ where: { studentId: id! } });
    await db.attendance.deleteMany({ where: { studentId: id! } });
    await db.student.delete({ where: { id: id! } });
    await db.user.delete({ where: { id: student.userId } });

    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'DELETION_FAILED' }, { status: 500 }); }
}
