import asyncio
import json
import logging
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from services import fetcher, claim_extractor, propagation, fact_checker, scorer

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
    stage: str = "done"


class IndexResponse(BaseModel):
    status: str
    articles_indexed: int


async def _run_analysis(url: str):
    """Run the full analysis pipeline and return the result."""
    # Stage 1: Fetch
    article = await fetcher.fetch_article(url)

    # Stage 2: Extract claims
    claims = await claim_extractor.extract_claims(article["text"])

    # Stage 3: Track propagation
    propagation_data = await propagation.track_propagation(url, claims)

    # Stage 4: Fact check
    fact_checks = await fact_checker.check_claims(claims)

    # Stage 5: Score
    score = scorer.calculate_score(article, claims, propagation_data, fact_checks)

    return {
        "article": article,
        "claims": claims,
        "propagation": propagation_data,
        "source_network": propagation_data.get("source_network", {"nodes": [], "edges": []}),
        "fact_checks": fact_checks,
        "credibility_score": score,
    }


@router.post("/analyze")
async def analyze_url(req: AnalyzeRequest):
    """Main analysis endpoint with SSE progress streaming."""
    logger.info(f"Analyzing URL: {req.url}")

    async def event_stream():
        try:
            # Stage 1: Fetch
            yield f"data: {json.dumps({'stage': 'fetching', 'message': 'Fetching article...'})}\n\n"
            article = await fetcher.fetch_article(req.url)

            # Stage 2: Extract claims
            yield f"data: {json.dumps({'stage': 'claims', 'message': 'Extracting claims...'})}\n\n"
            claims = await claim_extractor.extract_claims(article["text"])

            # Stage 3: Track propagation
            yield f"data: {json.dumps({'stage': 'propagation', 'message': 'Tracking propagation...'})}\n\n"
            propagation_data = await propagation.track_propagation(req.url, claims)

            # Stage 4: Fact check
            yield f"data: {json.dumps({'stage': 'factcheck', 'message': 'Cross-referencing facts...'})}\n\n"
            fact_checks = await fact_checker.check_claims(claims)

            # Stage 5: Score
            yield f"data: {json.dumps({'stage': 'scoring', 'message': 'Calculating credibility score...'})}\n\n"
            score = scorer.calculate_score(article, claims, propagation_data, fact_checks)

            # Done — send full result
            result = {
                "article": article,
                "claims": claims,
                "propagation": propagation_data,
                "source_network": propagation_data.get("source_network", {"nodes": [], "edges": []}),
                "fact_checks": fact_checks,
                "credibility_score": score,
                "stage": "done",
            }
            yield f"data: {json.dumps({'stage': 'done', 'result': result})}\n\n"

        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'stage': 'error', 'message': 'Analysis timed out after 120 seconds. Try a shorter article.'})}\n\n"
        except ValueError as e:
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)})}\n\n"
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            yield f"data: {json.dumps({'stage': 'error', 'message': f'Analysis failed: {e}'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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