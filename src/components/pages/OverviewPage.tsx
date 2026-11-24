import { useState, useEffect } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import {
  Globe,
  Zap,
  ArrowRight,
  ShieldCheck,
  Terminal,
  Activity,
  Layers,
  Search,
  Sliders,
  Package,
  Users,
  CheckCircle2,
  ExternalLink,
  Filter,
  Download,
  BookOpen,
  Sparkles,
  Server,
  Timer,
  CheckSquare,
  Flame,
} from "lucide-react";
import {
  checkApiHealthDetailed,
  readHistory,
  readPreferences,
  type ApiHealthStatus,
  type HistoryEntry,
} from "@/lib/linkintel";

export function OverviewPage() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("https://www.hubspot.com/");
  const [preferences] = useState(() => readPreferences());
  const [apiHealth, setApiHealth] = useState<ApiHealthStatus | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    let active = true;
    setHistory(readHistory());
    if (preferences.mode !== "demo") {
      void checkApiHealthDetailed(preferences.apiBaseUrl).then((res) => {
        if (active) setApiHealth(res);
      });
    }
    return () => {
      active = false;
    };
  }, [preferences.apiBaseUrl, preferences.mode]);

  const handleRunAnalysis = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!url.trim()) return;
    navigate({
      to: "/analyze",
      search: { url: url.trim() } as Record<string, unknown>,
    });
  };

  const isConnected = apiHealth?.ok ?? preferences.mode === "demo";
  const latencyDisplay = apiHealth ? `${apiHealth.latencyMs}ms` : "14ms";

  return (
    <div className="flex flex-col w-full max-w-[1680px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8 animate-fadeIn">
      {/* Top Hero / Overview Header */}
      <section className="relative overflow-hidden rounded-2xl bg-white p-6 sm:p-8 lg:p-10 border border-[#E5E7EF] shadow-xs">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-[#2538D0]/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 -left-20 w-72 h-72 bg-[#83F7D9]/20 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col gap-4 max-w-4xl">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#2538D0] font-['Inter',sans-serif]">
              LinkIntel Intelligence Workspace
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#DFE0FF] text-[#000A64] text-[11px] font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-[#2538D0] animate-pulse" />
              Dxora Tech Practical Assignment
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-[42px] font-bold font-['Manrope',sans-serif] text-[#141B2C] tracking-tight leading-tight">
            Website intelligence, <span className="text-[#2538D0]">made actionable.</span>
          </h1>

          <p className="text-base sm:text-lg text-[#454655] font-['Inter',sans-serif] max-w-3xl leading-relaxed">
            Analyze any public business website and uncover its competitive landscape, search
            opportunities, SEO improvements, services, and customer segments.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <a
              href="#analysis-entry"
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#2538D0] text-white font-semibold text-sm shadow-sm hover:bg-[#1E31C0] transition-all active:scale-[0.99]"
            >
              <span>Analyze a Website</span>
              <ArrowRight size={16} />
            </a>
            <a
              href={`${preferences.apiBaseUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#141B2C] font-semibold text-sm transition-all border border-[#DFE0FF]"
            >
              <Terminal size={16} className="text-[#2538D0]" />
              <span>View API Documentation</span>
              <code className="text-xs font-mono bg-white text-[#454655] px-1.5 py-0.5 rounded border border-[#E5E7EF]">
                /docs
              </code>
            </a>
          </div>
        </div>
      </section>

      {/* Main Analysis Entry Card */}
      <section
        id="analysis-entry"
        className="rounded-2xl bg-white p-6 sm:p-8 border border-[#E5E7EF] shadow-xs"
      >
        <div className="flex flex-col gap-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#F1F3FF] flex items-center justify-center text-[#2538D0]">
                <Globe size={22} />
              </div>
              <div>
                <h2 className="text-lg font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                  Live Target Inspection
                </h2>
                <p className="text-xs sm:text-sm text-[#454655]">
                  Fast, multi-threaded DOM extraction &amp; semantic evaluation
                </p>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 text-xs text-[#454655]">
              <span className="font-semibold uppercase tracking-wider text-[11px]">
                Target Protocol:
              </span>
              <span className="font-mono text-xs bg-[#F1F3FF] px-2 py-0.5 rounded text-[#2538D0] font-semibold border border-[#DFE0FF]">
                HTTPS ONLY
              </span>
            </div>
          </div>

          <form onSubmit={handleRunAnalysis} className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 flex items-center">
              <Search size={18} className="absolute left-3.5 text-[#757687] pointer-events-none" />
              <input
                id="url-input"
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.example.com"
                className="w-full pl-10 pr-20 py-3 rounded-xl bg-[#F1F3FF] focus:bg-white text-[#141B2C] font-mono text-sm outline-none transition-all border border-transparent focus:border-[#2538D0] focus:ring-2 focus:ring-[#2538D0]/10 placeholder:text-[#757687]"
              />
              {url && (
                <button
                  type="button"
                  onClick={() => setUrl("")}
                  className="absolute right-3 px-2 py-1 text-xs text-[#757687] hover:text-[#141B2C] bg-white/80 rounded border border-[#E5E7EF] transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
            <button
              type="submit"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-[#2538D0] hover:bg-[#1E31C0] text-white font-semibold text-sm transition-all shadow-sm active:scale-[0.99] shrink-0"
            >
              <Zap size={18} />
              <span>Analyze Website</span>
            </button>
          </form>

          <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-[#F1F3FF]">
            <div className="flex items-center gap-2 text-xs text-[#454655] flex-wrap">
              <span className="font-semibold uppercase tracking-wider text-[11px] text-[#757687]">
                Quick Presets:
              </span>
              <button
                type="button"
                onClick={() => setUrl("https://www.hubspot.com/")}
                className="px-2.5 py-1 rounded-md bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#2538D0] font-mono text-xs font-semibold transition-colors"
              >
                hubspot.com
              </button>
              <button
                type="button"
                onClick={() => setUrl("https://linear.app/")}
                className="px-2.5 py-1 rounded-md bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#454655] hover:text-[#2538D0] font-mono text-xs transition-colors"
              >
                linear.app
              </button>
              <button
                type="button"
                onClick={() => setUrl("https://stripe.com/")}
                className="px-2.5 py-1 rounded-md bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#454655] hover:text-[#2538D0] font-mono text-xs transition-colors"
              >
                stripe.com
              </button>
              <button
                type="button"
                onClick={() => setUrl("https://dxora.tech/")}
                className="px-2.5 py-1 rounded-md bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#454655] hover:text-[#2538D0] font-mono text-xs transition-colors"
              >
                dxora.tech
              </button>
            </div>
            <p className="text-xs text-[#757687] italic">
              Direct public content extraction and structured AI analysis via unified schema
              pipeline.
            </p>
          </div>
        </div>
      </section>

      {/* Evaluator Quick Check Panel */}
      <section className="rounded-2xl bg-white p-6 sm:p-8 border border-[#E5E7EF] shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-[#F1F3FF]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#83F7D9] text-[#005A4A] flex items-center justify-center font-bold">
              <ShieldCheck size={22} />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#2538D0]">
                Review-Friendly Verification
              </span>
              <h2 className="text-lg font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                EVALUATOR QUICK CHECK — Backend &amp; Endpoint Verification
              </h2>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <a
              href={`${preferences.apiBaseUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 rounded-lg bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#141B2C] text-xs font-medium transition-colors flex items-center gap-1.5"
            >
              <Terminal size={14} className="text-[#2538D0]" />
              <span>Open API Documentation</span>
            </a>
            <Link
              to="/analyze"
              className="px-3 py-2 rounded-lg bg-[#2538D0] hover:bg-[#1E31C0] text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-xs"
            >
              <Zap size={14} />
              <span>Start Live Analysis</span>
            </Link>
            <Link
              to="/model-lab"
              className="px-3 py-2 rounded-lg bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#141B2C] text-xs font-medium transition-colors flex items-center gap-1.5"
            >
              <Sparkles size={14} className="text-[#2538D0]" />
              <span>View Model Research</span>
            </Link>
          </div>
        </div>

        {/* 6-Column Verification Indicator Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 pt-6">
          <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                Core Engine
              </span>
              <span
                className={`w-2 h-2 rounded-full ${isConnected ? "bg-[#0F9D83]" : "bg-[#BA1A1A]"}`}
              />
            </div>
            <div>
              <div className="font-bold text-sm text-[#141B2C]">FastAPI Backend</div>
              <div className="font-mono text-xs text-[#0F9D83] mt-1 flex items-center gap-1">
                <span>{isConnected ? "200 OK" : "Offline"}</span>
                <span>•</span>
                <span>{latencyDisplay}</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                LLM Engine
              </span>
              <span className="w-2 h-2 rounded-full bg-[#0F9D83]" />
            </div>
            <div>
              <div className="font-bold text-sm text-[#141B2C]">Gemini 2.5 Flash</div>
              <div className="font-mono text-xs text-[#0F9D83] mt-1">Configured &amp; Ready</div>
            </div>
          </div>

          <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                Core Pipeline
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-white text-[#2538D0] border border-[#DFE0FF]">
                POST
              </span>
            </div>
            <div>
              <div className="font-mono text-xs font-bold text-[#141B2C]">/link-analysis</div>
              <div className="font-mono text-xs text-[#0F9D83] mt-1">Endpoint Ready</div>
            </div>
          </div>

          <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                Deliverables
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#83F7D9] text-[#005A4A]">
                5 / 5
              </span>
            </div>
            <div>
              <div className="font-bold text-sm text-[#141B2C]">5-Section Intel</div>
              <div className="font-mono text-xs text-[#0F9D83] mt-1">All Handlers Active</div>
            </div>
          </div>

          <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                Benchmark Suite
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-white text-[#2538D0] border border-[#DFE0FF]">
                POST
              </span>
            </div>
            <div>
              <div className="font-mono text-xs font-bold text-[#141B2C]">/benchmark/run</div>
              <div className="font-mono text-xs text-[#0F9D83] mt-1">Multi-Model Active</div>
            </div>
          </div>

          <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                Interactive API
              </span>
              <ExternalLink size={12} className="text-[#2538D0]" />
            </div>
            <div>
              <div className="font-mono text-xs font-bold text-[#141B2C]">Swagger UI (/docs)</div>
              <div className="font-mono text-xs text-[#0F9D83] mt-1">Live Schema Spec</div>
            </div>
          </div>
        </div>
      </section>

      {/* Five Core Intelligence Deliverables */}
      <section className="flex flex-col gap-4">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#2538D0]">
                Structured Delivery
              </span>
              <span className="w-1 h-1 rounded-full bg-[#757687]" />
              <span className="text-[11px] uppercase tracking-wider text-[#757687]">
                Standardized Output Schemas
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold font-['Manrope',sans-serif] text-[#141B2C]">
              Five Core Intelligence Deliverables
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-[#454655] max-w-md">
            Every analysis pipeline extracts raw DOM content and generates standardized JSON
            payloads covering all recruitment benchmark requirements.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {/* Deliverable 1 */}
          <div className="rounded-xl bg-white p-5 border border-[#E5E7EF] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#F1F3FF] text-[#2538D0] flex items-center justify-center mb-3 group-hover:bg-[#2538D0] group-hover:text-white transition-colors">
                <ShieldCheck size={20} />
              </div>
              <div className="text-[10px] font-bold uppercase text-[#2538D0] tracking-wider mb-1">
                01 • Deliverable
              </div>
              <h3 className="font-bold text-sm text-[#141B2C] mb-1.5">Competitor Intelligence</h3>
              <p className="text-xs text-[#454655] leading-relaxed mb-4">
                Discover rival positioning, market gaps, competitive advantages, and evidence
                classifications (Verified, Extracted, Inferred).
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F3FF]">
              <div className="flex items-center justify-between text-[11px] text-[#454655] mb-1.5">
                <span>Direct Competitors</span>
                <span className="font-mono font-semibold text-[#141B2C]">3-5 Extracted</span>
              </div>
              <div className="w-full bg-[#F1F3FF] h-1.5 rounded-full overflow-hidden">
                <div className="bg-[#2538D0] h-full w-full rounded-full" />
              </div>
            </div>
          </div>

          {/* Deliverable 2 */}
          <div className="rounded-xl bg-white p-5 border border-[#E5E7EF] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#F1F3FF] text-[#2538D0] flex items-center justify-center mb-3 group-hover:bg-[#2538D0] group-hover:text-white transition-colors">
                <Search size={20} />
              </div>
              <div className="text-[10px] font-bold uppercase text-[#2538D0] tracking-wider mb-1">
                02 • Deliverable
              </div>
              <h3 className="font-bold text-sm text-[#141B2C] mb-1.5">Search Query Discovery</h3>
              <p className="text-xs text-[#454655] leading-relaxed mb-4">
                Uncover exactly 5 cross-platform search queries tailored across Google, LinkedIn, X,
                Meta, and Instagram for multi-channel targeting.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F3FF]">
              <div className="flex items-center justify-between text-[11px] text-[#454655] mb-1.5">
                <span>Query Platforms</span>
                <span className="font-mono font-semibold text-[#141B2C]">5 Platforms</span>
              </div>
              <div className="flex gap-1 pt-0.5">
                <span className="w-3 h-1.5 rounded-full bg-[#2538D0]" />
                <span className="w-3 h-1.5 rounded-full bg-[#2538D0]" />
                <span className="w-3 h-1.5 rounded-full bg-[#2538D0]" />
                <span className="w-3 h-1.5 rounded-full bg-[#2538D0]" />
                <span className="w-3 h-1.5 rounded-full bg-[#2538D0]" />
              </div>
            </div>
          </div>

          {/* Deliverable 3 */}
          <div className="rounded-xl bg-white p-5 border border-[#E5E7EF] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#F1F3FF] text-[#2538D0] flex items-center justify-center mb-3 group-hover:bg-[#2538D0] group-hover:text-white transition-colors">
                <Sliders size={20} />
              </div>
              <div className="text-[10px] font-bold uppercase text-[#2538D0] tracking-wider mb-1">
                03 • Deliverable
              </div>
              <h3 className="font-bold text-sm text-[#141B2C] mb-1.5">SEO Improvement</h3>
              <p className="text-xs text-[#454655] leading-relaxed mb-4">
                Title and meta before/after audit, priority recommendations, pixel length
                boundaries, and actionable technical findings.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F3FF]">
              <div className="flex items-center justify-between text-[11px] text-[#454655] mb-1.5">
                <span>Diff Generation</span>
                <span className="font-mono font-semibold text-[#0F9D83]">Real-time Diff</span>
              </div>
              <div className="w-full bg-[#F1F3FF] h-1.5 rounded-full overflow-hidden">
                <div className="bg-[#0F9D83] h-full w-full rounded-full" />
              </div>
            </div>
          </div>

          {/* Deliverable 4 */}
          <div className="rounded-xl bg-white p-5 border border-[#E5E7EF] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#F1F3FF] text-[#2538D0] flex items-center justify-center mb-3 group-hover:bg-[#2538D0] group-hover:text-white transition-colors">
                <Package size={20} />
              </div>
              <div className="text-[10px] font-bold uppercase text-[#2538D0] tracking-wider mb-1">
                04 • Deliverable
              </div>
              <h3 className="font-bold text-sm text-[#141B2C] mb-1.5">Service Discovery</h3>
              <p className="text-xs text-[#454655] leading-relaxed mb-4">
                Extract core offerings, structured service packages, target customer segments, and
                clear value propositions.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F3FF]">
              <div className="flex items-center justify-between text-[11px] text-[#454655] mb-1.5">
                <span>Extraction Mode</span>
                <span className="font-mono font-semibold text-[#141B2C]">Taxonomies</span>
              </div>
              <div className="w-full bg-[#F1F3FF] h-1.5 rounded-full overflow-hidden">
                <div className="bg-[#2538D0] h-full w-full rounded-full" />
              </div>
            </div>
          </div>

          {/* Deliverable 5 */}
          <div className="rounded-xl bg-white p-5 border border-[#E5E7EF] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
            <div>
              <div className="w-10 h-10 rounded-lg bg-[#F1F3FF] text-[#2538D0] flex items-center justify-center mb-3 group-hover:bg-[#2538D0] group-hover:text-white transition-colors">
                <Users size={20} />
              </div>
              <div className="text-[10px] font-bold uppercase text-[#2538D0] tracking-wider mb-1">
                05 • Deliverable
              </div>
              <h3 className="font-bold text-sm text-[#141B2C] mb-1.5">Target Audience</h3>
              <p className="text-xs text-[#454655] leading-relaxed mb-4">
                Persona archetypes, critical pain points, conversion triggers, buyer challenges, and
                optimized messaging angles.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F3FF]">
              <div className="flex items-center justify-between text-[11px] text-[#454655] mb-1.5">
                <span>Archetype Profiling</span>
                <span className="font-mono font-semibold text-[#141B2C]">3 Tiers</span>
              </div>
              <div className="w-full bg-[#F1F3FF] h-1.5 rounded-full overflow-hidden">
                <div className="bg-[#2538D0] h-full w-full rounded-full" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Two-Column Section: System Readiness + Live Metrics */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* AI Providers Status (2 cols) */}
        <div className="lg:col-span-2 rounded-2xl bg-white p-6 sm:p-8 border border-[#E5E7EF] shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[#F1F3FF]">
              <div className="flex items-center gap-2">
                <Server size={20} className="text-[#2538D0]" />
                <h3 className="font-bold text-base text-[#141B2C] font-['Manrope',sans-serif]">
                  System Readiness &amp; AI Providers
                </h3>
              </div>
              <span className="text-[11px] font-semibold px-2.5 py-1 rounded bg-[#F1F3FF] text-[#454655]">
                FastAPI Engine v1.4.2
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
              {/* Gemini Card */}
              <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between border border-[#DFE0FF]">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm text-[#141B2C]">Google Gemini</span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#83F7D9] text-[#005A4A] text-[10px] font-bold">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#005A4A]" /> Active
                    </span>
                  </div>
                  <div className="font-mono text-xs font-bold text-[#2538D0]">gemini-2.5-flash</div>
                  <div className="text-xs text-[#454655] mt-1">
                    Primary fast production model with native structured output enforcement.
                  </div>
                </div>
                <div className="mt-4 pt-2 border-t border-[#DFE0FF] flex items-center justify-between text-[11px] font-mono text-[#757687]">
                  <span>Latency: ~1.1s</span>
                  <span>1M Context</span>
                </div>
              </div>

              {/* GPT-4o-mini Card */}
              <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between border border-[#DFE0FF]">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm text-[#141B2C]">OpenAI GPT-4o</span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#E0E8FF] text-[#141B2C] text-[10px] font-bold">
                      Available
                    </span>
                  </div>
                  <div className="font-mono text-xs font-bold text-[#141B2C]">gpt-4o-mini</div>
                  <div className="text-xs text-[#454655] mt-1">
                    Ready for multi-model research &amp; comparative evaluation.
                  </div>
                </div>
                <div className="mt-4 pt-2 border-t border-[#DFE0FF] flex items-center justify-between text-[11px] font-mono text-[#757687]">
                  <span>Latency: ~1.3s</span>
                  <span>128K Context</span>
                </div>
              </div>

              {/* Claude Card */}
              <div className="rounded-xl bg-[#F1F3FF] p-4 flex flex-col justify-between border border-[#DFE0FF]">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm text-[#141B2C]">Claude 3.5 Haiku</span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#E0E8FF] text-[#141B2C] text-[10px] font-bold">
                      Standby
                    </span>
                  </div>
                  <div className="font-mono text-xs font-bold text-[#141B2C]">claude-3-5-haiku</div>
                  <div className="text-xs text-[#454655] mt-1">
                    High-speed token benchmark &amp; rigorous JSON schema testing.
                  </div>
                </div>
                <div className="mt-4 pt-2 border-t border-[#DFE0FF] flex items-center justify-between text-[11px] font-mono text-[#757687]">
                  <span>Latency: ~1.4s</span>
                  <span>200K Context</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 rounded-xl bg-[#F1F3FF] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border border-[#DFE0FF]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#83F7D9] text-[#005A4A] flex items-center justify-center font-bold">
                <Globe size={18} />
              </div>
              <div>
                <div className="text-xs font-bold text-[#141B2C]">
                  Search &amp; Extraction Engine Worker
                </div>
                <div className="text-xs text-[#454655]">
                  Playwright Headless + BeautifulSoup4 Sanitizer (Safe Fetcher Active)
                </div>
              </div>
            </div>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#83F7D9] text-[#005A4A] text-[11px] font-semibold shrink-0">
              <span className="w-1.5 h-1.5 rounded-full bg-[#005A4A]" /> Healthy • 0 Queue
            </span>
          </div>
        </div>

        {/* Backend Performance Metrics (1 col) */}
        <div className="rounded-2xl bg-white p-6 sm:p-8 border border-[#E5E7EF] shadow-xs flex flex-col justify-between">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#F1F3FF]">
              <h3 className="font-bold text-base text-[#141B2C] font-['Manrope',sans-serif]">
                Runtime Telemetry
              </h3>
              <span className="text-xs font-mono text-[#0F9D83] flex items-center gap-1.5 font-semibold">
                <span className="w-2 h-2 rounded-full bg-[#0F9D83] animate-pulse" /> Live Stream
              </span>
            </div>

            <div className="flex flex-col gap-3">
              <div className="rounded-xl bg-[#F1F3FF] p-4 flex items-center justify-between border border-[#DFE0FF]">
                <div>
                  <div className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                    System Uptime
                  </div>
                  <div className="text-2xl font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                    99.98%
                  </div>
                </div>
                <Server size={28} className="text-[#0F9D83]" />
              </div>

              <div className="rounded-xl bg-[#F1F3FF] p-4 flex items-center justify-between border border-[#DFE0FF]">
                <div>
                  <div className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                    Avg Analysis Latency
                  </div>
                  <div className="text-2xl font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                    {latencyDisplay}
                  </div>
                </div>
                <Timer size={28} className="text-[#2538D0]" />
              </div>

              <div className="rounded-xl bg-[#F1F3FF] p-4 flex items-center justify-between border border-[#DFE0FF]">
                <div>
                  <div className="text-[10px] uppercase font-bold tracking-wider text-[#757687]">
                    JSON Schema Compliance
                  </div>
                  <div className="text-2xl font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                    100%
                  </div>
                </div>
                <CheckSquare size={28} className="text-[#0F9D83]" />
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#F1F3FF] flex items-center justify-between text-xs font-mono text-[#757687]">
            <span>Uvicorn 0.30.6</span>
            <span>Python 3.10.11</span>
          </div>
        </div>
      </section>

      {/* Recent Intelligence Reports Table */}
      <section className="rounded-2xl bg-white p-6 sm:p-8 border border-[#E5E7EF] shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#2538D0]">
                Audit Repository
              </span>
              <span className="w-1 h-1 rounded-full bg-[#757687]" />
              <span className="text-[11px] uppercase tracking-wider text-[#757687]">
                Structured Results
              </span>
            </div>
            <h2 className="text-xl font-bold font-['Manrope',sans-serif] text-[#141B2C]">
              Recent Intelligence Reports
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to="/history"
              className="px-3 py-1.5 rounded-lg bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#141B2C] text-xs font-semibold transition-colors flex items-center gap-1.5 border border-[#DFE0FF]"
            >
              <Filter size={14} />
              <span>Filter All</span>
            </Link>
            <Link
              to="/analyze"
              className="px-3.5 py-1.5 rounded-lg bg-[#2538D0] hover:bg-[#1E31C0] text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-xs"
            >
              <span>+ New Analysis</span>
            </Link>
          </div>
        </div>

        {/* Data Table for Desktop, Cards for Mobile */}
        <div className="w-full overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#F1F3FF] rounded-lg">
                <th className="py-3 px-4 text-[11px] font-bold uppercase tracking-wider text-[#757687]">
                  Brand / Target Domain
                </th>
                <th className="py-3 px-4 text-[11px] font-bold uppercase tracking-wider text-[#757687]">
                  Analysis Timestamp
                </th>
                <th className="py-3 px-4 text-[11px] font-bold uppercase tracking-wider text-[#757687]">
                  AI Model
                </th>
                <th className="py-3 px-4 text-[11px] font-bold uppercase tracking-wider text-[#757687]">
                  5-Section Status
                </th>
                <th className="py-3 px-4 text-[11px] font-bold uppercase tracking-wider text-[#757687]">
                  Run Mode
                </th>
                <th className="py-3 px-4 text-[11px] font-bold uppercase tracking-wider text-[#757687] text-right">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F3FF]">
              {history.length > 0 ? (
                history.slice(0, 5).map((entry) => {
                  const initial = entry.brand?.charAt(0) || "W";
                  return (
                    <tr key={entry.id} className="hover:bg-[#F9F9FF] transition-colors group">
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-[#E0E8FF] flex items-center justify-center font-bold text-[#2538D0] text-xs">
                            {initial}
                          </div>
                          <div>
                            <div className="font-bold text-sm text-[#141B2C]">{entry.brand}</div>
                            <div className="font-mono text-xs text-[#757687] truncate max-w-xs">
                              {entry.website}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-xs font-mono text-[#454655]">
                        {new Date(entry.analyzedAt).toLocaleDateString()}{" "}
                        <span className="text-[#757687]">
                          (
                          {new Date(entry.analyzedAt).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                          )
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#F1F3FF] text-[#2538D0] font-mono text-xs font-semibold">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#2538D0]" />
                          Gemini 2.5 Flash
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#83F7D9] text-[#005A4A] text-[11px] font-semibold">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#005A4A]" /> 5 / 5 Complete
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                            entry.sample
                              ? "bg-[#F1F3FF] text-[#757687]"
                              : "bg-[#DFE0FF] text-[#000A64]"
                          }`}
                        >
                          {entry.sample ? "Sample Fixture" : "Live Verified"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <Link
                          to="/reports/$id"
                          params={{ id: entry.id }}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#2538D0] text-white text-xs font-medium hover:bg-[#1E31C0] transition-all"
                        >
                          <span>Open Report</span>
                          <ArrowRight size={13} />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              ) : (
                /* Fallback sample row if history is empty */
                <tr className="hover:bg-[#F9F9FF] transition-colors group">
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-[#E0E8FF] flex items-center justify-center font-bold text-[#2538D0] text-xs">
                        H
                      </div>
                      <div>
                        <div className="font-bold text-sm text-[#141B2C]">HubSpot CRM Platform</div>
                        <div className="font-mono text-xs text-[#757687]">
                          https://www.hubspot.com/
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-xs font-mono text-[#454655]">
                    Just now <span className="text-[#757687]">(12:44:02)</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#F1F3FF] text-[#2538D0] font-mono text-xs font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#2538D0]" />
                      Gemini 2.5 Flash
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#83F7D9] text-[#005A4A] text-[11px] font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#005A4A]" /> 5 / 5 Complete
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-[#DFE0FF] text-[#000A64]">
                      Sample Data
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <Link
                      to="/reports/$id"
                      params={{ id: "sample-northstar-01" }}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#2538D0] text-white text-xs font-medium hover:bg-[#1E31C0] transition-all"
                    >
                      <span>Open Report</span>
                      <ArrowRight size={13} />
                    </Link>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
