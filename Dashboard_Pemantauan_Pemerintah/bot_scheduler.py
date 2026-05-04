import schedule
import time
from datetime import datetime
import logging
from bot_scraper import run_all_scrapers

logging.basicConfig(
    filename='scheduler.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def job():
    print(f"\n[{datetime.now()}] --- Scheduler Terpicu ---")
    logging.info("Memulai proses scraping terjadwal")
    try:
        run_all_scrapers()
        logging.info("Selesai proses scraping.")
    except Exception as e:
        logging.error(f"Error fatal selama proses scheduler: {e}")

# Penjadwalan: Eksekusi setiap 12 jam
# Kita dapat mengubahnya misal setiap jam 08:00 dan 20:00
schedule.every(12).hours.do(job)

if __name__ == "__main__":
    print(f"[{datetime.now()}] Memulai Daemon Bot Scheduler. Scraping berjalan tiap 12 jam.")
    
    # Jalankan satu kali di awal ketika skrip dijalankan
    job()
    
    # Loop continuously
    while True:
        schedule.run_pending()
        time.sleep(60) # Cek jadwal setiap 1 menit
