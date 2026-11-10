import { Card } from "@/components/ui/Card";
import { formatNumber } from "@/lib/utils";
import type { Claim } from "@/types";

export function ExtractionDetails({ claim }: { claim: Claim }) {
  const fields = [
    ["Species", claim.species ?? "—"],
    ["Methodology", claim.baseline_method ?? "—"],
    ["Monitoring period", claim.monitoring_period ?? "—"],
    ["Coordinates", claim.coordinates_raw ?? claim.geometry_wkt ?? "—"],
    [
      "Extraction confidence",
      claim.extraction_confidence != null
        ? `${formatNumber(claim.extraction_confidence * 100)}%`
        : "—",
    ],
  ];
  const flags = Object.entries(claim.uncertainty_flags ?? {});
  return (
    <Card title="Claim extraction details">
      <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {fields.map(([label, value]) => (
          <div key={label}>
            <dt className="text-xs text-muted">{label}</dt>
            <dd className="mt-1 text-sm">{value}</dd>
          </div>
        ))}
      </dl>
      {flags.length > 0 && (
        <div className="mt-6 border-t border-line pt-4">
          <p className="text-sm font-medium">Fields flagged for review</p>
          {flags.map(([key, reason]) => (
            <p key={key} className="mt-2 text-sm text-risk-medium">
              <span className="font-mono">{key}</span>: {reason}
            </p>
          ))}
        </div>
      )}
    </Card>
  );
}
