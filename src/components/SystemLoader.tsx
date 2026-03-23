import { School } from 'lucide-react';

export default function SystemLoader({ text = "Syncing Core Matrix...", fullScreen = false }: { text?: string, fullScreen?: boolean }) {
  const containerClass = fullScreen
    ? "fixed inset-0 z-[100] flex flex-col items-center justify-center bg-slate-50/80 backdrop-blur-sm"
    : "w-full h-full min-h-[400px] flex flex-col items-center justify-center";

  return (
    <div className={containerClass}>
      <div className="relative flex items-center justify-center w-24 h-24 mb-6">
        {/* Outer spinning ring */}
        <div className="absolute inset-0 border-4 border-blue-100 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
        
        {/* Inner pulsing logo */}
        <div className="bg-white rounded-full p-3 shadow-sm">
          <School className="w-8 h-8 text-blue-600 animate-pulse" />
        </div>
      </div>
      <p className="text-sm font-semibold text-slate-500 uppercase tracking-widest animate-pulse">
        {text}
      </p>
    </div>
  );
}
