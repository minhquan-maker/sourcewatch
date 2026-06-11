import json
import logging
from pathlib import Path

from config import settings
from db import chromadb_client

logger = logging.getLogger(__name__)

FACT_CHECK_DB_FILE = settings.chromadb_path.parent / "fact_check_db.json"


def _load_fact_check_db() -> list[dict]:
    try:
        with open(FACT_CHECK_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load fact-check DB: {e}")
        return []


async def check_claims(claims: list[dict]) -> list[dict]:
    fact_checks = []
    db = _load_fact_check_db()

    try:
        chromadb_client.index_fact_checks(db)
    except Exception as e:
        logger.warning(f"Failed to index fact-check DB in ChromaDB: {e}")

    for claim in claims:
        claim_text = claim["text"]
        result = _search_fact_check(claim_text, db)
        fact_checks.append(
            {
                "claim_id": claim["id"],
                "claim": claim_text,
                "status": result["status"],
                "source": result["source"],
                "url": result.get("url", ""),
                "date": result.get("date", ""),
            }
        )

    return fact_checks


def _search_fact_check(claim_text: str, db: list[dict]) -> dict:
    try:
        results = chromadb_client.search_fact_checks(claim_text, n=3)
        if results:
            meta = results[0]["metadata"]
            return {
                "status": meta.get("verdict", "unverified"),
                "source": meta.get("source", "Custom DB"),
                "url": meta.get("url", ""),
                "date": meta.get("date", ""),
            }
    except Exception as e:
        logger.warning(f"ChromaDB fact-check search failed: {e}")

    for fc in db:
        if _claim_matches(claim_text, fc["claim"]):
            return {
                "status": fc["verdict"],
                "source": fc["source"],
                "url": fc.get("url", ""),
                "date": fc.get("date", ""),
            }

    return {"status": "unverified", "source": "Custom DB"}


def _claim_matches(text1: str, text2: str) -> bool:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    overlap = len(words1 & words2)
    return overlap >= 3 and overlap / max(len(words1), len(words2)) > 0.4
