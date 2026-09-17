import { formatNumber } from "@/lib/utils";
import type { Claim, Verification } from "@/types";

const CREDIT_FLAG_LABEL: Record<string, string> = {
  ok: "Within screening band",
  under_claimed: "Under-claimed vs satellite",
  over_claimed: "Potentially over-claimed",
  major_discrepancy: "Major discrepancy",
};

export function ClaimVsSatellite({
  claim,
  verification,
}: {
  claim: Claim | null;
  verification: Verification | null;
}) {
  if (!claim || !verification) return null;

  const delta = verification.credit_delta_pct;
  const flag = verification.credit_flag ?? "ok";

  return (
    <div className="rounded-xl border bg-white p-6 dark:bg-zinc-900">
      <h3 className="mb-4 text-sm font-semibold">Claim vs Satellite</h3>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Claimed tCO2" value={formatNumber(claim.claimed_tco2)} />
        <Stat
          label="Satellite estimate"
          value={formatNumber(verification.estimated_tco2)}
          sub={
            verification.estimated_tco2_low != null
              ? `${formatNumber(verification.estimated_tco2_low)} – ${formatNumber(
                  verification.estimated_tco2_high,
                )} (±50%)`
              : undefined
          }
        />
        <Stat
          label="Divergence"
          value={delta != null ? `${delta > 0 ? "+" : ""}${delta.toFixed(1)}%` : "—"}
          sub={CREDIT_FLAG_LABEL[flag] ?? flag}
        />
      </div>

      <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-4">
        <Field label="Area" value={claim.claimed_hectares ? `${formatNumber(claim.claimed_hectares)} ha` : "—"} />
        <Field label="Species" value={claim.species ?? "—"} />
        <Field label="Start year" value={claim.start_year ? String(claim.start_year) : "—"} />
        <Field label="Methodology" value={claim.baseline_method ?? "—"} />
        <Field label="NDVI trend" value={verification.ndvi_trend ?? "—"} />
        <Field label="Current NDVI" value={formatNumber(verification.ndvi_current, 2)} />
        <Field label="Control NDVI" value={formatNumber(verification.ndvi_control, 2)} />
        <Field
          label="Fire events"
          value={verification.fire_events_detected != null ? String(verification.fire_events_detected) : "—"}
        />
      </dl>
    </div>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-lg bg-zinc-50 p-4 dark:bg-zinc-800">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="text-2xl font-semibold">{value}</p>
      {sub && <p className="text-xs text-zinc-500">{sub}</p>}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-zinc-500">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}