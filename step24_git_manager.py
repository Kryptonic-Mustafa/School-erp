import os
import sys
import subprocess
import datetime

PROJECT_NAME = "school-os"
REPO_URL = "https://github.com/Kryptonic-Mustafa/School-erp.git"

def run_cmd(cmd, cwd, hide_output=False):
    if not hide_output:
        print(f"[*] Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0 and not hide_output:
        print(f"[!] Warning/Error executing: {cmd}\n{result.stderr}")
        return False, result.stderr
    return True, result.stdout

def main():
    print("====================================================")
    print("   M.A.C.DevOS: CLOUD SYNC & GITHUB MANAGER         ")
    print("====================================================")
    
    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    
    server_bkp_dir = os.path.join(project_dir, "bkp", "from_server")
    os.makedirs(server_bkp_dir, exist_ok=True)
    with open(os.path.join(server_bkp_dir, "README.txt"), "w") as f:
        f.write("Place automated live-server zip backups in this folder.")

    # 1. Check Git Initialization
    if not os.path.exists(os.path.join(project_dir, ".git")):
        print("\n[*] Initializing Git Repository...")
        run_cmd("git init", cwd=project_dir)
        with open(os.path.join(project_dir, ".gitignore"), "a") as f:
            f.write("\n/bkp\nnode_modules\n.next\n.env\n")

    # 2. Force Remote Connection Check
    success, remotes = run_cmd("git remote -v", cwd=project_dir, hide_output=True)
    if "origin" not in remotes:
        print(f"\n[*] Linking to GitHub Repository: {REPO_URL}...")
        run_cmd(f"git remote add origin {REPO_URL}", cwd=project_dir)
    else:
        # Update URL just in case it's wrong
        run_cmd(f"git remote set-url origin {REPO_URL}", cwd=project_dir, hide_output=True)

    print("\nSelect Sync Operation:")
    print("1. [PUSH] Commit all changes and push to GitHub")
    print("2. [PULL] Fetch latest changes from GitHub")
    print("3. [EXIT] Cancel")
    
    choice = input("\nEnter choice (1-3): ")

    if choice == '1':
        msg = input("Enter commit message (or press enter for default): ")
        if not msg:
            msg = f"Automated System Backup - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        run_cmd("git add .", cwd=project_dir)
        run_cmd(f'git commit -m "{msg}"', cwd=project_dir)
        
        # Force branch to main
        run_cmd("git branch -M main", cwd=project_dir)
        
        print("\n[*] Pushing to GitHub (You may be prompted for credentials)...")
        success, _ = run_cmd("git push -u origin main", cwd=project_dir)
        
        if success:
            print("\n[SUCCESS] Code pushed to GitHub!")
        else:
            print("\n[FAILED] Could not push to GitHub. Check the errors above.")

    elif choice == '2':
        print("\n[*] Pulling from GitHub...")
        run_cmd("git branch -M main", cwd=project_dir)
        success, _ = run_cmd("git pull origin main", cwd=project_dir)
        if success:
            print("\n[SUCCESS] Code synced from GitHub!")

if __name__ == "__main__":
    main()