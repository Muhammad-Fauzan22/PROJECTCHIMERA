import os
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env
load_dotenv()

class ProcessedInsight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: str
    source_topic: str
    summary: str
    sentiment_score: float
    bullish_args: str
    bearish_args: str
    narrative_strength: int

# Inisialisasi engine untuk SQLite (mudah untuk memulai)
sqlite_file_name = "knowledge_base.db"
sqlite_url = f"sqlite:///COLLECTIVE_MEMORY/{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    """Membuat database dan semua tabel jika belum ada."""
    SQLModel.metadata.create_all(engine)
