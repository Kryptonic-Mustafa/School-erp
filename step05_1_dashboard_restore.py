import os
import sys

PROJECT_NAME = "school-os"

def apply_patch():
    print("====================================================")
    print("    M.A.C.DevOS PATCH: DASHBOARD MATRIX RESTORE     ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    dashboard_path = os.path.join(project_dir, "src/app/admin/dashboard/page.tsx")

    correct_tsx = """import { Terminal, Users, Camera, Activity } from 'lucide-react';
import Link from 'next/link';

export default function AdminDashboard() {
  return (
    <div className="min-h-screen p-8 relative z-10">
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
        {/* Unlocked Entity Matrix Link */}
        <Link href="/admin/students" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group">
          <Users className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Entity Management</h2>
          <p className="text-sm text-zinc-400 mb-4">Manage students, teachers, and system access.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Access Matrix <span className="animate-pulse">_</span></span>
        </Link>

        {/* Existing Scanner Link */}
        <Link href="/attendance" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group">
          <Camera className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Launch Scanner</h2>
          <p className="text-sm text-zinc-400 mb-4">Initialize the face recognition attendance kiosk.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">&gt;&gt; Execute <span className="animate-pulse">_</span></span>
        </Link>

        {/* Restricted Telemetry Block */}
        <div className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors">
          <Activity className="w-8 h-8 mb-4 text-green-500" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">System Telemetry</h2>
          <p className="text-sm text-zinc-400 mb-4">View attendance metrics and audit logs.</p>
          <span className="text-xs text-zinc-600 uppercase">&gt;&gt; Access Restricted</span>
        </div>
      </div>
    </div>
  );
}
"""
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(correct_tsx)

    print("\n[+] Admin Dashboard layout completely restored.")
    print("[SUCCESS] Grid Matrix Online. Turbopack will hot-reload.")
    print("====================================================\n")

if __name__ == "__main__":
    apply_patch()