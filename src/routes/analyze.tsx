import { createFileRoute } from "@tanstack/react-router";
import { WorkstationShell } from "@/components/layout/WorkstationShell";
import { AnalyzePage } from "@/components/pages/AnalyzePage";

export const Route = createFileRoute("/analyze")({
  component: () => (
    <WorkstationShell activeRoute="analyze" breadcrumb="Analyze Website">
      <AnalyzePage />
    </WorkstationShell>
  ),
});
