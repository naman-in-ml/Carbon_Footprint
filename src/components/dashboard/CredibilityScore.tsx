import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { RiskFlag } from "@/types";

type Props = {
  composite_score: number;
  risk_flag: RiskFlag;
  flag_reasons: Record<string, string>;
  extraction_score: number;
  planting_score: number;
  permanence_score: number;
  credit_math_score: number;
};

const FLAG_CONFIG: Record<RiskFlag, { color: string; label: string; text: string }> = {
  low: { color: "bg-green-500", label: "Low Risk", text: "text-green-700 dark:text-green-400" },
  medium: { color: "bg-yellow-500", label: "Medium Risk", text: "text-yellow-700 dark:text-yellow-400" },
  high: { color: "bg-orange-500", label: "High Risk", text: "text-orange-700 dark:text-orange-400" },
  critical: { color: "bg-red-500", label: "Critical Risk", text: "text-red-700 dark:text-red-400" },
};

export function CredibilityScore({
  composite_score,
  risk_flag,
  flag_reasons,
  extraction_score,
  planting_score,
  permanence_score,
  credit_math_score,
}: Props) {
  const cfg = FLAG_CONFIG[risk_flag] ?? FLAG_CONFIG.medium;

  const breakdown = [
    { label: "Claim Extraction", score: extraction_score, weight: "15%" },
    { label: "Planting Verified", score: planting_score, weight: "35%" },
    { label: "Permanence Check", score: permanence_score, weight: "35%" },
    { label: "Credit Math", score: credit_math_score, weight: "15%" },
  ];

  return (
    <div className="rounded-xl border bg-white p-6 space-y-6 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-zinc-500">Credibility Score</p>
          <p className={`text-5xl font-bold ${cfg.text}`}>
            {composite_score.toFixed(0)}
            <span className="text-2xl text-zinc-400">/100</span>
          </p>
        </div>
        <Badge className={`${cfg.color} text-white`}>{cfg.label}</Badge>
      </div>

      <div className="space-y-3">
        {breakdown.map(({ label, score, weight }) => (
          <div key={label}>
            <div className="flex justify-between text-sm mb-1">
              <span>{label}</span>
              <span className="text-zinc-500">
                {score.toFixed(0)} / 100 (weight {weight})
              </span>
            </div>
            <Progress value={score} />
          </div>
        ))}
      </div>

      {Object.keys(flag_reasons).length > 0 && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 space-y-1 dark:border-red-900 dark:bg-red-950">
          <p className="text-sm font-medium text-red-800 dark:text-red-200">Risk Flags</p>
          {Object.entries(flag_reasons).map(([key, reason]) => (
            <p key={key} className="text-xs text-red-600 dark:text-red-300">
              • {reason}
            </p>
          ))}
        </div>
      )}

      <p className="text-xs text-zinc-500">
        Screening tool for auditors — flags indicate areas requiring human review, not a fraud
        verdict. Biomass and credit estimates are order-of-magnitude screening estimates
        (&plusmn;50%), not verified carbon accounting.
      </p>
    </div>
  );
}