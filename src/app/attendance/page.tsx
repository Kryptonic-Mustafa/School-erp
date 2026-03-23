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
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Neural Memory & Spam Prevention
  const faceMatcherRef = useRef<faceapi.FaceMatcher | null>(null);
  const cooldownMap = useRef<Map<string, number>>(new Map());
  const scanInterval = useRef<NodeJS.Timeout | null>(null);

  const terminateOptics = useCallback((showToast = true) => {
    if (scanInterval.current) clearInterval(scanInterval.current);
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    }
    setIsCameraActive(false);
    setStatus('READY');
    if (showToast) osToast.fire({ icon: 'info', title: 'Scanner Offline' });
  }, []);

  useEffect(() => {
    const initSystem = async () => {
      // 1. Load Models
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models')
      ]);

      // 2. Fetch Neural Data from DB
      const res = await fetch('/api/face/sync');
      const data = await res.json();
      
      if (data.success && data.data.length > 0) {
        const labeledDescriptors = data.data.map((d: any) => {
          const descriptors = d.descriptors.map((desc: any) => new Float32Array(desc));
          return new faceapi.LabeledFaceDescriptors(d.label, descriptors);
        });
        faceMatcherRef.current = new faceapi.FaceMatcher(labeledDescriptors, 0.45);
      }
      setStatus('READY');
    };
    initSystem();
    return () => terminateOptics(false);
  }, [terminateOptics]);

  const toggleScanner = async () => {
    if (isCameraActive) return terminateOptics(false);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) { 
        videoRef.current.srcObject = stream; 
        setIsCameraActive(true); 
      }
    } catch (e) { osAlert.error('Hardware Error', 'Camera access denied.'); }
  };

  // Continuous Detection Loop
  const handleVideoPlay = () => {
    if (!videoRef.current || !canvasRef.current || !faceMatcherRef.current) return;
    setStatus('SCANNING');

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const displaySize = { width: video.videoWidth, height: video.videoHeight };
    faceapi.matchDimensions(canvas, displaySize);

    scanInterval.current = setInterval(async () => {
      const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceDescriptors();

      const resizedDetections = faceapi.resizeResults(detections, displaySize);
      const ctx = canvas.getContext('2d');
      ctx?.clearRect(0, 0, canvas.width, canvas.height);

      for (const detection of resizedDetections) {
        const match = faceMatcherRef.current!.findBestMatch(detection.descriptor);
        const box = detection.detection.box;

        // Draw Custom Green Box & Tooltip
        const drawBox = new faceapi.draw.DrawBox(box, { 
          label: match.label === 'unknown' ? 'Unknown Entity' : match.label.split('|')[1], 
          boxColor: match.label === 'unknown' ? '#ef4444' : '#22c55e', // Red if unknown, Green if known
          lineWidth: 3
        });
        drawBox.draw(canvas);

        // Auto-Log Attendance (Anti-Spam: 60 sec cooldown per student)
        if (match.label !== 'unknown') {
          const studentId = match.label.split('|')[0];
          const studentName = match.label.split('|')[1];
          const now = Date.now();
          const lastScan = cooldownMap.current.get(studentId) || 0;

          if (now - lastScan > 60000) { // 60 seconds cooldown
            cooldownMap.current.set(studentId, now);
            
            // Send to backend
            const payload = encryptPayload(JSON.stringify({ classId: '', capturedEmbedding: Array.from(detection.descriptor) }));
            fetch('/api/attendance/mark', { 
              method: 'POST', 
              headers: { 'Content-Type': 'application/json' }, 
              body: JSON.stringify({ encryptedData: payload }) 
            }).then(async (res) => {
              const resData = await res.json();
              if (res.ok && resData.message === 'ATTENDANCE_VERIFIED') {
                osAlert.success('Attendance Logged', `${studentName} has been marked Present.`);
                terminateOptics(false); // Instantly close camera
              } else if (resData.message === 'SUBJECT_ALREADY_LOGGED_TODAY') {
                osAlert.error('Already Logged', `${studentName} is already marked for today.`);
                terminateOptics(false); // Instantly close camera
              }
            });
          }
        }
      }
    }, 200); // 5 FPS is optimal for web
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-100 font-sans">
      <Link href="/admin/dashboard" className="absolute top-6 left-6 flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-blue-600 bg-white px-4 py-2 rounded-lg shadow-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-blue-600 p-6 text-center text-white">
          <UserCheck className="w-12 h-12 mx-auto mb-3 opacity-90" />
          <h1 className="text-2xl font-bold tracking-tight">Live AI Scanner</h1>
          <p className="text-blue-100 text-sm mt-1">Stand in front of the camera. Attendance is logged automatically.</p>
        </div>

        <div className="p-8">
          <div className="aspect-video bg-slate-100 rounded-xl border-2 border-slate-200 mb-8 relative overflow-hidden shadow-inner flex items-center justify-center">
             <video ref={videoRef} onPlay={handleVideoPlay} autoPlay muted className={`absolute inset-0 w-full h-full object-cover ${isCameraActive ? 'opacity-100' : 'opacity-0'}`}></video>
             {/* THE NEURAL CANVAS OVERLAY */}
             <canvas ref={canvasRef} className="absolute inset-0 w-full h-full object-cover z-20 pointer-events-none" />
             
             {!isCameraActive && <Camera className="w-16 h-16 text-slate-300 z-10" />}
          </div>

          <button onClick={toggleScanner} disabled={status === 'LOADING'} className={`w-full py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2 ${isCameraActive ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100' : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'}`}>
            {isCameraActive ? <><PowerOff className="w-5 h-5" /> Deactivate Scanner</> : 'Initialize Optical Engine'}
          </button>
        </div>
      </div>
    </div>
  );
}
