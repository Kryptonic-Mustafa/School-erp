import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  try {
    const totalStudents = await db.student.count();
    const totalClasses = await db.class.count();
    const totalTeachers = await db.teacher.count();

    const startOfDay = new Date();
    startOfDay.setHours(0, 0, 0, 0);

    const todayAttendance = await db.attendance.count({
      where: { date: { gte: startOfDay } }
    });

    const recentLogs = await db.auditLog.findMany({
      take: 10,
      orderBy: { timestamp: 'desc' },
      include: { user: { select: { email: true, role: true } } }
    });

    const chartData = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      d.setHours(0, 0, 0, 0);
      
      const nextD = new Date(d);
      nextD.setDate(d.getDate() + 1);

      const count = await db.attendance.count({
        where: { date: { gte: d, lt: nextD } }
      });

      chartData.push({
        name: d.toLocaleDateString('en-US', { weekday: 'short' }),
        scans: count
      });
    }

    return NextResponse.json({
      success: true,
      metrics: { totalStudents, totalClasses, totalTeachers, todayAttendance },
      chartData,
      recentLogs
    });
  } catch (error) {
    return NextResponse.json({ error: 'TELEMETRY_FAILURE' }, { status: 500 });
  }
}
