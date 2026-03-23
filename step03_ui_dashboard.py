import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Rendered UI Component: {path}")

def step03_deploy():
    print("====================================================")
    print("     M.A.C.DevOS: FRONTEND UI & DASHBOARD MATRIX    ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print(f"\n[*] Target System: {project_dir}")
    print("\n>>> INJECTING VISUAL ASSETS AND REACT COMPONENTS...")

    # 1. Global CSS (The OS Theme)
    globals_css = """
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-[#050505] text-green-500 font-mono antialiased overflow-x-hidden;
  }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #000; 
}
::-webkit-scrollbar-thumb {
  background: #22c55e; 
}
::-webkit-scrollbar-thumb:hover {
  background: #16a34a; 
}

/* Scanline Effect */
.scanlines::before {
  content: " ";
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  z-index: 50;
  background-size: 100% 2px, 3px 100%;
  pointer-events: none;
}
    """
    create_file(os.path.join(project_dir, "src/app/globals.css"), globals_css)

    # 2. Root Layout
    layout_tsx = """
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'School-OS | Core System',
  description: 'M.A.C.DevOS Architecture',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="scanlines min-h-screen relative selection:bg-green-500 selection:text-black">
        {children}
      </body>
    </html>
  )
}
    """
    create_file(os.path.join(project_dir, "src/app/layout.tsx"), layout_tsx)

    # 3. Landing Page (Auto Redirect)
    page_tsx = """
import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/login');
}
    """
    create_file(os.path.join(project_dir, "src/app/page.tsx"), page_tsx)

    # 4. Login Interface
    login_tsx = """
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Terminal } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Authentication Failed');

      if (data.role === 'ADMIN') router.push('/admin/dashboard');
      else if (data.role === 'TEACHER') router.push('/teacher');
      else router.push('/student');
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4 z-10 relative">
      <div className="w-full max-w-md bg-black border border-zinc-800 p-8 shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-green-500 opacity-80" />
        
        <div className="flex items-center gap-3 mb-8">
          <Terminal className="w-8 h-8 text-green-500" />
          <h1 className="text-2xl font-bold tracking-widest text-white">SYS_LOGIN</h1>
        </div>

        {error && (
          <div className="mb-4 p-3 border border-red-500 text-red-500 bg-red-500/10 text-sm uppercase">
            [ERROR]: {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Identifier</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500 transition-colors"
              placeholder="admin@system.local"
              required
            />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Passkey</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500 transition-colors"
              placeholder="••••••••"
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-green-500 hover:bg-green-400 text-black font-bold py-3 uppercase tracking-widest transition-colors disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Initialize Session'}
          </button>
        </form>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/login/page.tsx"), login_tsx)

    # 5. Face Recognition Attendance UI
    attendance_tsx = """
'use client';

import { useState } from 'react';
import { Camera, TerminalSquare, ShieldCheck } from 'lucide-react';
import { generateMockEmbedding } from '@/lib/face_service';

export default function AttendanceKiosk() {
  const [isMockMode, setIsMockMode] = useState(true);
  const [status, setStatus] = useState<'IDLE' | 'SCANNING' | 'SUCCESS' | 'FAILED'>('IDLE');

  const handleScan = async () => {
    setStatus('SCANNING');
    await new Promise(resolve => setTimeout(resolve, 1500)); 
    
    const vectorData = isMockMode ? generateMockEmbedding() : []; 

    // Simulate sending encrypted payload directly to route (Mocked for UI demo without valid DB user)
    // Real implementation uses encryptPayload() here.
    setStatus('SUCCESS');
    setTimeout(() => setStatus('IDLE'), 3000);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative z-10">
      <div className="absolute top-4 right-4 flex items-center gap-2 border border-zinc-800 p-2 bg-black">
         <span className="text-xs uppercase tracking-widest text-zinc-400">MOCK_MODE</span>
         <input 
            type="checkbox" 
            checked={isMockMode} 
            onChange={() => setIsMockMode(!isMockMode)}
            className="accent-green-500 cursor-pointer"
         />
      </div>

      <div className="max-w-md w-full border border-zinc-800 bg-black p-8 shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-green-500 to-transparent opacity-50" />
        
        <h1 className="text-2xl font-bold mb-8 flex items-center gap-3 text-white tracking-widest uppercase">
          <TerminalSquare className="w-6 h-6 text-green-500" />
          Attendance_OS
        </h1>

        <div className="aspect-video bg-zinc-900 flex items-center justify-center border border-zinc-800 mb-6 relative overflow-hidden group">
           {status === 'SCANNING' && (
             <div className="absolute inset-0 border-2 border-green-500 animate-pulse" />
           )}
           {status === 'SCANNING' && (
             <div className="absolute top-0 left-0 w-full h-1 bg-green-500/50 shadow-[0_0_15px_#22c55e] animate-[scrolldown_2s_linear_infinite]" />
           )}
           <Camera className={`w-12 h-12 transition-all duration-300 ${status === 'SCANNING' ? 'text-green-500 scale-110' : 'text-zinc-700'}`} />
        </div>

        <button 
          onClick={handleScan}
          disabled={status === 'SCANNING'}
          className="w-full bg-zinc-900 hover:bg-zinc-800 text-green-500 border border-green-500/30 hover:border-green-500 py-3 uppercase tracking-widest transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'SCANNING' ? 'Parsing Biometrics...' : 'Initialize Scanner'}
        </button>

        {status === 'SUCCESS' && (
          <div className="mt-4 p-3 bg-green-500/10 border border-green-500 text-green-400 flex items-center gap-3 text-sm uppercase">
            <ShieldCheck className="w-5 h-5" />
            <span>Identity Verified. Logged.</span>
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
    create_file(os.path.join(project_dir, "src/app/attendance/page.tsx"), attendance_tsx)

    # 6. Admin Dashboard (Basic skeleton)
    admin_tsx = """
import { Terminal, Users, Camera, Activity } from 'lucide-react';
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
        <div className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors">
          <Users className="w-8 h-8 mb-4 text-green-500" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Entity Management</h2>
          <p className="text-sm text-zinc-400 mb-4">Manage students, teachers, and system access.</p>
          <span className="text-xs text-zinc-600 uppercase">>> Access Restricted</span>
        </div>

        <Link href="/attendance" className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors group">
          <Camera className="w-8 h-8 mb-4 text-green-500 group-hover:scale-110 transition-transform" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">Launch Scanner</h2>
          <p className="text-sm text-zinc-400 mb-4">Initialize the face recognition attendance kiosk.</p>
          <span className="text-xs text-green-500 uppercase flex items-center gap-2">>> Execute <span className="animate-pulse">_</span></span>
        </Link>

        <div className="border border-zinc-800 bg-black p-6 hover:border-green-500/50 transition-colors">
          <Activity className="w-8 h-8 mb-4 text-green-500" />
          <h2 className="text-xl font-bold text-white mb-2 uppercase">System Telemetry</h2>
          <p className="text-sm text-zinc-400 mb-4">View attendance metrics and audit logs.</p>
          <span className="text-xs text-zinc-600 uppercase">>> Access Restricted</span>
        </div>
      </div>
    </div>
  );
}
    """
    create_file(os.path.join(project_dir, "src/app/admin/dashboard/page.tsx"), admin_tsx)


    print("\n====================================================")
    print(" [SUCCESS] UI DASHBOARD MATRIX FULLY DEPLOYED.")
    print("====================================================")
    print("\n🚀 BOOT SEQUENCE READY.")
    print(" To start the School-OS interface, run the following command in your terminal:")
    print(" -> npm run dev")
    print("\n Then open: http://localhost:3000 in your browser.")
    print(" Use '/attendance' to test the Face Recognition UI.")

if __name__ == "__main__":
    step03_deploy()