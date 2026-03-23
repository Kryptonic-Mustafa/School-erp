import os
import subprocess
import sys

PROJECT_NAME = "school-os"

def run_command(command, cwd=None):
    print(f"[*] Executing: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"[!] Error executing: {command}")
        sys.exit(1)

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Injected Telemetry Node: {path}")

def step10_deploy():
    print("====================================================")
    print("    M.A.C.DevOS: SYSTEM TELEMETRY DEPLOYMENT        ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> INSTALLING DATA VISUALIZATION ENGINE...")
    run_command("npm install recharts", cwd=project_dir)

    print("\n>>> INJECTING TELEMETRY API & VISUAL MATRIX...")

    # 1. Telemetry API Route (Aggregates Data for Charts)
    api_ts = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  try {
    const totalStudents = await db.student.count();
    const totalClasses = await db.class.count();

    const startOfDay = new Date();
    startOfDay.setHours(0, 0, 0, 0);

    const todayAttendance = await db.attendance.count({
      where: { date: { gte: startOfDay } }
    });

    // Fetch last 10 Audit Logs
    const recentLogs = await db.auditLog.findMany({
      take: 10,
      orderBy: { timestamp: 'desc' },
      include: { user: { select: { email: true, role: true } } }
    });

    // Generate Chart Data (Last 7 Days)
    const chartData = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      d.setHours(0, 0, 0, 0);
      
      const nextD = new Date(d);
      nextD.setDate(d.getDate() + 1);

      const count = await db.attendance.count({
        where: {
          date: { gte: d, lt: nextD }
        }
      });

      chartData.push({
        name: d.toLocaleDateString('en-US', { weekday: 'short' }),
        scans: count
      });
    }

    return NextResponse.json({
      success: true,
      metrics: { totalStudents, totalClasses, todayAttendance },
      chartData,
      recentLogs
    });
  } catch (error) {
    return NextResponse.json({ error: 'TELEMETRY_FAILURE' }, { status: 500 });
  }
}
    """
    create_file(os.path.join(project_dir, "src/app/api/telemetry/route.ts"), api_ts)

    # 2. Telemetry Dashboard UI
    telemetry_ui = """
'use client';

import { useState, useEffect } from 'react';
import { Activity, Users, Scan, Server, ShieldAlert } from 'lucide-react';
import Link from 'next/link';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { osToast } from '@/lib/alert_engine';

export default function TelemetryDashboard() {
  const [data, setData] = useState({
    metrics: { totalStudents: 0, totalClasses: 0, todayAttendance: 0 },
    chartData: [],
    recentLogs: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/telemetry')
      .then(res => res.json())
      .then(res => {
        if (res.success) setData(res);
        else throw new Error('Data fetch failed');
        setLoading(false);
      })
      .catch(() => {
        osToast.fire({ icon: 'error', title: 'Telemetry Node Offline' });
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen p-8 relative z-10 font-mono">
      <header className="mb-8 border-b border-zinc-800 pb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-3 text-white uppercase tracking-widest">
          <Activity className="w-6 h-6 text-green-500" /> System_Telemetry
        </h1>
        <Link href="/admin/dashboard" className="text-xs text-zinc-500 hover:text-green-500 uppercase transition-colors">
          [ Return to Root ]
        </Link>
      </header>

      {/* METRICS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="border border-zinc-800 bg-black p-6 flex items-center gap-4">
          <div className="p-3 bg-zinc-900 border border-zinc-700 text-green-500"><Users className="w-6 h-6" /></div>
          <div>
            <div className="text-xs text-zinc-500 uppercase">Active Entities</div>
            <div className="text-2xl font-bold text-white">{loading ? '-' : data.metrics.totalStudents}</div>
          </div>
        </div>
        <div className="border border-zinc-800 bg-black p-6 flex items-center gap-4">
          <div className="p-3 bg-zinc-900 border border-zinc-700 text-green-500"><Scan className="w-6 h-6" /></div>
          <div>
            <div className="text-xs text-zinc-500 uppercase">Today's Verifications</div>
            <div className="text-2xl font-bold text-white">{loading ? '-' : data.metrics.todayAttendance}</div>
          </div>
        </div>
        <div className="border border-zinc-800 bg-black p-6 flex items-center gap-4">
          <div className="p-3 bg-zinc-900 border border-zinc-700 text-green-500"><Server className="w-6 h-6" /></div>
          <div>
            <div className="text-xs text-zinc-500 uppercase">Registered Classes</div>
            <div className="text-2xl font-bold text-white">{loading ? '-' : data.metrics.totalClasses}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* CHART DATA */}
        <div className="lg:col-span-2 border border-zinc-800 bg-black p-6 h-[400px] flex flex-col">
          <h2 className="text-sm text-zinc-500 uppercase mb-6 flex items-center gap-2">
             <Activity className="w-4 h-4 text-green-500" /> 7-Day Matrix Activity Volume
          </h2>
          <div className="flex-1 w-full relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center text-green-500 animate-pulse uppercase text-xs">Awaiting Matrix Data...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorScans" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis dataKey="name" stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', color: '#22c55e', borderRadius: '0', fontFamily: 'monospace' }}
                    itemStyle={{ color: '#22c55e' }}
                  />
                  <Area type="monotone" dataKey="scans" stroke="#22c55e" strokeWidth={2} fillOpacity={1} fill="url(#colorScans)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* AUDIT LOGS */}
        <div className="border border-zinc-800 bg-black p-6 overflow-hidden flex flex-col">
          <h2 className="text-sm text-zinc-500 uppercase mb-6 flex items-center gap-2">
             <ShieldAlert className="w-4 h-4 text-green-500" /> Security Audit Log
          </h2>
          <div className="flex-1 overflow-y-auto pr-2 space-y-3">
             {loading ? <div className="text-xs text-zinc-600 uppercase">Syncing...</div> : null}
             {!loading && data.recentLogs.map((log: any) => (
                <div key={log.id} className="border border-zinc-800 bg-zinc-900/50 p-3">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-xs text-green-500 font-bold">{log.action}</span>
                    <span className="text-[10px] text-zinc-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="text-xs text-zinc-400 truncate">{log.user.email} [{log.user.role}]</div>
                </div>
             ))}
             {!loading && data.recentLogs.length === 0 && (
                <div className="text-xs text-zinc-600 uppercase">No events logged.</div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/telemetry/page.tsx"), telemetry_ui)

    # 3. Clean Rewrite of Dashboard to unlock Telemetry Link
    dashboard_tsx = """import { Terminal, Users, Camera, Activity, ScanFace } from 'lucide-react';
import Link from 'next/link';

export default function AdminDashboard() {
  return (
    <div className="min-h-screen p-8 relative z-10 font-mono">
      <header className="flex justify-between items-center mb-12 border-b border-zinc-800 pb-6">
        <h1 className="text-3xl font-bold flex items-center gap-3 text-white uppercase tracking-widest">
          <Terminal className="w-8 h-8 text-green-500" />
          Root_Command
        </h1>
        <div className="text-xs text-zinc-500 uppercase flex flex-col items-end">
           <span>Status: <span className="text-green-500">Online</span></span>
           <span>Role: Admin</span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Entity Matrix */}
        <Link href="/admin/students" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group flex flex-col justify-between">
          <div>
            <Users className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-bold text-white mb-2 uppercase">Entity Matrix</h2>
            <p className="text-sm text-zinc-400 mb-4">Manage students and identities.</p>
          </div>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Access <span className="animate-pulse">_</span></span>
        </Link>

        {/* Biometric Registry */}
        <Link href="/admin/face-register" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group flex flex-col justify-between">
          <div>
            <ScanFace className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-bold text-white mb-2 uppercase">Registry</h2>
            <p className="text-sm text-zinc-400 mb-4">Map vectors to active entities.</p>
          </div>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Initialize <span className="animate-pulse">_</span></span>
        </Link>

        {/* Live Scanner */}
        <Link href="/attendance" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group flex flex-col justify-between">
          <div>
            <Camera className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-bold text-white mb-2 uppercase">Scanner</h2>
            <p className="text-sm text-zinc-400 mb-4">Launch face recognition kiosk.</p>
          </div>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Execute <span className="animate-pulse">_</span></span>
        </Link>

        {/* UNLOCKED: System Telemetry */}
        <Link href="/admin/telemetry" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group flex flex-col justify-between">
          <div>
            <Activity className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-bold text-white mb-2 uppercase">Telemetry</h2>
            <p className="text-sm text-zinc-400 mb-4">View metrics and security logs.</p>
          </div>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Monitor <span className="animate-pulse">_</span></span>
        </Link>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/dashboard/page.tsx"), dashboard_tsx)

    print("\n====================================================")
    print(" [SUCCESS] TELEMETRY MATRIX IS ONLINE.              ")
    print("====================================================\n")

if __name__ == "__main__":
    step10_deploy()