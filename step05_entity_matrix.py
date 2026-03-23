import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Wrote Matrix File: {path}")

def step05_deploy():
    print("====================================================")
    print("     M.A.C.DevOS: ENTITY MATRIX (CRUD) DEPLOYMENT   ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print(f"\n[*] Target System: {project_dir}")
    print("\n>>> INJECTING ENTITY API ROUTES AND UI DASHBOARDS...")

    # 1. API Route: Students CRUD
    students_api_ts = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';
import bcrypt from 'bcryptjs';

export async function GET() {
  try {
    const students = await db.student.findMany({
      include: {
        user: { select: { email: true } },
        class: { select: { name: true } }
      },
      orderBy: { name: 'asc' }
    });
    return NextResponse.json({ success: true, students });
  } catch (error) {
    return NextResponse.json({ error: 'FAILED_TO_FETCH' }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { name, email, password, className } = await req.json();

    // 1. Relational Safety: Ensure a default Teacher exists
    let defaultTeacher = await db.teacher.findFirst();
    if (!defaultTeacher) {
      const tUser = await db.user.create({
        data: { email: 'system.teacher@school.os', password: await bcrypt.hash('teacher123', 10), role: 'TEACHER' }
      });
      defaultTeacher = await db.teacher.create({
        data: { userId: tUser.id, name: 'System Auto-Teacher' }
      });
    }

    // 2. Relational Safety: Ensure the Class exists
    let targetClass = await db.class.findFirst({ where: { name: className } });
    if (!targetClass) {
      targetClass = await db.class.create({
        data: { name: className, teacherId: defaultTeacher.id }
      });
    }

    // 3. Create Student User & Profile
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await db.user.create({
      data: { email, password: hashedPassword, role: 'STUDENT' }
    });

    const student = await db.student.create({
      data: { userId: user.id, name, classId: targetClass.id }
    });

    return NextResponse.json({ success: true, student });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'ENTITY_CREATION_FAILED' }, { status: 500 });
  }
}
    """
    create_file(os.path.join(project_dir, "src/app/api/students/route.ts"), students_api_ts)

    # 2. UI Route: Entity Management Dashboard
    students_ui_ts = """
'use client';

import { useState, useEffect } from 'react';
import { Users, PlusSquare, Terminal } from 'lucide-react';
import Link from 'next/link';

export default function EntityMatrix() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ name: '', email: '', password: '', className: 'CS-101' });

  const fetchEntities = async () => {
    const res = await fetch('/api/students');
    const data = await res.json();
    if (data.success) setStudents(data.students);
    setLoading(false);
  };

  useEffect(() => { fetchEntities(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await fetch('/api/students', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    setFormData({ name: '', email: '', password: '', className: 'CS-101' });
    fetchEntities();
  };

  return (
    <div className="min-h-screen p-8 relative z-10 font-mono">
      <header className="mb-8 border-b border-zinc-800 pb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-3 text-white uppercase tracking-widest">
          <Users className="w-6 h-6 text-green-500" />
          Entity_Matrix
        </h1>
        <Link href="/admin/dashboard" className="text-xs text-zinc-500 hover:text-green-500 uppercase transition-colors">
          [ Return to Root ]
        </Link>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* ADD ENTITY FORM */}
        <div className="border border-zinc-800 bg-black p-6 h-fit">
          <h2 className="text-lg text-white mb-6 uppercase flex items-center gap-2">
            <PlusSquare className="w-5 h-5 text-green-500" /> Initialize Subject
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4 text-sm">
            <div>
              <label className="block text-zinc-500 uppercase mb-1">Full Name</label>
              <input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" placeholder="John Doe" />
            </div>
            <div>
              <label className="block text-zinc-500 uppercase mb-1">System Identifier (Email)</label>
              <input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" placeholder="john@student.os" />
            </div>
            <div>
              <label className="block text-zinc-500 uppercase mb-1">Passkey</label>
              <input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" placeholder="••••••••" />
            </div>
            <div>
              <label className="block text-zinc-500 uppercase mb-1">Assigned Designation (Class)</label>
              <input type="text" required value={formData.className} onChange={e => setFormData({...formData, className: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" />
            </div>
            <button type="submit" disabled={loading} className="w-full bg-green-500 text-black py-2 uppercase font-bold hover:bg-green-400 disabled:opacity-50 mt-4">
              {loading ? 'Processing...' : 'Write to Database'}
            </button>
          </form>
        </div>

        {/* ENTITY DATAGRID */}
        <div className="lg:col-span-2 border border-zinc-800 bg-black p-6">
          <h2 className="text-lg text-white mb-6 uppercase flex items-center gap-2">
            <Terminal className="w-5 h-5 text-green-500" /> Active Subjects
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-zinc-500 border-b border-zinc-800 uppercase">
                <tr>
                  <th className="pb-3 px-2">ID Fragment</th>
                  <th className="pb-3 px-2">Name</th>
                  <th className="pb-3 px-2">Designation</th>
                  <th className="pb-3 px-2">Identifier</th>
                </tr>
              </thead>
              <tbody className="text-zinc-300">
                {students.map((student) => (
                  <tr key={student.id} className="border-b border-zinc-800/50 hover:bg-zinc-900/50 transition-colors">
                    <td className="py-3 px-2 text-xs text-zinc-600">{student.id.split('-')[0]}</td>
                    <td className="py-3 px-2 text-green-500">{student.name}</td>
                    <td className="py-3 px-2">{student.class.name}</td>
                    <td className="py-3 px-2">{student.user.email}</td>
                  </tr>
                ))}
                {!loading && students.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-zinc-600 uppercase">No active subjects found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/students/page.tsx"), students_ui_ts)

    # 3. Update Admin Dashboard to link to Entity Matrix
    admin_tsx_path = os.path.join(project_dir, "src/app/admin/dashboard/page.tsx")
    if os.path.exists(admin_tsx_path):
        with open(admin_tsx_path, "r", encoding="utf-8") as f:
            admin_content = f.read()
        
        # Replace the restricted block with an active link
        old_block = """
        <div className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors">
          <Users className="w-8 h-8 mb-4 text-green-500" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Entity Management</h2>
          <p className="text-sm text-zinc-400 mb-4">Manage students, teachers, and system access.</p>
          <span className="text-xs text-zinc-600 uppercase">&gt;&gt; Access Restricted</span>
        </div>
        """
        
        new_block = """
        <Link href="/admin/students" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group">
          <Users className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Entity Management</h2>
          <p className="text-sm text-zinc-400 mb-4">Manage students, teachers, and system access.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Access Matrix <span className="animate-pulse">_</span></span>
        </Link>
        """
        
        # Safe replace (handling whitespace variations roughly)
        if "Entity Management" in admin_content:
            import re
            admin_content = re.sub(
                r'<div[^>]*>.*?<Users.*?Entity Management.*?</div>', 
                new_block.strip(), 
                admin_content, 
                flags=re.DOTALL
            )
            create_file(admin_tsx_path, admin_content)

    print("\n====================================================")
    print(" [SUCCESS] ENTITY MATRIX FULLY INTEGRATED.")
    print("====================================================\n")

if __name__ == "__main__":
    step05_deploy()