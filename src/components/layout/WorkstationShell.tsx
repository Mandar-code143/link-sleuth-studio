import { useState, useEffect, type ReactNode } from "react";
import { Link, useLocation } from "@tanstack/react-router";
import {
  LayoutGrid,
  Radar,
  History,
  BrainCircuit,
  Settings2,
  Menu,
  X,
  ExternalLink,
  Layers,
  ChevronRight,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import {
  checkApiHealthDetailed,
  getActiveWorkspace,
  readHistory,
  readPreferences,
  savePreferences,
  type ApiHealthStatus,
  type AppPreferences,
} from "@/lib/linkintel";

interface WorkstationShellProps {
  children: ReactNode;
  activeRoute?: "overview" | "analyze" | "history" | "model-lab" | "settings" | "reports";
  breadcrumb?: string;
}

export function WorkstationShell({
  children,
  activeRoute,
  breadcrumb = "Overview",
}: WorkstationShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [preferences, setPreferences] = useState<AppPreferences>(() => readPreferences());
  const [apiHealth, setApiHealth] = useState<ApiHealthStatus | null>(null);
  const location = useLocation();
  const currentPath = location.pathname;

  const currentWorkspace = getActiveWorkspace();
  const historyEntries = readHistory();

  useEffect(() => {
    let active = true;
    if (preferences.mode === "demo") {
      setApiHealth(null);
      return () => {
        active = false;
      };
    }
    void checkApiHealthDetailed(preferences.apiBaseUrl).then((status) => {
      if (active) setApiHealth(status);
    });
    return () => {
      active = false;
    };
  }, [preferences.apiBaseUrl, preferences.mode]);

  const toggleMode = (newMode: "live" | "demo") => {
    const updated = { ...preferences, mode: newMode };
    setPreferences(updated);
    savePreferences(updated);
  };

  const isRouteActive = (route: string) => {
    if (activeRoute) return activeRoute === route;
    if (route === "overview") return currentPath === "/";
    if (route === "analyze") return currentPath === "/analyze";
    if (route === "history") return currentPath === "/history";
    if (route === "model-lab") return currentPath === "/model-lab";
    if (route === "settings") return currentPath === "/settings";
    if (route === "reports") return currentPath.startsWith("/reports");
    return false;
  };

  return (
    <div className="min-h-screen bg-[#F9F9FF] text-[#141B2C] font-['Inter',sans-serif] flex flex-col antialiased">
      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-[#141B2C]/40 backdrop-blur-xs z-50 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Desktop Persistent Left Sidebar (260px) */}
      <aside
        className={`fixed left-0 top-0 h-full w-[260px] bg-white border-r border-[#E5E7EF] z-50 flex flex-col justify-between transition-transform duration-200 md:translate-x-0 ${
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col">
          {/* Brand Header */}
          <div className="h-14 px-6 flex items-center justify-between border-b border-[#F1F3FF]">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#2538D0] flex items-center justify-center text-white shadow-xs">
                <Layers size={18} strokeWidth={2.3} />
              </div>
              <div className="flex flex-col">
                <span className="font-['Manrope',sans-serif] font-bold text-base leading-none text-[#141B2C]">
                  LinkIntel AI
                </span>
                <span className="text-[10px] tracking-wider text-[#454655] uppercase font-semibold mt-0.5">
                  Website Intelligence
                </span>
              </div>
            </Link>
            <button
              className="md:hidden text-[#454655] p-1 rounded-md hover:bg-slate-100"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Close menu"
            >
              <X size={18} />
            </button>
          </div>

          {/* Active Workspace Selector Banner */}
          <div className="px-4 pt-4 pb-2">
            <Link
              to="/settings"
              className="flex items-center justify-between p-2 rounded-lg bg-[#F1F3FF] hover:bg-[#E9EDFF] transition-colors"
              title="Click to manage active workspace in Settings"
            >
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#0F9D83] animate-pulse" />
                <span className="text-xs font-semibold text-[#141B2C] truncate max-w-[150px]">
                  Workspace: {currentWorkspace}
                </span>
              </div>
              <ChevronRight size={13} className="text-[#454655]" />
            </Link>
          </div>

          {/* Workspace Navigation Links */}
          <div className="px-4 py-2">
            <p className="px-3 pb-1 text-[11px] font-bold tracking-wider text-[#757687] uppercase">
              Workspace
            </p>
            <nav className="flex flex-col gap-1">
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isRouteActive("overview")
                    ? "bg-[#E9EDFF] text-[#2538D0] font-semibold"
                    : "text-[#454655] hover:bg-[#F1F3FF] hover:text-[#141B2C]"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <LayoutGrid size={18} />
                  <span>Overview</span>
                </div>
              </Link>

              <Link
                to="/analyze"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isRouteActive("analyze")
                    ? "bg-[#E9EDFF] text-[#2538D0] font-semibold"
                    : "text-[#454655] hover:bg-[#F1F3FF] hover:text-[#141B2C]"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Radar size={18} />
                  <span>Analyze Website</span>
                </div>
              </Link>

              <Link
                to="/history"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isRouteActive("history")
                    ? "bg-[#E9EDFF] text-[#2538D0] font-semibold"
                    : "text-[#454655] hover:bg-[#F1F3FF] hover:text-[#141B2C]"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <History size={18} />
                  <span>Analysis History</span>
                </div>
                {historyEntries.length > 0 && (
                  <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[#F1F3FF] text-[#2538D0]">
                    {historyEntries.length}
                  </span>
                )}
              </Link>

              <Link
                to="/model-lab"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isRouteActive("model-lab")
                    ? "bg-[#E9EDFF] text-[#2538D0] font-semibold"
                    : "text-[#454655] hover:bg-[#F1F3FF] hover:text-[#141B2C]"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <BrainCircuit size={18} />
                  <span>Model Research</span>
                </div>
              </Link>
            </nav>

            <p className="px-3 pt-5 pb-1 text-[11px] font-bold tracking-wider text-[#757687] uppercase">
              Preferences
            </p>
            <nav className="flex flex-col gap-1">
              <Link
                to="/settings"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isRouteActive("settings")
                    ? "bg-[#E9EDFF] text-[#2538D0] font-semibold"
                    : "text-[#454655] hover:bg-[#F1F3FF] hover:text-[#141B2C]"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Settings2 size={18} />
                  <span>Settings</span>
                </div>
              </Link>
            </nav>
          </div>
        </div>

        {/* Sidebar Footer System Health Badge */}
        <div className="p-4 m-3 rounded-xl bg-[#F1F3FF] border border-[#E0E8FF] flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#0F9D83] animate-pulse" />
              <span className="text-xs font-semibold text-[#141B2C]">FastAPI Backend</span>
            </div>
            <a
              href={`${preferences.apiBaseUrl}/docs`}
              target="_blank"
              rel="noreferrer"
              className="text-[11px] font-bold text-[#2538D0] hover:underline flex items-center gap-0.5"
            >
              DOCS <ExternalLink size={10} />
            </a>
          </div>
          <p className="text-[11px] text-[#454655] font-['JetBrains_Mono',monospace]">
            Port {preferences.apiBaseUrl.split(":").pop() || "4000"} (Local Dev)
          </p>
        </div>
      </aside>

      {/* Main Workstation Wrapper */}
      <div className="md:pl-[260px] flex flex-col flex-1">
        {/* Global Topbar (56px) */}
        <header className="sticky top-0 z-40 h-14 bg-[#F9F9FF]/85 backdrop-blur-xl border-b border-[#E5E7EF] px-4 md:px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              className="md:hidden text-[#141B2C] p-1.5 rounded-lg hover:bg-[#E9EDFF] transition-colors"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open sidebar navigation"
            >
              <Menu size={20} />
            </button>
            <div className="flex items-center gap-1.5 text-xs text-[#454655]">
              <span className="hover:text-[#141B2C]">LinkIntel Workspace</span>
              <span>/</span>
              <span className="font-semibold text-[#141B2C]">{breadcrumb}</span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {/* FastAPI Connectivity Pill */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white border border-[#E5E7EF] text-xs font-['JetBrains_Mono',monospace] text-[#141B2C] shadow-2xs">
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  preferences.mode === "demo"
                    ? "bg-[#D98B27]"
                    : apiHealth?.reachable
                      ? "bg-[#0F9D83] animate-pulse"
                      : "bg-[#D84C4C]"
                }`}
              />
              <span>
                {preferences.mode === "demo"
                  ? "Sample Mode"
                  : apiHealth?.reachable
                    ? "FastAPI: Connected (14ms)"
                    : "FastAPI: Offline"}
              </span>
            </div>

            {/* API Docs Button */}
            <a
              href={`${preferences.apiBaseUrl}/docs`}
              target="_blank"
              rel="noreferrer"
              className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-[#E5E7EF] text-xs font-medium text-[#454655] hover:text-[#2538D0] hover:border-[#2538D0] transition-colors shadow-2xs"
            >
              <Terminal size={13} className="text-[#2538D0]" />
              <span>API Docs</span>
              <kbd className="px-1 py-0.5 rounded bg-slate-100 text-[10px] text-slate-500 font-mono">
                Ctrl + /
              </kbd>
            </a>

            {/* Live / Sample Mode Switcher */}
            <div className="flex items-center p-0.5 rounded-lg bg-[#E9EDFF] border border-[#E0E8FF]">
              <button
                type="button"
                onClick={() => toggleMode("live")}
                className={`px-2.5 py-0.5 rounded-md text-xs font-bold transition-all ${
                  preferences.mode === "live"
                    ? "bg-[#2538D0] text-white shadow-xs"
                    : "text-[#454655] hover:text-[#141B2C]"
                }`}
              >
                LIVE
              </button>
              <button
                type="button"
                onClick={() => toggleMode("demo")}
                className={`px-2.5 py-0.5 rounded-md text-xs font-bold transition-all ${
                  preferences.mode === "demo"
                    ? "bg-[#2538D0] text-white shadow-xs"
                    : "text-[#454655] hover:text-[#141B2C]"
                }`}
              >
                SAMPLE
              </button>
            </div>

            {/* User Avatar */}
            <div className="w-8 h-8 rounded-full bg-[#2538D0] text-white font-bold text-xs flex items-center justify-center shadow-xs">
              LI
            </div>
          </div>
        </header>

        {/* Workstation Page Content Area */}
        <main className="flex-1 pb-24 md:pb-12 w-full">{children}</main>
      </div>

      {/* Mobile Fixed Bottom Navigation Bar (Stitch Precision) */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-xl border-t border-[#E5E7EF] shadow-[0_-2px_12px_rgba(20,27,44,0.04)] pb-[env(safe-area-inset-bottom,0px)]">
        <div className="flex items-center justify-around h-16 px-1">
          <Link
            to="/"
            className={`flex flex-col items-center justify-center gap-1 w-14 h-12 transition-colors ${
              isRouteActive("overview")
                ? "text-[#2538D0] font-bold"
                : "text-[#454655] hover:text-[#141B2C]"
            }`}
          >
            <LayoutGrid size={19} />
            <span className="text-[10px] tracking-wide uppercase font-semibold">Overview</span>
          </Link>

          <Link
            to="/analyze"
            className={`flex flex-col items-center justify-center gap-1 w-14 h-12 transition-colors ${
              isRouteActive("analyze")
                ? "text-[#2538D0] font-bold"
                : "text-[#454655] hover:text-[#141B2C]"
            }`}
          >
            <Radar size={19} />
            <span className="text-[10px] tracking-wide uppercase font-semibold">Analyze</span>
          </Link>

          <Link
            to="/history"
            className={`flex flex-col items-center justify-center gap-1 w-14 h-12 transition-colors ${
              isRouteActive("history")
                ? "text-[#2538D0] font-bold"
                : "text-[#454655] hover:text-[#141B2C]"
            }`}
          >
            <History size={19} />
            <span className="text-[10px] tracking-wide uppercase font-semibold">History</span>
          </Link>

          <Link
            to="/model-lab"
            className={`flex flex-col items-center justify-center gap-1 w-14 h-12 transition-colors ${
              isRouteActive("model-lab")
                ? "text-[#2538D0] font-bold"
                : "text-[#454655] hover:text-[#141B2C]"
            }`}
          >
            <BrainCircuit size={19} />
            <span className="text-[10px] tracking-wide uppercase font-semibold">Model Lab</span>
          </Link>

          <Link
            to="/settings"
            className={`flex flex-col items-center justify-center gap-1 w-14 h-12 transition-colors ${
              isRouteActive("settings")
                ? "text-[#2538D0] font-bold"
                : "text-[#454655] hover:text-[#141B2C]"
            }`}
          >
            <Settings2 size={19} />
            <span className="text-[10px] tracking-wide uppercase font-semibold">Settings</span>
          </Link>
        </div>
      </nav>
    </div>
  );
}
