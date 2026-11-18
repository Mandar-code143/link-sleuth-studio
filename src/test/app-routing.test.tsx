import { QueryClient } from "@tanstack/react-query";
import { createRouter, rootRouteId } from "@tanstack/react-router";
import { describe, expect, it } from "vitest";

import { routeTree } from "@/routeTree.gen";
import {
  validateWebsiteUrl,
  DEMO_REPORT,
  saveReport,
  getReport,
  deleteReport,
  readHistory,
} from "@/lib/linkintel";

describe("App routing and integration", () => {
  const router = createRouter({ routeTree, context: { queryClient: new QueryClient() } });

  it("matches a page for / instead of falling back to not found", () => {
    const matches = router.matchRoutes("/");
    expect(matches.at(-1)?.routeId).not.toBe(rootRouteId);
    expect(matches.at(-1)?.routeId).toBe("/");
  });

  it("matches the /analyze route", () => {
    const matches = router.matchRoutes("/analyze");
    expect(matches.at(-1)?.routeId).toBe("/analyze");
  });

  it("matches the /history route", () => {
    const matches = router.matchRoutes("/history");
    expect(matches.at(-1)?.routeId).toBe("/history");
  });

  it("matches the /model-lab route", () => {
    const matches = router.matchRoutes("/model-lab");
    expect(matches.at(-1)?.routeId).toBe("/model-lab");
  });

  it("matches the /settings route", () => {
    const matches = router.matchRoutes("/settings");
    expect(matches.at(-1)?.routeId).toBe("/settings");
  });

  it("matches the /reports/$id route", () => {
    const matches = router.matchRoutes("/reports/sample-northstar-01");
    expect(matches.at(-1)?.routeId).toBe("/reports/$id");
  });
});

describe("URL Validator (Frontend Boundary)", () => {
  it("rejects empty URLs", () => {
    expect(validateWebsiteUrl("")).toBe("Enter a website address to continue.");
    expect(validateWebsiteUrl("   ")).toBe("Enter a website address to continue.");
  });

  it("requires http or https protocol", () => {
    expect(validateWebsiteUrl("ftp://example.com")).toBe(
      "Use a website address beginning with http:// or https://.",
    );
    expect(validateWebsiteUrl("file:///path/to/file")).toBe(
      "Use a website address beginning with http:// or https://.",
    );
  });

  it("requires a complete domain with dot extension", () => {
    expect(validateWebsiteUrl("http://localhost")).toBe(
      "Enter a complete domain, such as example.com.",
    );
    expect(validateWebsiteUrl("https://intranet")).toBe(
      "Enter a complete domain, such as example.com.",
    );
  });

  it("accepts valid public website URLs", () => {
    expect(validateWebsiteUrl("https://example.com")).toBeNull();
    expect(validateWebsiteUrl("http://acme.org/about")).toBeNull();
  });
});

describe("Demo Data Contract and Persistence", () => {
  it("DEMO_REPORT satisfies mandatory LinkAnalysis structure", () => {
    expect(DEMO_REPORT.success).toBe(true);
    expect(DEMO_REPORT.brand.name).toBeTruthy();
    expect(DEMO_REPORT.analysis.competitor_analysis).toBeDefined();
    expect(DEMO_REPORT.analysis.target_search_queries).toHaveLength(5);
    expect(DEMO_REPORT.analysis.seo_improvements).toBeDefined();
    expect(DEMO_REPORT.analysis.top_services.length).toBeGreaterThan(0);
    expect(DEMO_REPORT.analysis.target_audience).toBeDefined();
    expect(DEMO_REPORT.metadata.sample_data).toBe(true);
  });

  it("saves, retrieves, and deletes reports in local history", () => {
    const reportCopy = {
      ...DEMO_REPORT,
      metadata: {
        ...DEMO_REPORT.metadata,
        report_id: "test-report-vitest-123",
      },
    };

    const entry = saveReport(reportCopy);
    expect(entry.id).toBe("test-report-vitest-123");

    const retrieved = getReport("test-report-vitest-123");
    expect(retrieved).not.toBeNull();
    expect(retrieved?.metadata.report_id).toBe("test-report-vitest-123");

    deleteReport("test-report-vitest-123");
    expect(getReport("test-report-vitest-123")).toBeNull();
  });
});
