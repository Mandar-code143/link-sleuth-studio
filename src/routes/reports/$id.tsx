import { createFileRoute } from "@tanstack/react-router";
import { WorkstationShell } from "@/components/layout/WorkstationShell";
import { ReportPage } from "@/components/pages/ReportPage";

export const Route = createFileRoute("/reports/$id")({
  component: () => (
    <WorkstationShell activeRoute="reports" breadcrumb="Analysis Report">
      <ReportPage />
    </WorkstationShell>
  ),
});
