import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';
import bcrypt from 'bcryptjs';

export async function GET() {
  try {
    const teachers = await db.teacher.findMany({
      include: {
        user: { select: { email: true } },
        classes: { select: { name: true } }
      },
      orderBy: { name: 'asc' }
    });
    return NextResponse.json({ success: true, teachers });
  } catch (error) {
    return NextResponse.json({ error: 'FAILED_TO_FETCH' }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { name, email, password } = await req.json();

    // Check if email already exists
    const existingUser = await db.user.findUnique({ where: { email } });
    if (existingUser) {
      return NextResponse.json({ error: 'Email already assigned to an entity.' }, { status: 400 });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await db.user.create({
      data: { email, password: hashedPassword, role: 'TEACHER' }
    });

    const teacher = await db.teacher.create({
      data: { userId: user.id, name }
    });

    return NextResponse.json({ success: true, teacher });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'TEACHER_CREATION_FAILED' }, { status: 500 });
  }
}

export async function PATCH(req: Request) {
  try {
    const { id, name } = await req.json();
    await db.teacher.update({
      where: { id },
      data: { name }
    });
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'UPDATE_FAILED' }, { status: 500 });
  }
}

export async function DELETE(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const id = searchParams.get('id');
    
    if (!id) return NextResponse.json({ error: 'MISSING_TEACHER_ID' }, { status: 400 });

    const teacher = await db.teacher.findUnique({ where: { id }, include: { classes: true } });
    if (!teacher) return NextResponse.json({ error: 'TEACHER_NOT_FOUND' }, { status: 404 });

    // Relational Safety Constraint
    if (teacher.classes.length > 0) {
      return NextResponse.json({ 
        error: `Cannot delete ${teacher.name}. They are assigned to ${teacher.classes.length} active class(es). Reassign the classes first.` 
      }, { status: 400 });
    }

    await db.teacher.delete({ where: { id } });
    await db.user.delete({ where: { id: teacher.userId } });

    return NextResponse.json({ success: true, message: 'Teacher purged from matrix.' });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'DELETION_FAILED' }, { status: 500 });
  }
}
