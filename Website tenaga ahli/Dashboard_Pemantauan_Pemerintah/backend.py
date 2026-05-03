import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Setup Database Config
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Publikasi(Base):
    __tablename__ = 'publikasi_kementerian'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sumber_kementerian = Column(String, nullable=False)
    judul_berita = Column(String, nullable=False)
    tanggal_publikasi = Column(String, nullable=True)
    link_url = Column(String, nullable=False, unique=True)
    waktu_scraping = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Membangun tabel database jika belum ada"""
    Base.metadata.create_all(engine)
    print("Database SQLite siap dan telah dimuat di:", DB_PATH)

def insert_publikasi(session, data):
    """Menyimpan publikasi baru, skip jika link sudah ada (Unique Constraint)"""
    try:
        # Pengecekan ada / tidaknya link (Upsert handling)
        existing = session.query(Publikasi).filter_by(link_url=data['link_url']).first()
        if not existing:
            new_pub = Publikasi(
                sumber_kementerian=data['sumber_kementerian'],
                judul_berita=data['judul_berita'],
                tanggal_publikasi=data.get('tanggal_publikasi', '-'),
                link_url=data['link_url'],
                waktu_scraping=datetime.now()
            )
            session.add(new_pub)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error Database DB Insert: {e}")
        return False

if __name__ == "__main__":
    init_db()
