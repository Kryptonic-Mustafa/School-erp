import os
import zipfile
import datetime
import sys

PROJECT_NAME = "school-os"

def step23_deploy():
    print("====================================================")
    print("   M.A.C.DevOS: ADVANCED LOCAL BACKUP ENGINE        ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    # NEW: Nested Directory Structure (bkp/local/)
    bkp_dir = os.path.join(project_dir, "bkp", "local")
    os.makedirs(bkp_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_filename = os.path.join(bkp_dir, f"school-os-local-{timestamp}.zip")

    ignore_dirs = {'node_modules', '.next', 'bkp', '.git'}

    print(f"[*] Compressing project... (ignoring {', '.join(ignore_dirs)})")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                zipf.write(file_path, arcname)

    print("\n====================================================")
    print(f" [SUCCESS] LOCAL SNAPSHOT SECURED.")
    print(f" Location: {zip_filename}")
    print("====================================================\n")

if __name__ == "__main__":
    step23_deploy()