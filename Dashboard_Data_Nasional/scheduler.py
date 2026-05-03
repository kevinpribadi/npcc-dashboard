import time
import schedule
from scraper_engine import ScraperEngine

def job():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Memulai job scraping rutin...")
    try:
        engine = ScraperEngine()
        engine.scrape_prototypes()
        engine.close()
        print("Job selesai dengan sukses.")
    except Exception as e:
        print(f"Error pada job scraper: {e}")

# Jadwalkan scraping setiap 12 jam.
schedule.every(12).hours.do(job)

if __name__ == "__main__":
    print("Memulai Service Scheduler (Setiap 12 Jam).")
    print("Menjalankan iterasi pertama...")
    job() # Run once on startup
    
    print("\nMenunggu jadwal berikutnya. Tekan Ctrl+C untuk berhenti.")
    while True:
        schedule.run_pending()
        time.sleep(60) # Cek setiap 1 menit
