export type Evidence = "extracted" | "inferred" | "verified";

export interface Brand {
  name: string;
  category: string;
  summary: string;
}

export interface Competitor {
  name: string;
  website: string;
  category: string;
  description: string;
  strengths: string[];
  gaps: string[];
  positioning: string;
  opportunity: string;
  evidence: Evidence;
  source_urls: string[];
  confidence: number | null;
}

export interface SearchQuery {
  query: string;
  platforms: string[];
  intent: string;
  relevance: string;
  audience: string;
}

export interface SeoSignal {
  name: string;
  value: string | null;
  status: "present" | "missing" | "potential_issue" | "not_inspected";
  note: string;
}

export interface ServiceInsight {
  name: string;
  description: string;
  target_industry: string;
  target_customer: string;
  benefit: string;
  evidence: Evidence;
  source: string | null;
}

export interface AudienceProfile {
  name: string;
  business_type: string;
  needs: string[];
  challenges: string[];
  services: string[];
  opportunity: string;
  evidence: Evidence;
}

export interface LinkAnalysis {
  success: boolean;
  website: string;
  brand: Brand;
  analysis: {
    competitor_analysis: {
      overview: string;
      competitors: Competitor[];
      strengths: string[];
      weaknesses: string[];
      advantages: string[];
      opportunities: string[];
      evidence: string[];
    };
    target_search_queries: SearchQuery[];
    seo_improvements: {
      primary_keyword: string;
      secondary_keywords: string[];
      long_tail_keywords: string[];
      business_keywords: string[];
      current_title: string | null;
      recommended_title: string;
      title_reason: string;
      current_meta_description: string | null;
      recommended_meta_description: string;
      business_summary: string;
      supporting_content: string[];
      technical_findings: SeoSignal[];
      search_volume_note: string;
    };
    top_services: ServiceInsight[];
    target_audience: {
      primary_audience: string;
      secondary_audience: string[];
      industry_segments: string[];
      business_types: string[];
      profiles: AudienceProfile[];
      geographic_focus: string[];
      needs: string[];
      challenges: string[];
      interests: string[];
      marketing_segments: string[];
    };
  };
  metadata: {
    report_id: string;
    analyzed_at: string;
    page_title: string | null;
    canonical_url: string | null;
    extraction_warnings: string[];
    sample_data: boolean;
    model: string | null;
  };
}

export interface HistoryEntry {
  id: string;
  website: string;
  brand: string;
  category: string;
  analyzedAt: string;
  status: "completed" | "failed";
  sample: boolean;
}

export interface AppPreferences {
  mode: "demo" | "live";
  apiBaseUrl: string;
}

export const DEFAULT_API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() || "http://localhost:4000";

export const DEMO_REPORT: LinkAnalysis = {
  success: true,
  website: "https://northstarstudio.example",
  brand: {
    name: "Northstar Studio",
    category: "Brand strategy & digital design",
    summary:
      "A fictional independent studio helping early-stage teams clarify their brand and build thoughtful digital experiences. This sample illustrates how extracted business details and clearly marked strategic inferences appear in a LinkIntel report.",
  },
  analysis: {
    competitor_analysis: {
      overview:
        "Illustrative market framing based on the fictional studio profile; suggestions are not verified competitors.",
      competitors: [
        {
          name: "Sample competitor — brand consultancy",
          website: "https://example.com",
          category: "Brand consultancy",
          description:
            "A hypothetical positioning example, included only to demonstrate the report format.",
          strengths: ["Clear specialist positioning"],
          gaps: ["No independent source review in demo mode"],
          positioning: "Established strategic partner",
          opportunity: "Differentiate with a transparent, founder-led process.",
          evidence: "inferred",
          source_urls: [],
          confidence: null,
        },
      ],
      strengths: ["A focused, end-to-end offer"],
      weaknesses: ["Sample-only assessment; not a live competitive audit"],
      advantages: ["Combines brand strategy with digital design"],
      opportunities: ["Make project outcomes and process easier to compare"],
      evidence: [],
    },
    target_search_queries: [
      {
        query: "brand strategy for early-stage startups",
        platforms: ["Google", "LinkedIn"],
        intent: "Commercial",
        relevance: "Connects the stated studio offer with a high-intent need.",
        audience: "Startup founders",
      },
      {
        query: "startup brand identity design studio",
        platforms: ["Google", "Instagram"],
        intent: "Service discovery",
        relevance: "Pairs the intended audience with a core service.",
        audience: "Early-stage teams",
      },
      {
        query: "how to position a new business",
        platforms: ["Google", "LinkedIn"],
        intent: "Informational",
        relevance: "A useful educational entry point for prospective clients.",
        audience: "New business owners",
      },
      {
        query: "website design for growing startups",
        platforms: ["Google", "Instagram"],
        intent: "Commercial",
        relevance: "Reflects the digital experience part of the sample offer.",
        audience: "Startup teams",
      },
      {
        query: "brand messaging workshop for founders",
        platforms: ["Google", "LinkedIn", "X"],
        intent: "Transactional",
        relevance: "A specific service-led query grounded in the sample positioning.",
        audience: "Startup founders",
      },
    ],
    seo_improvements: {
      primary_keyword: "brand strategy for startups",
      secondary_keywords: ["startup brand identity", "brand messaging workshop"],
      long_tail_keywords: ["brand strategy studio for early-stage startups"],
      business_keywords: ["brand strategy", "digital design"],
      current_title: null,
      recommended_title: "Brand Strategy for Startups | Northstar Studio",
      title_reason: "States the audience and service before the studio name.",
      current_meta_description: null,
      recommended_meta_description:
        "Build a clearer brand and digital experience with Northstar Studio, a strategy-led creative partner for early-stage teams.",
      business_summary: "Brand strategy and digital design for early-stage teams.",
      supporting_content: [
        "Brand strategy service page",
        "Founder brand-positioning guide",
        "Frequently asked questions about the studio process",
      ],
      technical_findings: [
        {
          name: "Title tag",
          value: null,
          status: "not_inspected",
          note: "No website was fetched in demo mode.",
        },
        {
          name: "Meta description",
          value: null,
          status: "not_inspected",
          note: "No website was fetched in demo mode.",
        },
        {
          name: "H1 heading",
          value: null,
          status: "not_inspected",
          note: "No website was fetched in demo mode.",
        },
        {
          name: "Canonical URL",
          value: null,
          status: "not_inspected",
          note: "No website was fetched in demo mode.",
        },
        {
          name: "Open Graph",
          value: null,
          status: "not_inspected",
          note: "No website was fetched in demo mode.",
        },
        {
          name: "Image alt text",
          value: null,
          status: "not_inspected",
          note: "No website was fetched in demo mode.",
        },
      ],
      search_volume_note: "No verified search-volume data available.",
    },
    top_services: [
      {
        name: "Brand strategy",
        description: "A sample strategic engagement to clarify positioning and direction.",
        target_industry: "Early-stage businesses",
        target_customer: "Founders",
        benefit: "A more coherent foundation for growth.",
        evidence: "inferred",
        source: null,
      },
      {
        name: "Visual identity",
        description: "A sample identity system aligned to the business strategy.",
        target_industry: "Early-stage businesses",
        target_customer: "Growing teams",
        benefit: "More consistent brand communication.",
        evidence: "inferred",
        source: null,
      },
      {
        name: "Digital experience design",
        description: "A sample website design engagement.",
        target_industry: "Digital-first businesses",
        target_customer: "Startup teams",
        benefit: "A clearer online experience.",
        evidence: "inferred",
        source: null,
      },
    ],
    target_audience: {
      primary_audience: "Founders of early-stage businesses",
      secondary_audience: ["Small in-house marketing teams", "Independent product teams"],
      industry_segments: ["Technology", "Professional services"],
      business_types: ["Startups", "Small businesses"],
      profiles: [
        {
          name: "The early-stage founder",
          business_type: "New startup",
          needs: ["A clear brand position", "A credible first website"],
          challenges: ["Limited time", "Unclear differentiation"],
          services: ["Brand strategy", "Visual identity"],
          opportunity: "Lead with a focused, outcome-oriented discovery offer.",
          evidence: "inferred",
        },
        {
          name: "The growing product team",
          business_type: "Digital-first business",
          needs: ["Consistent brand expression", "A more useful web experience"],
          challenges: ["Siloed design decisions", "An evolving audience"],
          services: ["Digital experience design"],
          opportunity: "Show how strategy and delivery connect.",
          evidence: "inferred",
        },
      ],
      geographic_focus: [],
      needs: ["Clear differentiation", "A credible digital presence"],
      challenges: ["Limited internal resources", "Messaging uncertainty"],
      interests: ["Brand positioning", "Product growth", "Digital design"],
      marketing_segments: [
        "Pre-launch founders",
        "Recently funded teams",
        "Small businesses refreshing their identity",
      ],
    },
  },
  metadata: {
    report_id: "sample-northstar-01",
    analyzed_at: "2026-11-18T09:00:00.000Z",
    page_title: "Northstar Studio — sample report",
    canonical_url: null,
    extraction_warnings: [
      "Sample report only. No external website or competitor was fetched or verified.",
    ],
    sample_data: true,
    model: null,
  },
};

const HISTORY_KEY = "linkintel.history.v1";
const REPORT_KEY_PREFIX = "linkintel.report.v1.";
const PREFS_KEY = "linkintel.preferences.v1";

function storageAvailable() {
  return typeof window !== "undefined" && window.localStorage !== undefined;
}

export function readHistory(): HistoryEntry[] {
  if (!storageAvailable()) return [];
  try {
    const parsed: unknown = JSON.parse(window.localStorage.getItem(HISTORY_KEY) || "[]");
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item): item is HistoryEntry => {
      if (!item || typeof item !== "object") return false;
      const value = item as Partial<HistoryEntry>;
      return (
        typeof value.id === "string" &&
        typeof value.website === "string" &&
        typeof value.brand === "string" &&
        typeof value.analyzedAt === "string" &&
        (value.status === "completed" || value.status === "failed")
      );
    });
  } catch {
    return [];
  }
}

export function saveReport(report: LinkAnalysis): HistoryEntry {
  const id = report.metadata.report_id || crypto.randomUUID();
  const entry: HistoryEntry = {
    id,
    website: report.website,
    brand: report.brand.name,
    category: report.brand.category,
    analyzedAt: report.metadata.analyzed_at,
    status: "completed",
    sample: report.metadata.sample_data,
  };
  if (storageAvailable()) {
    const reports = readHistory().filter((item) => item.id !== id);
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify([entry, ...reports]));
    window.localStorage.setItem(`${REPORT_KEY_PREFIX}${id}`, JSON.stringify(report));
  }
  return entry;
}

export function getReport(id: string): LinkAnalysis | null {
  if (id === DEMO_REPORT.metadata.report_id) return DEMO_REPORT;
  if (!storageAvailable()) return null;
  try {
    const raw = window.localStorage.getItem(`${REPORT_KEY_PREFIX}${id}`);
    return raw ? (JSON.parse(raw) as LinkAnalysis) : null;
  } catch {
    return null;
  }
}

export function deleteReport(id: string) {
  if (!storageAvailable()) return;
  window.localStorage.setItem(
    HISTORY_KEY,
    JSON.stringify(readHistory().filter((item) => item.id !== id)),
  );
  window.localStorage.removeItem(`${REPORT_KEY_PREFIX}${id}`);
}

export function readPreferences(): AppPreferences {
  if (!storageAvailable()) return { mode: "demo", apiBaseUrl: DEFAULT_API_BASE_URL };
  try {
    const value: unknown = JSON.parse(window.localStorage.getItem(PREFS_KEY) || "null");
    if (value && typeof value === "object") {
      const prefs = value as Partial<AppPreferences>;
      return {
        mode: prefs.mode === "live" ? "live" : "demo",
        apiBaseUrl:
          typeof prefs.apiBaseUrl === "string" && prefs.apiBaseUrl.trim()
            ? prefs.apiBaseUrl.trim().replace(/\/+$/, "")
            : DEFAULT_API_BASE_URL,
      };
    }
  } catch {
    // Corrupted preferences return to safe demo mode.
  }
  return { mode: "demo", apiBaseUrl: DEFAULT_API_BASE_URL };
}

export function savePreferences(preferences: AppPreferences) {
  if (storageAvailable()) window.localStorage.setItem(PREFS_KEY, JSON.stringify(preferences));
}

export function validateWebsiteUrl(value: string): string | null {
  if (!value.trim()) return "Enter a website address to continue.";
  try {
    const url = new URL(value.trim());
    if (!new Set(["http:", "https:"]).has(url.protocol))
      return "Use a website address beginning with http:// or https://.";
    if (!url.hostname.includes(".")) return "Enter a complete domain, such as example.com.";
    return null;
  } catch {
    return "Enter a valid website address, such as https://example.com.";
  }
}

export async function analyzeWebsite(
  url: string,
  preferences: AppPreferences,
): Promise<LinkAnalysis> {
  if (preferences.mode === "demo") {
    await new Promise((resolve) => window.setTimeout(resolve, 700));
    return DEMO_REPORT;
  }
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 90_000);
  try {
    const response = await fetch(`${preferences.apiBaseUrl}/link-analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ url }),
      signal: controller.signal,
    });
    const payload: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      let detailMsg = `The analysis service returned ${response.status}.`;
      if (payload && typeof payload === "object" && "detail" in payload) {
        const detail = (payload as { detail: unknown }).detail;
        if (typeof detail === "string") {
          detailMsg = detail;
        } else if (detail && typeof detail === "object") {
          const det = detail as Record<string, unknown>;
          if (typeof det.message === "string") {
            detailMsg = det.error_code ? `[${det.error_code}] ${det.message}` : det.message;
          } else {
            detailMsg = JSON.stringify(detail);
          }
        }
      }
      throw new Error(detailMsg);
    }
    if (
      !payload ||
      typeof payload !== "object" ||
      !("success" in payload) ||
      payload.success !== true ||
      !("analysis" in payload) ||
      !("brand" in payload)
    ) {
      throw new Error("The API response did not match the expected report format.");
    }
    return payload as LinkAnalysis;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("The analysis took too long. Check the API service and try again.");
    }
    if (error instanceof TypeError) {
      throw new Error(
        `Could not reach the live API at ${preferences.apiBaseUrl}. Check the address and that the Python service is running.`,
      );
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export interface ApiHealthStatus {
  reachable: boolean;
  status: "ready" | "degraded" | "healthy" | "offline";
  service?: string;
  version?: string;
  provider?: string;
  model?: string;
  providerKeyConfigured?: boolean;
  searchProviderConfigured?: boolean;
  warnings?: string[];
  errorKind?: "connection_refused" | "cors" | "timeout" | "server_error" | "invalid_response";
  errorMessage?: string;
}

export async function checkApiHealthDetailed(apiBaseUrl: string): Promise<ApiHealthStatus> {
  const normalized = apiBaseUrl.trim().replace(/\/+$/, "");
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 6000);
  try {
    let res = await fetch(`${normalized}/health/ready`, {
      signal: controller.signal,
      headers: { Accept: "application/json" },
    }).catch(() => null);

    if (!res || res.status === 404) {
      res = await fetch(`${normalized}/health`, {
        signal: controller.signal,
        headers: { Accept: "application/json" },
      }).catch(() => null);
    }

    if (!res) {
      return {
        reachable: false,
        status: "offline",
        errorKind: "connection_refused",
        errorMessage: `Could not reach ${normalized}. Ensure the backend service is running.`,
      };
    }

    if (!res.ok && res.status >= 500) {
      return {
        reachable: true,
        status: "offline",
        errorKind: "server_error",
        errorMessage: `Backend returned HTTP ${res.status}. Check backend logs.`,
      };
    }

    const data = await res.json().catch(() => null);
    if (!data || typeof data !== "object") {
      return {
        reachable: true,
        status: "offline",
        errorKind: "invalid_response",
        errorMessage: "API responded with non-JSON content.",
      };
    }

    const payload = data as Record<string, unknown>;
    const providerKeyConfigured = Boolean(
      payload.provider_key_present ?? payload.provider_key_configured ?? false,
    );
    const searchConfigured = Boolean(payload.search_provider_configured ?? false);
    const isReady =
      payload.status === "ready" || (payload.status === "healthy" && providerKeyConfigured);

    return {
      reachable: true,
      status: isReady ? "ready" : "degraded",
      service: typeof payload.service === "string" ? payload.service : undefined,
      version: typeof payload.version === "string" ? payload.version : undefined,
      provider: typeof payload.provider === "string" ? payload.provider : undefined,
      model: typeof payload.model === "string" ? payload.model : undefined,
      providerKeyConfigured,
      searchProviderConfigured: searchConfigured,
      warnings: Array.isArray(payload.warnings) ? (payload.warnings as string[]) : [],
    };
  } catch (err) {
    const isAbort = err instanceof DOMException && err.name === "AbortError";
    return {
      reachable: false,
      status: "offline",
      errorKind: isAbort ? "timeout" : "connection_refused",
      errorMessage: isAbort
        ? `Request timed out reaching ${normalized}.`
        : `Network error reaching ${normalized}. Check CORS settings or connection.`,
    };
  } finally {
    window.clearTimeout(timer);
  }
}

export async function checkApiHealth(apiBaseUrl: string): Promise<boolean> {
  const result = await checkApiHealthDetailed(apiBaseUrl);
  return result.reachable;
}

export interface ProviderStatusItem {
  provider: string;
  name: string;
  model: string;
  configured: boolean;
  input_rate_per_million: number;
  output_rate_per_million: number;
  context_window: string;
  pricing_source: string;
}

export interface ProviderStatusResponse {
  providers: ProviderStatusItem[];
  default_provider: string;
  recommended_model: string;
  timestamp: string;
}

export interface BenchmarkRunRequest {
  url?: string;
  providers?: string[];
  mock_mode?: boolean;
}

export interface ModelBenchmarkResult {
  provider: string;
  model: string;
  status: "success" | "unconfigured" | "error";
  latency_ms: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  cost_per_thousand_analyses_usd: number;
  schema_valid: boolean;
  completeness_score: number;
  quality_score: number;
  extracted_brand?: string | null;
  error_message?: string | null;
  dimension_scores: {
    competitors: number;
    search_queries: number;
    seo: number;
    services: number;
    target_audience: number;
  };
}

export interface BenchmarkRunResponse {
  benchmark_id: string;
  timestamp: string;
  target_url: string;
  results: ModelBenchmarkResult[];
  recommended_winner: string;
  recommendation_rationale: string;
}

export async function fetchProviderStatus(apiBaseUrl: string): Promise<ProviderStatusResponse> {
  const normalized = apiBaseUrl.trim().replace(/\/+$/, "");
  const response = await fetch(`${normalized}/models/status`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch model status (HTTP ${response.status})`);
  }
  return response.json();
}

export async function runModelBenchmark(
  apiBaseUrl: string,
  request: BenchmarkRunRequest = {},
): Promise<BenchmarkRunResponse> {
  const normalized = apiBaseUrl.trim().replace(/\/+$/, "");
  const response = await fetch(`${normalized}/benchmark/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => null);
    const msg =
      err && typeof err === "object" && "detail" in err
        ? typeof err.detail === "object" && err.detail?.message
          ? err.detail.message
          : String(err.detail)
        : `Benchmark failed (HTTP ${response.status})`;
    throw new Error(msg);
  }
  return response.json();
}
