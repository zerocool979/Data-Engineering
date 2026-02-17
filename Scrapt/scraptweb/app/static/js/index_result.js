document.addEventListener('DOMContentLoaded', function() {
    // Simpan ke recent scrapes
    const urlElement = document.querySelector('.url-link');
    if (urlElement) {
        saveToRecent(urlElement.textContent);
    }
    
    // Syntax highlighting untuk JSON
    highlightJSON();
    
    // Copy JSON button
    addCopyButton();
    
    // Image error handling
    handleImageErrors();
});

function highlightJSON() {
    const jsonDisplay = document.querySelector('.json-display');
    if (!jsonDisplay) return;
    
    // Syntax highlighting sederhana
    let json = jsonDisplay.textContent;
    json = json.replace(/"([^"]+)":/g, '<span style="color: #f687b3;">"$1"</span>:');
    json = json.replace(/: "([^"]+)"/g, ': <span style="color: #9ae6b4;">"$1"</span>');
    json = json.replace(/: (\d+)/g, ': <span style="color: #fbbf24;">$1</span>');
    json = json.replace(/: (true|false)/g, ': <span style="color: #f687b3;">$1</span>');
    
    jsonDisplay.innerHTML = json;
}

function addCopyButton() {
    const jsonSection = document.querySelector('.json-section');
    if (!jsonSection) return;
    
    const button = document.createElement('button');
    button.textContent = '📋 Copy JSON';
    button.style.cssText = `
        position: absolute;
        top: 1rem;
        right: 1rem;
        padding: 0.5rem 1rem;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: background 0.3s;
    `;
    
    button.addEventListener('mouseenter', () => {
        button.style.background = '#764ba2';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.background = '#667eea';
    });
    
    button.addEventListener('click', () => {
        const jsonText = document.querySelector('.json-display').textContent;
        navigator.clipboard.writeText(jsonText).then(() => {
            const originalText = button.textContent;
            button.textContent = '✅ Copied!';
            setTimeout(() => {
                button.textContent = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Gagal menyalin ke clipboard');
        });
    });
    
    // Set position relative untuk section
    jsonSection.style.position = 'relative';
    jsonSection.appendChild(button);
}

function handleImageErrors() {
    const images = document.querySelectorAll('.image-item img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            // Ganti dengan placeholder jika gambar gagal load
            this.src = 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100\' height=\'100\' viewBox=\'0 0 100 100\'%3E%3Crect width=\'100\' height=\'100\' fill=\'%23f0f0f0\'/%3E%3Ctext x=\'50\' y=\'50\' font-size=\'14\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3EGambar%3C/text%3E%3C/svg%3E';
            this.alt = 'Gambar tidak dapat dimuat';
        });
    });
}

function toggleFullJSON() {
    const jsonDisplay = document.querySelector('.json-display');
    if (!jsonDisplay) return;
    
    if (jsonDisplay.style.maxHeight) {
        jsonDisplay.style.maxHeight = null;
    } else {
        jsonDisplay.style.maxHeight = '500px';
        jsonDisplay.style.overflow = 'auto';
    }
}

function exportToCSV() {
    // Ambil data dari halaman
    const resultContainer = document.querySelector('.result-container');
    if (!resultContainer) return;
    
    // Buat CSV sederhana
    const data = {
        url: document.querySelector('.url-link')?.textContent || '',
        title: document.querySelector('.stat-card:first-child .stat-value')?.textContent || ''
    };
    
    const csv = Object.entries(data)
        .map(([key, value]) => `${key},${value}`)
        .join('\n');
    
    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'scrape_result.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}
