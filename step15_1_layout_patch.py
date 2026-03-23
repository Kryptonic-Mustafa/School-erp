import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Cleanly Patched: {path}")

def apply_patch():
    print("====================================================")
    print("   M.A.C.DevOS PATCH: SIDEBAR ICON RESOLUTION       ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    layout_tsx = """
'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Users, BookOpen, Camera, ScanFace, Activity, Settings, LogOut, GraduationCap, School, CalendarDays } from 'lucide-react';
import { osToast } from '@/lib/alert_engine';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    osToast.fire({ icon: 'success', title: 'Logged out successfully' });
    router.push('/login');
  };

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

  return (
    <div className="min-h-screen flex bg-slate-50 font-sans">
      {/* LEFT SIDEBAR */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col fixed h-full z-20">
        <div className="h-16 flex items-center px-6 border-b border-slate-200">
          <School className="w-6 h-6 text-blue-600 mr-3" />
          <span className="font-bold text-lg text-slate-800 tracking-tight">EduAdmin</span>
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link key={item.name} href={item.href} className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}>
                <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                {item.name}
              </Link>
            )
          })}
        </nav>
        <div className="p-4 border-t border-slate-200">
          <button onClick={handleLogout} className="flex items-center w-full px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
            <LogOut className="w-5 h-5 mr-3 text-red-500" /> Sign Out
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT WRAPPER */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        {/* TOP HEADER */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
          <h1 className="text-xl font-semibold text-slate-800 capitalize">
            {pathname.split('/').pop()?.replace('-', ' ') || 'Dashboard'}
          </h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">A</div>
              <div className="text-sm">
                <p className="font-medium text-slate-700 leading-none">Admin User</p>
                <p className="text-xs text-slate-500 mt-1">admin@school.os</p>
              </div>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/layout.tsx"), layout_tsx)

    print("\n====================================================")
    print(" [SUCCESS] SIDEBAR LAYOUT RESTORED.                 ")
    print("====================================================\n")

if __name__ == "__main__":
    apply_patch()