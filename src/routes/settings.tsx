import { createFileRoute } from "@tanstack/react-router";
import { WorkstationShell } from "@/components/layout/WorkstationShell";
import { SettingsPage } from "@/components/pages/SettingsPage";

export const Route = createFileRoute("/settings")({
  component: () => (
    <WorkstationShell activeRoute="settings" breadcrumb="Settings">
      <SettingsPage />
    </WorkstationShell>
  ),
});
