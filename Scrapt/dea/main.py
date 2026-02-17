'''
import requests
import beautifulsoup4 as BeautifulSoup

def scrape_news():
    url = "https://os.cuydrone.id"
    response = requests.get(url)
    element = BeautifulSoup(response.content, 'html.parser')
    headline - element.find("div", class_="headline")
    return headline.text
'''


'''
import requests
import beautifulsoup4 as BeautifulSoup

from bs4 import BeautifulSoup as BS

def filter_web(nama_web):
    nama_element = ""
    nama_kelas = ""

    if nama_web == "cuydrone":
        nama_element = "div"
        nama_kelas = "headline"
    elif nama_web == "tribun":
        nama_element = "div"
        nama_kelas = "hltitle"
    elif nama_web == "kompas":  
        nama_element = "h1"
        nama_kelas = "hlTitle"
    else:
        return "Nama web tidak dikenali"
    
    return [nama_element, nama_kelas]

def scrape_web(nama_web, url):
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Gagal mengambil halaman"

    soup = BS(response.content, 'html.parser')

    hasil_filter = filter_web(nama_web)
    if isinstance(hasil_filter, str):
        return hasil_filter

    nama_element, nama_kelas = hasil_filter

    data = soup.find_all(nama_element, class_=nama_kelas)

    hasil = []
    for item in data:
        teks = item.get_text(strip=True)
        if teks:
            hasil.append(teks)

    return hasil

if __name__ == "__main__":
    url = "https://www.kompas.com/"
    hasil = scrape_web("kompas", url)

    for i, judul in enumerate(hasil, 1):
        print(f"{i}. {judul}")
'''

'''
import requests
import beautifulsoup4 as BeautifulSoup

def filter_web(nama_web):
    nama_element = ""
    nama_kelas = ""

    if nama_web == "cuydrone":
        nama_element = "div"
        nama_kelas = "headline"
    elif nama_web == "tribun":
        nama_element = "div"
        nama_kelas = "hltitle"
    elif nama_web == "kompas":  
        nama_element = "h1"
        nama_kelas = "hlTitle"
    else:
        return "Nama web tidak dikenali"
    
    return [nama_element, nama_kelas]

def scrape_web(nama_web, url):
    response = requests.get(url)

    if response.status_code != 200:
        return "Gagal mengambil halaman"

    soup = BeautifulSoup(response.content, 'html.parser')

    filter_result = filter_web(nama_web)
    if isinstance(filter_result, str):
        return filter_result

    nama_element, nama_kelas = filter_result

    hasil = soup.find_all(nama_element, class_=nama_kelas)

    data = []
    for item in hasil:
        text = item.get_text(strip=True)
        if text:
            data.append(text)

    return data

# Contoh penggunaan
hasil = scrape_web("kompas", "https://www.kompas.com/")
for h in hasil:
    print(h)

    '''

import requests
import beautifulsoup4 as BeautifulSoup

def filter_web(nama_web):
    nama_element = ""
    nama_kelas = ""

    if nama_web == "cuydrone":
        nama_element = "div"
        nama_kelas = "headline"
    elif nama_web == "tribun":
        nama_element = "div"
        nama_kelas = "hltitle"
    elif nama_web == "kompas":  
        nama_element = "h1"
        nama_kelas = "hlTitle"
    else:
        return "Nama web tidak dikenali"
    
    return [nama_element, nama_kelas]

def scrape_web(nama_web, url):
    response = requests.get(url)
    element = BeautifulSoup(response.content, 'html.parser')

