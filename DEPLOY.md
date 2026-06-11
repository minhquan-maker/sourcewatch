# Deploying SourceWatch

## Architecture

```
User → Vercel (frontend) → Render (backend) → Gemini API + ChromaDB + SQLite
```

- **Frontend**: Vercel (React 19 + Vite + Tailwind v4) — served at `sourcewatch.vercel.app`
- **Backend**: Render Web Service (FastAPI + Playwright, port 8000)
- **Database**: Render persistent disk at `/data` (SQLite + ChromaDB)
- **AI**: Google Gemini 3.5 Flash via `google-genai` SDK

---

## Step 1 — Deploy Backend to Render

### Option A: One-click from GitHub

1. Go to [render.com](https://render.com) → New → Web Service → Connect your GitHub repo
2. Configure the service:
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Region**: Singapore
   - **Plan**: Starter ($7/mo)
3. Add environment variables (Environment → Environment Variables):
   - `GEMINI_API_KEY` — your Google AI Studio key (starts with `AIza.` or `AQ.`)
   - `DATABASE_PATH` = `/data/sourcewatch.db`
   - `CHROMADB_PATH` = `/data/chromadb`
   - `scrape_delay` = `1.0`
   - `PYTHONPATH` = `/app`
   - `PYTHONUNBUFFERED` = `1`
4. Add a **Persistent Disk** (Environment → Disks):
   - Name: `sourcewatch-data`
   - Mount Path: `/data`
   - Size: 1GB
5. Click **Create Web Service** — the Dockerfile builds Playwright + Chromium automatically.

### Option B: render.yaml (Infrastructure as Code)

```bash
npm install -g @render/cloudcicd
render blueprint apply render.yaml
```

The `render.yaml` defines the same config as Option A. After apply, set `GEMINI_API_KEY` manually in the Render dashboard (sync: false).

---

## Step 2 — Update vercel.json

Before deploying the frontend, edit `vercel.json` and replace the placeholder Render URL with your actual backend URL.

```json
"destination": "https://your-actual-render-url.onrender.com/analyze"
```

Do the same for `/health` and `/index` rewrites.

---

## Step 3 — Deploy Frontend to Vercel

Connect the repo at [vercel.com](https://vercel.com) — the `vercel.json` already handles:
- Build: `cd frontend && npm install && npm run build`
- Output: `frontend/dist`
- Rewrites: `/analyze`, `/health`, `/index` → your Render backend

Or deploy via CLI:

```bash
cd frontend
npm install -g vercel
vercel --prod
```

> **Note:** No `VITE_API_URL` needed. The frontend uses relative paths (`axios.post("/analyze")`). Vercel's `vercel.json` rewrites route these to Render. Same pattern as local dev (`vite.config.js` proxies to `localhost:8000`).

---

## Step 4 — Index VN News Sources

After backend is live, run this once to populate ChromaDB with the 10 tracked sources:

```bash
curl -X POST https://your-render-url.onrender.com/index
```

This scrapes latest articles from:
- vnexpress.net (trust: 8.0)
- tuoitre.vn (trust: 8.0)
- vov.vn (trust: 8.5)
- vtv.vn (trust: 8.5)
- dantri.com.vn (trust: 7.5)
- thanhnien.vn (trust: 7.5)
- zing.vn (trust: 7.0)
- laodong.vn (trust: 7.0)
- tienphong.vn (trust: 7.0)
- nguoiduatin.vn (trust: 6.5)

~150 articles indexed, takes ~5 minutes. ChromaDB downloads an embedding model (~79MB) on first run — keep the `/data` disk persistent or re-run `/index` after restarts.

---

## Local Development

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

### Environment
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY
```

---

## Important Notes

- **Playwright + Chromium** is required for article fetching. The Dockerfile installs it automatically via `playwright install --with-deps chromium`. Locally, run `playwright install chromium`.
- **Gemini rate limits**: Free tier = 20 req/min. The backend has exponential backoff (5 retries on 429/503/UNAVAILABLE) and falls back to sentence-splitting if quota is exhausted.
- **ChromaDB embedding model** downloads on first use. The Render persistent disk keeps it across restarts.
- **CORS**: The Vercel rewrite proxy bypasses CORS entirely — no CORS headers needed on Render.