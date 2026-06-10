import json
import logging
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)

SOURCES_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "vietnamese_sources.json"


def _load_sources() -> dict:
    try:
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            sources = json.load(f)
            return {s["domain"]: s["trust_score"] for s in sources}
    except Exception:
        return {}


def calculate_score(
    article: dict, claims: list[dict], propagation: dict, fact_checks: list[dict]
) -> dict:
    source_score = _calc_source_reputation(article)
    consistency_score = _calc_claim_consistency(claims, fact_checks)
    amplification_score = _calc_amplification_pattern(propagation)

    total = round(
        source_score * 0.4 + consistency_score * 0.3 + amplification_score * 0.3, 1
    )

    label = _score_label(total)

    return {
        "total": total,
        "label": label,
        "breakdown": {
            "source_reputation": round(source_score, 1),
            "claim_consistency": round(consistency_score, 1),
            "amplification_pattern": round(amplification_score, 1),
        },
    }


def _score_label(total: float) -> str:
    if total >= 8.0:
        return "Verified"
    elif total >= 6.5:
        return "Credible"
    elif total >= 5.0:
        return "Mixed"
    elif total >= 3.0:
        return "Suspicious"
    else:
        return "Disputed"


def _calc_source_reputation(article: dict) -> float:
    scores = _load_sources()
    domain = article.get("source", "")
    if domain.startswith("http"):
        from urllib.parse import urlparse

        domain = urlparse(domain).netloc
    return scores.get(domain, 5.0)


def _calc_claim_consistency(claims: list[dict], fact_checks: list[dict]) -> float:
    if not fact_checks:
        return 5.0

    status_weights = {
        "verified": 10.0,
        "unverified": 5.0,
        "disputed": 3.0,
        "false": 1.0,
    }
    total = sum(status_weights.get(fc["status"], 5.0) for fc in fact_checks)
    return total / len(fact_checks)


def _calc_amplification_pattern(propagation: dict) -> float:
    timeline = propagation.get("timeline", [])
    if not timeline:
        return 5.0

    scores = _load_sources()
    low_trust_count = 0
    total_count = len(timeline)

    for event in timeline:
        domain = event.get("source_domain", "")
        score = scores.get(domain, 5.0)
        if score < 5.0:
            low_trust_count += 1

    if total_count == 0:
        return 7.0

    low_trust_ratio = low_trust_count / total_count
    base_score = 7.0
    penalty = low_trust_ratio * 4.0
    return max(1.0, round(base_score - penalty, 1))
