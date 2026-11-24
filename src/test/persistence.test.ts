import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  getActiveWorkspace,
  setActiveWorkspace,
  fetchReportsList,
  fetchReportById,
  deleteReportById,
  fetchBenchmarksList,
  fetchBenchmarkById,
} from "@/lib/linkintel";

describe("Frontend Workspace and Persistence Client", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("handles active workspace storage and default fallback", () => {
    expect(getActiveWorkspace()).toBe("default");
    setActiveWorkspace("client-omega");
    expect(getActiveWorkspace()).toBe("client-omega");
    setActiveWorkspace("");
    expect(getActiveWorkspace()).toBe("default");
  });

  it("fetchReportsList sends workspace header and query params", async () => {
    setActiveWorkspace("team-finance");
    const mockResponse = {
      items: [
        {
          id: "rep_101",
          workspace_id: "team-finance",
          url: "https://finance.example",
          brand_name: "Finance Corp",
          category: "Finance",
          summary: "A fintech solution.",
          model_used: "gemini-2.5-flash",
          is_sample: false,
          tokens_used: 1000,
          cost_usd: 0.0002,
          created_at: "2026-11-24T12:00:00Z",
        },
      ],
      total: 1,
      workspace_id: "team-finance",
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response);

    const result = await fetchReportsList("http://localhost:4000", { q: "fintech" });

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://localhost:4000/reports?q=fintech",
      expect.objectContaining({
        headers: expect.objectContaining({
          "X-Workspace-Id": "team-finance",
        }),
      }),
    );
    expect(result.items).toHaveLength(1);
    expect(result.items[0].brand_name).toBe("Finance Corp");
  });

  it("fetchReportById loads single report", async () => {
    const mockReport = {
      success: true,
      website: "https://sample.example",
      brand: { name: "Sample Brand", category: "Tech", summary: "Summary" },
    };

    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockReport,
    } as Response);

    const report = await fetchReportById("http://localhost:4000", "rep_123", "custom-ws");
    expect(report.success).toBe(true);
    expect(report.brand.name).toBe("Sample Brand");
  });

  it("deleteReportById sends DELETE method with workspace header", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: "deleted", id: "rep_999" }),
    } as Response);

    const res = await deleteReportById("http://localhost:4000", "rep_999", "custom-ws");
    expect(res.status).toBe("deleted");
    expect(fetchSpy).toHaveBeenCalledWith(
      "http://localhost:4000/reports/rep_999",
      expect.objectContaining({
        method: "DELETE",
        headers: expect.objectContaining({
          "X-Workspace-Id": "custom-ws",
        }),
      }),
    );
  });

  it("fetchBenchmarksList and fetchBenchmarkById work properly", async () => {
    const mockBenchmarks = {
      items: [
        {
          id: "bmk_001",
          workspace_id: "default",
          target_url: "https://benchmark.example",
          benchmark_mode: "synthetic",
          is_simulated: true,
          winner_model: "gemini-2.5-flash",
          created_at: "2026-11-24T12:00:00Z",
        },
      ],
      total: 1,
      workspace_id: "default",
    };

    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBenchmarks,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          benchmark_id: "bmk_001",
          target_url: "https://benchmark.example",
          recommended_winner: "gemini-2.5-flash",
        }),
      } as Response);

    const list = await fetchBenchmarksList("http://localhost:4000");
    expect(list.total).toBe(1);
    expect(list.items[0].winner_model).toBe("gemini-2.5-flash");

    const detail = await fetchBenchmarkById("http://localhost:4000", "bmk_001");
    expect(detail.benchmark_id).toBe("bmk_001");
  });
});
