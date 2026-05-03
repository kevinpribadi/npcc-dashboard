import streamlit as st
import pandas as pd
import sqlite3

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Data Nasional", 
    page_icon="📊", 
    layout="wide"
)

import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_data.db')

# --- FUNGSI PENGAMBILAN DATA (DI-CACHE) ---
@st.cache_data(ttl=600) # Cache tahan 10 menit
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM tb_publikasi ORDER BY waktu_scraping DESC", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- HEADER UI ---
st.title("📊 Nusantara Policy Command Center")
st.subheader("Dashboard Pemantauan Publikasi Kementerian & Lembaga")
st.markdown("Aplikasi mengekstraksi data secara otomatis (12 jam interval) dan menampilkan rilis berita/press-release untuk kebutuhan intelijen bisnis strategis.")

# --- LOAD DATA ---
df = load_data()

if df.empty:
    st.warning("Belum ada data di database. Pastikan script `scraper_engine.py` (atau `scheduler.py`) telah berjalan.")
else:
    # Mengatasi tipe datetime
    if 'tanggal_publikasi' in df.columns:
        df['tanggal_publikasi'] = pd.to_datetime(df['tanggal_publikasi'], errors='coerce')
    
    # --- SIDEBAR FILTER ---
    st.sidebar.header("Filter Data")
    
    sumber_list = df['sumber_kementerian'].dropna().unique().tolist()
    sumber_list.insert(0, "Semua")
    selected_sumber = st.sidebar.selectbox("Filter Kementerian", sumber_list)
    
    # --- PROSES FILTER ---
    df_filtered = df.copy()
    if selected_sumber != "Semua":
        df_filtered = df_filtered[df_filtered['sumber_kementerian'] == selected_sumber]
        
    # --- METRIK KPI ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Berita Diekstrak", value=len(df))
    with col2:
        st.metric(label="Total Data (Tampil)", value=len(df_filtered))
    with col3:
        if not df.empty and 'waktu_scraping' in df.columns:
            waktu_terakhir = df['waktu_scraping'].max()
            st.metric(label="Update Scraping Terakhir", value=str(waktu_terakhir))

    st.divider()

    # --- DATAFRAME VIEW ---
    st.markdown("### Daftar Publikasi Terkini")
    
    # Modifikasi format url agar bisa diklik jika didukung 
    # Atau kita hanya menampilkannya dalam table
    df_display = df_filtered[['sumber_kementerian', 'judul_berita', 'tanggal_publikasi', 'link_url', 'waktu_scraping']]
    
    st.dataframe(
        df_display, 
        use_container_width=True,
        column_config={
            "sumber_kementerian": st.column_config.TextColumn("Sumber"),
            "judul_berita": st.column_config.TextColumn("Judul Berita"),
            "link_url": st.column_config.LinkColumn("Tautan Asli"),
            "tanggal_publikasi": st.column_config.DateColumn("Tanggal Rilis", format="YYYY-MM-DD")
        },
        hide_index=True
    )
    
    # --- TOMBOL REFRESH MANUAL ---
    if st.button("Refresh Cache Data"):
        st.cache_data.clear()
        st.rerun()
