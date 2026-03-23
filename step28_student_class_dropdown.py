import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] UI Upgraded: {path}")

def step28_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: STUDENT SEARCHABLE COMBO-BOX         ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> REWRITING STUDENTS UI (INJECTING SEARCHABLE DROPDOWN)...")

    students_ui = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit, GraduationCap } from 'lucide-react';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function EntityMatrix() {
  const [students, setStudents] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]); // New state for classes
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [formData, setFormData] = useState({ name: '', email: '', password: '', className: '' });
  
  // Search UI State
  const [searchQuery, setSearchQuery] = useState('');
  const [classSearchQuery, setClassSearchQuery] = useState('');
  const [isClassDropdownOpen, setIsClassDropdownOpen] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [sRes, cRes] = await Promise.all([
        fetch('/api/students').then(r => r.json()),
        fetch('/api/classes').then(r => r.json())
      ]);
      if (sRes.success) setStudents(sRes.students);
      if (cRes.success) setClasses(cRes.classes);
    } catch (e) { 
      osToast.fire({ icon: 'error', title: 'Data Fetch Failed' }); 
    } finally { 
      setLoading(false); 
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.className) return osAlert.error('Missing Data', 'Please select a class designation.');

    const confirm = await osAlert.confirm('Register New Student?', `Create database entry for ${formData.name}.`);
    if (!confirm.isConfirmed) return;
    
    setIsSubmitting(true);
    try {
      const res = await fetch('/api/students', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osAlert.success('Registration Complete', `Student ${data.student.name} has been added.<br/>System ID: ${data.student.id.split('-')[0].toUpperCase()}`);
      
      // Reset Form
      setFormData({ name: '', email: '', password: '', className: '' }); 
      setClassSearchQuery('');
      fetchData();
    } catch (err: any) { 
      osAlert.error('Failed', err.message); 
    } finally { 
      setIsSubmitting(false); 
    }
  };

  const handleEdit = async (student: any) => {
    // Generate dropdown options dynamically from the fetched classes
    const classOptions = classes.map(c => 
      `<option value="${c.name}" ${student.class.name === c.name ? 'selected' : ''}>${c.name}</option>`
    ).join('');

    const { value: formValues } = await osAlert.confirm('Edit Student', `
      <div class="text-left space-y-3 mt-2">
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Student Name</label>
          <input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${student.name}">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Class Designation</label>
          <select id="swal-class" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 bg-white">
            ${classOptions}
          </select>
        </div>
      </div>
    `);
    
    if (formValues) {
      const name = formValues?.name || (document.getElementById('swal-name') as HTMLInputElement)?.value;
      const className = formValues?.className || (document.getElementById('swal-class') as HTMLSelectElement)?.value;
      
      const res = await fetch('/api/students', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: student.id, name, className }) });
      if (res.ok) { osToast.fire({ icon: 'success', title: 'Updated' }); fetchData(); }
    }
  };

  const handleDelete = async (id: string, name: string) => {
    const confirm = await osAlert.confirm('Delete Record?', `This will purge ${name}'s data. Cannot be undone.`);
    if (!confirm.isConfirmed) return;
    const res = await fetch(`/api/students?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); } else { osAlert.error('Error', (await res.json()).error); }
  };

  // Filters for Directory Search
  const filtered = students.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.user.email.toLowerCase().includes(searchQuery.toLowerCase()));
  
  // Filters for the Class Combo-box
  const filteredClasses = classes.filter(c => c.name.toLowerCase().includes(classSearchQuery.toLowerCase()));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      {/* CREATE RECORD FORM */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600" /> Create Record</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} autoComplete="new-password" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          
          {/* SEARCHABLE CLASS COMBO-BOX */}
          <div className="relative">
            <label className="block text-sm font-medium mb-1">Class Designation</label>
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search & select class..." 
                value={classSearchQuery}
                onChange={e => {
                  setClassSearchQuery(e.target.value);
                  setFormData({...formData, className: e.target.value});
                  setIsClassDropdownOpen(true);
                }}
                onFocus={() => setIsClassDropdownOpen(true)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2.5 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {isClassDropdownOpen && (
              <div className="absolute z-20 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                <div className="p-2 border-b border-slate-100 flex justify-between items-center bg-slate-50 sticky top-0 z-10">
                  <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Available Classes</span>
                  <button type="button" onClick={() => setIsClassDropdownOpen(false)} className="text-xs text-blue-600 font-medium hover:text-blue-800 bg-blue-50 px-2 py-1 rounded">Close</button>
                </div>
                {filteredClasses.length === 0 ? (
                  <div className="p-3 text-xs text-slate-500 text-center italic">Will create new class: "{classSearchQuery}"</div>
                ) : filteredClasses.map(c => (
                  <div 
                    key={c.id} 
                    onClick={() => {
                      setFormData({...formData, className: c.name});
                      setClassSearchQuery(c.name);
                      setIsClassDropdownOpen(false);
                    }}
                    className="p-3 text-sm hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-0 font-medium text-slate-700"
                  >
                    {c.name}
                  </div>
                ))}
              </div>
            )}
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
              {!loading && filtered.length === 0 && <tr><td colSpan={4} className="py-8 text-center text-slate-500">No student records found.</td></tr>}
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

    print("\n====================================================")
    print(" [SUCCESS] STUDENT DROPDOWN UPGRADE COMPLETE.       ")
    print("====================================================\n")

if __name__ == "__main__":
    step28_deploy()