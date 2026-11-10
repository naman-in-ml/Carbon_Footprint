import { AlertTriangle, UserCheck } from "lucide-react";
import { RISK } from "@/lib/risk";
import { cn } from "@/lib/utils";
import type { RiskFlag } from "@/types";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ScoreGauge } from "./ScoreGauge";

export function VerdictBanner({
  score,
  risk,
  reasons,
  requiresReview,
}: {
  score: number;
  risk: RiskFlag;
  reasons: Record<string, string>;
  requiresReview: boolean;
}) {
  const style = RISK[risk];
  return (
    <section
      className={cn(
        "flex flex-col items-center gap-5 rounded-xl border bg-surface p-6 shadow-[0_10px_30px_rgba(30,59,99,0.06)] md:flex-row",
        style.border,
      )}
    >
      <div className={cn("rounded-full", style.bg)}>
        <ScoreGauge score={score} color={style.hex} />
      </div>
      <div className="flex-1">
        <RiskBadge risk={risk} />
        <p className="mt-3 text-xl font-medium">{style.verdict}</p>
        <div className="mt-3 space-y-1">
          {Object.values(reasons).map((reason) => (
            <p key={reason} className={cn("flex gap-2 text-sm", style.text)}>
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              {reason}
            </p>
          ))}
        </div>
        {requiresReview && (
          <span className="mt-4 inline-flex items-center gap-2 rounded-lg border border-line bg-bg px-3 py-1.5 text-xs text-muted">
            <UserCheck className="h-4 w-4 text-accent" />
            Routed to human review
          </span>
        )}
      </div>
    </section>
  );
}
