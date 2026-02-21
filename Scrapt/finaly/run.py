import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib.parse import urljoin, urlparse
import concurrent.futures
import time
import re
import json
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import os
from typing import Dict, List, Set, Optional, Tuple
import random

class WebScraperEcommerce:
    """
    Class utama untuk melakukan web scraping pada website e-commerce
    """
    
    def __init__(self, max_workers: int = 5, headless: bool = True):
        """
        Inisialisasi scraper dengan konfigurasi dasar
        
        Args:
            max_workers: Jumlah maksimum thread untuk parallel processing
            headless: Mode headless untuk selenium browser
        """
        self.max_workers = max_workers
        self.headless = headless
        self.visited_urls: Set[str] = set()
        self.all_data: List[Dict] = []
        self.setup_logging()
        self.setup_session()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_session(self):
        """Setup requests session dengan headers yang tepat"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def init_driver(self):
        """Inisialisasi Selenium WebDriver untuk konten dinamis"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    # ============= FUNGSI 1: USER INPUT =============
    def get_user_input(self) -> str:
        """
        Fungsi untuk mendapatkan input URL dari user
        
        Returns:
            str: URL website yang akan di-scrape
        """
        print("\n" + "="*50)
        print("WEB SCRAPER E-COMMERCE")
        print("="*50)
        
        while True:
            url = input("\nMasukkan URL website e-commerce (contoh: https://shopee.co.id/): ").strip()
            
            # Validasi URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    self.logger.info(f"URL valid: {url}")
                    return url
                else:
                    print(f"URL tidak dapat diakses. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error mengakses URL: {e}")
                print("Silakan coba lagi...")
    
    # ============= FUNGSI 2: ANALISIS HTML =============
    def analyze_html_structure(self, html_content: str, url: str) -> Dict:
        """
        Menganalisis struktur HTML untuk memahami elemen-elemen penting
        
        Args:
            html_content: Konten HTML
            url: URL sumber
            
        Returns:
            Dict: Informasi struktur HTML
        """
        self.logger.info(f"Menganalisis struktur HTML dari: {url}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        structure_info = {
            'url': url,
            'title': soup.title.string if soup.title else 'N/A',
            'meta_tags': {},
            'important_elements': {
                'product_elements': [],
                'price_elements': [],
                'review_elements': [],
                'link_elements': []
            }
        }
        
        # Analisis meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                structure_info['meta_tags'][meta['name']] = meta.get('content', '')
            elif meta.get('property'):
                structure_info['meta_tags'][meta['property']] = meta.get('content', '')
        
        # Identifikasi elemen produk
        product_indicators = ['product', 'item', 'goods', 'barang', 'produk']
        for indicator in product_indicators:
            elements = soup.find_all(class_=re.compile(indicator, re.I))
            structure_info['important_elements']['product_elements'].extend(
                [str(elem)[:100] for elem in elements[:5]]
            )
        
        # Identifikasi elemen harga
        price_indicators = ['price', 'harga', 'discount', 'diskon', 'rp', 'currency']
        for indicator in price_indicators:
            elements = soup.find_all(class_=re.compile(indicator, re.I))
            structure_info['important_elements']['price_elements'].extend(
                [str(elem)[:100] for elem in elements[:5]]
            )
        
        # Identifikasi elemen review
        review_indicators = ['review', 'rating', 'ulasan', 'testimoni']
        for indicator in review_indicators:
            elements = soup.find_all(class_=re.compile(indicator, re.I))
            structure_info['important_elements']['review_elements'].extend(
                [str(elem)[:100] for elem in elements[:5]]
            )
        
        return structure_info
    
    # ============= FUNGSI 3: SCRAPING DATA HALAMAN =============
    def scrape_page_data(self, url: str, use_selenium: bool = False) -> Dict:
        """
        Melakukan scraping semua data dari satu halaman
        
        Args:
            url: URL yang akan di-scrape
            use_selenium: Gunakan Selenium untuk konten dinamis
            
        Returns:
            Dict: Data yang berhasil di-scrape
        """
        self.logger.info(f"Scraping data dari: {url}")
        
        if use_selenium:
            return self._scrape_with_selenium(url)
        else:
            return self._scrape_with_requests(url)
    
    def _scrape_with_requests(self, url: str) -> Dict:
        """Scraping menggunakan Requests + BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return self._extract_all_data(soup, url, response.text)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    def _scrape_with_selenium(self, url: str) -> Dict:
        """Scraping menggunakan Selenium untuk konten JavaScript"""
        driver = None
        try:
            driver = self.init_driver()
            driver.get(url)
            
            # Tunggu hingga konten utama dimuat
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll untuk memuat konten lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            return self._extract_all_data(soup, url, page_source)
            
        except TimeoutException:
            self.logger.error(f"Timeout loading {url} dengan Selenium")
            return {'url': url, 'error': 'Timeout'}
        except Exception as e:
            self.logger.error(f"Error Selenium scraping {url}: {e}")
            return {'url': url, 'error': str(e)}
        finally:
            if driver:
                driver.quit()
    
    def _extract_all_data(self, soup: BeautifulSoup, url: str, raw_html: str) -> Dict:
        """
        Ekstrak semua data yang diperlukan dari BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object
            url: URL sumber
            raw_html: Raw HTML string
            
        Returns:
            Dict: Semua data yang berhasil diekstrak
        """
        data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'pricing_data': self._extract_pricing_data(soup),
            'inventory_data': self._extract_inventory_data(soup),
            'supplier_data': self._extract_supplier_data(soup),
            'review_data': self._extract_review_data(soup),
            'promo_data': self._extract_promo_data(soup),
            'metadata': self._extract_metadata(soup, raw_html)
        }
        
        return data
    
    def _extract_pricing_data(self, soup: BeautifulSoup) -> Dict:
        """Ekstrak data pricing intelligence"""
        pricing = {
            'normal_price': None,
            'discount_price': None,
            'discount_percentage': None,
            'flash_sale_timing': None,
            'wholesale_prices': [],
            'dynamic_patterns': {}
        }
        
        # Cari harga normal
        price_patterns = [
            r'Rp\s*[\d.,]+',
            r'IDR\s*[\d.,]+',
            r'price["\']?\s*:\s*["\']?([\d.,]+)',
            r'original[_\-]?price["\']?\s*:\s*["\']?([\d.,]+)'
        ]
        
        # Cari di text
        for pattern in price_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches and not pricing['normal_price']:
                pricing['normal_price'] = self._clean_price(matches[0])
        
        # Cari harga diskon
        discount_patterns = [
            r'discount[_\-]?price["\']?\s*:\s*["\']?([\d.,]+)',
            r'sale[_\-]?price["\']?\s*:\s*["\']?([\d.,]+)',
            r'promo[_\-]?price["\']?\s*:\s*["\']?([\d.,]+)'
        ]
        
        for pattern in discount_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches and not pricing['discount_price']:
                pricing['discount_price'] = self._clean_price(matches[0])
        
        # Cari flash sale
        flash_sale_elements = soup.find_all(class_=re.compile(r'flash[-_\s]?sale', re.I))
        if flash_sale_elements:
            pricing['flash_sale_timing'] = flash_sale_elements[0].get_text(strip=True)
        
        # Cari harga grosir
        wholesale_elements = soup.find_all(class_=re.compile(r'wholesale|grosir', re.I))
        for elem in wholesale_elements[:5]:
            text = elem.get_text(strip=True)
            if text:
                pricing['wholesale_prices'].append(text[:100])
        
        return pricing
    
    def _extract_inventory_data(self, soup: BeautifulSoup) -> Dict:
        """Ekstrak data stok dan inventory"""
        inventory = {
            'stock_quantity': None,
            'stock_status': None,
            'restock_estimate': None,
            'warehouse_location': None,
            'almost_out': False
        }
        
        # Cari jumlah stok
        stock_patterns = [
            r'stock["\']?\s*:\s*["\']?(\d+)',
            r'stok["\']?\s*:\s*["\']?(\d+)',
            r'quantity["\']?\s*:\s*["\']?(\d+)',
            r'jumlah["\']?\s*:\s*["\']?(\d+)'
        ]
        
        for pattern in stock_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches and not inventory['stock_quantity']:
                try:
                    inventory['stock_quantity'] = int(matches[0])
                    inventory['almost_out'] = inventory['stock_quantity'] < 10
                except ValueError:
                    pass
        
        # Cari status stok
        status_indicators = ['habis', 'tersisa', 'stok', 'stock']
        for indicator in status_indicators:
            elements = soup.find_all(text=re.compile(indicator, re.I))
            if elements and not inventory['stock_status']:
                inventory['stock_status'] = elements[0][:100]
        
        # Cari lokasi gudang
        warehouse_indicators = ['gudang', 'warehouse', 'dikirim dari', 'shipped from']
        for indicator in warehouse_indicators:
            elements = soup.find_all(text=re.compile(indicator, re.I))
            if elements and not inventory['warehouse_location']:
                inventory['warehouse_location'] = elements[0][:100]
        
        return inventory
    
    def _extract_supplier_data(self, soup: BeautifulSoup) -> Dict:
        """Ekstrak data supplier/vendor"""
        supplier = {
            'name': None,
            'email': None,
            'phone': None,
            'brand_partnerships': []
        }
        
        # Cari nama supplier
        supplier_elements = soup.find_all(class_=re.compile(r'shop|store|seller|vendor|penjual|toko', re.I))
        if supplier_elements:
            supplier['name'] = supplier_elements[0].get_text(strip=True)[:100]
        
        # Cari email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, str(soup))
        if emails:
            supplier['email'] = emails[0]
        
        # Cari nomor telepon
        phone_patterns = [
            r'(\+62|0)[0-9]{9,12}',
            r'\(\d{3,4}\)\s*\d{3,4}[-.\s]?\d{3,8}',
            r'\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,8}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, str(soup))
            if phones and not supplier['phone']:
                supplier['phone'] = phones[0]
        
        # Cari brand partnership
        brand_indicators = ['brand', 'partner', 'official', 'resmi', 'authorized']
        for indicator in brand_indicators:
            elements = soup.find_all(text=re.compile(indicator, re.I))
            for elem in elements[:3]:
                supplier['brand_partnerships'].append(elem[:100])
        
        return supplier
    
    def _extract_review_data(self, soup: BeautifulSoup) -> Dict:
        """Ekstrak data customer dan review"""
        reviews = {
            'total_reviews': None,
            'average_rating': None,
            'recent_reviews': [],
            'negative_comments': [],
            'usernames': []
        }
        
        # Cari total review
        review_patterns = [
            r'(\d+)\s*(?:review|ulasan)',
            r'total[_\-]?reviews["\']?\s*:\s*["\']?(\d+)'
        ]
        
        for pattern in review_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches and not reviews['total_reviews']:
                try:
                    reviews['total_reviews'] = int(matches[0])
                except ValueError:
                    pass
        
        # Cari rating rata-rata
        rating_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:rating|bintang)',
            r'average[_\-]?rating["\']?\s*:\s*["\']?(\d+(?:\.\d+)?)'
        ]
        
        for pattern in rating_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches and not reviews['average_rating']:
                try:
                    reviews['average_rating'] = float(matches[0])
                except ValueError:
                    pass
        
        # Ambil beberapa review terbaru
        review_elements = soup.find_all(class_=re.compile(r'review|ulasan|testimoni', re.I))
        for elem in review_elements[:10]:
            review_text = elem.get_text(strip=True)
            if review_text and len(review_text) > 10:
                # Deteksi komentar negatif
                negative_keywords = ['jelek', 'buruk', 'kecewa', 'rusak', 'cacat', 'lambat']
                if any(keyword in review_text.lower() for keyword in negative_keywords):
                    reviews['negative_comments'].append(review_text[:200])
                
                reviews['recent_reviews'].append(review_text[:200])
        
        # Cari username pembeli
        username_patterns = [
            r'username["\']?\s*:\s*["\']?([^"\']+)',
            r'buyer["\']?\s*:\s*["\']?([^"\']+)',
            r'pembeli["\']?\s*:\s*["\']?([^"\']+)'
        ]
        
        for pattern in username_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            reviews['usernames'].extend(matches[:5])
        
        return reviews
    
    def _extract_promo_data(self, soup: BeautifulSoup) -> Dict:
        """Ekstrak data promo dan campaign"""
        promo = {
            'discount_patterns': [],
            'vouchers': [],
            'cashback': [],
            'affiliate_info': []
        }
        
        # Cari pola diskon
        discount_elements = soup.find_all(text=re.compile(r'diskon|discount|promo|sale', re.I))
        for elem in discount_elements[:10]:
            promo['discount_patterns'].append(elem[:100])
        
        # Cari voucher
        voucher_elements = soup.find_all(text=re.compile(r'voucher|kupon', re.I))
        for elem in voucher_elements[:10]:
            promo['vouchers'].append(elem[:100])
        
        # Cari cashback
        cashback_elements = soup.find_all(text=re.compile(r'cashback', re.I))
        for elem in cashback_elements[:10]:
            promo['cashback'].append(elem[:100])
        
        # Cari affiliate program
        affiliate_elements = soup.find_all(text=re.compile(r'affiliate|afiliasi', re.I))
        for elem in affiliate_elements[:10]:
            promo['affiliate_info'].append(elem[:100])
        
        return promo
    
    def _extract_metadata(self, soup: BeautifulSoup, raw_html: str) -> Dict:
        """Ekstrak metadata halaman"""
        metadata = {
            'page_title': soup.title.string if soup.title else 'N/A',
            'meta_description': None,
            'meta_keywords': None,
            'html_size': len(raw_html),
            'script_count': len(soup.find_all('script')),
            'link_count': len(soup.find_all('a')),
            'image_count': len(soup.find_all('img'))
        }
        
        # Cari meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata['meta_description'] = meta_desc['content']
        
        # Cari meta keywords
        meta_keys = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keys and meta_keys.get('content'):
            metadata['meta_keywords'] = meta_keys['content']
        
        return metadata
    
    def _clean_price(self, price_str: str) -> str:
        """Membersihkan string harga"""
        # Hapus karakter non-digit kecuali koma dan titik
        cleaned = re.sub(r'[^\d.,]', '', price_str)
        return cleaned
    
    # ============= FUNGSI 4: EKSTRAK ENDPOINT =============
    def extract_endpoints(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Mengekstrak semua endpoint dari halaman
        
        Args:
            soup: BeautifulSoup object
            base_url: URL dasar untuk membangun URL absolut
            
        Returns:
            List[str]: Daftar URL endpoint
        """
        self.logger.info("Mengekstrak endpoint dari halaman")
        
        endpoints = set()
        
        # Cari semua link
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Filter link yang relevan
            if self._is_valid_endpoint(href):
                absolute_url = urljoin(base_url, href)
                
                # Filter URL yang sudah dikunjungi
                if absolute_url not in self.visited_urls:
                    endpoints.add(absolute_url)
        
        # Cari link dalam JavaScript
        script_patterns = [
            r'location\.href\s*=\s*["\']([^"\']+)',
            r'window\.open\(["\']([^"\']+)',
            r'url["\']?\s*:\s*["\']([^"\']+)'
        ]
        
        for pattern in script_patterns:
            matches = re.findall(pattern, str(soup))
            for match in matches:
                if self._is_valid_endpoint(match):
                    absolute_url = urljoin(base_url, match)
                    if absolute_url not in self.visited_urls:
                        endpoints.add(absolute_url)
        
        self.logger.info(f"Ditemukan {len(endpoints)} endpoint baru")
        return list(endpoints)
    
    def _is_valid_endpoint(self, url: str) -> bool:
        """
        Memeriksa apakah URL valid untuk di-scrape
        
        Args:
            url: URL yang akan diperiksa
            
        Returns:
            bool: True jika valid
        """
        # Skip URL yang tidak diinginkan
        skip_patterns = [
            r'javascript:',
            r'mailto:',
            r'tel:',
            r'#',
            r'logout',
            r'login',
            r'register',
            r'cart',
            r'checkout',
            r'\.(jpg|jpeg|png|gif|pdf|doc|zip|css|js)$'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url, re.I):
                return False
        
        return True
    
    # ============= FUNGSI 5 & 6: PARALLEL PROCESSING =============
    def process_endpoints_parallel(self, endpoints: List[str]) -> List[Dict]:
        """
        Memproses multiple endpoints secara parallel
        
        Args:
            endpoints: Daftar URL yang akan diproses
            
        Returns:
            List[Dict]: Hasil scraping dari semua endpoint
        """
        self.logger.info(f"Memproses {len(endpoints)} endpoint secara parallel")
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit semua task
            future_to_url = {
                executor.submit(self.scrape_page_data, url): url 
                for url in endpoints
            }
            
            # Kumpulkan hasil
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                    self.visited_urls.add(url)
                    self.logger.info(f"Berhasil memproses: {url}")
                    
                    # Delay random untuk menghindari blocking
                    time.sleep(random.uniform(1, 3))
                    
                except concurrent.futures.TimeoutError:
                    self.logger.error(f"Timeout memproses: {url}")
                except Exception as e:
                    self.logger.error(f"Error memproses {url}: {e}")
        
        return results
    
    # ============= FUNGSI 7: LOOPING UNTUK SEMUA ENDPOINT =============
    def scrape_all_endpoints(self, start_url: str, max_depth: int = 3, max_pages: int = 50):
        """
        Melakukan scraping berulang untuk semua endpoint yang ditemukan
        
        Args:
            start_url: URL awal
            max_depth: Kedalaman maksimum crawling
            max_pages: Maksimum jumlah halaman yang di-scrape
        """
        self.logger.info(f"Memulai scraping semua endpoint dari: {start_url}")
        
        # Inisialisasi
        urls_to_scrape = [start_url]
        depth = 0
        
        while urls_to_scrape and depth < max_depth and len(self.visited_urls) < max_pages:
            self.logger.info(f"Depth {depth + 1}: Memproses {len(urls_to_scrape)} URL")
            
            # Proses URL saat ini secara parallel
            batch_results = self.process_endpoints_parallel(urls_to_scrape)
            
            # Simpan hasil
            self.all_data.extend(batch_results)
            
            # Cari URL baru dari hasil scraping
            new_urls = set()
            for result in batch_results:
                if 'error' not in result:
                    # Ambil halaman untuk mengekstrak endpoint baru
                    try:
                        response = self.session.get(result['url'], timeout=10)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        endpoints = self.extract_endpoints(soup, result['url'])
                        new_urls.update(endpoints)
                    except:
                        continue
            
            # Update URL untuk diproses selanjutnya
            urls_to_scrape = list(new_urls - self.visited_urls)
            
            depth += 1
            
            self.logger.info(f"Total halaman terproses: {len(self.visited_urls)}")
        
        self.logger.info(f"Selesai scraping. Total halaman: {len(self.visited_urls)}")
    
    # ============= FUNGSI 8: SIMPAN KE CSV =============
    def save_to_csv(self, filename: str = None):
        """
        Menyimpan hasil scraping ke file CSV yang terstruktur
        
        Args:
            filename: Nama file output (opsional)
        """
        if not self.all_data:
            self.logger.warning("Tidak ada data untuk disimpan")
            return
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'scraper_results_{timestamp}.csv'
        
        self.logger.info(f"Menyimpan {len(self.all_data)} hasil ke {filename}")
        
        # Flatten data untuk CSV
        flattened_data = []
        
        for item in self.all_data:
            if 'error' in item:
                continue
                
            row = {
                'URL': item['url'],
                'Timestamp': item['timestamp'],
                
                # Pricing Data
                'Harga Normal': item['pricing_data']['normal_price'],
                'Harga Diskon': item['pricing_data']['discount_price'],
                'Diskon (%)': item['pricing_data']['discount_percentage'],
                'Flash Sale': item['pricing_data']['flash_sale_timing'],
                'Harga Grosir': '; '.join(item['pricing_data']['wholesale_prices']),
                
                # Inventory Data
                'Jumlah Stok': item['inventory_data']['stock_quantity'],
                'Status Stok': item['inventory_data']['stock_status'],
                'Estimasi Restock': item['inventory_data']['restock_estimate'],
                'Lokasi Gudang': item['inventory_data']['warehouse_location'],
                'Hampir Habis': item['inventory_data']['almost_out'],
                
                # Supplier Data
                'Nama Supplier': item['supplier_data']['name'],
                'Email Supplier': item['supplier_data']['email'],
                'No Telepon': item['supplier_data']['phone'],
                'Brand Partnership': '; '.join(item['supplier_data']['brand_partnerships']),
                
                # Review Data
                'Total Review': item['review_data']['total_reviews'],
                'Rating Rata-rata': item['review_data']['average_rating'],
                'Review Terbaru': '; '.join(item['review_data']['recent_reviews'][:3]),
                'Komentar Negatif': '; '.join(item['review_data']['negative_comments'][:3]),
                'Username Pembeli': '; '.join(item['review_data']['usernames']),
                
                # Promo Data
                'Pola Diskon': '; '.join(item['promo_data']['discount_patterns']),
                'Voucher': '; '.join(item['promo_data']['vouchers']),
                'Cashback': '; '.join(item['promo_data']['cashback']),
                'Informasi Afiliasi': '; '.join(item['promo_data']['affiliate_info']),
                
                # Metadata
                'Page Title': item['metadata']['page_title'],
                'Meta Description': item['metadata']['meta_description'],
                'Jumlah Link': item['metadata']['link_count'],
                'Jumlah Gambar': item['metadata']['image_count']
            }
            
            flattened_data.append(row)
        
        # Buat DataFrame dan simpan ke CSV
        if flattened_data:
            df = pd.DataFrame(flattened_data)
            
            # Reorder columns untuk kemudahan membaca
            column_order = [
                'URL', 'Timestamp', 'Page Title',
                'Harga Normal', 'Harga Diskon', 'Diskon (%)', 'Flash Sale', 'Harga Grosir',
                'Jumlah Stok', 'Status Stok', 'Estimasi Restock', 'Lokasi Gudang', 'Hampir Habis',
                'Nama Supplier', 'Email Supplier', 'No Telepon', 'Brand Partnership',
                'Total Review', 'Rating Rata-rata', 'Review Terbaru', 'Komentar Negatif', 'Username Pembeli',
                'Pola Diskon', 'Voucher', 'Cashback', 'Informasi Afiliasi',
                'Meta Description', 'Jumlah Link', 'Jumlah Gambar'
            ]
            
            # Hanya gunakan kolom yang ada
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            # Simpan ke CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_NONNUMERIC)
            
            self.logger.info(f"Data berhasil disimpan ke {filename}")
            self.logger.info(f"Total baris: {len(df)}")
            
            # Buat juga ringkasan statistik
            self._save_summary_stats(filename.replace('.csv', '_summary.csv'), df)
        else:
            self.logger.warning("Tidak ada data valid untuk disimpan")
    
    def _save_summary_stats(self, filename: str, df: pd.DataFrame):
        """
        Menyimpan ringkasan statistik
        
        Args:
            filename: Nama file output
            df: DataFrame dengan data
        """
        summary = {
            'Total Halaman': [len(df)],
            'Total Produk dengan Stok': [df['Jumlah Stok'].notna().sum()],
            'Rata-rata Stok': [df['Jumlah Stok'].mean() if df['Jumlah Stok'].dtype in ['int64', 'float64'] else 0],
            'Produk Hampir Habis': [df['Hampir Habis'].sum() if 'Hampir Habis' in df.columns else 0],
            'Rata-rata Rating': [df['Rating Rata-rata'].mean() if df['Rating Rata-rata'].dtype in ['int64', 'float64'] else 0],
            'Total Supplier Unik': [df['Nama Supplier'].nunique() if 'Nama Supplier' in df.columns else 0],
            'Total Review': [df['Total Review'].sum() if df['Total Review'].dtype in ['int64', 'float64'] else 0],
            'Timestamp': [datetime.now().isoformat()]
        }
        
        summary_df = pd.DataFrame(summary)
        summary_df.to_csv(filename, index=False, encoding='utf-8-sig')
        self.logger.info(f"Ringkasan statistik disimpan ke {filename}")
    
    # ============= FUNGSI UTAMA =============
    def run(self):
        """
        Fungsi utama untuk menjalankan seluruh proses scraping
        """
        try:
            # Langkah 1: Input dari user
            start_url = self.get_user_input()
            
            # Langkah 2 & 3: Analisis awal dan scraping halaman pertama
            self.logger.info("Menganalisis halaman utama...")
            initial_data = self.scrape_page_data(start_url, use_selenium=True)
            self.all_data.append(initial_data)
            self.visited_urls.add(start_url)
            
            # Analisis struktur HTML
            if 'error' not in initial_data:
                response = self.session.get(start_url)
                structure = self.analyze_html_structure(response.text, start_url)
                self.logger.info(f"Struktur HTML: {json.dumps(structure, indent=2)[:500]}...")
            
            # Langkah 4-7: Scraping semua endpoint secara berulang
            self.scrape_all_endpoints(start_url, max_depth=3, max_pages=30)
            
            # Langkah 8: Simpan ke CSV
            self.save_to_csv()
            
            self.logger.info("Proses scraping selesai!")
            
        except KeyboardInterrupt:
            self.logger.info("Proses dihentikan oleh user")
            self.save_to_csv('scraper_partial_results.csv')
        except Exception as e:
            self.logger.error(f"Error dalam proses utama: {e}")
            self.save_to_csv('scraper_error_results.csv')

# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    # Buat instance scraper
    scraper = WebScraperEcommerce(max_workers=3, headless=True)
    
    # Jalankan proses scraping
    scraper.run()
    
    print("\n" + "="*50)
    print("PROSES SELESAI")
    print("="*50)
    print("\nHasil scraping telah disimpan dalam file CSV.")
    print("Cek file scraper_results_[timestamp].csv untuk melihat hasil.")
    print("Cek file scraper.log untuk melihat log detail.")