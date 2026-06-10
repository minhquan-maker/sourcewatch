# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SourceWatch is a Vietnamese news credibility analyzer. User pastes a news URL → backend fetches article → extracts claims → tracks propagation across VN news sources → returns timeline, source graph, and credibility score.

**Stack:** Vite + React + Tailwind v4 (frontend) | FastAPI + Playwright (backend) | Gemini 3.5 Flash (AI) | SQLite + ChromaDB (data)

**Design:** Dark-only forensics lab aesthetic. Electric cyan accent (#22d3ee) on deep navy-black (#080b12). Fonts: Syne (display) + DM Sans (body) + JetBrains Mono (data). Refer to `DESIGN.md` for full design spec.

## Dev Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend
python -m pytest tests/ -v
```

## Architecture

```
User paste URL
     ↓
POST /analyze → routers/analyze.py
     ↓
services/fetcher.py         → Playwright fetch article HTML (BeautifulSoup fallback)
services/claim_extractor.py → Gemini 3.5 Flash extract claims (google-genai SDK)
services/propagation.py     → Scrape VN news sites → build timeline
services/fact_checker.py    → ChromaDB similarity + custom fact-check DB
services/scorer.py          → Composite credibility score
     ↓
db/sqlite_db.py → timeline + source graph adjacency list + URL cache
db/chromadb_client.py  → claim embeddings + similarity search
     ↓
Frontend renders: Timeline + D3 source graph + Score card + Fact-check badges
```

## Key Files

| File | Role |
|------|------|
| `backend/main.py` | FastAPI app, routes registration |
| `backend/routers/analyze.py` | `POST /analyze` — orchestrates all services |
| `backend/services/fetcher.py` | Playwright article fetching + BeautifulSoup fallback |
| `backend/services/claim_extractor.py` | Gemini 3.5 Flash via `google-genai` SDK |
| `backend/services/propagation.py` | Scrape VN news sites, build timeline |
| `backend/services/fact_checker.py` | ChromaDB similarity + custom JSON DB |
| `backend/services/scorer.py` | Credibility scoring (40% source + 30% consistency + 30% amplification) |
| `backend/db/sqlite_db.py` | SQLite: timeline, source graph adjacency list, URL cache |
| `backend/db/chromadb_client.py` | ChromaDB: claim embeddings + similarity search |
| `frontend/src/components/SourceGraph.jsx` | D3.js force-directed graph |
| `frontend/src/components/ScoreCard.jsx` | SVG circular gauge, breakdown bars |
| `frontend/src/components/Timeline.jsx` | Vertical timeline with role badges |
| `frontend/src/components/FactCheckBadge.jsx` | Verified/Unverified/Disputed/False badges |
| `data/vietnamese_sources.json` | 10 tracked VN news sources + trust scores |
| `data/fact_check_db.json` | Pre-indexed Vietnamese fact-checks |
| `DESIGN.md` | Full design system — colors, typography, layout, animations |

## Design Conventions

- **Dark-only** — no light mode toggle. Body background always `#080b12`.
- **Color tokens** defined in `DESIGN.md` — use semantic names (accent, verified, disputed, false)
- **Fonts:** Syne (display/headings), DM Sans (body), JetBrains Mono (scores/timestamps)
- **Animations:** fade-up stagger on mount, draw-line for graph edges, pulse-glow for accent elements
- **Icons:** `lucide-react` for all icons (see DESIGN.md icon table)
- **Tailwind v4** — colors via CSS `@theme` variables, not default palette

## Critical Conventions

- **Package name:** `google-genai` (NOT `google-generativeai`)
- **Model name:** `gemini-3.5-flash` (NOT `gemini-2.0-flash`)
- **No Neo4j** — source graph stored as SQLite adjacency list
- **No Google Custom Search API** — discontinued Jan 2027, use Playwright scraping instead
- **Cache everything** — propagate results 24h, fact-check results 7d
- **UTF-8 everywhere** — Vietnamese text encoding is critical
- **Respect robots.txt** — add delay between scrapes, rotate user-agents

## Environment Variables

```
GEMINI_API_KEY
GOOGLE_FACT_CHECK_API_KEY  (supplementary only)
DATABASE_PATH=./data/sourcewatch.db
CHROMADB_PATH=./data/chromadb
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

## References

- [Gemini API Docs](https://ai.google.dev/)
- [Playwright Python](https://playwright.dev/python/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind v4](https://tailwindcss.com/docs/customizing-colors)
- [D3.js Force Graph](https://d3js.org/)
