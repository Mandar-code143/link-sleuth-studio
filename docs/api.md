# LinkIntel AI — Backend API Reference & Contract Documentation

**Base URL (Local):** `http://localhost:4000`  
**Swagger UI:** `http://localhost:4000/docs`  
**ReDoc:** `http://localhost:4000/redoc`  
**OpenAPI Specification:** `http://localhost:4000/openapi.json`

---

## 1. Core Link Analysis Endpoint

### `POST /link-analysis`
Executes an end-to-end website intelligence analysis. Performs SSRF-safe fetching, technical SEO signal extraction, competitor search grounding, and LLM-driven business intelligence across all 5 mandatory dimensions.

#### Request Headers
- `Content-Type: application/json`
- `Accept: application/json`

#### Request Body
```json
{
  "url": "https://www.hubspot.com"
}
```

#### Successful Response (HTTP 200 OK)
```json
{
  "success": true,
  "website": "https://www.hubspot.com",
  "brand": {
    "name": "HubSpot",
    "category": "Customer Relationship Management (CRM) Platform",
    "summary": "HubSpot provides a complete cloud platform connecting sales, marketing, and customer service teams."
  },
  "analysis": {
    "competitor_analysis": {
      "overview": "HubSpot competes against leading CRM and marketing automation platforms with emphasis on inbound marketing.",
      "competitors": [
        {
          "name": "Salesforce",
          "website": "https://salesforce.com",
          "category": "Enterprise CRM",
          "description": "Comprehensive enterprise cloud CRM and application platform.",
          "strengths": ["Enterprise customization", "Massive ecosystem"],
          "gaps": ["Higher total cost of ownership", "Complex implementation"],
          "positioning": "High-end enterprise corporate CRM",
          "opportunity": "Win mid-market teams needing faster time-to-value.",
          "evidence": "verified",
          "source_urls": ["https://salesforce.com"],
          "confidence": 0.85
        }
      ],
      "strengths": ["All-in-one platform usability", "Strong content marketing ecosystem"],
      "weaknesses": ["Tiered pricing escalation at scale"],
      "advantages": ["Native integration across hubs", "Free tier onboarding"],
      "opportunities": ["AI agent automation across sales sequences"],
      "evidence": ["Homepage copy", "Pricing tier comparisons"]
    },
    "target_search_queries": [
      {
        "query": "best crm for growing sales teams",
        "platforms": ["Google"],
        "intent": "Commercial Investigation",
        "relevance": "Direct high-intent purchase keyword.",
        "audience": "Sales Directors and VP of Sales"
      },
      {
        "query": "how to scale inbound marketing lead generation",
        "platforms": ["LinkedIn"],
        "intent": "Informational",
        "relevance": "Matches core thought leadership topics.",
        "audience": "Growth Marketers and Demand Gen Leads"
      },
      {
        "query": "hubspot vs salesforce pricing comparison",
        "platforms": ["X"],
        "intent": "Comparative / Transactional",
        "relevance": "Bottom-of-funnel decision query.",
        "audience": "RevOps Leads and Operations Managers"
      },
      {
        "query": "marketing automation workflows for agencies",
        "platforms": ["Instagram"],
        "intent": "Visual Discovery / Commercial",
        "relevance": "Appeals to creative and agency partner tier.",
        "audience": "Agency Owners and Digital Strategists"
      },
      {
        "query": "small business customer retention tools",
        "platforms": ["Facebook"],
        "intent": "Community / Business Networking",
        "relevance": "Addresses SMB owner peer discussions.",
        "audience": "Small Business Founders and Operators"
      }
    ],
    "seo_improvements": {
      "primary_keyword": "inbound crm software",
      "secondary_keywords": ["marketing automation", "sales pipeline management", "help desk software"],
      "long_tail_keywords": ["all in one crm platform for growing teams"],
      "business_keywords": ["crm", "customer relationship management", "inbound marketing"],
      "current_title": "HubSpot | Inbound Marketing, Sales, and Service Software",
      "recommended_title": "HubSpot CRM | Inbound Marketing, Sales & Customer Service Platform",
      "title_reason": "Strengthens keyword density for 'CRM platform' while retaining brand equity.",
      "current_meta_description": "HubSpot offers a complete CRM platform with all the tools needed for marketing, sales, content management, and customer service.",
      "recommended_meta_description": "Scale your revenue with HubSpot's all-in-one CRM platform. Connect sales, marketing, and customer service tools with seamless AI workflows.",
      "business_summary": "Inbound customer relationship management platform connecting sales, marketing, and support teams.",
      "supporting_content": ["Inbound sales playbook", "Marketing automation workflows guide", "CRM migration checklist"],
      "technical_findings": [
        {
          "name": "Title Tag",
          "value": "HubSpot | Inbound Marketing, Sales, and Service Software",
          "status": "present",
          "note": "Title is present and within recommended character length (56 chars)."
        },
        {
          "name": "Meta Description",
          "value": "HubSpot offers a complete CRM platform...",
          "status": "present",
          "note": "Meta description is well formatted (134 chars)."
        },
        {
          "name": "HTTPS Protocol",
          "value": "https://www.hubspot.com",
          "status": "present",
          "note": "Site served securely over TLS/HTTPS."
        },
        {
          "name": "Robots Directives",
          "value": "index, follow",
          "status": "present",
          "note": "Crawling directives allow search indexing."
        }
      ],
      "search_volume_note": "Target queries reflect high commercial buyer intent in the CRM and MarTech space."
    },
    "top_services": [
      {
        "name": "Marketing Hub",
        "description": "Marketing automation, lead generation, analytics, and content management.",
        "target_industry": "B2B, SaaS, Agency, Ecommerce",
        "target_customer": "Marketing Directors and Demand Gen Teams",
        "benefit": "Attract and convert visitors into qualified leads.",
        "evidence": "extracted",
        "source": "Marketing Hub navigation section"
      },
      {
        "name": "Sales Hub",
        "description": "Sales CRM, deal tracking, email templates, and automated follow-ups.",
        "target_industry": "B2B SaaS, Mid-Market, Professional Services",
        "target_customer": "Account Executives and Sales Directors",
        "benefit": "Accelerate pipeline velocity and close deals faster.",
        "evidence": "extracted",
        "source": "Sales Hub overview copy"
      },
      {
        "name": "Service Hub",
        "description": "Customer support ticketing, knowledge base, and customer feedback surveys.",
        "target_industry": "Software, E-commerce, Telecom",
        "target_customer": "Customer Support Leads and Customer Success Managers",
        "benefit": "Improve customer retention and NPS scores.",
        "evidence": "extracted",
        "source": "Service Hub product specs"
      },
      {
        "name": "Content Hub",
        "description": "CMS software with drag-and-drop website builder and SEO tools.",
        "target_industry": "Digital Media, Corporate Communications",
        "target_customer": "Web Masters and Content Creators",
        "benefit": "Publish optimized web content without heavy IT dependency.",
        "evidence": "extracted",
        "source": "CMS / Content Hub page"
      },
      {
        "name": "Operations Hub",
        "description": "Data synchronization, programmable automation, and data quality curation.",
        "target_industry": "Enterprise, Scale-ups, FinTech",
        "target_customer": "RevOps Analysts and Database Administrators",
        "benefit": "Eliminate data silos between disparate business systems.",
        "evidence": "extracted",
        "source": "Operations Hub architecture doc"
      }
    ],
    "target_audience": {
      "primary_audience": "B2B Founders and Revenue Leaders scaling go-to-market teams",
      "secondary_audience": ["Mid-Market RevOps Managers", "Digital Marketing Agencies", "Customer Support Directors"],
      "industry_segments": ["SaaS & Software", "Professional Services", "E-commerce", "Financial Technology"],
      "business_types": ["High-Growth Startups", "Mid-Market Enterprises", "Agency Service Providers"],
      "profiles": [
        {
          "name": "The Scaling Revenue Leader",
          "business_type": "High-Growth B2B SaaS",
          "needs": ["Unified customer view across sales and marketing", "Predictable deal velocity", "Automated pipeline attribution"],
          "challenges": ["Disconnected point tools causing data silos", "Ramp-up friction for new sales reps", "Unclear lead quality signals"],
          "services": ["Marketing Hub", "Sales Hub"],
          "opportunity": "Standardize on an integrated tech stack to accelerate customer onboarding.",
          "evidence": "extracted"
        },
        {
          "name": "The Modern RevOps Architect",
          "business_type": "Mid-Market Enterprise",
          "needs": ["Clean two-way data sync with ERP", "Automated lead routing logic", "Compliance audit trails"],
          "challenges": ["Duplicate records across legacy databases", "Engineering backlog for CRM customization"],
          "services": ["Operations Hub", "Enterprise CRM Suite"],
          "opportunity": "Deploy no-code webhook automation and bidirectional sync.",
          "evidence": "extracted"
        }
      ],
      "geographic_focus": ["Global", "North America", "EMEA", "APAC"],
      "needs": ["CRM integration", "Inbound lead capture", "Pipeline visibility", "Lifecycle reporting"],
      "challenges": ["Tool sprawl", "High customer churn", "Inconsistent lead follow-up"],
      "interests": ["Inbound methodology", "AI-assisted sales cadence", "Conversion rate optimization"],
      "marketing_segments": ["Tech Startup Founders", "Enterprise Marketing Executives", "Digital Transformation Leads"]
    }
  },
  "metadata": {
    "report_id": "rep-4a92c311",
    "analyzed_at": "2026-11-24T12:00:00.000Z",
    "page_title": "HubSpot | Inbound Marketing, Sales, and Service Software",
    "canonical_url": "https://www.hubspot.com",
    "extraction_warnings": [],
    "sample_data": false,
    "model": "gemini-2.5-flash"
  }
}
```

#### Error Responses
- **HTTP 400 Bad Request:** Missing or invalid URL schema (`http/https`).
- **HTTP 403 Forbidden / SSRF Blocked:** Prohibited target (e.g. localhost, private RFC1918 IP, AWS metadata `169.254.169.254`).
- **HTTP 502 Bad Gateway:** Remote server unreachable, DNS lookup failed, or redirect loop detected.
- **HTTP 503 Service Unavailable:** AI provider not configured (`GEMINI_API_KEY` missing).

---

## 2. Health & Readiness Endpoints

### `GET /health`
Liveness probe returning operational status.
```json
{
  "status": "healthy",
  "service": "linkintel-backend",
  "version": "1.0.0",
  "timestamp": "2026-11-24T12:00:00Z"
}
```

### `GET /health/ready`
Readiness probe verifying API key configuration, search provider status, and environment health.
```json
{
  "status": "ready",
  "service": "linkintel-backend",
  "version": "1.0.0",
  "provider": "gemini",
  "model": "gemini-2.5-flash",
  "provider_key_configured": true,
  "search_provider_configured": true,
  "warnings": [],
  "timestamp": "2026-11-24T12:00:00Z"
}
```

---

## 3. Multi-Model Research Lab Endpoints

### `GET /models/status`
Returns live configuration status, default models, context windows, and official published pricing for Gemini, OpenAI, and Anthropic.
```json
{
  "providers": [
    {
      "provider": "gemini",
      "name": "Google Gemini",
      "model": "gemini-2.5-flash",
      "configured": true,
      "input_rate_per_million": 0.15,
      "output_rate_per_million": 0.60,
      "context_window": "1,048,576 tokens",
      "structured_output_mode": "Native Pydantic Schema Mode",
      "pricing_source": "https://ai.google.dev/gemini-api/docs/pricing"
    },
    {
      "provider": "openai",
      "name": "OpenAI",
      "model": "gpt-4o-mini",
      "configured": false,
      "input_rate_per_million": 0.15,
      "output_rate_per_million": 0.60,
      "context_window": "128,000 tokens",
      "structured_output_mode": "JSON Object / Structured Outputs",
      "pricing_source": "https://developers.openai.com/api/docs/pricing"
    },
    {
      "provider": "anthropic",
      "name": "Anthropic Claude",
      "model": "claude-3-5-haiku-20241022",
      "configured": false,
      "input_rate_per_million": 0.80,
      "output_rate_per_million": 4.00,
      "context_window": "200,000 tokens",
      "structured_output_mode": "Messages API JSON Schema Enforcement",
      "pricing_source": "https://platform.claude.com/docs/en/about-claude/pricing"
    }
  ],
  "default_provider": "gemini",
  "recommended_model": "gemini-2.5-flash",
  "timestamp": "2026-11-24T12:00:00Z"
}
```

### `POST /benchmark/run`
Executes an on-demand comparative benchmark across the specified LLM models. Calculates response latency, token consumption, microdollar costs, schema compliance, and dimensional completeness.

#### Request Body
```json
{
  "url": "https://acmecloud.example",
  "providers": ["gemini", "openai", "anthropic"],
  "mock_mode": false
}
```

#### Response (HTTP 200 OK)
Returns array of model benchmark results, dimension scores (0-100%), and recommended winner.
