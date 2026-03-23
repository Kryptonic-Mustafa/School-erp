import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Deployed: {path}")

def step30_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: UNIVERSAL SYSTEM LOADER INTEGRATION  ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. CREATING BRANDED LOADER COMPONENT...")

    # The core UI component for the loader
    system_loader_tsx = """
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
"""
    create_file(os.path.join(project_dir, "src/components/SystemLoader.tsx"), system_loader_tsx)

    print("\n>>> 2. INJECTING NEXT.JS ROUTE TRANSITION LOADER...")

    # Automatically catches all page navigations within /admin/
    admin_loading_tsx = """
import SystemLoader from '@/components/SystemLoader';

export default function Loading() {
  return <SystemLoader fullScreen={false} text="Routing Data..." />;
}
"""
    create_file(os.path.join(project_dir, "src/app/admin/loading.tsx"), admin_loading_tsx)

    print("\n>>> 3. UPGRADING ALERT ENGINE WITH osLoader KERNEL...")

    alert_engine_path = os.path.join(project_dir, "src/lib/alert_engine.ts")
    with open(alert_engine_path, "r", encoding="utf-8") as f:
        alert_engine_code = f.read()

    # Append the osLoader object to the SweetAlert engine
    if "osLoader" not in alert_engine_code:
        osloader_code = """
export const osLoader = {
  show: (text = 'Processing...') => {
    MySwal.fire({
      html: `
        <div class="flex flex-col items-center justify-center py-4">
          <div class="relative flex items-center justify-center w-16 h-16 mb-4">
            <div class="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
          </div>
          <p class="text-slate-600 font-bold text-sm uppercase tracking-wider animate-pulse">${text}</p>
        </div>
      `,
      showConfirmButton: false,
      allowOutsideClick: false,
      background: '#ffffff',
      customClass: { popup: 'rounded-2xl shadow-2xl border border-slate-100 w-[90%] sm:max-w-[300px] !p-2' }
    });
  },
  hide: () => {
    MySwal.close();
  }
};
"""
        with open(alert_engine_path, "a", encoding="utf-8") as f:
            f.write(osloader_code)

    print("\n>>> 4. PATCHING MATRICES TO UTILIZE NEW LOADER...")

    def patch_page(filepath):
        if not os.path.exists(filepath): return
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        # 1. Update Imports
        if "osLoader" not in code:
            code = code.replace("import { osToast, osAlert }", "import { osToast, osAlert, osLoader }")
            code = code.replace("import { osAlert, osToast }", "import { osAlert, osToast, osLoader }")
            code = code.replace("from '@/lib/alert_engine';", "from '@/lib/alert_engine';\nimport SystemLoader from '@/components/SystemLoader';")

        # 2. Inject Page Loader
        if "if (loading) return <SystemLoader />;" not in code:
            code = code.replace('return (\n    <div className="grid', 'if (loading) return <SystemLoader text="Loading Records..." />;\n\n  return (\n    <div className="grid')

        # 3. Inject CRUD Create/Edit Loader (try block)
        code = code.replace("setIsSubmitting(true);\n    try {", "setIsSubmitting(true);\n    osLoader.show('Saving Record...');\n    try {")
        
        # 4. Inject CRUD Hide Loader (finally block)
        if "finally { setIsSubmitting(false); }" in code:
            code = code.replace("finally { setIsSubmitting(false); }", "finally { setIsSubmitting(false); osLoader.hide(); }")
            
        # 5. Inject Delete Loader
        code = code.replace("const res = await fetch(`/api/", "osLoader.show('Deleting...');\n    const res = await fetch(`/api/")
        code = code.replace("fetchData(); } else {", "fetchData(); osLoader.hide(); } else { osLoader.hide(); ")
        code = code.replace("fetchData(); } catch", "fetchData(); osLoader.hide(); } catch") # fallback

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"  [+] Patched: {os.path.basename(filepath)}")

    patch_page(os.path.join(project_dir, "src/app/admin/students/page.tsx"))
    patch_page(os.path.join(project_dir, "src/app/admin/teachers/page.tsx"))
    patch_page(os.path.join(project_dir, "src/app/admin/classes/page.tsx"))

    print("\n====================================================")
    print(" [SUCCESS] UNIVERSAL SYSTEM LOADER ONLINE.          ")
    print("====================================================\n")

if __name__ == "__main__":
    step30_deploy()