import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Deployed: {path}")

def step15_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: REAL-TIME SCANNER & ATTENDANCE GRID  ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. INJECTING NEURAL SYNC & ATTENDANCE APIs...")

    # A. Face Vector Sync API (Feeds the browser FaceMatcher)
    api_sync = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET() {
  try {
    const students = await db.student.findMany({
      include: { embeddings: true }
    });
    // Format for face-api.js LabeledFaceDescriptors
    const labeledData = students.filter(s => s.embeddings.length > 0).map(s => ({
      label: `${s.id}|${s.name}`,
      descriptors: s.embeddings.map(e => e.vectorData)
    }));
    return NextResponse.json({ success: true, data: labeledData });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to sync vectors' }, { status: 500 });
  }
}
"""
    create_file(os.path.join(project_dir, "src/app/api/face/sync/route.ts"), api_sync)

    # B. Attendance Management CRUD API
    api_attendance = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const month = parseInt(searchParams.get('month') || (new Date().getMonth() + 1).toString());
    const year = parseInt(searchParams.get('year') || new Date().getFullYear().toString());

    const startDate = new Date(year, month - 1, 1);
    const endDate = new Date(year, month, 0, 23, 59, 59);

    const students = await db.student.findMany({
      include: {
        class: true,
        attendances: {
          where: { date: { gte: startDate, lte: endDate } }
        }
      },
      orderBy: { name: 'asc' }
    });

    return NextResponse.json({ success: true, students });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch attendance' }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { studentId, date, status } = await req.json(); // status: 'P', 'A', 'L'
    
    const targetDate = new Date(date);
    targetDate.setHours(12, 0, 0, 0); // Normalize to noon to avoid timezone shifts
    
    const startOfDay = new Date(targetDate); startOfDay.setHours(0,0,0,0);
    const endOfDay = new Date(targetDate); endOfDay.setHours(23,59,59,999);

    const existing = await db.attendance.findFirst({
      where: { studentId, date: { gte: startOfDay, lte: endOfDay } }
    });

    if (existing) {
      if (status === 'NONE') {
        await db.attendance.delete({ where: { id: existing.id } });
      } else {
        await db.attendance.update({ where: { id: existing.id }, data: { status } });
      }
    } else if (status !== 'NONE') {
      await db.attendance.create({
        data: { studentId, date: targetDate, status, confidence: 1.0 } // 1.0 = Manual override
      });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to update record' }, { status: 500 });
  }
}
"""
    create_file(os.path.join(project_dir, "src/app/api/attendance/route.ts"), api_attendance)

    print("\n>>> 2. UPGRADING LIVE SCANNER (REAL-TIME BOUNDING BOXES)...")

    # C. REAL-TIME CONTINUOUS SCANNER
    scanner_ui = """
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
              if (res.ok) {
                osToast.fire({ icon: 'success', title: `${studentName} Marked Present` });
              } else if (resData.message === 'SUBJECT_ALREADY_LOGGED_TODAY') {
                // Ignore silent duplicate
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
"""
    create_file(os.path.join(project_dir, "src/app/attendance/page.tsx"), scanner_ui)

    print("\n>>> 3. DEPLOYING 30-DAY ENTERPRISE ERP MATRIX...")

    # D. Attendance Management Dashboard
    admin_attendance_ui = """
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
      const status = (document.getElementById('swal-status') as HTMLSelectElement).value;
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
                    <div className="text-xs text-slate-500">{student.class?.name}</div>
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
"""
    create_file(os.path.join(project_dir, "src/app/admin/attendance/page.tsx"), admin_attendance_ui)

    print("\n>>> 4. ADDING ATTENDANCE MANAGER TO SIDEBAR...")

    # E. Update Layout Sidebar
    layout_path = os.path.join(project_dir, "src/app/admin/layout.tsx")
    with open(layout_path, "r", encoding="utf-8") as f:
        layout_code = f.read()
    
    new_nav = """
  const navItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Students', href: '/admin/students', icon: GraduationCap },
    { name: 'Classes', href: '/admin/classes', icon: BookOpen },
    { name: 'Attendance Logs', href: '/admin/attendance', icon: CalendarDays },
    { name: 'User Management', href: '/admin/users', icon: Users },
    { name: 'Roles & Access', href: '/admin/roles', icon: Settings },
    { name: 'Live Scanner', href: '/attendance', icon: Camera },
    { name: 'Biometrics', href: '/admin/face-register', icon: ScanFace },
    { name: 'Telemetry', href: '/admin/telemetry', icon: Activity },
  ];
"""
    import re
    layout_code = re.sub(r'const navItems = \[.*?\];', new_nav.strip(), layout_code, flags=re.DOTALL)
    
    # Ensure CalendarDays is imported
    if "CalendarDays" not in layout_code:
        layout_code = layout_code.replace("Activity, Settings, LogOut", "Activity, Settings, LogOut, CalendarDays")
    
    create_file(layout_path, layout_code)

    print("\n====================================================")
    print(" [SUCCESS] ATTENDANCE MASTERY SYSTEM ONLINE.        ")
    print("====================================================\n")

if __name__ == "__main__":
    step15_deploy()