# LinkIntel AI — Evidence & Artifact Index

This directory contains visual screenshots and sanitized API request/response logs demonstrating the working implementation of **LinkIntel AI** in satisfaction of the Dxora Technologies Python Practical Test.

---

## 1. Visual Screenshots Index

All screenshots were captured from the running application across desktop (`1440x900` / `1280x800`) and mobile (`390x844` iPhone 14/15 profile) viewports using automated headless Chrome.

| Item # | Screenshot File                                                                      | Viewport         | Demonstrated Application Capability                                                                                                                                              |
| ------ | ------------------------------------------------------------------------------------ | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **01** | [`01-overview-desktop.png`](01-overview-desktop.png)                                 | Desktop (1440px) | Overview dashboard with hero banner, live target inspection presets, evaluator quick-check verification cards, 5-deliverable bento grid, and backend status footer.              |
| **01** | [`01-overview-mobile.png`](01-overview-mobile.png)                                   | Mobile (390px)   | Mobile responsive overview with compact cards and 64px fixed bottom navigation bar (`pb-safe`).                                                                                  |
| **02** | [`02-analyze-desktop.png`](02-analyze-desktop.png)                                   | Desktop (1440px) | Website inspection form with real-time URL validation, 5-dimension preview cards, live pipeline checklist, and resilience edge-case simulator.                                   |
| **02** | [`02-analyze-mobile.png`](02-analyze-mobile.png)                                     | Mobile (390px)   | Mobile analysis input with stacked touch buttons (`min-h-[48px]`) and security notices.                                                                                          |
| **03** | [`03-report-overview-desktop.png`](03-report-overview-desktop.png)                   | Desktop (1440px) | Completed Analysis Report header with verification pills, Raw JSON modal trigger, PDF/CSV export dropdown, and 3 Executive Summary Bento cards.                                  |
| **03** | [`03-report-overview-mobile.png`](03-report-overview-mobile.png)                     | Mobile (390px)   | Mobile report layout with responsive metadata badges and touch-friendly export triggers.                                                                                         |
| **04** | [`04-report-competitors-desktop.png`](04-report-competitors-desktop.png)             | Desktop (1440px) | Competitor Analysis section featuring competitor vs brand comparison table with subject brand highlight, evidence badges, and source links.                                      |
| **05** | [`05-report-queries-seo-desktop.png`](05-report-queries-seo-desktop.png)             | Desktop (1280px) | Target Search Queries (5 queries across Google, LinkedIn, X, Instagram, Facebook) and SEO Before/After Title & Meta Description Diff with technical findings checklist.          |
| **06** | [`06-report-services-audience-desktop.png`](06-report-services-audience-desktop.png) | Tablet (1024px)  | Top Services catalog cards with customer benefits and Target Audience buyer personas.                                                                                            |
| **07** | [`07-model-research-desktop.png`](07-model-research-desktop.png)                     | Desktop (1440px) | Model Research Lab with 3 provisioned engine cards (Gemini 2.5 Flash, GPT-4o-mini, Claude 3.5 Haiku), multi-model test rig, evaluation matrix, and cost burn projection bars.    |
| **07** | [`07-model-research-mobile.png`](07-model-research-mobile.png)                       | Mobile (390px)   | Mobile Model Research view with compact engine specs and vertical test controls.                                                                                                 |
| **08** | [`08-history-desktop.png`](08-history-desktop.png)                                   | Desktop (1440px) | Analysis History repository with keyword search, status filters, sort order, and report cards.                                                                                   |
| **08** | [`08-history-mobile.png`](08-history-mobile.png)                                     | Mobile (390px)   | Mobile audit history feed with delete actions and direct report view.                                                                                                            |
| **09** | [`09-settings-desktop.png`](09-settings-desktop.png)                                 | Desktop (1440px) | Settings with runtime execution mode toggle (Live vs Sample), backend host ping test, 4 endpoint health pills, zero-secret exposure AI orchestration, and multi-tenancy manager. |
| **09** | [`09-settings-mobile.png`](09-settings-mobile.png)                                   | Mobile (390px)   | Mobile settings layout with responsive wrap and cache purge controls.                                                                                                            |
| **10** | [`10-swagger-docs-desktop.png`](10-swagger-docs-desktop.png)                         | Desktop (1440px) | Live interactive FastAPI Swagger UI documentation rendered at `/docs` displaying all System, Model Lab, and Analysis endpoints.                                                  |

---

## 2. Sanitized API Evidence Files

| File                                                               | Content Description                                                                                                |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [`sample-request.json`](sample-request.json)                       | Valid `POST /link-analysis` JSON payload specifying target website URL.                                            |
| [`sample-response.json`](sample-response.json)                     | Complete, structured 200 OK JSON response demonstrating all 5 business intelligence sections and request metadata. |
| [`validation-error-response.json`](validation-error-response.json) | Structured 400 Bad Request response showing SSRF security policy rejection of private/loopback IP address.         |
| [`health-check-response.json`](health-check-response.json)         | Sanitized JSON output from `/health` (liveness) and `/health/ready` (deep readiness without secret exposure).      |
