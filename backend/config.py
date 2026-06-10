import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    gemini_api_key: str = ""
    google_fact_check_api_key: str = ""
    database_path: Path = DATA_DIR / "sourcewatch.db"
    chromadb_path: Path = DATA_DIR / "chromadb"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    playwright_timeout: int = 30000
    scrape_delay: float = 1.0
    cache_ttl_hours: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
