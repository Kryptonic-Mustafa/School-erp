import os
import subprocess
import sys

PROJECT_NAME = "school-os"

def run_command(command, cwd=None):
    print(f"[*] Executing: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"[!] Error executing: {command}")
        sys.exit(1)

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Wrote Optimized File: {path}")

def step07_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: OPTIMIZATION & ALERT ENGINE DEPLOY   ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> INSTALLING SWEETALERT2 DEPENDENCIES...")
    run_command("npm install sweetalert2 sweetalert2-react-content", cwd=project_dir)

    print("\n>>> INJECTING OS-LEVEL ALERT ENGINE...")

    # 1. Alert Engine Lib (Forces SweetAlert to match the dark OS theme)
    alert_engine_ts = """
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';

const MySwal = withReactContent(Swal);

const osTheme = {
  background: '#050505',
  color: '#22c55e',
  confirmButtonColor: '#22c55e',
  cancelButtonColor: '#27272a',
  customClass: {
    popup: 'border border-zinc-800 rounded-none font-mono shadow-[0_0_20px_rgba(34,197,94,0.1)]',
    confirmButton: 'rounded-none text-black font-bold uppercase tracking-widest hover:bg-green-400',
    cancelButton: 'rounded-none text-white uppercase tracking-widest border border-zinc-700 hover:bg-zinc-800',
    title: 'text-green-500 uppercase tracking-widest text-lg font-bold',
    htmlContainer: 'text-sm text-zinc-400'
  }
};

export const osToast = MySwal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  background: '#0a0a0a',
  color: '#22c55e',
  customClass: {
    popup: 'border border-zinc-800 rounded-none font-mono text-sm'
  },
  didOpen: (toast) => {
    toast.addEventListener('mouseenter', Swal.stopTimer)
    toast.addEventListener('mouseleave', Swal.resumeTimer)
  }
});

export const osAlert = {
  success: (title: string, text: string) => MySwal.fire({ icon: 'success', title, text, ...osTheme, iconColor: '#22c55e' }),
  error: (title: string, text: string) => MySwal.fire({ icon: 'error', title, text, ...osTheme, iconColor: '#ef4444' }),
  confirm: (title: string, text: string) => MySwal.fire({ 
    icon: 'warning', 
    title, 
    text, 
    showCancelButton: true, 
    confirmButtonText: 'EXECUTE',
    cancelButtonText: 'ABORT',
    iconColor: '#eab308',
    ...osTheme 
  })
};
    """
    create_file(os.path.join(project_dir, "src/lib/alert_engine.ts"), alert_engine_ts)

    print("\n>>> OPTIMIZING UI COMPONENTS & CAMERA KERNEL...")

    # 2. Optimized Login Page (with Toasts)
    login_tsx = """
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Terminal } from 'lucide-react';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Authentication Failed');

      osToast.fire({ icon: 'success', title: 'Session Authenticated' });

      if (data.role === 'ADMIN') router.push('/admin/dashboard');
      else if (data.role === 'TEACHER') router.push('/teacher');
      else router.push('/student');
      
    } catch (err: any) {
      osAlert.error('Access Denied', err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4 z-10 relative">
      <div className="w-full max-w-md bg-black border border-zinc-800 p-8 shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-green-500 opacity-80" />
        <div className="flex items-center gap-3 mb-8">
          <Terminal className="w-8 h-8 text-green-500" />
          <h1 className="text-2xl font-bold tracking-widest text-white">SYS_LOGIN</h1>
        </div>
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Identifier</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500 transition-colors" placeholder="admin@system.local" required />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Passkey</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500 transition-colors" placeholder="••••••••" required />
          </div>
          <button type="submit" disabled={loading} className="w-full bg-green-500 hover:bg-green-400 text-black font-bold py-3 uppercase tracking-widest transition-colors disabled:opacity-50">
            {loading ? 'Authenticating...' : 'Initialize Session'}
          </button>
        </form>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/login/page.tsx"), login_tsx)

    # 3. Optimized Entity Matrix (CRUD + SweetAlert Confirmation)
    students_ui_ts = """
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Users, PlusSquare, Terminal } from 'lucide-react';
import Link from 'next/link';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function EntityMatrix() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
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
    
    // OS-level Confirmation Dialog
    const confirm = await osAlert.confirm('Write to Database?', `You are about to register entity: ${formData.name}`);
    if (!confirm.isConfirmed) return;

    setIsSubmitting(true);
    try {
      const res = await fetch('/api/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error);

      osToast.fire({ icon: 'success', title: 'Entity Registered' });
      setFormData({ name: '', email: '', password: '', className: 'CS-101' });
      fetchEntities();
    } catch (err: any) {
      osAlert.error('Write Failed', err.message || 'System error occurred.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen p-8 relative z-10 font-mono">
      <header className="mb-8 border-b border-zinc-800 pb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-3 text-white uppercase tracking-widest">
          <Users className="w-6 h-6 text-green-500" /> Entity_Matrix
        </h1>
        <Link href="/admin/dashboard" className="text-xs text-zinc-500 hover:text-green-500 uppercase transition-colors">
          [ Return to Root ]
        </Link>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="border border-zinc-800 bg-black p-6 h-fit">
          <h2 className="text-lg text-white mb-6 uppercase flex items-center gap-2">
            <PlusSquare className="w-5 h-5 text-green-500" /> Initialize Subject
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4 text-sm">
            <div><label className="block text-zinc-500 uppercase mb-1">Full Name</label><input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" /></div>
            <div><label className="block text-zinc-500 uppercase mb-1">Identifier (Email)</label><input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" /></div>
            <div><label className="block text-zinc-500 uppercase mb-1">Passkey</label><input type="password" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" /></div>
            <div><label className="block text-zinc-500 uppercase mb-1">Designation (Class)</label><input type="text" required value={formData.className} onChange={e => setFormData({...formData, className: e.target.value})} className="w-full bg-zinc-900 border border-zinc-700 p-2 text-green-500 focus:outline-none focus:border-green-500" /></div>
            <button type="submit" disabled={isSubmitting} className="w-full bg-green-500 text-black py-2 uppercase font-bold hover:bg-green-400 disabled:opacity-50 mt-4">
              {isSubmitting ? 'Processing...' : 'Write to Database'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 border border-zinc-800 bg-black p-6">
          <h2 className="text-lg text-white mb-6 uppercase flex items-center gap-2">
            <Terminal className="w-5 h-5 text-green-500" /> Active Subjects
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-zinc-500 border-b border-zinc-800 uppercase">
                <tr><th className="pb-3 px-2">ID Fragment</th><th className="pb-3 px-2">Name</th><th className="pb-3 px-2">Designation</th><th className="pb-3 px-2">Identifier</th></tr>
              </thead>
              <tbody className="text-zinc-300">
                {students.map((student) => (
                  <tr key={student.id} className="border-b border-zinc-800/50 hover:bg-zinc-900/50 transition-colors">
                    <td className="py-3 px-2 text-xs text-zinc-600">{student.id.split('-')[0]}</td>
                    <td className="py-3 px-2 text-green-500">{student.name}</td>
                    <td className="py-3 px-2">{student.class.name}</td>
                    <td className="py-3 px-2">{student.user.email}</td>
                  </tr>
                ))}
                {!loading && students.length === 0 && <tr><td colSpan={4} className="py-8 text-center text-zinc-600 uppercase">No active subjects found.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/students/page.tsx"), students_ui_ts)

    # 4. Optimized Biometric Registry (Hardware Kill Switch & Unmount Cleanup)
    register_ui = """
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Camera, Save, ScanFace, PowerOff } from 'lucide-react';
import * as faceapi from 'face-api.js';
import Link from 'next/link';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function FaceRegistration() {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [status, setStatus] = useState('AWAITING_MODELS');
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Hardware Kill Switch Function
  const terminateOptics = useCallback(() => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setStatus('SYSTEM_READY');
    osToast.fire({ icon: 'info', title: 'Optics Terminated' });
  }, []);

  useEffect(() => {
    fetch('/api/students').then(res => res.json()).then(data => { if (data.success) setStudents(data.students); });

    const loadModels = async () => {
      setStatus('LOADING_NEURAL_WEIGHTS...');
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models')
      ]);
      setModelsLoaded(true);
      setStatus('SYSTEM_READY');
    };
    loadModels();

    // Critical Unmount Cleanup (Prevents memory leak & stuck camera)
    return () => {
      terminateOptics();
    };
  }, [terminateOptics]);

  const startVideo = () => {
    if (!modelsLoaded) return;
    setStatus('INITIALIZING_CAMERA...');
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsCameraActive(true);
          setStatus('OPTICS_ONLINE');
        }
      })
      .catch(() => {
        setStatus('CAMERA_ACCESS_DENIED');
        osAlert.error('Hardware Error', 'Camera access was denied by the OS.');
      });
  };

  const captureFace = async () => {
    if (!videoRef.current || !selectedStudent) return;
    setStatus('SCANNING_BIOMETRICS...');

    const detection = await faceapi.detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptor();

    if (!detection) {
      setStatus('OPTICS_ONLINE');
      osAlert.error('Scan Failed', 'No valid subject detected. Please look into the optics.');
      return;
    }

    const vectorData = Array.from(detection.descriptor);
    setStatus('TRANSMITTING...');

    try {
      const res = await fetch('/api/face/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentId: selectedStudent, vectorData })
      });
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error);

      osAlert.success('Biometrics Locked', 'Neural mapping written to database successfully.');
      setSelectedStudent('');
      terminateOptics(); // Auto-close camera on success
    } catch (err: any) {
      osAlert.error('Write Failed', err.message);
      setStatus('OPTICS_ONLINE');
    }
  };

  return (
    <div className="min-h-screen p-8 relative z-10 font-mono">
      <header className="mb-8 border-b border-zinc-800 pb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-3 text-white uppercase tracking-widest">
          <ScanFace className="w-6 h-6 text-green-500" /> Biometric_Registry
        </h1>
        <Link href="/admin/dashboard" className="text-xs text-zinc-500 hover:text-green-500 uppercase transition-colors">
          [ Return to Root ]
        </Link>
      </header>

      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="border border-zinc-800 bg-black p-6 flex flex-col gap-6 h-fit">
          <div className="p-3 bg-zinc-900 border border-zinc-700 text-xs text-green-500 uppercase flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isCameraActive ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></span>
            SYS_STATUS: {status}
          </div>

          <div>
            <label className="block text-zinc-500 uppercase mb-2 text-sm">1. Target Subject</label>
            <select value={selectedStudent} onChange={(e) => setSelectedStudent(e.target.value)} className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500">
              <option value="">-- AWAITING_SELECTION --</option>
              {students.map(s => <option key={s.id} value={s.id}>{s.name} ({s.class.name})</option>)}
            </select>
          </div>

          {!isCameraActive ? (
            <button onClick={startVideo} disabled={!modelsLoaded} className="w-full bg-zinc-900 text-white border border-zinc-700 py-3 uppercase hover:border-green-500 disabled:opacity-50 transition-all">
              2. Initialize Optics
            </button>
          ) : (
            <button onClick={terminateOptics} className="w-full bg-red-500/10 text-red-500 border border-red-500/50 py-3 uppercase hover:bg-red-500 hover:text-black transition-all flex justify-center items-center gap-2">
              <PowerOff className="w-5 h-5" /> Terminate Optics
            </button>
          )}

          <button onClick={captureFace} disabled={!selectedStudent || !isCameraActive || status === 'TRANSMITTING...'} className="w-full bg-green-500 text-black font-bold py-3 uppercase hover:bg-green-400 disabled:opacity-50 transition-all flex justify-center items-center gap-2">
            <Save className="w-5 h-5" /> 3. Lock Biometrics
          </button>
        </div>

        <div className="border border-zinc-800 bg-black p-6 flex flex-col items-center justify-center min-h-[300px] relative">
           <div className="relative w-full aspect-video bg-zinc-900 border border-zinc-800 overflow-hidden flex items-center justify-center">
             {!isCameraActive && <Camera className="w-12 h-12 text-zinc-700 absolute" />}
             <video ref={videoRef} autoPlay muted className={`absolute inset-0 w-full h-full object-cover ${isCameraActive ? 'opacity-100' : 'opacity-0'}`}></video>
             {status === 'SCANNING_BIOMETRICS...' && <div className="absolute inset-0 border-2 border-green-500 animate-pulse z-20" />}
           </div>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/face-register/page.tsx"), register_ui)

    # 5. Optimized Attendance Scanner (Memory Cleanup & Auto-Terminate)
    attendance_ui = """
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Camera, TerminalSquare, PowerOff } from 'lucide-react';
import * as faceapi from 'face-api.js';
import { encryptPayload } from '@/lib/crypto_engine';
import { osAlert, osToast } from '@/lib/alert_engine';
import Link from 'next/link';

export default function AttendanceKiosk() {
  const [status, setStatus] = useState<'LOADING' | 'READY' | 'SCANNING'>('LOADING');
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const terminateOptics = useCallback(() => {
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

    // Cleanup on unmount
    return () => terminateOptics();
  }, [terminateOptics]);

  const toggleScanner = async () => {
    if (isCameraActive) {
      terminateOptics();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (e) {
      osAlert.error('Hardware Error', 'Camera access denied.');
    }
  };

  const executeScan = async () => {
    if (!videoRef.current?.srcObject) return;
    setStatus('SCANNING');

    try {
      const detection = await faceapi.detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptor();

      if (!detection) {
        throw new Error('NO_SUBJECT_DETECTED');
      }

      const vectorData = Array.from(detection.descriptor);
      const payload = encryptPayload(JSON.stringify({ classId: 'CS-101', capturedEmbedding: vectorData }));

      const res = await fetch('/api/attendance/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ encryptedData: payload })
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'UNAUTHORIZED_ENTITY');

      osAlert.success('Identity Verified', 'Attendance successfully logged to the matrix.');
      terminateOptics(); // Auto-shutdown camera on success to save resources

    } catch (error: any) {
      osToast.fire({ icon: 'error', title: error.message });
      setStatus('READY');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative z-10 font-mono">
      <Link href="/admin/dashboard" className="absolute top-4 left-4 text-xs text-zinc-500 hover:text-green-500 uppercase transition-colors">
        [ Return to Root ]
      </Link>

      <div className="max-w-md w-full border border-zinc-800 bg-black p-8 shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-green-500 to-transparent opacity-50" />
        
        <h1 className="text-2xl font-bold mb-8 flex items-center justify-between text-white tracking-widest uppercase">
          <span className="flex items-center gap-3"><TerminalSquare className="w-6 h-6 text-green-500" /> Scanner</span>
          {isCameraActive && <span className="text-[10px] text-red-500 animate-pulse border border-red-500 px-2 py-1">REC</span>}
        </h1>

        <div className="aspect-video bg-zinc-900 flex items-center justify-center border border-zinc-800 mb-6 relative overflow-hidden group">
           <video ref={videoRef} autoPlay muted className={`absolute inset-0 w-full h-full object-cover grayscale ${isCameraActive ? 'opacity-100' : 'opacity-0'}`}></video>
           {status === 'SCANNING' && <div className="absolute top-0 left-0 w-full h-1 bg-green-500/80 shadow-[0_0_15px_#22c55e] animate-[scrolldown_2s_linear_infinite] z-20" />}
           {!isCameraActive && <Camera className={`w-12 h-12 transition-all duration-300 z-10 ${status === 'LOADING' ? 'text-zinc-800 animate-pulse' : 'text-zinc-600'}`} />}
        </div>

        <div className="flex gap-4">
          <button onClick={toggleScanner} disabled={status === 'LOADING' || status === 'SCANNING'} className={`flex-1 py-3 uppercase tracking-widest transition-all border flex items-center justify-center gap-2 ${isCameraActive ? 'bg-red-500/10 text-red-500 border-red-500/50 hover:bg-red-500 hover:text-black' : 'bg-zinc-900 text-white border-zinc-700 hover:border-green-500 disabled:opacity-50'}`}>
            {isCameraActive ? <><PowerOff className="w-4 h-4" /> Terminate</> : '1. Init Optics'}
          </button>

          <button onClick={executeScan} disabled={!isCameraActive || status === 'SCANNING'} className="flex-1 bg-green-500 hover:bg-green-400 text-black font-bold py-3 uppercase tracking-widest transition-all disabled:opacity-50">
            {status === 'SCANNING' ? 'Processing...' : '2. Scan Face'}
          </button>
        </div>
      </div>
      <style jsx>{`@keyframes scrolldown { 0% { transform: translateY(-100%); } 100% { transform: translateY(1000%); } }`}</style>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/attendance/page.tsx"), attendance_ui)

    print("\n====================================================")
    print(" [SUCCESS] OPTIMIZATION & ALERT MATRIX DEPLOYED.    ")
    print("====================================================\n")

if __name__ == "__main__":
    step07_deploy()