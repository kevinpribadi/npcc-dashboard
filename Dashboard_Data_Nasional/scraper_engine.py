from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import database
import time
from datetime import datetime

class ScraperEngine:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        # Set timeout to 30 seconds
        self.page.set_default_timeout(30000)

    def close(self):
        self.browser.close()
        self.playwright.stop()

    def _get_page_content(self, url):
        """Membuka halaman web dan mengembalikan HTML-nya dengan Playwright."""
        try:
            print(f"[Engine] Mengakses url: {url}")
            self.page.goto(url, wait_until='domcontentloaded')
            time.sleep(3) # Tunggu agar halaman dan konten javascript ter-render
            return self.page.content()
        except Exception as e:
            print(f"[Error] Gagal mengakses {url}: {e}")
            return None

    def scrape_prototypes(self):
        """Menjalankan prototipe scraper untuk BUMN dan Kemendag."""
        total_inserted = 0
        
        # 1. Scraping Kementerian BUMN
        bumn_url = "https://bumn.go.id/media/press-release"
        html = self._get_page_content(bumn_url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            # Pendekatan umum: Cari elemen HTML bersarang yang berisi teks panjang dan tautan
            articles = soup.find_all('a', href=True)
            for a in articles:
                # heuristic: class atau isi teks
                text = a.get_text(strip=True)
                if len(text) > 30 and 'bumn.go.id' not in text: # Judul berita biasanya > 30 karakter
                    link = a['href']
                    if not link.startswith('http'):
                        link = f"https://bumn.go.id{link}"
                    if '/media/press-release/' in link or '/berita/' in link:
                        if database.insert_or_ignore("BP BUMN", text, datetime.now().strftime('%Y-%m-%d'), link):
                            total_inserted += 1

        # 2. Scraping Kemendag
        kemendag_url = "https://www.kemendag.go.id/berita/siaran-pers"
        html = self._get_page_content(kemendag_url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('a', href=True)
            for a in articles:
                text = a.get_text(strip=True)
                if len(text) > 30 and 'kemendag' not in text.lower():
                    link = a['href']
                    if not link.startswith('http'):
                        link = f"https://www.kemendag.go.id{link}"
                    if 'berita/siaran-pers/' in link or 'berita/' in link:
                        if database.insert_or_ignore("Kementerian Perdagangan", text, datetime.now().strftime('%Y-%m-%d'), link):
                            total_inserted += 1

        print(f"[Sukses] Bot selesai dieksekusi. Berhasil menyimpan {total_inserted} berita baru.")

if __name__ == "__main__":
    engine = ScraperEngine()
    engine.scrape_prototypes()
    engine.close()
