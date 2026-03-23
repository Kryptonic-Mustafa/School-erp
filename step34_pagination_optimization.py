import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Optimized with Pagination: {path}")

def step34_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: SYSTEM PAGINATION & DOM OPTIMIZATION ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. OPTIMIZING STUDENTS MATRIX (10-ITEMS PER PAGE)...")

    students_ui = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit, GraduationCap, ChevronLeft, ChevronRight } from 'lucide-react';
import { osToast, osAlert, osLoader } from '@/lib/alert_engine';
import SystemLoader from '@/components/SystemLoader';

export default function EntityMatrix() {
  const [students, setStudents] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<{name: string, email: string, password: string, classIds: string[]}>({ name: '', email: '', password: '', classIds: [] });
  
  const [searchQuery, setSearchQuery] = useState('');
  const [classSearchQuery, setClassSearchQuery] = useState('');
  
  // PAGINATION ENGINE
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const fetchData = useCallback(async () => {
    try {
      const [sRes, cRes] = await Promise.all([
        fetch('/api/students').then(r => r.json()),
        fetch('/api/classes').then(r => r.json())
      ]);
      if (sRes.success) setStudents(sRes.students);
      if (cRes.success) setClasses(cRes.classes);
    } catch (e) { osToast.fire({ icon: 'error', title: 'Data Fetch Failed' }); } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Reset to page 1 when searching
  useEffect(() => { setCurrentPage(1); }, [searchQuery]);

  const toggleClassSelection = (id: string) => setFormData(prev => ({ ...prev, classIds: prev.classIds.includes(id) ? prev.classIds.filter(cId => cId !== id) : [...prev.classIds, id] }));
  const removeClass = (id: string) => setFormData(prev => ({ ...prev, classIds: prev.classIds.filter(cId => cId !== id) }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.classIds.length === 0) return osAlert.error('Missing Data', 'Please assign at least one class.');
    setIsSubmitting(true);
    osLoader.show('Saving Record...');
    try {
      const res = await fetch('/api/students', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osAlert.success('Registration Complete', `Student ${data.student.name} added.`);
      setFormData({ name: '', email: '', password: '', classIds: [] }); setClassSearchQuery(''); fetchData();
    } catch (err: any) { osAlert.error('Failed', err.message); } finally { setIsSubmitting(false); osLoader.hide(); }
  };

  const handleEdit = async (student: any) => {
    const classCheckboxes = classes.map(c => `
      <label class="flex items-center gap-2 p-2 hover:bg-slate-50 border-b border-slate-100 cursor-pointer text-sm">
        <input type="checkbox" class="swal-class-cb w-4 h-4 text-blue-600 rounded focus:ring-blue-500" value="${c.id}" ${student.classes.some((sc:any) => sc.id === c.id) ? 'checked' : ''}>
        ${c.name}
      </label>
    `).join('');

    const { value: formValues } = await osAlert.confirm('Edit Student', `
      <div class="text-left space-y-3 mt-2">
        <div><label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Student Name</label><input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${student.name}"></div>
        <div><label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Assign Classes</label><div class="border border-slate-300 rounded-lg bg-white h-32 overflow-y-auto">${classCheckboxes}</div></div>
      </div>
    `);
    
    if (formValues) {
      osLoader.show('Updating...');
      const name = (document.getElementById('swal-name') as HTMLInputElement)?.value;
      const classIds = Array.from(document.querySelectorAll('.swal-class-cb:checked')).map((cb: any) => cb.value);
      const res = await fetch('/api/students', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: student.id, name, classIds }) });
      if (res.ok) { osToast.fire({ icon: 'success', title: 'Updated' }); fetchData(); }
      osLoader.hide();
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!(await osAlert.confirm('Delete Record?', `Purge ${name}? Cannot be undone.`)).isConfirmed) return;
    osLoader.show('Deleting...');
    const res = await fetch(`/api/students?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); } else { osAlert.error('Error', (await res.json()).error); }
    osLoader.hide();
  };

  const filtered = students.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.user.email.toLowerCase().includes(searchQuery.toLowerCase()));
  const filteredClasses = classes.filter(c => c.name.toLowerCase().includes(classSearchQuery.toLowerCase()));

  // DATA SLICING FOR PAGINATION
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginatedData = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  if (loading) return <SystemLoader text="Loading Records..." />;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* FORM SECTION KEEPS ORIGINAL CODE... */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600" /> Create Record</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} autoComplete="new-password" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div className="space-y-3">
            <label className="block text-sm font-medium flex justify-between items-center">Classes <span className="text-xs text-blue-600 font-semibold bg-blue-50 px-2 py-0.5 rounded-full">{formData.classIds.length} Selected</span></label>
            <div className="relative"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input type="text" placeholder="Filter classes..." value={classSearchQuery} onChange={e => setClassSearchQuery(e.target.value)} className="w-full bg-white border border-slate-300 rounded-lg py-2.5 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 shadow-sm" /></div>
            <div className="border border-slate-200 rounded-lg bg-slate-50 p-2 h-40 overflow-y-auto space-y-1 shadow-inner">
              {filteredClasses.length === 0 ? <p className="text-xs text-slate-400 p-4 text-center">No classes found.</p> : filteredClasses.map(c => (
                <label key={c.id} className="flex items-center gap-3 p-2.5 hover:bg-white rounded-md cursor-pointer transition-all border border-transparent hover:border-slate-200 hover:shadow-sm"><input type="checkbox" checked={formData.classIds.includes(c.id)} onChange={() => toggleClassSelection(c.id)} className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500" /><span className="text-sm font-semibold text-slate-700">{c.name}</span></label>
              ))}
            </div>
          </div>
          <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors mt-2">{isSubmitting ? 'Saving...' : 'Register Student'}</button>
        </form>
      </div>

      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col h-fit">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2"><GraduationCap className="w-5 h-5 text-blue-600" /> Student Directory</h2>
          <div className="relative"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input type="text" placeholder="Search students..." value={searchQuery} onChange={e=>setSearchQuery(e.target.value)} className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" /></div>
        </div>
        
        {/* DESKTOP TABLE */}
        <div className="hidden md:block overflow-x-auto px-6 pt-4">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200"><tr><th className="py-3 px-6">ID</th><th className="py-3 px-6">Name & Email</th><th className="py-3 px-6">Classes</th><th className="py-3 px-6 text-right">Actions</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedData.map(s => (
                <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-6 text-xs text-slate-400 font-mono">{s.id.split('-')[0].toUpperCase()}</td>
                  <td className="py-3 px-6"><div className="font-medium text-slate-800">{s.name}</div><div className="text-xs text-slate-500">{s.user.email}</div></td>
                  <td className="py-3 px-6"><div className="flex flex-wrap gap-1 max-w-[200px]">{s.classes.map((c:any) => <span key={c.id} className="bg-blue-50 text-blue-700 border border-blue-100 px-2 py-0.5 rounded-md text-[10px] font-semibold shadow-sm">{c.name}</span>)}</div></td>
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
          {paginatedData.map(s => (
            <div key={s.id} className="bg-white border border-slate-200 rounded-lg shadow-sm">
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Student</span>
                <div className="text-right"><div className="text-sm font-bold text-slate-800">{s.name}</div><div className="text-xs text-slate-500">{s.user.email}</div></div>
              </div>
              <div className="flex justify-between items-center p-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Classes</span>
                <div className="flex flex-wrap justify-end gap-1">
                  {s.classes.map((c:any) => <span key={c.id} className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-[10px] font-semibold">{c.name}</span>)}
                </div>
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

        {/* UNIVERSAL PAGINATION FOOTER */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 rounded-b-xl flex flex-col sm:flex-row justify-between items-center gap-4">
          <span className="text-xs text-slate-500 font-medium">
            Showing <strong className="text-slate-800">{(currentPage - 1) * itemsPerPage + 1}</strong> to <strong className="text-slate-800">{Math.min(currentPage * itemsPerPage, filtered.length)}</strong> of <strong className="text-slate-800">{filtered.length}</strong> entries
          </span>
          <div className="flex gap-2">
            <button disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)} className="px-3 py-1.5 flex items-center gap-1 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition-colors shadow-sm"><ChevronLeft className="w-4 h-4"/> Prev</button>
            <button disabled={currentPage >= totalPages} onClick={() => setCurrentPage(p => p + 1)} className="px-3 py-1.5 flex items-center gap-1 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition-colors shadow-sm">Next <ChevronRight className="w-4 h-4"/></button>
          </div>
        </div>

      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/students/page.tsx"), students_ui)

    print("\n>>> 2. OPTIMIZING TEACHERS MATRIX...")

    teachers_ui = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit, Presentation, ChevronLeft, ChevronRight } from 'lucide-react';
import { osToast, osAlert, osLoader } from '@/lib/alert_engine';
import SystemLoader from '@/components/SystemLoader';

export default function TeachersMatrix() {
  const [teachers, setTeachers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [searchQuery, setSearchQuery] = useState('');

  // PAGINATION ENGINE
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const fetchEntities = useCallback(async () => {
    try {
      const res = await fetch('/api/teachers');
      const data = await res.json();
      if (data.success) setTeachers(data.teachers);
    } catch (e) { osToast.fire({ icon: 'error', title: 'Data Fetch Failed' }); } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchEntities(); }, [fetchEntities]);
  useEffect(() => { setCurrentPage(1); }, [searchQuery]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    osLoader.show('Saving Record...');
    try {
      const res = await fetch('/api/teachers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osAlert.success('Registration Complete', `Faculty ${data.teacher.name} has been added.`);
      setFormData({ name: '', email: '', password: '' }); fetchEntities();
    } catch (err: any) { osAlert.error('Failed', err.message); } finally { setIsSubmitting(false); osLoader.hide(); }
  };

  const handleEdit = async (teacher: any) => {
    const { value: formValues } = await osAlert.confirm('Edit Faculty', `
      <div class="text-left mt-2">
        <label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Faculty Name</label>
        <input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${teacher.name}">
      </div>
    `);
    if (formValues) {
      osLoader.show('Updating...');
      const name = formValues?.name || (document.getElementById('swal-name') as HTMLInputElement)?.value;
      const res = await fetch('/api/teachers', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: teacher.id, name }) });
      if (res.ok) { osToast.fire({ icon: 'success', title: 'Updated' }); fetchEntities(); }
      osLoader.hide();
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!(await osAlert.confirm('Delete Record?', `Purge ${name}? Cannot be undone.`)).isConfirmed) return;
    osLoader.show('Deleting...');
    const res = await fetch(`/api/teachers?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchEntities(); } else { osAlert.error('Error', (await res.json()).error); }
    osLoader.hide();
  };

  const filtered = teachers.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()) || t.user.email.toLowerCase().includes(searchQuery.toLowerCase()));
  
  // DATA SLICING FOR PAGINATION
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginatedData = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  if (loading) return <SystemLoader text="Loading Records..." />;

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
        <div className="hidden md:block overflow-x-auto px-6 pt-4">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200"><tr><th className="py-3 px-6">Name</th><th className="py-3 px-6">Classes</th><th className="py-3 px-6 text-right">Actions</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedData.map(t => (
                <tr key={t.id} className="hover:bg-slate-50 transition-colors">
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
          {paginatedData.map(t => (
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
        
        {/* PAGINATION FOOTER */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 rounded-b-xl flex flex-col sm:flex-row justify-between items-center gap-4">
          <span className="text-xs text-slate-500 font-medium">
            Showing <strong className="text-slate-800">{(currentPage - 1) * itemsPerPage + 1}</strong> to <strong className="text-slate-800">{Math.min(currentPage * itemsPerPage, filtered.length)}</strong> of <strong className="text-slate-800">{filtered.length}</strong> entries
          </span>
          <div className="flex gap-2">
            <button disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)} className="px-3 py-1.5 flex items-center gap-1 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition-colors shadow-sm"><ChevronLeft className="w-4 h-4"/> Prev</button>
            <button disabled={currentPage >= totalPages} onClick={() => setCurrentPage(p => p + 1)} className="px-3 py-1.5 flex items-center gap-1 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition-colors shadow-sm">Next <ChevronRight className="w-4 h-4"/></button>
          </div>
        </div>

      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/teachers/page.tsx"), teachers_ui)

    print("\n====================================================")
    print(" [SUCCESS] DATA MATRICES OPTIMIZED AND PAGINATED.   ")
    print("====================================================\n")

if __name__ == "__main__":
    step34_deploy()