import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const month = parseInt(searchParams.get('month') || (new Date().getMonth() + 1).toString());
    const year = parseInt(searchParams.get('year') || new Date().getFullYear().toString());

    const startDate = new Date(year, month - 1, 1);
    const endDate = new Date(year, month, 0, 23, 59, 59);

    const students = await db.student.findMany({
      include: {
        classes: true,
        attendances: {
          where: { date: { gte: startDate, lte: endDate } }
        }
      },
      orderBy: { name: 'asc' }
    });

    return NextResponse.json({ success: true, students });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch attendance' }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { studentId, date, status } = await req.json(); // status: 'P', 'A', 'L'
    
    const targetDate = new Date(date);
    targetDate.setHours(12, 0, 0, 0); // Normalize to noon to avoid timezone shifts
    
    const startOfDay = new Date(targetDate); startOfDay.setHours(0,0,0,0);
    const endOfDay = new Date(targetDate); endOfDay.setHours(23,59,59,999);

    const existing = await db.attendance.findFirst({
      where: { studentId, date: { gte: startOfDay, lte: endOfDay } }
    });

    if (existing) {
      if (status === 'NONE') {
        await db.attendance.delete({ where: { id: existing.id } });
      } else {
        await db.attendance.update({ where: { id: existing.id }, data: { status } });
      }
    } else if (status !== 'NONE') {
      await db.attendance.create({
        data: { studentId, date: targetDate, status, confidence: 1.0 } // 1.0 = Manual override
      });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to update record' }, { status: 500 });
  }
}
