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
