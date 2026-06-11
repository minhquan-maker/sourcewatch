import json
import os
import time
from contextlib import contextmanager
from typing import Any, Optional

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from config import settings
from utils import url_hash

_db_pool: Optional[pool.SimpleConnectionPool] = None


def _get_pool() -> pool.SimpleConnectionPool:
    global _db_pool
    if _db_pool is None:
        db_url = os.environ.get("DATABASE_URL") or settings.database_url
        if not db_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set. "
                "Ensure a PostgreSQL database is linked to this service."
            )
        _db_pool = pool.SimpleConnectionPool(
            1, 5,
            db_url,
            cursor_factory=RealDictCursor,
        )
    return _db_pool


@contextmanager
def get_db():
    pg = _get_pool()
    conn = pg.getconn()
    try:
        yield conn
    finally:
        pg.putconn(conn)


def _init_schema(conn):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS article_cache (
                url_hash TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                text TEXT,
                source TEXT,
                author TEXT,
                published_at TEXT,
                cached_at INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS propagation_events (
                id SERIAL PRIMARY KEY,
                url_hash TEXT NOT NULL,
                claim_id INTEGER NOT NULL,
                source_domain TEXT NOT NULL,
                source_name TEXT,
                publish_time TEXT,
                role TEXT NOT NULL,
                altered INTEGER DEFAULT 0,
                cached_at INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS source_nodes (
                domain TEXT PRIMARY KEY,
                name TEXT,
                trust_score REAL,
                total_articles INTEGER DEFAULT 0,
                credibility_avg REAL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS source_edges (
                id SERIAL PRIMARY KEY,
                source_domain TEXT NOT NULL,
                target_domain TEXT NOT NULL,
                claim_id INTEGER,
                copied_at TEXT,
                altered INTEGER DEFAULT 0,
                UNIQUE(source_domain, target_domain, claim_id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_article_cache_hash ON article_cache(url_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_propagation_url ON propagation_events(url_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_propagation_claim ON propagation_events(claim_id)")
        conn.commit()
        cur.close()


def cache_article(url: str, article: dict, ttl_hours: int = 24) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO article_cache
 (url_hash, url, title, text, source, author, published_at, cached_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url_hash) DO UPDATE SET
                title = EXCLUDED.title,
                text = EXCLUDED.text,
                source = EXCLUDED.source,
                author = EXCLUDED.author,
                published_at = EXCLUDED.published_at,
                cached_at = EXCLUDED.cached_at
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
        cur.close()


def get_cached_article(url: str, ttl_hours: int = 24) -> Optional[dict]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM article_cache
            WHERE url_hash = %s
              AND (EXTRACT(EPOCH FROM NOW())::integer - cached_at) < %s
            """,
            (url_hash(url), ttl_hours * 3600),
        )
        row = cur.fetchone()
        cur.close()
        if row:
            return dict(row)
        return None


def save_propagation_events(url_hash_val: str, events: list[dict]) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        for event in events:
            cur.execute(
                """
                INSERT INTO propagation_events
                (url_hash, claim_id, source_domain, source_name, publish_time, role, altered, cached_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
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
        cur.close()


def save_source_graph(nodes: list[dict], edges: list[dict]) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        for node in nodes:
            cur.execute(
                """
                INSERT INTO source_nodes
                (domain, name, trust_score, total_articles, credibility_avg)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (domain) DO UPDATE SET
                    name = EXCLUDED.name,
                    trust_score = EXCLUDED.trust_score,
                    total_articles = EXCLUDED.total_articles,
                    credibility_avg = EXCLUDED.credibility_avg
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
            cur.execute(
                """
                INSERT INTO source_edges
                (source_domain, target_domain, claim_id, copied_at, altered)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_domain, target_domain, claim_id) DO UPDATE SET
                    copied_at = EXCLUDED.copied_at,
                    altered = EXCLUDED.altered
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
        cur.close()


def get_source_graph() -> dict:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM source_nodes")
        nodes = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT * FROM source_edges")
        edges = [dict(r) for r in cur.fetchall()]
        cur.close()
        return {"nodes": nodes, "edges": edges}
