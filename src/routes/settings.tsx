import { createFileRoute } from "@tanstack/react-router";
import { SettingsPage } from "@/components/linkintel-app";

export const Route = createFileRoute("/settings")({
  component: SettingsPage,
});
