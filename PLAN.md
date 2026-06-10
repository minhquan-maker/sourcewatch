# SourceWatch — Build Plan

## ⚠️ Corrections from Research (2026)

| # | Issue | Fix Applied |
|---|-------|-------------|
| 1 | Google Custom Search API **closed to new customers**, discontinued Jan 2027 | Replaced with **Playwright scraping** of VN news sites directly |
| 2 | Package `google-generativeai` **deprecated** | Changed to **`google-genai`** |
| 3 | Model name "Gemini 2.0 Flash" **does not exist** | Changed to **`gemini-3.5-flash`** (free tier) |
| 4 | Neo4j Aura has **storage pricing** ($/GB/month) | Removed Neo4j — use **SQLite adjacency list** for graph |
| 5 | Google Fact Check API not fully free | Primary: **custom fact-check DB**; API as supplementary only |
| 6 | Plan over-engineered for MVP | Simplified:1 DB (SQLite), 1 vector store (ChromaDB), no graph DB |

---

## Phases Overview

| Phase | Contents | Estimated Time |
|-------|----------|----------------|
| **Phase 1** | Project setup, folder structure, basic frontend + backend skeleton | 1-2 days |
| **Phase 2** | Article fetching (Playwright) + basic display |2-3 days |
| **Phase 3** | Claim extraction (Gemini 3.5 Flash) | 1-2 days |
| **Phase 4** | Propagation tracking (Playwright scraping + SQLite) | 2-3 days |
| **Phase 5** | Source network graph (SQLite adjacency list + D3.js) | 2-3 days |
| **Phase 6** | Fact-check cross-reference (custom DB + ChromaDB) | 1-2 days |
| **Phase 7** | Credibility scoring + frontend polish | 2-3 days |
| **Phase 8** | Deployment (Vercel + Render) + testing | 1-2 days |

**Total: ~12-18 days** (parallelize where possible)

---

## Directory Structure

```
SourceWatch/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt
│   ├── routers/
│   │   ├── analyze.py          # POST /analyze — main analysis endpoint
│   │   └── health.py           # GET /health
│   ├── services/
│   │   ├── fetcher.py          # Playwright article fetching
│   │   ├── claim_extractor.py  # Gemini3.5 Flash claim extraction
│   │   ├── propagation.py      # VN news scraping + timeline builder
│   │   ├── fact_checker.py     # Custom DB + ChromaDB similarity search
│   │   └── scorer.py           # Credibility scoring logic
│   ├── db/
│   │   ├── sqlite_db.py        # SQLite: timeline + source graph + cache
│   │   └── chromadb_client.py  # ChromaDB: claim embeddings
│   ├── config.py               # API keys, settings
│   └── utils.py                # Helpers (rate limiting, caching, etc.)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   │   ├── InputBar.jsx
│   │   │   ├── Timeline.jsx
│   │   │   ├── SourceGraph.jsx
│   │   │   ├── ScoreCard.jsx
│   │   │   └── FactCheckBadge.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── styles/
│   │       └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── data/
│   ├── vietnamese_sources.json
│   └── fact_check_db.json
├── tests/
│   ├── test_fetcher.py
│   ├── test_claim_extractor.py
│   └── test_scorer.py
├── CLAUDE.md
├── README.md
└── .env.example
```

---

## Tech Stack

### Frontend
- **Vite** + **React 19** — build tool + UI framework
- **Tailwind CSS v4** — styling
- **D3.js** — timeline + network graph visualization
- **Axios** — HTTP client
- **Vercel** — hosting ($0)

### Backend
- **FastAPI** — Python web framework
- **Uvicorn** — ASGI server
- **Playwright** — headless browser for article + VN news scraping
- **Render** — hosting ($0 free tier)

### AI
- **Gemini 3.5 Flash** — claim extraction (free tier, unlimited requests)
- **`google-genai`** — Python SDK (NOT `google-generativeai`)

### Database
- **SQLite** — propagation timeline + source graph adjacency list + cache (local file)
- **ChromaDB** — claim vector embeddings (local)

### External APIs
- **Google Fact Check Claim Search API** — supplementary fact-check source (free quota)
- No Google Custom Search API (deprecated Jan 2027)

### Utilities
- **httpx** — async HTTP client
- **python-dotenv** — env variable management
- **pydantic** — data validation
- **beautifulsoup4** — HTML parsing fallback when Playwright blocked

---

## API Design

### `POST /analyze`

**Input:**
```json
{
  "url": "https://vnexpress.net/article/..."
}
```

**Output:**
```json
{
  "article": {
    "title": "...",
    "source": "VnExpress",
    "published_at": "2026-06-10T08:00:00Z",
    "url": "..."
  },
  "claims": [
    { "id": 1, "text": "Lũ lụt gây thiệt hại 200 tỷ tại Đà Nẵng" }
  ],
  "propagation": {
    "timeline": [
      { "source": "VnExpress", "time": "08:00", "role": "origin" },
      { "source": "Dân Trí", "time": "09:30", "role": "copy", "altered": true },
      { "source": "Zing", "time": "10:15", "role": "copy" }
    ]
  },
  "source_network": {
    "nodes": [...],
    "edges": [...]
  },
  "fact_checks": [
    { "claim": "...", "status": "unverified", "source": "Custom DB" }
  ],
  "credibility_score": {
    "total": 7.2,
    "breakdown": {
      "source_reputation": 8.0,
      "claim_consistency": 6.5,
      "amplification_pattern": 7.0
    }
  }
}
```

### `GET /health`
Returns `{ "status": "ok", "version": "1.0.0" }`

---

## Workflow Step-by-Step

### Step 1: Project Setup
```bash
# Backend
cd backend
pip install fastapi uvicorn playwright chromadb google-genai httpx python-dotenv pydantic beautifulsoup4 lxml
playwright install chromium

# Frontend
cd frontend
npm create vite@latest . -- --template react
npm install axios d3 tailwindcss postcss autoprefixer
```

### Step 2: Basic Backend Skeleton
- `main.py` with FastAPI app
- `/health` endpoint
- `config.py` with API keys from `.env`
- Test: `uvicorn main:app --reload --port 8000`

### Step 3: Article Fetcher
- `services/fetcher.py` — Playwright fetches URL, extracts title/text/author/date
- Extract using article-specific selectors (meta tags, structured data)
- Handle errors: invalid URL, CAPTCHAs, blocked domains, timeouts
- Cache result in SQLite by URL hash (24h TTL)
- Fallback: use `requests` + BeautifulSoup if Playwright blocked

### Step 4: Claim Extractor
- `services/claim_extractor.py` — send article text to Gemini 3.5 Flash via `google-genai`
- Prompt: extract 3-7 factual claims, return as JSON array
- Store claims in ChromaDB for similarity search
- Handle rate limiting with retry + exponential backoff

### Step 5: Propagation Tracker
- `services/propagation.py` — for each claim, scrape top10 VN news sites with Playwright
- Per site: search query → extract article title, date, URL
- Parse results: extract source, URL, publish time
- Store timeline in SQLite: `propagation_events(url_hash, claim_id, source, time, role)`
- Role inference: earliest publish time = "origin", later = "copy", social media = "amplify"
- Cache all scraped results (24h per URL)

### Step 6: Source Network Graph
- `db/sqlite_db.py` — source graph stored as adjacency list in SQLite
- Table: `source_nodes(domain, trust_score, total_articles, credibility_avg)`
- Table: `source_edges(source_domain, target_domain, claim_id, copied_at, altered)`
- `services/propagation.py` creates/updates nodes and edges
- No Neo4j needed for MVP — graph traversal via SQL JOINs

### Step 7: Fact-Check Cross-Reference
- `services/fact_checker.py` — for each claim, search ChromaDB similarity against custom fact-check DB
- Search custom JSON DB: `data/fact_check_db.json` — pre-indexed Vietnamese claims
- Supplementary: Google Fact Check Claim Search API (claimreview)
- Return status: "verified", "unverified", "disputed", "false"
- Cache fact-check results (7d TTL)

### Step 8: Credibility Scorer
- `services/scorer.py` — composite score calculation
- `source_reputation`: pre-defined scores from `data/vietnamese_sources.json`
- `claim_consistency`: ChromaDB similarity score across sources reporting same claim
- `amplification_pattern`: low-trust pages amplifying? How fast?
- Total score: weighted average (40% source + 30% consistency + 30% amplification)

### Step 9: Frontend — Input Bar
- `components/InputBar.jsx` — text input for URL + "Analyze" button
- Loading state with progress indicator
- Error display (invalid URL, fetch failed, etc.)
- Call `POST /analyze` on submit

### Step 10: Frontend — Timeline Display
- `components/Timeline.jsx` — vertical timeline from propagation data
- Show source logo/name, time, role (origin/copy/amplify)
- Highlight altered claims in yellow
- Highlight low-credibility sources in red

### Step 11: Frontend — Source Network Graph
- `components/SourceGraph.jsx` — D3.js force-directed graph
- Nodes: circles sized by article count, colored by trust score
- Edges: arrows showing propagation direction
- Interactive: hover for details, click to open source

### Step 12: Frontend — Score Card
- `components/ScoreCard.jsx` — circular gauge showing total score 0-10
- Breakdown bars for each sub-score
- Color coding: green (7+), yellow (4-6), red (<4)

### Step 13: Frontend — Fact-Check Badge
- `components/FactCheckBadge.jsx` — small badge next to each claim
- Status: ✅ Verified, ❓ Unverified, ⚠️ Disputed, ❌ False
- Link to external fact-check source if available

### Step 14: Polish + Error Handling
- Consistent Tailwind styling across all components
- Responsive design (mobile-friendly)
- Error states: API down, rate limited, invalid URL, timeout
- Empty states: no results found
- Loading skeletons (not just spinner)

### Step 15: Deployment
- Backend: `git push to GitHub` → Render auto-deploys
- Frontend: `vercel deploy`
- Set environment variables in Render: `GEMINI_API_KEY`
- Custom domain: `sourcewatch.vn` (optional, use `.vercel.app` first)
- Test end-to-end: paste VnExpress URL → verify results display

---

## Data Files

### `data/vietnamese_sources.json`
```json
[
  { "domain": "vnexpress.net", "name": "VnExpress", "trust_score": 8.0, "type": "major" },
  { "domain": "dantri.com.vn", "name": "Dân Trí", "trust_score": 7.5, "type": "major" },
  { "domain": "zing.vn", "name": "Zing News", "trust_score": 7.0, "type": "major" },
  { "domain": "tuoitre.vn", "name": "Tuổi Trẻ", "trust_score": 8.0, "type": "major" },
  { "domain": "vov.vn", "name": "VOV", "trust_score": 8.5, "type": "gov" },
  { "domain": "vtv.vn", "name": "VTV", "trust_score": 8.5, "type": "gov" },
  { "domain": "laodong.vn", "name": "Lao Động", "trust_score": 7.0, "type": "major" },
  { "domain": "thanhnien.vn", "name": "Thanh Niên", "trust_score": 7.5, "type": "major" },
  { "domain": "tienphong.vn", "name": "Tiền Phong", "trust_score": 7.0, "type": "major" },
  { "domain": "nguoiduatin.vn", "name": "Người Lao Động", "trust_score": 6.5, "type": "major" }
]
```

### `data/fact_check_db.json`
Pre-indexed fact-checks from Vietnamese sources. Format:
```json
[
  {
    "claim": "...",
    "verdict": "false",
    "source": "VnExpress thật sự",
    "url": "...",
    "date": "2026-01-15"
  }
]
```

---

## Rate Limits & Cost Management

| API / Service | Free Tier | Risk | Mitigation |
|--------------|-----------|------|------------|
| Gemini 3.5 Flash | Unlimited (free) | None | Cache claim embeddings |
| Playwright scraping | Unlimited | News sites may block | Cache 24h, rotate user-agents, respect robots.txt |
| Google Fact Check API | Limited free quota | Hit limit | Cache results 7d, use custom DB as primary |
| Render | 750h/month | Sleeps after 15min idle | Keep-alive ping or upgrade to paid |
| ChromaDB | Unlimited (local) | None | Local storage |
| SQLite | Unlimited (local) | None | Local file |

---

## Environment Variables (`.env.example`)

```
# Gemini
GEMINI_API_KEY=your_gemini_api_key

# Google Fact Check (supplementary)
GOOGLE_FACT_CHECK_API_KEY=your_api_key

# Database
DATABASE_PATH=./data/sourcewatch.db
CHROMADB_PATH=./data/chromadb

# App
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## Testing Strategy

| Test | File | What to test |
|------|------|-------------|
| Fetcher | `tests/test_fetcher.py` | Playwright fetches VnExpress URL, extracts title/text correctly |
| Claim Extractor | `tests/test_claim_extractor.py` | Gemini returns 3-7 claims from sample article |
| Propagation | `tests/test_propagation.py` | Scraping returns results for known claim |
| Scorer | `tests/test_scorer.py` | Known credible story scores 7+, known fake scores <4 |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Playwright blocked by news site | Critical | Fallback to `requests` + BeautifulSoup; cache aggressively |
| Gemini rate limit | Low | Free tier is generous; cache embeddings |
| Vietnamese news site changes HTML | Medium | Add fallback selectors, log broken fetchers |
| Vietnamese text encoding | Low | Ensure UTF-8 everywhere, test with VnExpress articles |
| Render sleep (free tier) | Medium | Upgrade to paid or add keep-alive ping |
| ChromaDB data loss | Low | Local file; backup periodically |
