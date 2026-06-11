# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SourceWatch is a Vietnamese news credibility analyzer. User pastes a news URL → backend fetches article → extracts claims → tracks propagation across VN news sources → returns timeline, source graph, and credibility score.

**Stack:** Vite + React 19 + Tailwind v4 (frontend) | FastAPI + Playwright (backend) | Gemini 3.5 Flash (AI) | SQLite + ChromaDB (data)

**Design:** Dark-only forensics lab aesthetic. Electric cyan accent (#22d3ee) on deep navy-black (#080b12). Fonts: Syne (display) + DM Sans (body) + JetBrains Mono (data/mono). Full spec in `DESIGN.md`.

## Dev Commands

```bash
# Setup (first time)
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# Backend
cd backend && pip install -r requirements.txt && playwright install chromium
uvicorn main:app --reload --port 8000

# Frontend (proxies /analyze, /health, /index to backend on port 8000 via vite.config.js)
cd frontend && npm install && npm run dev

# Run a single test
PYTHONPATH=backend python3 -m pytest backend/tests/test_scorer.py -v

# Run all tests
PYTHONPATH=backend python3 -m pytest backend/tests/ -v
```

## Architecture

```
User paste URL
     ↓
POST /analyze → routers/analyze.py
     ↓
fetcher.fetch_article()     → Playwright (primary) → requests+BeautifulSoup (fallback)
     ↓
claim_extractor.extract_claims() → Gemini 3.5 Flash → _fallback_claims() on quota
     ↓
propagation.track_propagation()  → ChromaDB search_similar_articles() → timeline + source graph
     ↓
fact_checker.check_claims()      → ChromaDB search_fact_checks() → JSON DB fallback
     ↓
scorer.calculate_score()         → 40% source + 30% consistency + 30% amplification
     ↓
SQLite (article_cache, propagation_events, source_nodes, source_edges)
ChromaDB (claims, fact_checks, articles collections)
     ↓
Frontend: ScoreCard + Timeline + SourceGraph (D3) + FactCheckBadge grid
```

## Key Files

| File | Role |
|------|------|
| `backend/main.py` | FastAPI app, CORS middleware, route registration |
| `backend/routers/analyze.py` | `POST /analyze`, `POST /index` — orchestrates all services |
| `backend/routers/health.py` | `GET /health` |
| `backend/services/fetcher.py` | Playwright → requests fallback, article extraction + caching |
| `backend/services/claim_extractor.py` | Gemini 3.5 Flash + custom `_retry_generate()` (503/429 backoff) + `_fallback_claims()` |
| `backend/services/propagation.py` | `_scrape_homepage_articles()`, `index_sources()`, `track_propagation()` |
| `backend/services/fact_checker.py` | ChromaDB primary + JSON DB keyword fallback via `_claim_matches()` |
| `backend/services/scorer.py` | Composite score: 40% source rep + 30% claim consistency + 30% amplification |
| `backend/db/sqlite_db.py` | article_cache (24h TTL), propagation_events, source_nodes, source_edges |
| `backend/db/chromadb_client.py` | claims, fact_checks, articles collections; singleton client |
| `backend/config.py` | Pydantic Settings — all env vars, `DATABASE_PATH`, `CHROMADB_PATH`, `playwright_timeout`, `scrape_delay` |
| `backend/utils.py` | `url_hash()`, `rate_limit()` decorator, `retry()` decorator, `safe_get()` |
| `frontend/src/services/api.js` | `analyzeUrl()`, `healthCheck()`, `indexSources()` — uses Vite proxy (no hardcoded baseURL) |
| `frontend/src/styles/index.css` | Tailwind v4 with `@import "tailwindcss"` + `@theme {}` block (no tailwind.config.js) |
| `data/vietnamese_sources.json` | 10 tracked VN news sources with domain, name, trust_score, type |
| `data/fact_check_db.json` | Pre-indexed Vietnamese fact-checks with verdict, claim, source, url, date |

## Frontend API Integration

The frontend uses Vite's dev server proxy (configured in `vite.config.js`) to forward `/analyze`, `/health`, `/index` to `http://localhost:8000`. No `VITE_BACKEND_URL` env var is needed for local dev. The `api.js` uses `baseURL: ""` (relative path).

## Claim Extraction Behavior

- Sends first 8KB of article text to Gemini with a Vietnamese system prompt
- `_retry_generate()` retries 5× with exponential backoff on 503/429/UNAVAILABLE/RESOURCE_EXHAUSTED
- On 429 quota error: silently falls back to `_fallback_claims()` (splits article into sentences)
- Parses JSON from response, stripping markdown code fences if present
- Indexes claims into ChromaDB `claims` collection after extraction

## Propagation Flow

1. `POST /index` → `propagation.index_sources()` scrapes each tracked source homepage via Playwright, fetches article text via requests, indexes into ChromaDB `articles` collection
2. `track_propagation()` searches ChromaDB `articles` for each claim text, builds timeline events and source graph adjacency from results
3. All results persisted to SQLite

## Fact-Checker Behavior

- On every `check_claims()` call: re-indexes `fact_check_db.json` into ChromaDB `fact_checks`
- Primary: ChromaDB similarity search (top 3 results)
- Fallback: keyword overlap `_claim_matches()` — requires ≥3 overlapping words and >40% overlap ratio
- Returns `unverified` by default if no match

## Critical Conventions

- **Package name:** `google-genai` (NOT `google-generativeai`)
- **Model name:** `gemini-3.5-flash` (NOT `gemini-2.0-flash`)
- **No Neo4j** — source graph stored as SQLite adjacency list
- **No Google Custom Search API** — discontinued Jan 2027, use Playwright scraping
- **Cache strategy:** article_cache 24h, propagate results 24h, fact-check 7d
- **UTF-8 everywhere** — Vietnamese text encoding is critical
- **Respect robots.txt** — `scrape_delay` (1s default) between scrapes, rotate user-agents
- **Import style:** Always use absolute imports (from X), NOT `from backend.X` or `from .X`. The Dockerfile flattens `backend/` into `/app`, so all imports resolve from `/app` as root.
- **Dead config:** `google_fact_check_api_key` in `config.py` is defined but unused — do not implement Google Fact Check API integration (discontinued Jan 2027 per Critical Conventions).

## Environment Variables

```
GEMINI_API_KEY
DATABASE_PATH=./data/sourcewatch.db
CHROMADB_PATH=./data/chromadb
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
playwright_timeout=30000    # ms
scrape_delay=1.0            # seconds between scrapes
```

## Deployment Architecture

```
User → Vercel (frontend) → Render (backend) → Gemini API + ChromaDB + SQLite
```

- **Frontend**: Vercel (React 19 + Vite + Tailwind v4) — rewrites `/analyze`, `/health`, `/index` to Render via `vercel.json`
- **Backend**: Render Web Service (FastAPI + Playwright, port 8000) — persistent disk at `/data`
- **No CORS needed** — Vercel rewrite proxy bypasses CORS entirely
- **Index VN sources after deploy**: `curl -X POST https://your-render-url.onrender.com/index` (~5 min, ~150 articles)
- Full deploy guide in `DEPLOY.md`

## Design Conventions

- **Dark-only** — body background always `#080b12`. No light mode toggle.
- **Tailwind v4** — colors via CSS `@theme` variables, not default palette. Font families via `@layer utilities`.
- **Fonts:** Syne (display/headings), DM Sans (body), JetBrains Mono (scores/timestamps)
- **Icons:** `lucide-react` for all icons
- **Animations:** `animate-fade-up-N` (N=0-4), `animate-fade-in`, `animate-scale-in`, `animate-pulse-glow`, `animate-draw-line`
- **Color tokens:** `text-bg`, `text-surface`, `text-accent`, `text-verified`, `text-disputed`, `text-false`, `text-unverified`