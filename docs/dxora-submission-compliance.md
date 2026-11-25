# Dxora Technologies Python Practical Test — Compliance & Audit Report

**Project:** LinkIntel AI (`Mandar-code143/link-sleuth-studio`)  
**Assignment Reference:** [Dxora Technologies Practical Test — Link Analysis](https://github.com/chivoxai/practical-test/blob/main/link-analysis.md)  
**Submission Deadline:** 27 November 2026  
**Audit Date:** 25 November 2026  
**Auditor:** Principal Software Architect, Senior Python Engineer & Technical Evaluator

---

## 1. Compliance Summary Table

| Requirement / Component                         | Assigned Marks | Implementation Status         | Evidence / Location                                                                                       |
| ----------------------------------------------- | -------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------- |
| **1. Web Extraction & SSRF Security**           | 20 Marks       | **Complete and verified**     | `backend/app/security/`, `backend/app/services/website_extractor.py`, 25 security tests passing           |
| **2. Competitor Analysis (Section 1)**          | 15 Marks       | **Complete and verified**     | `backend/app/services/competitor_service.py`, `analysis_service.py`, 7 competitor tests passing           |
| **3. 5-Platform Search Queries (Section 2)**    | 10 Marks       | **Complete and verified**     | `backend/app/services/analysis_service.py`, `test_analysis.py`, 100% 5-platform coverage                  |
| **4. Technical SEO Improvements (Section 3)**   | 10 Marks       | **Complete and verified**     | `backend/app/services/seo_service.py`, DOM signal checks (title, meta, H1, OG, canonical, robots)         |
| **5. Top Services & Audience (Sections 4 & 5)** | 10 Marks       | **Complete and verified**     | `backend/app/services/analysis_service.py`, up to 5 real services, structured persona profiles            |
| **6. LLM Research & Comparison**                | 15 Marks       | **Complete and verified**     | `backend/docs/llm-research.md`, official published rates (Gemini, OpenAI, Anthropic), cost models         |
| **7. Multi-Model Benchmark Service**            | 10 Marks       | **Complete and verified**     | `backend/app/services/benchmark_service.py`, `/benchmark/run`, neutral scoring formula                    |
| **8. API & Database Architecture**              | 10 Marks       | **Complete and verified**     | FastAPI `POST /link-analysis`, SQLite / SQLAlchemy persistence, workspace isolation                       |
| **9. Production React Frontend**                | Bonus / UI     | **Complete and verified**     | React 19, Google Stitch design tokens, 6 responsive pages, 17 vitest tests passing                        |
| **10. Live Cloud Deployment**                   | Submission     | **Complete and verified**     | Deployed on Render: [Frontend](https://link-sleuth-studio.onrender.com), [API](https://linkintel-api-4dvd.onrender.com), [PostgreSQL](docs/deployment.md) |

---

## 2. Requirement-by-Requirement Forensic Audit

### Section 1: Competitor vs Submitted Brand Comparison

- **Assignment Expectation:** Ingest website content and provide realistic competitor landscape, comparing at least 3 competitors with strengths, weaknesses, positioning, opportunities, and attributable evidence.
- **Status:** **Complete and verified**
- **Verification Details:**
  - `CompetitorResearchService` (`backend/app/services/competitor_service.py`) conducts live external search via DuckDuckGo / Brave / Tavily.
  - Aggregator and directory domains (G2, Capterra, Wikipedia, Reddit, Clutch, etc.) are strictly filtered out via `AGGREGATOR_DOMAINS`.
  - Self-domains and duplicates are blocked.
  - Competitors are strictly classified into `extracted` (found on-page HTML), `verified` (corroborated via live search with attributable destination URLs and non-aggregator domains), or `inferred` (LLM-reasoned alternatives with `source_urls=[]` and `competitor_type="inferred_alternative"`).
  - Search failures are handled transparently without fabricating fake companies or fake URLs.
  - 7 regression tests in `backend/tests/test_competitor.py` verify aggregator rejection, duplicate rejection, listicle rejection, evidence classification, and graceful failure handling.

---

### Section 2: Top Five Target Search Queries with 5-Platform Coverage

- **Assignment Expectation:** Generate exactly 5 target search queries covering Google, LinkedIn, X, Instagram, and Facebook, with intent, commercial relevance, and audience.
- **Status:** **Complete and verified**
- **Verification Details:**
  - `LLMAnalysisPayload` enforces `min_length=5, max_length=5` on `target_search_queries`.
  - `AnalysisService.normalize_search_queries()` guarantees that across the exactly 5 queries, all 5 platforms (`Google`, `LinkedIn`, `X`, `Instagram`, `Facebook`) are collectively represented.
  - Each query includes query phrase, platform list, intent (`Commercial`, `Informational`, `Transactional`, etc.), commercial relevance, and target audience.
  - Tested in `backend/tests/test_analysis.py::test_search_queries_five_platforms_coverage`.

---

### Section 3: SEO Improvements & Technical Signals

- **Assignment Expectation:** Provide primary, secondary, long-tail, and business keywords, recommended title (<60 chars) and meta description (<160 chars) with rationale, and factual technical SEO findings.
- **Status:** **Complete and verified**
- **Verification Details:**
  - Deterministic DOM inspection in `backend/app/services/seo_service.py` evaluates live extracted signals: title presence and length, meta description presence and length, H1 tag count and content, canonical URL, OpenGraph tags (`og:title`, `og:image`), and robots directives.
  - Actual extracted title and meta description are preserved in `current_title` and `current_meta_description`.
  - Search volume note explicitly states: `"No verified search-volume data available; recommendations are strategy-led."` to avoid inventing fabricated search numbers.
  - Verified in `backend/tests/test_extractor.py::test_inspect_technical_seo_evaluation`.

---

### Section 4: Up to Five Top Services

- **Assignment Expectation:** Extract up to 5 real services/products offered by the company. If fewer than 5 are offered, report only what is present without inventing fake offerings.
- **Status:** **Complete and verified**
- **Verification Details:**
  - Pydantic schema enforces `max_length=5` on `top_services`.
  - Each service includes name, description, target industry, target customer, customer benefit, evidence (`extracted` or `inferred`), and source URL where applicable.
  - Prompt instructions explicitly direct the model to report only what is on the page.

---

### Section 5: Target Audience Profiles & Personas

- **Assignment Expectation:** Define primary and secondary audiences, industry segments, business types, geographic focus, needs, challenges, and customer personas.
- **Status:** **Complete and verified**
- **Verification Details:**
  - `TargetAudience` schema captures primary audience, secondary audience list, industry segments, business types, geographic focus, core needs, challenges, interests, and marketing segments.
  - Structured `AudienceProfile` personas include persona title, business type, needs, challenges, matching services, and strategic opportunity.

---

### Section 6: LLM Comparison & Cost Optimization Research (15 Marks)

- **Assignment Expectation:** Compare at least 3 models based on accuracy, speed, pricing, context length, JSON support, recommendation, and cost optimization techniques.
- **Status:** **Complete and verified**
- **Verification Details:**
  - Full research report in `backend/docs/llm-research.md` (and mirrored in `docs/llm-research.md`).
  - Evaluates Google Gemini 2.5 Flash, OpenAI GPT-4o mini, and Anthropic Claude 3.5 Haiku using published official pricing verified as of 24 November 2026.
  - Pricing is reconciled across all project files: Gemini 2.5 Flash (\$0.15/1M in, \$0.60/1M out), GPT-4o-mini (\$0.15/1M in, \$0.60/1M out), Claude 3.5 Haiku (\$0.80/1M in, \$4.00/1M out).
  - Explicit baseline token assumption: 3,500 input tokens, 1,200 output tokens = \$0.001245 per analysis.
  - Scale projections calculated for 100, 500, 1,000, 5,000, 10,000, and 50,000 daily scans.
  - Four cost optimization engineering techniques detailed: DOM distillation (75–85% token reduction), native Pydantic schema binding (zero retry tokens), in-memory TTL caching (\$0.00 on duplicate requests), and dynamic micro-dollar accounting.
  - Primary recommendation (Gemini 2.5 Flash) and fallback (GPT-4o-mini) documented with engineering rationale.

---

### Section 7: Multi-Model Benchmark Service (`/benchmark/run`)

- **Assignment Expectation:** Benchmark runner comparing models on latency, cost, and schema compliance.
- **Status:** **Complete and verified**
- **Verification Details:**
  - `BenchmarkService` (`backend/app/services/benchmark_service.py`) runs concurrent provider evaluations.
  - Synthetic benchmark dataset mode (`benchmark_mode="synthetic"`).
  - Live benchmark mode (`benchmark_mode="live"`): extracts the submitted URL; if live extraction fails, it returns an explicit `status="failed"` result (`LIVE_EXTRACTION_FAILED`) and **never silently falls back to synthetic data**.
  - Neutral multi-criteria scoring methodology: 45% structural completeness, 30% latency efficiency, 25% cost economics. No pre-selected winner bias.
  - Simulated / mock runs are explicitly flagged (`is_simulated=True`, `simulated=True`).
  - Tested in `backend/tests/test_benchmark.py` (8 passing tests).

---

### Section 8: SSRF Security, DNS Pinning & Isolation

- **Assignment Expectation:** Secure outbound HTTP requests, private IP blocking, DNS rebinding mitigation, rate limiting, and workspace scoping.
- **Status:** **Complete and verified**
- **Verification Details:**
  - `validate_and_normalize_url`: enforces HTTP/HTTPS only, blocks embedded credentials, blocks localhost, `.internal`, `.local`, `.onion`, `.corp`, and direct private IPs (RFC 1918, RFC 4193, loopback, link-local, cloud metadata `169.254.169.254`).
  - `resolve_and_validate_hostname`: pre-flight DNS validation resolving both A and AAAA records, fails closed if any IP is private.
  - `PinnedAsyncNetworkBackend`: custom HTTP transport forcing socket connection directly to pre-validated IP while retaining original hostname in TLS SNI and HTTP `Host` header.
  - Streaming size enforcement: early rejection on `Content-Length > 5MB` and per-chunk streamed byte counting.
  - Rate limiting: sliding-window in-memory throttler (60 req/min). `X-Forwarded-For` is only trusted when the direct connecting peer is a configured reverse proxy (`TRUSTED_PROXIES`).
  - Workspace scoping: `X-Workspace-Id` scopes SQLite database records and isolates in-memory cache keys.
  - Limitation honestly documented: `X-Workspace-Id` provides tenant filtering, not user authentication.
  - 25 security tests in `backend/tests/test_security.py` passing.

---

### Section 9: Automated Test Suites

- **Status:** **Complete and verified**
- **Backend Tests:** **81 / 81 passed** (`python -m pytest backend/tests` in 1.83s, 100% pass rate).
- **Frontend Tests:** **17 / 17 passed** (`npm test` in 2.91s, 100% pass rate).
- **Type Checking:** **Clean (0 errors)** (`npx tsc --noEmit`).
- **ESLint:** **Clean (0 errors)** (`npm run lint`).
- **Production Build:** **Clean compilation, 0 errors** (`npm run build`).
- **Total Automated Tests:** **98 / 98 passed (100% success rate)**.

---

### Section 10: Live Cloud Deployment

- **Status:** **Complete and verified**
- **Live Deployment Architecture:**
  - **Live Frontend App:** [https://link-sleuth-studio.onrender.com](https://link-sleuth-studio.onrender.com) (TanStack Start & Nitro SSR)
  - **Live Backend API:** [https://linkintel-api-4dvd.onrender.com](https://linkintel-api-4dvd.onrender.com) (FastAPI 0.115 on Uvicorn)
  - **API Health Check:** [https://linkintel-api-4dvd.onrender.com/health](https://linkintel-api-4dvd.onrender.com/health) (`{"status":"ok"}`)
  - **Interactive Swagger Docs:** [https://linkintel-api-4dvd.onrender.com/docs](https://linkintel-api-4dvd.onrender.com/docs)
  - **Managed Database:** Render PostgreSQL (`linkintel-db`) in Ohio (`us-east`) with connection pooling enabled.
  - Complete configuration and verification details are documented in [`docs/deployment.md`](docs/deployment.md).
