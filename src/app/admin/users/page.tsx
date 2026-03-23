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
          <div><label className="block text-sm font-medium mb-1">Email</label><input type="email" required autoComplete="off" data-lpignore="true" onChange={e=>setFormData({...formData, email: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" /></div>
          <div><label className="block text-sm font-medium mb-1">Password</label><input type="password" required autoComplete="new-password" data-lpignore="true" onChange={e=>setFormData({...formData, password: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" /></div>
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
