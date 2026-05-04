import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

# Konfigurasi Halaman Streamlit - MUST BE THE FIRST COMMAND
st.set_page_config(
    page_title="Dashboard Pemantauan Data Strategis",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling Tambahan untuk "Vibe Coding" & Professional Look
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1a365d;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
    }
    .metric-card {
        background-color: #f8fafc;
        border-left: 5px solid #2563eb;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Path Database
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

@st.cache_data(ttl=3600)  # Caching 1 Jam agar performa dashboard ngebut
def load_data():
    """Mengambil data dari SQLite dengan caching bawaan Streamlit."""
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}")
        query = "SELECT * FROM publikasi_kementerian ORDER BY waktu_scraping DESC"
        df = pd.read_sql(query, engine)
        
        # Konversi tipe datetime jika diperlukan (optional formatting)
        if not df.empty:
            df['waktu_scraping'] = pd.to_datetime(df['waktu_scraping']).dt.strftime('%d %b %Y, %H:%M')
            
        return df
    except Exception as e:
        # Jika file DB tidak ada atau query gagal
        st.error(f"Koneksi Database gagal: {e}")
        return pd.DataFrame()

def main():
    st.title("🏛️ Hub Kebijakan & Data Strategis End-to-End")
    st.write("Dashboard Command Center untuk memantau pergerakan, kebijakan, dan rilis laporan makroekonomi lintas kementerian/lembaga.")
    
    st.sidebar.header("🕹️ Filter Kontrol")
    
    df = load_data()
    
    if df.empty:
         st.warning("Belum ada data di database. Pastikan module `bot_scraper.py` atau scheduler sudah dijalankan terlebih dahulu.")
         return
         
    # Konfigurasi Filter
    kementerian_list = ['Semua Kementerian/Lembaga'] + list(df['sumber_kementerian'].unique())
    selected_kementerian = st.sidebar.selectbox("Fokus Lembaga", kementerian_list)
    
    # Text Search Filter
    search_query = st.sidebar.text_input("🔍 Cari Kata Kunci Rilis", "")
    
    # Logika Filter
    df_filtered = df.copy()
    
    if selected_kementerian != 'Semua Kementerian/Lembaga':
        df_filtered = df_filtered[df_filtered['sumber_kementerian'] == selected_kementerian]
        
    if search_query:
        # Case insensitive text search
        df_filtered = df_filtered[df_filtered['judul_berita'].str.contains(search_query, case=False, na=False)]

    # Layout Bagian Atas: Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
         st.markdown(f"""
         <div class="metric-card">
            <h4>Total Publikasi Terpantau</h4>
            <h2>{len(df_filtered)}</h2>
         </div>
         """, unsafe_allow_html=True)
         
    with col2:
         st.markdown(f"""
         <div class="metric-card">
            <h4>Sumber Aktif</h4>
            <h2>{df_filtered['sumber_kementerian'].nunique()}</h2>
         </div>
         """, unsafe_allow_html=True)
         
    with col3:
         latest = "N/A"
         if not df_filtered.empty:
             latest = df_filtered['waktu_scraping'].iloc[0]
         st.markdown(f"""
         <div class="metric-card">
            <h4>Pembaruan Terakhir</h4>
            <h4>{latest}</h4>
         </div>
         """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Layout Tabel Profesional
    st.subheader("Data Rilis Terkini")
    
    if df_filtered.empty:
         st.info("Tidak ada data yang sesuai dengan filter Anda.")
    else:
         # Hanya menampilkan kolom yang relevan
         display_df = df_filtered[['sumber_kementerian', 'tanggal_publikasi', 'judul_berita', 'waktu_scraping', 'link_url']]
         
         # Tampilkan di UI dengan format kolom interaktif (bisa klik link URL)
         st.dataframe(
             display_df,
             column_config={
                 "sumber_kementerian": st.column_config.TextColumn("Lembaga"),
                 "tanggal_publikasi": st.column_config.TextColumn("Tgl Publikasi"),
                 "judul_berita": st.column_config.TextColumn("Judul Rilis / Laporan"),
                 "waktu_scraping": st.column_config.TextColumn("Ditarik Oleh Bot Pada"),
                 "link_url": st.column_config.LinkColumn("Opsi Lanjutan", display_text="Buka Sumber 🔗")
             },
             hide_index=True,
             use_container_width=True
         )

if __name__ == "__main__":
    main()
