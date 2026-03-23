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
