import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Mobile Layout Patched: {path}")

def step25_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: RESPONSIVE MOBILE ARCHITECTURE       ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> REWRITING ROOT ADMIN LAYOUT (RESPONSIVE SIDEBAR)...")

    layout_tsx = """
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Users, BookOpen, Camera, ScanFace, Activity, Settings, LogOut, GraduationCap, School, CalendarDays, Library, Menu, X } from 'lucide-react';
import { osToast } from '@/lib/alert_engine';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    osToast.fire({ icon: 'success', title: 'Logged out successfully' });
    router.push('/login');
  };

  const closeSidebar = () => setIsSidebarOpen(false);

  const navItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Students', href: '/admin/students', icon: GraduationCap },
    { name: 'Teachers', href: '/admin/teachers', icon: Users },
    { name: 'Classes', href: '/admin/classes', icon: BookOpen },
    { name: 'Academics', href: '/admin/academics', icon: Library },
    { name: 'Attendance Logs', href: '/admin/attendance', icon: CalendarDays },
    { name: 'User Management', href: '/admin/users', icon: Users },
    { name: 'Roles & Access', href: '/admin/roles', icon: Settings },
    { name: 'Live Scanner', href: '/attendance', icon: Camera },
    { name: 'Biometrics', href: '/admin/face-register', icon: ScanFace },
    { name: 'Telemetry', href: '/admin/telemetry', icon: Activity },
  ];

  return (
    <div className="min-h-screen flex bg-slate-50 font-sans overflow-x-hidden">
      
      {/* MOBILE OVERLAY */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/50 z-40 lg:hidden transition-opacity"
          onClick={closeSidebar}
        />
      )}

      {/* LEFT SIDEBAR (Responsive Off-Canvas) */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 flex flex-col h-full transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-auto ${isSidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}`}>
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-200 shrink-0">
          <div className="flex items-center">
            <School className="w-6 h-6 text-blue-600 mr-3 shrink-0" />
            <span className="font-bold text-lg text-slate-800 tracking-tight">EduAdmin</span>
          </div>
          <button onClick={closeSidebar} className="lg:hidden p-2 text-slate-500 hover:bg-slate-100 rounded-md">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link 
                key={item.name} 
                href={item.href} 
                onClick={closeSidebar} // Auto-close on mobile when link clicked
                className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}
              >
                <Icon className={`w-5 h-5 mr-3 shrink-0 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                {item.name}
              </Link>
            )
          })}
        </nav>
        
        <div className="p-4 border-t border-slate-200 shrink-0">
          <button onClick={handleLogout} className="flex items-center w-full px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
            <LogOut className="w-5 h-5 mr-3 shrink-0 text-red-500" /> Sign Out
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT WRAPPER */}
      <div className="flex-1 flex flex-col min-h-screen min-w-0 w-full lg:w-[calc(100%-16rem)]">
        
        {/* TOP HEADER */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-8 sticky top-0 z-30 shrink-0">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsSidebarOpen(true)} className="lg:hidden p-2 -ml-2 text-slate-600 hover:bg-slate-100 rounded-md">
              <Menu className="w-6 h-6" />
            </button>
            <h1 className="text-lg sm:text-xl font-semibold text-slate-800 capitalize truncate">
              {pathname.split('/').pop()?.replace('-', ' ') || 'Dashboard'}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm shrink-0">A</div>
            <div className="hidden sm:block text-sm">
              <p className="font-medium text-slate-700 leading-none">Admin User</p>
              <p className="text-xs text-slate-500 mt-1">admin@school.os</p>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/layout.tsx"), layout_tsx)

    print("\n====================================================")
    print(" [SUCCESS] SYSTEM IS NOW MOBILE RESPONSIVE.         ")
    print("====================================================\n")

if __name__ == "__main__":
    step25_deploy()