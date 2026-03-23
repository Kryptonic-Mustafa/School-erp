import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] UI Patched: {path}")

def step22_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: CONTAINED MULTI-SELECT UX FIX        ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> REWRITING CLASSES UI (CONTAINED INLINE LIST)...")

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
      osToast.fire({ icon: 'success', title: `Teacher assigned to ${assignData.classIds.length} class(es)` }); 
      setAssignData({classIds: [], teacherId: ''}); 
      setSearchQuery('');
      fetchData(); 
    }
  };

  const toggleClassSelection = (id: string) => {
    setAssignData(prev => ({
      ...prev,
      classIds: prev.classIds.includes(id) 
        ? prev.classIds.filter(cId => cId !== id) 
        : [...prev.classIds, id]
    }));
  };

  const removeClass = (id: string) => {
    setAssignData(prev => ({ ...prev, classIds: prev.classIds.filter(cId => cId !== id) }));
  };

  const handleDelete = async (id: string) => {
    if (!(await osAlert.confirm('Delete Class?', 'Cannot delete if students are enrolled.')).isConfirmed) return;
    const res = await fetch(`/api/classes?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); }
    else { osAlert.error('Error', (await res.json()).error); }
  };

  const filteredClasses = classes.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6 h-fit">
        
        {/* CREATE CLASS CARD */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Create Class</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Class Name</label>
              <input type="text" required value={newClassName} onChange={e=>setNewClassName(e.target.value)} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. CS-101" />
            </div>
            <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Create Class</button>
          </form>
        </div>

        {/* ASSIGN TEACHER CARD (CONTAINED UI) */}
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
              <label className="block text-sm font-medium flex justify-between items-center">
                Select Classes 
                <span className="text-xs text-blue-600 font-semibold bg-blue-50 border border-blue-100 px-2 py-0.5 rounded-full">{assignData.classIds.length} Selected</span>
              </label>

              {/* SEARCH INPUT */}
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input 
                  type="text" 
                  placeholder="Filter classes..." 
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-lg py-2.5 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                />
              </div>

              {/* BADGES CONTAINER */}
              {assignData.classIds.length > 0 && (
                <div className="flex flex-wrap gap-2 p-2 border border-blue-100 rounded-lg bg-blue-50/50 max-h-24 overflow-y-auto">
                  {assignData.classIds.map(id => {
                    const c = classes.find(cls => cls.id === id);
                    if (!c) return null;
                    return (
                      <span key={id} className="bg-white text-blue-700 text-xs font-semibold px-2 py-1 rounded-md flex items-center gap-1 shadow-sm border border-blue-200">
                        {c.name}
                        <button type="button" onClick={() => removeClass(id)} className="hover:text-red-600 focus:outline-none ml-1 transition-colors">
                          <X className="w-3 h-3"/>
                        </button>
                      </span>
                    );
                  })}
                </div>
              )}

              {/* INLINE SCROLLABLE LIST */}
              <div className="border border-slate-200 rounded-lg bg-slate-50 p-2 h-48 overflow-y-auto space-y-1 shadow-inner">
                {filteredClasses.length === 0 ? (
                  <p className="text-xs text-slate-400 p-4 text-center">No classes found matching "{searchQuery}".</p>
                ) : filteredClasses.map(c => (
                  <label key={c.id} className="flex items-center gap-3 p-2.5 hover:bg-white rounded-md cursor-pointer transition-all border border-transparent hover:border-slate-200 hover:shadow-sm">
                    <input 
                      type="checkbox" 
                      checked={assignData.classIds.includes(c.id)}
                      onChange={() => toggleClassSelection(c.id)}
                      className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500" 
                    />
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-slate-700">{c.name}</span>
                      <span className="text-[10px] text-slate-400">Current: {c.teacher.name}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <button type="submit" disabled={assignData.classIds.length === 0 || !assignData.teacherId} className="w-full bg-emerald-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-emerald-700 flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              <CheckSquare className="w-4 h-4" /> Batch Assign
            </button>
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

    print("\n====================================================")
    print(" [SUCCESS] CONTAINED MULTI-SELECT DEPLOYED.         ")
    print("====================================================\n")

if __name__ == "__main__":
    step22_deploy()