import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Patched: {path}")

def apply_patch():
    print("====================================================")
    print("   M.A.C.DevOS PATCH: TAILWIND V4 ENGINE UPGRADE    ")
    print("====================================================")
    
    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)
    
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print(f"\n[*] Target Directory: {project_dir}")
    print("\n>>> REWRITING STYLESHEETS FOR V4 COMPLIANCE...")

    # 1. Update globals.css to use Tailwind v4 import and remove @apply
    globals_css = """
@import "tailwindcss";

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

    # 2. Move body styles directly into layout.tsx
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
      <body className="bg-[#050505] text-green-500 font-mono antialiased overflow-x-hidden scanlines min-h-screen relative selection:bg-green-500 selection:text-black">
        {children}
      </body>
    </html>
  )
}
    """
    create_file(os.path.join(project_dir, "src/app/layout.tsx"), layout_tsx)

    print("\n====================================================")
    print(" [SUCCESS] CSS ENGINE UPGRADED TO TAILWIND V4.")
    print(" Please restart your Next.js server.")
    print("====================================================\n")

if __name__ == "__main__":
    apply_patch()