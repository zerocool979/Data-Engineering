import re
import os
import logging
from datetime import datetime
from collections import Counter
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from youtube_comment_downloader import YoutubeCommentDownloader

# ===================== KONFIGURASI =====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
MAX_COMMENTS = 500  # Batas maksimal komentar yang diambil
STOPWORDS = set([
    "yang", "dan", "di", "ke", "ini", "itu", "aku", "kamu", "nya", "the", "and", "for", "with",
    "pada", "dalam", "untuk", "dengan", "saya", "dia", "mereka", "kita", "adalah", "ada", "bisa",
    "akan", "tidak", "juga", "sudah", "belum", "seperti", "karena", "jadi", "atau", "tapi", "oleh",
    "saat", "kalau", "jika", "maka", "saja", "dari", "lagi", "sebagai", "tersebut", "para", "para"
])  # Stopwords sederhana

# ===================== FUNGSI PEMBERSIHAN TEKS =====================
def clean_text(text):
    """Membersihkan teks komentar: lower case, hapus URL, hapus non-alfabet, dan spasi berlebih."""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)           # hapus URL
    text = re.sub(r"[^a-zA-Z\s]", "", text)       # hapus angka dan tanda baca
    text = re.sub(r"\s+", " ", text).strip()      # hapus spasi berlebih
    return text

# ===================== FUNGSI ANALISIS TAMBAHAN =====================
def analisis_tambahan(comments_raw):
    """Menampilkan beberapa statistik dasar dari komentar."""
    if not comments_raw:
        print("Tidak ada komentar untuk dianalisis.")
        return
    panjang = [len(c) for c in comments_raw]
    print("\n=== Analisis Tambahan ===")
    print(f"Total komentar: {len(comments_raw)}")
    print(f"Rata-rata panjang komentar: {sum(panjang)/len(panjang):.2f} karakter")
    print(f"Komentar terpendek: {min(panjang)} karakter")
    print(f"Komentar terpanjang: {max(panjang)} karakter")
    # Jumlah komentar unik (tidak duplikat)
    unik = len(set(comments_raw))
    print(f"Komentar unik: {unik} ({unik/len(comments_raw)*100:.1f}%)")

# ===================== FUNGSI VISUALISASI =====================
def visualisasi(top_words, all_text, timestamp):
    """Membuat dan menyimpan grafik batang dan wordcloud."""
    # Grafik batang
    words, counts = zip(*top_words)
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue', edgecolor='black')
    plt.xlabel('Kata')
    plt.ylabel('Frekuensi')
    plt.title('10 Kata Paling Sering Muncul dalam Komentar')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'top_words_{timestamp}.png', dpi=150)
    plt.close()
    logging.info(f"Grafik batang disimpan sebagai top_words_{timestamp}.png")

    # Wordcloud
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(all_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('WordCloud dari Komentar YouTube')
    plt.tight_layout()
    plt.savefig(f'wordcloud_{timestamp}.png', dpi=150)
    plt.close()
    logging.info(f"Wordcloud disimpan sebagai wordcloud_{timestamp}.png")

# ===================== FUNGSI UTAMA =====================
def main():
    # 1. Input URL dari user
    url = input("Masukkan URL video YouTube: ").strip()
    if not url:
        logging.error("URL tidak boleh kosong.")
        return

    # 2. Inisialisasi downloader
    downloader = YoutubeCommentDownloader()
    logging.info("Mengambil komentar dari YouTube...")

    # 3. Ambil komentar dengan progress bar (tqdm)
    try:
        comments_generator = downloader.get_comments_from_url(url)
        comments_raw = []
        # Gunakan tqdm untuk menunjukkan progress (maksimal MAX_COMMENTS)
        with tqdm(total=MAX_COMMENTS, desc="Mengunduh komentar") as pbar:
            for i, comment in enumerate(comments_generator):
                if i >= MAX_COMMENTS:
                    break
                comments_raw.append(comment['text'])
                pbar.update(1)
        logging.info(f"Berhasil mengunduh {len(comments_raw)} komentar.")
    except Exception as e:
        logging.error(f"Gagal mengambil komentar: {e}")
        return

    if not comments_raw:
        logging.warning("Tidak ada komentar yang ditemukan.")
        return

    # 4. Simpan data mentah ke CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df_raw = pd.DataFrame(comments_raw, columns=["comment"])
    df_raw.to_csv(f"raw_comments_{timestamp}.csv", index=False)
    logging.info(f"Data mentah disimpan sebagai raw_comments_{timestamp}.csv")

    # 5. Pembersihan teks
    cleaned_comments = [clean_text(c) for c in comments_raw]
    all_text = " ".join(cleaned_comments)

    # 6. Tokenisasi dan filter stopwords
    words = all_text.split()
    filtered_words = [word for word in words if word not in STOPWORDS and len(word) > 2]

    # 7. Hitung frekuensi kata
    word_counts = Counter(filtered_words)
    top_words = word_counts.most_common(10)

    # 8. Tampilkan 10 kata teratas
    print("\n=== 10 Kata Paling Sering Muncul ===")
    for word, count in top_words:
        print(f"{word} : {count}")

    # 9. Analisis tambahan
    analisis_tambahan(comments_raw)

    # 10. Visualisasi
    visualisasi(top_words, all_text, timestamp)

    print(f"\n✅ Selesai! Semua file disimpan dengan timestamp {timestamp}")

if __name__ == "__main__":
    main()
