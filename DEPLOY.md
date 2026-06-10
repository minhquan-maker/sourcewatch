# Deploying SourceWatch

## Architecture

```
User → Vercel (frontend) → Render (backend) → Gemini API + ChromaDB
```

- **Frontend**: Vercel (React + Vite, port 5173)
- **Backend**: Render Web Service (FastAPI, port 8000)
- **Database**: Render persistent disk (SQLite + ChromaDB)
- **AI**: Google Gemini 3.5 Flash via `google-genai` SDK

---

## Step 1: Deploy Backend to Render

### Option A — One-click from GitHub

1. Go to [render.com](https://render.com) → Connect your GitHub repo
2. Create a **Web Service**:
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Region**: Singapore
   - **Plan**: Starter ($7/mo)
3. Add environment variables:
   - `GEMINI_API_KEY` — your Google AI Studio key (starts with `AQ.` or `AIza.`)
   - `GOOGLE_FACT_CHECK_API_KEY` — optional, for extended fact-check
   - `DATABASE_PATH` = `/data/sourcewatch.db`
   - `CHROMADB_PATH` = `/data/chromadb`
   - `PYTHONPATH` = `/app`
   - `SCRAPE_DELAY` = `1.0`
4. Add **Persistent Disk** (1GB):
   - Mount Path: `/data`
5. Deploy — Docker build installs Playwright + Chromium automatically

### Option B — render.yaml (Infrastructure as Code)

```bash
# Install Render CLI
npm install -g @render/cloudcicd

# Apply from repo root
render blueprint apply render.yaml
```

---

## Step 2: Deploy Frontend to Vercel

```bash
cd frontend
npm install -g vercel
vercel --prod
```

Or connect the GitHub repo at [vercel.com](https://vercel.com) — `vercel.json` handles the build command and proxy rewrites automatically.

### Environment Variables (Vercel)

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://sourcewatch-api.onrender.com` (your Render URL) |

---

## Step 3: Update vercel.json

Edit `vercel.json` and replace `sourcewatch-api.onrender.com` with your actual Render service URL:

```json
"destination": "https://your-actual-render-url.onrender.com/analyze"
```

---

## Step 4: First-time Setup (Index Sources)

After backend is deployed, run the indexing once to populate ChromaDB with VN news sources:

```bash
curl -X POST https://your-render-url.onrender.com/index
```

This scrapes latest articles from:
- dantri.com.vn
- tuoitre.vn
- vtv.vn
- nguoiduatin.vn
- vnexpress.net
- baomoi.com
- anninhthudo.vn
- tapchicongsan.org.vn

(~72 articles indexed, ~5 min)

---

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
playwright install --with-deps chromium
PYTHONPATH=. python3 -m uvicorn backend.main:app --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment
Create `backend/.env` from `backend/.env.example`:
```
GEMINI_API_KEY=your_key_here
GOOGLE_FACT_CHECK_API_KEY=your_key_here
DATABASE_PATH=./data/sourcewatch.db
CHROMADB_PATH=./data/chromadb
SCRAPE_DELAY=1.0
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## Notes

- **Playwright** is required for article fetching (headless Chromium). The Dockerfile installs it automatically. Locally, run `playwright install --with-deps chromium`.
- **ChromaDB** downloads an embedding model (~79MB) on first use. Keep the `/data` disk persistent on Render or re-index via `/index` after restarts.
- **Rate limits**: Gemini free tier = 20 req/min. The backend has exponential backoff + fallback mode when quota exceeded.
- **Vercel proxy** rewrites `/analyze`, `/health`, `/index` → Render backend. No CORS issues.