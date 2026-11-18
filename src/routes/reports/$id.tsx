import { createFileRoute } from "@tanstack/react-router";
import { ReportPage } from "@/components/linkintel-app";

export const Route = createFileRoute("/reports/$id")({
  component: ReportPage,
});
