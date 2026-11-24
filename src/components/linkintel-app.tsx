import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "@tanstack/react-router";
import {
  Activity,
  ArrowDownToLine,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  BookOpen,
  BrainCircuit,
  BriefcaseBusiness,
  Check,
  ChevronDown,
  ChevronRight,
  CircleAlert,
  CircleCheck,
  Clipboard,
  Clock3,
  Code2,
  Coins,
  Compass,
  Copy,
  ExternalLink,
  FileJson2,
  FileSearch,
  Filter,
  Gauge,
  Globe2,
  History,
  Layers3,
  Lightbulb,
  Link2,
  LoaderCircle,
  LockKeyhole,
  Menu,
  MoreHorizontal,
  PanelTop,
  Radar,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Tags,
  Target,
  TrendingUp,
  Users2,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  analyzeWebsite,
  checkApiHealth,
  checkApiHealthDetailed,
  DEFAULT_API_BASE_URL,
  deleteReport,
  deleteReportById,
  DEMO_REPORT,
  fetchBenchmarksList,
  fetchBenchmarkById,
  fetchProviderStatus,
  fetchReportById,
  fetchReportsList,
  getActiveWorkspace,
  getReport,
  readHistory,
  readPreferences,
  runModelBenchmark,
  savePreferences,
  saveReport,
  setActiveWorkspace,
  validateWebsiteUrl,
  type ApiHealthStatus,
  type AppPreferences,
  type AudienceProfile,
  type BenchmarkRunResponse,
  type Competitor,
  type HistoryEntry,
  type LinkAnalysis,
  type ModelBenchmarkResult,
  type ProviderStatusItem,
  type SearchQuery,
  type ServiceInsight,
} from "@/lib/linkintel";

type IconType = typeof Globe2;

const nav = [
  { to: "/", label: "Overview", icon: PanelTop },
  { to: "/analyze", label: "Analyze website", icon: FileSearch },
  { to: "/history", label: "Analysis history", icon: History },
  { to: "/model-lab", label: "Model research", icon: BrainCircuit },
] as const;

const features: { label: string; description: string; icon: IconType; color: string }[] = [
  {
    label: "Competitor intelligence",
    description: "Map the landscape and find where your brand stands apart.",
    icon: Radar,
    color: "feature-indigo",
  },
  {
    label: "Search opportunities",
    description: "Explore five relevant queries, intent, and audience fit.",
    icon: Search,
    color: "feature-blue",
  },
  {
    label: "SEO improvements",
    description: "Turn real page signals into specific on-page priorities.",
    icon: TrendingUp,
    color: "feature-teal",
  },
  {
    label: "Service analysis",
    description: "Identify the offers your website actually describes.",
    icon: Layers3,
    color: "feature-amber",
  },
  {
    label: "Audience insights",
    description: "Understand likely customer needs, with evidence labels.",
    icon: Users2,
    color: "feature-rose",
  },
];

const tabs = [
  { id: "competitors", label: "Competitors", icon: Radar },
  { id: "queries", label: "Search queries", icon: Search },
  { id: "seo", label: "SEO analysis", icon: TrendingUp },
  { id: "services", label: "Top services", icon: Layers3 },
  { id: "audience", label: "Target audience", icon: Users2 },
] as const;

function usePreferences() {
  const [preferences, setPreferences] = useState<AppPreferences>(() => readPreferences());
  const update = (value: AppPreferences) => {
    setPreferences(value);
    savePreferences(value);
  };
  return [preferences, update] as const;
}

function BrandMark({ small = false }: { small?: boolean }) {
  return (
    <span className={`brand-mark${small ? " brand-mark-small" : ""}`} aria-hidden="true">
      <Link2 size={small ? 17 : 20} strokeWidth={2.3} />
      <i />
    </span>
  );
}

function Sidebar({ pathname, onClose }: { pathname: string; onClose: () => void }) {
  const currentWs = getActiveWorkspace();
  return (
    <aside className="app-sidebar">
      <div className="sidebar-brand">
        <BrandMark />
        <span className="brand-name">
          LinkIntel<span>AI</span>
        </span>
        <button aria-label="Close navigation" className="mobile-close" onClick={onClose}>
          <X size={18} />
        </button>
      </div>
      <Link
        to="/settings"
        onClick={onClose}
        className="workspace-select hover:opacity-90 transition-opacity"
        title="Click to manage active workspace in Settings"
      >
        <span className="workspace-icon">
          <BarChart3 size={15} />
        </span>
        <span>
          <b>Intelligence desk</b>
          <small>Workspace: {currentWs}</small>
        </span>
        <ChevronRight size={14} className="workspace-chevron" />
      </Link>
      <p className="sidebar-label">WORKSPACE</p>
      <nav className="sidebar-nav" aria-label="Main navigation">
        {nav.map((item) => {
          const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={`sidebar-link${active ? " active" : ""}`}
            >
              <Icon size={17} strokeWidth={1.8} />
              <span>{item.label}</span>
              {item.to === "/history" && (
                <span className="nav-count">{readHistory().length || "—"}</span>
              )}
            </Link>
          );
        })}
      </nav>
      <p className="sidebar-label sidebar-label-lower">PREFERENCES</p>
      <Link
        to="/settings"
        onClick={onClose}
        className={`sidebar-link${pathname === "/settings" ? " active" : ""}`}
      >
        <Settings2 size={17} strokeWidth={1.8} />
        <span>Settings</span>
      </Link>
      <div className="sidebar-bottom">
        <div className="sidebar-security">
          <ShieldCheck size={16} />
          <span>Privacy-first analysis</span>
          <Check size={13} />
        </div>
        <div className="sidebar-footer">
          <span className="online-dot" />
          Local workspace <span>v1.0</span>
        </div>
      </div>
    </aside>
  );
}

function AppShell({ children, title }: { children: ReactNode; title: string }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [preferences] = usePreferences();
  const [apiHealth, setApiHealth] = useState<ApiHealthStatus | null>(null);
  const pathname = typeof window === "undefined" ? "/" : window.location.pathname;
  useEffect(() => {
    let current = true;
    if (preferences.mode === "demo") {
      setApiHealth(null);
      return () => {
        current = false;
      };
    }
    void checkApiHealthDetailed(preferences.apiBaseUrl).then((status) => {
      if (current) setApiHealth(status);
    });
    return () => {
      current = false;
    };
  }, [preferences.apiBaseUrl, preferences.mode]);

  const badgeClass = useMemo(() => {
    if (preferences.mode === "demo") return "mode-demo";
    if (!apiHealth) return "mode-live";
    if (!apiHealth.reachable) return "mode-live";
    if (!apiHealth.providerKeyConfigured) return "mode-warning";
    return "mode-online";
  }, [preferences.mode, apiHealth]);

  const badgeText = useMemo(() => {
    if (preferences.mode === "demo") return "Sample mode";
    if (!apiHealth) return "Checking API...";
    if (!apiHealth.reachable) return "API unavailable";
    if (!apiHealth.providerKeyConfigured) return "API key missing";
    return "API connected";
  }, [preferences.mode, apiHealth]);

  return (
    <div className="app-frame">
      {mobileOpen && (
        <button
          className="mobile-scrim"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <div className={mobileOpen ? "sidebar-wrap sidebar-wrap-open" : "sidebar-wrap"}>
        <Sidebar pathname={pathname} onClose={() => setMobileOpen(false)} />
      </div>
      <main className="app-main">
        <header className="topbar">
          <div className="topbar-left">
            <Button
              variant="ghost"
              size="icon"
              className="menu-button"
              aria-label="Open navigation"
              onClick={() => setMobileOpen(true)}
            >
              <Menu size={19} />
            </Button>
            <span className="breadcrumb-root">Workspace</span>
            <ChevronRight size={14} className="breadcrumb-chevron" />
            <span className="breadcrumb-current">{title}</span>
          </div>
          <div className="topbar-right">
            <span
              className={`mode-badge ${badgeClass}`}
              title={apiHealth?.errorMessage || undefined}
            >
              <i />
              {badgeText}
            </span>
            <Link to="/settings" className="topbar-settings" aria-label="Settings">
              <Settings2 size={17} />
            </Link>
            <div className="avatar-chip">LI</div>
          </div>
        </header>
        <div className="page-content">{children}</div>
      </main>
      <nav className="mobile-bottom-nav" aria-label="Mobile Navigation">
        <Link to="/" className={pathname === "/" ? "active" : ""}>
          <PanelTop size={20} />
          <span>Overview</span>
        </Link>
        <Link to="/analyze" className={pathname === "/analyze" ? "active" : ""}>
          <FileSearch size={20} />
          <span>Analyze</span>
        </Link>
        <Link to="/history" className={pathname === "/history" ? "active" : ""}>
          <History size={20} />
          <span>History</span>
        </Link>
        <Link to="/model-lab" className={pathname === "/model-lab" ? "active" : ""}>
          <BrainCircuit size={20} />
          <span>Model Lab</span>
        </Link>
        <Link to="/settings" className={pathname === "/settings" ? "active" : ""}>
          <Settings2 size={20} />
          <span>Settings</span>
        </Link>
      </nav>
    </div>
  );
}

function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {description && <p className="page-description">{description}</p>}
      </div>
      {action && <div className="page-heading-action">{action}</div>}
    </div>
  );
}

function SectionHeading({
  title,
  note,
  action,
}: {
  title: string;
  note?: string;
  action?: ReactNode;
}) {
  return (
    <div className="section-heading">
      <div>
        <h2>{title}</h2>
        {note && <p>{note}</p>}
      </div>
      {action}
    </div>
  );
}

function StatusPill({ children, tone = "neutral" }: { children: ReactNode; tone?: string }) {
  return (
    <span className={`status-pill status-${tone}`}>
      <i />
      {children}
    </span>
  );
}

function EmptyState({
  icon: Icon = FileSearch,
  title,
  description,
  action,
}: {
  icon?: IconType;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <Icon size={22} />
      </span>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}

function AnalysisForm({
  compact = false,
  initialUrl = "",
}: {
  compact?: boolean;
  initialUrl?: string;
}) {
  const navigate = useNavigate();
  const [preferences] = usePreferences();
  const [url, setUrl] = useState(() => {
    if (initialUrl) return initialUrl;
    if (typeof window !== "undefined") {
      const sp = new URLSearchParams(window.location.search);
      const qUrl = sp.get("url");
      if (qUrl) return qUrl;
    }
    return "";
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = validateWebsiteUrl(url);
    if (message) {
      setError(message);
      return;
    }
    setError("");
    setBusy(true);
    try {
      const report = saveReport(await analyzeWebsite(new URL(url.trim()).href, preferences));
      void navigate({ to: "/reports/$id", params: { id: report.id } });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The analysis could not be completed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className={`analysis-form${compact ? " analysis-form-compact" : ""}`} onSubmit={submit}>
      <label htmlFor={compact ? "dashboard-url" : "analysis-url"}>Website URL</label>
      <div className={`url-input-wrap${error ? " input-error" : ""}`}>
        <Globe2 size={18} />
        <input
          id={compact ? "dashboard-url" : "analysis-url"}
          type="url"
          value={url}
          onChange={(event) => {
            setUrl(event.target.value);
            setError("");
          }}
          placeholder="https://yourbusiness.com"
          aria-describedby={error ? "analysis-error" : undefined}
        />
        <Button type="submit" className="analyze-button" disabled={busy}>
          {busy ? (
            <>
              <LoaderCircle size={16} className="spin" /> Analyzing
            </>
          ) : (
            <>
              Analyze website <ArrowRight size={16} />
            </>
          )}
        </Button>
      </div>
      {error && (
        <p id="analysis-error" role="alert" className="form-error">
          <CircleAlert size={15} />
          {error}
        </p>
      )}
      {!compact && (
        <div className="form-helper">
          <span>
            <LockKeyhole size={13} />
            No passwords or private pages
          </span>
          <button
            type="button"
            onClick={() => {
              setUrl("https://northstarstudio.example");
              setMessage(
                "Sample address added. Enable sample mode in Settings to explore a complete example.",
              );
            }}
          >
            Try a sample address
          </button>
        </div>
      )}
      {message && (
        <p className="inline-note" role="status">
          {message}
        </p>
      )}
    </form>
  );
}

export function DashboardPage() {
  const [preferences, setPreferences] = usePreferences();
  const history = readHistory();
  const recent = history.slice(0, 4);
  const last = history[0];
  return (
    <AppShell title="Overview">
      <PageHeader
        eyebrow="YOUR INTELLIGENCE WORKSPACE"
        title="Website Intelligence Overview"
        description="Turn a business website into clearer market, search, and audience insights."
        action={
          <span className="overview-date">
            <Clock3 size={15} />
            {new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date())}
          </span>
        }
      />
      <section className="analysis-hero">
        <div className="analysis-hero-copy">
          <span className="hero-kicker">
            <Sparkles size={14} /> WEBSITE INTELLIGENCE
          </span>
          <h2>
            Know what your website
            <br className="desktop-break" /> is telling the market.
          </h2>
          <p>
            Explore competitor positioning, SEO opportunities, services and customer insights —
            grounded in your website.
          </p>
          <div className="hero-trust">
            <span>
              <ShieldCheck size={15} />
              Evidence-aware insights
            </span>
            <span>
              <LockKeyhole size={14} />
              Secure by design
            </span>
          </div>
        </div>
        <div className="analysis-hero-form">
          <AnalysisForm compact />
          <p>Discover competitors, SEO opportunities, services, customers and search queries.</p>
        </div>
        <span className="hero-art" aria-hidden="true">
          <span className="hero-orbit orbit-one" />
          <span className="hero-orbit orbit-two" />
          <span className="hero-center">
            <BrandMark small />
          </span>
          <span className="hero-node node-one">
            <Search size={14} />
          </span>
          <span className="hero-node node-two">
            <Users2 size={14} />
          </span>
          <span className="hero-node node-three">
            <TrendingUp size={14} />
          </span>
        </span>
      </section>

      <div className="evaluator-quickcheck p-4 rounded-xl border border-[#E5E7EF] bg-white shadow-xs mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="p-2 rounded-lg bg-[#EEF0FD] text-[#4355E8]">
            <Radar size={18} />
          </span>
          <div>
            <h4 className="text-sm font-semibold text-[#141B2C]">Evaluator Quick-Check Presets</h4>
            <p className="text-xs text-[#475467]">
              One-click live target evaluation for practical test review
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {[
            { label: "Stripe", url: "https://stripe.com" },
            { label: "Linear", url: "https://linear.app" },
            { label: "Supabase", url: "https://supabase.com" },
            { label: "Notion", url: "https://notion.so" },
          ].map((preset) => (
            <Link
              key={preset.label}
              to="/analyze"
              search={{ url: preset.url }}
              className="px-3 py-1.5 text-xs font-medium rounded-lg border border-[#E5E7EF] bg-slate-50 hover:border-[#4355E8] hover:text-[#4355E8] hover:bg-[#EEF0FD] transition-colors"
            >
              {preset.label}
            </Link>
          ))}
        </div>
      </div>

      <div className="overview-metrics">
        <div className="metric-card">
          <span className="metric-icon metric-icon-blue">
            <FileSearch size={17} />
          </span>
          <div>
            <p>Total analyses</p>
            <strong>{history.length}</strong>
          </div>
          <span className="metric-note">in this workspace</span>
        </div>
        <div className="metric-card">
          <span className="metric-icon metric-icon-teal">
            <CircleCheck size={17} />
          </span>
          <div>
            <p>Completed</p>
            <strong>{history.filter((item) => item.status === "completed").length}</strong>
          </div>
          <span className="metric-note">reports saved</span>
        </div>
        <div className="metric-card">
          <span className="metric-icon metric-icon-violet">
            <Clock3 size={17} />
          </span>
          <div>
            <p>Last analysis</p>
            <strong className="metric-date">
              {last
                ? new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(
                    new Date(last.analyzedAt),
                  )
                : "—"}
            </strong>
          </div>
          <span className="metric-note">{last?.brand || "Not yet analyzed"}</span>
        </div>
        <div className="metric-card">
          <span className="metric-icon metric-icon-amber">
            <Layers3 size={17} />
          </span>
          <div>
            <p>Insight categories</p>
            <strong>05</strong>
          </div>
          <span className="metric-note">included per report</span>
        </div>
      </div>
      <div className="dashboard-columns">
        <section className="section-block recent-section">
          <SectionHeading
            title="Recent analyses"
            note="Your saved website intelligence reports"
            action={
              <Link to="/history" className="text-link">
                View history <ArrowRight size={14} />
              </Link>
            }
          />
          {recent.length ? (
            <div className="recent-list">
              {recent.map((item) => (
                <RecentRow key={item.id} item={item} />
              ))}
            </div>
          ) : (
            <div className="recent-empty">
              <EmptyState
                icon={History}
                title="Your research starts here"
                description="Run a website analysis and your reports will appear here."
                action={
                  <Link to="/analyze" className="text-link">
                    Start an analysis <ArrowRight size={14} />
                  </Link>
                }
              />
            </div>
          )}
        </section>
        <section className="section-block setup-section">
          <SectionHeading title="Workspace mode" note="Choose how you want to explore." />
          <div className="mode-selector">
            <button
              className={preferences.mode === "demo" ? "mode-option selected" : "mode-option"}
              onClick={() => setPreferences({ ...preferences, mode: "demo" })}
            >
              <span className="mode-option-icon">
                <Sparkles size={17} />
              </span>
              <span>
                <b>Sample mode</b>
                <small>Explore with a clearly labelled example</small>
              </span>
              {preferences.mode === "demo" && <Check size={16} />}
            </button>
            <button
              className={preferences.mode === "live" ? "mode-option selected" : "mode-option"}
              onClick={() => setPreferences({ ...preferences, mode: "live" })}
            >
              <span className="mode-option-icon live-icon">
                <Globe2 size={17} />
              </span>
              <span>
                <b>Live API</b>
                <small>Analyze with your Python service</small>
              </span>
              {preferences.mode === "live" && <Check size={16} />}
            </button>
          </div>
          <Link to="/settings" className="settings-inline">
            Configure API connection <ArrowUpRight size={14} />
          </Link>
        </section>
      </div>
      <section className="section-block features-section">
        <SectionHeading
          title="Five dimensions of intelligence"
          note="Every report explores the details that matter to your next decision."
        />
        <div className="feature-grid">
          {features.map(({ label, description, icon: Icon, color }) => (
            <div key={label} className="feature-item">
              <span className={`feature-icon ${color}`}>
                <Icon size={18} />
              </span>
              <h3>{label}</h3>
              <p>{description}</p>
            </div>
          ))}
        </div>
      </section>
    </AppShell>
  );
}

function RecentRow({ item }: { item: HistoryEntry }) {
  return (
    <div className="recent-row">
      <span className="site-favicon">
        <Globe2 size={17} />
      </span>
      <div className="recent-site">
        <b>{item.brand}</b>
        <span>{safeDomain(item.website)}</span>
      </div>
      <span className="recent-category">{item.category || "—"}</span>
      <StatusPill tone={item.sample ? "sample" : "success"}>
        {item.sample ? "Sample" : "Complete"}
      </StatusPill>
      <Link
        to="/reports/$id"
        params={{ id: item.id }}
        aria-label={`View report for ${item.brand}`}
        className="row-arrow"
      >
        <ArrowRight size={16} />
      </Link>
    </div>
  );
}

function safeDomain(value: string) {
  try {
    return new URL(value).hostname.replace(/^www\./, "");
  } catch {
    return value;
  }
}

export function AnalyzePage() {
  const [preferences] = usePreferences();
  const history = readHistory();
  return (
    <AppShell title="Analyze website">
      <PageHeader
        eyebrow="NEW ANALYSIS"
        title="Understand a website."
        description="Start with any public business website. LinkIntel turns what it says into a structured, evidence-aware report."
      />
      <div className="analyze-layout">
        <section className="analysis-workspace">
          <div className="analysis-step">
            <span>01</span>
            <div>
              <h2>Enter a website</h2>
              <p>We’ll inspect its publicly accessible pages and business information.</p>
            </div>
          </div>
          <div className="analysis-panel">
            <AnalysisForm />
            <div className="url-suggestions">
              <span>Try a format like</span>
              <code>https://example.com</code>
              <span className="suggestion-divider">or</span>
              <code>https://www.acme.co</code>
            </div>
          </div>
          <div className="analysis-step analysis-step-secondary">
            <span>02</span>
            <div>
              <h2>What your report covers</h2>
              <p>All five insight categories are included in every analysis.</p>
            </div>
          </div>
          <div className="analysis-category-list">
            {features.map(({ label, description, icon: Icon, color }, i) => (
              <div className="analysis-category" key={label}>
                <span className={`feature-icon ${color}`}>
                  <Icon size={17} />
                </span>
                <div>
                  <b>{label}</b>
                  <small>{description}</small>
                </div>
                <span className="category-index">0{i + 1}</span>
              </div>
            ))}
          </div>
        </section>
        <aside className="analysis-aside">
          <div className="aside-intro">
            <span className="aside-intro-icon">
              <Compass size={19} />
            </span>
            <h3>Designed for useful answers</h3>
            <p>
              Specific findings where the website provides evidence. Clearly marked inferences where
              the answer requires interpretation.
            </p>
          </div>
          <div className="report-includes">
            <p>YOUR REPORT INCLUDES</p>
            {[
              "Brand overview",
              "Competitor positioning",
              "Five target search queries",
              "SEO recommendations",
              "Services and audience",
            ].map((item) => (
              <div key={item}>
                <Check size={14} />
                {item}
              </div>
            ))}
          </div>
          <div className="secure-note">
            <ShieldCheck size={16} />
            <span>
              <b>Public pages only</b>
              <small>We never request login credentials or bypass access controls.</small>
            </span>
          </div>
          <div className="mode-note">
            <span className={preferences.mode === "demo" ? "mode-note-sample" : "mode-note-live"}>
              <i />
              {preferences.mode === "demo" ? "SAMPLE MODE" : "LIVE API MODE"}
            </span>
            <p>
              {preferences.mode === "demo"
                ? "Analysis results are labelled sample data and are not presented as real website findings."
                : "Reports come from your configured FastAPI endpoint. No sample fallback is used."}
            </p>
          </div>
        </aside>
      </div>
      {history.length > 0 && (
        <section className="section-block recent-analysis-bottom">
          <SectionHeading
            title="Continue your research"
            note={`${history.length} report${history.length === 1 ? "" : "s"} saved on this device`}
            action={
              <Link to="/history" className="text-link">
                Open history <ArrowRight size={14} />
              </Link>
            }
          />
        </section>
      )}
    </AppShell>
  );
}

const queryIntents = [
  "All intents",
  "Informational",
  "Commercial",
  "Transactional",
  "Navigational",
  "Service discovery",
];

export function ReportPage() {
  const { id = "" } = useParams({ strict: false });
  const [preferences] = usePreferences();
  const [report, setReport] = useState<LinkAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [activeTab, setActiveTab] = useState("competitors");
  const [copied, setCopied] = useState("");
  const [queryFilter, setQueryFilter] = useState("All intents");
  const [showJson, setShowJson] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const local = getReport(id);
    if (local) {
      setReport(local);
      return;
    }
    if (id && preferences.mode !== "demo") {
      setLoading(true);
      fetchReportById(preferences.apiBaseUrl, id)
        .then((fetched) => {
          if (fetched) {
            saveReport(fetched);
            setReport(fetched);
          }
        })
        .catch((err) => {
          setErrorMsg(err instanceof Error ? err.message : "Report could not be retrieved.");
        })
        .finally(() => setLoading(false));
    }
  }, [id, preferences.apiBaseUrl, preferences.mode]);

  const copyText = async (key: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(key);
      window.setTimeout(() => setCopied(""), 1600);
    } catch {
      setCopied("");
    }
  };
  const exportJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = `linkintel-${safeDomain(report.website)}.json`;
    link.click();
    URL.revokeObjectURL(href);
  };

  if (loading) {
    return (
      <AppShell title="Loading report...">
        <div className="flex flex-col items-center justify-center min-h-[50vh] p-8">
          <LoaderCircle size={36} className="animate-spin text-[#4355E8] mb-4" />
          <p className="text-sm font-medium text-[#141B2C]">
            Fetching report from workspace archive...
          </p>
        </div>
      </AppShell>
    );
  }

  if (!report)
    return (
      <AppShell title="Report not found">
        <PageHeader
          title="Report not found"
          description={errorMsg || "This report is not available on this device."}
        />
        <EmptyState
          title="No saved report here"
          description="The report may have been removed or opened in a different browser."
          action={
            <Link to="/history" className="text-link">
              Back to history <ArrowRight size={14} />
            </Link>
          }
        />
      </AppShell>
    );
  const analysis = report.analysis;
  return (
    <AppShell title="Analysis report">
      <div className="report-back">
        <Link to="/history" className="back-link">
          <ArrowLeft size={15} />
          All analyses
        </Link>
        {report.metadata.sample_data && <StatusPill tone="sample">SAMPLE DATA</StatusPill>}
      </div>
      <div className="report-title-row">
        <div>
          <p className="eyebrow">WEBSITE INTELLIGENCE REPORT</p>
          <h1>{report.brand.name}</h1>
          <div className="report-domain">
            <Globe2 size={14} />
            <span>{safeDomain(report.website)}</span>
            <a
              href={report.website}
              target="_blank"
              rel="noreferrer"
              aria-label="Open analyzed website"
            >
              <ExternalLink size={13} />
            </a>
            <span className="report-dot">·</span>
            <span>{report.brand.category}</span>
          </div>
        </div>
        <div className="report-actions">
          <Button variant="outline" onClick={() => setShowJson(!showJson)}>
            <Code2 size={15} />
            {showJson ? "Hide JSON" : "View JSON"}
          </Button>
          <Button
            variant="outline"
            onClick={() => void copyText("report", JSON.stringify(report, null, 2))}
          >
            {copied === "report" ? <Check size={15} /> : <Copy size={15} />}
            {copied === "report" ? "Copied" : "Copy report"}
          </Button>
          <Button onClick={exportJson}>
            <ArrowDownToLine size={15} />
            Export JSON
          </Button>
        </div>
      </div>
      <div className="report-meta-strip">
        <span>
          <Clock3 size={14} />
          Analyzed{" "}
          {new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(
            new Date(report.metadata.analyzed_at),
          )}
        </span>
        <span>
          <FileJson2 size={14} />
          Report {report.metadata.report_id}
        </span>
        {report.metadata.model && (
          <span>
            <BrainCircuit size={14} />
            {report.metadata.model}
          </span>
        )}
        {report.metadata.cost_breakdown && (
          <span
            title={`Input: ${report.metadata.cost_breakdown.input_tokens ?? 0} tokens | Output: ${report.metadata.cost_breakdown.output_tokens ?? 0} tokens | Source: ${report.metadata.cost_breakdown.pricing_verification_date}`}
          >
            <Coins size={14} />
            {report.metadata.cost_breakdown.total_estimated_cost_usd !== null &&
            report.metadata.cost_breakdown.total_estimated_cost_usd !== undefined
              ? `$${report.metadata.cost_breakdown.total_estimated_cost_usd.toFixed(6)}`
              : "Cost N/A"}{" "}
            ({report.metadata.cost_breakdown.total_tokens?.toLocaleString() ?? 0} tokens)
          </span>
        )}
        <StatusPill tone={report.metadata.sample_data ? "sample" : "success"}>
          {report.metadata.sample_data ? "Sample report" : "Analysis complete"}
        </StatusPill>
      </div>
      {report.metadata.sample_data && (
        <div className="sample-banner">
          <Sparkles size={16} />
          <span>
            <b>Illustrative sample report.</b> The company and insights below are fictional; no
            website has been fetched or verified.
          </span>
        </div>
      )}
      {report.metadata.extraction_warnings.length > 0 && !report.metadata.sample_data && (
        <div className="report-warning">
          <CircleAlert size={16} />
          <span>{report.metadata.extraction_warnings.join(" · ")}</span>
        </div>
      )}
      {showJson && <pre className="json-preview">{JSON.stringify(report, null, 2)}</pre>}
      <section className="brand-summary-panel">
        <div className="brand-summary-avatar">
          <BrandMark small />
        </div>
        <div className="brand-summary-main">
          <p className="eyebrow">BRAND OVERVIEW</p>
          <h2>{report.brand.name}</h2>
          <p>{report.brand.summary}</p>
          <div className="summary-tags">
            <span>
              <BriefcaseBusiness size={13} />
              {report.brand.category}
            </span>
            <span>
              <Globe2 size={13} />
              {report.metadata.canonical_url || report.website}
            </span>
          </div>
        </div>
        <span className="brand-category-chip">BUSINESS PROFILE</span>
      </section>
      <div className="report-tab-bar" role="tablist" aria-label="Analysis report sections">
        {tabs.map(({ id: tabId, label, icon: Icon }) => (
          <button
            key={tabId}
            role="tab"
            aria-selected={activeTab === tabId}
            className={activeTab === tabId ? "report-tab active" : "report-tab"}
            onClick={() => setActiveTab(tabId)}
          >
            <Icon size={16} />
            {label}
            {tabId === "queries" && <span>{analysis.target_search_queries.length}</span>}
          </button>
        ))}
      </div>
      <div className="report-tab-content">
        {activeTab === "competitors" && (
          <CompetitorsSection report={report} copyText={copyText} copied={copied} />
        )}
        {activeTab === "queries" && (
          <QueriesSection
            items={analysis.target_search_queries}
            filter={queryFilter}
            setFilter={setQueryFilter}
            copyText={copyText}
            copied={copied}
          />
        )}
        {activeTab === "seo" && <SeoSection report={report} copyText={copyText} copied={copied} />}
        {activeTab === "services" && <ServicesSection services={analysis.top_services} />}
        {activeTab === "audience" && <AudienceSection report={report} />}
      </div>
    </AppShell>
  );
}

function EvidenceTag({ value }: { value: string }) {
  const label = value.replaceAll("_", " ");
  return <span className={`evidence-tag evidence-${value}`}>{label}</span>;
}

function CompetitorsSection({
  report,
  copyText,
  copied,
}: {
  report: LinkAnalysis;
  copyText: (key: string, value: string) => void;
  copied: string;
}) {
  const data = report.analysis.competitor_analysis;
  return (
    <>
      <SectionHeading
        title="Competitive landscape"
        note={data.overview}
        action={<StatusPill tone="neutral">{data.competitors.length} suggestions</StatusPill>}
      />
      <div className="report-insight-grid">
        <div className="insight-card">
          <span className="insight-card-icon feature-blue">
            <Target size={17} />
          </span>
          <p>YOUR POSITIONING</p>
          <h3>{report.brand.category}</h3>
          <span>{report.brand.name} · submitted brand</span>
        </div>
        <div className="insight-card">
          <span className="insight-card-icon feature-teal">
            <TrendingUp size={17} />
          </span>
          <p>COMPETITIVE ADVANTAGE</p>
          <h3>{data.advantages[0] || "No clear advantage extracted"}</h3>
          <span>Evidence-aware summary</span>
        </div>
        <div className="insight-card">
          <span className="insight-card-icon feature-amber">
            <Lightbulb size={17} />
          </span>
          <p>MARKET OPPORTUNITY</p>
          <h3>{data.opportunities[0] || "More evidence needed"}</h3>
          <span>AI inference · validate before acting</span>
        </div>
      </div>
      {data.competitors.length === 0 ? (
        <EmptyState
          icon={Radar}
          title="No verified competitors identified"
          description="The analysis did not find enough reliable, attributable competitor evidence. We won’t invent brands to fill the list."
        />
      ) : (
        <>
          <SectionHeading
            title="Suggested competitor comparison"
            note="AI-generated suggestions are not independently verified unless a source is shown."
          />
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>COMPANY</th>
                  <th>POSITIONING</th>
                  <th>STRENGTHS</th>
                  <th>GAPS / OPPORTUNITY</th>
                  <th>PROVENANCE</th>
                </tr>
              </thead>
              <tbody>
                {data.competitors.map((item, index) => (
                  <CompetitorRow key={`${item.name}-${index}`} item={item} />
                ))}
              </tbody>
            </table>
          </div>
          <div className="competitor-cards">
            {data.competitors.map((item, index) => (
              <CompetitorCard key={`card-${item.name}-${index}`} item={item} />
            ))}
          </div>
        </>
      )}
      <div className="landscape-bottom-grid">
        <div className="content-panel">
          <h3>Your competitive advantages</h3>
          <BulletList items={data.advantages} empty="No clear advantages extracted yet." />
        </div>
        <div className="content-panel">
          <h3>Positioning opportunities</h3>
          <BulletList items={data.opportunities} empty="No opportunity identified." />
        </div>
        <div className="content-panel">
          <h3>Observed gaps</h3>
          <BulletList items={data.weaknesses} empty="No supported gaps identified." />
        </div>
      </div>
      {data.evidence.length > 0 && (
        <div className="sources-block">
          <h3>Evidence sources</h3>
          {data.evidence.map((source) => (
            <a key={source} href={source} target="_blank" rel="noreferrer">
              {source}
              <ExternalLink size={12} />
            </a>
          ))}
        </div>
      )}
    </>
  );
}

function CompetitorRow({ item }: { item: Competitor }) {
  return (
    <tr>
      <td>
        <div className="table-brand">
          <span className="table-brand-icon">
            <Globe2 size={15} />
          </span>
          <span>
            <b>{item.name}</b>
            <a href={item.website} target="_blank" rel="noreferrer">
              {safeDomain(item.website)} <ExternalLink size={11} />
            </a>
          </span>
        </div>
      </td>
      <td>{item.positioning || item.category || "—"}</td>
      <td>
        <BulletList items={item.strengths} empty="Not assessed" compact />
      </td>
      <td>
        <span>{item.opportunity || item.gaps.join(" · ") || "Not assessed"}</span>
      </td>
      <td>
        <EvidenceTag value={item.evidence} />
        {item.source_urls.length > 0 && (
          <a
            className="source-indicator"
            href={item.source_urls[0]}
            target="_blank"
            rel="noreferrer"
          >
            {" "}
            Source <ExternalLink size={10} />
          </a>
        )}
      </td>
    </tr>
  );
}

function CompetitorCard({ item }: { item: Competitor }) {
  return (
    <article className="competitor-card">
      <div className="competitor-card-head">
        <span className="table-brand-icon">
          <Globe2 size={15} />
        </span>
        <div>
          <h3>{item.name}</h3>
          <a href={item.website} target="_blank" rel="noreferrer">
            {safeDomain(item.website)} <ExternalLink size={11} />
          </a>
        </div>
        <EvidenceTag value={item.evidence} />
      </div>
      <p>{item.description || "No description available."}</p>
      <div className="competitor-card-columns">
        <div>
          <b>Strengths</b>
          <BulletList items={item.strengths} empty="Not identified" compact />
        </div>
        <div>
          <b>Gaps</b>
          <BulletList items={item.gaps} empty="Not identified" compact />
        </div>
      </div>
    </article>
  );
}

function BulletList({
  items,
  empty,
  compact = false,
}: {
  items: string[];
  empty: string;
  compact?: boolean;
}) {
  if (!items.length) return <span className="muted-empty">{empty}</span>;
  return (
    <ul className={compact ? "bullet-list bullet-list-compact" : "bullet-list"}>
      {items.map((item, i) => (
        <li key={`${i}-${item}`}>{item}</li>
      ))}
    </ul>
  );
}

function QueriesSection({
  items,
  filter,
  setFilter,
  copyText,
  copied,
}: {
  items: SearchQuery[];
  filter: string;
  setFilter: (value: string) => void;
  copyText: (key: string, value: string) => void;
  copied: string;
}) {
  const queries =
    filter === "All intents"
      ? items
      : items.filter((item) => item.intent.toLowerCase() === filter.toLowerCase());
  return (
    <>
      <SectionHeading
        title="Search query intelligence"
        note="Five strategy-led query ideas. No search-volume or ranking data is fabricated."
        action={
          <span className="metric-inline">
            <Search size={14} />
            {items.length} queries
          </span>
        }
      />
      <div className="query-toolbar">
        <span>
          <Filter size={14} /> Filter by intent
        </span>
        <select
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          aria-label="Filter search queries by intent"
        >
          {queryIntents.map((intent) => (
            <option key={intent}>{intent}</option>
          ))}
        </select>
        <span className="no-volume-note">
          <i />
          No verified search-volume data available
        </span>
      </div>
      <div className="query-list">
        {queries.length ? (
          queries.map((item, index) => (
            <article key={`${item.query}-${index}`} className="query-row">
              <span className="query-number">0{index + 1}</span>
              <div className="query-main">
                <h3>{item.query}</h3>
                <p>{item.relevance}</p>
                <div className="query-meta">
                  <span
                    className={`intent-tag intent-${item.intent.toLowerCase().replaceAll(" ", "-")}`}
                  >
                    {item.intent}
                  </span>
                  <span>
                    <Users2 size={12} />
                    {item.audience}
                  </span>
                  <div className="platforms">
                    {item.platforms.map((platform) => (
                      <span key={platform}>{platform}</span>
                    ))}
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Copy ${item.query}`}
                onClick={() => void copyText(`query-${index}`, item.query)}
              >
                {copied === `query-${index}` ? <Check size={16} /> : <Copy size={15} />}
              </Button>
            </article>
          ))
        ) : (
          <EmptyState
            icon={Search}
            title="No queries match this intent"
            description="Choose another filter to view the suggested search queries."
          />
        )}
      </div>
      <div className="platform-coverage">
        <span>PLATFORMS CONSIDERED</span>
        {["Google", "Facebook", "Instagram", "LinkedIn", "X"].map((platform) => (
          <b key={platform}>
            <Check size={12} />
            {platform}
          </b>
        ))}
      </div>
    </>
  );
}

function CopyField({
  title,
  value,
  reason,
  copyText,
  copied,
  id,
}: {
  title: string;
  value: string | null;
  reason?: string;
  copyText: (key: string, value: string) => void;
  copied: string;
  id: string;
}) {
  return (
    <div className="copy-field">
      <div className="copy-field-top">
        <span>{title}</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => value && void copyText(id, value)}
          disabled={!value}
        >
          {copied === id ? <Check size={13} /> : <Copy size={13} />}
          {copied === id ? "Copied" : "Copy"}
        </Button>
      </div>
      <div className="copy-field-value">{value || "Not available in the source website."}</div>
      {reason && <p>{reason}</p>}
    </div>
  );
}

function SeoSection({
  report,
  copyText,
  copied,
}: {
  report: LinkAnalysis;
  copyText: (key: string, value: string) => void;
  copied: string;
}) {
  const seo = report.analysis.seo_improvements;
  const keywords = [
    ...seo.secondary_keywords.map((word) => ({ word, type: "Secondary" })),
    ...seo.long_tail_keywords.map((word) => ({ word, type: "Long-tail" })),
    ...seo.business_keywords.map((word) => ({ word, type: "Business" })),
  ];
  const statusLabel: Record<string, string> = {
    present: "Present",
    missing: "Missing",
    potential_issue: "Potential issue",
    not_inspected: "Not inspected",
  };
  return (
    <>
      <SectionHeading
        title="On-page SEO intelligence"
        note="Recommendations are based on the extracted page content, not search-engine ranking data."
        action={<StatusPill tone="neutral">{seo.search_volume_note}</StatusPill>}
      />
      <div className="seo-overview-strip">
        <div>
          <span>PRIMARY KEYWORD</span>
          <strong>{seo.primary_keyword || "Not identified"}</strong>
        </div>
        <div>
          <span>SUPPORTING TERMS</span>
          <strong>{keywords.length}</strong>
        </div>
        <div>
          <span>PAGE SIGNALS</span>
          <strong>{seo.technical_findings.length}</strong>
        </div>
        <div>
          <span>SCOPE</span>
          <strong>Page-level review</strong>
        </div>
      </div>
      <div className="seo-two-col">
        <div className="content-panel">
          <h3>
            <span className="panel-heading-icon feature-blue">
              <Tags size={15} />
            </span>
            Keyword recommendations
          </h3>
          <div className="primary-keyword">
            <span>PRIMARY</span>
            <b>{seo.primary_keyword || "—"}</b>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Copy primary keyword"
              onClick={() =>
                seo.primary_keyword && void copyText("primary-keyword", seo.primary_keyword)
              }
            >
              {copied === "primary-keyword" ? <Check size={14} /> : <Copy size={14} />}
            </Button>
          </div>
          <p className="field-note">
            Chosen for alignment with the website’s stated business and offer.
          </p>
          <div className="keyword-chips">
            {keywords.map(({ word, type }) => (
              <span key={`${type}-${word}`}>
                <b>{type}</b>
                {word}
              </span>
            ))}
          </div>
        </div>
        <div className="content-panel">
          <h3>
            <span className="panel-heading-icon feature-teal">
              <FileSearch size={15} />
            </span>
            Page title & description
          </h3>
          <div className="existing-meta">
            <span>EXISTING TITLE</span>
            <p>{seo.current_title || "Not extracted"}</p>
            <span>EXISTING META DESCRIPTION</span>
            <p>{seo.current_meta_description || "Not extracted"}</p>
          </div>
        </div>
      </div>
      <div className="seo-two-col seo-recommendations">
        <CopyField
          id="seo-title"
          title="RECOMMENDED TITLE"
          value={seo.recommended_title}
          reason={seo.title_reason}
          copyText={copyText}
          copied={copied}
        />
        <CopyField
          id="seo-description"
          title="RECOMMENDED META DESCRIPTION"
          value={seo.recommended_meta_description}
          reason={seo.business_summary}
          copyText={copyText}
          copied={copied}
        />
      </div>
      <section className="content-panel content-panel-spaced">
        <h3>
          <span className="panel-heading-icon feature-amber">
            <Lightbulb size={15} />
          </span>
          Supporting content ideas
        </h3>
        <div className="content-ideas">
          {seo.supporting_content.map((idea, i) => (
            <div key={idea}>
              <span>0{i + 1}</span>
              <p>{idea}</p>
              <ArrowUpRight size={14} />
            </div>
          ))}
        </div>
      </section>
      <section className="content-panel content-panel-spaced">
        <div className="technical-heading">
          <div>
            <h3>
              <span className="panel-heading-icon feature-violet">
                <Gauge size={15} />
              </span>
              Technical signals observed
            </h3>
            <p>
              Lightweight inspection of public page markup; this is not a full technical SEO audit.
            </p>
          </div>
          <span className="not-ranking">
            <ShieldCheck size={13} />
            Not a ranking assessment
          </span>
        </div>
        <div className="technical-grid">
          {seo.technical_findings.map((item) => (
            <div className="technical-item" key={item.name}>
              <span className="technical-state">
                {item.status === "present" ? (
                  <Check size={13} />
                ) : item.status === "missing" ? (
                  <X size={13} />
                ) : (
                  <CircleAlert size={13} />
                )}
                {statusLabel[item.status]}
              </span>
              <h4>{item.name}</h4>
              <p>{item.value || item.note}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

function ServicesSection({ services }: { services: ServiceInsight[] }) {
  return (
    <>
      <SectionHeading
        title="Services identified"
        note="Only offerings supported by website evidence or a clearly marked inference are included."
        action={<StatusPill tone="neutral">{services.length} identified</StatusPill>}
      />
      {services.length ? (
        <div className="service-grid">
          {services.map((service, index) => (
            <ServiceCard service={service} index={index} key={`${service.name}-${index}`} />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Layers3}
          title="No services confidently identified"
          description="The available website content did not support a reliable service list."
        />
      )}
    </>
  );
}

function ServiceCard({ service, index }: { service: ServiceInsight; index: number }) {
  return (
    <article className="service-card">
      <div className="service-card-top">
        <span className="service-number">0{index + 1}</span>
        <EvidenceTag value={service.evidence} />
      </div>
      <h3>{service.name}</h3>
      <p>{service.description || "No supporting description available."}</p>
      <div className="service-benefit">
        <span>CUSTOMER BENEFIT</span>
        <p>{service.benefit || "Not available"}</p>
      </div>
      <div className="service-meta">
        <div>
          <span>Industry</span>
          <b>{service.target_industry || "Not identified"}</b>
        </div>
        <div>
          <span>Customer</span>
          <b>{service.target_customer || "Not identified"}</b>
        </div>
      </div>
      {service.source && (
        <a className="service-source" href={service.source} target="_blank" rel="noreferrer">
          View evidence <ExternalLink size={12} />
        </a>
      )}
    </article>
  );
}

function AudienceSection({ report }: { report: LinkAnalysis }) {
  const audience = report.analysis.target_audience;
  return (
    <>
      <SectionHeading
        title="Audience intelligence"
        note="Audience profiles combine extracted business information with qualified strategic inference."
        action={
          <span className="metric-inline">
            <Users2 size={15} />
            Customer profiles
          </span>
        }
      />
      <div className="audience-overview">
        <div className="audience-lead-icon">
          <Users2 size={21} />
        </div>
        <div>
          <span>PRIMARY AUDIENCE</span>
          <h2>{audience.primary_audience || "Not identified from available evidence"}</h2>
        </div>
        <div className="audience-secondary">
          <span>ALSO RELEVANT</span>
          <div>
            {audience.secondary_audience.length ? (
              audience.secondary_audience.map((item) => <b key={item}>{item}</b>)
            ) : (
              <span>Not identified</span>
            )}
          </div>
        </div>
      </div>
      <div className="audience-profile-grid">
        {audience.profiles.map((profile, i) => (
          <AudienceCard key={`${profile.name}-${i}`} profile={profile} index={i} />
        ))}
      </div>
      {audience.profiles.length === 0 && (
        <EmptyState
          icon={Users2}
          title="No audience profiles yet"
          description="The website content didn’t support a sufficiently specific audience profile."
        />
      )}
      <div className="audience-bottom-grid">
        <div className="content-panel">
          <h3>
            <BriefcaseBusiness size={15} />
            Industry segments
          </h3>
          <TagList items={audience.industry_segments} empty="No industry segments identified" />
        </div>
        <div className="content-panel">
          <h3>
            <Layers3 size={15} />
            Business types
          </h3>
          <TagList items={audience.business_types} empty="No business types identified" />
        </div>
        <div className="content-panel">
          <h3>
            <Globe2 size={15} />
            Geographic focus
          </h3>
          <TagList items={audience.geographic_focus} empty="No geographic presence verified" />
        </div>
      </div>
      <div className="audience-bottom-grid audience-bottom-grid-lower">
        <div className="content-panel">
          <h3>Customer needs</h3>
          <BulletList items={audience.needs} empty="Not identified" />
        </div>
        <div className="content-panel">
          <h3>Challenges</h3>
          <BulletList items={audience.challenges} empty="Not identified" />
        </div>
        <div className="content-panel">
          <h3>Interests</h3>
          <BulletList items={audience.interests} empty="Not identified" />
        </div>
      </div>
      {audience.marketing_segments.length > 0 && (
        <section className="content-panel content-panel-spaced">
          <h3>
            <Target size={15} />
            Recommended marketing segments
          </h3>
          <TagList items={audience.marketing_segments} />
        </section>
      )}
    </>
  );
}

function AudienceCard({ profile, index }: { profile: AudienceProfile; index: number }) {
  return (
    <article className="audience-card">
      <div className="audience-card-head">
        <span className={`audience-persona-icon persona-${index % 3}`}>
          <Users2 size={18} />
        </span>
        <span>PROFILE 0{index + 1}</span>
        <EvidenceTag value={profile.evidence} />
      </div>
      <h3>{profile.name}</h3>
      <p className="persona-type">{profile.business_type}</p>
      <div className="persona-details">
        <div>
          <b>Needs</b>
          <BulletList items={profile.needs} empty="Not identified" compact />
        </div>
        <div>
          <b>Challenges</b>
          <BulletList items={profile.challenges} empty="Not identified" compact />
        </div>
        <div>
          <b>Relevant services</b>
          <TagList items={profile.services} empty="Not identified" />
        </div>
      </div>
      <div className="persona-opportunity">
        <span>MARKETING OPPORTUNITY</span>
        <p>{profile.opportunity || "Not identified"}</p>
      </div>
    </article>
  );
}

function TagList({ items, empty = "Not identified" }: { items: string[]; empty?: string }) {
  if (!items.length) return <span className="muted-empty">{empty}</span>;
  return (
    <div className="tag-list">
      {items.map((item) => (
        <span key={item}>{item}</span>
      ))}
    </div>
  );
}

export function HistoryPage() {
  const [preferences] = usePreferences();
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("All status");
  const [category, setCategory] = useState("All categories");
  const [sortNewest, setSortNewest] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  useEffect(() => {
    // 1. Initial load from local storage
    const local = readHistory();
    setEntries(local);

    // 2. Query persistent backend database if in live mode
    if (preferences.mode !== "demo") {
      fetchReportsList(preferences.apiBaseUrl)
        .then((res) => {
          if (res && res.items && res.items.length > 0) {
            const dbEntries: HistoryEntry[] = res.items.map((item) => ({
              id: item.id,
              website: item.url,
              brand: item.brand_name || item.url.replace(/^https?:\/\//, "").split("/")[0],
              category: item.category || "General",
              analyzedAt: item.created_at || new Date().toISOString(),
              sample: item.is_sample,
              status: "completed",
            }));
            const merged = [...dbEntries];
            for (const l of local) {
              if (!merged.some((m) => m.id === l.id || m.website === l.website)) {
                merged.push(l);
              }
            }
            setEntries(merged);
          }
        })
        .catch(() => {
          // Gracefully fallback to local records
        });
    }
  }, [preferences.apiBaseUrl, preferences.mode]);

  const categories = useMemo(
    () => [...new Set(entries.map((item) => item.category).filter(Boolean))],
    [entries],
  );
  const filtered = useMemo(
    () =>
      entries
        .filter((item) => {
          const term = search.toLowerCase();
          return (
            (!term || `${item.brand} ${item.website}`.toLowerCase().includes(term)) &&
            (status === "All status" || item.status === status.toLowerCase()) &&
            (category === "All categories" || item.category === category)
          );
        })
        .sort((a, b) =>
          sortNewest
            ? b.analyzedAt.localeCompare(a.analyzedAt)
            : a.analyzedAt.localeCompare(b.analyzedAt),
        ),
    [entries, search, status, category, sortNewest],
  );
  const confirmDelete = async (id: string) => {
    deleteReport(id);
    if (preferences.mode !== "demo") {
      try {
        await deleteReportById(preferences.apiBaseUrl, id);
      } catch {
        // Handled gracefully
      }
    }
    setEntries((prev) => prev.filter((item) => item.id !== id));
    setDeleteTarget(null);
  };
  return (
    <AppShell title="Analysis history">
      <PageHeader
        eyebrow="YOUR RESEARCH LIBRARY"
        title="Analysis history"
        description="All reports saved to this browser, ready when you need them."
        action={
          <Link to="/analyze" className="button-link">
            <FileSearch size={15} />
            New analysis
          </Link>
        }
      />
      <div className="history-stats">
        <div>
          <span className="metric-icon metric-icon-blue">
            <FileSearch size={17} />
          </span>
          <span>
            <small>TOTAL REPORTS</small>
            <b>{entries.length}</b>
          </span>
        </div>
        <div>
          <span className="metric-icon metric-icon-teal">
            <CircleCheck size={17} />
          </span>
          <span>
            <small>COMPLETED</small>
            <b>{entries.filter((item) => item.status === "completed").length}</b>
          </span>
        </div>
        <div>
          <span className="metric-icon metric-icon-amber">
            <Sparkles size={17} />
          </span>
          <span>
            <small>SAMPLE REPORTS</small>
            <b>{entries.filter((item) => item.sample).length}</b>
          </span>
        </div>
      </div>
      <section className="history-panel">
        <div className="history-toolbar">
          <label className="history-search">
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by brand or domain…"
              aria-label="Search analysis history"
            />
          </label>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            aria-label="Filter by status"
          >
            <option>All status</option>
            <option>completed</option>
            <option>failed</option>
          </select>
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            aria-label="Filter by category"
          >
            <option>All categories</option>
            {categories.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
          <Button variant="outline" onClick={() => setSortNewest(!sortNewest)}>
            <Clock3 size={14} />
            {sortNewest ? "Newest first" : "Oldest first"}
            <ChevronDown size={13} />
          </Button>
        </div>
        {filtered.length ? (
          <div className="table-scroll">
            <table className="data-table history-table">
              <thead>
                <tr>
                  <th>WEBSITE</th>
                  <th>CATEGORY</th>
                  <th>DATE ANALYZED</th>
                  <th>STATUS</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="table-brand">
                        <span className="table-brand-icon">
                          <Globe2 size={15} />
                        </span>
                        <span>
                          <b>{item.brand}</b>
                          <small>{safeDomain(item.website)}</small>
                        </span>
                      </div>
                    </td>
                    <td>{item.category || "—"}</td>
                    <td>
                      {new Intl.DateTimeFormat("en", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      }).format(new Date(item.analyzedAt))}
                    </td>
                    <td>
                      <StatusPill
                        tone={
                          item.sample ? "sample" : item.status === "completed" ? "success" : "error"
                        }
                      >
                        {item.sample ? "Sample" : item.status}
                      </StatusPill>
                    </td>
                    <td>
                      <div className="history-actions">
                        <Link
                          to="/reports/$id"
                          params={{ id: item.id }}
                          className="view-report-link"
                        >
                          View report <ArrowRight size={13} />
                        </Link>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Delete ${item.brand} report`}
                          onClick={() => setDeleteTarget(item.id)}
                        >
                          <MoreHorizontal size={17} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            icon={
              search || status !== "All status" || category !== "All categories" ? Search : History
            }
            title={entries.length ? "No reports match these filters" : "Your history is waiting"}
            description={
              entries.length
                ? "Try a different name or clear the active filters."
                : "Analyze a public website to create your first saved report."
            }
            action={
              !entries.length ? (
                <Link to="/analyze" className="text-link">
                  Start your first analysis <ArrowRight size={14} />
                </Link>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => {
                    setSearch("");
                    setStatus("All status");
                    setCategory("All categories");
                  }}
                >
                  Clear filters
                </Button>
              )
            }
          />
        )}
      </section>
      <p className="local-history-note">
        <LockKeyhole size={14} />
        Reports are stored locally in this browser. Clearing site data removes them.
      </p>
      {deleteTarget && (
        <div
          className="dialog-backdrop"
          role="presentation"
          onClick={(event) => {
            if (event.target === event.currentTarget) setDeleteTarget(null);
          }}
        >
          <div
            className="confirm-dialog"
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="delete-title"
          >
            <span className="confirm-icon">
              <CircleAlert size={18} />
            </span>
            <h2 id="delete-title">Delete this report?</h2>
            <p>This removes the saved report from this browser. This action cannot be undone.</p>
            <div>
              <Button variant="outline" onClick={() => setDeleteTarget(null)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={() => confirmDelete(deleteTarget)}>
                Delete report
              </Button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}

const modelProviders = [
  {
    name: "Google Gemini",
    model: "Gemini 2.5 Flash",
    description:
      "Fast multimodal model with native structured-output support; a practical default to evaluate on concise website analysis.",
    input: "See current official pricing",
    output: "See current official pricing",
    context: "1M tokens†",
    speed: "Not benchmarked",
    structured: "JSON schema mode",
    suitability: "Strong candidate · evaluate first",
    color: "provider-google",
    pricing: "https://ai.google.dev/gemini-api/docs/pricing",
    structuredUrl: "https://ai.google.dev/gemini-api/docs/structured-output",
  },
  {
    name: "OpenAI",
    model: "GPT-4.1 mini",
    description:
      "Cost-conscious model family with schema-constrained output support; compare against the same validation set.",
    input: "See current official pricing",
    output: "See current official pricing",
    context: "1M tokens†",
    speed: "Not benchmarked",
    structured: "Structured Outputs",
    suitability: "Strong alternative · compare",
    color: "provider-openai",
    pricing: "https://developers.openai.com/api/docs/pricing",
    structuredUrl: "https://developers.openai.com/api/docs/guides/structured-outputs",
  },
  {
    name: "Anthropic Claude",
    model: "Claude Haiku 4.5",
    description:
      "A lightweight Claude option suited to concise extraction; enforce the response contract with Pydantic validation.",
    input: "See current official pricing",
    output: "See current official pricing",
    context: "200K tokens†",
    speed: "Not benchmarked",
    structured: "JSON mode / tool schema‡",
    suitability: "Worth benchmarking",
    color: "provider-anthropic",
    pricing: "https://platform.claude.com/docs/en/about-claude/pricing",
    structuredUrl: "https://platform.claude.com/docs/en/build-with-claude/structured-outputs",
  },
];

export function ModelLabPage() {
  const preferences = readPreferences();
  const [expanded, setExpanded] = useState<string[]>(["Google Gemini"]);
  const [activeTab, setActiveTab] = useState("comparison");
  const [providerStatuses, setProviderStatuses] = useState<ProviderStatusItem[]>([]);

  useEffect(() => {
    fetchProviderStatus(preferences.apiBaseUrl)
      .then((data) => {
        setProviderStatuses(data.providers);
      })
      .catch(() => {
        // Handled silently when backend is starting or offline
      });
  }, [preferences.apiBaseUrl]);

  const toggle = (name: string) =>
    setExpanded((current) =>
      current.includes(name) ? current.filter((item) => item !== name) : [...current, name],
    );

  const getProviderConfigured = (name: string) => {
    const key = name.toLowerCase().includes("gemini")
      ? "gemini"
      : name.toLowerCase().includes("openai")
        ? "openai"
        : name.toLowerCase().includes("claude") || name.toLowerCase().includes("anthropic")
          ? "anthropic"
          : "";
    const found = providerStatuses.find((p) => p.provider === key);
    return found ? found.configured : null;
  };

  const checked = new Intl.DateTimeFormat("en", { dateStyle: "long" }).format(new Date());
  return (
    <AppShell title="Model research">
      <PageHeader
        eyebrow="EVALUATION & COST RESEARCH"
        title="Model research lab"
        description="A transparent comparison framework for selecting a reliable, cost-aware analysis model."
        action={
          <span className="research-updated">
            <Clock3 size={14} />
            Pricing sources checked {checked}
          </span>
        }
      />
      <div className="research-callout">
        <span>
          <BrainCircuit size={19} />
        </span>
        <div>
          <b>Start with a defensible comparison.</b>
          <p>
            Current API rates change frequently. Confirm the live provider pricing and measure
            response quality before choosing a production default.
          </p>
        </div>
        <span className="callout-status">
          <i />
          RESEARCH IN PROGRESS
        </span>
      </div>
      <div className="research-tabs">
        {[
          ["comparison", "Model comparison"],
          ["benchmarks", "Benchmark plan"],
          ["optimization", "Cost optimization"],
        ].map(([key, label]) => (
          <button
            key={key}
            className={activeTab === key ? "research-tab active" : "research-tab"}
            onClick={() => setActiveTab(key)}
          >
            {label}
          </button>
        ))}
      </div>
      {activeTab === "comparison" && (
        <>
          <section className="model-recommendation">
            <div className="recommendation-icon">
              <Lightbulb size={18} />
            </div>
            <div>
              <span>INITIAL RECOMMENDATION</span>
              <h2>Evaluate Gemini 2.5 Flash first</h2>
              <p>
                Its native schema mode and focused extraction use case make it a sensible candidate;
                this is a research hypothesis, not a measured winner.
              </p>
            </div>
            <StatusPill tone="neutral">Not benchmarked</StatusPill>
          </section>
          <section className="model-list">
            {modelProviders.map((model) => {
              const isConfigured = getProviderConfigured(model.name);
              return (
                <article key={model.name} className="model-card">
                  <button
                    className="model-card-head"
                    onClick={() => toggle(model.name)}
                    aria-expanded={expanded.includes(model.name)}
                  >
                    <span className={`provider-emblem ${model.color}`}>
                      {model.name === "OpenAI" ? (
                        <Activity size={17} />
                      ) : model.name === "Google Gemini" ? (
                        <Sparkles size={17} />
                      ) : (
                        <BrainCircuit size={17} />
                      )}
                    </span>
                    <span className="provider-name">
                      <b>{model.name}</b>
                      <small>{model.model}</small>
                    </span>
                    {isConfigured !== null && (
                      <span className="model-json-badge" style={{ marginRight: "0.5rem" }}>
                        {isConfigured ? (
                          <span
                            style={{
                              color: "#059669",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.25rem",
                            }}
                          >
                            <Check size={12} /> Active
                          </span>
                        ) : (
                          <span
                            style={{
                              color: "#9ca3af",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.25rem",
                            }}
                          >
                            Unconfigured
                          </span>
                        )}
                      </span>
                    )}
                    <span className="model-price-summary">
                      {model.input}
                      <small>Input rate</small>
                    </span>
                    <span className="model-json-badge">
                      <Code2 size={13} />
                      {model.structured}
                    </span>
                    <ChevronDown
                      className={
                        expanded.includes(model.name) ? "model-chevron expanded" : "model-chevron"
                      }
                      size={16}
                    />
                  </button>
                  {expanded.includes(model.name) && (
                    <div className="model-details">
                      <p>{model.description}</p>
                      <div className="model-facts">
                        <div>
                          <span>INPUT / 1M TOKENS</span>
                          <b>{model.input}</b>
                        </div>
                        <div>
                          <span>OUTPUT / 1M TOKENS</span>
                          <b>{model.output}</b>
                        </div>
                        <div>
                          <span>CONTEXT WINDOW</span>
                          <b>{model.context}</b>
                        </div>
                        <div>
                          <span>ACTUAL SPEED</span>
                          <b>{model.speed}</b>
                        </div>
                        <div>
                          <span>STRUCTURED OUTPUT</span>
                          <b>{model.structured}</b>
                        </div>
                        <div>
                          <span>APPLICATION FIT</span>
                          <b>{model.suitability}</b>
                        </div>
                      </div>
                      <div className="model-source-links">
                        <a href={model.pricing} target="_blank" rel="noreferrer">
                          Official pricing <ExternalLink size={12} />
                        </a>
                        <a href={model.structuredUrl} target="_blank" rel="noreferrer">
                          Structured output docs <ExternalLink size={12} />
                        </a>
                      </div>
                    </div>
                  )}
                </article>
              );
            })}
          </section>
          <p className="model-footnote">
            † Context windows and model availability must be checked in the provider’s current
            documentation for your account, API version, and model identifier. ‡ Provider response
            formats differ; run the same schema validation suite. Pricing values are intentionally
            linked to authoritative live sources rather than hardcoded as stale facts.
          </p>
        </>
      )}
      {activeTab === "benchmarks" && <BenchmarkPlan />}
      {activeTab === "optimization" && <OptimizationPlan />}
    </AppShell>
  );
}

function BenchmarkPlan() {
  const preferences = readPreferences();
  const [targetUrl, setTargetUrl] = useState("https://acmecloud.example");
  const [mockMode, setMockMode] = useState(false);
  const [benchmarkMode, setBenchmarkMode] = useState<"synthetic" | "live">("synthetic");
  const [isRunning, setIsRunning] = useState(false);
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkRunResponse | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const handleRun = async () => {
    setIsRunning(true);
    setRunError(null);
    try {
      const res = await runModelBenchmark(preferences.apiBaseUrl, {
        url: targetUrl.trim(),
        mock_mode: mockMode,
        benchmark_mode: benchmarkMode,
        providers: ["gemini", "openai", "anthropic"],
      });
      setBenchmarkResult(res);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsRunning(false);
    }
  };

  const cases = [
    "SaaS / software",
    "Professional services",
    "Local business",
    "Retail / ecommerce",
    "Content-light website",
  ];

  return (
    <>
      <section className="benchmark-runner-panel">
        <div className="benchmark-runner-header">
          <h3>
            <Activity size={18} />
            Live Multi-Model Benchmark Runner
          </h3>
          <StatusPill tone={isRunning ? "warning" : benchmarkResult ? "positive" : "neutral"}>
            {isRunning
              ? "Benchmarking..."
              : benchmarkResult
                ? "Benchmark Complete"
                : "Ready to Test"}
          </StatusPill>
        </div>

        <div className="benchmark-runner-controls">
          <div className="benchmark-input-row">
            <input
              type="text"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              placeholder="Enter website URL to benchmark (e.g. https://acmecloud.example)"
              className="benchmark-url-input"
              disabled={isRunning}
            />
            <Button onClick={handleRun} disabled={isRunning || !targetUrl.trim()} className="gap-2">
              {isRunning ? (
                <>
                  <LoaderCircle size={15} className="animate-spin" />
                  Running Models...
                </>
              ) : (
                <>
                  <Sparkles size={15} />
                  Run Live Benchmark
                </>
              )}
            </Button>
          </div>

          <div className="benchmark-presets">
            <span>Quick datasets:</span>
            <button
              type="button"
              className="benchmark-preset-btn"
              onClick={() => setTargetUrl("https://acmecloud.example")}
            >
              Standard Acme Cloud (Benchmark)
            </button>
            <button
              type="button"
              className="benchmark-preset-btn"
              onClick={() => setTargetUrl("https://www.hubspot.com")}
            >
              HubSpot (Enterprise SaaS)
            </button>
            <button
              type="button"
              className="benchmark-preset-btn"
              onClick={() => setTargetUrl("https://stripe.com")}
            >
              Stripe (Fintech Infrastructure)
            </button>
          </div>

          <div className="benchmark-provider-options flex flex-wrap gap-4 items-center">
            <label className="benchmark-option-label">
              <input
                type="checkbox"
                checked={mockMode}
                onChange={(e) => setMockMode(e.target.checked)}
              />
              <span>Mock / Simulation mode (Compare all 3 without consuming live API credits)</span>
            </label>
            <label className="benchmark-option-label">
              <input
                type="checkbox"
                checked={benchmarkMode === "synthetic"}
                onChange={(e) => setBenchmarkMode(e.target.checked ? "synthetic" : "live")}
              />
              <span>Standard synthetic dataset (deterministic benchmark)</span>
            </label>
          </div>
        </div>

        {runError && (
          <div className="mt-4 p-3 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2">
            <CircleAlert size={16} />
            <span>{runError}</span>
          </div>
        )}
      </section>

      {benchmarkResult && (
        <>
          <div className="benchmark-winner-banner">
            <div className="benchmark-winner-icon">
              <Sparkles size={22} />
            </div>
            <div className="benchmark-winner-text">
              <div className="flex items-center gap-2">
                <h4>Benchmark Winner: {benchmarkResult.recommended_winner}</h4>
                {benchmarkResult.is_simulated && <StatusPill tone="neutral">SIMULATED</StatusPill>}
              </div>
              <p>{benchmarkResult.recommendation_rationale}</p>
            </div>
          </div>

          {(benchmarkResult.fastest_model ||
            benchmarkResult.cheapest_model ||
            benchmarkResult.highest_quality_model) && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 my-4">
              {benchmarkResult.fastest_model && (
                <div className="p-3 bg-muted/40 rounded-lg border border-border/50 text-xs">
                  <span className="text-muted-foreground block font-medium mb-1">
                    ⚡ FASTEST MODEL
                  </span>
                  <span className="font-semibold text-foreground text-sm">
                    {benchmarkResult.fastest_model}
                  </span>
                </div>
              )}
              {benchmarkResult.cheapest_model && (
                <div className="p-3 bg-muted/40 rounded-lg border border-border/50 text-xs">
                  <span className="text-muted-foreground block font-medium mb-1">
                    💰 MOST ECONOMICAL
                  </span>
                  <span className="font-semibold text-foreground text-sm">
                    {benchmarkResult.cheapest_model}
                  </span>
                </div>
              )}
              {benchmarkResult.highest_quality_model && (
                <div className="p-3 bg-muted/40 rounded-lg border border-border/50 text-xs">
                  <span className="text-muted-foreground block font-medium mb-1">
                    🏆 HIGHEST QUALITY
                  </span>
                  <span className="font-semibold text-foreground text-sm">
                    {benchmarkResult.highest_quality_model}
                  </span>
                </div>
              )}
            </div>
          )}

          <div className="benchmark-grid">
            {benchmarkResult.results.map((res) => {
              const isWinner = res.model === benchmarkResult.recommended_winner;
              return (
                <div
                  key={res.provider}
                  className={`benchmark-model-card ${isWinner ? "is-winner" : ""}`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <b className="text-sm font-semibold block capitalize">{res.provider}</b>
                        {res.simulated && (
                          <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                            Simulated
                          </span>
                        )}
                      </div>
                      <small className="text-xs text-muted-foreground">{res.model}</small>
                    </div>
                    <StatusPill
                      tone={
                        res.status === "success"
                          ? "positive"
                          : res.status === "unconfigured"
                            ? "neutral"
                            : "critical"
                      }
                    >
                      {res.status === "success"
                        ? "Evaluated"
                        : res.status === "unconfigured"
                          ? "Unconfigured"
                          : "Error"}
                    </StatusPill>
                  </div>

                  {res.status === "unconfigured" ? (
                    <div className="py-4 text-xs text-muted-foreground text-center bg-muted/40 rounded p-3">
                      Provider credentials missing in backend <code>.env</code>. Configure{" "}
                      <code>{res.provider.toUpperCase()}_API_KEY</code> to enable live benchmarking,
                      or enable mock mode above.
                    </div>
                  ) : res.status === "error" ? (
                    <div className="py-2 text-xs text-destructive bg-destructive/10 rounded p-2">
                      {res.error_message || "Benchmark failed"}
                    </div>
                  ) : (
                    <>
                      <div className="benchmark-stat-row">
                        <span className="benchmark-stat-label">Response Latency</span>
                        <span className="benchmark-stat-value">{res.latency_ms} ms</span>
                      </div>
                      <div className="benchmark-stat-row">
                        <span className="benchmark-stat-label">Token Usage</span>
                        <span className="benchmark-stat-value">
                          {res.input_tokens != null ? res.input_tokens.toLocaleString() : "N/A"} in
                          / {res.output_tokens != null ? res.output_tokens.toLocaleString() : "N/A"}{" "}
                          out
                        </span>
                      </div>
                      <div className="benchmark-stat-row">
                        <span className="benchmark-stat-label">Cost per Run</span>
                        <span className="benchmark-stat-value">
                          {res.estimated_cost_usd != null
                            ? `$${res.estimated_cost_usd.toFixed(6)}`
                            : "N/A"}
                        </span>
                      </div>
                      <div className="benchmark-stat-row">
                        <span className="benchmark-stat-label">Cost per 1,000 Runs</span>
                        <span className="benchmark-stat-value">
                          {res.cost_per_thousand_analyses_usd != null
                            ? `$${res.cost_per_thousand_analyses_usd.toFixed(4)}`
                            : "N/A"}
                        </span>
                      </div>
                      <div className="benchmark-stat-row">
                        <span className="benchmark-stat-label">Schema Validity</span>
                        <span className="benchmark-stat-value text-emerald-600 dark:text-emerald-400">
                          {res.schema_valid ? "100% Valid" : "Invalid"}
                        </span>
                      </div>
                      <div className="benchmark-stat-row">
                        <span className="benchmark-stat-label">Completeness</span>
                        <span className="benchmark-stat-value">{res.completeness_score}%</span>
                      </div>
                      <div className="benchmark-stat-row">
                        <span className="benchmark-stat-label">Quality Score</span>
                        <span className="benchmark-stat-value">{res.quality_score}%</span>
                      </div>

                      <div className="dimension-bar-container">
                        <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Dimension Completeness
                        </span>
                        <div className="dimension-bar-item">
                          <span>Competitors</span>
                          <div className="dimension-progress">
                            <div
                              className="dimension-fill"
                              style={{ width: `${res.dimension_scores.competitors}%` }}
                            />
                          </div>
                          <b>{res.dimension_scores.competitors}%</b>
                        </div>
                        <div className="dimension-bar-item">
                          <span>Search Queries</span>
                          <div className="dimension-progress">
                            <div
                              className="dimension-fill"
                              style={{ width: `${res.dimension_scores.search_queries}%` }}
                            />
                          </div>
                          <b>{res.dimension_scores.search_queries}%</b>
                        </div>
                        <div className="dimension-bar-item">
                          <span>SEO Signals</span>
                          <div className="dimension-progress">
                            <div
                              className="dimension-fill"
                              style={{ width: `${res.dimension_scores.seo}%` }}
                            />
                          </div>
                          <b>{res.dimension_scores.seo}%</b>
                        </div>
                        <div className="dimension-bar-item">
                          <span>Services</span>
                          <div className="dimension-progress">
                            <div
                              className="dimension-fill"
                              style={{ width: `${res.dimension_scores.services}%` }}
                            />
                          </div>
                          <b>{res.dimension_scores.services}%</b>
                        </div>
                        <div className="dimension-bar-item">
                          <span>Audience</span>
                          <div className="dimension-progress">
                            <div
                              className="dimension-fill"
                              style={{ width: `${res.dimension_scores.target_audience}%` }}
                            />
                          </div>
                          <b>{res.dimension_scores.target_audience}%</b>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}

      <div className="benchmark-table-wrap">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <BookOpen size={15} />
          Benchmark Evaluation Rubric & Measurement Standards
        </h4>
        <table className="data-table benchmark-table">
          <thead>
            <tr>
              <th>TEST DIMENSION</th>
              <th>HOW TO MEASURE</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {[
              ["Dataset", "A small, labelled set of publicly accessible websites by category."],
              [
                "Input / output tokens",
                "Capture provider-reported usage for each successful analysis.",
              ],
              ["Latency", "Measure request time from API dispatch through validated response."],
              ["Schema validity", "Count responses passing strict Pydantic validation."],
              [
                "Extraction accuracy",
                "Compare brand, title, services and metadata against manual labels.",
              ],
              [
                "Relevance",
                "Have reviewers score query and recommendation relevance against a rubric.",
              ],
              ["Actual cost", "Calculate from captured token usage and current published rates."],
            ].map(([name, how]) => (
              <tr key={name}>
                <td>
                  <b>{name}</b>
                </td>
                <td>{how}</td>
                <td>
                  <StatusPill tone={benchmarkResult ? "positive" : "neutral"}>
                    {benchmarkResult ? "Benchmarked" : "Ready"}
                  </StatusPill>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="dataset-categories">
        <span>WEBSITE CATEGORIES TO INCLUDE</span>
        {cases.map((item) => (
          <b key={item}>{item}</b>
        ))}
      </div>
    </>
  );
}

function OptimizationPlan() {
  const optimizations = [
    [
      "Clean before prompting",
      "Remove scripts, navigation, repeated footer copy and boilerplate before the model sees the page.",
    ],
    [
      "Limit pages and context",
      "Inspect the home page plus a small, configurable set of service and about pages.",
    ],
    [
      "Deduplicate content",
      "Remove repeated blocks and avoid sending identical copy from multiple pages.",
    ],
    [
      "Cache careful stages",
      "Cache extraction by URL and content hash; expire entries and never cache failures as reports.",
    ],
    [
      "Route to the right model",
      "Benchmark a smaller model first; escalate only when extraction quality requires it.",
    ],
    [
      "Record real usage",
      "Capture provider-reported token counts and cost separately from rough pre-call estimates.",
    ],
  ];
  return (
    <>
      <div className="optimization-header">
        <div className="optimization-icon">
          <Gauge size={20} />
        </div>
        <div>
          <h2>Make every request count.</h2>
          <p>Lower cost without reducing the evidence available to the model.</p>
        </div>
      </div>
      <div className="optimization-list">
        {optimizations.map(([title, description], index) => (
          <article key={title}>
            <span>0{index + 1}</span>
            <div>
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
            <Check size={16} />
          </article>
        ))}
      </div>
      <p className="model-footnote">
        Estimated cost per analysis should be calculated only after measured token counts and
        current provider rates are available. This app reports no fabricated benchmark or cost
        figures.
      </p>
    </>
  );
}

export function SettingsPage() {
  const [preferences, setPreferences] = usePreferences();
  const [apiUrl, setApiUrl] = useState(preferences.apiBaseUrl);
  const [workspace, setWorkspace] = useState(() => getActiveWorkspace());
  const [wsSaved, setWsSaved] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testing, setTesting] = useState(false);
  const [healthStatus, setHealthStatus] = useState<ApiHealthStatus | null>(null);
  const [connection, setConnection] = useState<"unknown" | "connected" | "degraded" | "failed">(
    "unknown",
  );
  const [copied, setCopied] = useState(false);
  const saveUrl = () => {
    const value = apiUrl.trim().replace(/\/+$/, "");
    if (!/^https?:\/\//.test(value)) {
      setConnection("failed");
      return;
    }
    setPreferences({ ...preferences, apiBaseUrl: value });
    setApiUrl(value);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1700);
  };
  const saveWorkspace = () => {
    setActiveWorkspace(workspace);
    setWsSaved(true);
    window.setTimeout(() => setWsSaved(false), 1700);
  };
  const testConnection = async () => {
    setTesting(true);
    const result = await checkApiHealthDetailed(apiUrl.trim().replace(/\/+$/, ""));
    setHealthStatus(result);
    if (!result.reachable) {
      setConnection("failed");
    } else if (!result.providerKeyConfigured) {
      setConnection("degraded");
    } else {
      setConnection("connected");
    }
    setTesting(false);
  };
  return (
    <AppShell title="Settings">
      <PageHeader
        eyebrow="WORKSPACE PREFERENCES"
        title="Settings"
        description="Configure how LinkIntel AI reaches its analysis service."
      />
      <div className="settings-layout">
        <div className="settings-main-column">
          <section className="settings-panel">
            <div className="settings-panel-heading">
              <span className="settings-panel-icon">
                <Activity size={18} />
              </span>
              <div>
                <h2>Analysis mode</h2>
                <p>Choose between a clearly labelled example and your live Python API.</p>
              </div>
            </div>
            <div className="settings-mode-options">
              <button
                className={
                  preferences.mode === "demo" ? "settings-mode-card selected" : "settings-mode-card"
                }
                onClick={() => {
                  setPreferences({ ...preferences, mode: "demo" });
                  setConnection("unknown");
                }}
              >
                <span className="settings-radio" />{" "}
                <span className="settings-mode-icon sample-mode-icon">
                  <Sparkles size={17} />
                </span>
                <span>
                  <b>Sample mode</b>
                  <small>Explore an illustrative report without an API connection.</small>
                </span>
                {preferences.mode === "demo" && <StatusPill tone="sample">ACTIVE</StatusPill>}
              </button>
              <button
                className={
                  preferences.mode === "live" ? "settings-mode-card selected" : "settings-mode-card"
                }
                onClick={() => {
                  setPreferences({ ...preferences, mode: "live" });
                  setConnection("unknown");
                }}
              >
                <span className="settings-radio" />
                <span className="settings-mode-icon live-mode-icon">
                  <Globe2 size={17} />
                </span>
                <span>
                  <b>Live API</b>
                  <small>Send website analysis requests to your configured FastAPI service.</small>
                </span>
                {preferences.mode === "live" && <StatusPill tone="success">ACTIVE</StatusPill>}
              </button>
            </div>
            <div className="settings-inline-notice">
              <CircleAlert size={15} />
              <span>
                Live mode never falls back to sample data. Connection or analysis errors are shown
                directly.
              </span>
            </div>
          </section>
          <section className="settings-panel">
            <div className="settings-panel-heading">
              <span className="settings-panel-icon settings-icon-green">
                <Globe2 size={18} />
              </span>
              <div>
                <h2>Python API connection</h2>
                <p>
                  Base URL for the FastAPI service; analysis uses <code>POST /link-analysis</code>.
                </p>
              </div>
            </div>
            <label className="settings-field-label" htmlFor="api-base-url">
              API base URL
            </label>
            <div className="settings-api-row">
              <input
                id="api-base-url"
                value={apiUrl}
                onChange={(event) => {
                  setApiUrl(event.target.value);
                  setConnection("unknown");
                  setHealthStatus(null);
                }}
                placeholder={DEFAULT_API_BASE_URL}
              />
              <Button variant="outline" onClick={() => void testConnection()} disabled={testing}>
                {testing ? <LoaderCircle size={15} className="spin" /> : <Activity size={15} />}Test
                connection
              </Button>
            </div>
            <p className="settings-field-help">
              Set <code>VITE_API_BASE_URL</code> before starting the frontend, or update this value
              for this browser.
            </p>
            <div className="settings-save-row">
              <span className={`connection-result connection-${connection}`}>
                {connection === "connected" ? (
                  <>
                    <CircleCheck size={14} />
                    Backend online &amp; AI provider ready
                  </>
                ) : connection === "degraded" ? (
                  <>
                    <CircleAlert size={14} />
                    Backend online, but AI provider key is not configured in backend/.env
                  </>
                ) : connection === "failed" ? (
                  <>
                    <CircleAlert size={14} />
                    {healthStatus?.errorMessage || "Could not reach this API address"}
                  </>
                ) : (
                  <>
                    <span className="online-dot" />
                    {preferences.mode === "demo"
                      ? "API connection not required in sample mode"
                      : "Connection not checked"}
                  </>
                )}
              </span>
              <Button onClick={saveUrl}>
                {saved ? (
                  <>
                    <Check size={15} />
                    Saved
                  </>
                ) : (
                  "Save API address"
                )}
              </Button>
            </div>

            {healthStatus?.reachable && (
              <div className="backend-status-card">
                <div className="status-row">
                  <span>Backend service:</span>
                  <span className="status-val">
                    {healthStatus.service || "linkintel-backend"} v{healthStatus.version || "1.0.0"}
                  </span>
                </div>
                <div className="status-row">
                  <span>AI Provider:</span>
                  <span className="status-val">
                    {healthStatus.provider || "gemini"} ({healthStatus.model || "gemini-2.5-flash"})
                  </span>
                </div>
                <div className="status-row">
                  <span>Provider API Key:</span>
                  <span
                    className="status-val"
                    style={{ color: healthStatus.providerKeyConfigured ? "#059669" : "#d97706" }}
                  >
                    {healthStatus.providerKeyConfigured
                      ? "Detected & Configured"
                      : "Missing from backend .env"}
                  </span>
                </div>
                <div className="status-row">
                  <span>Live Search Discovery:</span>
                  <span className="status-val">
                    {healthStatus.searchProviderConfigured
                      ? "DuckDuckGo / Live Search Active"
                      : "Aggregator Filter Active"}
                  </span>
                </div>
              </div>
            )}
          </section>
          <section className="settings-panel">
            <div className="settings-panel-heading">
              <span className="settings-panel-icon settings-icon-blue">
                <BarChart3 size={18} />
              </span>
              <div>
                <h2>Workspace & Multi-Tenancy</h2>
                <p>Isolate reports and benchmark history by workspace identifier.</p>
              </div>
            </div>
            <label className="settings-field-label" htmlFor="workspace-id">
              Active Workspace Identifier
            </label>
            <div className="settings-api-row">
              <input
                id="workspace-id"
                value={workspace}
                onChange={(e) => setWorkspace(e.target.value)}
                placeholder="default"
              />
              <Button onClick={saveWorkspace}>
                {wsSaved ? (
                  <>
                    <Check size={15} />
                    Saved
                  </>
                ) : (
                  "Switch Workspace"
                )}
              </Button>
            </div>
            <p className="settings-field-help">
              Outbound analysis and report queries include{" "}
              <code>X-Workspace-Id: {workspace || "default"}</code> to isolate records in the
              persistent database.
            </p>
          </section>
          <section className="settings-panel">
            <div className="settings-panel-heading">
              <span className="settings-panel-icon settings-icon-purple">
                <Code2 size={18} />
              </span>
              <div>
                <h2>API quick start</h2>
                <p>Run the Python service locally, then enable live mode above.</p>
              </div>
            </div>
            <div className="command-snippet">
              <code>
                cd backend &amp;&amp; uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
              </code>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Copy API command"
                onClick={() => {
                  void navigator.clipboard.writeText(
                    "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload",
                  );
                  setCopied(true);
                  window.setTimeout(() => setCopied(false), 1500);
                }}
              >
                {copied ? <Check size={15} /> : <Copy size={15} />}
              </Button>
            </div>
            <div className="settings-link-row">
              <span>
                <span className="online-dot" />
                Local API documentation
              </span>
              <a href={`${apiUrl || DEFAULT_API_BASE_URL}/docs`} target="_blank" rel="noreferrer">
                Open /docs <ExternalLink size={13} />
              </a>
            </div>
          </section>
        </div>
        <aside className="settings-aside">
          <div className="settings-about">
            <BrandMark />
            <h3>LinkIntel AI</h3>
            <p>Website intelligence, made actionable.</p>
            <div className="version-label">
              APPLICATION VERSION <b>1.0.0</b>
            </div>
          </div>
          <div className="settings-security">
            <ShieldCheck size={17} />
            <h3>Your keys stay server-side</h3>
            <p>
              Provider credentials belong in the Python backend environment. This browser never asks
              for or stores an LLM key.
            </p>
          </div>
          <div className="settings-links">
            <p>REFERENCE</p>
            <Link to="/model-lab">
              <BookOpen size={15} />
              Model research lab <ArrowRight size={13} />
            </Link>
            <a href="http://localhost:4000/docs" target="_blank" rel="noreferrer">
              <Code2 size={15} />
              FastAPI documentation <ExternalLink size={12} />
            </a>
          </div>
        </aside>
      </div>
    </AppShell>
  );
}
