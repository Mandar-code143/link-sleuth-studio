# LinkIntel AI — Frontend Design Decisions & Stitch Integration Matrix

This document details the architectural decisions, component hierarchy, Stitch prototype reconciliation, and creative UI/UX enhancements made while integrating the Google Stitch design system into LinkIntel AI.

---

## 1. Reference Architecture & Stitch Mapping

The user provided 12 Stitch design exports covering desktop and mobile viewports for all 6 core workstation routes. Each export was extracted, inspected, and mapped to native React 19 + TypeScript + TanStack Router components:

| Route Path | Viewport | Source Stitch Export | Implemented React Component / Route |
| :--- | :--- | :--- | :--- |
| `/` (Overview) | Desktop | `desktop_overview` (`stitch_linkintel_ai_workstation.zip`) | `src/routes/index.tsx` + `DashboardBento` |
| `/` (Overview) | Mobile | `mobile_overview` (`stitch_linkintel_ai_workstation (7).zip`) | `src/routes/index.tsx` (responsive mobile view) |
| `/analyze` | Desktop | `desktop_analyze` (`stitch_linkintel_ai_workstation (1).zip`) | `src/routes/analyze.tsx` + `AnalysisConsole` |
| `/analyze` | Mobile | `mobile_analyze` (`stitch_linkintel_ai_workstation (8).zip`) | `src/routes/analyze.tsx` (responsive touch flow) |
| `/report` | Desktop | `desktop_report` (`stitch_linkintel_ai_workstation (2).zip`) | `src/routes/report.tsx` + `ReportStudio` |
| `/report` | Mobile | `mobile_report` (`stitch_linkintel_ai_workstation (6).zip`) | `src/routes/report.tsx` (sticky section navigation) |
| `/models` (Model Lab) | Desktop | `desktop_model_research` (`stitch_linkintel_ai_workstation (3).zip`) | `src/routes/models.tsx` + `ModelBenchmarkingSuite` |
| `/models` (Model Lab) | Mobile | `mobile_model_research` (`stitch_linkintel_ai_workstation (11).zip`) | `src/routes/models.tsx` (touch-optimized runner) |
| `/history` | Desktop | `desktop_history` (`stitch_linkintel_ai_workstation (4).zip`) | `src/routes/history.tsx` + `HistoryArchiveTable` |
| `/history` | Mobile | `mobile_history` (`stitch_linkintel_ai_workstation (10).zip`) | `src/routes/history.tsx` (responsive cards list) |
| `/settings` | Desktop | `desktop_settings` (`stitch_linkintel_ai_workstation (5).zip`) | `src/routes/settings.tsx` + `WorkspaceSettings` |
| `/settings` | Mobile | `mobile_settings` (`stitch_linkintel_ai_workstation (9).zip`) | `src/routes/settings.tsx` (compact settings stack) |

---

## 2. Filtering Prototype Inaccuracies

The Stitch static prototypes contained several hardcoded assumptions, fictional metrics, and disconnected prototype simulations. These were systematically replaced with real application truth:

| Inaccuracy in Stitch Prototype | Correction in LinkIntel AI Production Integration |
| :--- | :--- |
| **Hardcoded `localhost:8000`** | Replaced with dynamic, user-configurable `preferences.apiBaseUrl` (defaults to backend port `4000`, supports remote production URLs). |
| **Fictional Telemetry / Latency** | Removed fake "14ms", "99.98% uptime", and "44 DOM blocks" claims. Connected directly to real server latency (`performance.now()`), actual token counts, and live cost calculation. |
| **Stale / Fictional Model Identifiers** | Replaced hardcoded references to `Gemini 1.5 Pro` and `GPT-4o` with the verified active models: `gemini-2.5-flash`, `gpt-4o-mini`, and `claude-3-5-haiku-20241022`. |
| **Simulated `setTimeout` Crawl Loops** | Replaced fake UI timeouts with genuine reactive async HTTP fetch requests to `/link-analysis` with real-time AbortController cancellation. |
| **Standalone Tailwind CDN** | Removed prototype CDN script tags (`<script src="https://cdn.tailwindcss.com">`). Embedded the design tokens directly into Tailwind CSS 4 theme rules in `src/styles.css`. |
| **Fictional Playwright Cluster Claims** | Cleaned up marketing copy claiming headless Playwright clusters; accurately documented safe HTTPX + Trafilatura + BeautifulSoup SSRF-guarded pipeline. |

---

## 3. Creative UI/UX Enhancements Beyond Stitch

Where the Stitch prototype was static or bare, LinkIntel AI introduced genuine architectural and user experience improvements:

1. **Database-Backed Persistent Archiving (Phase 10)**:
   - Stitch prototypes only kept records in ephemeral UI memory.
   - LinkIntel AI features persistent SQLite/PostgreSQL storage with `ReportRecord` and `BenchmarkRecord`.
   - History and Dashboard live-query the backend `/reports` and `/benchmarks` endpoints, ensuring analysis reports persist across browser sessions and devices.
2. **Workspace Isolation (`X-Workspace-Id`)**:
   - Added multi-tenant workspace isolation. Users can create, switch, and filter reports by workspace without leaking sensitive client intelligence across accounts.
3. **Evaluator Quick-Check Bar**:
   - Enhanced the overview dashboard with one-click test target presets (`stripe.com`, `linear.app`, `supabase.com`, `notion.so`) for rapid reviewer grading and evaluation.
4. **Interactive Evidence Pill Filter**:
   - In the Report view, users can click to filter insights by provenance (`verified`, `extracted`, `inferred`), giving analysts instant clarity on which claims are backed by raw DOM content versus LLM synthesis.
5. **Universal Export & Raw JSON Modals**:
   - Real client-side Markdown, CSV, and raw JSON export capabilities formatted to Dxora grading specifications.
6. **Mobile-First Touch Ergonomics**:
   - Added sticky mobile section navigation pills (`Overview`, `Competitors`, `Queries`, `SEO`, `Services`, `Audience`), 48px min touch targets, and iOS home-indicator safe-area offsets.

---

## 4. Single Source of Truth Responsive Philosophy

Desktop and mobile viewports are powered by the **exact same underlying data models and API services** (`src/lib/linkintel.ts`).
- When an analysis runs on mobile, it sends the exact same payload to `/link-analysis` and renders the exact same five-dimension data structure.
- When a report is deleted on desktop, it disappears from the mobile history view via synchronized backend persistence.
- There is zero divergence between mobile and desktop intelligence metrics.
