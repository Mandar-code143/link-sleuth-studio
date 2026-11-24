import { createFileRoute } from "@tanstack/react-router";
import { WorkstationShell } from "@/components/layout/WorkstationShell";
import { OverviewPage } from "@/components/pages/OverviewPage";

export const Route = createFileRoute("/")({
  component: () => (
    <WorkstationShell activeRoute="overview" breadcrumb="Overview">
      <OverviewPage />
    </WorkstationShell>
  ),
});
