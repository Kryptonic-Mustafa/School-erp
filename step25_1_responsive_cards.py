import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Patched UI: {path}")

def step25_deploy():
    print("====================================================")
    print("  M.A.C.DevOS: HYBRID MOBILE CARD RESPONSIVENESS    ")
    print("====================================================")

    project_dir = os.getcwd() if os.path.basename(os.getcwd()) == PROJECT_NAME else os.path.join(os.getcwd(), PROJECT_NAME)

    print("\n>>> REWRITING STUDENTS UI (INJECTING MOBILE CARDS)...")

    students_path = os.path.join(project_dir, "src/app/admin/students/page.tsx")
    with open(students_path, "r", encoding="utf-8") as f:
        student_code = f.read()

    # Replace the single table wrapper with a dual Desktop/Mobile layout
    old_table_section = """<div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-sm whitespace-nowrap">"""
    
    new_table_section = """<div className="flex-1 p-0 sm:p-2">
          
          {/* DESKTOP TABLE (Hidden on Mobile) */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">"""
            
    student_code = student_code.replace(old_table_section, new_table_section)

    old_tbody_end = """</tbody>
          </table>
        </div>"""
        
    new_tbody_end = """</tbody>
            </table>
          </div>

          {/* MOBILE CARDS (Hidden on Desktop) */}
          <div className="md:hidden flex flex-col gap-4 p-4">
            {students.map((student) => (
              <div key={student.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col gap-3 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-slate-800 text-base">{student.name}</h3>
                    <p className="text-xs text-slate-500">{student.user.email}</p>
                  </div>
                  <span className="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full text-xs font-semibold">{student.class.name}</span>
                </div>
                
                <div className="flex justify-between items-center mt-2 pt-3 border-t border-slate-100">
                  <span className="text-xs text-slate-400 font-mono">ID: {student.id.split('-')[0].toUpperCase()}</span>
                  <div className="flex gap-2">
                    <button onClick={() => handleEdit(student)} className="p-2 bg-slate-50 text-slate-500 hover:text-blue-600 rounded-lg border border-slate-200 shadow-sm transition-colors">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(student.id, student.name)} className="p-2 bg-slate-50 text-slate-500 hover:text-red-600 rounded-lg border border-slate-200 shadow-sm transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
            {!loading && students.length === 0 && <div className="text-center py-8 text-slate-500 text-sm">No student records found.</div>}
          </div>
        </div>"""

    student_code = student_code.replace(old_tbody_end, new_tbody_end)
    create_file(students_path, student_code)

    print("\n>>> REWRITING TEACHERS UI (INJECTING MOBILE CARDS)...")
    
    teachers_path = os.path.join(project_dir, "src/app/admin/teachers/page.tsx")
    with open(teachers_path, "r", encoding="utf-8") as f:
        teacher_code = f.read()

    teacher_code = teacher_code.replace(old_table_section, new_table_section)
    
    new_teacher_tbody_end = """</tbody>
            </table>
          </div>

          {/* MOBILE CARDS */}
          <div className="md:hidden flex flex-col gap-4 p-4">
            {teachers.map((teacher) => (
              <div key={teacher.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col gap-3 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-violet-500"></div>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-slate-800 text-base">{teacher.name}</h3>
                    <p className="text-xs text-slate-500">{teacher.user.email}</p>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1 mt-1">
                  {teacher.classes.length > 0 ? teacher.classes.map((c: any) => (
                    <span key={c.name} className="bg-violet-50 text-violet-700 px-2 py-0.5 rounded text-[10px] font-semibold">{c.name}</span>
                  )) : <span className="text-xs text-slate-400 italic">No classes</span>}
                </div>

                <div className="flex justify-end items-center mt-1 pt-3 border-t border-slate-100">
                  <div className="flex gap-2">
                    <button onClick={() => handleEdit(teacher)} className="p-2 bg-slate-50 text-slate-500 hover:text-blue-600 rounded-lg border border-slate-200 shadow-sm transition-colors">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(teacher.id, teacher.name)} className="p-2 bg-slate-50 text-slate-500 hover:text-red-600 rounded-lg border border-slate-200 shadow-sm transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
            {!loading && teachers.length === 0 && <div className="text-center py-8 text-slate-500 text-sm">No faculty records found.</div>}
          </div>
        </div>"""
        
    teacher_code = teacher_code.replace(old_tbody_end, new_teacher_tbody_end)
    create_file(teachers_path, teacher_code)

    print("\n====================================================")
    print(" [SUCCESS] RESPONSIVE CARD UI PERFECTLY INTEGRATED. ")
    print("====================================================\n")

if __name__ == "__main__":
    step25_deploy()