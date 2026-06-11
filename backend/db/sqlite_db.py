import sqlite3
import json
import time
from pathlib import Path
from typing import Any, Optional

from .config import settings
from .utils import url_hash

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS article_cache (
            url_hash TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT,
            text TEXT,
            source TEXT,
            author TEXT,
            published_at TEXT,
            cached_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS propagation_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_hash TEXT NOT NULL,
            claim_id INTEGER NOT NULL,
            source_domain TEXT NOT NULL,
            source_name TEXT,
            publish_time TEXT,
            role TEXT NOT NULL,
            altered INTEGER DEFAULT 0,
            cached_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS source_nodes (
            domain TEXT PRIMARY KEY,
            name TEXT,
            trust_score REAL,
            total_articles INTEGER DEFAULT 0,
            credibility_avg REAL
        );

        CREATE TABLE IF NOT EXISTS source_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_domain TEXT NOT NULL,
            target_domain TEXT NOT NULL,
            claim_id INTEGER,
            copied_at TEXT,
            altered INTEGER DEFAULT 0,
            UNIQUE(source_domain, target_domain, claim_id)
        );

        CREATE INDEX IF NOT EXISTS idx_article_cache_hash ON article_cache(url_hash);
        CREATE INDEX IF NOT EXISTS idx_propagation_url ON propagation_events(url_hash);
        CREATE INDEX IF NOT EXISTS idx_propagation_claim ON propagation_events(claim_id);
    """)


def cache_article(url: str, article: dict, ttl_hours: int = 24) -> None:
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO article_cache
 (url_hash, url, title, text, source, author, published_at, cached_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                url_hash(url),
                url,
                article.get("title"),
                article.get("text"),
                article.get("source"),
                article.get("author"),
                article.get("published_at"),
                int(time.time()),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_cached_article(url: str, ttl_hours: int = 24) -> Optional[dict]:
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT * FROM article_cache
            WHERE url_hash = ? AND (strftime('%s','now') - cached_at) < ?
            """,
            (url_hash(url), ttl_hours * 3600),
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def save_propagation_events(url_hash_val: str, events: list[dict]) -> None:
    conn = get_db()
    try:
        for event in events:
            conn.execute(
                """
                INSERT OR IGNORE INTO propagation_events
                (url_hash, claim_id, source_domain, source_name, publish_time, role, altered, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    url_hash_val,
                    event.get("claim_id", 0),
                    event["source_domain"],
                    event.get("source_name"),
                    event.get("publish_time"),
                    event["role"],
                    int(event.get("altered", False)),
                    int(time.time()),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def save_source_graph(nodes: list[dict], edges: list[dict]) -> None:
    conn = get_db()
    try:
        for node in nodes:
            conn.execute(
                """
                INSERT OR REPLACE INTO source_nodes
                (domain, name, trust_score, total_articles, credibility_avg)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    node["domain"],
                    node.get("name"),
                    node.get("trust_score", 5.0),
                    node.get("total_articles", 0),
                    node.get("credibility_avg", 5.0),
                ),
            )
        for edge in edges:
            conn.execute(
                """
                INSERT OR IGNORE INTO source_edges
                (source_domain, target_domain, claim_id, copied_at, altered)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    edge["source_domain"],
                    edge["target_domain"],
                    edge.get("claim_id"),
                    edge.get("copied_at"),
                    int(edge.get("altered", False)),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def get_source_graph() -> dict:
    conn = get_db()
    try:
        nodes = [
            dict(r)
            for r in conn.execute("SELECT * FROM source_nodes").fetchall()
        ]
        edges = [
            dict(r)
            for r in conn.execute("SELECT * FROM source_edges").fetchall()
        ]
        return {"nodes": nodes, "edges": edges}
    finally:
        conn.close()
