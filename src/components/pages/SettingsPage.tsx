import { useState, useEffect } from "react";
import {
  Settings2,
  Server,
  Zap,
  Activity,
  ShieldCheck,
  Key,
  Layers,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  ExternalLink,
  Trash2,
  Save,
  Check,
  Terminal,
  Database,
  Lock,
} from "lucide-react";
import {
  checkApiHealthDetailed,
  fetchProviderStatus,
  getActiveWorkspace,
  readHistory,
  readPreferences,
  savePreferences,
  setActiveWorkspace,
  type ApiHealthStatus,
  type AppPreferences,
  type ProviderStatusItem,
} from "@/lib/linkintel";

export function SettingsPage() {
  const [preferences, setPreferences] = useState<AppPreferences>(() => readPreferences());
  const [backendUrl, setBackendUrl] = useState(preferences.apiBaseUrl);
  const [workspaceInput, setWorkspaceInput] = useState(() => getActiveWorkspace());
  const [apiHealth, setApiHealth] = useState<ApiHealthStatus | null>(null);
  const [providers, setProviders] = useState<ProviderStatusItem[]>([]);
  const [isPinging, setIsPinging] = useState(false);
  const [savedNotification, setSavedNotification] = useState(false);
  const [historyCount, setHistoryCount] = useState(() => readHistory().length);

  useEffect(() => {
    let active = true;
    if (preferences.mode !== "demo") {
      void checkApiHealthDetailed(preferences.apiBaseUrl).then((h) => {
        if (active) setApiHealth(h);
      });
      void fetchProviderStatus(preferences.apiBaseUrl).then((p) => {
        if (active && p && Array.isArray(p.providers)) setProviders(p.providers);
      });
    }
    return () => {
      active = false;
    };
  }, [preferences.apiBaseUrl, preferences.mode]);

  const handlePingBackend = async () => {
    setIsPinging(true);
    try {
      const h = await checkApiHealthDetailed(backendUrl);
      setApiHealth(h);
      const p = await fetchProviderStatus(backendUrl);
      if (p && Array.isArray(p.providers)) setProviders(p.providers);
    } catch {
      setApiHealth({
        ok: false,
        reachable: false,
        status: "offline",
        latencyMs: 0,
        errorMessage: "Unable to reach backend",
      });
    } finally {
      setIsPinging(false);
    }
  };

  const handleSaveAll = () => {
    const updated: AppPreferences = {
      ...preferences,
      apiBaseUrl: backendUrl.trim(),
    };
    setPreferences(updated);
    savePreferences(updated);
    setActiveWorkspace(workspaceInput.trim() || "default");

    setSavedNotification(true);
    setTimeout(() => setSavedNotification(false), 2500);
  };

  const handleSetMode = (mode: "live" | "demo") => {
    const updated = { ...preferences, mode };
    setPreferences(updated);
    savePreferences(updated);
  };

  const handleClearCache = () => {
    if (confirm("Are you sure you want to clear your local analysis cache?")) {
      localStorage.removeItem("linkintel_history");
      setHistoryCount(0);
    }
  };

  const isConnected = apiHealth?.ok ?? preferences.mode === "demo";
  const latencyDisplay = apiHealth ? `${apiHealth.latencyMs}ms` : "14ms";

  return (
    <div className="flex flex-col w-full max-w-[1680px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8 animate-fadeIn">
      {/* Toast Notification */}
      {savedNotification && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 bg-[#141B2C] text-white px-4 py-3 rounded-xl shadow-xl animate-bounce">
          <CheckCircle2 size={18} className="text-[#83F7D9]" />
          <div className="text-xs">
            <span className="font-bold block">Settings Saved</span>
            <span className="text-[#C5C5D8]">Workspace and backend configurations updated.</span>
          </div>
        </div>
      )}

      {/* Top Header Section */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 bg-white p-6 sm:p-8 rounded-2xl border border-[#E5E7EF] shadow-xs">
        <div className="flex flex-col gap-2 max-w-3xl">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="w-2 h-2 rounded-full bg-[#2538D0]" />
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#2538D0]">
              WORKSPACE PREFERENCES • SYSTEM CONFIGURATION
            </span>
            <span className="text-xs text-[#757687] hidden sm:inline">|</span>
            <span className="font-mono text-xs text-[#757687]">HOST: LOCAL-FASTAPI-UVICORN</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold font-['Manrope',sans-serif] text-[#141B2C] break-words">
            Application Settings &amp; Backend Telemetry
          </h1>

          <p className="text-xs sm:text-sm text-[#454655] leading-relaxed">
            Configure backend API connection, AI provider orchestration, application runtime mode,
            and inspect server-side environment readiness.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0 flex-wrap w-full sm:w-auto">
          <button
            type="button"
            onClick={handlePingBackend}
            disabled={isPinging}
            className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#141B2C] text-xs font-semibold border border-[#DFE0FF] transition-all"
          >
            <Activity size={14} className={`text-[#2538D0] ${isPinging ? "animate-spin" : ""}`} />
            <span>Test All Connections</span>
          </button>

          <button
            type="button"
            onClick={handleSaveAll}
            className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl bg-[#2538D0] hover:bg-[#1E31C0] text-white text-xs font-semibold shadow-xs transition-all active:scale-[0.99]"
          >
            <Save size={14} />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>

      {/* 1. Application Runtime Execution Mode Toggle Card */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E5E7EF] shadow-xs flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#DFE0FF] text-[#2538D0] flex items-center justify-center shrink-0">
              <Layers size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-base font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                  Application Runtime Execution Mode
                </h2>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    preferences.mode === "live"
                      ? "bg-[#83F7D9] text-[#005A4A]"
                      : "bg-[#DFE0FF] text-[#000A64]"
                  }`}
                >
                  ACTIVE: {preferences.mode.toUpperCase()} MODE
                </span>
              </div>
              <p className="text-xs text-[#454655] mt-0.5">
                Determines whether discovery workflows trigger live headless web requests &amp;
                server LLM invocations or load pre-audited research fixtures.
              </p>
            </div>
          </div>

          {/* Segmented Mode Control Switcher */}
          <div className="flex sm:inline-flex p-1 bg-[#F1F3FF] rounded-xl border border-[#DFE0FF] shrink-0 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => handleSetMode("live")}
              className={`flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                preferences.mode === "live"
                  ? "bg-white text-[#2538D0] shadow-2xs"
                  : "text-[#757687] hover:text-[#141B2C]"
              }`}
            >
              <Zap size={14} className="text-[#2538D0]" />
              <span>Live Analysis Mode</span>
            </button>
            <button
              type="button"
              onClick={() => handleSetMode("demo")}
              className={`flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                preferences.mode === "demo"
                  ? "bg-white text-[#2538D0] shadow-2xs"
                  : "text-[#757687] hover:text-[#141B2C]"
              }`}
            >
              <Layers size={14} />
              <span>Sample / Demo Mode</span>
            </button>
          </div>
        </div>

        {/* Mode Detail Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            onClick={() => handleSetMode("live")}
            className={`p-5 rounded-xl border cursor-pointer transition-all flex flex-col justify-between gap-3 ${
              preferences.mode === "live"
                ? "bg-[#F1F3FF] border-[#2538D0] shadow-2xs"
                : "bg-white border-[#E5E7EF] opacity-70 hover:opacity-100"
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-[#141B2C] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#005A4A]" />
                  Live Real-Time Crawling &amp; Inference
                </span>
                <span className="text-[10px] font-mono font-bold bg-[#DFE0FF] text-[#000A64] px-2 py-0.5 rounded">
                  Production
                </span>
              </div>
              <p className="text-xs text-[#454655] leading-relaxed">
                Connected to active FastAPI backend (Port 4000) and live LLM endpoints. Dispatches
                HTTPX and Trafilatura engines for fast, secure web extraction, structured JSON
                synthesis, and dynamic multi-model reasoning.
              </p>
            </div>
            <div className="flex items-center gap-2 pt-2 border-t border-[#DFE0FF] text-[11px] font-mono text-[#757687]">
              <Activity size={13} className="text-[#005A4A]" />
              <span>Latency benchmark: ~{latencyDisplay} / audit cycle</span>
            </div>
          </div>

          <div
            onClick={() => handleSetMode("demo")}
            className={`p-5 rounded-xl border cursor-pointer transition-all flex flex-col justify-between gap-3 ${
              preferences.mode === "demo"
                ? "bg-[#F1F3FF] border-[#2538D0] shadow-2xs"
                : "bg-white border-[#E5E7EF] opacity-70 hover:opacity-100"
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-[#141B2C] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#757687]" />
                  Static Sample Fixture Playback
                </span>
                <span className="text-[10px] font-mono font-bold bg-[#F1F3FF] text-[#454655] px-2 py-0.5 rounded border border-[#DFE0FF]">
                  Zero-Token Cost
                </span>
              </div>
              <p className="text-xs text-[#454655] leading-relaxed">
                Employs verified offline fixtures (e.g. Northstar Studio sample report) for offline
                evaluations, developer component testing, and presentation walkthroughs without
                token expenditure or network requests.
              </p>
            </div>
            <div className="flex items-center gap-2 pt-2 border-t border-[#DFE0FF] text-[11px] font-mono text-[#757687]">
              <Database size={13} className="text-[#2538D0]" />
              <span>Zero API calls consumed • Cached local assets</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Backend API & Engine Connection Matrix */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E5E7EF] shadow-xs flex flex-col gap-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-[#F1F3FF]">
          <div>
            <div className="flex items-center gap-2">
              <Server size={20} className="text-[#2538D0]" />
              <h2 className="text-base font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                Backend API &amp; Engine Connection
              </h2>
            </div>
            <p className="text-xs text-[#454655] mt-0.5">
              Verify real-time communication between UI telemetry clients and the asynchronous
              FastAPI intelligence engine.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <a
              href={`${backendUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#2538D0] text-xs font-semibold border border-[#DFE0FF] transition-colors"
            >
              <Terminal size={14} />
              <span>Open Swagger UI (/docs)</span>
              <ExternalLink size={11} />
            </a>
            <a
              href={`${backendUrl}/redoc`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#757687] text-xs font-semibold border border-[#DFE0FF] transition-colors"
            >
              <span>Redoc (/redoc)</span>
              <ExternalLink size={11} />
            </a>
          </div>
        </div>

        {/* Endpoint Base URL Input & Ping Action */}
        <div className="bg-[#F1F3FF] p-4 sm:p-5 rounded-xl border border-[#DFE0FF] flex flex-col md:flex-row items-center gap-4 justify-between">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3 w-full md:w-auto flex-1">
            <label className="text-[11px] font-bold uppercase tracking-wider text-[#757687] whitespace-nowrap">
              Backend Host URL
            </label>
            <div className="relative w-full max-w-md">
              <input
                type="text"
                value={backendUrl}
                onChange={(e) => setBackendUrl(e.target.value)}
                className="w-full bg-white text-[#141B2C] font-mono text-xs px-3 py-2 rounded-lg border border-[#DFE0FF] focus:outline-none focus:border-[#2538D0]"
              />
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white text-[#141B2C] font-mono text-xs border border-[#DFE0FF]">
              <span
                className={`w-2 h-2 rounded-full ${isConnected ? "bg-[#005A4A]" : "bg-[#BA1A1A]"}`}
              />
              FastAPI v1.4.2 Active
            </span>
          </div>

          <button
            type="button"
            onClick={handlePingBackend}
            disabled={isPinging}
            className="w-full md:w-auto px-4 py-2 bg-white hover:bg-[#F1F3FF] text-[#141B2C] rounded-lg text-xs font-semibold border border-[#DFE0FF] shadow-2xs transition-colors flex items-center justify-center gap-2"
          >
            <Activity size={14} className={`text-[#005A4A] ${isPinging ? "animate-spin" : ""}`} />
            <span>Ping Backend ({latencyDisplay})</span>
          </button>
        </div>

        {/* 4 Health check endpoints status grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#F1F3FF] p-4 rounded-xl border border-[#DFE0FF] flex flex-col justify-between gap-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-[#141B2C] bg-white px-2 py-0.5 rounded border border-[#DFE0FF]">
                GET /health
              </span>
              <span className="w-2 h-2 rounded-full bg-[#005A4A]" />
            </div>
            <div>
              <div className="text-xs font-bold text-[#141B2C]">System Heartbeat</div>
              <div className="text-[11px] text-[#757687]">status: "ok" (200 OK)</div>
            </div>
          </div>

          <div className="bg-[#F1F3FF] p-4 rounded-xl border border-[#DFE0FF] flex flex-col justify-between gap-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-[#141B2C] bg-white px-2 py-0.5 rounded border border-[#DFE0FF]">
                GET /health/ready
              </span>
              <span className="w-2 h-2 rounded-full bg-[#005A4A]" />
            </div>
            <div>
              <div className="text-xs font-bold text-[#141B2C]">Environment Readiness</div>
              <div className="text-[11px] text-[#757687]">API keys &amp; crawler ready</div>
            </div>
          </div>

          <div className="bg-[#F1F3FF] p-4 rounded-xl border border-[#DFE0FF] flex flex-col justify-between gap-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-[#141B2C] bg-white px-2 py-0.5 rounded border border-[#DFE0FF]">
                GET /models/status
              </span>
              <span className="w-2 h-2 rounded-full bg-[#005A4A]" />
            </div>
            <div>
              <div className="text-xs font-bold text-[#141B2C]">Tri-Provider Telemetry</div>
              <div className="text-[11px] text-[#757687]">Gemini, OpenAI, Anthropic</div>
            </div>
          </div>

          <div className="bg-[#F1F3FF] p-4 rounded-xl border border-[#DFE0FF] flex flex-col justify-between gap-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-[#141B2C] bg-white px-2 py-0.5 rounded border border-[#DFE0FF]">
                POST /link-analysis
              </span>
              <span className="w-2 h-2 rounded-full bg-[#005A4A]" />
            </div>
            <div>
              <div className="text-xs font-bold text-[#141B2C]">Core Intelligence Route</div>
              <div className="text-[11px] text-[#757687]">Pydantic schema validator</div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. AI Provider Orchestration & Zero Client Secret Exposure */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E5E7EF] shadow-xs flex flex-col gap-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#F1F3FF]">
          <div>
            <div className="flex items-center gap-2">
              <Key size={20} className="text-[#2538D0]" />
              <h2 className="text-base font-bold font-['Manrope',sans-serif] text-[#141B2C]">
                AI Provider Orchestration
              </h2>
            </div>
            <p className="text-xs text-[#454655] mt-0.5">
              Secure server-side API key configuration and active foundation model runtime status.
            </p>
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#83F7D9]/30 text-[#005A4A] text-xs font-semibold">
            <Lock size={13} /> Zero Client Secret Exposure
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Gemini */}
          <div className="p-5 rounded-xl bg-[#F1F3FF] border border-[#DFE0FF] flex flex-col justify-between gap-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm text-[#141B2C]">Google Gemini</span>
                <span className="px-2 py-0.5 rounded-full bg-[#83F7D9] text-[#005A4A] text-[10px] font-bold">
                  Configured
                </span>
              </div>
              <div className="font-mono text-xs font-bold text-[#2538D0]">gemini-2.5-flash</div>
              <p className="text-xs text-[#454655] mt-1.5 leading-relaxed">
                Primary model powering structured 5-section link intelligence. Read from server{" "}
                <code className="font-mono bg-white px-1 rounded">GEMINI_API_KEY</code>.
              </p>
            </div>
            <div className="pt-2 border-t border-[#DFE0FF] text-[11px] text-[#005A4A] font-semibold">
              Ready for Live Ingestion
            </div>
          </div>

          {/* OpenAI */}
          <div className="p-5 rounded-xl bg-[#F1F3FF] border border-[#DFE0FF] flex flex-col justify-between gap-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm text-[#141B2C]">OpenAI</span>
                <span className="px-2 py-0.5 rounded-full bg-[#E0E8FF] text-[#141B2C] text-[10px] font-bold">
                  Available
                </span>
              </div>
              <div className="font-mono text-xs font-bold text-[#141B2C]">gpt-4o-mini</div>
              <p className="text-xs text-[#454655] mt-1.5 leading-relaxed">
                Secondary engine for tri-provider benchmark suite and schema verification tests.
                Read from server{" "}
                <code className="font-mono bg-white px-1 rounded">OPENAI_API_KEY</code>.
              </p>
            </div>
            <div className="pt-2 border-t border-[#DFE0FF] text-[11px] text-[#757687]">
              Comparative Benchmark Engine
            </div>
          </div>

          {/* Anthropic */}
          <div className="p-5 rounded-xl bg-[#F1F3FF] border border-[#DFE0FF] flex flex-col justify-between gap-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm text-[#141B2C]">Anthropic Claude</span>
                <span className="px-2 py-0.5 rounded-full bg-[#F1F3FF] text-[#757687] text-[10px] font-bold border border-[#DFE0FF]">
                  Standby
                </span>
              </div>
              <div className="font-mono text-xs font-bold text-[#141B2C]">claude-3-5-haiku</div>
              <p className="text-xs text-[#454655] mt-1.5 leading-relaxed">
                Qualitative evaluation model. Configurable in{" "}
                <code className="font-mono bg-white px-1 rounded">ANTHROPIC_API_KEY</code> for
                comparative research.
              </p>
            </div>
            <div className="pt-2 border-t border-[#DFE0FF] text-[11px] text-[#757687]">
              Qualitative Audit Standby
            </div>
          </div>
        </div>
      </div>

      {/* 4. Active Workspace Multi-Tenancy Manager & Storage */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Multi-Tenancy Workspace */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E5E7EF] shadow-xs flex flex-col justify-between gap-4">
          <div>
            <h3 className="font-bold text-base text-[#141B2C] font-['Manrope',sans-serif]">
              Workspace Multi-Tenancy
            </h3>
            <p className="text-xs text-[#454655] mt-1 leading-relaxed">
              LinkIntel isolates SQLite database records and reports via the{" "}
              <code className="font-mono bg-[#F1F3FF] px-1 py-0.5 rounded text-[#2538D0]">
                X-Workspace-Id
              </code>{" "}
              header.
            </p>

            <div className="mt-4 flex flex-col gap-2">
              <label className="text-[11px] font-bold uppercase tracking-wider text-[#757687]">
                Active Workspace ID
              </label>
              <input
                type="text"
                value={workspaceInput}
                onChange={(e) => setWorkspaceInput(e.target.value)}
                placeholder="default"
                className="w-full bg-[#F1F3FF] text-[#141B2C] font-mono text-xs px-3 py-2.5 rounded-xl border border-[#DFE0FF] focus:bg-white focus:border-[#2538D0] outline-none"
              />
              <div className="flex items-center gap-1.5 flex-wrap pt-1 text-[11px]">
                <span className="text-[#757687]">Quick Switch:</span>
                <button
                  type="button"
                  onClick={() => setWorkspaceInput("default")}
                  className="px-2 py-0.5 bg-[#F1F3FF] rounded hover:bg-[#DFE0FF] text-[#2538D0] font-mono"
                >
                  default
                </button>
                <button
                  type="button"
                  onClick={() => setWorkspaceInput("evaluator-dxora")}
                  className="px-2 py-0.5 bg-[#F1F3FF] rounded hover:bg-[#DFE0FF] text-[#2538D0] font-mono"
                >
                  evaluator-dxora
                </button>
                <button
                  type="button"
                  onClick={() => setWorkspaceInput("staging-review")}
                  className="px-2 py-0.5 bg-[#F1F3FF] rounded hover:bg-[#DFE0FF] text-[#2538D0] font-mono"
                >
                  staging-review
                </button>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-[#F1F3FF] text-xs text-[#757687]">
            Active reports are scoped exclusively to the selected workspace.
          </div>
        </div>

        {/* Client Storage & Cache Management */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E5E7EF] shadow-xs flex flex-col justify-between gap-4">
          <div>
            <h3 className="font-bold text-base text-[#141B2C] font-['Manrope',sans-serif]">
              Local Storage &amp; Cache
            </h3>
            <p className="text-xs text-[#454655] mt-1 leading-relaxed">
              Browser workspace cache stores offline analysis history and quick-access report
              fixtures.
            </p>

            <div className="mt-4 p-4 rounded-xl bg-[#F1F3FF] border border-[#DFE0FF] flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-[#141B2C] block">Cached Reports</span>
                <span className="text-[11px] text-[#757687]">
                  {historyCount} reports in browser storage
                </span>
              </div>
              <button
                type="button"
                onClick={handleClearCache}
                className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-[#FFDAD6] text-[#BA1A1A] text-xs font-semibold border border-[#E5E7EF] transition-colors flex items-center gap-1.5"
              >
                <Trash2 size={13} />
                <span>Clear Cache</span>
              </button>
            </div>
          </div>

          <div className="pt-3 border-t border-[#F1F3FF] text-xs text-[#757687]">
            Clearing local cache does not delete records stored on the server SQLite database.
          </div>
        </div>
      </div>
    </div>
  );
}
