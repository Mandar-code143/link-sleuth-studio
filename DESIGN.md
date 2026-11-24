# LinkIntel Studio Precision — Design System & Visual Specification

This document defines the visual architecture, typography, token taxonomy, responsive layouts, and component primitives for **LinkIntel AI (LinkIntel Studio Precision)**.

---

## 1. Core Visual Identity & Philosophy

LinkIntel AI is an intelligence workstation designed for senior analysts, digital strategists, and business leaders. The interface conveys cryptographic trust, high-density clarity, and effortless responsive navigation across desktop, tablet, and mobile form factors.

- **Design Philosophy**: High-density intelligence without clutter. Clean Bento grid structures, precise 1px borders, subtle interactive elevation, and unambiguous evidence lineage tags.
- **Surface Elevation**: Layered white surfaces over a cool, distraction-free neutral canvas (`#F6F7FB`).
- **Interactive State**: Predictable focus rings, subtle smooth transitions (150ms-200ms ease), and zero jarring layout shifts.

---

## 2. Color Palette & Design Tokens

### Primary & Functional Colors
| Token Name | Hex Code | Purpose / Usage |
| :--- | :--- | :--- |
| **Primary (Brand Indigo)** | `#4355E8` | Key interactive actions, active navigation states, primary focus rings |
| **Primary Hover** | `#2538D0` | Hover state for buttons and primary touch points |
| **Primary Subtly Tinted** | `#EEF0FD` | Active tab highlights, badge backgrounds, selected sidebar row |
| **Accent (Interactive Purple)** | `#6475FF` | Metric sparklines, AI generation gradients, highlights |
| **Canvas / Background** | `#F6F7FB` | Main workspace background (`bg-[#F6F7FB]`) |
| **Surface (Card / Sheet)** | `#FFFFFF` | Bento cards, table surfaces, modals, popovers |
| **Borders & Dividers** | `#E5E7EF` | Structural borders (`border-[#E5E7EF]`), subtle cell dividers |
| **Surface Hover** | `#F8F9FC` | Table row hover, secondary button hover |

### Typography & Text Hierarchy
| Token Name | Hex Code | Usage |
| :--- | :--- | :--- |
| **Text Primary** | `#141B2C` | Headings, card titles, key values, active nav items |
| **Text Secondary / Muted** | `#475467` | Subheadings, descriptions, metadata labels, breadcrumbs |
| **Text Tertiary / Disabled** | `#98A2B3` | Disabled buttons, inactive icons, helper text |

### Evidence Pill & Status Taxonomy
Every claim or insight presented in LinkIntel AI is tagged with its provenance level:

| Provenance Level | Badge Background | Text / Border | Description |
| :--- | :--- | :--- | :--- |
| **Verified** | `#E6F5F2` | `#0F9D83` | Ground truth confirmed from extracted DOM signals or official pricing specs |
| **Extracted** | `#EEF0FD` | `#4355E8` | Directly scraped and parsed from target website HTML/content |
| **Inferred** | `#FEF6EE` | `#D98B27` | Synthesized by LLM reasoning from extracted evidence |
| **Critical / Review** | `#FEF3F2` | `#D84C4C` | Missing critical SEO tag, blocked outbound request, or security alert |

---

## 3. Typography Scale & Font Families

LinkIntel AI pairs geometric strength with legible tabular clarity:
- **Headings & Metrics**: `Manrope`, sans-serif (weights 600, 700, 800)
- **Body & UI Elements**: `Inter`, sans-serif (weights 400, 500, 600)
- **Tabular Data, Code & Tokens**: `JetBrains Mono`, monospace (weights 400, 500)

```css
/* Typography Scale */
--text-xs:   0.75rem / 1.00rem; /* 12px / 16px */
--text-sm:   0.875rem / 1.25rem; /* 14px / 20px */
--text-base: 1.00rem / 1.50rem; /* 16px / 24px */
--text-lg:   1.125rem / 1.75rem; /* 18px / 28px */
--text-xl:   1.25rem / 1.75rem; /* 20px / 28px */
--text-2xl:  1.50rem / 2.00rem; /* 24px / 32px */
--text-3xl:  1.875rem / 2.25rem; /* 30px / 36px */
```

---

## 4. Layout Architecture & Responsive Breakpoints

### 8px Grid System
All margins, paddings, and component dimensions adhere to multiples of 8px (with 4px half-grid increments for dense micro-controls):
- `p-2` / `m-2`: 8px
- `p-4` / `m-4`: 16px
- `p-6` / `m-6`: 24px
- `p-8` / `m-8`: 32px
- `gap-3`: 12px
- `gap-4`: 16px
- `gap-6`: 24px

### Responsive Breakpoints
| Viewport | Width | Layout Behavior |
| :--- | :--- | :--- |
| **Desktop** | `>= 1024px` (`lg:`) | 240px fixed left sidebar, 56px topbar, multi-column bento grids, sticky tab headers |
| **Tablet** | `768px – 1023px` (`md:`) | Compact collapsible navigation, 2-column bento grids, horizontal scroll tab bars |
| **Mobile** | `< 768px` | Fixed 56px compact topbar, single-column vertical stack, 5-destination bottom navigation bar, touch-friendly 44px+ hit targets |

### Fixed Navigation Dimensions
- **Desktop Sidebar Width**: 240px (`w-60`)
- **Global Topbar Height**: 56px (`h-14`)
- **Mobile Bottom Navigation Bar Height**: 64px (`h-16`) with safe area padding for iOS/Android home indicators
- **Mobile Main Content Bottom Padding**: `pb-24` to prevent bottom nav overlap

---

## 5. Mobile Bottom Navigation Spec
Mobile navigation features 5 touch-optimized destinations:
1. **Overview** (`LayoutDashboard`): Executive status, recent reports, quick entry
2. **Analyze** (`SearchCode`): URL submission, engine configuration, live crawl progress
3. **History** (`History`): Database-backed searchable report archive
4. **Model Lab** (`Cpu`): Provider benchmarks, latency/cost comparisons
5. **Settings** (`Settings`): Backend endpoint selection, workspace isolation, API key diagnostics

---

## 6. Deliverable Cards (5 Dimensions)
Reports render five structured dimensions with consistent header, evidence lineage pill, copy/export controls, and content inspection:
1. **Competitor Comparison**: Direct competitors, strategic advantages, market gaps, positioning statements.
2. **Search Query Opportunities**: 5 platform distributions (Google, YouTube, LinkedIn, X, Reddit/Instagram) with intent and relevance.
3. **Actionable SEO Recommendations**: Title tag & meta description proposals, primary/secondary/long-tail keywords, technical audit findings.
4. **Core Services & Value Propositions**: Service offerings, target buyers, explicit business benefits, extraction quotes.
5. **Target Audience Profiles**: Buyer personas, operational pain points, recommended services, engagement opportunities.
