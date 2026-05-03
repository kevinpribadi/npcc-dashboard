import sqlite3
import os
from datetime import datetime

DB_PATH = 'dashboard_data.db'

def init_db():
    """Inisialisasi database SQLite dan membuat tabel jika belum ada."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tb_publikasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sumber_kementerian TEXT,
            judul_berita TEXT,
            tanggal_publikasi TEXT,
            link_url TEXT UNIQUE,
            waktu_scraping DATETIME
        )
    ''')
    conn.commit()
    conn.close()
    print("Database SQLite initialized!")

def insert_or_ignore(sumber, judul, tanggal, link):
    """Menyisipkan data berita ke tabel jika link_url belum pernah ada sebelumnya."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        waktu_scraping = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT OR IGNORE INTO tb_publikasi 
            (sumber_kementerian, judul_berita, tanggal_publikasi, link_url, waktu_scraping)
            VALUES (?, ?, ?, ?, ?)
        ''', (sumber, judul, tanggal, link, waktu_scraping))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # lastrowid returns 0 if INSERT OR IGNORE ignored the row
        if row_id != 0 and cursor.rowcount > 0:
            return True
        return False
    except Exception as e:
        print(f"[DB Error] Gagal menyimpan '{judul[:20]}...': {e}")
        return False

# Jalankan inisialisasi ketika module ini diimport pertama kali
init_db()
