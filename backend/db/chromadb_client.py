import hashlib
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional

from config import settings


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]

_client: Optional[chromadb.PersistentClient] = None


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=str(settings.chromadb_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_claims_collection():
    client = get_client()
    try:
        return client.get_collection("claims")
    except Exception:
        return client.create_collection("claims")


def get_factcheck_collection():
    client = get_client()
    try:
        return client.get_collection("fact_checks")
    except Exception:
        return client.create_collection("fact_checks")


def add_claims(claims: list[dict]):
    collection = get_claims_collection()
    collection.add(
        ids=[f"claim_{i}" for i in range(len(claims))],
        documents=[c["text"] for c in claims],
        metadatas=[{"id": c["id"], "source": c.get("source", "")} for c in claims],
    )


def search_similar_claims(query: str, n: int = 5) -> list[dict]:
    collection = get_claims_collection()
    results = collection.query(query_texts=[query], n_results=n)
    return [
        {
            "id": results["metadatas"][0][i]["id"],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
        }
        for i in range(len(results["documents"][0]))
    ]


def search_fact_checks(query: str, n: int = 3) -> list[dict]:
    collection = get_factcheck_collection()
    results = collection.query(query_texts=[query], n_results=n)
    if not results["documents"][0]:
        return []
    return [
        {
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
            "metadata": results["metadatas"][0][i],
        }
        for i in range(len(results["documents"][0]))
    ]


def index_fact_checks(fact_checks: list[dict]):
    collection = get_factcheck_collection()
    collection.add(
        ids=[f"fc_{i}" for i in range(len(fact_checks))],
        documents=[fc["claim"] for fc in fact_checks],
        metadatas=[
            {
                "verdict": fc["verdict"],
                "source": fc["source"],
                "url": fc.get("url", ""),
                "date": fc.get("date", ""),
            }
            for fc in fact_checks
        ],
    )


def get_articles_collection():
    client = get_client()
    try:
        return client.get_collection("articles")
    except Exception:
        return client.create_collection("articles")


def index_article(url: str, title: str, text: str, source_domain: str, source_name: str):
    """Index an article into ChromaDB for propagation search."""
    collection = get_articles_collection()
    article_id = url_hash(url)
    collection.add(
        ids=[article_id],
        documents=[f"{title}. {text[:4000]}"],
        metadatas=[{
            "url": url,
            "title": title,
            "source_domain": source_domain,
            "source_name": source_name,
        }],
    )


def search_similar_articles(query: str, n: int = 10) -> list[dict]:
    """Search local ChromaDB for articles similar to a claim."""
    collection = get_articles_collection()
    try:
        results = collection.query(query_texts=[query], n_results=n)
    except Exception:
        return []

    if not results or not results["documents"][0]:
        return []

    return [
        {
            "url": results["metadatas"][0][i].get("url", ""),
            "title": results["metadatas"][0][i].get("title", ""),
            "source_domain": results["metadatas"][0][i].get("source_domain", ""),
            "source_name": results["metadatas"][0][i].get("source_name", ""),
            "distance": results["distances"][0][i],
        }
        for i in range(len(results["documents"][0]))
    ]
