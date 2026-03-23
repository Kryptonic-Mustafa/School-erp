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

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Created Script: {path}")

def step04_seed():
    print("====================================================")
    print("    M.A.C.DevOS: ROOT ADMIN INJECTION SEQUENCE      ")
    print("====================================================")
    
    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)
    
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print(f"\n[*] Target Directory: {project_dir}")
    print("\n>>> COMPILING SEED INJECTION SCRIPT...")

    # Create the raw Node.js script to bypass TypeScript module resolution issues
    seed_js = """
const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function main() {
  console.log('>>> Connecting to TiDB Cloud Matrix...');
  
  const hashedPassword = await bcrypt.hash('admin123', 10);
  
  const admin = await prisma.user.upsert({
    where: { email: 'admin@school.os' },
    update: {},
    create: {
      email: 'admin@school.os',
      password: hashedPassword,
      role: 'ADMIN',
    },
  });

  console.log('====================================================');
  console.log(' [SUCCESS] ROOT ADMIN INJECTED.');
  console.log(' -> EMAIL:    admin@school.os');
  console.log(' -> PASSWORD: admin123');
  console.log('====================================================');
}

main()
  .catch(e => {
    console.error('[!] Database Injection Failed:');
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
    """
    seed_path = os.path.join(project_dir, "seed_admin.js")
    create_file(seed_path, seed_js)

    print("\n>>> EXECUTING DATABASE INJECTION...")
    run_command("node seed_admin.js", cwd=project_dir)

    # Clean up the seed script after it runs so it doesn't clutter the portfolio
    os.remove(seed_path)
    print("\n[*] Trace erased. Seed script removed from filesystem.")

if __name__ == "__main__":
    step04_seed()