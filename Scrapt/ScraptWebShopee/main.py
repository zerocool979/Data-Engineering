import csv
import json
import re
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

with open('Shopee.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

data = {
    'flash_sale': [],
    'categories': [],
    'trending': [],
    'suppliers': [],
    'promotions': [],
    'top_products': [],
    'banners': [],
    'footer_links': []
}

def extract_flash_sale():
    flash_section = soup.find('div', class_='R3bOnT')
    if not flash_section:
        print("Section Flash Sale tidak ditemukan.")
        return

    items = flash_section.find_all('li', class_='image-carousel__item')
    for item in items:
        link = item.find('a', href=re.compile(r'flash_sale.*fromItem='))
        if not link:
            continue

        aria_label = link.get('aria-label', '')
        href = link.get('href', '')
        item_id_match = re.search(r'fromItem=(\d+)', href)

        price_elem = item.find('strong', class_=re.compile(r'iwH3_q'))
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace('Rp', '').replace('.', '').replace(',', '')
            if price_text.isdigit():
                price = int(price_text)

        discount_elem = item.find('div', class_=re.compile(r'EKx6p6'))
        discount = None
        if discount_elem:
            disc_text = discount_elem.get_text(strip=True)
            disc_match = re.search(r'-(\d+)%', disc_text)
            if disc_match:
                discount = int(disc_match.group(1))

        stock_elem = item.find('div', class_=re.compile(r'cx1ruZ'))
        stock_text = stock_elem.get_text(strip=True) if stock_elem else None

        product_name = aria_label[:200] if aria_label else None

        data['flash_sale'].append({
            'item_id': item_id_match.group(1) if item_id_match else None,
            'product_name': product_name,
            'price': price,
            'discount_percent': discount,
            'stock_info': stock_text,
            'url': href,
            'timestamp': datetime.now().isoformat()
        })

def extract_categories():
    """Ekstrak kategori dari home category list."""
    category_links = soup.find_all('a', class_='home-category-list__category-grid')
    for cat in category_links:
        href = cat.get('href', '')
        cat_id_match = re.search(r'cat\.(\d+)', href)
        name_elem = cat.find('div', class_='Qwqg8J')
        name = name_elem.get_text(strip=True) if name_elem else None
        if name:
            data['categories'].append({
                'category_id': cat_id_match.group(1) if cat_id_match else None,
                'name': name,
                'url': href,
                'timestamp': datetime.now().isoformat()
            })

def extract_trending():
    scripts = soup.find_all('script', type=lambda t: t and ('json' in t or 'javascript' in t))
    for script in scripts:
        if script.string and 'popsearch_sec' in script.string:
            try:
                match = re.search(r'"popsearch_sec":({.*?})', script.string, re.DOTALL)
                if match:
                    pop_data = json.loads('{' + match.group(1) + '}')
                    if 'data' in pop_data:
                        for item in pop_data['data']:
                            keyword = item.get('keyword')
                            if keyword:
                                data['trending'].append({
                                    'keyword': keyword,
                                    'timestamp': datetime.now().isoformat()
                                })
            except Exception as e:
                print(f"Gagal parsing trending: {e}")
                continue

def extract_suppliers():
    payment_section = soup.find('div', string=re.compile(r'Pembayaran', re.I))
    if payment_section:
        parent = payment_section.find_parent('div')
        if parent:
            for img in parent.find_all('img'):
                alt = img.get('alt', '')
                src = img.get('src', '')
                if alt:
                    data['suppliers'].append({
                        'partner_name': alt,
                        'type': 'Payment',
                        'logo': src,
                        'timestamp': datetime.now().isoformat()
                    })

    shipping_section = soup.find('div', string=re.compile(r'Pengiriman', re.I))
    if shipping_section:
        parent = shipping_section.find_parent('div')
        if parent:
            for img in parent.find_all('img'):
                alt = img.get('alt', '')
                src = img.get('src', '')
                if alt:
                    data['suppliers'].append({
                        'partner_name': alt,
                        'type': 'Shipping',
                        'logo': src,
                        'timestamp': datetime.now().isoformat()
                    })

def extract_promotions():
    banner_section = soup.find('section', id='HomePageCarouselBannerSection')
    if banner_section:
        banners = banner_section.find_all('a', class_='bWc0R0')
        for idx, banner in enumerate(banners):
            img = banner.find('img')
            if img:
                data['promotions'].append({
                    'type': 'main_banner',
                    'image_url': img.get('src', ''),
                    'link': banner.get('href', ''),
                    'alt': img.get('alt', ''),
                    'timestamp': datetime.now().isoformat()
                })

    square_section = soup.find('section', id='HomePageSquareBannerSection')
    if square_section:
        squares = square_section.find_all('a', class_='sT3XrC')
        for square in squares:
            img = square.find('img')
            name = square.find('div', class_='EJnNeM')
            data['promotions'].append({
                'type': 'square_banner',
                'image_url': img.get('src', '') if img else None,
                'link': square.get('href', ''),
                'name': name.get_text(strip=True) if name else None,
                'timestamp': datetime.now().isoformat()
            })

    footer = soup.find('footer')
    if footer:
        footer_text = footer.get_text()
        promo_patterns = ['9.9', '10.10', '11.11', '12.12', 'ramadan', 'flash sale', 'gratis ongkir']
        found = [p for p in promo_patterns if p in footer_text.lower()]
        data['promotions'].append({
            'type': 'footer_text',
            'promo_names': ', '.join(found),
            'footer_snippet': footer_text[:500] + '...' if len(footer_text) > 500 else footer_text,
            'timestamp': datetime.now().isoformat()
        })

def extract_top_products():
    top_section = soup.find('div', class_='au6P2T')
    if not top_section:
        print("Section Produk Terlaris tidak ditemukan.")
        return

    items = top_section.find_all('li', class_='a11y-image-carousel__item')
    for item in items:
        link = item.find('a', class_='_O6OdC')
        if not link:
            continue
        img = link.find('img')
        name_elem = link.find('div', class_='mXocXb')
        sales_elem = link.find('div', class_='wp7t0i')
        data['top_products'].append({
            'product_name': name_elem.get_text(strip=True) if name_elem else None,
            'image': img.get('src', '') if img else None,
            'sales_info': sales_elem.get_text(strip=True) if sales_elem else None,
            'url': link.get('href', ''),
            'timestamp': datetime.now().isoformat()
        })

def extract_footer_links():
    footer = soup.find('footer')
    if not footer:
        return

    sections = footer.find_all('div', class_='WgSr6D')
    for section in sections:
        title_elem = section.find('div', class_='JlKgZM')
        if not title_elem:
            continue
        title = title_elem.get_text(strip=True)
        links = section.find_all('a', href=True)
        for link in links:
            text = link.get_text(strip=True)
            if text:
                data['footer_links'].append({
                    'section': title,
                    'text': text,
                    'url': link.get('href', ''),
                    'timestamp': datetime.now().isoformat()
                })

print("Mengekstrak data dari Shopee.html...")
extract_flash_sale()
extract_categories()
extract_trending()
extract_suppliers()
extract_promotions()
extract_top_products()
extract_footer_links()

for key in data:
    if not data[key]:
        print(f"Peringatan: Data '{key}' kosong. Mungkin struktur HTML berbeda.")
    else:
        print(f"  ✅ {key}: {len(data[key])} item")

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

all_rows = []
for category, items in data.items():
    for item in items:
        row = {'category': category}
        row.update(item)
        all_rows.append(row)

if all_rows:
    df_all = pd.DataFrame(all_rows)
    df_all.to_csv('hasil.csv', index=False, encoding='utf-8-sig')
    print("hasil.csv berhasil disimpan (gabungan semua data)")
else:
    print("Tidak ada data sama sekali, CSV tidak dibuat.")

with pd.ExcelWriter('hasil.xlsx', engine='openpyxl') as writer:
    for sheet_name, records in data.items():
        if records:
            df = pd.DataFrame(records)
            safe_name = sheet_name[:31].capitalize()
            df.to_excel(writer, sheet_name=safe_name, index=False)
    print("hasil.xlsx berhasil disimpan (multi sheet)")

with open('hasil.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
print("hasil.json berhasil disimpan")

print("\nProses selesai. File yang dihasilkan: hasil.csv, hasil.xlsx, hasil.json")
