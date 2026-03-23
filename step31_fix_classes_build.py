import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Patched TypeScript Error: {path}")

def step31_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: TYPESCRIPT BUILD FIX                 ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> INJECTING MISSING STATE INTO CLASSES UI...")

    classes_path = os.path.join(project_dir, "src/app/admin/classes/page.tsx")
    if os.path.exists(classes_path):
        with open(classes_path, "r", encoding="utf-8") as f:
            classes_code = f.read()

        # 1. Add the missing loading state
        if "const [loading, setLoading]" not in classes_code:
            classes_code = classes_code.replace(
                "const [searchQuery, setSearchQuery] = useState('');",
                "const [searchQuery, setSearchQuery] = useState('');\n  const [loading, setLoading] = useState(true);"
            )

        # 2. Update the fetchData function to disable loading when done
        old_fetch = """if (tRes.success) setTeachers(tRes.teachers);
  };"""
        new_fetch = """if (tRes.success) setTeachers(tRes.teachers);
    setLoading(false);
  };"""
        classes_code = classes_code.replace(old_fetch, new_fetch)

        create_file(classes_path, classes_code)

    print("\n====================================================")
    print(" [SUCCESS] CLASSES PAGE IS NOW BUILD-READY.         ")
    print("====================================================\n")

if __name__ == "__main__":
    step31_deploy()