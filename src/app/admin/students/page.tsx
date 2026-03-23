'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, Trash2, Edit, GraduationCap, X } from 'lucide-react';
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

  const toggleClassSelection = (id: string) => {
    setFormData(prev => ({
      ...prev,
      classIds: prev.classIds.includes(id) ? prev.classIds.filter(cId => cId !== id) : [...prev.classIds, id]
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
      const res = await fetch('/api/students', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osAlert.success('Registration Complete', `Student ${data.student.name} added.<br/>ID: ${data.student.id.split('-')[0].toUpperCase()}`);
      setFormData({ name: '', email: '', password: '', classIds: [] }); setClassSearchQuery(''); fetchData();
    } catch (err: any) { osAlert.error('Failed', err.message); } finally { setIsSubmitting(false); osLoader.hide(); }
  };

  const handleEdit = async (student: any) => {
    // Generate inner HTML checkboxes for SweetAlert
    const classCheckboxes = classes.map(c => `
      <label class="flex items-center gap-2 p-2 hover:bg-slate-50 border-b border-slate-100 cursor-pointer text-sm">
        <input type="checkbox" class="swal-class-cb w-4 h-4 text-blue-600 rounded focus:ring-blue-500" value="${c.id}" ${student.classes.some((sc:any) => sc.id === c.id) ? 'checked' : ''}>
        ${c.name}
      </label>
    `).join('');

    const { value: formValues } = await osAlert.confirm('Edit Student', `
      <div class="text-left space-y-3 mt-2">
        <div><label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Student Name</label><input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${student.name}"></div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Assign Classes</label>
          <div class="border border-slate-300 rounded-lg bg-white h-32 overflow-y-auto">
            ${classCheckboxes}
          </div>
        </div>
      </div>
    `);
    
    if (formValues) {
      const name = (document.getElementById('swal-name') as HTMLInputElement)?.value;
      // Extract all checked values from the DOM
      const classIds = Array.from(document.querySelectorAll('.swal-class-cb:checked')).map((cb: any) => cb.value);
      
      const res = await fetch('/api/students', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: student.id, name, classIds }) });
      if (res.ok) { osToast.fire({ icon: 'success', title: 'Updated' }); fetchData(); }
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!(await osAlert.confirm('Delete Record?', `Purge ${name}? Cannot be undone.`)).isConfirmed) return;
    osLoader.show('Deleting...');
    const res = await fetch(`/api/students?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); osLoader.hide(); } else { osLoader.hide();  osAlert.error('Error', (await res.json()).error); }
  };

  const filtered = students.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.user.email.toLowerCase().includes(searchQuery.toLowerCase()));
  const filteredClasses = classes.filter(c => c.name.toLowerCase().includes(classSearchQuery.toLowerCase()));

  if (loading) return <SystemLoader text="Loading Records..." />;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600" /> Create Record</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} autoComplete="off" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} autoComplete="new-password" className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" /></div>
          
          <div className="space-y-3">
            <label className="block text-sm font-medium flex justify-between items-center">Classes <span className="text-xs text-blue-600 font-semibold bg-blue-50 px-2 py-0.5 rounded-full">{formData.classIds.length} Selected</span></label>
            <div className="relative"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input type="text" placeholder="Filter classes..." value={classSearchQuery} onChange={e => setClassSearchQuery(e.target.value)} className="w-full bg-white border border-slate-300 rounded-lg py-2.5 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 shadow-sm" /></div>
            
            {formData.classIds.length > 0 && (
              <div className="flex flex-wrap gap-2 p-2 border border-blue-100 rounded-lg bg-blue-50/50 max-h-24 overflow-y-auto">
                {formData.classIds.map(id => {
                  const c = classes.find(cls => cls.id === id);
                  if (!c) return null;
                  return <span key={id} className="bg-white text-blue-700 text-xs font-semibold px-2 py-1 rounded-md flex items-center gap-1 shadow-sm border border-blue-200">{c.name} <button type="button" onClick={() => removeClass(id)} className="hover:text-red-600 focus:outline-none ml-1"><X className="w-3 h-3"/></button></span>
                })}
              </div>
            )}
            
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
        <div className="hidden md:block overflow-x-auto p-6 pt-0">
          <table className="w-full text-left text-sm whitespace-nowrap mt-4">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200"><tr><th className="py-3 px-6">ID</th><th className="py-3 px-6">Name & Email</th><th className="py-3 px-6">Classes</th><th className="py-3 px-6 text-right">Actions</th></tr></thead>
            <tbody className="divide-y divide-slate-200">
              {filtered.map(s => (
                <tr key={s.id} className="hover:bg-slate-50">
                  <td className="py-3 px-6 text-xs text-slate-400 font-mono">{s.id.split('-')[0].toUpperCase()}</td>
                  <td className="py-3 px-6"><div className="font-medium text-slate-800">{s.name}</div><div className="text-xs text-slate-500">{s.user.email}</div></td>
                  <td className="py-3 px-6">
                    <div className="flex flex-wrap gap-1 max-w-[200px]">
                      {s.classes.map((c:any) => <span key={c.id} className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-[10px] font-semibold">{c.name}</span>)}
                    </div>
                  </td>
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
      </div>
    </div>
  );
}
