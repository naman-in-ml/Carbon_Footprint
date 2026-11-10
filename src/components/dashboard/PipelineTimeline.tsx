import { Check } from "lucide-react";
import { Card } from "@/components/ui/Card";
import type { Claim, Score, Verification } from "@/types";

export function PipelineTimeline({
  claim,
  verification,
  score,
}: {
  claim: Claim;
  verification: Verification;
  score: Score;
}) {
  const extraction =
    claim.geocoding_method === "doc"
      ? "Coordinates read from document"
      : claim.geocoding_method === "nominatim"
        ? "Location geocoded"
        : claim.geocoding_method === "boundary"
          ? "Uploaded boundary"
          : "Claims extracted";
  const steps = [
    { label: "Claims extracted", detail: extraction, done: true },
    {
      label: "Area measured",
      detail: "Satellite tree-cover area",
      done: verification.tree_cover_ha != null,
    },
    {
      label: "Planting verified",
      detail: "NDVI versus control",
      done: !!verification.planting_verified,
    },
    {
      label: "Permanence checked",
      detail: "Fire and forest loss",
      done: !!verification.still_standing,
    },
    { label: "Scored", detail: `${score.composite_score.toFixed(0)} / 100`, done: true },
  ];
  return (
    <Card title="Verification pipeline">
      <ol className="space-y-5">
        {steps.map((step) => (
          <li key={step.label} className="flex gap-3">
            <span
              className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border ${step.done ? "border-accent bg-accent/15 text-accent" : "border-line text-muted"}`}
            >
              {step.done && <Check className="h-3.5 w-3.5" />}
            </span>
            <div>
              <p className="text-sm font-medium">{step.label}</p>
              <p className="text-xs text-muted">{step.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </Card>
  );
}
