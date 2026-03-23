import os
import sys

PROJECT_NAME = "school-os"

def apply_patch():
    print("====================================================")
    print("    M.A.C.DevOS PATCH: ICON DEPENDENCY RESOLUTION   ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    dashboard_path = os.path.join(project_dir, "src/app/admin/dashboard/page.tsx")

    correct_tsx = """import { Terminal, Users, Camera, Activity, ScanFace } from 'lucide-react';
import Link from 'next/link';

export default function AdminDashboard() {
  return (
    <div className="min-h-screen p-8 relative z-10 font-mono">
      <header className="flex justify-between items-center mb-12 border-b border-zinc-800 pb-6">
        <h1 className="text-3xl font-bold flex items-center gap-3 text-white uppercase tracking-widest">
          <Terminal className="w-8 h-8 text-green-500" />
          Root_Command
        </h1>
        <div className="text-xs text-zinc-500 uppercase flex flex-col items-end">
           <span>Status: <span className="text-green-500">Online</span></span>
           <span>Role: Admin</span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Entity Matrix Link */}
        <Link href="/admin/students" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group">
          <Users className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Entity Management</h2>
          <p className="text-sm text-zinc-400 mb-4">Manage students, teachers, and system access.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Access Matrix <span className="animate-pulse">_</span></span>
        </Link>

        {/* Scanner Link */}
        <Link href="/attendance" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group">
          <Camera className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Launch Scanner</h2>
          <p className="text-sm text-zinc-400 mb-4">Initialize the face recognition attendance kiosk.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Execute <span className="animate-pulse">_</span></span>
        </Link>

        {/* Biometric Registry Link (Now properly imported) */}
        <Link href="/admin/face-register" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group">
          <ScanFace className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Biometric Registry</h2>
          <p className="text-sm text-zinc-400 mb-4">Capture and map physical vectors to active entities.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Initialize Optics <span className="animate-pulse">_</span></span>
        </Link>
      </div>
    </div>
  );
}
"""
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(correct_tsx)

    print("\n[+] Added missing 'ScanFace' import from lucide-react.")
    print("[SUCCESS] Module online. Turbopack will hot-reload.")
    print("====================================================\n")

if __name__ == "__main__":
    apply_patch()