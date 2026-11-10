export function ScoreGauge({
  score,
  color,
  size = 132,
}: {
  score: number;
  color: string;
  size?: number;
}) {
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      role="img"
      aria-label={`Credibility score ${score.toFixed(0)} out of 100`}
    >
      <circle cx="60" cy="60" r={radius} fill="none" stroke="#e3e9f1" strokeWidth="10" />
      <circle
        cx="60"
        cy="60"
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={`${circumference * pct} ${circumference}`}
        transform="rotate(-90 60 60)"
        style={{ transition: "stroke-dasharray 0.8s ease" }}
      />
      <text
        x="60"
        y="58"
        textAnchor="middle"
        fontSize="30"
        fontWeight="600"
        fill="#18253a"
        fontFamily="var(--font-geist-mono)"
      >
        {score.toFixed(0)}
      </text>
      <text x="60" y="78" textAnchor="middle" fontSize="11" fill="#6e7c90">
        / 100
      </text>
    </svg>
  );
}
