import time
import logging
import requests
from bs4 import BeautifulSoup
from backend import SessionLocal, init_db, insert_publikasi
import random

# Setting up Advanced Logging
logging.basicConfig(
    filename='scraper_errors.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Kumpulan URL (sebagai contoh / placeholder - struktur sebenarnya bergantung pada masing-masing web)
TARGETS = [
    {
        "nama": "BP BUMN",
        "url": "https://bumn.go.id/media/press-release", # Placeholder URL
        "selector_list": "div.news-item",
        "selector_title": "h3",
        "selector_date": "span.date",
        "selector_link": "a"
    },
    {
        "nama": "Kemendag",
        "url": "https://www.kemendag.go.id/berita/siaran-pers", # Placeholder URL
        "selector_list": "article",
        "selector_title": "h2",
        "selector_date": "time",
        "selector_link": "a"
    },
    {
        "nama": "KPPU",
        "url": "https://kppu.go.id/siaran-pers/", # Placeholder URL
        "selector_list": "article.post",
        "selector_title": "h2.entry-title",
        "selector_date": "span.published",
        "selector_link": "a.more-link"
    }
    # Tambahkan instansi lainnya di sini (BPI Danantara, BPKN, BP Batam, dsb.)
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"
]

def fetch_page_with_retry(url, max_retries=3):
    """Fungsi tangguh mengekstrak halaman dengan sistem retry & rotasi user-agent."""
    for attempt in range(max_retries):
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            # Timeout diberikan pada 15 detik agar scraper tidak stuck pada server gantung
            response = requests.get(url, headers=headers, timeout=15)
            # Jika response 200, return HTML
            if response.status_code == 200:
                return response.text
            elif response.status_code in [403, 429]:
                 # WAF blocking (Cloudflare/dsb)
                 logging.warning(f"Terkena WAF Block ({response.status_code}) di URL: {url}. Melewati.")
                 break # Langsung skip jika terkena rate limit / block absolut
            else:
                 logging.error(f"Status Code {response.status_code} untuk URL: {url}. Retry {attempt+1}/{max_retries}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Koneksi Timeout / Error ke {url}: {e}. Retry {attempt+1}/{max_retries}")
        
        # Backoff exponential
        time.sleep(2 ** attempt)
        
    return None

def extract_and_save_data(instansi_config):
    """Mengekstrak DOM berdasarkan config spesifik dan save ke SQLite."""
    html_content = fetch_page_with_retry(instansi_config['url'])
    if not html_content:
        logging.error(f"Melewati {instansi_config['nama']} karena kegagalan jaringan atau diblokir.")
        return 0

    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.select(instansi_config['selector_list'])
    
    session = SessionLocal()
    inserted_count = 0
    
    for item in items:
        try:
            title_el = item.select_one(instansi_config['selector_title'])
            date_el = item.select_one(instansi_config['selector_date'])
            link_el = item.select_one(instansi_config['selector_link'])
            
            if title_el and link_el:
                title = title_el.get_text(strip=True)
                date_text = date_el.get_text(strip=True) if date_el else "Tanggal Tidak Diketahui"
                
                href = link_el.get('href', '')
                if href.startswith('/'):
                     # Memperbaiki relative URL
                     base_dom = instansi_config['url'].split('/')[0] + "//" + instansi_config['url'].split('/')[2]
                     href = base_dom + href
                     
                data = {
                    'sumber_kementerian': instansi_config['nama'],
                    'judul_berita': title,
                    'tanggal_publikasi': date_text,
                    'link_url': href
                }
                
                if insert_publikasi(session, data):
                     inserted_count += 1
                     
        except Exception as e:
            logging.error(f"Error parsing item di {instansi_config['nama']}: {e}")
            continue

    session.close()
    return inserted_count
    
def run_all_scrapers():
    """Fungsi utama mengeksekusi semua delegasi scraping."""
    init_db() # Pastikan tabel ada
    print(f"[{datetime.now()}] Memulai batch pemantauan kementerian...")
    total_added = 0
    for target in TARGETS:
        print(f"-> Memeriksa {target['nama']}...")
        added = extract_and_save_data(target)
        total_added += added
        # Sleep sebentar agar tidak meledakkan resource jika loop
        time.sleep(2)
        
    print(f"[{datetime.now()}] Selesai. Menambahkan {total_added} publikasi baru ke database.")

if __name__ == "__main__":
    from datetime import datetime
    run_all_scrapers()
