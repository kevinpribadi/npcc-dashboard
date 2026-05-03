import feedparser
import json
import os
import urllib.parse
from datetime import datetime

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

def generate_analysis(agency, title):
    """
    Fungsi sederhana untuk meracik analisis 'Pro, Kontra, dan Pertanyaan Kritis'
    sebagai ganti data dummy di fitur The Whispering General.
    """
    templates = {
        "Kementerian Perdagangan": {
            "pro": ["Kebijakan berpotensi menstabilkan harga pasok domestik.", "Membuka peluang peningkatan neraca dagang positif."],
            "kontra": ["Risiko distorsi harga jika intervensi pasar tidak tepat sasaran.", "Biasanya menekan marjin pelaku usaha menengah di tahap awal."],
            "tanya": ["Apakah sudah ada mitigasi anti-monopoli pada rantai pasok?", "Bagaimana respon asosiasi pengusaha terkait?"]
        },
        "Danantara": {
            "pro": ["Konsolidasi aset raksasa meningkatkan leverage investasi skala makro.", "Mempermudah pendanaan proyek strategis hilirisasi."],
            "kontra": ["Tumpang tindih yurisdiksi dengan Kementerian BUMN masih rawan terjadi.", "Transparansi audit bagi sovereign wealth fund mendapat sorotan keras."],
            "tanya": ["Bagaimana skema dewan pengawas independen bagi Danantara?"]
        },
        "KPPU": {
            "pro": ["Iklim usaha yang lebih adil bagi pelaku UMKM di tengah gempuran korporasi.", "Mencegah permainan kartel harga strategis."],
            "kontra": ["Investigasi KPPU seringkali memakan waktu bertahun-tahun untuk vonis inkrah.", "Sanksi denda terkadang terlalu kecil bagi konglomerat raksasa."],
            "tanya": ["Adakah kasus monopoli komoditas pokok yang sedang aktif dikawal?"]
        }
    }
    
    # Generic default jika tidak ada template khusus
    default = {
            "pro": [f"Langkah {agency} membawa efek katalis pada operasional lembaga.", "Sejalan dengan amanat penyelarasan regulasi strategis."],
            "kontra": ["Hambatan birokratis pada tingkat daerah untuk eksekusi putusan ini.", "Potensi kekurangan fleksibilitas karena rigiditas birokrasi."],
            "tanya": ["Sejauh mana efektivitas putusan ini divalidasi?"]
    }
    
    return templates.get(agency, default)

def fetch_data():
    results = []
    for agency, query in AGENCIES.items():
        # Membaca RSS Google News Bahasa Indonesia
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=id&gl=ID&ceid=ID:id"
        print(f"Menarik data dari {agency}...")
        
        try:
            feed = feedparser.parse(url)
            if feed.entries and len(feed.entries) > 0:
                entry = feed.entries[0] # Ambil headlinenya (Berita No.1)
                analysis = generate_analysis(agency, entry.title)
                results.append({
                    "agency": agency,
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published,
                    "analysis": analysis
                })
            else:
                results.append({
                    "agency": agency,
                    "title": f"[Sistem Alert] Tidak ada data rilis / berita terbaru untuk keyword {agency}.",
                    "link": "#",
                    "published": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    "analysis": generate_analysis(agency, "")
                })
        except Exception as e:
            print(f"Error fetching {agency}: {e}")
            
    # Ekspor ke file JSON
    output_path = os.path.join(os.path.dirname(__file__), 'live_data.json')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"\n[SUKSES] Data berhasil diperbarui pada jam {datetime.now().strftime('%H:%M:%S')}. ({len(results)} entitas tersimpan)")
    except Exception as e:
        print(f"[GAGAL] Error saat menyimpan data: {e}")

if __name__ == "__main__":
    print("=== NPCC ENGINE DIMULAI ===")
    fetch_data()
