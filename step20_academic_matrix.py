import os
import subprocess
import sys
import re

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

def step20_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: ACADEMIC MATRIX & EXAMINATIONS       ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. UPGRADING PRISMA SCHEMA (INJECTING ACADEMIC RELATIONS)...")
    
    schema_path = os.path.join(project_dir, "prisma/schema.prisma")
    
    # We cleanly rewrite the schema to ensure all reverse relations are perfect
    full_schema = """
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}

model User {
  id           String      @id @default(uuid())
  email        String      @unique
  password     String
  role         String      // ADMIN, TEACHER, STUDENT
  createdAt    DateTime    @default(now())
  student      Student?
  teacher      Teacher?
  auditLogs    AuditLog[]
  accessRoleId String?
  accessRole   AccessRole? @relation(fields: [accessRoleId], references: [id])
}

model AccessRole {
  id          String   @id @default(uuid())
  name        String   @unique
  permissions Json
  users       User[]
}

model Student {
  id            String          @id @default(uuid())
  name          String
  userId        String          @unique
  user          User            @relation(fields: [userId], references: [id])
  classId       String
  class         Class           @relation(fields: [classId], references: [id])
  embeddings    FaceEmbedding[]
  attendances   Attendance[]
  grades        Grade[]
}

model Teacher {
  id        String    @id @default(uuid())
  name      String
  userId    String    @unique
  user      User      @relation(fields: [userId], references: [id])
  classes   Class[]
  subjects  Subject[]
}

model Class {
  id        String    @id @default(uuid())
  name      String    @unique
  teacherId String
  teacher   Teacher   @relation(fields: [teacherId], references: [id])
  students  Student[]
  subjects  Subject[]
}

// ================= NEW ACADEMIC MODELS ================= //

model Subject {
  id        String   @id @default(uuid())
  name      String
  code      String   @unique
  classId   String
  class     Class    @relation(fields: [classId], references: [id])
  teacherId String
  teacher   Teacher  @relation(fields: [teacherId], references: [id])
  exams     Exam[]
}

model Exam {
  id        String   @id @default(uuid())
  title     String
  date      DateTime
  subjectId String
  subject   Subject  @relation(fields: [subjectId], references: [id])
  grades    Grade[]
}

model Grade {
  id        String   @id @default(uuid())
  score     Float
  remarks   String?
  studentId String
  student   Student  @relation(fields: [studentId], references: [id])
  examId    String
  exam      Exam     @relation(fields: [examId], references: [id])

  @@unique([studentId, examId])
}

// ================= EXISTING DATA MODELS ================= //

model FaceEmbedding {
  id         String   @id @default(uuid())
  vectorData Json
  studentId  String
  student    Student  @relation(fields: [studentId], references: [id])
}

model Attendance {
  id         String   @id @default(uuid())
  date       DateTime @default(now())
  status     String   @default("PRESENT")
  confidence Float    @default(1.0)
  studentId  String
  student    Student  @relation(fields: [studentId], references: [id])
}

model AuditLog {
  id        String   @id @default(uuid())
  action    String
  timestamp DateTime @default(now())
  userId    String
  user      User     @relation(fields: [userId], references: [id])
}
"""
    create_file(schema_path, full_schema)
    run_command("npx prisma generate", cwd=project_dir)
    run_command("npx prisma db push", cwd=project_dir)

    print("\n>>> 2. BUILDING ACADEMIC APIs...")

    # A. Subjects API
    api_subjects = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  const subjects = await db.subject.findMany({ include: { class: true, teacher: true, _count: { select: { exams: true } } } });
  return NextResponse.json({ success: true, subjects });
}

export async function POST(req: Request) {
  try {
    const { name, code, classId, teacherId } = await req.json();
    const subject = await db.subject.create({ data: { name, code, classId, teacherId } });
    return NextResponse.json({ success: true, subject });
  } catch (error) { return NextResponse.json({ error: 'Subject creation failed. Code must be unique.' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.subject.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Cannot delete subject with active exams' }, { status: 500 }); }
}
"""
    create_file(os.path.join(project_dir, "src/app/api/subjects/route.ts"), api_subjects)

    # B. Exams API
    api_exams = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  const exams = await db.exam.findMany({ include: { subject: { include: { class: true } }, _count: { select: { grades: true } } }, orderBy: { date: 'desc' } });
  return NextResponse.json({ success: true, exams });
}

export async function POST(req: Request) {
  try {
    const { title, date, subjectId } = await req.json();
    const exam = await db.exam.create({ data: { title, date: new Date(date), subjectId } });
    return NextResponse.json({ success: true, exam });
  } catch (error) { return NextResponse.json({ error: 'Exam creation failed.' }, { status: 500 }); }
}

export async function DELETE(req: Request) {
  try {
    const id = new URL(req.url).searchParams.get('id');
    await db.grade.deleteMany({ where: { examId: id! } }); // Cascade delete grades
    await db.exam.delete({ where: { id: id! } });
    return NextResponse.json({ success: true });
  } catch (error) { return NextResponse.json({ error: 'Deletion failed' }, { status: 500 }); }
}
"""
    create_file(os.path.join(project_dir, "src/app/api/exams/route.ts"), api_exams)

    print("\n>>> 3. DEPLOYING ACADEMICS UI HUB...")

    academics_ui = """
'use client';

import { useState, useEffect } from 'react';
import { Library, FileText, Plus, Trash2, Award } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function AcademicsHub() {
  const [activeTab, setActiveTab] = useState('SUBJECTS');
  const [subjects, setSubjects] = useState<any[]>([]);
  const [exams, setExams] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);

  // Forms
  const [subForm, setSubForm] = useState({ name: '', code: '', classId: '', teacherId: '' });
  const [examForm, setExamForm] = useState({ title: '', date: '', subjectId: '' });

  const fetchData = async () => {
    const [subRes, exRes, clsRes, tchRes] = await Promise.all([
      fetch('/api/subjects').then(r => r.json()),
      fetch('/api/exams').then(r => r.json()),
      fetch('/api/classes').then(r => r.json()),
      fetch('/api/teachers').then(r => r.json())
    ]);
    if (subRes.success) setSubjects(subRes.subjects);
    if (exRes.success) setExams(exRes.exams);
    if (clsRes.success) setClasses(clsRes.classes);
    if (tchRes.success) setTeachers(tchRes.teachers);
  };

  useEffect(() => { fetchData(); }, []);

  const handleCreateSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/subjects', { method: 'POST', body: JSON.stringify(subForm) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Subject Created' }); setSubForm({name:'', code:'', classId:'', teacherId:''}); fetchData(); }
    else osAlert.error('Error', (await res.json()).error);
  };

  const handleCreateExam = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/exams', { method: 'POST', body: JSON.stringify(examForm) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Exam Scheduled' }); setExamForm({title:'', date:'', subjectId:''}); fetchData(); }
    else osAlert.error('Error', (await res.json()).error);
  };

  const deleteRecord = async (endpoint: string, id: string) => {
    if (!(await osAlert.confirm('Delete Record?', 'This action is irreversible.')).isConfirmed) return;
    const res = await fetch(`/api/${endpoint}?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); }
    else osAlert.error('Error', (await res.json()).error);
  };

  return (
    <div className="space-y-6">
      {/* TABS */}
      <div className="flex border-b border-slate-200">
        <button onClick={() => setActiveTab('SUBJECTS')} className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'SUBJECTS' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}>
          <Library className="w-4 h-4" /> Curriculum / Subjects
        </button>
        <button onClick={() => setActiveTab('EXAMS')} className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'EXAMS' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}>
          <FileText className="w-4 h-4" /> Examinations
        </button>
      </div>

      {activeTab === 'SUBJECTS' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Add Subject</h2>
            <form onSubmit={handleCreateSubject} className="space-y-4">
              <div><label className="block text-sm font-medium mb-1">Subject Name</label><input type="text" required value={subForm.name} onChange={e=>setSubForm({...subForm, name: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" placeholder="e.g. Advanced Physics" /></div>
              <div><label className="block text-sm font-medium mb-1">Subject Code</label><input type="text" required value={subForm.code} onChange={e=>setSubForm({...subForm, code: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm uppercase" placeholder="e.g. PHY-201" /></div>
              <div><label className="block text-sm font-medium mb-1">Assign Class</label><select required value={subForm.classId} onChange={e=>setSubForm({...subForm, classId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- Select Class --</option>{classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
              <div><label className="block text-sm font-medium mb-1">Assign Teacher</label><select required value={subForm.teacherId} onChange={e=>setSubForm({...subForm, teacherId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- Select Teacher --</option>{teachers.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></div>
              <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Save Subject</button>
            </form>
          </div>
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Library className="w-5 h-5 text-blue-600"/> Curriculum Master List</h2>
            <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Code / Subject</th><th className="py-3 px-4">Class</th><th className="py-3 px-4">Teacher</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {subjects.map(s => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="py-3 px-4"><div className="font-bold text-slate-800">{s.name}</div><div className="text-xs text-slate-500 font-mono">{s.code}</div></td>
                    <td className="py-3 px-4"><span className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs font-semibold">{s.class.name}</span></td>
                    <td className="py-3 px-4 text-slate-600">{s.teacher.name}</td>
                    <td className="py-3 px-4 text-right"><button onClick={()=>deleteRecord('subjects', s.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button></td>
                  </tr>
                ))}
                {subjects.length === 0 && <tr><td colSpan={4} className="py-8 text-center text-slate-500">No subjects defined.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'EXAMS' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-emerald-600"/> Schedule Exam</h2>
            <form onSubmit={handleCreateExam} className="space-y-4">
              <div><label className="block text-sm font-medium mb-1">Exam Title</label><input type="text" required value={examForm.title} onChange={e=>setExamForm({...examForm, title: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" placeholder="e.g. Mid-Term Assessment" /></div>
              <div><label className="block text-sm font-medium mb-1">Target Subject</label><select required value={examForm.subjectId} onChange={e=>setExamForm({...examForm, subjectId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- Select Subject --</option>{subjects.map(s => <option key={s.id} value={s.id}>{s.name} ({s.class.name})</option>)}</select></div>
              <div><label className="block text-sm font-medium mb-1">Date</label><input type="date" required value={examForm.date} onChange={e=>setExamForm({...examForm, date: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" /></div>
              <button type="submit" className="w-full bg-emerald-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-emerald-700">Schedule Exam</button>
            </form>
          </div>
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><FileText className="w-5 h-5 text-emerald-600"/> Upcoming Examinations</h2>
            <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Exam Title</th><th className="py-3 px-4">Subject & Class</th><th className="py-3 px-4">Date</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {exams.map(ex => (
                  <tr key={ex.id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-bold text-slate-800">{ex.title}</td>
                    <td className="py-3 px-4"><div className="text-slate-700">{ex.subject.name}</div><div className="text-xs text-slate-500">{ex.subject.class.name}</div></td>
                    <td className="py-3 px-4 text-slate-600">{new Date(ex.date).toLocaleDateString()}</td>
                    <td className="py-3 px-4 text-right">
                      <button onClick={()=>osToast.fire({icon:'info', title: 'Grading module pending...'})} className="text-slate-400 hover:text-emerald-600 mr-3"><Award className="w-4 h-4"/></button>
                      <button onClick={()=>deleteRecord('exams', ex.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button>
                    </td>
                  </tr>
                ))}
                {exams.length === 0 && <tr><td colSpan={4} className="py-8 text-center text-slate-500">No exams scheduled.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/academics/page.tsx"), academics_ui)

    print("\n>>> 4. ADDING ACADEMICS TO SIDEBAR...")

    layout_path = os.path.join(project_dir, "src/app/admin/layout.tsx")
    with open(layout_path, "r", encoding="utf-8") as f:
        layout_code = f.read()
        
    if "Library" not in layout_code:
        layout_code = layout_code.replace("School, CalendarDays", "School, CalendarDays, Library")

    new_nav = """
  const navItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Students', href: '/admin/students', icon: GraduationCap },
    { name: 'Teachers', href: '/admin/teachers', icon: Presentation },
    { name: 'Classes', href: '/admin/classes', icon: BookOpen },
    { name: 'Academics', href: '/admin/academics', icon: Library },
    { name: 'Attendance Logs', href: '/admin/attendance', icon: CalendarDays },
    { name: 'User Management', href: '/admin/users', icon: Users },
    { name: 'Roles & Access', href: '/admin/roles', icon: Settings },
    { name: 'Live Scanner', href: '/attendance', icon: Camera },
    { name: 'Biometrics', href: '/admin/face-register', icon: ScanFace },
    { name: 'Telemetry', href: '/admin/telemetry', icon: Activity },
  ];
"""
    layout_code = re.sub(r'const navItems = \[.*?\];', new_nav.strip(), layout_code, flags=re.DOTALL)
    create_file(layout_path, layout_code)

    print("\n====================================================")
    print(" [SUCCESS] ACADEMIC MATRIX SUCCESSFULLY DEPLOYED.   ")
    print("====================================================\n")

if __name__ == "__main__":
    step20_deploy()