# LinkIntel AI — Master Render Deployment Guide

**Document Version:** 3.0 (November 2026)  
**Target Platform:** Render.com (Render Blueprint Infrastructure-as-Code)  
**Architecture:** 3-Tier Independent Cloud Services (Node.js SSR Frontend + Python FastAPI Backend + Render PostgreSQL)

---

## 1. Architecture & Render Topology

LinkIntel AI is configured for deployment on **Render** using a single root-level Blueprint specification (`render.yaml`). The services run independently as managed resources in the same cloud region (`oregon`):

```mermaid
flowchart TD
    User[End User Browser] -->|Public HTTPS Requests| Frontend["linkintel-frontend<br/>(Render Node.js SSR Web Service)<br/>Nitro render-com preset"]
    User -->|Public API Calls: /link-analysis| Backend["linkintel-api<br/>(Render Python FastAPI Web Service)<br/>Uvicorn on $PORT"]
    Backend -->|SSRF-Safe Outbound Fetch| Internet[Target Business Websites]
    Backend -->|LLM API Inference| LLM[Google Gemini 2.5 Flash]
    Backend -->|Managed Relational Storage| DB[("linkintel-db<br/>(Render PostgreSQL)")<br/>fromDatabase connectionString]
```

### Deployed Services Summary:

| Resource Name | Render Resource Type | Runtime / Engine | Build Command | Start Command | Health Check |
|---|---|---|---|---|---|
| **`linkintel-frontend`** | Web Service | Node.js 24 (Nitro SSR) | `corepack enable && pnpm install --frozen-lockfile && pnpm run build` | `node .output/server/index.mjs` | `/` |
| **`linkintel-api`** | Web Service | Python 3.10+ (FastAPI) | `pip install --upgrade pip && pip install -r requirements.txt` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | `/health` |
| **`linkintel-db`** | PostgreSQL Database | PostgreSQL 16 (Managed) | N/A (Managed by Render) | N/A | Automated connection pre-ping (`SELECT 1`) |

---

## 2. Infrastructure Configuration (`render.yaml`)

The Blueprint declares all three resources with zero hardcoded credentials and sensible cost-conscious free-tier resource allocation:

```yaml
services:
  - type: web
    name: linkintel-frontend
    runtime: node
    plan: free
    region: oregon
    buildCommand: corepack enable && pnpm install --frozen-lockfile && pnpm run build
    startCommand: node .output/server/index.mjs
    healthCheckPath: /
    envVars:
      - key: NODE_VERSION
        value: 24
      - key: NITRO_PRESET
        value: render_com
      - key: NITRO_HOST
        value: 0.0.0.0
      - key: HOST
        value: 0.0.0.0
      - key: VITE_API_BASE_URL
        sync: false

  - type: web
    name: linkintel-api
    runtime: python
    rootDir: backend
    plan: free
    region: oregon
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: APP_ENV
        value: production
      - key: LLM_PROVIDER
        value: gemini
      - key: LLM_MODEL
        value: gemini-2.5-flash
      - key: GEMINI_API_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: linkintel-db
          property: connectionString
      - key: SEARCH_PROVIDER
        value: duckduckgo
      - key: FRONTEND_ORIGINS
        sync: false
      - key: TRUSTED_PROXIES
        value: 127.0.0.1,::1,localhost,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16

databases:
  - name: linkintel-db
    databaseName: linkintel
    user: linkintel_user
    plan: free
    region: oregon
```

---

## 3. Environment Variables Specification

### 3.1 Backend Service Environment Variables (`linkintel-api`)

| Variable | Required? | Blueprint Source | Description |
|---|---|---|---|
| `APP_ENV` | **Yes** | Blueprint (`production`) | Enables production security checks, logging, and alerts. |
| `LLM_PROVIDER` | **Yes** | Blueprint (`gemini`) | Primary LLM engine. |
| `LLM_MODEL` | **Yes** | Blueprint (`gemini-2.5-flash`) | Foundation model for link analysis. |
| `GEMINI_API_KEY` | **Yes** | Prompted securely (`sync: false`) | Google Gemini API key from Google AI Studio. |
| `DATABASE_URL` | **Yes** | `fromDatabase: linkintel-db` | Automatically injected Render PostgreSQL connection string. |
| `SEARCH_PROVIDER` | No | Blueprint (`duckduckgo`) | Search provider for competitor discovery. |
| `FRONTEND_ORIGINS` | **Yes** | User configured (`sync: false`) | Public URL of `linkintel-frontend` (e.g. `https://linkintel-frontend.onrender.com`). |
| `TRUSTED_PROXIES` | No | Blueprint | Subnets allowed to forward `X-Forwarded-For` without IP spoofing. |
| `PORT` | Auto | Render runtime | Port assigned by Render; Uvicorn binds to `0.0.0.0:$PORT`. |

### 3.2 Frontend Service Environment Variables (`linkintel-frontend`)

| Variable | Required? | Blueprint Source | Description |
|---|---|---|---|
| `NODE_VERSION` | **Yes** | Blueprint (`24`) | Pins Node.js runtime version (Node 24 LTS). |
| `NITRO_PRESET` | **Yes** | Blueprint (`render_com`) | Configures TanStack Start/Nitro for Render Node.js SSR (`node .output/server/index.mjs`). |
| `NITRO_HOST` | **Yes** | Blueprint (`0.0.0.0`) | Binds server to all interfaces. |
| `HOST` | **Yes** | Blueprint (`0.0.0.0`) | Binds server to all interfaces. |
| `PORT` | Auto | Render runtime | Port assigned by Render; Nitro automatically listens on `$PORT`. |
| `VITE_API_BASE_URL` | **Yes** | User configured (`sync: false`) | Public URL of `linkintel-api` (e.g. `https://linkintel-api.onrender.com`). |

> [!IMPORTANT]
> **Public vs Internal Backend URL:** `VITE_API_BASE_URL` must be set to the **public** HTTPS address of `linkintel-api` (`https://<service-name>.onrender.com`), not an internal `.render.internal` private hostname. Link analysis calls originate from the end-user's browser, which cannot resolve Render internal private mesh networks.

---

## 4. PostgreSQL Persistence & Schema Management

### 4.1 Connection String Normalization
Render PostgreSQL connection strings use the `postgres://` dialect prefix by default. SQLAlchemy 2.0 requires `postgresql+psycopg2://`. The application automatically normalizes this in `backend/app/database.py`:
- `postgres://...` $\rightarrow$ `postgresql+psycopg2://...`
- `postgresql://...` $\rightarrow$ `postgresql+psycopg2://...`

### 4.2 Connection Pool Configuration
Render free-tier PostgreSQL instances drop idle client sockets after periods of inactivity. To prevent `SSL SYSCALL error: EOF detected` or dead connection errors, the engine is initialized with:
- `pool_pre_ping=True`: Verifies connection liveness before every checkout.
- `pool_recycle=300`: Refreshes connections every 5 minutes.
- `pool_size=5`: Conservative base connection pool capacity for Render free tier.
- `max_overflow=5`: Burst connection headroom within database limits.
- `pool_timeout=30`: Max wait time for connection checkout.

### 4.3 Database Initialization & Schema Migrations
- **Cold-Start Provisioning:** The FastAPI `lifespan` handler automatically invokes `init_db()` upon application startup, executing `Base.metadata.create_all(bind=engine)`. Tables (`analysis_reports` and `benchmark_runs`) are created automatically if they do not exist.
- **Production Migrations:** If table schemas change in future versions, apply schema migrations using Alembic or explicit SQL DDL migrations via the Render PostgreSQL web console or `psql` connection.

---

## 5. Step-by-Step Render Deployment Sequence

Follow this exact sequence to deploy the complete LinkIntel AI system:

### Step 1: Push Changes to GitHub
Push the `deployment-ready` branch to your GitHub repository:
```bash
git push origin deployment-ready
```

### Step 2: Open Render Dashboard
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click the **New +** button in the top navigation bar.
3. Select **Blueprint**.

### Step 3: Connect Repository
1. Select your GitHub account and choose repository `link-sleuth-studio` (`Mandar-code143/link-sleuth-studio`).
2. Set the **Branch** to `deployment-ready`.
3. Render will detect and parse `render.yaml`.

### Step 4: Supply Required Environment Variables
Render will display the Blueprint plan with the 3 resources:
- **`GEMINI_API_KEY`:** Paste your Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/)).
- **`VITE_API_BASE_URL`:** Initially set to `https://linkintel-api.onrender.com` (or your chosen service name).
- **`FRONTEND_ORIGINS`:** Initially set to `https://linkintel-frontend.onrender.com` (or your chosen service name).

### Step 5: Create Blueprint Resources
Click **Apply**. Render will concurrently provision:
1. `linkintel-db` (PostgreSQL instance).
2. `linkintel-api` (Python container running `pip install -r requirements.txt`).
3. `linkintel-frontend` (Node.js container running `corepack enable && pnpm install --frozen-lockfile && pnpm run build`).

### Step 6: Cross-Link Public URLs
Once Render assigns the permanent `.onrender.com` hostnames:
1. Verify the exact URL assigned to `linkintel-api` (e.g. `https://linkintel-api-xyz.onrender.com`).
2. Verify the exact URL assigned to `linkintel-frontend` (e.g. `https://linkintel-frontend-xyz.onrender.com`).
3. If the generated subdomains differ from default predictions:
   - In `linkintel-frontend` settings, update `VITE_API_BASE_URL` to match the real API URL and trigger a re-deploy.
   - In `linkintel-api` settings, update `FRONTEND_ORIGINS` to match the real frontend URL.

### Step 7: Verify Service Health
1. Open `https://<your-api-url>/health` $\rightarrow$ should return `{"status":"ok"}`.
2. Open `https://<your-api-url>/health/ready` $\rightarrow$ should return:
   ```json
   {
     "status": "ready",
     "provider": "gemini",
     "model": "gemini-2.5-flash",
     "provider_key_present": true,
     "search_provider": "duckduckgo",
     "search_provider_configured": true,
     "database_connected": true,
     "database_dialect": "postgresql",
     "app_env": "production"
   }
   ```
3. Open `https://<your-api-url>/docs` $\rightarrow$ Swagger UI loads and documents all endpoints.
4. Open `https://<your-frontend-url>` $\rightarrow$ LinkIntel AI loads in Live Mode.
5. In Settings, click **Test All Connections** to verify frontend-to-backend communication.
6. Submit a website analysis (e.g. `https://linear.app`) and verify report generation and persistence.

---

## 6. Production Troubleshooting & FAQ

### Issue: "Render free tier instance spins down when inactive"
- **Behavior:** Render free instances spin down after 15 minutes of inactivity. The first incoming request takes ~30-50 seconds for cold boot.
- **Solution:** The frontend displays an informative loading state with progressive retry messaging while the backend boots up. In production, upgrading to Render's "Starter" tier maintains 24/7 warm instances.

### Issue: "CORS error when submitting analysis"
- **Cause:** `FRONTEND_ORIGINS` on `linkintel-api` does not include the exact scheme and hostname of `linkintel-frontend`.
- **Solution:** In Render Dashboard $\rightarrow$ `linkintel-api` $\rightarrow$ Environment, add your frontend origin:
  `FRONTEND_ORIGINS=https://linkintel-frontend.onrender.com,http://localhost:8080`

### Issue: "Database connection failed during cold start"
- **Cause:** `DATABASE_URL` was not injected properly or points to an invalid dialect.
- **Solution:** Ensure `render.yaml` specifies `fromDatabase: { name: linkintel-db, property: connectionString }`. The app automatically rewrites `postgres://` to `postgresql+psycopg2://`. Check `https://<api>/health/ready` to verify `"database_connected": true`.

---

## 7. Security & Operational Scope

- **Tenant Scoping vs User Authentication:** Workspace IDs (`X-Workspace-Id`) provide logical tenant scoping for database records and cache keys. They do not constitute cryptographically verified user authentication. In enterprise multi-user deployments, place an OAuth2 / OIDC proxy or JWT authentication layer in front of the API.
- **Reverse Proxy IP Trust:** Rate limiting extracts client IPs from `X-Forwarded-For` only when the request peer is a recognized internal proxy (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.1`), defeating spoofed IP headers.
- **SSRF Defense:** Outbound HTTP fetches validate IP addresses against IPv4/IPv6 private ranges, link-local, loopback, and cloud metadata endpoints (`169.254.169.254`) with DNS pinning.
