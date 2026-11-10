import { Progress } from "@/components/ui/progress";

const scoreColor = (score: number) =>
  score >= 75
    ? "bg-risk-low"
    : score >= 50
      ? "bg-risk-medium"
      : score >= 30
        ? "bg-risk-high"
        : "bg-risk-critical";

export function CredibilityScore({
  extraction_score,
  planting_score,
  permanence_score,
  credit_math_score,
}: {
  extraction_score: number;
  planting_score: number;
  permanence_score: number;
  credit_math_score: number;
}) {
  const breakdown = [
    { label: "Claim extraction", score: extraction_score, weight: "15%" },
    { label: "Planting verified", score: planting_score, weight: "35%" },
    { label: "Permanence check", score: permanence_score, weight: "35%" },
    { label: "Credit math", score: credit_math_score, weight: "15%" },
  ];
  return (
    <div className="space-y-4">
      {breakdown.map(({ label, score, weight }) => (
        <div key={label}>
          <div className="mb-1 flex justify-between text-sm">
            <span>{label}</span>
            <span className="text-muted">
              {score.toFixed(0)} / 100 · weight {weight}
            </span>
          </div>
          <Progress value={score} colorClass={scoreColor(score)} />
        </div>
      ))}
      <p className="pt-2 text-xs text-muted">
        Screening tool for auditors — flags indicate areas requiring human review, not a fraud
        verdict. Biomass and credit estimates are order-of-magnitude screening estimates (±50%), not
        verified carbon accounting.
      </p>
    </div>
  );
}
