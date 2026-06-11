import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config import settings
from db import sqlite_db
from db import chromadb_client
from utils import url_hash, rate_limit

logger = logging.getLogger(__name__)

TRACKED_SOURCES_FILE = settings.chromadb_path.parent / "vietnamese_sources.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


def _load_sources() -> list[dict]:
    with open(TRACKED_SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@rate_limit(calls=3, period=5)
def _scrape_homepage_articles(source: dict) -> list[dict]:
    """Scrape latest articles from a news source homepage."""
    domain = source["domain"]
    articles = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
            page = browser.new_page()
            page.set_default_timeout(15000)
            page.set_extra_http_headers(dict(HEADERS))
            page.goto(f"https://{domain}/", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)

            links = page.query_selector_all("a[href]")
            seen_urls = set()

            for link in links:
                href = link.get_attribute("href") or ""
                if not href:
                    continue

                # Normalize to full URL
                if href.startswith("/"):
                    full_url = f"https://{domain}{href}"
                elif href.startswith("http"):
                    full_url = href
                else:
                    continue

                # Must be from same domain
                if domain not in full_url:
                    continue
                if full_url in seen_urls:
                    continue
                if any(skip in full_url for skip in ["/tag/", "/author/", "/search", "#"]):
                    continue
                if "/20" not in full_url and ".htm" not in full_url:
                    continue

                seen_urls.add(full_url)
                # Try nested elements first, fallback to link's own text
                title_el = link.query_selector("h1, h2, h3, h4, span, div")
                if title_el:
                    title = title_el.inner_text().strip()
                else:
                    title = link.inner_text().strip()

                if len(title) < 10:
                    continue

                articles.append({
                    "url": full_url,
                    "title": title,
                    "source_domain": domain,
                    "source_name": source["name"],
                })

                if len(articles) >= 15:
                    break

            browser.close()
    except Exception as e:
        logger.warning(f"Failed to scrape homepage {domain}: {e}")

    return articles


def _fetch_article_text(url: str) -> Optional[str]:
    """Fetch and extract article text from a URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        for tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        article = soup.find("article") or soup.find("div", class_=lambda c: c and ("content" in c or "article" in c))
        if article:
            return article.get_text(separator=" ", strip=True)[:5000]
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        logger.warning(f"Failed to fetch article {url}: {e}")
        return None


async def index_sources() -> int:
    """Pre-index articles from all tracked sources into ChromaDB."""
    sources = _load_sources()
    total_indexed = 0

    for source in sources:
        logger.info(f"Indexing {source['name']}...")
        homepage_articles = await asyncio.to_thread(_scrape_homepage_articles, source)

        for article in homepage_articles:
            text = await asyncio.to_thread(_fetch_article_text, article["url"])
            if not text or len(text) < 100:
                continue

            try:
                chromadb_client.index_article(
                    url=article["url"],
                    title=article["title"],
                    text=text,
                    source_domain=article["source_domain"],
                    source_name=article["source_name"],
                )
                total_indexed += 1
            except Exception as e:
                logger.warning(f"Failed to index {article['url']}: {e}")

        time.sleep(settings.scrape_delay)

    logger.info(f"Indexed {total_indexed} articles total")
    return total_indexed


async def track_propagation(original_url: str, claims: list[dict]) -> dict:
    if not claims:
        return {"timeline": [], "source_network": {"nodes": [], "edges": []}}

    sources = _load_sources()
    source_map = {s["domain"]: s for s in sources}

    all_events = []
    all_nodes = []
    all_edges = []
    seen_domains = {}

    for claim in claims:
        claim_text = claim["text"]
        logger.info(f"Searching propagation for claim: {claim_text[:80]}...")

        similar = chromadb_client.search_similar_articles(claim_text, n=10)

        for article in similar:
            domain = article.get("source_domain", "")
            if not domain:
                continue

            if domain not in seen_domains:
                source_info = source_map.get(domain, {})
                seen_domains[domain] = {
                    "domain": domain,
                    "name": article.get("source_name", source_info.get("name", domain)),
                    "trust_score": source_info.get("trust_score", 5.0),
                    "total_articles": 1,
                }
                all_nodes.append(seen_domains[domain])
            else:
                seen_domains[domain]["total_articles"] += 1

            all_events.append({
                "claim_id": claim["id"],
                "source_domain": domain,
                "source_name": article.get("source_name", ""),
                "publish_time": article.get("published_at", ""),
                "role": "copy",
                "altered": False,
            })

            all_edges.append({
                "source_domain": original_url,
                "target_domain": domain,
                "claim_id": claim["id"],
                "altered": False,
            })

    url_hash_val = url_hash(original_url)
    if all_events:
        sqlite_db.save_propagation_events(url_hash_val, all_events)
    if all_nodes or all_edges:
        sqlite_db.save_source_graph(all_nodes, all_edges)

    timeline = [
        {
            "source": e["source_name"],
            "source_domain": e["source_domain"],
            "time": e["publish_time"],
            "role": e["role"],
            "altered": e.get("altered", False),
        }
        for e in all_events
    ]

    return {
        "timeline": timeline,
        "source_network": {"nodes": all_nodes, "edges": all_edges},
    }
