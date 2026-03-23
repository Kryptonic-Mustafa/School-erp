import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Deployed: {path}")

def step17_deploy():
    print("====================================================")
    print("   M.A.C.DevOS: TEACHER MANAGEMENT MATRIX           ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. BUILDING TEACHER API KERNEL (CRUD)...")

    api_ts = """
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
"""
    create_file(os.path.join(project_dir, "src/app/api/teachers/route.ts"), api_ts)

    print("\n>>> 2. INJECTING TEACHER UI MODULE...")

    teachers_tsx = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit, Presentation } from 'lucide-react';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function TeachersMatrix() {
  const [teachers, setTeachers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });

  const fetchEntities = useCallback(async () => {
    try {
      const res = await fetch('/api/teachers');
      const data = await res.json();
      if (data.success) setTeachers(data.teachers);
    } catch (e) {
      osToast.fire({ icon: 'error', title: 'Data Fetch Failed' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchEntities(); }, [fetchEntities]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const confirm = await osAlert.confirm('Register Teacher?', `Create database entry for ${formData.name}.`);
    if (!confirm.isConfirmed) return;

    setIsSubmitting(true);
    try {
      const res = await fetch('/api/teachers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error);
      
      osAlert.success('Registration Complete', `Faculty member ${data.teacher.name} has been added.`);
      setFormData({ name: '', email: '', password: '' });
      fetchEntities();
    } catch (err: any) {
      osAlert.error('Registration Failed', err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = async (teacher: any) => {
    const { value: formValues } = await osAlert.confirm('Edit Faculty Details', `
      <div class="text-left space-y-3 mt-4">
        <label class="block text-sm font-medium text-slate-700">Full Name</label>
        <input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" value="${teacher.name}">
        <p class="text-xs text-slate-400 mt-2">Note: To change assigned classes, navigate to the Classes menu.</p>
      </div>
    `);
    
    if (formValues) {
      const name = formValues?.name || (document.getElementById('swal-name') as HTMLInputElement)?.value;
      
      try {
        const res = await fetch('/api/teachers', {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: teacher.id, name })
        });
        if (!res.ok) throw new Error((await res.json()).error);
        osToast.fire({ icon: 'success', title: 'Record Updated' }); 
        fetchEntities();
      } catch (err: any) {
        osAlert.error('Update Failed', err.message);
      }
    }
  };

  const handleDelete = async (id: string, name: string) => {
    const confirm = await osAlert.confirm(
      'Delete Faculty Record?', 
      `This will permanently purge ${name}'s account. This cannot be undone.`
    );
    if (!confirm.isConfirmed) return;

    try {
      osToast.fire({ icon: 'info', title: 'Processing deletion...' });
      const res = await fetch(`/api/teachers?id=${id}`, { method: 'DELETE' });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error);

      osToast.fire({ icon: 'success', title: 'Teacher record deleted' });
      fetchEntities();
    } catch (err: any) {
      osAlert.error('Deletion Failed', err.message);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* ADD TEACHER FORM */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
          <Plus className="w-5 h-5 text-blue-600" /> Create Faculty Record
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Jane Smith" /></div>
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="jane@school.edu" /></div>
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Temporary Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" /></div>
          <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors mt-2">
            {isSubmitting ? 'Saving...' : 'Register Teacher'}
          </button>
        </form>
      </div>

      {/* TEACHERS TABLE */}
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
        <div className="p-6 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <Presentation className="w-5 h-5 text-blue-600" /> Faculty Directory
          </h2>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input type="text" placeholder="Search records..." className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
              <tr>
                <th className="py-3 px-6">Name</th>
                <th className="py-3 px-6">Assigned Classes</th>
                <th className="py-3 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {teachers.map((teacher) => (
                <tr key={teacher.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-6 font-medium text-slate-800">
                    <div>{teacher.name}</div>
                    <div className="text-xs text-slate-500 font-normal">{teacher.user.email}</div>
                  </td>
                  <td className="py-3 px-6">
                    <div className="flex flex-wrap gap-1">
                      {teacher.classes.length > 0 ? teacher.classes.map((c: any) => (
                        <span key={c.name} className="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full text-xs font-semibold">{c.name}</span>
                      )) : <span className="text-xs text-slate-400 italic">No classes assigned</span>}
                    </div>
                  </td>
                  <td className="py-3 px-6 text-right">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => handleEdit(teacher)} className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(teacher.id, teacher.name)} className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!loading && teachers.length === 0 && <tr><td colSpan={3} className="py-8 text-center text-slate-500">No faculty records found.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/teachers/page.tsx"), teachers_tsx)

    print("\n>>> 3. RE-LINKING SIDEBAR NAVIGATION...")

    layout_path = os.path.join(project_dir, "src/app/admin/layout.tsx")
    if os.path.exists(layout_path):
        with open(layout_path, "r", encoding="utf-8") as f:
            layout_code = f.read()
        
        # Inject the Presentation icon for Teachers if missing
        if "Presentation" not in layout_code:
            layout_code = layout_code.replace("GraduationCap,", "GraduationCap, Presentation,")
        
        new_nav = """
  const navItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Students', href: '/admin/students', icon: GraduationCap },
    { name: 'Teachers', href: '/admin/teachers', icon: Presentation },
    { name: 'Classes', href: '/admin/classes', icon: BookOpen },
    { name: 'Attendance Logs', href: '/admin/attendance', icon: CalendarDays },
    { name: 'User Management', href: '/admin/users', icon: Users },
    { name: 'Roles & Access', href: '/admin/roles', icon: Settings },
    { name: 'Live Scanner', href: '/attendance', icon: Camera },
    { name: 'Biometrics', href: '/admin/face-register', icon: ScanFace },
    { name: 'Telemetry', href: '/admin/telemetry', icon: Activity },
  ];
"""
        import re
        layout_code = re.sub(r'const navItems = \[.*?\];', new_nav.strip(), layout_code, flags=re.DOTALL)
        create_file(layout_path, layout_code)

    print("\n====================================================")
    print(" [SUCCESS] TEACHER MANAGEMENT MODULE ONLINE.        ")
    print("====================================================\n")

if __name__ == "__main__":
    step17_deploy()