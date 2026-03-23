import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] UI Patched: {path}")

def step27_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: COMPACT MOBILE MODALS                ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)
    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print("\n>>> 1. RECONFIGURING ALERT ENGINE (COMPACT THEME)...")

    alert_engine_ts = """
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';

const MySwal = withReactContent(Swal);

const enterpriseTheme = {
  buttonsStyling: false, // Disables default huge SweetAlert buttons
  customClass: {
    popup: 'rounded-2xl shadow-2xl font-sans border border-slate-100 w-[90%] sm:max-w-[380px] !p-5',
    icon: '!scale-75 !m-0 !mx-auto !mb-2', // Shrinks the huge icon by 25% and removes margins
    title: 'text-slate-800 font-bold text-lg !p-0 !m-0 !mb-2',
    htmlContainer: 'text-sm text-slate-600 text-left !m-0 !p-0',
    actions: '!mt-5 !w-full flex gap-3', // Places buttons side-by-side cleanly
    confirmButton: 'rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 px-4 py-2.5 text-sm w-full transition-colors',
    cancelButton: 'rounded-lg bg-white text-slate-700 font-medium hover:bg-slate-50 border border-slate-200 px-4 py-2.5 text-sm w-full transition-colors',
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
      const swalName = document.getElementById('swal-name') as HTMLInputElement;
      const swalClass = document.getElementById('swal-class') as HTMLInputElement;
      const swalStatus = document.getElementById('swal-status') as HTMLSelectElement;
      
      if (swalName && swalClass) return { name: swalName.value, className: swalClass.value };
      if (swalName && !swalClass) return { name: swalName.value };
      if (swalStatus) return { status: swalStatus.value };
      return true;
    }
  })
};
"""
    create_file(os.path.join(project_dir, "src/lib/alert_engine.ts"), alert_engine_ts)

    print("\n>>> 2. TIGHTENING HTML INPUTS IN FORMS...")

    # Tighten Students Modal
    student_path = os.path.join(project_dir, "src/app/admin/students/page.tsx")
    if os.path.exists(student_path):
        with open(student_path, "r", encoding="utf-8") as f:
            student_code = f.read()
        
        # Replace old clunky HTML with clean Tailwind HTML
        old_html = """<div class="text-left space-y-3 mt-4">
        <label class="block text-sm">Name</label><input id="swal-name" class="w-full border rounded p-2 text-sm" value="${student.name}">
        <label class="block text-sm mt-3">Class</label><input id="swal-class" class="w-full border rounded p-2 text-sm" value="${student.class.name}">
      </div>"""
        new_html = """<div class="text-left space-y-3 mt-2">
        <div><label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Student Name</label><input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${student.name}"></div>
        <div><label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Class</label><input id="swal-class" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${student.class.name}"></div>
      </div>"""
        student_code = student_code.replace(old_html, new_html)
        create_file(student_path, student_code)

    # Tighten Teachers Modal
    teacher_path = os.path.join(project_dir, "src/app/admin/teachers/page.tsx")
    if os.path.exists(teacher_path):
        with open(teacher_path, "r", encoding="utf-8") as f:
            teacher_code = f.read()
        
        old_html_t = """<div class="text-left space-y-3 mt-4">
        <label class="block text-sm">Full Name</label>
        <input id="swal-name" class="w-full border rounded p-2 text-sm" value="${teacher.name}">
      </div>"""
        new_html_t = """<div class="text-left mt-2">
        <label class="block text-xs font-semibold text-slate-500 mb-1 uppercase">Faculty Name</label>
        <input id="swal-name" class="w-full border border-slate-300 rounded-lg p-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" value="${teacher.name}">
      </div>"""
        teacher_code = teacher_code.replace(old_html_t, new_html_t)
        create_file(teacher_path, teacher_code)

    print("\n====================================================")
    print(" [SUCCESS] COMPACT MODALS DEPLOYED.                 ")
    print("====================================================\n")

if __name__ == "__main__":
    step27_deploy()