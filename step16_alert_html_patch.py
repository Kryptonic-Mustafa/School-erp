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
    print("   M.A.C.DevOS PATCH: SWEETALERT HTML RENDERING     ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> RECONFIGURING ALERT ENGINE KERNEL...")

    # 1. UPGRADE ALERT ENGINE TO PARSE RAW HTML
    alert_engine_ts = """
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';

const MySwal = withReactContent(Swal);

const enterpriseTheme = {
  customClass: {
    popup: 'rounded-xl shadow-xl font-sans border border-slate-100',
    confirmButton: 'rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 px-6 py-2.5',
    cancelButton: 'rounded-lg bg-white text-slate-700 font-medium hover:bg-slate-50 border border-slate-200 px-6 py-2.5',
    title: 'text-slate-800 font-semibold text-xl',
    htmlContainer: 'text-sm text-slate-500 text-left'
  }
};

export const osToast = MySwal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  customClass: { popup: 'rounded-lg font-sans text-sm shadow-lg border border-slate-100 z-50' }
});

export const osAlert = {
  // Switched from 'text:' to 'html:' globally
  success: (title: string, content: string) => MySwal.fire({ icon: 'success', title, html: content, ...enterpriseTheme }),
  error: (title: string, content: string) => MySwal.fire({ icon: 'error', title, html: content, ...enterpriseTheme }),
  confirm: (title: string, content: string) => MySwal.fire({ 
    icon: 'question', 
    title, 
    html: content, 
    showCancelButton: true, 
    confirmButtonText: 'Confirm', 
    cancelButtonText: 'Cancel', 
    ...enterpriseTheme,
    preConfirm: () => {
      // Safely extract values from DOM before the modal is destroyed
      const swalName = document.getElementById('swal-name') as HTMLInputElement;
      const swalClass = document.getElementById('swal-class') as HTMLInputElement;
      const swalStatus = document.getElementById('swal-status') as HTMLSelectElement;
      
      if (swalName && swalClass) return { name: swalName.value, className: swalClass.value };
      if (swalStatus) return { status: swalStatus.value };
      return true;
    }
  })
};
"""
    create_file(os.path.join(project_dir, "src/lib/alert_engine.ts"), alert_engine_ts)

    print("\n>>> SECURING CRUD COMPONENTS FOR HTML EXTRACTION...")

    # 2. PATCH STUDENTS UI DOM EXTRACTION
    student_path = os.path.join(project_dir, "src/app/admin/students/page.tsx")
    if os.path.exists(student_path):
        with open(student_path, "r", encoding="utf-8") as f:
            student_code = f.read()
        
        student_code = student_code.replace(
            "const name = (document.getElementById('swal-name') as HTMLInputElement).value;",
            "const name = formValues?.name || (document.getElementById('swal-name') as HTMLInputElement)?.value;"
        )
        student_code = student_code.replace(
            "const className = (document.getElementById('swal-class') as HTMLInputElement).value;",
            "const className = formValues?.className || (document.getElementById('swal-class') as HTMLInputElement)?.value;"
        )
        create_file(student_path, student_code)

    # 3. PATCH ATTENDANCE UI DOM EXTRACTION
    attendance_path = os.path.join(project_dir, "src/app/admin/attendance/page.tsx")
    if os.path.exists(attendance_path):
        with open(attendance_path, "r", encoding="utf-8") as f:
            att_code = f.read()
            
        att_code = att_code.replace(
            "const status = (document.getElementById('swal-status') as HTMLSelectElement).value;",
            "const status = newStatus?.status || (document.getElementById('swal-status') as HTMLSelectElement)?.value;"
        )
        create_file(attendance_path, att_code)

    print("\n====================================================")
    print(" [SUCCESS] SWEETALERT HTML RENDERING ACTIVE.        ")
    print("====================================================\n")

if __name__ == "__main__":
    apply_patch()