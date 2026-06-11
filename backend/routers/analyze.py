import logging
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from .services import fetcher, claim_extractor, propagation, fact_checker, scorer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    url: str


class AnalyzeResponse(BaseModel):
    article: dict
    claims: list[dict]
    propagation: dict
    source_network: dict
    fact_checks: list[dict]
    credibility_score: dict


class IndexResponse(BaseModel):
    status: str
    articles_indexed: int


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_url(req: AnalyzeRequest):
    try:
        logger.info(f"Analyzing URL: {req.url}")

        article = await fetcher.fetch_article(req.url)
        claims = await claim_extractor.extract_claims(article["text"])
        propagation_data = await propagation.track_propagation(req.url, claims)
        fact_checks = await fact_checker.check_claims(claims)
        score = scorer.calculate_score(article, claims, propagation_data, fact_checks)

        return AnalyzeResponse(
            article=article,
            claims=claims,
            propagation=propagation_data,
            source_network=propagation_data.get("source_network", {"nodes": [], "edges": []}),
            fact_checks=fact_checks,
            credibility_score=score,
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index", response_model=IndexResponse)
async def index_sources():
    """Pre-index articles from all tracked Vietnamese news sources into ChromaDB."""
    try:
        logger.info("Starting article indexing...")
        count = await propagation.index_sources()
        return IndexResponse(status="ok", articles_indexed=count)
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
