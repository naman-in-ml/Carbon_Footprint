"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Props = {
  timeSeries: Record<string, number>;
  startYear: number;
  declineYear?: string;
};

export function NDVIChart({ timeSeries, startYear, declineYear }: Props) {
  const data = Object.entries(timeSeries).map(([year, ndvi]) => ({
    year,
    ndvi: typeof ndvi === "number" ? +ndvi.toFixed(3) : null,
  }));

  return (
    <div className="rounded-xl border bg-white p-4 dark:bg-zinc-900">
      <h3 className="mb-4 text-sm font-semibold">NDVI Time Series (Sentinel-2)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <ReferenceLine x={String(startYear)} stroke="#22c55e" label="Planting" />
          {declineYear && <ReferenceLine x={declineYear} stroke="#ef4444" label="Decline" />}
          <ReferenceLine y={0.5} stroke="#15803d" strokeDasharray="4 4" />
          <ReferenceLine y={0.2} stroke="#ca8a04" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="ndvi"
            stroke="#22c55e"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="NDVI"
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="mt-2 text-xs text-zinc-500">
        NDVI: 0.0 = bare soil, 0.5+ = dense canopy. Source: Sentinel-2 L2A (10m, 5-day revisit).
      </p>
    </div>
  );
}