import os
import subprocess
import sys

PROJECT_NAME = "school-os"

def run_command(command, cwd=None):
    print(f"[*] Executing: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"[!] Error executing: {command}")
        sys.exit(1)

def apply_patch():
    print("====================================================")
    print("   M.A.C.DevOS PATCH: PRISMA ENGINE ROLLBACK        ")
    print("====================================================")
    
    # Context-Aware Directory Detection
    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)
    
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print(f"\n[*] Target Directory: {project_dir}")
    print("\n>>> PURGING UNSTABLE PRISMA V7 CORE...")
    run_command("npm uninstall prisma @prisma/client", cwd=project_dir)
    
    print("\n>>> INSTALLING STABLE PRISMA V5 LTS...")
    run_command("npm install @prisma/client@5.22.0", cwd=project_dir)
    run_command("npm install -D prisma@5.22.0", cwd=project_dir)

    print("\n====================================================")
    print(" [SUCCESS] SYSTEM STABILITY RESTORED.")
    print(" Please run:")
    print(" -> npx prisma db push")
    print("====================================================\n")

if __name__ == "__main__":
    apply_patch()