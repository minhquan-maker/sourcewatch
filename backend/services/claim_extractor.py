import json
import logging
import time
from typing import Optional

from google import genai

from .config import settings
from .db import chromadb_client

logger = logging.getLogger(__name__)


def _retry_generate(client, model, contents, max_retries=5):
    """Call Gemini with exponential backoff retry on 503/429 errors."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model, contents=contents)
            return response
        except Exception as e:
            err_str = str(e)
            is_retryable = "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str or "RESOURCE_EXHAUSTED" in err_str
            if is_retryable and attempt < max_retries - 1:
                wait = (2 ** attempt) * 3
                logger.warning(f"Gemini attempt {attempt+1} failed (retryable), waiting {wait}s: {err_str[:100]}")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Exhausted retries")

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


SYSTEM_PROMPT = """Bạn là một trợ lý phân tích tin tức. Từ bài báo được cung cấp, hãy trích xuất 3-7 phát biểu quan trọng nhất (claims) — những tuyên bố có thể kiểm chứng được.

Mỗi claim phải là một câu khẳng định rõ ràng, có thể kiểm chứng được bằng fact-check.
Trả lời CHỈở định dạng JSON array, không có gì khác.
Ví dụ: [{"id": 1, "text": "Lũ lụt tại Đà Nẵng gây thiệt hại 200 tỷ đồng"}]"""


async def extract_claims(article_text: str) -> list[dict]:
    if not article_text or len(article_text) < 50:
        raise ValueError("Article text too short to extract claims")

    text_to_analyze = article_text[: 8 * 1024]

    client = _get_client()
    try:
        response = _retry_generate(
            client,
            "gemini-3.5-flash",
            f"{SYSTEM_PROMPT}\n\nBài báo:\n{text_to_analyze}",
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        claims = json.loads(raw)
    except Exception as e:
        err_str = str(e)
        is_quota = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
        if is_quota:
            logger.warning(f"Gemini quota exceeded, using fallback mock claims: {err_str[:80]}")
            claims = _fallback_claims(article_text)
        else:
            logger.error(f"Gemini claim extraction failed: {e}")
            raise ValueError(f"Failed to extract claims: {e}")

    if not isinstance(claims, list):
        raise ValueError("Invalid claims format from Gemini")

    for i, claim in enumerate(claims):
        claim["id"] = claim.get("id", i + 1)

    try:
        chromadb_client.add_claims(claims)
    except Exception as e:
        logger.warning(f"Failed to index claims in ChromaDB: {e}")

    return claims


def _fallback_claims(article_text: str) -> list[dict]:
    """Generate mock claims from article text when API is unavailable."""
    sentences = [s.strip() for s in article_text.split(".") if len(s.strip()) > 20]
    claim_candidates = []
    for s in sentences[:7]:
        clean = s.strip().rstrip(".,;:!?")
        if 30 <= len(clean) <= 300:
            claim_candidates.append(clean)

    claims = []
    for i, text in enumerate(claim_candidates[:5]):
        claims.append({
            "id": i + 1,
            "text": text,
            "source": "fallback",
        })
    return claims
