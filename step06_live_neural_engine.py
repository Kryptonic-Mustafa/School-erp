import os
import sys
import urllib.request
import subprocess

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
    print(f"  [+] Wrote Neural Component: {path}")

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"  [-] Model already exists: {os.path.basename(dest)}")
        return
    print(f"  [↓] Downloading {os.path.basename(dest)}...")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:
        print(f"[!] Failed to download {url}: {e}")
        sys.exit(1)

def step06_deploy():
    print("====================================================")
    print("   M.A.C.DevOS: LIVE NEURAL ENGINE DEPLOYMENT       ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> INSTALLING AI DEPENDENCIES...")
    run_command("npm install face-api.js", cwd=project_dir)

    print("\n>>> DOWNLOADING PRE-TRAINED NEURAL WEIGHTS (May take a minute)...")
    models_dir = os.path.join(project_dir, "public", "models")
    os.makedirs(models_dir, exist_ok=True)

    base_url = "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/"
    models = [
        "tiny_face_detector_model-weights_manifest.json",
        "tiny_face_detector_model-shard1",
        "face_landmark_68_model-weights_manifest.json",
        "face_landmark_68_model-shard1",
        "face_recognition_model-weights_manifest.json",
        "face_recognition_model-shard1",
        "face_recognition_model-shard2"
    ]

    for model in models:
        download_file(base_url + model, os.path.join(models_dir, model))

    print("\n>>> INJECTING LIVE BIOMETRIC INTERFACES...")

    # 1. Face Registration UI (Linking a face to a Student ID)
    register_ui = """
'use client';

import { useState, useEffect, useRef } from 'react';
import { Camera, Save, Users, ScanFace } from 'lucide-react';
import * as faceapi from 'face-api.js';
import Link from 'next/link';

export default function FaceRegistration() {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [status, setStatus] = useState('AWAITING_MODELS');
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    fetch('/api/students')
      .then(res => res.json())
      .then(data => { if (data.success) setStudents(data.students); });

    const loadModels = async () => {
      setStatus('LOADING_NEURAL_WEIGHTS...');
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models')
      ]);
      setModelsLoaded(true);
      setStatus('MODELS_ONLINE. AWAITING_CAMERA...');
    };
    loadModels();
  }, []);

  const startVideo = () => {
    setStatus('INITIALIZING_CAMERA...');
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) videoRef.current.srcObject = stream;
        setStatus('SYSTEM_READY');
      })
      .catch((err) => setStatus('CAMERA_ACCESS_DENIED'));
  };

  const captureFace = async () => {
    if (!videoRef.current || !selectedStudent) return;
    setStatus('SCANNING_BIOMETRICS...');

    const detection = await faceapi.detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceDescriptor();

    if (!detection) {
      setStatus('ERROR: NO_FACE_DETECTED');
      setTimeout(() => setStatus('SYSTEM_READY'), 3000);
      return;
    }

    // Convert Float32Array to standard array for JSON payload
    const vectorData = Array.from(detection.descriptor);

    setStatus('ENCRYPTING_AND_TRANSMITTING...');
    const res = await fetch('/api/face/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ studentId: selectedStudent, vectorData })
    });

    if (res.ok) {
      setStatus('SUCCESS: BIOMETRICS_LOCKED');
      setSelectedStudent('');
    } else {
      setStatus('ERROR: TRANSMISSION_FAILED');
    }
    setTimeout(() => setStatus('SYSTEM_READY'), 3000);
  };

  return (
    <div className="min-h-screen p-8 relative z-10 font-mono">
      <header className="mb-8 border-b border-zinc-800 pb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-3 text-white uppercase tracking-widest">
          <ScanFace className="w-6 h-6 text-green-500" />
          Biometric_Registry
        </h1>
        <Link href="/admin/dashboard" className="text-xs text-zinc-500 hover:text-green-500 uppercase transition-colors">
          [ Return to Root ]
        </Link>
      </header>

      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* CONTROL PANEL */}
        <div className="border border-zinc-800 bg-black p-6 flex flex-col gap-6 h-fit">
          <div className="p-3 bg-zinc-900 border border-zinc-700 text-xs text-green-500 uppercase flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            SYS_STATUS: {status}
          </div>

          <div>
            <label className="block text-zinc-500 uppercase mb-2 text-sm">1. Select Target Subject</label>
            <select 
              value={selectedStudent} 
              onChange={(e) => setSelectedStudent(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500"
            >
              <option value="">-- AWAITING_SELECTION --</option>
              {students.map(s => (
                <option key={s.id} value={s.id}>{s.name} ({s.class.name})</option>
              ))}
            </select>
          </div>

          <button 
            onClick={startVideo} 
            disabled={!modelsLoaded}
            className="w-full bg-zinc-900 text-white border border-zinc-700 py-3 uppercase tracking-widest hover:border-green-500 disabled:opacity-50 transition-all"
          >
            2. Initialize Optics
          </button>

          <button 
            onClick={captureFace} 
            disabled={!selectedStudent || status !== 'SYSTEM_READY'}
            className="w-full bg-green-500 text-black font-bold py-3 uppercase tracking-widest hover:bg-green-400 disabled:opacity-50 transition-all flex justify-center items-center gap-2"
          >
            <Save className="w-5 h-5" />
            3. Lock Biometrics
          </button>
        </div>

        {/* OPTICS VIEWER */}
        <div className="border border-zinc-800 bg-black p-6 flex flex-col items-center justify-center min-h-[400px] relative">
           <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-green-500 to-transparent opacity-50" />
           <div className="relative w-full aspect-video bg-zinc-900 border border-zinc-800 overflow-hidden">
             <video ref={videoRef} autoPlay muted className="absolute inset-0 w-full h-full object-cover"></video>
             <canvas ref={canvasRef} className="absolute inset-0 w-full h-full object-cover z-10"></canvas>
             {status === 'SCANNING_BIOMETRICS...' && (
                <div className="absolute inset-0 border-2 border-green-500 animate-pulse z-20" />
             )}
           </div>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/face-register/page.tsx"), register_ui)

    # 2. Overwrite Attendance Kiosk with Live Live Engine
    attendance_ui = """
'use client';

import { useState, useEffect, useRef } from 'react';
import { Camera, TerminalSquare, ShieldCheck, AlertTriangle } from 'lucide-react';
import * as faceapi from 'face-api.js';
import { encryptPayload } from '@/lib/crypto_engine';

export default function AttendanceKiosk() {
  const [status, setStatus] = useState<'LOADING' | 'READY' | 'SCANNING' | 'SUCCESS' | 'FAILED'>('LOADING');
  const [message, setMessage] = useState('INITIALIZING_NEURAL_NET...');
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const initSystem = async () => {
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models')
      ]);
      setMessage('AWAITING_OPTICS_ACTIVATION');
      setStatus('READY');
    };
    initSystem();
  }, []);

  const handleScan = async () => {
    if (status !== 'READY' && status !== 'FAILED') return;
    setStatus('SCANNING');
    setMessage('ACTIVATING_OPTICS...');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) videoRef.current.srcObject = stream;
      
      // Wait for video to stabilize
      await new Promise(resolve => setTimeout(resolve, 1500));
      setMessage('ANALYZING_VECTOR_FIELD...');

      const detection = await faceapi.detectSingleFace(videoRef.current!, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceDescriptor();

      if (!detection) {
        throw new Error('NO_SUBJECT_DETECTED');
      }

      setMessage('ENCRYPTING_PAYLOAD...');
      const vectorData = Array.from(detection.descriptor);
      
      // In a real system, we'd know the class ID based on the teacher's login or schedule.
      // For this matrix, we'll hardcode the target class or pass empty to search all.
      const payload = encryptPayload(JSON.stringify({
        classId: 'CS-101', // Should match the class you assigned John/Emily
        capturedEmbedding: vectorData
      }));

      const res = await fetch('/api/attendance/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ encryptedData: payload })
      });

      const data = await res.json();

      // Turn off camera
      stream.getTracks().forEach(track => track.stop());
      if (videoRef.current) videoRef.current.srcObject = null;

      if (res.ok) {
        setStatus('SUCCESS');
        setMessage(data.message || 'IDENTITY_VERIFIED');
      } else {
        throw new Error(data.error || 'UNAUTHORIZED_ENTITY');
      }
    } catch (error: any) {
      setStatus('FAILED');
      setMessage(error.message);
      if (videoRef.current?.srcObject) {
        (videoRef.current.srcObject as MediaStream).getTracks().forEach(track => track.stop());
      }
    }

    setTimeout(() => {
      setStatus('READY');
      setMessage('AWAITING_OPTICS_ACTIVATION');
    }, 4000);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative z-10 font-mono">
      <div className="max-w-md w-full border border-zinc-800 bg-black p-8 shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-green-500 to-transparent opacity-50" />
        
        <h1 className="text-2xl font-bold mb-8 flex items-center gap-3 text-white tracking-widest uppercase">
          <TerminalSquare className="w-6 h-6 text-green-500" />
          Live_Scanner
        </h1>

        <div className="aspect-video bg-zinc-900 flex items-center justify-center border border-zinc-800 mb-6 relative overflow-hidden group">
           <video ref={videoRef} autoPlay muted className="absolute inset-0 w-full h-full object-cover opacity-50 grayscale"></video>
           
           {status === 'SCANNING' && (
             <div className="absolute top-0 left-0 w-full h-1 bg-green-500/80 shadow-[0_0_15px_#22c55e] animate-[scrolldown_2s_linear_infinite] z-20" />
           )}
           
           {(!videoRef.current?.srcObject) && (
             <Camera className={`w-12 h-12 transition-all duration-300 z-10 ${status === 'LOADING' ? 'text-zinc-800 animate-pulse' : 'text-zinc-600'}`} />
           )}
        </div>

        <div className="text-xs uppercase tracking-widest text-center mb-6 h-4 text-zinc-400">
           {status === 'FAILED' ? <span className="text-red-500 animate-pulse">{message}</span> : message}
        </div>

        <button 
          onClick={handleScan}
          disabled={status === 'LOADING' || status === 'SCANNING'}
          className="w-full bg-zinc-900 hover:bg-zinc-800 text-green-500 border border-green-500/30 hover:border-green-500 py-3 uppercase tracking-widest transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'SCANNING' ? 'Processing...' : 'Execute Scan'}
        </button>

        {status === 'SUCCESS' && (
          <div className="mt-4 p-3 bg-green-500/10 border border-green-500 text-green-400 flex items-center gap-3 text-sm uppercase">
            <ShieldCheck className="w-5 h-5" />
            <span>Attendance Logged.</span>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes scrolldown {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(1000%); }
        }
      `}</style>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/attendance/page.tsx"), attendance_ui)

    # 3. Inject Link into Admin Dashboard
    dashboard_path = os.path.join(project_dir, "src/app/admin/dashboard/page.tsx")
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            admin_content = f.read()
        
        new_block = """
        {/* NEW: Biometric Registry Link */}
        <Link href="/admin/face-register" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group col-span-1 md:col-span-3 lg:col-span-1">
          <ScanFace className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Biometric Registry</h2>
          <p className="text-sm text-zinc-400 mb-4">Capture and map physical vectors to active entities.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Initialize Optics <span className="animate-pulse">_</span></span>
        </Link>
        """
        
        # Replace the restricted block with the new Registry block
        import re
        admin_content = re.sub(
            r'\{\/\*\s*Restricted Telemetry Block\s*\*\/\}.*?</div>\s*</div>', 
            new_block.strip() + "\n      </div>", 
            admin_content, 
            flags=re.DOTALL
        )
        create_file(dashboard_path, admin_content)

    print("\n====================================================")
    print(" [SUCCESS] LIVE NEURAL ENGINE INTEGRATED.")
    print("====================================================\n")

if __name__ == "__main__":
    step06_deploy()