document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scrapeForm');
    
    // Load recent scrapes dari localStorage
    loadRecentScrapes();
    
    // Form validation
    form.addEventListener('submit', function(e) {
        const urlInput = document.getElementById('url');
        const url = urlInput.value.trim();
        
        if (!isValidUrl(url)) {
            e.preventDefault();
            showError('Masukkan URL yang valid (contoh: https://www.example.com)');
            urlInput.focus();
        }
    });
    
    // Auto-suggest untuk URL
    const urlInput = document.getElementById('url');
    urlInput.addEventListener('blur', function() {
        let url = this.value.trim();
        if (url && !url.match(/^https?:\/\//)) {
            this.value = 'https://' + url;
        }
    });
});

function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function showError(message) {
    // Hapus error message yang sudah ada
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Buat error message baru
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        background: #fee;
        color: #c00;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
        border: 1px solid #fcc;
    `;
    errorDiv.textContent = message;
    
    // Insert setelah form
    const form = document.getElementById('scrapeForm');
    form.parentNode.insertBefore(errorDiv, form.nextSibling);
    
    // Auto-hide setelah 5 detik
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function loadRecentScrapes() {
    const recentList = document.querySelector('.recent-list');
    if (!recentList) return;
    
    // Ambil dari localStorage
    const scrapes = JSON.parse(localStorage.getItem('recentScrapes') || '[]');
    
    if (scrapes.length === 0) {
        recentList.innerHTML = '<p class="no-data">Belum ada data scraping</p>';
        return;
    }
    
    // Tampilkan 5 terbaru
    const html = scrapes.slice(0, 5).map(scrape => `
        <div class="recent-item" style="
            padding: 1rem;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span style="color: #667eea;">${scrape.url}</span>
            <span style="color: #888; font-size: 0.9rem;">${scrape.date}</span>
        </div>
    `).join('');
    
    recentList.innerHTML = html;
}

// Simpan hasil scraping ke localStorage (dipanggil dari halaman result)
function saveToRecent(url) {
    const scrapes = JSON.parse(localStorage.getItem('recentScrapes') || '[]');
    
    // Cek apakah URL sudah ada
    const exists = scrapes.some(s => s.url === url);
    if (!exists) {
        scrapes.unshift({
            url: url,
            date: new Date().toLocaleDateString('id-ID')
        });
        
        // Batasi hanya 10 item
        if (scrapes.length > 10) {
            scrapes.pop();
        }
        
        localStorage.setItem('recentScrapes', JSON.stringify(scrapes));
    }
}
