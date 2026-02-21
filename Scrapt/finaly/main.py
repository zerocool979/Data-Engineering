import csv
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

with open('Shopee.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

results = {
    'pricing': [],
    'inventory': [],
    'suppliers': [],
    'reviews': [],
    'promotions': [],
    'categories': [],
    'flash_sale_items': [],
    'trending_searches': []
}

# Fungsi untuk mengekstrak data dari script JSON
def extract_json_data():
    """Ekstrak data dari tag script yang berisi JSON"""
    scripts = soup.find_all('script', type=lambda t: t and ('json' in t or 'javascript' in t))
    
    for script in scripts:
        if script.string:
            # Cari data popSearch (trending searches)
            if 'popsearch_sec' in str(script.string):
                try:
                    # Regex untuk mengekstrak data JSON
                    json_match = re.search(r'"popsearch_sec":({.*?})', str(script.string))
                    if json_match:
                        pop_data = json.loads('{' + json_match.group(1) + '}')
                        if 'data' in pop_data:
                            for item in pop_data['data']:
                                if 'keyword' in item:
                                    results['trending_searches'].append({
                                        'keyword': item['keyword'],
                                        'timestamp': datetime.now().isoformat()
                                    })
                except:
                    pass
            
            # Cari data category tree
            if 'category_list' in str(script.string):
                try:
                    cat_match = re.search(r'"category_list":(\[.*?\])', str(script.string), re.DOTALL)
                    if cat_match:
                        categories = json.loads(cat_match.group(1))
                        for cat in categories:
                            results['categories'].append({
                                'category_id': cat.get('catid', ''),
                                'name': cat.get('display_name', cat.get('name', '')),
                                'parent_id': cat.get('parent_catid', 0),
                                'level': cat.get('level', 1),
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass

# Fungsi untuk mengekstrak data Flash Sale
def extract_flash_sale():
    """Ekstrak data produk Flash Sale"""
    flash_sale_items = soup.find_all('div', class_=re.compile(r'flash|sale', re.I))
    
    for item in soup.find_all('li', class_='image-carousel__item'):
        # Cari item flash sale berdasarkan struktur yang ada di HTML
        flash_link = item.find('a', href=re.compile(r'flash_sale.*fromItem='))
        if flash_link:
            # Ekstrak URL untuk mendapatkan item_id
            href = flash_link.get('href', '')
            item_id_match = re.search(r'fromItem=(\d+)', href)
            
            # Cari harga
            price_element = item.find('strong', class_=re.compile(r'price', re.I))
            discount_element = item.find('div', class_=re.compile(r'discount|EKx6p6', re.I))
            stock_element = item.find('div', class_=re.compile(r'stock|tersisa', re.I))
            
            # Cari nama produk dari aria-label
            aria_label = flash_link.get('aria-label', '')
            
            price = None
            if price_element:
                price_text = price_element.get_text(strip=True)
                price_match = re.search(r'Rp\.?\s*([\d.,]+)', price_text)
                if price_match:
                    price = price_match.group(1).replace('.', '').replace(',', '')
            
            discount = None
            if discount_element:
                discount_text = discount_element.get_text(strip=True)
                discount_match = re.search(r'-(\d+)%', discount_text)
                if discount_match:
                    discount = discount_match.group(1)
            
            results['flash_sale_items'].append({
                'item_id': item_id_match.group(1) if item_id_match else None,
                'product_name': aria_label[:200] if aria_label else None,
                'price': price,
                'discount_percentage': discount,
                'stock_status': stock_element.get_text(strip=True) if stock_element else None,
                'url': href,
                'timestamp': datetime.now().isoformat()
            })

# Fungsi untuk mengekstrak data kategori
def extract_categories():
    """Ekstrak data kategori dari halaman utama"""
    category_links = soup.find_all('a', class_='home-category-list__category-grid')
    
    for cat in category_links:
        href = cat.get('href', '')
        cat_id_match = re.search(r'cat\.(\d+)', href)
        
        # Cari nama kategori
        name_element = cat.find('div', class_='Qwqg8J')
        if name_element:
            results['categories'].append({
                'category_id': cat_id_match.group(1) if cat_id_match else None,
                'name': name_element.get_text(strip=True),
                'url': href,
                'timestamp': datetime.now().isoformat()
            })

# Fungsi untuk mengekstrak data promo footer
def extract_promo_patterns():
    """Ekstrak pola promo dari footer"""
    footer_text = soup.find('footer').get_text() if soup.find('footer') else ''
    
    promo_patterns = ['9.9', '10.10', '11.11', '12.12', 'ramadan', 'flash sale']
    found_promos = []
    
    for pattern in promo_patterns:
        if pattern in footer_text.lower():
            found_promos.append(pattern)
    
    results['promotions'].append({
        'promo_patterns': ', '.join(found_promos),
        'footer_text_snippet': footer_text[:500] + '...' if len(footer_text) > 500 else footer_text,
        'timestamp': datetime.now().isoformat()
    })

# Fungsi untuk mengekstrak data supplier dari footer
def extract_suppliers():
    """Ekstrak informasi supplier/partner dari footer"""
    # Cari bagian pembayaran
    payment_section = soup.find('div', string=re.compile(r'Pembayaran|Payment', re.I))
    if payment_section:
        parent = payment_section.find_parent('div')
        if parent:
            logos = parent.find_all('img')
            for logo in logos:
                alt = logo.get('alt', '')
                src = logo.get('src', '')
                if alt:
                    results['suppliers'].append({
                        'partner_name': alt,
                        'partner_type': 'Payment',
                        'logo_url': src,
                        'timestamp': datetime.now().isoformat()
                    })
    
    # Cari bagian pengiriman
    shipping_section = soup.find('div', string=re.compile(r'Pengiriman|Shipping', re.I))
    if shipping_section:
        parent = shipping_section.find_parent('div')
        if parent:
            logos = parent.find_all('img')
            for logo in logos:
                alt = logo.get('alt', '')
                src = logo.get('src', '')
                if alt:
                    results['suppliers'].append({
                        'partner_name': alt,
                        'partner_type': 'Shipping',
                        'logo_url': src,
                        'timestamp': datetime.now().isoformat()
                    })

# Fungsi untuk menyimpan ke CSV
def save_to_csv():
    """Simpan semua hasil ke file CSV terpisah"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Data Flash Sale
    if results['flash_sale_items']:
        with open(f'shopee_flash_sale_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['item_id', 'product_name', 'price', 'discount_percentage', 'stock_status', 'url', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results['flash_sale_items'])
        print(f"✓ Data Flash Sale disimpan: {len(results['flash_sale_items'])} item")
    
    # 2. Data Kategori
    if results['categories']:
        with open(f'shopee_categories_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['category_id', 'name', 'parent_id', 'level', 'url', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            # Filter unique categories by name
            seen = set()
            unique_cats = []
            for cat in results['categories']:
                if cat['name'] not in seen:
                    seen.add(cat['name'])
                    unique_cats.append(cat)
            writer.writerows(unique_cats)
        print(f"✓ Data Kategori disimpan: {len(unique_cats)} kategori")
    
    # 3. Data Trending Searches
    if results['trending_searches']:
        with open(f'shopee_trending_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['keyword', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results['trending_searches'])
        print(f"✓ Data Trending Searches disimpan: {len(results['trending_searches'])} keyword")
    
    # 4. Data Supplier
    if results['suppliers']:
        with open(f'shopee_suppliers_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['partner_name', 'partner_type', 'logo_url', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results['suppliers'])
        print(f"✓ Data Supplier disimpan: {len(results['suppliers'])} partner")
    
    # 5. Data Promosi
    if results['promotions']:
        with open(f'shopee_promotions_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['promo_patterns', 'footer_text_snippet', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results['promotions'])
        print(f"✓ Data Promosi disimpan")

    # 6. Simpan juga data lengkap dalam format JSON untuk referensi
    with open(f'shopee_complete_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"✓ Data lengkap disimpan dalam format JSON")

# Ekstrak semua data
print("Memulai ekstraksi data dari Shopee.html...")
extract_json_data()
extract_flash_sale()
extract_categories()
extract_promo_patterns()
extract_suppliers()

# Tampilkan ringkasan
print("\n=== RINGKASAN HASIL EKSTRAKSI ===")
print(f"Total Flash Sale Items: {len(results['flash_sale_items'])}")
print(f"Total Kategori: {len(results['categories'])}")
print(f"Total Trending Searches: {len(results['trending_searches'])}")
print(f"Total Supplier/Partner: {len(results['suppliers'])}")
print(f"Total Data Promosi: {len(results['promotions'])}")
print("\n" + "="*40 + "\n")

# Simpan ke CSV
save_to_csv()

print("\n✅ Proses selesai! File CSV telah disimpan.")

