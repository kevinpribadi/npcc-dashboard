import feedparser
import json
import os
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import yfinance as yf

# ============================================================
# 1. DATA SUMBER: LEMBAGA & KEYWORD
# ============================================================
AGENCIES = {
    "Kementerian BUMN": "Kementerian BUMN",
    "Kementerian Perdagangan": "Kementerian Perdagangan OR Kemendag",
    "Kementerian Koperasi": "Kementerian Koperasi OR Kemenkop",
    "Danantara": "Badan Pengelola Investasi Daya Anagata Nusantara OR Danantara",
    "BPKN": "Badan Perlindungan Konsumen Nasional OR BPKN",
    "KPPU": "Komisi Pengawas Persaingan Usaha OR KPPU",
    "BP Batam": "BP Batam OR Badan Pengusahaan Kawasan Perdagangan Bebas",
    "BPK Sabang": "Badan Pengusahaan Kawasan Sabang OR BPK Sabang",
    "Dekopin": "Dewan Koperasi Indonesia OR Dekopin",
    "Badan Pengaturan BUMN": "Badan Pengaturan BUMN"
}

# ============================================================
# 2. DATA ANGGOTA KOMISI VI DPR RI
# ============================================================
KOMISI6_MEMBERS = {
    "Gerindra": ["Andre Rosiade", "Khilmi", "Muhammad Husein Fadlulloh", "Mulan Jameela", "Kawendra Lukistian", "Unru Baso"],
    "PDI-P": ["Adisatrya Suryo Sulisto", "Mufti Anam", "Darmadi Durianto", "Rieke Diah Pitaloka", "I Gusti Ngurah Kesuma Kelakan", "Sadarestuwati", "Ida Nurlaela", "Budi Sulistyono", "G. M. Totok Hedi Santosa"],
    "Golkar": ["Nurdin Halid", "Gde Sumarjaya Linggih", "Ahmad Labib", "Sarifah Suraidah", "Doni Akbar", "Firnando Hadityo Ganinduto", "Rizki Faisal", "Muhammad Sarmuji"],
    "PKB": ["Anggia Erma Rini", "Rivqy Abdul Halim", "M. Nasim Khan", "Ida Fauziyah", "Imas Aan Ubudiah"],
    "NasDem": ["Rachmad Gobel", "Asep Wahyuwijaya", "I Nengah Senantara", "Randi Zulmariadi", "Rudi Hartono Bangun", "Subardi"],
    "PKS": ["Amin Ak.", "Rizal Bawazier", "Ghufran", "Ismail"],
    "PAN": ["Eko Patrio", "Nasril Bahar", "Abdul Hakim Bafagih", "Iskandar"],
    "Demokrat": ["Sartono", "Ni Putu Tutik", "Herman Khaeron", "Faujia Helga"]
}

def generate_analysis(agency, title):
    templates = {
        "Kementerian Perdagangan": {
            "pro": ["Kebijakan berpotensi menstabilkan harga pasok domestik."],
            "kontra": ["Risiko distorsi harga jika intervensi pasar tidak tepat sasaran."],
            "tanya": ["Apakah sudah ada mitigasi anti-monopoli pada rantai pasok?"]
        },
    }
    default = {
        "pro": [f"Langkah {agency} membawa efek katalis pada operasional lembaga."],
        "kontra": ["Hambatan birokratis pada tingkat daerah."],
        "tanya": ["Sejauh mana efektivitas putusan ini divalidasi?"]
    }
    return templates.get(agency, default)

def fetch_agency_news():
    results = []
    for agency, query in AGENCIES.items():
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=id&gl=ID&ceid=ID:id"
        try:
            feed = feedparser.parse(url)
            if feed.entries and len(feed.entries) > 0:
                entry = feed.entries[0]
                results.append({
                    "agency": agency,
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "analysis": generate_analysis(agency, entry.title)
                })
            else:
                results.append({"agency": agency, "title": "Tidak ada berita terbaru", "link": "#", "published": "", "analysis": generate_analysis(agency, "")})
        except Exception:
            results.append({"agency": agency, "title": "Gagal menarik data", "link": "#", "published": "", "analysis": generate_analysis(agency, "")})
    return results

def fetch_member_news():
    results = {}
    all_members = [m for members in KOMISI6_MEMBERS.values() for m in members]
    for member in all_members[:10]: # Batasi ke 10 saja agar cepat di Vercel (mencegah timeout)
        try:
            query = urllib.parse.quote(f'"{member}" DPR OR Komisi')
            url = f"https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"
            feed = feedparser.parse(url)
            if feed.entries and len(feed.entries) > 0:
                entry = feed.entries[0]
                results[member] = {"title": entry.title, "link": entry.link, "published": entry.get("published", "N/A")}
        except Exception:
            pass
    return results

def fetch_market_data():
    market_data = {"live_kurs": 15500, "live_minyak": 80}
    try:
        usd_idr = yf.Ticker("IDR=X")
        kurs = usd_idr.history(period="1d")['Close'].iloc[-1]
        market_data["live_kurs"] = int(round(float(kurs)))
    except Exception:
        pass

    try:
        wti_oil = yf.Ticker("CL=F")
        oil = wti_oil.history(period="1d")['Close'].iloc[-1]
        market_data["live_minyak"] = int(round(float(oil)))
    except Exception:
        pass
        
    return market_data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            agency_news = fetch_agency_news()
            member_news = fetch_member_news()
            market_data = fetch_market_data()

            output = {
                "agency_news": agency_news,
                "member_news": member_news,
                "ai_briefing": "Sistem intelijen aktif. Data scraper (yfinance & news) dikembalikan sesuai rollback darurat.",
                "live_kurs": market_data.get("live_kurs"),
                "live_minyak": market_data.get("live_minyak"),
                "last_updated": datetime.now().isoformat()
            }

            self.wfile.write(json.dumps(output).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
