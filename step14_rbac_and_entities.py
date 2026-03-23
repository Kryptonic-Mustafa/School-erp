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
    print(f"  [+] Deployed: {path}")

def step14_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: ENTERPRISE RBAC & ACADEMIC CORE      ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. UPGRADING PRISMA DATABASE SCHEMA (RBAC INJECTION)...")
    schema_path = os.path.join(project_dir, "prisma/schema.prisma")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_content = f.read()

    if "AccessRole" not in schema_content:
        # Inject AccessRole relation into User model safely
        schema_content = schema_content.replace(
            "auditLogs AuditLog[]\n}",
            "auditLogs AuditLog[]\n  accessRoleId String?\n  accessRole AccessRole? @relation(fields: [accessRoleId], references: [id])\n}"
        )
        # Append AccessRole model
        schema_content += """
model AccessRole {
  id          String   @id @default(uuid())
  name        String   @unique
  permissions Json     // Array of permission strings
  users       User[]
}
"""
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(schema_content)
        
        print("  [+] Schema updated. Pushing to TiDB Matrix...")
        run_command("npx prisma db push", cwd=project_dir)
    else:
        print("  [-] Schema already contains RBAC models.")

    print("\n>>> 2. DEPLOYING RBAC & ACADEMIC API ROUTES...")

    # A. ROLES API
    api_roles = """
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
"""
    create_file(os.path.join(project_dir, "src/app/api/roles/route.ts"), api_roles)

    # B. USERS API (System Users / Admins / Staff)
    api_users = """
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
"""
    create_file(os.path.join(project_dir, "src/app/api/users/route.ts"), api_users)

    # C. CLASSES API
    api_classes = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  const classes = await db.class.findMany({ include: { teacher: true, _count: { select: { students: true } } } });
  return NextResponse.json({ success: true, classes });
}

export async function POST(req: Request) {
  try {
    const { name, teacherId } = await req.json();
    const newClass = await db.class.create({ data: { name, teacherId } });
    return NextResponse.json({ success: true, class: newClass });
  } catch (error) { return NextResponse.json({ error: 'Class creation failed' }, { status: 500 }); }
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

    # D. TEACHERS API
    api_teachers = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  const teachers = await db.teacher.findMany({ include: { user: true, classes: true } });
  return NextResponse.json({ success: true, teachers });
}
"""
    create_file(os.path.join(project_dir, "src/app/api/teachers/route.ts"), api_teachers)

    # E. UPDATE STUDENTS API (Add PATCH for Editing)
    api_students_path = os.path.join(project_dir, "src/app/api/students/route.ts")
    with open(api_students_path, "a", encoding="utf-8") as f:
        f.write("""
export async function PATCH(req: Request) {
  try {
    const { id, name, className } = await req.json();
    let targetClass = await db.class.findFirst({ where: { name: className } });
    if (!targetClass) {
      let defaultTeacher = await db.teacher.findFirst();
      targetClass = await db.class.create({ data: { name: className, teacherId: defaultTeacher!.id } });
    }
    await db.student.update({ where: { id }, data: { name, classId: targetClass.id } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Update failed' }, { status: 500 }); }
}
""")

    print("\n>>> 3. DEPLOYING ENTERPRISE UI MODULES...")

    # A. ROLES PAGE
    roles_ui = """
'use client';

import { useState, useEffect } from 'react';
import { Shield, Plus, Trash2 } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

const PERMISSIONS_LIST = [
  { id: 'manage_users', label: 'Manage System Users' },
  { id: 'manage_roles', label: 'Manage Roles & Permissions' },
  { id: 'manage_students', label: 'Manage Students' },
  { id: 'manage_academic', label: 'Manage Classes & Teachers' },
  { id: 'view_telemetry', label: 'View System Telemetry' },
];

export default function RolesMatrix() {
  const [roles, setRoles] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [selectedPerms, setSelectedPerms] = useState<string[]>([]);

  const fetchRoles = async () => {
    const res = await fetch('/api/roles').then(r => r.json());
    if (res.success) setRoles(res.roles);
  };
  useEffect(() => { fetchRoles(); }, []);

  const handleToggle = (id: string) => {
    setSelectedPerms(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/roles', { method: 'POST', body: JSON.stringify({ name, permissions: selectedPerms }) });
      if (!res.ok) throw new Error();
      osToast.fire({ icon: 'success', title: 'Role Created' });
      setName(''); setSelectedPerms([]); fetchRoles();
    } catch { osAlert.error('Error', 'Failed to create role'); }
  };

  const handleDelete = async (id: string) => {
    if (!(await osAlert.confirm('Delete Role?', 'This will permanently remove the role.')).isConfirmed) return;
    await fetch(`/api/roles?id=${id}`, { method: 'DELETE' });
    fetchRoles();
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Create Role</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Role Name</label><input type="text" required value={name} onChange={e=>setName(e.target.value)} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm" placeholder="e.g. IT Admin" /></div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Permissions</label>
            <div className="space-y-2 border border-slate-200 p-3 rounded-lg bg-slate-50">
              {PERMISSIONS_LIST.map(p => (
                <label key={p.id} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                  <input type="checkbox" checked={selectedPerms.includes(p.id)} onChange={() => handleToggle(p.id)} className="w-4 h-4 text-blue-600 rounded border-slate-300" />
                  {p.label}
                </label>
              ))}
            </div>
          </div>
          <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Save Role</button>
        </form>
      </div>
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Shield className="w-5 h-5 text-blue-600"/> System Roles</h2>
        <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Role</th><th className="py-3 px-4">Permissions</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
          <tbody className="divide-y divide-slate-100">
            {roles.map(r => (
              <tr key={r.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-medium text-slate-800">{r.name}</td><td className="py-3 px-4 text-xs text-slate-500 flex flex-wrap gap-1">{r.permissions.map((p:string) => <span key={p} className="bg-slate-100 px-2 py-0.5 rounded">{p.replace('_',' ')}</span>)}</td><td className="py-3 px-4 text-right"><button onClick={()=>handleDelete(r.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/roles/page.tsx"), roles_ui)

    # B. USERS PAGE
    users_ui = """
'use client';

import { useState, useEffect } from 'react';
import { UserCog, Plus, Trash2 } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function UsersMatrix() {
  const [users, setUsers] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [formData, setFormData] = useState({ email: '', password: '', roleType: 'ADMIN', accessRoleId: '' });

  const fetchData = async () => {
    const uRes = await fetch('/api/users').then(r => r.json());
    const rRes = await fetch('/api/roles').then(r => r.json());
    if (uRes.success) setUsers(uRes.users);
    if (rRes.success) setRoles(rRes.roles);
  };
  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/users', { method: 'POST', body: JSON.stringify(formData) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'User Created' }); fetchData(); }
  };

  const handleDelete = async (id: string) => {
    if (!(await osAlert.confirm('Delete User?', 'Remove access immediately?')).isConfirmed) return;
    await fetch(`/api/users?id=${id}`, { method: 'DELETE' }); fetchData();
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Add Staff/Admin</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required onChange={e=>setFormData({...formData, email: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required onChange={e=>setFormData({...formData, password: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" /></div>
          <div><label className="block text-sm font-medium mb-1">System Base Role</label><select onChange={e=>setFormData({...formData, roleType: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="ADMIN">Administrator</option><option value="TEACHER">Teacher</option></select></div>
          <div><label className="block text-sm font-medium mb-1">Custom Permissions Role</label><select onChange={e=>setFormData({...formData, accessRoleId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- No Custom Role --</option>{roles.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}</select></div>
          <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Create User</button>
        </form>
      </div>
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><UserCog className="w-5 h-5 text-blue-600"/> System Users</h2>
        <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">User</th><th className="py-3 px-4">Base Role</th><th className="py-3 px-4">Custom Role</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
          <tbody className="divide-y divide-slate-100">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-medium">{u.email}</td><td className="py-3 px-4 text-slate-500">{u.role}</td><td className="py-3 px-4"><span className="bg-blue-50 text-blue-700 px-2 rounded text-xs">{u.accessRole?.name || 'Standard'}</span></td><td className="py-3 px-4 text-right"><button onClick={()=>handleDelete(u.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/users/page.tsx"), users_ui)

    # C. CLASSES PAGE
    classes_ui = """
'use client';

import { useState, useEffect } from 'react';
import { BookOpen, Plus, Trash2 } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function ClassesMatrix() {
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [formData, setFormData] = useState({ name: '', teacherId: '' });

  const fetchData = async () => {
    const cRes = await fetch('/api/classes').then(r => r.json());
    const tRes = await fetch('/api/teachers').then(r => r.json());
    if (cRes.success) setClasses(cRes.classes);
    if (tRes.success) setTeachers(tRes.teachers);
  };
  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/classes', { method: 'POST', body: JSON.stringify(formData) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Class Created' }); fetchData(); }
  };

  const handleDelete = async (id: string) => {
    if (!(await osAlert.confirm('Delete Class?', 'Cannot delete if students are enrolled.')).isConfirmed) return;
    const res = await fetch(`/api/classes?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); }
    else { osAlert.error('Error', (await res.json()).error); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Create Class</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Class Name</label><input type="text" required onChange={e=>setFormData({...formData, name: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" placeholder="e.g. CS-101" /></div>
          <div><label className="block text-sm font-medium mb-1">Assign Teacher</label><select required onChange={e=>setFormData({...formData, teacherId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- Select --</option>{teachers.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></div>
          <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Create Class</button>
        </form>
      </div>
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><BookOpen className="w-5 h-5 text-blue-600"/> Active Classes</h2>
        <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Class</th><th className="py-3 px-4">Teacher</th><th className="py-3 px-4">Students</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
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

    # D. UNLOCK STUDENT EDITING IN UI
    student_path = os.path.join(project_dir, "src/app/admin/students/page.tsx")
    with open(student_path, "r", encoding="utf-8") as f:
        student_code = f.read()

    # Inject the SweetAlert Edit logic
    edit_function = """
  const handleEdit = async (student: any) => {
    const { value: formValues } = await osAlert.confirm('Edit Student', `
      <div class="text-left space-y-3 mt-4">
        <label class="block text-sm">Name</label>
        <input id="swal-name" class="w-full border rounded p-2 text-sm" value="${student.name}">
        <label class="block text-sm mt-3">Class</label>
        <input id="swal-class" class="w-full border rounded p-2 text-sm" value="${student.class.name}">
      </div>
    `);
    
    if (formValues) {
      const name = (document.getElementById('swal-name') as HTMLInputElement).value;
      const className = (document.getElementById('swal-class') as HTMLInputElement).value;
      
      const res = await fetch('/api/students', {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: student.id, name, className })
      });
      if (res.ok) { osToast.fire({ icon: 'success', title: 'Updated' }); fetchEntities(); }
    }
  };
"""
    student_code = student_code.replace("const handleDelete = async", edit_function + "\n  const handleDelete = async")
    student_code = student_code.replace(
        "onClick={() => osToast.fire({icon: 'info', title: 'Edit mode locked for Admin.'})}",
        "onClick={() => handleEdit(student)}"
    )
    create_file(student_path, student_code)

    # E. UPDATE ADMIN SIDEBAR NAVIGATION
    layout_path = os.path.join(project_dir, "src/app/admin/layout.tsx")
    with open(layout_path, "r", encoding="utf-8") as f:
        layout_code = f.read()
    
    new_nav = """
  const navItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Students', href: '/admin/students', icon: GraduationCap },
    { name: 'Classes', href: '/admin/classes', icon: BookOpen },
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
    print(" [SUCCESS] ENTERPRISE RBAC MATRIX ONLINE.           ")
    print("====================================================\n")

if __name__ == "__main__":
    step14_deploy()