import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Overhauled: {path}")

def step11_deploy():
    print("====================================================")
    print("   M.A.C.DevOS: ENTERPRISE SAAS UI OVERHAUL         ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> PURGING HACKER THEME & INJECTING ENTERPRISE CSS...")

    # 1. CLEAN GLOBALS (Remove scanlines, switch to standard light theme)
    globals_css = """
@import "tailwindcss";

@layer base {
  body {
    @apply bg-slate-50 text-slate-900 font-sans antialiased;
  }
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    """
    create_file(os.path.join(project_dir, "src/app/globals.css"), globals_css)

    # 2. ROOT LAYOUT (Remove dark mode classes)
    layout_tsx = """
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'EduAdmin | School Management System',
  description: 'Enterprise Grade School Management',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 font-sans antialiased min-h-screen">
        {children}
      </body>
    </html>
  )
}
    """
    create_file(os.path.join(project_dir, "src/app/layout.tsx"), layout_tsx)

    print("\n>>> BUILDING ADMIN SIDEBAR LAYOUT...")

    # 3. NEW: ADMIN LAYOUT (The Left Sidebar + Header Wrapper)
    admin_layout_tsx = """
'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Users, BookOpen, Camera, ScanFace, Activity, Settings, LogOut, GraduationCap, School } from 'lucide-react';
import { osToast } from '@/lib/alert_engine';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    osToast.fire({ icon: 'success', title: 'Logged out successfully' });
    router.push('/login');
  };

  const navItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Students', href: '/admin/students', icon: GraduationCap },
    { name: 'Teachers', href: '#', icon: Users },
    { name: 'Classes', href: '#', icon: BookOpen },
    { name: 'Live Scanner', href: '/attendance', icon: Camera },
    { name: 'Biometrics', href: '/admin/face-register', icon: ScanFace },
    { name: 'Telemetry', href: '/admin/telemetry', icon: Activity },
  ];

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* LEFT SIDEBAR */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col fixed h-full z-20">
        <div className="h-16 flex items-center px-6 border-b border-slate-200">
          <School className="w-6 h-6 text-blue-600 mr-3" />
          <span className="font-bold text-lg text-slate-800 tracking-tight">EduAdmin</span>
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link key={item.name} href={item.href} className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}>
                <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                {item.name}
              </Link>
            )
          })}
        </nav>
        <div className="p-4 border-t border-slate-200">
          <button onClick={handleLogout} className="flex items-center w-full px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
            <LogOut className="w-5 h-5 mr-3 text-red-500" /> Sign Out
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT WRAPPER */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        {/* TOP HEADER */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
          <h1 className="text-xl font-semibold text-slate-800 capitalize">
            {pathname.split('/').pop()?.replace('-', ' ') || 'Dashboard'}
          </h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">A</div>
              <div className="text-sm">
                <p className="font-medium text-slate-700 leading-none">Admin User</p>
                <p className="text-xs text-slate-500 mt-1">admin@school.os</p>
              </div>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/layout.tsx"), admin_layout_tsx)

    print("\n>>> REWRITING PAGES TO ENTERPRISE DESIGN...")

    # 4. DASHBOARD PAGE
    dashboard_tsx = """
import { Users, GraduationCap, BookOpen, UserCheck } from 'lucide-react';

export default function AdminDashboard() {
  const stats = [
    { title: 'Total Students', value: '1,248', icon: GraduationCap, color: 'bg-blue-500' },
    { title: 'Total Teachers', value: '84', icon: Users, color: 'bg-violet-500' },
    { title: 'Active Classes', value: '42', icon: BookOpen, color: 'bg-amber-500' },
    { title: 'Present Today', value: '1,102', icon: UserCheck, color: 'bg-emerald-500' },
  ];

  return (
    <div className="space-y-6">
      {/* STATS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.title} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-white ${stat.color}`}>
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                <h3 className="text-2xl font-bold text-slate-800">{stat.value}</h3>
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm min-h-[300px]">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Recent System Activity</h2>
          <p className="text-sm text-slate-500">Activity stream will populate here.</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm min-h-[300px]">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Quick Actions</h2>
          <div className="space-y-3">
             <button className="w-full text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all text-sm font-medium text-slate-700">Add New Student Profile</button>
             <button className="w-full text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all text-sm font-medium text-slate-700">Generate Attendance Report</button>
             <button className="w-full text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-blue-500 hover:bg-blue-50 transition-all text-sm font-medium text-slate-700">System Backup</button>
          </div>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/dashboard/page.tsx"), dashboard_tsx)

    # 5. STUDENTS MATRIX OVERHAUL
    students_tsx = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Plus } from 'lucide-react';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function EntityMatrix() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ name: '', email: '', password: '', className: 'CS-101' });

  const fetchEntities = useCallback(async () => {
    try {
      const res = await fetch('/api/students');
      const data = await res.json();
      if (data.success) setStudents(data.students);
    } catch (e) {
      osToast.fire({ icon: 'error', title: 'Data Fetch Failed' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchEntities(); }, [fetchEntities]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const confirm = await osAlert.confirm('Register Student?', `Adding ${formData.name} to the database.`);
    if (!confirm.isConfirmed) return;

    try {
      const res = await fetch('/api/students', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      osToast.fire({ icon: 'success', title: 'Student Registered' });
      setFormData({ name: '', email: '', password: '', className: 'CS-101' });
      fetchEntities();
    } catch (err: any) {
      osAlert.error('Write Failed', err.message);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* ADD STUDENT FORM */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
          <Plus className="w-5 h-5 text-blue-600" /> New Student
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="John Doe" /></div>
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="student@school.edu" /></div>
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Password</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="••••••••" /></div>
          <div><label className="block text-sm font-medium text-slate-700 mb-1">Class Designation</label><input type="text" required value={formData.className} onChange={e => setFormData({...formData, className: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" /></div>
          <button type="submit" className="w-full bg-blue-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-blue-700 transition-colors mt-2">
            Register Student
          </button>
        </form>
      </div>

      {/* STUDENTS TABLE */}
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
        <div className="p-6 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800">Directory</h2>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input type="text" placeholder="Search..." className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
              <tr><th className="py-3 px-6">Name</th><th className="py-3 px-6">Email</th><th className="py-3 px-6">Class</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {students.map((student) => (
                <tr key={student.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-6 font-medium text-slate-800">{student.name}</td>
                  <td className="py-3 px-6 text-slate-500">{student.user.email}</td>
                  <td className="py-3 px-6 text-slate-500">
                    <span className="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full text-xs font-semibold">{student.class.name}</span>
                  </td>
                </tr>
              ))}
              {!loading && students.length === 0 && <tr><td colSpan={3} className="py-8 text-center text-slate-500">No students found.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/students/page.tsx"), students_tsx)

    # 6. BIOMETRICS OVERHAUL
    registry_tsx = """
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Camera, Save, ScanFace, PowerOff } from 'lucide-react';
import * as faceapi from 'face-api.js';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function FaceRegistration() {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const terminateOptics = useCallback((showToast = true) => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    if (showToast) osToast.fire({ icon: 'info', title: 'Camera disabled' });
  }, []);

  useEffect(() => {
    fetch('/api/students').then(res => res.json()).then(data => { if (data.success) setStudents(data.students); });

    const loadModels = async () => {
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models')
      ]);
      setModelsLoaded(true);
    };
    loadModels();
    return () => terminateOptics(false);
  }, [terminateOptics]);

  const startVideo = () => {
    if (!modelsLoaded) return;
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    }).catch(() => osAlert.error('Hardware Error', 'Camera access denied.'));
  };

  const captureFace = async () => {
    if (!videoRef.current || !selectedStudent) return;
    const detection = await faceapi.detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptor();

    if (!detection) {
      osAlert.error('Scan Failed', 'No face detected. Please ensure good lighting.');
      return;
    }

    try {
      const res = await fetch('/api/face/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentId: selectedStudent, vectorData: Array.from(detection.descriptor) })
      });
      if (!res.ok) throw new Error((await res.json()).error);
      osAlert.success('Success', 'Biometric data securely registered.');
      setSelectedStudent('');
      terminateOptics(false); 
    } catch (err: any) {
      osAlert.error('Registration Failed', err.message);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* CONTROLS */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 h-fit">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
          <ScanFace className="w-5 h-5 text-blue-600" /> Biometric Registration
        </h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">1. Select Student Profile</label>
            <select value={selectedStudent} onChange={(e) => setSelectedStudent(e.target.value)} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">-- Choose Student --</option>
              {students.map(s => <option key={s.id} value={s.id}>{s.name} ({s.class.name})</option>)}
            </select>
          </div>

          {!isCameraActive ? (
            <button onClick={startVideo} disabled={!modelsLoaded} className="w-full bg-slate-100 text-slate-700 border border-slate-300 rounded-lg py-3 text-sm font-medium hover:bg-slate-200 transition-colors disabled:opacity-50">
              {modelsLoaded ? '2. Activate Camera' : 'Loading AI Models...'}
            </button>
          ) : (
            <button onClick={() => terminateOptics(true)} className="w-full bg-red-50 text-red-600 border border-red-200 rounded-lg py-3 text-sm font-medium hover:bg-red-100 transition-colors flex justify-center items-center gap-2">
              <PowerOff className="w-4 h-4" /> Stop Camera
            </button>
          )}

          <button onClick={captureFace} disabled={!selectedStudent || !isCameraActive} className="w-full bg-blue-600 text-white rounded-lg py-3 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors flex justify-center items-center gap-2 shadow-sm">
            <Save className="w-4 h-4" /> 3. Scan & Save
          </button>
        </div>
      </div>

      {/* CAMERA VIEWPORT */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex flex-col items-center justify-center min-h-[400px]">
         <div className="relative w-full aspect-video bg-slate-100 rounded-lg border border-slate-200 overflow-hidden flex items-center justify-center">
           {!isCameraActive && <Camera className="w-12 h-12 text-slate-300 absolute" />}
           <video ref={videoRef} autoPlay muted className={`absolute inset-0 w-full h-full object-cover ${isCameraActive ? 'opacity-100' : 'opacity-0'}`}></video>
         </div>
         <p className="mt-4 text-sm text-slate-500">Ensure the subject's face is clearly visible.</p>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/face-register/page.tsx"), registry_tsx)

    # 7. ATTENDANCE KIOSK OVERHAUL (iPad App Style)
    attendance_tsx = """
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Camera, UserCheck, PowerOff, ArrowLeft } from 'lucide-react';
import * as faceapi from 'face-api.js';
import { encryptPayload } from '@/lib/crypto_engine';
import { osAlert, osToast } from '@/lib/alert_engine';
import Link from 'next/link';

export default function AttendanceKiosk() {
  const [status, setStatus] = useState<'LOADING' | 'READY' | 'SCANNING'>('LOADING');
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const terminateOptics = useCallback((showToast = true) => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setStatus('READY');
  }, []);

  useEffect(() => {
    const initSystem = async () => {
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models')
      ]);
      setStatus('READY');
    };
    initSystem();
    return () => terminateOptics(false);
  }, [terminateOptics]);

  const toggleScanner = async () => {
    if (isCameraActive) return terminateOptics(false);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) { videoRef.current.srcObject = stream; setIsCameraActive(true); }
    } catch (e) { osAlert.error('Hardware Error', 'Camera access denied.'); }
  };

  const executeScan = async () => {
    if (!videoRef.current?.srcObject) return;
    setStatus('SCANNING');
    try {
      const detection = await faceapi.detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptor();
      if (!detection) throw new Error('No face detected.');

      const payload = encryptPayload(JSON.stringify({ classId: 'CS-101', capturedEmbedding: Array.from(detection.descriptor) }));
      const res = await fetch('/api/attendance/mark', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ encryptedData: payload }) });
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error || 'Verification failed.');

      osAlert.success('Verified', 'Attendance successfully logged.');
      terminateOptics(false); 
    } catch (error: any) {
      osToast.fire({ icon: 'error', title: error.message });
      setStatus('READY');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-100 font-sans">
      <Link href="/admin/dashboard" className="absolute top-6 left-6 flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-blue-600 transition-colors bg-white px-4 py-2 rounded-lg shadow-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      <div className="max-w-xl w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-blue-600 p-6 text-center text-white">
          <UserCheck className="w-12 h-12 mx-auto mb-3 opacity-90" />
          <h1 className="text-2xl font-bold tracking-tight">Kiosk Scanner</h1>
          <p className="text-blue-100 text-sm mt-1">Look into the camera to verify attendance</p>
        </div>

        <div className="p-8">
          <div className="aspect-video bg-slate-100 rounded-xl border-2 border-slate-200 mb-8 relative overflow-hidden shadow-inner flex items-center justify-center">
             <video ref={videoRef} autoPlay muted className={`absolute inset-0 w-full h-full object-cover ${isCameraActive ? 'opacity-100' : 'opacity-0'}`}></video>
             {status === 'SCANNING' && <div className="absolute inset-0 border-4 border-blue-500 animate-pulse z-20 rounded-xl" />}
             {!isCameraActive && <Camera className="w-16 h-16 text-slate-300 z-10" />}
          </div>

          <div className="flex gap-4">
            <button onClick={toggleScanner} disabled={status === 'LOADING' || status === 'SCANNING'} className={`flex-1 py-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${isCameraActive ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100' : 'bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200'}`}>
              {isCameraActive ? <><PowerOff className="w-5 h-5" /> Stop Camera</> : '1. Turn On Camera'}
            </button>

            <button onClick={executeScan} disabled={!isCameraActive || status === 'SCANNING'} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-md transition-all disabled:opacity-50 disabled:shadow-none">
              {status === 'SCANNING' ? 'Verifying...' : '2. Scan Face'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/attendance/page.tsx"), attendance_tsx)

    # 8. UPDATE ALERT ENGINE THEME TO LIGHT
    alert_engine_ts = """
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';

const MySwal = withReactContent(Swal);

const enterpriseTheme = {
  customClass: {
    popup: 'rounded-xl shadow-xl font-sans border border-slate-100',
    confirmButton: 'rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 px-6 py-2.5',
    cancelButton: 'rounded-lg bg-white text-slate-700 font-medium hover:bg-slate-50 border border-slate-200 px-6 py-2.5',
    title: 'text-slate-800 font-semibold text-xl',
    htmlContainer: 'text-sm text-slate-500'
  }
};

export const osToast = MySwal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  customClass: { popup: 'rounded-lg font-sans text-sm shadow-lg border border-slate-100' }
});

export const osAlert = {
  success: (title: string, text: string) => MySwal.fire({ icon: 'success', title, text, ...enterpriseTheme }),
  error: (title: string, text: string) => MySwal.fire({ icon: 'error', title, text, ...enterpriseTheme }),
  confirm: (title: string, text: string) => MySwal.fire({ 
    icon: 'question', title, text, showCancelButton: true, confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', ...enterpriseTheme 
  })
};
    """
    create_file(os.path.join(project_dir, "src/lib/alert_engine.ts"), alert_engine_ts)

    print("\n====================================================")
    print(" [SUCCESS] ENTERPRISE SAAS UI OVERHAUL COMPLETE.    ")
    print("====================================================\n")

if __name__ == "__main__":
    step11_deploy()