import asyncio
import logging
import re
from urllib.parse import urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .config import settings
from .db import sqlite_db
from .utils import url_hash, retry

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def fetch_article(url: str) -> dict:
    cached = sqlite_db.get_cached_article(url)
    if cached:
        logger.info(f"Cache hit for {url}")
        return {
            "title": cached["title"],
            "text": cached["text"],
            "source": cached["source"],
            "author": cached["author"],
            "published_at": cached["published_at"],
            "url": url,
 }

    article = await asyncio.to_thread(_fetch_with_playwright, url)
    if not article or not article.get("text"):
        article = _fetch_with_requests(url)

    if not article or not article.get("text"):
        raise ValueError(f"Could not fetch article from {url}")

    sqlite_db.cache_article(url, article)
    return {**article, "url": url}


def _fetch_with_playwright(url: str) -> Optional[dict]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(settings.playwright_timeout)
            page.set_extra_http_headers(dict(HEADERS))
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            title = page.title()
            text = _extract_article_text(page.content())
            source = urlparse(url).netloc
            author = _extract_author(page)
            published_at = _extract_published_at(page)

            browser.close()
            return {
                "title": title,
                "text": text,
                "source": source,
                "author": author,
                "published_at": published_at,
            }
    except Exception as e:
        logger.warning(f"Playwright fetch failed for {url}: {e}")
        return None


def _fetch_with_requests(url: str) -> Optional[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"

        soup = BeautifulSoup(resp.text, "lxml")
        title = soup.title.string if soup.title else ""
        text = _extract_article_text(str(soup))
        source = urlparse(url).netloc
        author = _extract_author_soup(soup)
        published_at = _extract_published_at_soup(soup)

        return {
            "title": title,
            "text": text,
            "source": source,
            "author": author,
            "published_at": published_at,
        }
    except Exception as e:
        logger.warning(f"Requests fetch failed for {url}: {e}")
        return None


def _extract_article_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    article = soup.find("article") or soup.find("div", class_=re.compile(r"article|content|post", re.I))
    if article:
        return article.get_text(separator=" ", strip=True)

    main = soup.find("main") or soup.find("div", class_=re.compile(r"main", re.I))
    if main:
        return main.get_text(separator=" ", strip=True)

    return soup.get_text(separator=" ", strip=True)[:10000]


def _extract_author(page) -> str:
    selectors = [
        '[rel="author"]',
        '[itemprop="author"]',
        ".author",
        ".byline",
        ".writer",
        "a[href*='/author/']",
    ]
    for sel in selectors:
        el = page.query_selector(sel)
        if el:
            return el.inner_text().strip()
    return ""


def _extract_published_at(page) -> str:
    selectors = [
        '[itemprop="datePublished"]',
        'time[datetime]',
        ".published",
        ".date",
        ".timestamp",
    ]
    for sel in selectors:
        el = page.query_selector(sel)
        if el:
            return el.get_attribute("datetime") or el.inner_text().strip()
    return ""


def _extract_author_soup(soup: BeautifulSoup) -> str:
    for meta in soup.find_all("meta", attrs={"rel": "author"}):
        return meta.get("content", "")
    for tag in soup.find_all(class_=re.compile(r"author|byline", re.I)):
        return tag.get_text(strip=True)
    return ""


def _extract_published_at_soup(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"itemprop": "datePublished"})
    if meta:
        return meta.get("content", "")
    time_tag = soup.find("time")
    if time_tag:
        return time_tag.get("datetime", "") or time_tag.get_text(strip=True)
    return ""
