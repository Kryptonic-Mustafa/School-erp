import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Syntax Repaired & UI Perfected: {path}")

def step38_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: TURBOPACK SYNTAX REPAIR              ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> REPAIRING STUDENTS UI (CLEAN OVERWRITE)...")

    # This is the full, optimized, and syntactically correct version of the Students Matrix
    students_ui = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit, GraduationCap, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { osToast, osAlert, osLoader } from '@/lib/alert_engine';
import SystemLoader from '@/components/SystemLoader';

export default function EntityMatrix() {
  const [students, setStudents] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [formData, setFormData] = useState<{name: string, email: string, password: string, classIds: string[]}>({ 
    name: '', email: '', password: '', classIds: [] 
  });
  
  const [searchQuery, setSearchQuery] = useState('');
  const [classSearchQuery, setClassSearchQuery] = useState('');
  
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
    } catch (e) { 
      osToast.fire({ icon: 'error', title: 'Data Fetch Failed' }); 
    } finally { 
      setLoading(false); 
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { setCurrentPage(1); }, [searchQuery]);

  const toggleClassSelection = (id: string) => {
    setFormData(prev => ({
      ...prev,
      classIds: prev.classIds.includes(id) 
        ? prev.classIds.filter(cId => cId !== id) 
        : [...prev.classIds, id]
    }));
  };

  const removeClass = (id: string) => {
    setFormData(prev => ({ ...prev, classIds: prev.classIds.filter(cId => cId !== id) }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.classIds.length === 0) return osAlert.error('Missing Data', 'Please assign at least one class.');

    setIsSubmitting(true);
    osLoader.show('Saving Record...');
    try {
      const res = await fetch('/api/students', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify(formData) 
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osAlert.success('Registration Complete', `Student ${data.student.name} added.`);
      setFormData({ name: '', email: '', password: '', classIds: [] }); 
      setClassSearchQuery(''); 
      fetchData();
    } catch (err: any) { 
      osAlert.error('Failed', err.message); 
    } finally { 
      setIsSubmitting(false); 
      osLoader.hide(); 
    }
  };

  const handleEdit = async (student: any) => {
    const classCheckboxes = classes.map(c => `
      <label class="flex items-center gap-2 p-2 hover:bg-slate-50 border-b border-slate-100 cursor-pointer text-sm transition-colors">
        <input type="checkbox" class="swal-class-cb w-4 h-4 text-blue-600 rounded focus:ring-blue-500" value="${c.id}" ${student.classes.some((sc:any) => sc.id === c.id) ? 'checked' : ''}>
        <span class="font-medium text-slate-700">${c.name}</span>
      </label>
    `).join('');

    const { value: formValues } = await osAlert.confirm('Edit Student', `
      <div class="text-left space-y-3 mt-2">
        <div><label class="block text-xs font-bold text-slate-400 mb-1 uppercase tracking-wider">Student Name</label><input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${student.name}"></div>
        <div>
          <label class="block text-xs font-bold text-slate-400 mb-1 uppercase tracking-wider">Assign Classes</label>
          <div class="border border-slate-300 rounded-lg bg-white h-32 overflow-y-auto custom-scrollbar">
            ${classCheckboxes}
          </div>
        </div>
      </div>
    `);
    
    if (formValues) {
      osLoader.show('Updating Matrix...');
      const name = (document.getElementById('swal-name') as HTMLInputElement)?.value;
      const classIds = Array.from(document.querySelectorAll('.swal-class-cb:checked')).map((cb: any) => cb.value);
      
      const res = await fetch('/api/students', { 
        method: 'PATCH', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({ id: student.id, name, classIds }) 
      });
      if (res.ok) { 
        osToast.fire({ icon: 'success', title: 'Updated Successfully' }); 
        fetchData(); 
      }
      osLoader.hide();
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!(await osAlert.confirm('Delete Record?', `Purge ${name}? Cannot be undone.`)).isConfirmed) return;
    osLoader.show('Purging Data...');
    const res = await fetch(`/api/students?id=${id}`, { method: 'DELETE' });
    if (res.ok) { 
      osToast.fire({ icon: 'success', title: 'Deleted' }); 
      fetchData(); 
    } else { 
      osAlert.error('Error', (await res.json()).error); 
    }
    osLoader.hide();
  };

  const filtered = students.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.user.email.toLowerCase().includes(searchQuery.toLowerCase()));
  const filteredClasses = classes.filter(c => c.name.toLowerCase().includes(classSearchQuery.toLowerCase()));

  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginatedData = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  if (loading) return <SystemLoader text="Syncing Student Matrix..." />;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      {/* CREATION FORM */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600" /> Create Record</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all" /></div>
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} autoComplete="new-password" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all" /></div>
          
          {/* PRO-SELECT BADGE UI */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest">Enroll in Classes</label>
            <div className="min-h-[46px] p-1.5 bg-slate-50 border border-slate-200 rounded-xl focus-within:ring-4 focus-within:ring-blue-50 focus-within:border-blue-500 transition-all">
               <div className="flex flex-wrap gap-1.5 mb-1">
                  {formData.classIds.map(id => {
                    const c = classes.find(cls => cls.id === id);
                    if (!c) return null;
                    return (
                      <span key={id} className="bg-white border border-slate-200 shadow-sm text-blue-700 text-[10px] font-bold px-2 py-1 rounded-lg flex items-center gap-1.5 animate-in zoom-in-90 duration-200">
                        {c.name}
                        <X onClick={() => removeClass(id)} className="w-3 h-3 cursor-pointer hover:text-red-500 transition-colors" />
                      </span>
                    );
                  })}
               </div>
               <div className="relative">
                 <Search className="w-3.5 h-3.5 absolute left-2 top-1/2 -translate-y-1/2 text-slate-400" />
                 <input 
                   type="text" 
                   placeholder={formData.classIds.length > 0 ? "" : "Search to assign classes..."}
                   className="w-full bg-transparent pl-7 pr-2 py-1 text-sm outline-none text-slate-700 placeholder:text-slate-400"
                   value={classSearchQuery}
                   onChange={e => setClassSearchQuery(e.target.value)}
                 />
               </div>
            </div>
            
            <div className="border border-slate-200 rounded-xl bg-white h-32 overflow-y-auto space-y-0.5 shadow-inner p-1 custom-scrollbar">
              {filteredClasses.length === 0 ? (
                <p className="text-xs text-slate-400 p-4 text-center">No classes matching "{classSearchQuery}"</p>
              ) : filteredClasses.map(c => (
                <label key={c.id} className="flex items-center gap-3 p-2.5 hover:bg-slate-50 rounded-md cursor-pointer transition-all border border-transparent">
                  <input 
                    type="checkbox" 
                    checked={formData.classIds.includes(c.id)} 
                    onChange={() => toggleClassSelection(c.id)} 
                    className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500 cursor-pointer" 
                  />
                  <span className="text-sm font-semibold text-slate-700">{c.name}</span>
                </label>
              ))}
            </div>
          </div>

          <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white rounded-lg py-3 text-sm font-bold hover:bg-blue-700 disabled:opacity-50 transition-all shadow-lg shadow-blue-100 mt-2">
            {isSubmitting ? 'Syncing...' : 'Register Student'}
          </button>
        </form>
      </div>

      {/* DIRECTORY SECTION */}
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col h-fit overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2"><GraduationCap className="w-5 h-5 text-blue-600" /> Student Directory</h2>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Quick search..." 
              value={searchQuery} 
              onChange={e=>setSearchQuery(e.target.value)} 
              className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white" 
            />
          </div>
        </div>
        
        {/* DESKTOP TABLE */}
        <div className="hidden md:block overflow-x-auto px-6 pt-4">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase text-[10px] tracking-widest">
              <tr><th className="py-3 px-6">System ID</th><th className="py-3 px-6">Identity</th><th className="py-3 px-6">Class Load</th><th className="py-3 px-6 text-right">Actions</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedData.map(s => (
                <tr key={s.id} className="hover:bg-slate-50 transition-colors group">
                  <td className="py-4 px-6 text-xs text-slate-400 font-mono">{s.id.split('-')[0].toUpperCase()}</td>
                  <td className="py-4 px-6">
                    <div className="font-bold text-slate-800">{s.name}</div>
                    <div className="text-xs text-slate-500">{s.user.email}</div>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex flex-wrap gap-1 max-w-[240px]">
                      {s.classes.map((c:any) => (
                        <span key={c.id} className="bg-white border border-slate-200 text-blue-600 px-2 py-0.5 rounded-md text-[10px] font-bold shadow-sm">
                          {c.name}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <button onClick={() => handleEdit(s)} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"><Edit className="w-4 h-4" /></button>
                    <button onClick={() => handleDelete(s.id, s.name)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg ml-1 transition-all"><Trash2 className="w-4 h-4" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* MOBILE CARDS */}
        <div className="md:hidden flex flex-col gap-4 p-4 bg-slate-50/50">
          {paginatedData.map(s => (
            <div key={s.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-bold text-slate-800">{s.name}</h3>
                  <p className="text-xs text-slate-500">{s.user.email}</p>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded uppercase">{s.id.split('-')[0]}</span>
              </div>
              <div className="flex flex-wrap gap-1 mb-4">
                {s.classes.map((c:any) => <span key={c.id} className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-[10px] font-bold">{c.name}</span>)}
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button onClick={() => handleEdit(s)} className="p-2 bg-slate-50 text-slate-500 rounded-lg border border-slate-200"><Edit className="w-4 h-4" /></button>
                <button onClick={() => handleDelete(s.id, s.name)} className="p-2 bg-red-50 text-red-500 rounded-lg border border-red-100"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          ))}
        </div>

        {/* PAGINATION */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/80 flex flex-col sm:flex-row justify-between items-center gap-4">
          <span className="text-xs text-slate-500 font-medium italic">
            Displaying <span className="text-slate-800 font-bold">{(currentPage - 1) * itemsPerPage + 1}</span> - <span className="text-slate-800 font-bold">{Math.min(currentPage * itemsPerPage, filtered.length)}</span> of {filtered.length}
          </span>
          <div className="flex gap-2">
            <button disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)} className="px-4 py-2 flex items-center gap-1 text-xs font-bold text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 disabled:opacity-30 transition-all shadow-sm"><ChevronLeft className="w-4 h-4"/> Prev</button>
            <button disabled={currentPage >= totalPages} onClick={() => setCurrentPage(p => p + 1)} className="px-4 py-2 flex items-center gap-1 text-xs font-bold text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 disabled:opacity-30 transition-all shadow-sm">Next <ChevronRight className="w-4 h-4"/></button>
          </div>
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/students/page.tsx"), students_ui)

    print("\n====================================================")
    print(" [SUCCESS] SYNTAX REPAIRED. READY FOR RE-DEPLOY.    ")
    print("====================================================\n")

if __name__ == "__main__":
    step38_deploy()