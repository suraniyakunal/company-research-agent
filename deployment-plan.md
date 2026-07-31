# Deployment Plan: Railway (backend) + Vercel (frontend)

## Top-Level Overview

Deploy the Company Research Agent so it is publicly accessible:
- **Backend (FastAPI):** Railway Web Service, running via Docker to guarantee Python 3.13. Railway does not spin down on the free tier ($5/month free credit, ~500 hrs).
- **Frontend (Next.js):** Vercel, using its native Next.js build pipeline.

The two services communicate over HTTPS: Vercel frontend → Railway backend (`POST /research`).  
No code logic changes are needed — only deployment configuration files and environment variable wiring.

---

## Sub-Tasks

---

### Sub-Task 1 — Add `backend/.env.example`

**Intent:** Document which environment variables the backend needs, so they're easy to reproduce locally and serve as a reference when filling in the Railway dashboard.

**Expected Outcomes:**
- `backend/.env.example` is committed with placeholder values for `GEMINI_API_KEY` and `SERPER_API_KEY`.

**Todo List:**
1. Create `backend/.env.example` with the two variable names and placeholder values.

**Relevant Context:**
- `backend/main.py` uses `load_dotenv()` and the agent reads keys from env via `os.getenv("GEMINI_API_KEY")` / `os.getenv("SERPER_API_KEY")`.
- The real `.env` is already `.gitignore`d — this file is documentation only.

**Status:** [ ] pending

---

### Sub-Task 2 — Write `backend/Dockerfile` and `backend/.dockerignore`

**Intent:** Containerise the FastAPI backend so Railway can build and run it with exactly Python 3.13.

**Expected Outcomes:**
- `backend/Dockerfile` builds a minimal Python 3.13-slim image.
- Dependencies are installed via `uv` (already used for local dev) using `pyproject.toml`.
- The container starts `uvicorn main:app` on `$PORT` (Railway injects this env var at runtime — must NOT be hardcoded to 8000).
- `backend/.dockerignore` excludes `.env`, `__pycache__`, `.venv`, etc.

**Todo List:**
1. Create `backend/Dockerfile`:
   - Base image: `python:3.13-slim`
   - Install `uv` via pip.
   - Copy `pyproject.toml` and `uv.lock` first for Docker layer caching.
   - Run `uv sync --no-dev` to install production dependencies.
   - Copy source files (`main.py`, `agent.py`, `schema.py`).
   - `CMD` must use the shell form to expand `$PORT`: `CMD uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Create `backend/.dockerignore`:
   - Exclude: `.env`, `__pycache__`, `.venv`, `*.pyc`, `.python-version`, `test_*.py`.

**Relevant Context:**
- `backend/pyproject.toml` lists all dependencies. `requires-python = ">=3.13"`.
- Railway injects `PORT` env var automatically — the `CMD` must use `$PORT`, not a hardcoded port.
- `uv` is the project's package manager; using it inside the Dockerfile keeps installs consistent with local dev.
- Check whether `uv.lock` exists in `backend/` before writing the Dockerfile (it may or may not be committed).

**Status:** [ ] pending

---

### Sub-Task 3 — Add `railway.toml` (Railway config)

**Intent:** Tell Railway which subdirectory contains the Dockerfile and how to build/start the service, so it can be deployed by simply connecting the GitHub repo.

**Expected Outcomes:**
- `railway.toml` at the repo root declares the build and deploy config for the backend service.
- Railway auto-detects the Dockerfile in `backend/`.
- Env var names for `GEMINI_API_KEY` and `SERPER_API_KEY` are documented (values set manually in the Railway dashboard).

**Todo List:**
1. Create `railway.toml` at the repo root:
   - Set `[build]` section: `dockerfilePath = "backend/Dockerfile"`, `dockerContextDir = "backend"`.
   - Set `[deploy]` section: `startCommand` can be left empty (CMD in Dockerfile handles it), `healthcheckPath = "/docs"`.

**Relevant Context:**
- Railway blueprint docs: https://docs.railway.com/reference/config-as-code
- `dockerContextDir` must be `"backend"` so the Dockerfile's `COPY` instructions resolve correctly relative to the `backend/` folder.
- Railway will auto-inject `PORT`, `RAILWAY_PUBLIC_DOMAIN`, and other platform vars — no need to declare them.

**Status:** [ ] pending

---

### Sub-Task 4 — Wire the frontend to the production backend URL

**Intent:** The frontend currently has `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`. For production, Vercel needs this set to the live Railway URL. This sub-task adds a `vercel.json` and `frontend/.env.example` to document and configure this.

**Expected Outcomes:**
- `frontend/.env.example` committed with `NEXT_PUBLIC_API_URL=https://YOUR_RAILWAY_SERVICE.up.railway.app`.
- `vercel.json` at repo root tells Vercel the project root is `frontend/` and the framework is Next.js.
- Clear instructions are captured for which Vercel dashboard env var to set post-deploy.

**Todo List:**
1. Create `frontend/.env.example` with `NEXT_PUBLIC_API_URL=https://YOUR_RAILWAY_SERVICE.up.railway.app`.
2. Create `vercel.json` at repo root:
   - Set `"root": "frontend"` and `"framework": "nextjs"`.
   - Do NOT hardcode the actual Railway URL — that value is set in the Vercel dashboard.

**Relevant Context:**
- `frontend/.env.local` (gitignored) currently holds `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- `frontend/pages/index.tsx` uses `process.env.NEXT_PUBLIC_API_URL` as the fetch target.
- Vercel automatically injects env vars defined in its dashboard at build time for `NEXT_PUBLIC_*` variables.
- Railway public URLs follow the pattern: `https://<service-name>.up.railway.app`

**Status:** [ ] pending

---

### Sub-Task 5 — Update `README.md` with deployment instructions

**Intent:** Document the end-to-end deployment steps so the repo is self-sufficient for anyone who forks it or returns to it later.

**Expected Outcomes:**
- `README.md` has a new **Deployment** section covering:
  1. How to deploy the backend on Railway (connect repo → auto-detects `railway.toml` + Dockerfile → set two env vars → note the public URL).
  2. How to deploy the frontend on Vercel (connect repo → set root to `frontend/` → set `NEXT_PUBLIC_API_URL`).
- The `[link once deployed]` placeholder lines at the top of the README are replaced with a note to fill in after deploy.
- The **Deploy** line in the architecture table is updated from `Render (backend)` to `Railway (backend)`.

**Todo List:**
1. Add a `## Deployment` section to `README.md` after the "Running locally" section.
2. Update line 47: change `Render (backend)` → `Railway (backend)` in the tech/deploy table.
3. Replace `[link once deployed]` placeholder text (lines 7–8) with `<!-- TODO: fill in after deploy -->` or a clear note.

**Relevant Context:**
- `README.md` lines 7–8: live demo / API docs placeholders.
- `README.md` line 47: `**Deploy:** Render (backend) + Vercel (frontend)`.
- "Running locally" section ends around line 124.

**Status:** [ ] pending

---

## Post-Deploy Checklist (manual steps — cannot be automated)

### Railway (backend)
1. Go to railway.com → New Project → Deploy from GitHub repo → select this repo.
2. Railway detects `railway.toml` automatically and builds `backend/Dockerfile`.
3. In the Railway service settings → Variables, add:
   - `GEMINI_API_KEY` = your key
   - `SERPER_API_KEY` = your key
4. Note the auto-assigned public URL (e.g. `https://company-research-agent.up.railway.app`).

### Vercel (frontend)
1. Go to vercel.com → New Project → Import from GitHub → select this repo.
2. Vercel detects `vercel.json` and sets the root to `frontend/` automatically.
3. In the Vercel project settings → Environment Variables, add:
   - `NEXT_PUBLIC_API_URL` = the Railway URL from step 4 above.
4. Deploy (or re-deploy if already deployed without the env var).

### CORS note
The backend's `allow_origins=["*"]` in `backend/main.py` already permits the Vercel domain — no changes needed.
