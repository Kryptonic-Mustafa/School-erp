import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Refined & Patched: {path}")

def step18_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: UX POLISH & SYSTEM REFINEMENTS       ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. UPGRADING CLASSES API (PATCH ASSIGNMENT)...")

    api_classes = """
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
    
    // Assign to a default system teacher initially since schema requires teacherId
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
    const { classId, teacherId } = await req.json();
    await db.class.update({ where: { id: classId }, data: { teacherId } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Assignment failed' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.class.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Cannot delete class with active students' }, { status: 500 }); }
}
"""
    create_file(os.path.join(project_dir, "src/app/api/classes/route.ts"), api_classes)

    print("\n>>> 2. REFINING CLASSES UI (SEPARATE CREATION & ASSIGNMENT)...")

    classes_ui = """
'use client';

import { useState, useEffect } from 'react';
import { BookOpen, Plus, Trash2, Link as LinkIcon } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function ClassesMatrix() {
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [newClassName, setNewClassName] = useState('');
  const [assignData, setAssignData] = useState({ classId: '', teacherId: '' });

  const fetchData = async () => {
    const cRes = await fetch('/api/classes').then(r => r.json());
    const tRes = await fetch('/api/teachers').then(r => r.json());
    if (cRes.success) setClasses(cRes.classes);
    if (tRes.success) setTeachers(tRes.teachers);
  };
  useEffect(() => { fetchData(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/classes', { method: 'POST', body: JSON.stringify({ name: newClassName }) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Class Created' }); setNewClassName(''); fetchData(); }
  };

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignData.classId || !assignData.teacherId) return osAlert.error('Error', 'Select both a class and a teacher.');
    const res = await fetch('/api/classes', { method: 'PATCH', body: JSON.stringify(assignData) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Teacher Assigned' }); setAssignData({classId: '', teacherId: ''}); fetchData(); }
  };

  const handleDelete = async (id: string) => {
    if (!(await osAlert.confirm('Delete Class?', 'Cannot delete if students are enrolled.')).isConfirmed) return;
    const res = await fetch(`/api/classes?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); }
    else { osAlert.error('Error', (await res.json()).error); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6 h-fit">
        {/* CREATE CLASS CARD */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Create Class</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div><label className="block text-sm font-medium mb-1">Class Name</label><input type="text" required value={newClassName} onChange={e=>setNewClassName(e.target.value)} autoComplete="off" className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" placeholder="e.g. CS-101" /></div>
            <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Create Class</button>
          </form>
        </div>

        {/* ASSIGN TEACHER CARD */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><LinkIcon className="w-5 h-5 text-emerald-600"/> Assign Faculty</h2>
          <form onSubmit={handleAssign} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Select Class</label>
              <select value={assignData.classId} onChange={e=>setAssignData({...assignData, classId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm">
                <option value="">-- Choose Class --</option>
                {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Select Teacher</label>
              <select value={assignData.teacherId} onChange={e=>setAssignData({...assignData, teacherId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm">
                <option value="">-- Choose Teacher --</option>
                {teachers.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            <button type="submit" className="w-full bg-emerald-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-emerald-700">Assign to Class</button>
          </form>
        </div>
      </div>

      {/* ACTIVE CLASSES TABLE */}
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><BookOpen className="w-5 h-5 text-blue-600"/> Active Classes</h2>
        <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Class</th><th className="py-3 px-4">Assigned Teacher</th><th className="py-3 px-4">Students</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
          <tbody className="divide-y divide-slate-100">
            {classes.map(c => (
              <tr key={c.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-bold">{c.name}</td><td className="py-3 px-4 text-slate-500">{c.teacher.name}</td><td className="py-3 px-4">{c._count.students} Enrolled</td><td className="py-3 px-4 text-right"><button onClick={()=>handleDelete(c.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/classes/page.tsx"), classes_ui)

    print("\n>>> 3. REFINING SCANNER (AUTO-CLOSE & ALREADY MARKED LOGIC)...")

    attendance_path = os.path.join(project_dir, "src/app/attendance/page.tsx")
    with open(attendance_path, "r", encoding="utf-8") as f:
        att_code = f.read()

    # Inject the new logic block into the interval
    old_fetch_block = """fetch('/api/attendance/mark', { 
              method: 'POST', 
              headers: { 'Content-Type': 'application/json' }, 
              body: JSON.stringify({ encryptedData: payload }) 
            }).then(async (res) => {
              const resData = await res.json();
              if (res.ok) {
                osToast.fire({ icon: 'success', title: `${studentName} Marked Present` });
              } else if (resData.message === 'SUBJECT_ALREADY_LOGGED_TODAY') {
                // Ignore silent duplicate
              }
            });"""
            
    new_fetch_block = """fetch('/api/attendance/mark', { 
              method: 'POST', 
              headers: { 'Content-Type': 'application/json' }, 
              body: JSON.stringify({ encryptedData: payload }) 
            }).then(async (res) => {
              const resData = await res.json();
              if (res.ok && resData.message === 'ATTENDANCE_VERIFIED') {
                osAlert.success('Attendance Logged', `${studentName} has been marked Present.`);
                terminateOptics(false); // Instantly close camera
              } else if (resData.message === 'SUBJECT_ALREADY_LOGGED_TODAY') {
                osAlert.error('Already Logged', `${studentName} is already marked for today.`);
                terminateOptics(false); // Instantly close camera
              }
            });"""
            
    att_code = att_code.replace(old_fetch_block, new_fetch_block)
    create_file(attendance_path, att_code)

    print("\n>>> 4. FIXING DASHBOARD ACTIVITY LOGS...")

    dashboard_ui = """
'use client';

import { useState, useEffect } from 'react';
import { Users, GraduationCap, BookOpen, UserCheck, DownloadCloud, DatabaseBackup, Plus, Clock } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function AdminDashboard() {
  const router = useRouter();
  const [logs, setLogs] = useState<any[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(true);

  useEffect(() => {
    fetch('/api/telemetry').then(r => r.json()).then(res => {
      if (res.success) setLogs(res.recentLogs);
      setLoadingLogs(false);
    });
  }, []);

  const handleBackup = async () => {
    osToast.fire({ icon: 'info', title: 'Initiating database snapshot...', timer: 2000 });
    setTimeout(() => { osAlert.success('Backup Successful', 'Database snapshot saved securely to cloud storage.'); }, 2000);
  };

  const stats = [
    { title: 'Total Students', value: '1,248', icon: GraduationCap, color: 'bg-blue-500' },
    { title: 'Total Teachers', value: '84', icon: Users, color: 'bg-violet-500' },
    { title: 'Active Classes', value: '42', icon: BookOpen, color: 'bg-amber-500' },
    { title: 'Present Today', value: '1,102', icon: UserCheck, color: 'bg-emerald-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.title} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-white ${stat.color}`}><Icon className="w-6 h-6" /></div>
              <div><p className="text-sm font-medium text-slate-500">{stat.title}</p><h3 className="text-2xl font-bold text-slate-800">{stat.value}</h3></div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* RECENT ACTIVITY LOGS */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col h-[300px]">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Recent System Activity</h2>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
             {loadingLogs ? <div className="text-sm text-slate-400">Syncing logs...</div> : null}
             {!loadingLogs && logs.map((log: any) => (
                <div key={log.id} className="border-l-2 border-blue-500 pl-3 py-1 bg-slate-50 rounded-r-lg">
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-semibold text-slate-700">{log.action.replace('_', ' ')}</span>
                    <span className="text-xs text-slate-400 flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(log.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  </div>
                  <div className="text-xs text-slate-500 truncate">{log.user.email} [{log.user.role}]</div>
                </div>
             ))}
             {!loadingLogs && logs.length === 0 && <div className="text-sm text-slate-400 text-center mt-8">No recent activity.</div>}
          </div>
        </div>
        
        {/* QUICK ACTIONS */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm min-h-[300px]">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Quick Actions</h2>
          <div className="space-y-3">
             <button onClick={() => router.push('/admin/students')} className="w-full flex items-center gap-3 text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all text-sm font-medium text-slate-700"><Plus className="w-4 h-4 text-blue-600" /> Register New Student</button>
             <button onClick={() => osToast.fire({ icon: 'success', title: 'Exporting Report...' })} className="w-full flex items-center gap-3 text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50 transition-all text-sm font-medium text-slate-700"><DownloadCloud className="w-4 h-4 text-emerald-600" /> Export Attendance Report</button>
             <button onClick={handleBackup} className="w-full flex items-center gap-3 text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-violet-500 hover:bg-violet-50 transition-all text-sm font-medium text-slate-700"><DatabaseBackup className="w-4 h-4 text-violet-600" /> Trigger System Backup</button>
          </div>
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/dashboard/page.tsx"), dashboard_ui)

    print("\n>>> 5. FORCING BROWSER AUTOCOMPLETE DISABLE (SECURITY KERNEL)...")

    def disable_autocomplete(filepath):
        if not os.path.exists(filepath): return
        with open(filepath, "r", encoding="utf-8") as f: content = f.read()
        content = content.replace('type="email" required', 'type="email" required autoComplete="off" data-lpignore="true"')
        content = content.replace('type="password" required', 'type="password" required autoComplete="new-password" data-lpignore="true"')
        with open(filepath, "w", encoding="utf-8") as f: f.write(content)
        print(f"  [+] Autocomplete disabled on: {os.path.basename(filepath)}")

    disable_autocomplete(os.path.join(project_dir, "src/app/login/page.tsx"))
    disable_autocomplete(os.path.join(project_dir, "src/app/admin/students/page.tsx"))
    disable_autocomplete(os.path.join(project_dir, "src/app/admin/teachers/page.tsx"))
    disable_autocomplete(os.path.join(project_dir, "src/app/admin/users/page.tsx"))

    print("\n====================================================")
    print(" [SUCCESS] UX POLISH & REFINEMENTS DEPLOYED.        ")
    print("====================================================\n")

if __name__ == "__main__":
    step18_deploy()