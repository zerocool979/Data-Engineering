document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.getElementById('progressBar');
    const statusValue = document.getElementById('statusValue');
    const progressValue = document.getElementById('progressValue');
    const currentAction = document.getElementById('currentAction');
    
    let progress = 0;
    const steps = [
        { progress: 20, message: 'Memvalidasi URL...', status: 'Validasi' },
        { progress: 40, message: 'Menyambung ke server...', status: 'Koneksi' },
        { progress: 60, message: 'Mendownload konten...', status: 'Download' },
        { progress: 80, message: 'Memproses data...', status: 'Processing' },
        { progress: 95, message: 'Menyiapkan hasil...', status: 'Finalisasi' }
    ];
    
    let stepIndex = 0;
    
    // Simulasi progress
    const interval = setInterval(() => {
        if (stepIndex < steps.length) {
            const step = steps[stepIndex];
            progress = step.progress;
            
            // Update UI
            progressBar.style.width = progress + '%';
            progressValue.textContent = progress + '%';
            statusValue.textContent = step.status;
            currentAction.textContent = step.message;
            
            stepIndex++;
        } else {
            // Selesai, redirect ke hasil
            clearInterval(interval);
            
            // Tampilkan pesan selesai
            statusValue.textContent = 'Selesai';
            currentAction.textContent = 'Mengarahkan ke halaman hasil...';
            
            // Redirect setelah 1 detik
            setTimeout(() => {
                window.location.href = '/scrape/result?url=' + encodeURIComponent(targetUrl);
            }, 1000);
        }
    }, 800); // Update setiap 800ms
    
    // Fallback jika ada error
    setTimeout(() => {
        if (progress < 100) {
            // Jika terlalu lama, tetap redirect
            window.location.href = '/scrape/result?url=' + encodeURIComponent(targetUrl);
        }
    }, 10000); // Timeout 10 detik
});

// Fungsi untuk animasi tambahan
function animateLoading() {
    const spinner = document.querySelector('.spinner');
    if (spinner) {
        spinner.style.animation = 'none';
        spinner.offsetHeight; // Trigger reflow
        spinner.style.animation = null;
    }
}
