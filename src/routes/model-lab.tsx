import { createFileRoute } from "@tanstack/react-router";
import { WorkstationShell } from "@/components/layout/WorkstationShell";
import { ModelLabPage } from "@/components/pages/ModelLabPage";

export const Route = createFileRoute("/model-lab")({
  component: () => (
    <WorkstationShell activeRoute="model-lab" breadcrumb="Model Research">
      <ModelLabPage />
    </WorkstationShell>
  ),
});
