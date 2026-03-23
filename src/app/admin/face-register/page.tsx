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
