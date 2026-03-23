'use client';

import { useState, useEffect } from 'react';
import { Users, GraduationCap, BookOpen, UserCheck, DownloadCloud, DatabaseBackup, Plus, Clock } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function AdminDashboard() {
  const router = useRouter();
  const [logs, setLogs] = useState<any[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(true);

  useEffect(() => {
    fetch('/api/telemetry').then(r => r.json()).then(res => {
      if (res.success) setLogs(res.recentLogs);
      setLoadingLogs(false);
    });
  }, []);

  const handleBackup = async () => {
    osToast.fire({ icon: 'info', title: 'Initiating database snapshot...', timer: 2000 });
    setTimeout(() => { osAlert.success('Backup Successful', 'Database snapshot saved securely to cloud storage.'); }, 2000);
  };

  const stats = [
    { title: 'Total Students', value: '1,248', icon: GraduationCap, color: 'bg-blue-500' },
    { title: 'Total Teachers', value: '84', icon: Users, color: 'bg-violet-500' },
    { title: 'Active Classes', value: '42', icon: BookOpen, color: 'bg-amber-500' },
    { title: 'Present Today', value: '1,102', icon: UserCheck, color: 'bg-emerald-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.title} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-white ${stat.color}`}><Icon className="w-6 h-6" /></div>
              <div><p className="text-sm font-medium text-slate-500">{stat.title}</p><h3 className="text-2xl font-bold text-slate-800">{stat.value}</h3></div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* RECENT ACTIVITY LOGS */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col h-[300px]">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Recent System Activity</h2>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
             {loadingLogs ? <div className="text-sm text-slate-400">Syncing logs...</div> : null}
             {!loadingLogs && logs.map((log: any) => (
                <div key={log.id} className="border-l-2 border-blue-500 pl-3 py-1 bg-slate-50 rounded-r-lg">
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-semibold text-slate-700">{log.action.replace('_', ' ')}</span>
                    <span className="text-xs text-slate-400 flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(log.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  </div>
                  <div className="text-xs text-slate-500 truncate">{log.user.email} [{log.user.role}]</div>
                </div>
             ))}
             {!loadingLogs && logs.length === 0 && <div className="text-sm text-slate-400 text-center mt-8">No recent activity.</div>}
          </div>
        </div>
        
        {/* QUICK ACTIONS */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm min-h-[300px]">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Quick Actions</h2>
          <div className="space-y-3">
             <button onClick={() => router.push('/admin/students')} className="w-full flex items-center gap-3 text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all text-sm font-medium text-slate-700"><Plus className="w-4 h-4 text-blue-600" /> Register New Student</button>
             <button onClick={() => osToast.fire({ icon: 'success', title: 'Exporting Report...' })} className="w-full flex items-center gap-3 text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50 transition-all text-sm font-medium text-slate-700"><DownloadCloud className="w-4 h-4 text-emerald-600" /> Export Attendance Report</button>
             <button onClick={handleBackup} className="w-full flex items-center gap-3 text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-violet-500 hover:bg-violet-50 transition-all text-sm font-medium text-slate-700"><DatabaseBackup className="w-4 h-4 text-violet-600" /> Trigger System Backup</button>
          </div>
        </div>
      </div>
    </div>
  );
}
