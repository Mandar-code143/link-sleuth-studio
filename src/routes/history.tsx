import { createFileRoute } from "@tanstack/react-router";
import { WorkstationShell } from "@/components/layout/WorkstationShell";
import { HistoryPage } from "@/components/pages/HistoryPage";

export const Route = createFileRoute("/history")({
  component: () => (
    <WorkstationShell activeRoute="history" breadcrumb="Analysis History">
      <HistoryPage />
    </WorkstationShell>
  ),
});
