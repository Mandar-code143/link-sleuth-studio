# Initial Codebase Audit: LinkIntel AI (Link Sleuth Studio)

**Date:** November 18, 2026  
**Auditor:** Senior Software Architect & Principal Full-Stack Engineer  
**Repository:** `https://github.com/Mandar-code143/link-sleuth-studio`  
**Working Directory:** `C:\Users\manda\Downloads\link-sleuth-studio-main`  
**Target Specification:** Dxora Technologies Python Practical Test — Link Analysis

---

## 1. Executive Summary

This codebase is being transformed from the initial scaffold (**Link Sleuth Studio**) into **LinkIntel AI**, a complete website intelligence platform satisfying all requirements of the Dxora Technologies Python Practical Test. The project features a modern React 19 frontend utilizing TanStack Start, TanStack Router, TanStack Query, Tailwind CSS v4, Lucide icons, and Shadcn UI components.

The audit reveals high-value, comprehensive frontend components and data schemas already present in `src/components/linkintel-app.tsx` and `src/lib/linkintel.ts`. However, several critical architectural components were missing or unlinked:

1. The root route (`src/routes/index.tsx`) was a blank Lovable placeholder rather than mounting the fully developed `DashboardPage`.
2. Dedicated routes for `/analyze`, `/history`, `/reports/$id`, `/model-lab`, and `/settings` were not yet wired as file-based routes in `src/routes/`.
3. The custom CSS classes powering the rich UI shell, badges, grids, metrics, and report tabs required complete stylistic definitions in `src/styles.css`.
4. The Python/FastAPI backend (`backend/`) was completely absent, requiring full implementation of safe HTTP fetching with SSRF protection, content extraction via Trafilatura and BeautifulSoup, LLM intelligence across the 5 mandatory sections, structured JSON validation, cost tracking, caching, and comprehensive test suites.

The core engineering rule for this project is: **EXTEND, DO NOT REBUILD**. All existing types, components, branding, and interfaces will be preserved and strengthened.

---

## 2. Existing Architecture & Directory Map

```
link-sleuth-studio-main/
├── .gitignore
├── .lovable/
│   └── project.json
├── .prettierignore
├── .prettierrc
├── AGENTS.md                 # Lovable integration rules: do not rewrite published git history
├── bun.lock                  # Bun lockfile from initial scaffolding
├── bunfig.toml
├── components.json           # Shadcn UI configuration
├── eslint.config.js          # ESLint 9 configuration
├── package.json              # React 19, Vite 8, TanStack Start, Tailwind v4
├── public/
│   ├── favicon.ico
│   └── robots.txt
├── README.md                 # Initial placeholder README
├── roadmap.md                # Development roadmap
├── src/
│   ├── components/
│   │   ├── linkintel-app.tsx # Core UI: Dashboard, Analyze, Report, History, ModelLab, Settings
│   │   └── ui/               # 38 Shadcn UI component primitives (Button, Card, Tabs, etc.)
│   ├── hooks/
│   │   └── use-mobile.tsx    # Mobile viewport detection hook
│   ├── lib/
│   │   ├── error-capture.ts  # Runtime error capture
│   │   ├── error-page.ts     # Error boundary display
│   │   ├── linkintel.ts      # Core data contract, API client, demo report, history manager
│   │   ├── lovable-error-reporting.ts # Telemetry wrapper
│   │   └── utils.ts          # clsx + twMerge helper
│   ├── routes/
│   │   ├── __root.tsx        # App root shell, query client provider, error component
│   │   ├── index.tsx         # [DEFECT] Blank placeholder image route
│   │   └── README.md         # TanStack Start routing conventions
│   ├── router.tsx            # Router instantiation with QueryClient context
│   ├── routeTree.gen.ts      # Auto-generated route tree (TanStack Router)
│   ├── server.ts             # SSR server entry point
│   ├── start.ts              # TanStack Start instance options
│   ├── styles.css            # Tailwind CSS v4 entry + OKLCH design tokens
│   └── test/
│       ├── app-routing.test.tsx # Basic router match test
│       └── setup.ts          # Testing library setup
├── tsconfig.json             # TypeScript configuration with @ alias
├── vite.config.ts            # Vite + TanStack Start configuration
└── vitest.config.ts          # Vitest configuration
```

---

## 3. Detailed Component & Contract Analysis

### 3.1 Data Contracts (`src/lib/linkintel.ts`)

The TypeScript contract defines the exact target response model for the backend:

- `Evidence`: `"extracted" | "inferred" | "verified"`
- `Brand`: `name`, `category`, `summary`
- `Competitor`: `name`, `website`, `category`, `description`, `strengths`, `gaps`, `positioning`, `opportunity`, `evidence`, `source_urls`, `confidence`
- `SearchQuery`: `query`, `platforms`, `intent`, `relevance`, `audience`
- `SeoSignal`: `name`, `value`, `status ("present" | "missing" | "potential_issue" | "not_inspected")`, `note`
- `ServiceInsight`: `name`, `description`, `target_industry`, `target_customer`, `benefit`, `evidence`, `source`
- `AudienceProfile`: `name`, `business_type`, `needs`, `challenges`, `services`, `opportunity`, `evidence`
- `LinkAnalysis`:
  - `success`: boolean
  - `website`: string
  - `brand`: `Brand`
  - `analysis`:
    - `competitor_analysis`: `overview`, `competitors[]`, `strengths[]`, `weaknesses[]`, `advantages[]`, `opportunities[]`, `evidence[]`
    - `target_search_queries`: `SearchQuery[]` (exactly 5)
    - `seo_improvements`: `primary_keyword`, `secondary_keywords[]`, `long_tail_keywords[]`, `business_keywords[]`, `current_title`, `recommended_title`, `title_reason`, `current_meta_description`, `recommended_meta_description`, `business_summary`, `supporting_content[]`, `technical_findings: SeoSignal[]`, `search_volume_note`
    - `top_services`: `ServiceInsight[]` (up to 5)
    - `target_audience`: `primary_audience`, `secondary_audience[]`, `industry_segments[]`, `business_types[]`, `profiles: AudienceProfile[]`, `geographic_focus[]`, `needs[]`, `challenges[]`, `interests[]`, `marketing_segments[]`
  - `metadata`: `report_id`, `analyzed_at`, `page_title`, `canonical_url`, `extraction_warnings[]`, `sample_data: boolean`, `model: string | null`

### 3.2 Existing UI Modules (`src/components/linkintel-app.tsx`)

The file contains an end-to-end interface implementation with 6 exported main screens and numerous sub-components:

- `DashboardPage`: Overview metrics, hero analysis form, recent analyses list, workspace mode toggle (Sample vs Live API), feature overview cards.
- `AnalyzePage`: Full URL input form with validation, steps breakdown, live vs sample badges, security notice.
- `ReportPage`: 5 interactive tabs:
  1. **Competitors**: Market framing, competitive cards, data table, advantages, opportunities, gaps, sources list.
  2. **Search queries**: 5 queries with intent filtering, platform badges (Google, Facebook, Instagram, LinkedIn, X), relevance descriptions.
  3. **SEO analysis**: Primary & secondary keyword chips, current vs recommended meta title & description with copy buttons, supporting content ideas, technical signal grid.
  4. **Top services**: Grid of identified services with target industry, target customer, customer benefit, evidence badge, source links.
  5. **Target audience**: Primary & secondary audience banners, persona cards, industry segments, business types, geographic focus, needs, challenges, marketing segments.
  - Report actions: View/Hide JSON preview, Copy full JSON, Export downloadable JSON report file.
- `HistoryPage`: LocalStorage-persisted analysis log, keyword search, status filter, category filter, date sort, view report link, delete confirmation modal.
- `ModelLabPage`: Provider comparison (Google Gemini, OpenAI, Anthropic Claude), model evaluation criteria, benchmark plan, cost optimization strategy.
- `SettingsPage`: Sample vs Live API mode switch, FastAPI base URL input, live `/health` connection test button, CLI command snippet, API `/docs` link.

### 3.3 Routing Architecture

- Router framework: TanStack Start with Vite TanStack plugin.
- Conventions: `src/routes/` file-based routing.
- Identified issue: Only `src/routes/index.tsx` was present, rendering a Lovable placeholder image.
- Required routes:
  - `/` -> `src/routes/index.tsx` rendering `DashboardPage`
  - `/analyze` -> `src/routes/analyze.tsx` rendering `AnalyzePage`
  - `/history` -> `src/routes/history.tsx` rendering `HistoryPage`
  - `/reports/$id` -> `src/routes/reports/$id.tsx` rendering `ReportPage`
  - `/model-lab` -> `src/routes/model-lab.tsx` rendering `ModelLabPage`
  - `/settings` -> `src/routes/settings.tsx` rendering `SettingsPage`

### 3.4 Styling System

- Tailwind CSS v4 with `@theme inline` and OKLCH color spaces.
- Dark mode custom variants.
- The UI in `src/components/linkintel-app.tsx` utilizes specific semantic class names (`app-frame`, `analysis-hero`, `data-table`, `status-pill`, `metric-card`, `query-row`, etc.) which will be given comprehensive definitions in `src/styles.css` matching the sleek design intent.

---

## 4. Planned Backend Architecture (`backend/`)

The Python backend will be built strictly following the Dxora requirements:

- Framework: Python 3.10+, FastAPI, Uvicorn, Pydantic v2.
- Directory Structure:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, CORS, routes, exception handlers
│   ├── config.py                 # Pydantic Settings (env vars)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py             # POST /link-analysis, GET /health
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py            # LinkAnalysisRequest (URL validation)
│   │   └── response.py           # LinkAnalysisResponse matching TypeScript interface
│   ├── security/
│   │   ├── __init__.py
│   │   ├── url_validator.py      # Scheme, hostname, port, domain structure
│   │   ├── dns_validator.py      # IP & CIDR blocking (IPv4/IPv6 private, loopback, link-local, cloud metadata)
│   │   └── safe_fetcher.py       # Pinned DNS socket / custom safe HTTPX transport
│   ├── services/
│   │   ├── __init__.py
│   │   ├── website_extractor.py  # Trafilatura + BeautifulSoup HTML extraction
│   │   ├── content_cleaner.py    # Boilerplate removal & prompt injection defense
│   │   ├── seo_service.py        # Technical signals (Title, Meta, H1, OG, Canonical)
│   │   ├── analysis_service.py   # Analysis orchestrator assembling all 5 sections
│   │   ├── competitor_service.py # Competitor analysis & candidate generation
│   │   ├── cost_service.py       # Token usage & published pricing calculator
│   │   └── research_service.py   # Extensible competitor discovery provider
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py               # BaseLLMProvider interface
│   │   ├── gemini.py             # Google GenAI / Gemini provider
│   │   ├── openai.py             # OpenAI provider
│   │   └── anthropic.py          # Anthropic Claude provider
│   └── utils/
│       ├── __init__.py
│       ├── logging.py            # Structured logging with request IDs
│       └── cache.py              # In-memory TTL cache with URL normalization
├── tests/
│   ├── __init__.py
│   ├── test_api.py               # Health & endpoint integration tests
│   ├── test_security.py          # SSRF, private IPs, DNS rebinding, malformed URLs
│   ├── test_extractor.py         # Trafilatura & BeautifulSoup parsing
│   ├── test_llm.py               # Provider adapters & prompt handling
│   └── test_analysis.py          # 5-section schema validation
├── docs/
│   ├── architecture.md
│   ├── security.md
│   ├── llm-research.md
│   └── benchmark-results.md
├── examples/
│   ├── request.json
│   └── response.json
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

---

## 5. File Inventory & Action Plan

### Files to Preserve

- `package.json`, `bun.lock`, `vite.config.ts`, `tsconfig.json`, `components.json`
- `src/components/linkintel-app.tsx` (all UI screens, logic, and state management)
- `src/lib/linkintel.ts` (data contract, local storage history, API client)
- `src/components/ui/*` (all 38 Shadcn UI component files)
- `src/routes/__root.tsx`, `src/router.tsx`, `src/server.ts`, `src/start.ts`
- `AGENTS.md` (no history rewrites on Lovable branch)

### Files to Modify

- `src/routes/index.tsx` (replace blank placeholder with `DashboardPage`)
- `src/styles.css` (add full layout, responsive design, and component styles)
- `src/test/app-routing.test.tsx` (expand test coverage to all routes)
- `README.md` (replace starter template with comprehensive production documentation)

### Files to Create

- Frontend routes:
  - `src/routes/analyze.tsx`
  - `src/routes/history.tsx`
  - `src/routes/reports/$id.tsx`
  - `src/routes/model-lab.tsx`
  - `src/routes/settings.tsx`
- Complete Python backend: `backend/app/...`, `backend/tests/...`, `backend/docs/...`, `backend/Dockerfile`, `backend/requirements.txt`, etc.
- Documentation: `docs/deployment.md`, `docs/implementation-status.md`.

---

## 6. Verification Milestones

1. **Frontend Verification**: Clean build with `pnpm run build`, lint with `pnpm run lint`, route tests passing with `pnpm run test`.
2. **Backend Verification**: Install backend dependencies, run unit & security tests with `pytest`, verify `/health` and `/docs`.
3. **End-to-End Integration**: Test `POST /link-analysis` from frontend in Live API mode, verify report rendering across all 5 tabs, verify history persistence, and verify error boundaries.
