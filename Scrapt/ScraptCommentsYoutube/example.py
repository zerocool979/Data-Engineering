from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from IPython.display import HTML, display
from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import base64
import time
import os
def button(file_path , button_text):
    with open(file_path , 'rb') as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    html = '''

    '''.format(file_name=os.path.basename(file_path),b64_data=b64, button_text=button_text)
    return HTML(html)
def main():
    chrome_options = Options()
    chrome_options.add_argument('--disable -dev-shm-usage')
    chrome_options.add_argument('--disable -extensions')
    chrome_options.add_argument('--start -maximized')
    chrome_options.add_argument('--disable -gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        url = 'https://www.youtube.com/watch?v=KH9txRUApUM'
        print("Membuka YouTube...")
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        print("Menunggu komentar muncul...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR , 'ytd-comments#comments')))
        print("Jeda 10 detik sebelum mulai scroll...\n")
        time.sleep(10)
        data = []
        print("Mulai sroll dan mengambil komentar...")
        for item in tqdm(range(10), desc='Srolling'):
            wait.until(EC.visibility_of_element_located((By.TAG_NAME , "body"))).send_keys(Keys.END)
            time.sleep(15)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source , 'html.parser')
        comment_elements = soup.select('ytd-comment -thread -renderer')
        for comment in comment_elements:
            comment_text_tag = comment.select_one('ytattributed -string#content -text')
            username_tag = comment.select_one('a#author -textspan')
            if comment_text_tag and username_tag:
                comment_text = comment_text_tag.get_text(strip=True)
                username = username_tag.get_text(strip=True)
                data.append({'Username': username , 'Comment':comment_text})
        print(f"Total komentar yang diambil: {len(data)}\n")
        df=pd.DataFrame(data)
        print(df.head())
        file_name='dataset_youtube_comment.csv'
        df.to_csv(file_name , index=False)
        print(f'\nData berhasil disimpan:\n')
        display(button(file_name , 'Download File'))
    except Exception as e:
        print(f"terjadi kesalahan: {e}")
    finally:
        driver.quit()
    if __name__=="__main__":
        main()