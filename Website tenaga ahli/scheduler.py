import schedule
import time
import engine
import os

def job():
    print("\n--- MENJALANKAN NPCC ENGINE TUGAS TERJADWAL ---")
    engine.fetch_data()
    print("--- TUGAS SELESAI. MENUNGGU JADWAL BERIKUTNYA... ---\n")

if __name__ == "__main__":
    print("==================================================")
    print("       NPCC SCHEDULER DIMULAI (LOCAL MODE)       ")
    print("==================================================")
    
    # 1. Jalankan pertama kali secara langsung
    job()
    
    # 2. Tetapkan jadwal setiap 12 jam
    schedule.every(12).hours.do(job)
    
    try:
        # Loop utama scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SYSTEM] Scheduler dimatikan oleh user.")

