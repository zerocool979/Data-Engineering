# Download comments from YouTube : pip install youtube-comment-downloader
from youtube_comment_downloader import YoutubeCommentDownloader

# Create & generate PDF (long text, paragraphs, images, styling) : pip install reportlab
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors

# Data visualization / creating graphs : pip install matplotlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Regex (text cleaning / pattern filtering) : built-in (no need to install)
import re

# Command line argument access: built-in (no need to install)
import sys

# Access filesystem / list directory files : built-in (no need to install)
import os

# Clear terminal screen : built-in (no need to install)
import platform

# Counting data frequency (e.g. most frequent words): built-in (no need to install)
from collections import Counter

# Creating a WordCloud visualization: pip install wordcloud
from wordcloud import WordCloud

# Stopwords list for filtering common words in word frequency analysis
from wordcloud import STOPWORDS

# Text sentiment analysis : pip install textblob
from textblob import TextBlob

# ==============================
# VALIDASI ARGUMENT
# ==============================
# def get_url():
#    if len(sys.argv) < 2:
#        introduce_cli()
#        sys.exit()
#    return sys.argv[1].split("?")[0]

# ==============================
# CONFIG
# ==============================

MAX_COMMENTS = 500

SCAN_TYPES = {
    "-scomment": "youtube",
    "-sweb": "website"
}

OPTIONS = {
    "-max": "max_comments"
}

OUTPUTS = {
    "-opdf": "pdf",
    "-ocsv": "csv",
    "-ojson": "json",
    "-oxlsx": "xlsx",
    "-odocx": "docx",
    "-opng": "png",
    "-ojpg": "jpg"
}

# ==============================
# BANNER
# ==============================
def introduce_cli():
    banner = r"""
=================================================================================================================================

    ██████╗ ███████╗████████╗███████╗   ███████╗███╗   ██╗███████╗ ██╗███╗   ██╗███████╗███████╗██████╗ ██╗███╗   ██╗███████╗
    ██╔══██╗██║  ██║╚══██╔══╝██║  ██║   ██╔════╝████╗  ██║██╔════╝ ╚═╝████╗  ██║██╔════╝██╔════╝██║  ██╗╚═╝████╗  ██║██╔════╝
    ██║  ██║███████║   ██║   ███████║   █████╗  ██╔██╗ ██║██║ ████╗██╗██╔██╗ ██║█████╗  █████╗  ███████║██╗██╔██╗ ██║██║ ████╗
    ██║  ██║██╔══██║   ██║   ██╔══██║   ██╔══╝  ██║ ██╗██║██║   ██║██║██║ ██╗██║██╔══╝  ██╔══╝  ██╔══██║██║██║ ██╗██║██║   ██║
    ██████╔╝██║  ██║   ██║   ██║  ██║   ███████╗██║  ████║╚██████╔╝██║██║  ████║███████╗███████╗██║  ██║██║██║  ████║╚██████╔╝
    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝

                                             -This Tool for Education Purpuse only-
                                                    Beel a.k.a zerocool979
=================================================================================================================================
Spider -v1 ( https://github.com/zerocool979/Data-Engineering/Scrapt ) 
Usage   : scan {url} [Type scan] [Options] [Output]
Exaple  :
            - scan https://youtube.com/watch?v=LMIS2PMqCL0 -scomment
            - scan https://youtube.com/watch?v=LMIS2PMqCL0 -scomment -max 200
            - scan https://youtube.com/watch?v=LMIS2PMqCL0 -scomment -max 200 -opdf hasil

            NOTE    : This tool is still under development, sorry if it is still a bit strange :<

TYPE SCAN:
  -sweb: Scan website information.
  -scomment: Scan comment youtube information.

OPTIONS:
  -matplotlib: creating graphic visualizations information from your type scan using matplotlib.
  -pandas: Processing data + create simple visualization information from your type scan using pandas.

  NOTE: must use -ojpg or -opng <name file>.

  -max <number>: Only scan specified number of comments.

OUTPUT:
  -ocsv <name file>  : Output scan with <your input name file>.csv extension.
  -ojson <name file> : Output scan with <your input name file>.json extension.
  -oxlsx <name file> : Output scan with <your input name file>.xlsx extension.
  -odocx <name file> : Output scan with <your input name file>.docx extension.
  -opdf <name file>  : Output scan with <your input name file>.pdf extension.
  -opng <name file>  : Output scan with <your input name file>.png extension.
  -ojpg <name file>  : Output scan with <your input name file>.jpg extension.

ANOTHER:
  exit : exit program...
  help : show this banner again...

FILES:
  ls           : show files in current directory
  pwd          : show current directory path
  clear        : clear terminal screen
  cat <file>   : read file content
  rm <file>    : delete file

=================================================================================================================================
"""
    print(banner)

# ==============================
# Command Line
# ==============================
def cli_loop():
    introduce_cli()

    while True:
        command = input("input somethin' here pleasee... > ").strip()

        if command.lower() == "exit":
            print("Thank u for using this tool, have a nice day >w<")
            sys.exit()

        if command.lower() == "help":
            introduce_cli()
            continue
    
        elif command.lower() == "ls":
            list_files()
            continue

        elif command.lower() == "pwd":
            show_pwd()
            continue

        elif command.lower() == "clear":
            clear_screen()
            continue

        elif command.startswith("cat"):
            read_file(command)
            continue

        elif command.startswith("rm"):
            delete_file(command)
            continue

        elif command == "":
            continue
        parsed = parse_command(command)

        if "error" in parsed:
            print("[ERROR]", parsed["error"])
            continue

        if parsed["scan"] == "youtube":

            print("\n[INFO] wait untill scraping is end...\n")

            comments, top_words, sentiment = main(
                parsed["url"],
                parsed["max"]
            )

        if parsed["output"] == "pdf":

            filename = parsed["filename"] + ".pdf"

            generate_pdf_report(
                filename,
                parsed["url"],
                comments,
                top_words,
                sentiment
            )

        elif parsed["output"] is None:
            print("[INFO] No output file requested")

        else:
            print("[ERROR] Output format not implemented yet")

# ==============================
# LIST FILES IN CURRENT DIRECTORY
# ==============================
def list_files():

    print("\nFiles in current directory:\n")

    files = os.listdir(".")

    if not files:
        print("Directory is empty\n")
        return

    for file in files:
        print(file)

    print()

# ==============================
# SHOW CURRENT DIRECTORY
# ==============================
def show_pwd():
    print("\nCurrent directory:")
    print(os.getcwd(), "\n")


# ==============================
# CLEAR TERMINAL
# ==============================
def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# ==============================
# READ FILE CONTENT
# ==============================
def read_file(command):

    parts = command.split()

    if len(parts) < 2:
        print("[ERROR] Usage: cat <filename>\n")
        return

    filename = parts[1]

    if not os.path.exists(filename):
        print("[ERROR] File not found\n")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            print()
            print(f.read())
            print()
    except:
        print("[ERROR] Cannot read file\n")


# ==============================
# DELETE FILE
# ==============================
def delete_file(command):

    parts = command.split()

    if len(parts) < 2:
        print("[ERROR] Usage: rm <filename>\n")
        return

    filename = parts[1]

    if not os.path.exists(filename):
        print("[ERROR] File not found\n")
        return

    os.remove(filename)

    print(f"[INFO] File deleted: {filename}\n")

# ==============================
# CLEANING TEXT
# ==============================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

# ==============================
# ANALISIS SENTIMEN
# ==============================
def analyze_sentiment(comments):
    positive = negative = neutral = 0

    for comment in comments:
        polarity = TextBlob(comment).sentiment.polarity

        if polarity > 0:
            positive += 1
        elif polarity < 0:
            negative += 1
        else:
            neutral += 1

    return positive, negative, neutral

# ==============================
# ANALISIS FREKUENSI KATA
# ==============================
def get_top_words(text):
    words = text.split()
    filtered = [
        word for word in words
        if word not in STOPWORDS and len(word) > 2
    ]
    counts = Counter(filtered)
    return counts.most_common(10)

# ==============================
# VISUALISASI
# ==============================
def generate_bar_chart(top_words):
    words = [w for w, _ in top_words]
    counts = [c for _, c in top_words]

    plt.figure()
    plt.bar(words, counts)
    plt.xticks(rotation=45)
    plt.title("10 Kata Paling Sering Muncul")
    plt.tight_layout()
    plt.savefig("top_words.png")

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400).generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("wordcloud.png")

def generate_pdf_report(filename, url, original_comments, top_words, sentiment_result):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    title_style = styles["Heading1"]

    # 1. Judul
    elements.append(Paragraph("Hasil Akhir Scraping Command Content Youtube", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # 2. Link Video
    elements.append(Paragraph(f"<b>Link Video/Sumber:</b> {url}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    # 3. 500 Komentar Asli
    elements.append(Paragraph("<b>500 Komentar Utuh/Asli:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    for comment in original_comments:
        elements.append(Paragraph(comment, normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.3 * inch))

    # 4. Top 10 Kata
    elements.append(Paragraph("<b>10 Kata Paling Sering Muncul:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    for word, count in top_words:
        elements.append(Paragraph(f"{word} : {count}", normal_style))

    elements.append(Spacer(1, 0.3 * inch))

    # 5. Gambar top_words.png
    elements.append(Paragraph("<b>Grafik 10 Kata Teratas:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Image("top_words.png", width=5 * inch, height=3 * inch))

    elements.append(Spacer(1, 0.3 * inch))

    # 6. Gambar wordcloud.png
    elements.append(Paragraph("<b>Wordcloud:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Image("wordcloud.png", width=5 * inch, height=3 * inch))

    elements.append(Spacer(1, 0.3 * inch))

    # 7. Hasil Sentimen
    positive, negative, neutral = sentiment_result

    total = positive + negative + neutral
    dominant = max(positive, negative, neutral)

    if dominant == positive:
        conclusion = "Mayoritas komentar bersifat Positif."
    elif dominant == negative:
        conclusion = "Mayoritas komentar bersifat Negatif."
    else:
        conclusion = "Mayoritas komentar bersifat Netral."

    elements.append(Paragraph("<b>Hasil Sentimen:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"Positif : {positive}", normal_style))
    elements.append(Paragraph(f"Negatif : {negative}", normal_style))
    elements.append(Paragraph(f"Netral  : {neutral}", normal_style))

    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "Deskripsi: Analisis dilakukan menggunakan metode TextBlob "
        "yang menghitung nilai polarity dari setiap komentar.",
        normal_style
    ))

    elements.append(Paragraph(
        "Alasan: Nilai polarity > 0 dianggap positif, < 0 negatif, dan = 0 netral.",
        normal_style
    ))

    elements.append(Paragraph(
        f"Kesimpulan: {conclusion}",
        normal_style
    ))

    doc.build(elements)

# ==============================
# MAIN PROGRAM
# ==============================
def main(url, max_comments=MAX_COMMENTS):

    downloader = YoutubeCommentDownloader()
    comments = downloader.get_comments_from_url(url)

    comment_list = [c["text"] for c in comments][:max_comments]
    cleaned_comments = [clean_text(c) for c in comment_list]

    all_text = " ".join(cleaned_comments)

    top_words = get_top_words(all_text)

    print("\n=== 10 KATA PALING SERING MUNCUL ===")
    for word, count in top_words:
        print(f"{word} : {count}")
    
    positive, negative, neutral = analyze_sentiment(cleaned_comments)

    generate_bar_chart(top_words)
    generate_wordcloud(all_text)

    return comment_list, top_words, (positive, negative, neutral)

if __name__ == "__main__":
    def parse_command(command):

        parts = command.split()

        if len(parts) < 2:
            return {"error": "Invalid command"}

        if parts[0] != "scan":
            return {"error": "Unknown command"}

        url = parts[1]

        result = {
            "url": url,
            "scan": None,
            "max": MAX_COMMENTS,
            "output": None,
            "filename": None
        }

        i = 2

        while i < len(parts):

            arg = parts[i]

            # scan type
            if arg in SCAN_TYPES:
                result["scan"] = SCAN_TYPES[arg]

            # options
            elif arg in OPTIONS:

                if i + 1 >= len(parts):
                    return {"error": f"{arg} requires value"}

                value = parts[i+1]

                if arg == "-max":
                    result["max"] = int(value)

                i += 1

            # output
            elif arg in OUTPUTS:

                if i + 1 >= len(parts):
                    return {"error": f"{arg} requires filename"}

                result["output"] = OUTPUTS[arg]
                result["filename"] = parts[i+1]

                i += 1

            else:
                return {"error": f"Unknown option {arg}"}

            i += 1

        return result
    cli_loop()

