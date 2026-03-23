import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';
import bcrypt from 'bcryptjs';

export async function GET() {
  const users = await db.user.findMany({ 
    where: { role: { not: 'STUDENT' } },
    include: { accessRole: true },
    orderBy: { createdAt: 'desc' }
  });
  return NextResponse.json({ success: true, users });
}

export async function POST(req: Request) {
  try {
    const { email, password, roleType, accessRoleId } = await req.json();
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await db.user.create({
      data: { email, password: hashedPassword, role: roleType, accessRoleId: accessRoleId || null }
    });
    return NextResponse.json({ success: true, user });
  } catch (error) { return NextResponse.json({ error: 'User creation failed' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.user.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Deletion failed' }, { status: 500 }); }
}
