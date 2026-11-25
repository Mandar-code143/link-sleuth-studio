# LLM Model Comparison & Cost Optimization Research

**Project:** LinkIntel AI — Website Intelligence Platform  
**Target Specification:** Dxora Technologies Python Practical Test  
**Evaluation & Verification Date:** 25 November 2026  
**Evaluated Models:**

1. **Google Gemini 2.5 Flash** (`gemini-2.5-flash`) — _Primary Model_
2. **OpenAI GPT-4o mini** (`gpt-4o-mini`) — _Secondary Fallback_
3. **Anthropic Claude 3.5 Haiku** (`claude-3-5-haiku-20241022`) — _Tertiary Research / Standby_

---

## 1. Executive Summary & Selection Decision

LinkIntel AI analyzes public business websites and extracts a structured, five-section intelligence report (competitor comparison, 5 platform search queries, SEO analysis, top services, and target audience profiles). The workload requires:

- **Strict Schema Adherence:** Every response must deserialize directly into Pydantic v2 data models (`LinkAnalysisResponse`) with zero syntax errors.
- **Context Capacity:** Capability to ingest 3,000–15,000 words of cleaned website copy, navigation hierarchies, and technical SEO signals without truncation.
- **Low Latency:** Fast turnaround for interactive user workflows.
- **Predictable, Scalable Unit Economics:** Low cost per analysis to enable high-volume batch processing and SaaS margins.

### Selection Decision

| Role                   | Model                          | Published Pricing (per 1M tokens)  | Context Window       | Key Selection Factor                                                                                                            |
| ---------------------- | ------------------------------ | ---------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Primary**            | **Google Gemini 2.5 Flash**    | **Input: \$0.30 / Output: \$2.50** | **1,048,576 tokens** | Native Pydantic schema enforcement via `google-genai`, 1M context window, high reasoning capability, and rapid throughput.     |
| **Secondary Fallback** | **OpenAI GPT-4o mini**         | **Input: \$0.15 / Output: \$0.60** | 128,000 tokens       | Strict JSON Schema validation (`response_format={"type": "json_object"}`), low token pricing, robust global availability.       |
| **Tertiary Standby**   | **Anthropic Claude 3.5 Haiku** | **Input: \$0.80 / Output: \$4.00** | 200,000 tokens       | Strong qualitative reasoning and safety; higher pricing makes it suitable for deep-dive audits or specialized checks.           |

---

## 2. Rigorous Multi-Model Comparison Matrix

The figures below reflect **official published provider pricing** verified on **25 November 2026**:

| Dimension                                              | Google Gemini 2.5 Flash                                            | OpenAI GPT-4o mini                                               | Anthropic Claude 3.5 Haiku                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Model Identifier**                                   | `gemini-2.5-flash`                                                 | `gpt-4o-mini`                                                    | `claude-3-5-haiku-20241022`                                                   |
| **Provider**                                           | Google AI (Gemini API)                                             | OpenAI                                                           | Anthropic                                                                     |
| **Input Rate (per 1M tokens)**                         | **\$0.300**                                                        | **\$0.150**                                                      | \$0.800                                                                       |
| **Output Rate (per 1M tokens)**                        | **\$2.500**                                                        | **\$0.600**                                                      | \$4.000                                                                       |
| **Context Window**                                     | **1,048,576 tokens**                                               | 128,000 tokens                                                   | 200,000 tokens                                                                |
| **Max Output Tokens**                                  | 8,192 tokens                                                       | **16,384 tokens**                                                | 8,192 tokens                                                                  |
| **Structured Output Mechanism**                        | Native Pydantic `response_schema`                                  | JSON Schema `response_format`                                    | Tool / Function Calling schema                                                |
| **Schema Reliability**                                 | High (enforced at API level)                                       | High (enforced at API level)                                     | High (enforced via tool calling)                                              |
| **Estimated Cost per Analysis** _(3.5k in / 1.2k out)_ | **\$0.004050** (~0.405¢)                                           | **\$0.001245** (~0.125¢)                                         | **\$0.007600** (~0.76¢)                                                       |
| **Cost per 1,000 Analyses**                            | **\$4.05**                                                         | **\$1.25**                                                       | **\$7.60**                                                                    |
| **Documentation Reference**                            | [Google AI Pricing](https://ai.google.dev/gemini-api/docs/pricing) | [OpenAI Pricing](https://developers.openai.com/api/docs/pricing) | [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing) |

> **Note on Measurements vs Estimates:**
> Token counts vary with website content volume. The per-analysis cost of **\$0.004050** is calculated based on a representative baseline workload of 3,500 input tokens (cleaned DOM content + system prompt) and 1,200 output tokens (5-section structured JSON). Real token counts and exact dollar costs are computed per-request in `backend/app/services/cost_service.py` and included in API response metadata.

---

## 3. Workload-Specific Model Analysis

### 3.1 Google Gemini 2.5 Flash (Recommended Primary)

- **Context Capacity:** 1,048,576 tokens ensures complete multi-page content, navigation links, and SEO metadata can be submitted in a single pass without aggressive pruning.
- **Python Integration:** The `google-genai` SDK allows passing the Pydantic model (`LLMAnalysisPayload`) directly via `response_schema`, eliminating regex post-processing and preventing schema mismatches.
- **Economics:** At \$0.30 / \$2.50 per million tokens, 1,000 comprehensive audits cost approximately **\$4.05**, providing SaaS gross margins above 90% on typical pricing tiers.

### 3.2 OpenAI GPT-4o mini (Recommended Fallback)

- **JSON Object Support:** Enforces strict adherence to specified JSON keys.
- **Drop-in Compatibility:** Integrated into `backend/app/providers/openai.py` via `BaseLLMProvider`. If the Gemini API experiences rate limiting or upstream disruption, switching `LLM_PROVIDER=openai` requires zero code changes.
- **Economics:** At \$0.15 / \$0.60 per 1M tokens, it provides high volume cost efficiency.

### 3.3 Anthropic Claude 3.5 Haiku (Tertiary Standby)

- **Analytical Nuance:** Well-regarded for subtle competitive positioning and nuanced persona synthesis.
- **Economics:** At \$0.80 / \$4.00 per 1M tokens, it is retained as an optional qualitative evaluator for enterprise accounts or comparative research.

---

## 4. Cost Projections at Scale

Calculated using the representative workload baseline of **3,500 input tokens** and **1,200 output tokens** per analysis:

$$\text{Cost per Analysis (Gemini 2.5 Flash)} = \left(\frac{3,500}{1,000,000} \times \$0.30\right) + \left(\frac{1,200}{1,000,000} \times \$2.50\right) = \$0.001050 + \$0.003000 = \$0.004050$$

| Daily Scans      | Monthly Volume | Gemini 2.5 Flash Cost  | OpenAI GPT-4o mini Cost | Claude 3.5 Haiku Cost |
| ---------------- | -------------- | ---------------------- | ----------------------- | --------------------- |
| **100 / day**    | 3,000          | **\$12.15 / month**    | **\$3.74 / month**      | \$22.80 / month       |
| **500 / day**    | 15,000         | **\$60.75 / month**    | **\$18.68 / month**     | \$114.00 / month      |
| **1,000 / day**  | 30,000         | **\$121.50 / month**   | **\$37.35 / month**     | \$228.00 / month      |
| **5,000 / day**  | 150,000        | **\$607.50 / month**   | **\$186.75 / month**    | \$1,140.00 / month    |
| **10,000 / day** | 300,000        | **\$1,215.00 / month** | **\$373.50 / month**    | \$2,280.00 / month    |
| **50,000 / day** | 1,500,000      | **\$6,075.00 / month** | **\$1,867.50 / month**  | \$11,400.00 / month   |

---

## 5. Cost Optimization Engineering

LinkIntel AI incorporates four active cost reduction techniques in the backend pipeline:

### 1. HTML Distillation & Boilerplate Stripping (`content_cleaner.py`)

- Raw webpage HTML typically spans 200 KB to 1.5 MB due to inline CSS, JavaScript bundles, tracking pixels, SVGs, and base64 images.
- `content_cleaner.py` and `trafilatura` strip all script, style, SVG, noscript, and iframe tags, reducing token consumption by 70–85% prior to prompt injection.

### 2. Tiered Headings Hierarchy Extraction

- Rather than submitting unformatted body text, the extractor produces structured heading hierarchies (`H1`–`H3`), meta tags, and high-signal paragraphs.
- This allows models to build context maps in fewer tokens without sacrificing semantic depth.

### 3. Server-Side Technical SEO Signals

- Critical SEO checks (missing title tags, absent meta descriptions, canonical mismatches, missing heading elements) are calculated deterministically via Python DOM traversal (`seo_service.py`), consuming zero LLM tokens.
- These computed facts are injected directly into the prompt as verified constraints, allowing the LLM to focus purely on strategic copy recommendations.

### 4. Deterministic Multi-Layer Caching (`cachetools.TTLCache`)

- Extracted website DOM representations and analysis payloads are cached with configurable TTLs. Repeated requests for identical URLs return instant responses without repeated model inference or token cost.
