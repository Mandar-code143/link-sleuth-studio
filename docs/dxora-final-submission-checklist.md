# Dxora Technologies Python Practical Test — Final Submission Checklist

**Candidate:** Mandar  
**Repository:** [https://github.com/Mandar-code143/link-sleuth-studio](https://github.com/Mandar-code143/link-sleuth-studio)  
**Branch:** `main`  
**Evaluation Target:** Dxora Technologies Python Practical Test — Link Analysis  
**Submission Deadline:** 27 November 2026  
**Final Audit & Verification Date:** 24 November 2026

---

## A. Completed and Verified by Repository Evidence

- [x] **SSRF Security & Pinned-IP Transport:** 6-layer defense pipeline rejecting loopback, RFC 1918 private IPs, link-local, and cloud metadata (`169.254.169.254`). Outbound HTTP connections pinned directly to validated IPs via `PinnedAsyncNetworkBackend`.
- [x] **Safe Website Extraction:** Trafilatura and BeautifulSoup4 HTML parser extracting main content, meta tags, OpenGraph data, headings, and canonical links with a 5 MB streaming limit.
- [x] **Competitor vs Brand Analysis (Section 1):** Rigorous candidate discovery with aggregator domain rejection, deduplication, and strictly typed evidence classification (`extracted`, `verified`, `inferred`). Inferred competitors have empty source URLs and are typed as `inferred_alternative`.
- [x] **Five-Platform Target Search Queries (Section 2):** Exactly 5 queries collectively covering `Google`, `LinkedIn`, `X`, `Instagram`, and `Facebook` with search intent, commercial relevance, and target audience.
- [x] **SEO Improvements & DOM Findings (Section 3):** Primary, secondary, long-tail, and business keywords, optimized title (<60 chars) and meta description (<160 chars) with rationale, and factual technical SEO findings inspected from actual HTML DOM nodes.
- [x] **Top Services (Section 4):** Up to 5 real services/products extracted from site copy with target industry, target customer, and value proposition.
- [x] **Target Audience Profiles (Section 5):** Primary and secondary audiences, industry segments, business types, geographic focus, and structured customer persona profiles.
- [x] **LLM Comparison Research (15 Marks):** Comprehensive multi-model research whitepaper in `backend/docs/llm-research.md` comparing Google Gemini 2.5 Flash, OpenAI GPT-4o mini, and Anthropic Claude 3.5 Haiku using published official pricing verified as of 24 November 2026.
- [x] **Cost Optimization Engineering:** Documented and verified DOM distillation (75–85% token reduction), native Pydantic schema enforcement (zero retry tokens), workspace-isolated TTL caching (\$0.00 on duplicate requests), and dynamic micro-dollar accounting.
- [x] **Multi-Model Benchmark Service:** `/models/status` and `/benchmark/run` endpoints. Synthetic mode uses labelled synthetic data; live mode extracts real websites and returns explicit failures (`LIVE_EXTRACTION_FAILED`) rather than silently falling back to synthetic datasets. Neutral multi-criteria recommendation scoring (45% completeness, 30% latency, 25% cost).
- [x] **SQLite / SQLAlchemy Persistence:** Database tables for reports and benchmarks with multi-tenant workspace isolation (`X-Workspace-Id`).
- [x] **Reverse Proxy Security:** `X-Forwarded-For` header is only trusted when the direct connecting peer is in `TRUSTED_PROXIES`, preventing IP spoofing.
- [x] **Workspace Cache Isolation:** Cache keys incorporate `workspace_id`, preventing cross-tenant cached data leaks.
- [x] **Google Stitch React 19 Frontend:** 6 responsive pages (Overview, Analyze, Report, Model Lab, History, Settings) with Desktop 260px sidebar / 56px topbar and Mobile 64px bottom navigation.
- [x] **Visual Evidence & Screenshots:** 15 genuine high-resolution screenshots across desktop and mobile viewports in `docs/evidence/` plus live Swagger UI capture (`10-swagger-docs-desktop.png`).
- [x] **Sanitized API Evidence:** Sample request, structured response, validation error, and health-check JSON files in `docs/evidence/`.

---

## B. Completed but Requiring Applicant Account / Deployment Action

- [ ] **Cloud Backend Deployment:** Backend container configuration (`backend/Dockerfile`, `docker-compose.yml`) is verified and port-adaptive (`$PORT`). You must deploy it to your personal hosting provider (e.g. Render, Railway, or Fly.io) and supply your own `GEMINI_API_KEY`.
- [ ] **Cloud Frontend Deployment:** Frontend builds cleanly with zero errors (`npm run build`). You must import the repository into Vercel, Netlify, or Cloudflare Pages and set `VITE_API_BASE_URL` to your deployed backend URL.

---

## C. Mandatory Personal Actions for Submission

1. **Supply Production AI Credentials:**
   - In your cloud hosting dashboard (e.g. Render/Railway), set `GEMINI_API_KEY` to your live Google AI Studio API key.
2. **Deploy Backend Service:**
   - Follow the step-by-step instructions in [`docs/deployment.md`](deployment.md).
   - Verify that your live `/health` and `/docs` endpoints respond.
3. **Deploy Frontend Web Application:**
   - Deploy the frontend to Vercel or Cloudflare Pages.
   - Point `VITE_API_BASE_URL` to your live backend service URL.
4. **Submit to Dxora Technologies:**
   - Submit your GitHub repository URL: `https://github.com/Mandar-code143/link-sleuth-studio`.
   - Provide your deployed live frontend and backend API documentation URLs.

---

## D. Remaining Blockers

- **None inside the repository.** All code, tests, documentation, security controls, and visual evidence are complete, tested, and committed.

---

## E. Deployment Links

| Service                        | Deployed Status        | Target URL / Placeholder                                                              |
| ------------------------------ | ---------------------- | ------------------------------------------------------------------------------------- |
| **FastAPI Backend API**        | Ready for cloud deploy | `https://linkintel-api.onrender.com` _(placeholder — deploy via Render)_              |
| **Interactive Swagger Docs**   | Ready for cloud deploy | `https://linkintel-api.onrender.com/docs` _(placeholder)_                             |
| **Production Frontend UI**     | Ready for cloud deploy | `https://link-sleuth-studio.pages.dev` _(placeholder — deploy via Cloudflare/Vercel)_ |
| **Local Development Backend**  | Verified live          | `http://127.0.0.1:4000`                                                               |
| **Local Development Docs**     | Verified live          | `http://127.0.0.1:4000/docs`                                                          |
| **Local Development Frontend** | Verified live          | `http://localhost:8080`                                                               |

---

## F. Actual Verified Test Results

### 1. Backend Pytest Suite

```bash
python -m pytest backend/tests -v
```

- **Total Tests:** 66
- **Passed:** 66
- **Failed:** 0
- **Pass Rate:** **100%**
- **Duration:** 23.93 seconds
- **Modules Covered:**
  - `test_analysis.py` (4 tests) — Schema validation, cost calculation, 5-platform query coverage, metadata schema.
  - `test_api.py` (9 tests) — Health, readiness, OpenAPI docs, input validation, localhost blocking, private IP rejection, honest failure when unconfigured.
  - `test_benchmark.py` (8 tests) — Model status, unconfigured handling, mock provider execution, simulation mode, quality score latency decoupling, live extraction failure regression test, neutral model recommendation scoring.
  - `test_competitor.py` (7 tests) — Aggregator rejection, self-domain and duplicate rejection, listicle rejection, verified candidate creation, on-page extracted classification, unverified inferred classification, transparent search failure handling.
  - `test_config.py` (6 tests) — Anchor-based `.env` path resolution, whitespace stripping, Gemini key detection, invalid provider rejection, invalid port rejection, safe masked diagnostics.
  - `test_extractor.py` (3 tests) — HTML parsing, technical SEO evaluation, prompt injection neutralization.
  - `test_persistence.py` (4 tests) — Database models, workspace isolation in reports, search and pagination, benchmark endpoints and isolation.
  - `test_security.py` (25 tests) — Public URLs, scheme validation, embedded credentials, private TLDs, loopback, RFC 1918, IPv6, cloud metadata, DNS validator, DNS rebinding, redirect hops, rate limiting, trusted proxy `X-Forwarded-For`, untrusted peer IP spoofing rejection, workspace cache isolation, pinned network transport.

### 2. Frontend Vitest Suite

```bash
npm test
```

- **Total Tests:** 17
- **Passed:** 17
- **Failed:** 0
- **Pass Rate:** **100%**
- **Duration:** 5.47 seconds
- **Modules Covered:**
  - `persistence.test.ts` (5 tests) — Workspace storage, report caching, preference management.
  - `app-routing.test.tsx` (12 tests) — Router tree resolution for all 6 core pages across viewports.

### 3. Production Build

```bash
npm run build
```

- **Client Environment:** Built in 1.26s (`.output/public`)
- **SSR Environment:** Built in 524ms
- **Nitro Worker Environment:** Built in 878ms
- **Compilation Errors:** **0**

---

## G. Evidence File Locations

All visual screenshots and sanitized API logs are committed under [`docs/evidence/`](evidence/):

- [`01-overview-desktop.png`](evidence/01-overview-desktop.png) — Overview Dashboard (Desktop)
- [`01-overview-mobile.png`](evidence/01-overview-mobile.png) — Overview Dashboard (Mobile)
- [`02-analyze-desktop.png`](evidence/02-analyze-desktop.png) — Analyze Website Form (Desktop)
- [`02-analyze-mobile.png`](evidence/02-analyze-mobile.png) — Analyze Website Form (Mobile)
- [`03-report-overview-desktop.png`](evidence/03-report-overview-desktop.png) — Completed Analysis Report Header (Desktop)
- [`03-report-overview-mobile.png`](evidence/03-report-overview-mobile.png) — Completed Analysis Report Header (Mobile)
- [`04-report-competitors-desktop.png`](evidence/04-report-competitors-desktop.png) — Competitor Analysis Table
- [`05-report-queries-seo-desktop.png`](evidence/05-report-queries-seo-desktop.png) — Target Search Queries & SEO Diff
- [`06-report-services-audience-desktop.png`](evidence/06-report-services-audience-desktop.png) — Top Services & Target Audience Personas
- [`07-model-research-desktop.png`](evidence/07-model-research-desktop.png) — Model Research Lab & Economics (Desktop)
- [`07-model-research-mobile.png`](evidence/07-model-research-mobile.png) — Model Research Lab & Economics (Mobile)
- [`08-history-desktop.png`](evidence/08-history-desktop.png) — Audit History Repository (Desktop)
- [`08-history-mobile.png`](evidence/08-history-mobile.png) — Audit History Repository (Mobile)
- [`09-settings-desktop.png`](evidence/09-settings-desktop.png) — Settings & Telemetry (Desktop)
- [`09-settings-mobile.png`](evidence/09-settings-mobile.png) — Settings & Telemetry (Mobile)
- [`10-swagger-docs-desktop.png`](evidence/10-swagger-docs-desktop.png) — Interactive FastAPI Swagger UI (`/docs`)
- [`sample-request.json`](evidence/sample-request.json) — Sample POST Request Payload
- [`sample-response.json`](evidence/sample-response.json) — Full Sample Structured Response Payload
- [`validation-error-response.json`](evidence/validation-error-response.json) — SSRF Security Policy Violation Error
- [`health-check-response.json`](evidence/health-check-response.json) — Liveness & Readiness JSON Outputs
- [`README.md`](evidence/README.md) — Evidence Artifact Index
