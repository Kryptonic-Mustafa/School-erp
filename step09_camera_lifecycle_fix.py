import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Cleanly Rewrote: {path}")

def step09_deploy():
    print("====================================================")
    print("   M.A.C.DevOS: CAMERA LIFECYCLE & MEMORY PATCH     ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    # 1. CLEAN REWRITE: Biometric Registry
    registry_tsx = """
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

  // Core Hardware Kill Switch
  const terminateOptics = useCallback((showToast = true) => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setStatus('SYSTEM_READY');
    if (showToast) osToast.fire({ icon: 'info', title: 'Optics Terminated' });
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

    // Critical Unmount Cleanup (Closes camera silently when leaving page)
    return () => terminateOptics(false);
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
      
      // Auto-close camera SILENTLY on success
      terminateOptics(false); 
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
            <button onClick={() => terminateOptics(true)} className="w-full bg-red-500/10 text-red-500 border border-red-500/50 py-3 uppercase hover:bg-red-500 hover:text-black transition-all flex justify-center items-center gap-2">
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
    create_file(os.path.join(project_dir, "src/app/admin/face-register/page.tsx"), registry_tsx)

    # 2. CLEAN REWRITE: Attendance Scanner
    attendance_tsx = """
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

  const terminateOptics = useCallback((showToast = true) => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setStatus('READY');
    if (showToast) osToast.fire({ icon: 'info', title: 'Optics Terminated' });
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

    // Silently terminate on unmount (leaving the page)
    return () => terminateOptics(false);
  }, [terminateOptics]);

  const toggleScanner = async () => {
    if (isCameraActive) {
      terminateOptics(true);
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
      
      // Auto-shutdown camera silently on success to save resources
      terminateOptics(false); 

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
    create_file(os.path.join(project_dir, "src/app/attendance/page.tsx"), attendance_tsx)

    print("\n====================================================")
    print(" [SUCCESS] CAMERA LIFECYCLE PERFECTLY RESTORED.     ")
    print("====================================================\n")

if __name__ == "__main__":
    step09_deploy()