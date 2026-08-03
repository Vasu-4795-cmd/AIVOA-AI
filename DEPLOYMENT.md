# Deploying AIVOA — Render (backend) + Vercel (frontend)

This repo is a monorepo with two independently-deployed apps:

```
aivoa-complaint-system/
├── backend/     -> deploy to Render (FastAPI + Postgres)
├── frontend/    -> deploy to Vercel (React/Vite)
├── render.yaml  -> Render Blueprint (one-click backend deploy)
```

Deploy the **backend first** (you need its URL for the frontend env var), then the frontend.

---

## 0. Push the code to GitHub

Both Render and Vercel deploy from a Git repo.

```bash
cd aivoa-complaint-system
git init
git add .
git commit -m "Initial commit"
gh repo create aivoa-complaint-system --source=. --public --push
# (or create a repo on github.com and `git remote add origin <url> && git push -u origin main`)
```

---

## 1. Backend on Render

### Option A — One-click Blueprint (recommended)
1. Go to https://dashboard.render.com/blueprints → **New Blueprint Instance**.
2. Connect your GitHub repo. Render detects `render.yaml` at the repo root and
   provisions:
   - a **free Postgres database** (`aivoa-db`)
   - a **web service** (`aivoa-backend`) built from `backend/`, wired to that
     database automatically via `DATABASE_URL`.
3. When prompted, set the `GROQ_API_KEY` secret (get one free at
   https://console.groq.com — optional, the app runs on the rule-based fallback
   without it).
4. Click **Apply**. First deploy takes a few minutes.
5. Once live, note the backend URL, e.g. `https://aivoa-backend.onrender.com`.
6. Visit `https://aivoa-backend.onrender.com/api/health` — you should see
   `{"status":"ok","groq_enabled":true|false}`.

### Option B — Manual web service (no Blueprint)
1. Render dashboard → **New +** → **Web Service** → connect the repo.
2. Settings:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add a Postgres instance separately (**New +** → **PostgreSQL**, free tier),
   then copy its **Internal Connection String** into the web service's
   `DATABASE_URL` env var. (SQLite also works for a quick demo, but Render's
   free disk is ephemeral — data is wiped on every redeploy, so Postgres is
   strongly recommended for anything real.)
4. Add the remaining env vars listed below.

### Backend environment variables
| Key | Value |
|---|---|
| `DATABASE_URL` | Postgres connection string (auto-filled by the Blueprint) |
| `GROQ_API_KEY` | Your Groq key, or leave blank to use the offline fallback |
| `GROQ_EXTRACTION_MODEL` | `gemma2-9b-it` |
| `GROQ_CONTEXT_MODEL` | `llama-3.3-70b-versatile` |
| `CORS_ORIGINS` | Your Vercel URL(s), comma-separated — e.g. `https://aivoa.vercel.app` |
| `APP_ENV` | `production` |

> ⚠️ **Important:** after you deploy the frontend in Step 2 and get its Vercel
> URL, come back to Render and update `CORS_ORIGINS` to that exact URL, then
> redeploy the backend (or the browser will block API requests with a CORS
> error).

Free Render web services **spin down after 15 minutes of inactivity** and take
~30–60s to wake back up on the next request — expect a slow first request after
idle periods on the free plan.

---

## 2. Frontend on Vercel

1. Go to https://vercel.com/new and import the same GitHub repo.
2. When asked for the project settings:
   - **Root Directory:** `frontend` (click "Edit" next to Root Directory and
     select it — this is the key monorepo setting)
   - Framework Preset: Vite (auto-detected once Root Directory is set)
   - Build Command: `npm run build` (default, already in `vercel.json`)
   - Output Directory: `dist` (default, already in `vercel.json`)
3. Add an environment variable:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** your Render backend URL, e.g. `https://aivoa-backend.onrender.com`
   - Apply to Production, Preview, and Development.
4. Click **Deploy**.
5. Once live you'll get a URL like `https://aivoa-complaint-system.vercel.app`.
6. Go back to Render and set `CORS_ORIGINS` to this exact URL (see the warning
   in Step 1), then trigger a manual redeploy of the backend.

---

## 3. Verify end-to-end

1. Open your Vercel URL.
2. Paste the contents of `demo_data/sample_email_complaint.txt` into the
   Copilot panel and send it.
3. The form on the left should auto-fill and the AI Risk Assessment box should
   populate.
4. Click **Commit to QMS Ledger** — status should flip to "Committed" with a
   generated `CC-2026-XXXXX` reference.
5. `GET https://<your-backend>/api/complaints` should show the persisted
   record.

If step 2 does nothing / errors in the browser console:
- Check the Network tab — a CORS error means `CORS_ORIGINS` on Render doesn't
  match your Vercel URL exactly (must include `https://`, no trailing slash).
- A failed/pending request for >30s usually means the free Render service was
  asleep and is waking up — retry once.

---

## 4. Local development (for reference)

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
npm run dev   # http://localhost:5173, proxies /api -> localhost:8000
```

## 5. What was added to the original source for deployment
- `render.yaml` — Render Blueprint (Postgres + FastAPI web service)
- `backend/runtime.txt` — pins Python 3.11.9 for Render's build
- `backend/app/config.py` / `database.py` — normalize the `postgres://` URL
  Render provides into the `postgresql+psycopg2://` form SQLAlchemy expects
- `frontend/vercel.json` — build settings + SPA rewrite for Vercel

No other application logic was changed.
