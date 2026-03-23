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
