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
