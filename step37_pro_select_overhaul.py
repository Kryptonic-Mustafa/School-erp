import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] UI Polished: {path}")

def step37_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: PRO-SELECT & BADGE UI OVERHAUL       ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)

    print("\n>>> 1. POLISHING FACE REGISTER (SINGLE SEARCH SELECT)...")

    face_reg_ui = """
'use client';

import { useState, useEffect, useRef } from 'react';
import * as faceapi from 'face-api.js';
import { Camera, ScanFace, CheckCircle2, AlertCircle, RefreshCcw, Search, ChevronDown, User } from 'lucide-react';
import { osAlert, osToast, osLoader } from '@/lib/alert_engine';

export default function FaceRegister() {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [isModelsLoaded, setIsModelsLoaded] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [appError, setAppError] = useState<string | null>(null);
  
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/api/students').then(r => r.json()).then(data => {
      if (data.success) setStudents(data.students);
    }).catch(() => setAppError("Database Offline."));

    const loadModels = async () => {
      try {
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
          faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
          faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
        ]);
        setIsModelsLoaded(true);
      } catch (err) { setAppError("AI Models missing."); }
    };
    loadModels();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) { videoRef.current.srcObject = stream; setIsCameraActive(true); }
    } catch (err) { osAlert.error("Camera Error", "Permissions denied."); }
  };

  const captureAndRegister = async () => {
    if (!selectedStudent) return osToast.fire({ icon: 'warning', title: 'Select a student' });
    osLoader.show("Mapping Face...");
    try {
      const detection = await faceapi.detectSingleFace(videoRef.current!, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptor();
      if (!detection) { osLoader.hide(); return osAlert.error("No Face Detected", "Look directly at camera."); }
      const res = await fetch('/api/face/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentId: selectedStudent.id, descriptor: Array.from(detection.descriptor) })
      });
      if (res.ok) { 
        osAlert.success("Linked", "Biometrics synced."); 
        (videoRef.current!.srcObject as MediaStream).getTracks().forEach(t => t.stop());
        setIsCameraActive(false);
      }
    } catch (err) { osAlert.error("AI Error", "Failed to extract features."); } finally { osLoader.hide(); }
  };

  const filteredStudents = students.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.user.email.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm h-fit">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600"><ScanFace /></div>
            <h2 className="text-xl font-bold text-slate-800 tracking-tight">Biometric Link</h2>
          </div>

          <div className="space-y-6">
            <div className="relative" ref={dropdownRef}>
              <label className="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-widest">Select Student Profile</label>
              <div 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className={`flex items-center justify-between w-full bg-slate-50 border rounded-xl p-3.5 cursor-pointer transition-all ${isDropdownOpen ? 'border-blue-500 ring-4 ring-blue-50' : 'border-slate-200 hover:border-slate-300'}`}
              >
                <div className="flex items-center gap-3 truncate">
                  <User className="w-4 h-4 text-slate-400" />
                  <span className={`text-sm ${selectedStudent ? 'text-slate-800 font-semibold' : 'text-slate-400'}`}>
                    {selectedStudent ? `${selectedStudent.name} (${selectedStudent.user.email})` : '-- Choose Student --'}
                  </span>
                </div>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </div>

              {isDropdownOpen && (
                <div className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-2xl overflow-hidden">
                  <div className="p-2 border-b border-slate-100 sticky top-0 bg-white/80 backdrop-blur-md">
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input 
                        autoFocus
                        type="text" 
                        placeholder="Search..." 
                        className="w-full bg-slate-100 rounded-lg py-2 pl-9 pr-3 text-xs outline-none focus:ring-2 focus:ring-blue-500"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="max-h-[300px] overflow-y-auto">
                    {filteredStudents.length === 0 ? (
                      <div className="p-4 text-center text-xs text-slate-400">No students found.</div>
                    ) : filteredStudents.map(s => (
                      <div 
                        key={s.id}
                        onClick={() => { setSelectedStudent(s); setIsDropdownOpen(false); setSearchQuery(''); }}
                        className="p-3 hover:bg-blue-50 cursor-pointer border-b border-slate-50 last:border-0 transition-colors"
                      >
                        <div className="text-sm font-bold text-slate-700">{s.name}</div>
                        <div className="text-[10px] text-slate-400 font-medium">{s.user.email}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {!isModelsLoaded ? (
              <div className="w-full bg-slate-50 border border-slate-100 text-slate-400 py-3.5 rounded-xl text-center text-xs font-bold flex items-center justify-center gap-2">
                <RefreshCcw className="w-4 h-4 animate-spin" /> Initializing...
              </div>
            ) : (
              <button 
                onClick={isCameraActive ? captureAndRegister : startCamera}
                className={`w-full py-4 rounded-xl font-bold text-white shadow-lg transition-all flex items-center justify-center gap-3 ${isCameraActive ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-blue-600 hover:bg-blue-700'}`}
              >
                {isCameraActive ? 'Capture Biometrics' : 'Open Optical Scanner'}
              </button>
            )}
          </div>
        </div>

        <div className="bg-slate-900 rounded-2xl overflow-hidden aspect-video relative flex items-center justify-center border-4 border-slate-800">
           <video ref={videoRef} autoPlay muted className={`w-full h-full object-cover ${isCameraActive ? 'block' : 'hidden'}`} />
        </div>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/face-register/page.tsx"), face_reg_ui)

    print("\n>>> 2. POLISHING STUDENT DIRECTORY (BADGES INSIDE FIELD)...")

    students_ui_path = os.path.join(project_dir, "src/app/admin/students/page.tsx")
    if os.path.exists(students_ui_path):
        with open(students_ui_path, "r", encoding="utf-8") as f:
            student_code = f.read()

        import_line = "import { Search, Plus, Trash2, Edit, GraduationCap, X, ChevronLeft, ChevronRight } from 'lucide-react';"
        if "X," not in student_code:
            student_code = student_code.replace("import { Search, Plus, Trash2, Edit, GraduationCap, ChevronLeft, ChevronRight }", import_line)

        # Replacing the older multi-select layout with the new "Inside-Badge" container
        old_classes_block = """<div className="space-y-3">
            <label className="block text-sm font-medium flex justify-between items-center">Classes <span className="text-xs text-blue-600 font-semibold bg-blue-50 px-2 py-0.5 rounded-full">{formData.classIds.length} Selected</span></label>
            <div className="relative"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input type="text" placeholder="Filter classes..." value={classSearchQuery} onChange={e => setClassSearchQuery(e.target.value)} className="w-full bg-white border border-slate-300 rounded-lg py-2.5 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 shadow-sm" /></div>
            <div className="border border-slate-200 rounded-lg bg-slate-50 p-2 h-40 overflow-y-auto space-y-1 shadow-inner">"""

        new_classes_block = """<div className="space-y-2">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest">Enroll in Classes</label>
            <div className="min-h-[46px] p-1.5 bg-slate-50 border border-slate-200 rounded-xl focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
               <div className="flex flex-wrap gap-1.5 mb-1">
                  {formData.classIds.map(id => {
                    const c = classes.find(cls => cls.id === id);
                    if (!c) return null;
                    return (
                      <span key={id} className="bg-white border border-slate-200 shadow-sm text-blue-700 text-[10px] font-bold px-2 py-1 rounded-lg flex items-center gap-1.5">
                        {c.name}
                        <X onClick={() => removeClass(id)} className="w-3 h-3 cursor-pointer hover:text-red-500" />
                      </span>
                    );
                  })}
               </div>
               <div className="relative">
                 <Search className="w-3.5 h-3.5 absolute left-2 top-1/2 -translate-y-1/2 text-slate-400" />
                 <input 
                   type="text" 
                   placeholder={formData.classIds.length > 0 ? "" : "Search to assign classes..."}
                   className="w-full bg-transparent pl-7 pr-2 py-1 text-sm outline-none text-slate-700"
                   value={classSearchQuery}
                   onChange={e => setClassSearchQuery(e.target.value)}
                 />
               </div>
            </div>
            <div className="border border-slate-200 rounded-xl bg-white h-32 overflow-y-auto space-y-0.5 shadow-inner">"""

        student_code = student_code.replace(old_classes_block, new_classes_block)
        create_file(students_ui_path, student_code)

    print("\n====================================================")
    print(" [SUCCESS] PRO DROPDOWNS & BADGES DEPLOYED.          ")
    print("====================================================\n")

if __name__ == "__main__":
    step37_deploy()