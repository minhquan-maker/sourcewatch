import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import health, analyze

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ChromaDB collections...")
    try:
        from db import chromadb_client
        chromadb_client.get_client()
        chromadb_client.get_claims_collection()
        chromadb_client.get_factcheck_collection()
        chromadb_client.get_articles_collection()
        logger.info("ChromaDB initialized successfully")
    except Exception as e:
        logger.error(f"ChromaDB initialization failed: {e}")

    logger.info("Initializing PostgreSQL schema...")
    try:
        from db import sqlite_db
        sqlite_db._init_schema()
        logger.info("PostgreSQL schema initialized")
    except Exception as e:
        logger.error(f"PostgreSQL schema init failed: {e}")

    yield
    logger.info("Shutting down SourceWatch API")


app = FastAPI(
    title="SourceWatch API",
    description="Vietnamese news credibility analyzer",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router)


@app.get("/")
def root():
    return {"message": "SourceWatch API", "version": "1.0.0"}
