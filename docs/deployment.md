# LinkIntel AI Production Deployment Guide

**Document Version:** 2.0 (November 2026)  
**Target Environments:** Cloud Containers (Docker), PaaS (Render / Railway / Fly.io / AWS ECS), Edge / Static Hosting (Vercel / Netlify / Cloudflare Pages)

---

## 1. Architecture & Deployment Topology

LinkIntel AI is designed to deploy cleanly as two decoupled, independently scalable tiers:

1. **Python FastAPI Backend:** Runs in a container or Python 3.10+ runtime, handling SSRF-protected link fetching, content distillation, LLM inference, SQLite/PostgreSQL persistence, and multi-model benchmarking.
2. **React 19 / TanStack Frontend:** Pre-rendered and built via Vite and Nitro, deploying to edge CDNs (Vercel, Netlify, Cloudflare Pages) or containerized with Node.js.

```mermaid
flowchart LR
    Browser[End User Browser] -->|Static Assets & UI| CDN[Cloudflare Pages / Vercel Edge]
    Browser -->|API Requests: /link-analysis| Backend[FastAPI Backend / Docker]
    Backend -->|SSRF-Safe Outbound Fetch| Internet[Public Internet Web Pages]
    Backend -->|LLM API Calls| Providers[Google Gemini / OpenAI / Anthropic]
    Backend -->|Persistence| DB[(SQLite / PostgreSQL)]
```

---

## 2. Environment Variables Specification

### 2.1 Backend Environment Variables (`backend/.env`)

| Variable Name | Required? | Default Value | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | **Yes** (for primary model) | `""` | Google Gemini API key from Google AI Studio. |
| `OPENAI_API_KEY` | Optional | `""` | OpenAI API key for `gpt-4o-mini` fallback and comparative benchmarking. |
| `ANTHROPIC_API_KEY` | Optional | `""` | Anthropic API key for `claude-3-5-haiku`. |
| `LLM_PROVIDER` | No | `"gemini"` | Active provider: `gemini`, `openai`, `anthropic`, or `mock`. |
| `LLM_MODEL` | No | `"gemini-2.5-flash"` | Active model identifier. |
| `APP_PORT` / `PORT` | No | `4000` | Port the backend listens on (automatically detects platform-assigned `$PORT`). |
| `FRONTEND_ORIGINS` | No | `http://localhost:8080,...` | Comma-separated list of permitted frontend origins for CORS. |
| `DATABASE_URL` | No | `sqlite:///./linkintel.db` | Database connection string. Use PostgreSQL for ephemeral cloud hosting. |
| `TRUSTED_PROXIES` | No | `127.0.0.1,::1,localhost` | Trusted reverse proxy IPs permitted to forward `X-Forwarded-For`. |
| `CACHE_TTL_SECONDS` | No | `3600` | Duration (seconds) to cache audited websites in memory. |
| `APP_ENV` | No | `"production"` | Runtime environment: `production` or `development`. |

> **Important Database Note on Ephemeral Hosting:**
> The default `sqlite:///./linkintel.db` works out-of-the-box for local execution, Docker volumes, and single-instance VMs with persistent disks. On ephemeral PaaS containers (such as free-tier Render or Railway without persistent volumes), container restarts recreate the filesystem. For production durability, configure a managed PostgreSQL database URL (e.g., via Neon, Supabase, or AWS RDS):
> `DATABASE_URL=postgresql://user:password@host:5432/linkintel`

### 2.2 Frontend Environment Variables (`.env.production`)

| Variable Name | Required? | Default Value | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | No | `http://localhost:4000` | Base URL of deployed FastAPI backend service. |

---

## 3. Containerized Backend Deployment (Docker)

The repository provides a production multi-stage Dockerfile located at `backend/Dockerfile` that dynamically respects cloud-assigned ports (`$PORT`).

### 3.1 Build & Run with Docker

```bash
# 1. Build image from repository root
docker build -t linkintel-backend:latest -f backend/Dockerfile backend

# 2. Run container with credentials and persistent volume
docker run -d \
  --name linkintel-api \
  -p 4000:4000 \
  -e GEMINI_API_KEY="AIzaSy..." \
  -e LLM_PROVIDER="gemini" \
  -e FRONTEND_ORIGINS="https://your-frontend.vercel.app,http://localhost:8080" \
  -v linkintel-data:/app \
  linkintel-backend:latest
```

### 3.2 Verify Running Container

```bash
# 1. Liveness check
curl -f http://localhost:4000/health
# Response: {"status":"ok"}

# 2. Deep readiness check (verifies credentials without leaking them)
curl -f http://localhost:4000/health/ready
# Response: {"status":"ready","provider":"gemini","provider_key_present":true,...}

# 3. Interactive OpenAPI documentation
# Open http://localhost:4000/docs in your browser
```

---

## 4. Step-by-Step Cloud Platform Deployment Recipes

### 4.1 Deploying Backend to Render.com (Recommended for FastAPI)

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository: `https://github.com/Mandar-code143/link-sleuth-studio`.
4. Configure service settings:
   - **Name:** `linkintel-api`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variables** in Render dashboard:
   - `GEMINI_API_KEY`: *(your Gemini API key)*
   - `LLM_PROVIDER`: `gemini`
   - `FRONTEND_ORIGINS`: `https://link-sleuth-studio.pages.dev,https://your-app.vercel.app`
   - `APP_ENV`: `production`
6. Set **Health Check Path** to `/health/ready`.
7. Click **Create Web Service**.
8. Once deployed, note your service URL (e.g., `https://linkintel-api.onrender.com`). Verify that `https://linkintel-api.onrender.com/docs` opens the Swagger UI.

### 4.2 Deploying Backend to Railway.app

1. Log in to [Railway](https://railway.app) and click **New Project** → **Deploy from GitHub repo**.
2. Select repository `link-sleuth-studio`.
3. In service settings:
   - Set **Root Directory** to `/backend`.
   - Railway will auto-detect the `Dockerfile`.
4. In the **Variables** tab, add `GEMINI_API_KEY`, `LLM_PROVIDER=gemini`, and `FRONTEND_ORIGINS`.
5. Under **Networking**, click **Generate Domain** to get your public API URL.

### 4.3 Deploying Frontend to Vercel / Netlify / Cloudflare Pages

The frontend produces standard production assets via Vite / Nitro.

#### Deploying on Vercel:
1. Go to [Vercel Dashboard](https://vercel.com) and click **Add New...** → **Project**.
2. Import `Mandar-code143/link-sleuth-studio`.
3. Set **Framework Preset:** `Vite` (or `Other`).
4. Set **Build Command:** `pnpm run build`
5. Set **Output Directory:** `.output/public`
6. Add Environment Variable:
   - `VITE_API_BASE_URL`: `https://linkintel-api.onrender.com` (your deployed backend URL)
7. Click **Deploy**.

#### Deploying on Cloudflare Pages:
1. Go to Cloudflare Dashboard → **Workers & Pages** → **Create application** → **Pages**.
2. Connect Git repository.
3. Build configuration:
   - **Framework preset:** `None`
   - **Build command:** `npm run build`
   - **Build output directory:** `.output/public`
4. Add environment variable:
   - `VITE_API_BASE_URL`: `https://linkintel-api.onrender.com`
5. Click **Save and Deploy**.

---

## 5. Production Security Verification Checklist

Before opening the application to external users:

- [x] **No Committed Secrets:** Repository `.gitignore` excludes `.env`, `linkintel.db`, and local task logs.
- [x] **SSRF Guardrails:** Target URLs are validated against private IPs, loopback, link-local, and cloud metadata (`169.254.169.254`).
- [x] **DNS Rebinding Defense:** Outbound connections use pinned DNS transport directly to pre-validated IP addresses.
- [x] **Rate Limiting:** Sliding-window rate limiter active (60 requests/minute per client IP).
- [x] **CORS Isolation:** `FRONTEND_ORIGINS` explicitly configured without permissive wildcard `*`.
- [x] **Error Shielding:** No internal stack traces, system paths, or raw exception strings leaked in HTTP responses.
- [x] **Documentation Access:** Public OpenAPI / Swagger documentation active at `/docs`.
