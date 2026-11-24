import { useState, useEffect, useMemo } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import {
  History,
  Search,
  Filter,
  Download,
  Plus,
  Trash2,
  ExternalLink,
  ChevronDown,
  Sparkles,
  ArrowRight,
  Database,
  CheckCircle2,
  Clock,
  Layers,
} from "lucide-react";
import { readHistory, deleteReport, type HistoryEntry } from "@/lib/linkintel";

export function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [modeFilter, setModeFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState<"newest" | "oldest" | "az">("newest");

  useEffect(() => {
    setHistory(readHistory());
  }, []);

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to remove this intelligence report?")) {
      deleteReport(id);
      setHistory(readHistory());
    }
  };

  const handleExportAll = () => {
    const data = {
      exported_at: new Date().toISOString(),
      reports: history,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `linkintel-history-archive.json`;
    a.click();
  };

  const filteredHistory = useMemo(() => {
    return history
      .filter((entry) => {
        const matchesSearch =
          entry.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
          entry.website.toLowerCase().includes(searchTerm.toLowerCase()) ||
          entry.category.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesStatus =
          statusFilter === "all" ||
          (statusFilter === "completed" && entry.status === "completed") ||
          (statusFilter === "failed" && entry.status === "failed");

        const matchesMode =
          modeFilter === "all" ||
          (modeFilter === "live" && !entry.sample) ||
          (modeFilter === "sample" && entry.sample);

        return matchesSearch && matchesStatus && matchesMode;
      })
      .sort((a, b) => {
        if (sortOrder === "newest") {
          return new Date(b.analyzedAt).getTime() - new Date(a.analyzedAt).getTime();
        }
        if (sortOrder === "oldest") {
          return new Date(a.analyzedAt).getTime() - new Date(b.analyzedAt).getTime();
        }
        if (sortOrder === "az") {
          return a.brand.localeCompare(b.brand);
        }
        return 0;
      });
  }, [history, searchTerm, statusFilter, modeFilter, sortOrder]);

  return (
    <div className="flex flex-col w-full max-w-[1680px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8 animate-fadeIn">
      {/* Header Section */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 bg-white p-6 sm:p-8 rounded-2xl border border-[#E5E7EF] shadow-xs">
        <div className="flex flex-col gap-2 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#2538D0]" />
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#2538D0]">
              AUDIT REPOSITORY • PERSONAL WORKSPACE
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold font-['Manrope',sans-serif] text-[#141B2C]">
            Your intelligence archive.
          </h1>
          <p className="text-xs sm:text-sm text-[#454655] leading-relaxed">
            Revisit websites you've previously analysed. Reports are stored locally in your browser
            workspace.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0 flex-wrap">
          <button
            type="button"
            onClick={handleExportAll}
            disabled={history.length === 0}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-[#F1F3FF] text-[#141B2C] hover:bg-[#E9EDFF] disabled:opacity-50 text-xs font-semibold border border-[#DFE0FF] transition-colors"
          >
            <Download size={15} className="text-[#757687]" />
            <span>Export All (JSON)</span>
          </button>
          <Link
            to="/analyze"
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-[#2538D0] hover:bg-[#1E31C0] text-white text-xs font-semibold shadow-xs transition-all active:scale-[0.99]"
          >
            <Plus size={15} />
            <span>New Analysis</span>
          </Link>
        </div>
      </div>

      {/* Search, Filter & Sort Toolbar */}
      <div className="bg-white rounded-2xl p-4 sm:p-5 border border-[#E5E7EF] shadow-xs flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
        <div className="relative flex-1 min-w-0">
          <Search
            size={16}
            className="text-[#757687] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
          />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by brand, domain, or industry..."
            className="w-full bg-[#F1F3FF] text-[#141B2C] placeholder:text-[#757687] rounded-xl pl-10 pr-4 py-2.5 text-xs outline-none focus:bg-white focus:border-[#2538D0] border border-[#DFE0FF] transition-colors"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#141B2C] text-xs font-medium rounded-xl px-3 py-2.5 outline-none border border-[#DFE0FF] cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="completed">5/5 Complete</option>
            <option value="failed">Failed</option>
          </select>

          {/* Mode filter */}
          <select
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            className="bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#141B2C] text-xs font-medium rounded-xl px-3 py-2.5 outline-none border border-[#DFE0FF] cursor-pointer"
          >
            <option value="all">All Modes</option>
            <option value="live">Live Verified</option>
            <option value="sample">Sample Data</option>
          </select>

          {/* Sort order */}
          <select
            value={sortOrder}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              setSortOrder(e.target.value as "newest" | "oldest" | "az")
            }
            className="bg-[#F1F3FF] hover:bg-[#E9EDFF] text-[#2538D0] font-semibold text-xs rounded-xl px-3 py-2.5 outline-none border border-[#DFE0FF] cursor-pointer"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="az">Brand A–Z</option>
          </select>
        </div>
      </div>

      {/* Intelligence Archive Table */}
      <div className="bg-white rounded-2xl border border-[#E5E7EF] shadow-xs overflow-hidden flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#F1F3FF] border-b border-[#DFE0FF]">
                <th className="py-3.5 px-5 font-bold uppercase tracking-wider text-[#757687]">
                  Brand &amp; Domain
                </th>
                <th className="py-3.5 px-4 font-bold uppercase tracking-wider text-[#757687]">
                  Industry / Category
                </th>
                <th className="py-3.5 px-4 font-bold uppercase tracking-wider text-[#757687]">
                  Analysis Date
                </th>
                <th className="py-3.5 px-4 font-bold uppercase tracking-wider text-[#757687]">
                  AI Model
                </th>
                <th className="py-3.5 px-4 font-bold uppercase tracking-wider text-[#757687]">
                  Status
                </th>
                <th className="py-3.5 px-4 font-bold uppercase tracking-wider text-[#757687]">
                  Mode
                </th>
                <th className="py-3.5 px-5 font-bold uppercase tracking-wider text-[#757687] text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F3FF]">
              {filteredHistory.length > 0 ? (
                filteredHistory.map((entry) => {
                  const initial = entry.brand?.charAt(0) || "W";
                  return (
                    <tr
                      key={entry.id}
                      onClick={() => navigate({ to: "/reports/$id", params: { id: entry.id } })}
                      className="hover:bg-[#F9F9FF] transition-colors cursor-pointer group"
                    >
                      <td className="py-4 px-5">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-[#DFE0FF] text-[#2538D0] flex items-center justify-center font-bold text-sm shrink-0">
                            {initial}
                          </div>
                          <div className="flex flex-col min-w-0">
                            <span className="font-bold text-sm text-[#141B2C] truncate">
                              {entry.brand}
                            </span>
                            <span className="font-mono text-xs text-[#757687] truncate max-w-xs">
                              {entry.website}
                            </span>
                          </div>
                        </div>
                      </td>

                      <td className="py-4 px-4 text-[#454655] font-medium">{entry.category}</td>

                      <td className="py-4 px-4 font-mono text-xs text-[#757687] whitespace-nowrap">
                        {new Date(entry.analyzedAt).toLocaleDateString()}{" "}
                        <span>
                          (
                          {new Date(entry.analyzedAt).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                          )
                        </span>
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#F1F3FF] text-[#2538D0] font-mono text-xs font-semibold">
                          <Sparkles size={12} />
                          <span>Gemini 2.5 Flash</span>
                        </span>
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#83F7D9]/40 text-[#005A4A] text-[11px] font-semibold">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#005A4A]" />
                          <span>5/5 Complete</span>
                        </span>
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap">
                        <span
                          className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                            entry.sample
                              ? "bg-[#F1F3FF] text-[#757687]"
                              : "bg-[#DFE0FF] text-[#000A64]"
                          }`}
                        >
                          {entry.sample ? "Sample Data" : "Live Verified"}
                        </span>
                      </td>

                      <td className="py-4 px-5 text-right whitespace-nowrap">
                        <div className="inline-flex items-center justify-end gap-1.5">
                          <Link
                            to="/reports/$id"
                            params={{ id: entry.id }}
                            onClick={(e) => e.stopPropagation()}
                            className="px-3 py-1.5 rounded-lg bg-[#F1F3FF] hover:bg-[#2538D0] hover:text-white text-[#2538D0] text-xs font-semibold transition-colors"
                          >
                            Open Report
                          </Link>
                          <button
                            type="button"
                            onClick={(e) => handleDelete(entry.id, e)}
                            className="p-1.5 rounded-lg text-[#757687] hover:text-[#BA1A1A] hover:bg-[#FFDAD6]/40 transition-colors"
                            title="Delete Artifact"
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-[#757687]">
                    <div className="flex flex-col items-center justify-center gap-3">
                      <div className="w-12 h-12 rounded-2xl bg-[#F1F3FF] flex items-center justify-center text-[#757687]">
                        <Database size={24} />
                      </div>
                      <div className="font-bold text-sm text-[#141B2C]">
                        {searchTerm
                          ? "No reports match your search query."
                          : "No analysis reports in archive yet."}
                      </div>
                      <p className="text-xs text-[#757687] max-w-sm">
                        Submit a business website from Overview or Analyze page to generate your
                        first structured report.
                      </p>
                      <Link
                        to="/analyze"
                        className="mt-2 px-4 py-2 rounded-xl bg-[#2538D0] text-white text-xs font-semibold shadow-xs hover:bg-[#1E31C0]"
                      >
                        Start New Analysis
                      </Link>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
