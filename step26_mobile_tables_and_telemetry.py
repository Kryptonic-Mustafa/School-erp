import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] UI Overwritten & Perfected: {path}")

def step26_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: PERFECT MOBILE CARDS & THEME SYNC    ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)

    print("\n>>> 1. OVERWRITING CLASSES UI (LEFT/RIGHT MOBILE CARDS)...")
    
    classes_ui = """
'use client';

import { useState, useEffect } from 'react';
import { BookOpen, Plus, Trash2, Link as LinkIcon, CheckSquare, X, Search } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function ClassesMatrix() {
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [newClassName, setNewClassName] = useState('');
  const [assignData, setAssignData] = useState<{classIds: string[], teacherId: string}>({ classIds: [], teacherId: '' });
  const [searchQuery, setSearchQuery] = useState('');

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
    if (assignData.classIds.length === 0 || !assignData.teacherId) return osAlert.error('Error', 'Select at least one class and a teacher.');
    const res = await fetch('/api/classes', { method: 'PATCH', body: JSON.stringify(assignData) });
    if (res.ok) { 
      osToast.fire({ icon: 'success', title: `Assigned to ${assignData.classIds.length} class(es)` }); 
      setAssignData({classIds: [], teacherId: ''}); setSearchQuery(''); fetchData(); 
    }
  };

  const toggleClassSelection = (id: string) => {
    setAssignData(prev => ({ ...prev, classIds: prev.classIds.includes(id) ? prev.classIds.filter(cId => cId !== id) : [...prev.classIds, id] }));
  };

  const removeClass = (id: string) => setAssignData(prev => ({ ...prev, classIds: prev.classIds.filter(cId => cId !== id) }));

  const handleDelete = async (id: string) => {
    if (!(await osAlert.confirm('Delete Class?', 'Cannot delete if students are enrolled.')).isConfirmed) return;
    const res = await fetch(`/api/classes?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); }
    else osAlert.error('Error', (await res.json()).error);
  };

  const filteredClasses = classes.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6 h-fit">
        {/* CREATE CLASS */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Create Class</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div><label className="block text-sm font-medium mb-1">Class Name</label><input type="text" required value={newClassName} onChange={e=>setNewClassName(e.target.value)} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. CS-101" /></div>
            <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Create Class</button>
          </form>
        </div>

        {/* ASSIGN TEACHER */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><LinkIcon className="w-5 h-5 text-emerald-600"/> Assign Faculty</h2>
          <form onSubmit={handleAssign} className="space-y-5">
            <div>
              <label className="block text-sm font-medium mb-1">Select Teacher</label>
              <select value={assignData.teacherId} onChange={e=>setAssignData({...assignData, teacherId: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">-- Choose Teacher --</option>
                {teachers.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            <div className="space-y-3">
              <label className="block text-sm font-medium flex justify-between items-center">Select Classes <span className="text-xs text-blue-600 font-semibold bg-blue-50 border border-blue-100 px-2 py-0.5 rounded-full">{assignData.classIds.length} Selected</span></label>
              <div className="relative"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input type="text" placeholder="Filter classes..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="w-full bg-white border border-slate-300 rounded-lg py-2.5 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 shadow-sm" /></div>
              {assignData.classIds.length > 0 && (
                <div className="flex flex-wrap gap-2 p-2 border border-blue-100 rounded-lg bg-blue-50/50 max-h-24 overflow-y-auto">
                  {assignData.classIds.map(id => {
                    const c = classes.find(cls => cls.id === id);
                    if (!c) return null;
                    return <span key={id} className="bg-white text-blue-700 text-xs font-semibold px-2 py-1 rounded-md flex items-center gap-1 shadow-sm border border-blue-200">{c.name} <button type="button" onClick={() => removeClass(id)} className="hover:text-red-600 focus:outline-none ml-1"><X className="w-3 h-3"/></button></span>
                  })}
                </div>
              )}
              <div className="border border-slate-200 rounded-lg bg-slate-50 p-2 h-48 overflow-y-auto space-y-1 shadow-inner">
                {filteredClasses.map(c => (
                  <label key={c.id} className="flex items-center gap-3 p-2.5 hover:bg-white rounded-md cursor-pointer transition-all border border-transparent hover:border-slate-200 hover:shadow-sm"><input type="checkbox" checked={assignData.classIds.includes(c.id)} onChange={() => toggleClassSelection(c.id)} className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500" /><div className="flex flex-col"><span className="text-sm font-semibold text-slate-700">{c.name}</span><span className="text-[10px] text-slate-400">Current: {c.teacher.name}</span></div></label>
                ))}
              </div>
            </div>
            <button type="submit" disabled={assignData.classIds.length === 0 || !assignData.teacherId} className="w-full bg-emerald-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-emerald-700 flex justify-center items-center gap-2 disabled:opacity-50 transition-colors"><CheckSquare className="w-4 h-4" /> Batch Assign</button>
          </form>
        </div>
      </div>

      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col h-fit">
        <div className="p-6 border-b border-slate-100"><h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2"><BookOpen className="w-5 h-5 text-blue-600"/> Active Classes</h2></div>
        
        {/* DESKTOP TABLE */}
        <div className="hidden md:block overflow-x-auto p-6 pt-0">
          <table className="w-full text-left text-sm mt-4"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Class</th><th className="py-3 px-4">Assigned Teacher</th><th className="py-3 px-4">Students</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {classes.map(c => (
                <tr key={c.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-bold">{c.name}</td><td className="py-3 px-4 text-slate-500">{c.teacher.name}</td><td className="py-3 px-4">{c._count.students} Enrolled</td><td className="py-3 px-4 text-right"><button onClick={()=>handleDelete(c.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button></td></tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* MOBILE KEY-VALUE CARDS */}
        <div className="md:hidden flex flex-col gap-4 p-4 bg-slate-50/50">
          {classes.map(c => (
            <div key={c.id} className="bg-white border border-slate-200 rounded-lg shadow-sm">
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Class</span>
                <span className="text-sm font-bold text-slate-800">{c.name}</span>
              </div>
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Teacher</span>
                <span className="text-sm text-slate-600">{c.teacher.name}</span>
              </div>
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Students</span>
                <span className="text-sm text-slate-600">{c._count.students} Enrolled</span>
              </div>
              <div className="flex justify-between items-center p-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Actions</span>
                <button onClick={()=>handleDelete(c.id)} className="p-2 bg-red-50 text-red-500 hover:bg-red-100 rounded-md transition-colors"><Trash2 className="w-4 h-4"/></button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/classes/page.tsx"), classes_ui)

    print("\n>>> 2. OVERWRITING STUDENTS UI (LEFT/RIGHT MOBILE CARDS)...")

    students_ui = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit } from 'lucide-react';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function EntityMatrix() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', password: '', className: 'CS-101' });
  const [searchQuery, setSearchQuery] = useState('');

  const fetchEntities = useCallback(async () => {
    try {
      const res = await fetch('/api/students');
      const data = await res.json();
      if (data.success) setStudents(data.students);
    } catch (e) { osToast.fire({ icon: 'error', title: 'Data Fetch Failed' }); } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchEntities(); }, [fetchEntities]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const confirm = await osAlert.confirm('Register New Student?', `Create database entry for ${formData.name}.`);
    if (!confirm.isConfirmed) return;
    setIsSubmitting(true);
    try {
      const res = await fetch('/api/students', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osAlert.success('Registration Complete', `Student ${data.student.name} has been added.<br/>System ID: ${data.student.id.split('-')[0].toUpperCase()}`);
      setFormData({ name: '', email: '', password: '', className: 'CS-101' }); fetchEntities();
    } catch (err: any) { osAlert.error('Failed', err.message); } finally { setIsSubmitting(false); }
  };

  const handleEdit = async (student: any) => {
    const { value: formValues } = await osAlert.confirm('Edit Student', `
      <div class="text-left space-y-3 mt-4">
        <label class="block text-sm">Name</label><input id="swal-name" class="w-full border rounded p-2 text-sm" value="${student.name}">
        <label class="block text-sm mt-3">Class</label><input id="swal-class" class="w-full border rounded p-2 text-sm" value="${student.class.name}">
      </div>
    `);
    if (formValues) {
      const name = formValues?.name || (document.getElementById('swal-name') as HTMLInputElement)?.value;
      const className = formValues?.className || (document.getElementById('swal-class') as HTMLInputElement)?.value;
      const res = await fetch('/api/students', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: student.id, name, className }) });
      if (res.ok) { osToast.fire({ icon: 'success', title: 'Updated' }); fetchEntities(); }
    }
  };

  const handleDelete = async (id: string, name: string) => {
    const confirm = await osAlert.confirm('Delete Record?', `This will purge ${name}'s data. Cannot be undone.`);
    if (!confirm.isConfirmed) return;
    const res = await fetch(`/api/students?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchEntities(); } else { osAlert.error('Error', (await res.json()).error); }
  };

  const filtered = students.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.user.email.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600" /> Create Record</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} autoComplete="new-password" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Class Designation</label><input type="text" required value={formData.className} onChange={e => setFormData({...formData, className: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors mt-2">{isSubmitting ? 'Saving...' : 'Register Student'}</button>
        </form>
      </div>

      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col h-fit">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800">Student Directory</h2>
          <div className="relative"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input type="text" placeholder="Search..." value={searchQuery} onChange={e=>setSearchQuery(e.target.value)} className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
        </div>
        
        {/* DESKTOP TABLE */}
        <div className="hidden md:block overflow-x-auto p-6 pt-0">
          <table className="w-full text-left text-sm whitespace-nowrap mt-4">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200"><tr><th className="py-3 px-6">ID</th><th className="py-3 px-6">Name & Email</th><th className="py-3 px-6">Class</th><th className="py-3 px-6 text-right">Actions</th></tr></thead>
            <tbody className="divide-y divide-slate-200">
              {filtered.map(s => (
                <tr key={s.id} className="hover:bg-slate-50">
                  <td className="py-3 px-6 text-xs text-slate-400 font-mono">{s.id.split('-')[0].toUpperCase()}</td>
                  <td className="py-3 px-6"><div className="font-medium text-slate-800">{s.name}</div><div className="text-xs text-slate-500">{s.user.email}</div></td>
                  <td className="py-3 px-6"><span className="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full text-xs font-semibold">{s.class.name}</span></td>
                  <td className="py-3 px-6 text-right">
                    <button onClick={() => handleEdit(s)} className="p-1.5 text-slate-400 hover:text-blue-600"><Edit className="w-4 h-4" /></button>
                    <button onClick={() => handleDelete(s.id, s.name)} className="p-1.5 text-slate-400 hover:text-red-600 ml-2"><Trash2 className="w-4 h-4" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* MOBILE KEY-VALUE CARDS */}
        <div className="md:hidden flex flex-col gap-4 p-4 bg-slate-50/50">
          {filtered.map(s => (
            <div key={s.id} className="bg-white border border-slate-200 rounded-lg shadow-sm">
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Student</span>
                <div className="text-right"><div className="text-sm font-bold text-slate-800">{s.name}</div><div className="text-xs text-slate-500">{s.user.email}</div></div>
              </div>
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Class</span>
                <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs font-semibold">{s.class.name}</span>
              </div>
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sys ID</span>
                <span className="text-xs text-slate-500 font-mono">{s.id.split('-')[0].toUpperCase()}</span>
              </div>
              <div className="flex justify-between items-center p-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Actions</span>
                <div className="flex gap-2">
                  <button onClick={() => handleEdit(s)} className="p-2 bg-slate-50 text-slate-500 hover:text-blue-600 rounded-md transition-colors"><Edit className="w-4 h-4" /></button>
                  <button onClick={() => handleDelete(s.id, s.name)} className="p-2 bg-red-50 text-red-500 hover:bg-red-100 rounded-md transition-colors"><Trash2 className="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/students/page.tsx"), students_ui)

    print("\n>>> 3. OVERWRITING TEACHERS UI (LEFT/RIGHT MOBILE CARDS)...")

    teachers_ui = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit, Presentation } from 'lucide-react';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function TeachersMatrix() {
  const [teachers, setTeachers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [searchQuery, setSearchQuery] = useState('');

  const fetchEntities = useCallback(async () => {
    try {
      const res = await fetch('/api/teachers');
      const data = await res.json();
      if (data.success) setTeachers(data.teachers);
    } catch (e) { osToast.fire({ icon: 'error', title: 'Data Fetch Failed' }); } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchEntities(); }, [fetchEntities]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await fetch('/api/teachers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osAlert.success('Registration Complete', `Faculty ${data.teacher.name} has been added.`);
      setFormData({ name: '', email: '', password: '' }); fetchEntities();
    } catch (err: any) { osAlert.error('Failed', err.message); } finally { setIsSubmitting(false); }
  };

  const handleEdit = async (teacher: any) => {
    const { value: formValues } = await osAlert.confirm('Edit Faculty', `
      <div class="text-left space-y-3 mt-4">
        <label class="block text-sm">Full Name</label>
        <input id="swal-name" class="w-full border rounded p-2 text-sm" value="${teacher.name}">
      </div>
    `);
    if (formValues) {
      const name = formValues?.name || (document.getElementById('swal-name') as HTMLInputElement)?.value;
      const res = await fetch('/api/teachers', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: teacher.id, name }) });
      if (res.ok) { osToast.fire({ icon: 'success', title: 'Updated' }); fetchEntities(); }
    }
  };

  const handleDelete = async (id: string, name: string) => {
    const confirm = await osAlert.confirm('Delete Record?', `Purge ${name}? Cannot be undone.`);
    if (!confirm.isConfirmed) return;
    const res = await fetch(`/api/teachers?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchEntities(); } else { osAlert.error('Error', (await res.json()).error); }
  };

  const filtered = teachers.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()) || t.user.email.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600" /> Create Faculty</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} autoComplete="new-password" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 mt-2">{isSubmitting ? 'Saving...' : 'Register Teacher'}</button>
        </form>
      </div>

      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col h-fit">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2"><Presentation className="w-5 h-5 text-blue-600" /> Directory</h2>
          <div className="relative"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input type="text" placeholder="Search..." value={searchQuery} onChange={e=>setSearchQuery(e.target.value)} className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
        </div>
        
        {/* DESKTOP TABLE */}
        <div className="hidden md:block overflow-x-auto p-6 pt-0">
          <table className="w-full text-left text-sm whitespace-nowrap mt-4">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200"><tr><th className="py-3 px-6">Name</th><th className="py-3 px-6">Classes</th><th className="py-3 px-6 text-right">Actions</th></tr></thead>
            <tbody className="divide-y divide-slate-200">
              {filtered.map(t => (
                <tr key={t.id} className="hover:bg-slate-50">
                  <td className="py-3 px-6"><div className="font-medium text-slate-800">{t.name}</div><div className="text-xs text-slate-500">{t.user.email}</div></td>
                  <td className="py-3 px-6"><div className="flex flex-wrap gap-1">{t.classes.map((c:any) => <span key={c.name} className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs">{c.name}</span>)}</div></td>
                  <td className="py-3 px-6 text-right">
                    <button onClick={() => handleEdit(t)} className="p-1.5 text-slate-400 hover:text-blue-600"><Edit className="w-4 h-4" /></button>
                    <button onClick={() => handleDelete(t.id, t.name)} className="p-1.5 text-slate-400 hover:text-red-600 ml-2"><Trash2 className="w-4 h-4" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* MOBILE KEY-VALUE CARDS */}
        <div className="md:hidden flex flex-col gap-4 p-4 bg-slate-50/50">
          {filtered.map(t => (
            <div key={t.id} className="bg-white border border-slate-200 rounded-lg shadow-sm">
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Teacher</span>
                <div className="text-right"><div className="text-sm font-bold text-slate-800">{t.name}</div><div className="text-xs text-slate-500">{t.user.email}</div></div>
              </div>
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Classes</span>
                <div className="flex flex-wrap justify-end gap-1">
                  {t.classes.length > 0 ? t.classes.map((c:any) => <span key={c.name} className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs">{c.name}</span>) : <span className="text-xs text-slate-400">None</span>}
                </div>
              </div>
              <div className="flex justify-between items-center p-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Actions</span>
                <div className="flex gap-2">
                  <button onClick={() => handleEdit(t)} className="p-2 bg-slate-50 text-slate-500 hover:text-blue-600 rounded-md transition-colors"><Edit className="w-4 h-4" /></button>
                  <button onClick={() => handleDelete(t.id, t.name)} className="p-2 bg-red-50 text-red-500 hover:bg-red-100 rounded-md transition-colors"><Trash2 className="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/teachers/page.tsx"), teachers_ui)

    print("\n>>> 4. FIXING TELEMETRY (FORCING ENTERPRISE LIGHT THEME)...")

    telemetry_ui = """
'use client';

import { useState, useEffect } from 'react';
import { Activity, Users, Scan, Server, ShieldAlert, Clock } from 'lucide-react';
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
    fetch('/api/telemetry').then(res => res.json()).then(res => {
        if (res.success) setData(res);
        setLoading(false);
      }).catch(() => { osToast.fire({ icon: 'error', title: 'Telemetry Offline' }); setLoading(false); });
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600"><Users className="w-6 h-6" /></div>
          <div><p className="text-sm font-medium text-slate-500">Active Entities</p><h3 className="text-2xl font-bold text-slate-800">{loading ? '-' : data.metrics.totalStudents}</h3></div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600"><Scan className="w-6 h-6" /></div>
          <div><p className="text-sm font-medium text-slate-500">Today's Verifications</p><h3 className="text-2xl font-bold text-slate-800">{loading ? '-' : data.metrics.todayAttendance}</h3></div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-violet-50 flex items-center justify-center text-violet-600"><Server className="w-6 h-6" /></div>
          <div><p className="text-sm font-medium text-slate-500">Registered Classes</p><h3 className="text-2xl font-bold text-slate-800">{loading ? '-' : data.metrics.totalClasses}</h3></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm h-[400px] flex flex-col">
          <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Activity className="w-5 h-5 text-blue-600" /> 7-Day Activity Volume</h2>
          <div className="flex-1 w-full relative">
            {loading ? <div className="absolute inset-0 flex items-center justify-center text-slate-400">Loading...</div> : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <defs><linearGradient id="colorScans" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2563eb" stopOpacity={0.2}/><stop offset="95%" stopColor="#2563eb" stopOpacity={0}/></linearGradient></defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '0.5rem' }} itemStyle={{ color: '#0f172a', fontWeight: '500' }}/>
                  <Area type="monotone" dataKey="scans" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#colorScans)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm overflow-hidden flex flex-col h-[400px]">
          <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><ShieldAlert className="w-5 h-5 text-blue-600" /> Security Audit Log</h2>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
             {loading ? <div className="text-sm text-slate-400">Syncing...</div> : null}
             {!loading && data.recentLogs.map((log: any) => (
                <div key={log.id} className="border-l-2 border-blue-500 pl-4 py-1">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-sm font-semibold text-slate-700">{log.action.replace('_', ' ')}</span>
                    <span className="text-xs text-slate-400 flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(log.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  </div>
                  <div className="text-xs text-slate-500 truncate">{log.user.email} <span className="text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded ml-1">{log.user.role}</span></div>
                </div>
             ))}
             {!loading && data.recentLogs.length === 0 && <div className="text-sm text-slate-500">No events logged.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/telemetry/page.tsx"), telemetry_ui)

    print("\n====================================================")
    print(" [SUCCESS] MOBILE & THEME SYNC COMPLETE.            ")
    print("====================================================\n")

if __name__ == "__main__":
    step26_deploy()