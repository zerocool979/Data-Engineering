from flask import Blueprint, render_template, request, jsonify, session
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import validators
import re

main = Blueprint('main', __name__)

def scrape_website(url):
    try:
        if not validators.url(url):
            return {"error": "Invalid URL. Please enter the complete URL (example: https://www.example.com)"}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "url": url,
            "title": soup.title.string if soup.title else "No title found",
            "meta_description": "",
            "headings": {
                "h1": [h1.get_text(strip=True) for h1 in soup.find_all('h1')[:5]],
                "h2": [h2.get_text(strip=True) for h2 in soup.find_all('h2')[:5]],
                "h3": [h3.get_text(strip=True) for h3 in soup.find_all('h3')[:5]]
            },
            "links": [],
            "images": [],
            "paragraphs": [],
            "statistics": {}
        }
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result["meta_description"] = meta_desc.get('content', '')
        
        for link in soup.find_all('a', href=True)[:10]:
            href = link.get('href')
            if href and not href.startswith('#'):
                result["links"].append({
                    "text": link.get_text(strip=True)[:50],
                    "url": href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                })
        
        for img in soup.find_all('img', src=True)[:10]:
            src = img.get('src')
            result["images"].append({
                "alt": img.get('alt', 'No alt text'),
                "src": src if src.startswith('http') else url.rstrip('/') + '/' + src.lstrip('/')
            })
        
        for p in soup.find_all('p')[:5]:
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                result["paragraphs"].append(text[:200] + "..." if len(text) > 200 else text)
        
        result["statistics"] = {
            "total_links": len(soup.find_all('a')),
            "total_images": len(soup.find_all('img')),
            "total_paragraphs": len(soup.find_all('p')),
            "total_headings": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        }
        
        return result
        
    except requests.exceptions.Timeout:
        return {"error": "Connection timed out. The server took too long to respond."}
    except requests.exceptions.ConnectionError:
        return {"error": "Failed to connect to the website. Please check the URL and your internet connection."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {str(e)}"}
    except Exception as e:
        return {"error": f"There is an error: {str(e)}"}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url', '').strip()
    
    if not url:
        return render_template('index_result.html', error="Please enter URL")
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    session['last_url'] = url
    return render_template('loading.html', url=url)

@main.route('/scrape/result')
def scrape_result():
    """Endpoint untuk menampilkan hasil scraping"""
    url = request.args.get('url', '')
    
    if not url:
        url = session.get('last_url', '')
    
    if not url:
        return render_template('index_result.html', error="URL not found. Please start a new scraping session.")
    
    result = scrape_website(url)
    
    if "error" in result:
        return render_template('index_result.html', error=result["error"])
    
    return render_template('index_result.html', result=result)

@main.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint untuk scraping (JSON response)"""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = scrape_website(url)
    return jsonify(result)

@main.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})
