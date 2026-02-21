from youtube_comment_downloader import YoutubeCommentDownloader
import re
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud

url = "https://www.youtube.com/watch?v=LMIS2PMqCL0"

downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url(url)

comment_list = []
for comment in comments:
    comment_list.append(comment['text'])

comment_list = comment_list[:500]

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

cleaned_comments = [clean_text(c) for c in comment_list]
all_text = " ".join(cleaned_comments)

words = all_text.split()

stopwords = ["yang", "dan", "di", "ke", "ini", "itu", "aku", "kamu", "nya", "the"]

filtered_words = [word for word in words if word not in stopwords and len(word) > 2]

word_counts = Counter(filtered_words)
top_words = word_counts.most_common(10)

print("10 Kata Paling Sering Muncul:")
for word, count in top_words:
    print(f"{word} : {count}")

# Grafik
words_list = [word for word, count in top_words]
counts = [count for word, count in top_words]

plt.figure()
plt.bar(words_list, counts)
plt.xticks(rotation=45)
plt.title("10 Kata Paling Sering Muncul")
plt.savefig("top_words.png")

# WordCloud
wordcloud = WordCloud(width=800, height=400).generate(all_text)

plt.figure(figsize=(10,5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.savefig("wordcloud.png")