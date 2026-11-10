import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn, formatNumber } from "@/lib/utils";
import type { Claim, Verification } from "@/types";

type Status = "ok" | "high" | "critical" | "muted";
const STATUS = {
  ok: "text-risk-low",
  high: "text-risk-high",
  critical: "text-risk-critical",
  muted: "text-muted",
} as const;

function Evidence({
  title,
  claimed,
  measured,
  interpretation,
  source,
  status,
  children,
}: {
  title: string;
  claimed: string;
  measured: string;
  interpretation: string;
  source: string;
  status: Status;
  children?: React.ReactNode;
}) {
  const Icon = status === "ok" ? CheckCircle2 : AlertTriangle;
  return (
    <Card>
      <div className="flex items-center justify-between">
        <h3 className="font-medium">{title}</h3>
        <Icon className={cn("h-5 w-5", STATUS[status])} />
      </div>
      <div className="mt-5 grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-muted">Claimed</p>
          <p className="mt-1 font-mono text-lg">{claimed}</p>
        </div>
        <div>
          <p className="text-xs text-muted">Measured</p>
          <p className="mt-1 font-mono text-lg">{measured}</p>
        </div>
      </div>
      {children}
      <p className="mt-4 text-sm">{interpretation}</p>
      <p className="mt-2 text-xs text-muted">Source: {source}</p>
    </Card>
  );
}

export function EvidenceCards({
  claim,
  verification,
}: {
  claim: Claim;
  verification: Verification;
}) {
  const areaRatio =
    verification.tree_cover_ha != null && claim.claimed_hectares
      ? verification.tree_cover_ha / claim.claimed_hectares
      : null;
  const areaStatus: Status = areaRatio == null ? "muted" : areaRatio >= 0.5 ? "ok" : "critical";
  const plantingStatus: Status =
    verification.planting_verified === "yes"
      ? "ok"
      : verification.planting_verified === "partial"
        ? "high"
        : verification.planting_verified === "no"
          ? "critical"
          : "muted";
  const forestLoss = verification.forest_loss_ha ?? 0;
  const permanenceStatus: Status =
    verification.still_standing === "no"
      ? "critical"
      : verification.still_standing === "yes" &&
          (verification.fire_events_detected ?? 0) === 0 &&
          forestLoss < (verification.tree_cover_ha ?? Infinity) * 0.1
        ? "ok"
        : "high";
  const carbonStatus: Status =
    verification.credit_flag === "ok" || verification.credit_flag === "under_claimed"
      ? "ok"
      : verification.credit_flag === "major_discrepancy"
        ? "critical"
        : "high";
  const scale = Math.max(claim.claimed_tco2 ?? 0, verification.estimated_tco2_high ?? 0) * 1.1;
  const rangeLeft = scale ? ((verification.estimated_tco2_low ?? 0) / scale) * 100 : 0;
  const rangeWidth = scale
    ? (((verification.estimated_tco2_high ?? 0) - (verification.estimated_tco2_low ?? 0)) / scale) *
      100
    : 0;
  const claimLeft = scale ? ((claim.claimed_tco2 ?? 0) / scale) * 100 : 0;
  const markerClass =
    carbonStatus === "ok"
      ? "bg-risk-low"
      : carbonStatus === "high"
        ? "bg-risk-high"
        : carbonStatus === "critical"
          ? "bg-risk-critical"
          : "bg-muted";
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Evidence
        title="Area"
        claimed={`${formatNumber(claim.claimed_hectares)} ha`}
        measured={
          verification.tree_cover_ha == null
            ? "Not measured"
            : `${formatNumber(verification.tree_cover_ha)} ha tree cover`
        }
        interpretation={
          verification.aoi_ha != null
            ? `${formatNumber(verification.aoi_ha)} ha analysed.`
            : "Awaiting independent area measurement."
        }
        source="ESA WorldCover 2021 (10 m)"
        status={areaStatus}
      />
      <Evidence
        title="Planting"
        claimed={`Planted from ${claim.start_year ?? "—"}`}
        measured={`NDVI ${formatNumber(verification.ndvi_before, 2)} → ${formatNumber(verification.ndvi_after_3yr, 2)} (control ${formatNumber(verification.ndvi_control, 2)})`}
        interpretation={
          verification.planting_verified
            ? `Planting verification: ${verification.planting_verified}.`
            : "Planting not measured."
        }
        source="Sentinel-2 L2A NDVI vs control region"
        status={plantingStatus}
      />
      <Evidence
        title="Permanence"
        claimed="Permanent forest"
        measured={`${verification.still_standing ?? "—"}; ${verification.fire_events_detected ?? 0} fire days; ${formatNumber(verification.forest_loss_ha)} ha lost`}
        interpretation={
          verification.decline_detected_since
            ? `Decline detected since ${verification.decline_detected_since}.`
            : "No sustained decline detected."
        }
        source="NASA FIRMS + Hansen GFC v1.11"
        status={permanenceStatus}
      />
      <Evidence
        title="Carbon"
        claimed={`${formatNumber(claim.claimed_tco2)} tCO₂`}
        measured={`${formatNumber(verification.estimated_tco2)} (${formatNumber(verification.estimated_tco2_low)}–${formatNumber(verification.estimated_tco2_high)})`}
        interpretation={`Credit check: ${(verification.credit_flag ?? "not measured").replaceAll("_", " ")}.`}
        source="IPCC allometric screening (±50%)"
        status={carbonStatus}
      >
        <div className="relative mt-4 h-2 rounded-full bg-surface-2">
          <div
            className="absolute h-2 rounded-full bg-accent/30"
            style={{ left: `${rangeLeft}%`, width: `${rangeWidth}%` }}
          />
          <div
            className={cn("absolute -top-1 h-4 w-0.5", markerClass)}
            style={{ left: `${claimLeft}%` }}
          />
        </div>
      </Evidence>
    </div>
  );
}
