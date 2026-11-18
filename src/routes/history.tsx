import { createFileRoute } from "@tanstack/react-router";
import { HistoryPage } from "@/components/linkintel-app";

export const Route = createFileRoute("/history")({
  component: HistoryPage,
});
