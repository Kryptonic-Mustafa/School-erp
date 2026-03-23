'use client';

import { useState, useEffect } from 'react';
import { Library, FileText, Plus, Trash2, Award } from 'lucide-react';
import { osAlert, osToast } from '@/lib/alert_engine';

export default function AcademicsHub() {
  const [activeTab, setActiveTab] = useState('SUBJECTS');
  const [subjects, setSubjects] = useState<any[]>([]);
  const [exams, setExams] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);

  // Forms
  const [subForm, setSubForm] = useState({ name: '', code: '', classId: '', teacherId: '' });
  const [examForm, setExamForm] = useState({ title: '', date: '', subjectId: '' });

  const fetchData = async () => {
    const [subRes, exRes, clsRes, tchRes] = await Promise.all([
      fetch('/api/subjects').then(r => r.json()),
      fetch('/api/exams').then(r => r.json()),
      fetch('/api/classes').then(r => r.json()),
      fetch('/api/teachers').then(r => r.json())
    ]);
    if (subRes.success) setSubjects(subRes.subjects);
    if (exRes.success) setExams(exRes.exams);
    if (clsRes.success) setClasses(clsRes.classes);
    if (tchRes.success) setTeachers(tchRes.teachers);
  };

  useEffect(() => { fetchData(); }, []);

  const handleCreateSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/subjects', { method: 'POST', body: JSON.stringify(subForm) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Subject Created' }); setSubForm({name:'', code:'', classId:'', teacherId:''}); fetchData(); }
    else osAlert.error('Error', (await res.json()).error);
  };

  const handleCreateExam = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/exams', { method: 'POST', body: JSON.stringify(examForm) });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Exam Scheduled' }); setExamForm({title:'', date:'', subjectId:''}); fetchData(); }
    else osAlert.error('Error', (await res.json()).error);
  };

  const deleteRecord = async (endpoint: string, id: string) => {
    if (!(await osAlert.confirm('Delete Record?', 'This action is irreversible.')).isConfirmed) return;
    const res = await fetch(`/api/${endpoint}?id=${id}`, { method: 'DELETE' });
    if (res.ok) { osToast.fire({ icon: 'success', title: 'Deleted' }); fetchData(); }
    else osAlert.error('Error', (await res.json()).error);
  };

  return (
    <div className="space-y-6">
      {/* TABS */}
      <div className="flex border-b border-slate-200">
        <button onClick={() => setActiveTab('SUBJECTS')} className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'SUBJECTS' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}>
          <Library className="w-4 h-4" /> Curriculum / Subjects
        </button>
        <button onClick={() => setActiveTab('EXAMS')} className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'EXAMS' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}`}>
          <FileText className="w-4 h-4" /> Examinations
        </button>
      </div>

      {activeTab === 'SUBJECTS' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-600"/> Add Subject</h2>
            <form onSubmit={handleCreateSubject} className="space-y-4">
              <div><label className="block text-sm font-medium mb-1">Subject Name</label><input type="text" required value={subForm.name} onChange={e=>setSubForm({...subForm, name: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" placeholder="e.g. Advanced Physics" /></div>
              <div><label className="block text-sm font-medium mb-1">Subject Code</label><input type="text" required value={subForm.code} onChange={e=>setSubForm({...subForm, code: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm uppercase" placeholder="e.g. PHY-201" /></div>
              <div><label className="block text-sm font-medium mb-1">Assign Class</label><select required value={subForm.classId} onChange={e=>setSubForm({...subForm, classId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- Select Class --</option>{classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
              <div><label className="block text-sm font-medium mb-1">Assign Teacher</label><select required value={subForm.teacherId} onChange={e=>setSubForm({...subForm, teacherId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- Select Teacher --</option>{teachers.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></div>
              <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700">Save Subject</button>
            </form>
          </div>
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Library className="w-5 h-5 text-blue-600"/> Curriculum Master List</h2>
            <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Code / Subject</th><th className="py-3 px-4">Class</th><th className="py-3 px-4">Teacher</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {subjects.map(s => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="py-3 px-4"><div className="font-bold text-slate-800">{s.name}</div><div className="text-xs text-slate-500 font-mono">{s.code}</div></td>
                    <td className="py-3 px-4"><span className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs font-semibold">{s.class.name}</span></td>
                    <td className="py-3 px-4 text-slate-600">{s.teacher.name}</td>
                    <td className="py-3 px-4 text-right"><button onClick={()=>deleteRecord('subjects', s.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button></td>
                  </tr>
                ))}
                {subjects.length === 0 && <tr><td colSpan={4} className="py-8 text-center text-slate-500">No subjects defined.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'EXAMS' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><Plus className="w-5 h-5 text-emerald-600"/> Schedule Exam</h2>
            <form onSubmit={handleCreateExam} className="space-y-4">
              <div><label className="block text-sm font-medium mb-1">Exam Title</label><input type="text" required value={examForm.title} onChange={e=>setExamForm({...examForm, title: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" placeholder="e.g. Mid-Term Assessment" /></div>
              <div><label className="block text-sm font-medium mb-1">Target Subject</label><select required value={examForm.subjectId} onChange={e=>setExamForm({...examForm, subjectId: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm"><option value="">-- Select Subject --</option>{subjects.map(s => <option key={s.id} value={s.id}>{s.name} ({s.class.name})</option>)}</select></div>
              <div><label className="block text-sm font-medium mb-1">Date</label><input type="date" required value={examForm.date} onChange={e=>setExamForm({...examForm, date: e.target.value})} className="w-full bg-slate-50 border rounded-lg p-2.5 text-sm" /></div>
              <button type="submit" className="w-full bg-emerald-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-emerald-700">Schedule Exam</button>
            </form>
          </div>
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2"><FileText className="w-5 h-5 text-emerald-600"/> Upcoming Examinations</h2>
            <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="py-3 px-4">Exam Title</th><th className="py-3 px-4">Subject & Class</th><th className="py-3 px-4">Date</th><th className="py-3 px-4 text-right">Actions</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {exams.map(ex => (
                  <tr key={ex.id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-bold text-slate-800">{ex.title}</td>
                    <td className="py-3 px-4"><div className="text-slate-700">{ex.subject.name}</div><div className="text-xs text-slate-500">{ex.subject.class.name}</div></td>
                    <td className="py-3 px-4 text-slate-600">{new Date(ex.date).toLocaleDateString()}</td>
                    <td className="py-3 px-4 text-right">
                      <button onClick={()=>osToast.fire({icon:'info', title: 'Grading module pending...'})} className="text-slate-400 hover:text-emerald-600 mr-3"><Award className="w-4 h-4"/></button>
                      <button onClick={()=>deleteRecord('exams', ex.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="w-4 h-4"/></button>
                    </td>
                  </tr>
                ))}
                {exams.length === 0 && <tr><td colSpan={4} className="py-8 text-center text-slate-500">No exams scheduled.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
