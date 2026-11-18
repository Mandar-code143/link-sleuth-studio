import { createFileRoute } from "@tanstack/react-router";
import { ModelLabPage } from "@/components/linkintel-app";

export const Route = createFileRoute("/model-lab")({
  component: ModelLabPage,
});
