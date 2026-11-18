import { createFileRoute } from "@tanstack/react-router";
import { AnalyzePage } from "@/components/linkintel-app";

export const Route = createFileRoute("/analyze")({
  component: AnalyzePage,
});
