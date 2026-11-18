import { createFileRoute } from "@tanstack/react-router";
import { DashboardPage } from "@/components/linkintel-app";

export const Route = createFileRoute("/")({
  component: DashboardPage,
});
