'use client';

import { useState, useEffect } from 'react';
import { CalendarDays, CheckCircle, XCircle, Clock } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function AttendanceManager() {
  const [students, setStudents] = useState<any[]>([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [loading, setLoading] = useState(true);

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const daysArray = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const fetchAttendance = async () => {
    setLoading(true);
    const month = currentDate.getMonth() + 1;
    const year = currentDate.getFullYear();
    const res = await fetch(`/api/attendance?month=${month}&year=${year}`);
    const data = await res.json();
    if (data.success) setStudents(data.students);
    setLoading(false);
  };

  useEffect(() => { fetchAttendance(); }, [currentDate]);

  const changeMonth = (offset: number) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + offset);
    setCurrentDate(newDate);
  };

  const handleCellClick = async (studentId: string, day: number, currentStatus: string) => {
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    
    const { value: newStatus } = await osAlert.confirm('Modify Attendance', `
      <select id="swal-status" class="w-full border rounded-lg p-3 text-sm mt-4 focus:ring-2 focus:ring-blue-500">
        <option value="PRESENT" ${currentStatus === 'PRESENT' ? 'selected' : ''}>Present (P)</option>
        <option value="ABSENT" ${currentStatus === 'ABSENT' ? 'selected' : ''}>Absent (A)</option>
        <option value="LEAVE" ${currentStatus === 'LEAVE' ? 'selected' : ''}>Leave (L)</option>
        <option value="NONE" ${currentStatus === 'NONE' ? 'selected' : ''}>Clear Record</option>
      </select>
    `);

    if (newStatus) {
      const status = newStatus?.status || (document.getElementById('swal-status') as HTMLSelectElement)?.value;
      const res = await fetch('/api/attendance', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentId, date: dateStr, status })
      });
      if (res.ok) {
        osToast.fire({ icon: 'success', title: 'Record Updated' });
        fetchAttendance();
      }
    }
  };

  const getStatusDisplay = (attendances: any[], day: number) => {
    const record = attendances.find(a => new Date(a.date).getDate() === day);
    if (!record) return { label: '-', class: 'text-slate-300 hover:bg-slate-100', raw: 'NONE' };
    if (record.status === 'PRESENT' || record.status === 'P') return { label: 'P', class: 'bg-emerald-100 text-emerald-700 font-bold border border-emerald-200', raw: 'PRESENT' };
    if (record.status === 'ABSENT' || record.status === 'A') return { label: 'A', class: 'bg-red-100 text-red-700 font-bold border border-red-200', raw: 'ABSENT' };
    if (record.status === 'LEAVE' || record.status === 'L') return { label: 'L', class: 'bg-amber-100 text-amber-700 font-bold border border-amber-200', raw: 'LEAVE' };
    return { label: 'P', class: 'bg-emerald-100 text-emerald-700 font-bold border border-emerald-200', raw: 'PRESENT' }; // Fallback for old records
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col h-[calc(100vh-8rem)]">
      {/* HEADER CONTROLS */}
      <div className="p-6 border-b border-slate-200 flex flex-wrap justify-between items-center gap-4">
        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <CalendarDays className="w-5 h-5 text-blue-600" /> Master Attendance Ledger
        </h2>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 mr-4">
            <span className="w-3 h-3 rounded-full bg-emerald-500"></span> Present
            <span className="w-3 h-3 rounded-full bg-red-500 ml-2"></span> Absent
            <span className="w-3 h-3 rounded-full bg-amber-500 ml-2"></span> Leave
          </div>

          <div className="flex items-center bg-slate-100 rounded-lg p-1 border border-slate-200">
            <button onClick={() => changeMonth(-1)} className="px-3 py-1 rounded hover:bg-white hover:shadow-sm text-sm font-medium transition-all">&larr;</button>
            <div className="px-4 text-sm font-bold text-slate-700 min-w-[120px] text-center">
              {currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
            </div>
            <button onClick={() => changeMonth(1)} className="px-3 py-1 rounded hover:bg-white hover:shadow-sm text-sm font-medium transition-all">&rarr;</button>
          </div>
        </div>
      </div>

      {/* 30-DAY SCROLLABLE GRID */}
      <div className="flex-1 overflow-auto relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-slate-400 font-medium">Syncing Ledger...</div>
        ) : (
          <table className="w-full text-center text-sm border-collapse">
            <thead className="bg-slate-50 text-slate-600 font-semibold sticky top-0 z-10 shadow-sm">
              <tr>
                <th className="py-3 px-4 text-left border-b border-r border-slate-200 min-w-[200px] sticky left-0 bg-slate-50 z-20">Student Details</th>
                {daysArray.map(day => (
                  <th key={day} className="py-3 px-2 border-b border-r border-slate-200 min-w-[40px] text-xs">
                    {day}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id} className="hover:bg-slate-50/50 group">
                  <td className="py-2 px-4 text-left border-b border-r border-slate-200 sticky left-0 bg-white group-hover:bg-slate-50/90 z-10">
                    <div className="font-medium text-slate-800">{student.name}</div>
                    <div className="text-xs text-slate-500">{student.classes?.map((c:any)=>c.name).join(', ')}</div>
                  </td>
                  {daysArray.map(day => {
                    const status = getStatusDisplay(student.attendances, day);
                    return (
                      <td key={day} className="border-b border-r border-slate-200 p-1">
                        <button 
                          onClick={() => handleCellClick(student.id, day, status.raw)}
                          className={`w-8 h-8 rounded-md flex items-center justify-center mx-auto transition-colors ${status.class}`}
                        >
                          {status.label}
                        </button>
                      </td>
                    )
                  })}
                </tr>
              ))}
              {students.length === 0 && (
                <tr><td colSpan={daysInMonth + 1} className="py-8 text-slate-500 text-center">No students registered in the system.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
