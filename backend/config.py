import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# DATA_DIR priority:
# 1. DATA_DIR env var (explicit, e.g. /app/data on Render)
# 2. /app/data if it exists (Docker container)
# 3. backend/data/ (local dev machine)
_DATA_DIR_ENV = os.environ.get("DATA_DIR", "")
if _DATA_DIR_ENV:
    DATA_DIR = Path(_DATA_DIR_ENV).resolve()
elif Path("/app/data").exists():
    DATA_DIR = Path("/app/data")
else:
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Settings(BaseSettings):
    gemini_api_key: str = ""
    google_fact_check_api_key: str = ""
    database_url: str = ""
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

    def model_post_init(self, __context):
        # If chromadb_path or database_path are relative (from env vars like
        # CHROMADB_PATH=./data/chromadb on Render), resolve them against DATA_DIR.
        # Do NOT touch absolute paths.
        if not self.chromadb_path.is_absolute():
            self.chromadb_path = DATA_DIR / "chromadb"
        if not self.database_path.is_absolute():
            self.database_path = DATA_DIR / "sourcewatch.db"


settings = Settings()