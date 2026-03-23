import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  const roles = await db.accessRole.findMany({ include: { _count: { select: { users: true } } } });
  return NextResponse.json({ success: true, roles });
}

export async function POST(req: Request) {
  try {
    const { name, permissions } = await req.json();
    const role = await db.accessRole.create({ data: { name, permissions } });
    return NextResponse.json({ success: true, role });
  } catch (error) { return NextResponse.json({ error: 'Failed to create role' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.accessRole.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Cannot delete role in use' }, { status: 500 }); }
}
