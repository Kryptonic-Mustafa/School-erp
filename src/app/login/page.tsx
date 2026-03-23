'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Terminal } from 'lucide-react';
import { osToast, osAlert } from '@/lib/alert_engine';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Authentication Failed');

      osToast.fire({ icon: 'success', title: 'Session Authenticated' });

      if (data.role === 'ADMIN') router.push('/admin/dashboard');
      else if (data.role === 'TEACHER') router.push('/teacher');
      else router.push('/student');
      
    } catch (err: any) {
      osAlert.error('Access Denied', err.message);
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
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Identifier</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500 transition-colors" placeholder="admin@system.local" required />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-widest text-zinc-500 mb-2">Passkey</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-zinc-900 border border-zinc-700 p-3 text-green-500 focus:outline-none focus:border-green-500 transition-colors" placeholder="••••••••" required />
          </div>
          <button type="submit" disabled={loading} className="w-full bg-green-500 hover:bg-green-400 text-black font-bold py-3 uppercase tracking-widest transition-colors disabled:opacity-50">
            {loading ? 'Authenticating...' : 'Initialize Session'}
          </button>
        </form>
      </div>
    </div>
  );
}
