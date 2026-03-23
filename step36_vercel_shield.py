import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Shield Applied: {path}")

def step36_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: VERCEL PRODUCTION SHIELD & DEBUG     ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)

    print("\n>>> PATCHING FACE-REGISTER PAGE FOR STABILITY...")

    # We are rewriting the page with better error boundaries
    face_reg_ui = """
'use client';

import { useState, useEffect, useRef } from 'react';
import * as faceapi from 'face-api.js';
import { Camera, ScanFace, CheckCircle2, AlertCircle, RefreshCcw } from 'lucide-react';
import { osAlert, osToast, osLoader } from '@/lib/alert_engine';
import SystemLoader from '@/components/SystemLoader';

export default function FaceRegister() {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [isModelsLoaded, setIsModelsLoaded] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [appError, setAppError] = useState<string | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);

  // 1. Fetch Students with Error Handling
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        console.log("Fetching students from API...");
        const res = await fetch('/api/students');
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        const data = await res.json();
        if (data.success) setStudents(data.students);
      } catch (err: any) {
        console.error("Student Fetch Error:", err);
        setAppError("Could not load student list. Check Database connection.");
      }
    };
    fetchStudents();
  }, []);

  // 2. Load AI Models with Path Verification
  useEffect(() => {
    const loadModels = async () => {
      try {
        console.log("Loading FaceAPI models from /models...");
        const MODEL_URL = '/models';
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
          faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
          faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
        ]);
        setIsModelsLoaded(true);
      } catch (err: any) {
        console.error("Model Loading Error:", err);
        setAppError("AI Models missing. Ensure /public/models is deployed.");
      }
    };
    loadModels();
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (err) {
      osAlert.error("Camera Error", "Please allow camera permissions in your browser.");
    }
  };

  const captureAndRegister = async () => {
    if (!selectedStudent) return osToast.fire({ icon: 'warning', title: 'Select a student first' });
    if (!videoRef.current) return;

    osLoader.show("Extracting Biometric Map...");
    try {
      const detection = await faceapi.detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceDescriptor();

      if (!detection) {
        osLoader.hide();
        return osAlert.error("No Face Detected", "Please look directly at the camera in good lighting.");
      }

      const res = await fetch('/api/face/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentId: selectedStudent, descriptor: Array.from(detection.descriptor) })
      });

      if (res.ok) {
        osAlert.success("Registration Success", "Biometric ID linked to profile.");
        // Stop camera
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
        setIsCameraActive(false);
      } else {
        throw new Error("API Save Failed");
      }
    } catch (err) {
      osAlert.error("AI Error", "Biometric extraction failed.");
    } finally {
      osLoader.hide();
    }
  };

  // ERROR STATE UI
  if (appError) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6 bg-white rounded-2xl border border-red-100">
        <AlertCircle className="w-16 h-16 text-red-500 mb-4 animate-bounce" />
        <h2 className="text-xl font-bold text-slate-800 mb-2">System Sync Error</h2>
        <p className="text-slate-500 max-w-md mb-6">{appError}</p>
        <button onClick={() => window.location.reload()} className="flex items-center gap-2 bg-slate-800 text-white px-6 py-2.5 rounded-lg font-medium">
          <RefreshCcw className="w-4 h-4" /> Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm h-fit">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600"><ScanFace /></div>
            <h2 className="text-xl font-bold text-slate-800">Biometric Registration</h2>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2 uppercase tracking-wider">1. Select Student Profile</label>
              <select 
                value={selectedStudent} 
                onChange={(e) => setSelectedStudent(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              >
                <option value="">-- Choose Student --</option>
                {students.map(s => <option key={s.id} value={s.id}>{s.name} ({s.user.email})</option>)}
              </select>
            </div>

            <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
               <p className="text-xs text-blue-700 leading-relaxed font-medium">
                 Ensure the subject is in a well-lit area. The AI will convert the facial geometry into a unique encrypted 128-bit vector.
               </p>
            </div>

            {!isModelsLoaded ? (
              <div className="w-full bg-slate-100 text-slate-500 py-3 rounded-xl text-center text-sm font-bold flex items-center justify-center gap-2">
                <RefreshCcw className="w-4 h-4 animate-spin" /> Syncing AI Neural Models...
              </div>
            ) : (
              <button 
                onClick={isCameraActive ? captureAndRegister : startCamera}
                className={`w-full py-4 rounded-xl font-bold text-white shadow-lg transition-all flex items-center justify-center gap-3 ${isCameraActive ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-blue-600 hover:bg-blue-700'}`}
              >
                {isCameraActive ? <CheckCircle2 className="w-5 h-5" /> : <Camera className="w-5 h-5" />}
                {isCameraActive ? '3. Capture & Sync' : '2. Activate Optical Scanner'}
              </button>
            )}
          </div>
        </div>

        <div className="bg-slate-900 rounded-2xl overflow-hidden aspect-video relative flex items-center justify-center border-4 border-slate-800 shadow-2xl">
           {!isCameraActive && (
              <div className="text-center">
                <Camera className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                <p className="text-slate-500 text-sm">Optical feed will appear here</p>
              </div>
           )}
           <video ref={videoRef} autoPlay muted className={`w-full h-full object-cover ${isCameraActive ? 'block' : 'hidden'}`} />
           {isCameraActive && <div className="absolute inset-0 border-[40px] border-slate-900/20 pointer-events-none flex items-center justify-center">
             <div className="w-64 h-64 border-2 border-blue-400/50 rounded-full animate-pulse flex items-center justify-center">
                <div className="w-48 h-48 border border-blue-400/30 rounded-full"></div>
             </div>
           </div>}
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/face-register/page.tsx"), face_reg_ui)

    print("\n====================================================")
    print(" [SUCCESS] PRODUCTION SHIELD DEPLOYED.              ")
    print("====================================================\n")

if __name__ == "__main__":
    step36_deploy()