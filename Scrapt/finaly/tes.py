from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

url = input("Masukkan URL target: ")

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
driver.get(url)

time.sleep(5)  # tunggu JS load

html_content = driver.page_source
soup = BeautifulSoup(html_content, "html.parser")

driver.quit()
