"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function NDVIChart({
  timeSeries,
  startYear,
  declineYear,
  controlNdvi,
  fireYears = [],
}: {
  timeSeries: Record<string, number>;
  startYear: number;
  declineYear?: string;
  controlNdvi?: number | null;
  fireYears?: string[];
}) {
  const data = Object.entries(timeSeries).map(([year, ndvi]) => ({
    year,
    ndvi: Number(ndvi.toFixed(3)),
  }));
  const years = new Set(data.map((point) => point.year));
  return (
    <div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid stroke="#e3e9f1" strokeDasharray="3 3" />
          <XAxis dataKey="year" tick={{ fontSize: 11, fill: "#6e7c90" }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 11, fill: "#6e7c90" }} />
          <Tooltip
            contentStyle={{
              background: "#ffffff",
              border: "1px solid #dce4ef",
              borderRadius: 8,
              boxShadow: "0 8px 24px rgba(30,59,99,0.08)",
            }}
          />
          <ReferenceLine x={String(startYear)} stroke="#2869d8" label="Planting" />
          {declineYear && (
            <ReferenceLine x={declineYear} stroke="#d85b63" strokeDasharray="4 4" label="Decline" />
          )}
          {controlNdvi != null && (
            <ReferenceLine y={controlNdvi} stroke="#6e7c90" strokeDasharray="4 4" label="Control" />
          )}
          {[...new Set(fireYears)]
            .filter((year) => years.has(year))
            .map((year) => (
              <ReferenceLine
                key={year}
                x={year}
                stroke="#e27b32"
                strokeDasharray="4 4"
                label="Fire"
              />
            ))}
          <Line
            type="monotone"
            dataKey="ndvi"
            stroke="#2869d8"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="NDVI"
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="mt-2 text-xs text-muted">
        NDVI: 0.0 = bare soil, 0.5+ = dense canopy. Source: Sentinel-2 L2A (10 m, 5-day revisit).
      </p>
    </div>
  );
}
