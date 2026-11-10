"use client";

import { Activity, Gauge, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { PortfolioMapLazy } from "@/components/map/PortfolioMapLazy";
import { Card } from "@/components/ui/Card";
import { DemoNotice } from "@/components/ui/DemoNotice";
import { Progress } from "@/components/ui/progress";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { useProjectList } from "@/hooks/useProject";
import { parsePointWkt } from "@/lib/geo";
import type { RiskFlag } from "@/types";

const FILTERS: { label: string; value: RiskFlag | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Low", value: "low" },
  { label: "Medium", value: "medium" },
  { label: "High", value: "high" },
  { label: "Critical", value: "critical" },
];

const BAR_COLORS: Record<RiskFlag, string> = {
  low: "bg-risk-low",
  medium: "bg-risk-medium",
  high: "bg-risk-high",
  critical: "bg-risk-critical",
};

export default function ProjectsPage() {
  const { data, isLoading, isError } = useProjectList();
  const [filter, setFilter] = useState<RiskFlag | "all">("all");
  const items = data?.items ?? [];
  const scored = items.filter((item) => item.composite_score != null);
  const average = scored.length
    ? scored.reduce((sum, item) => sum + (item.composite_score ?? 0), 0) / scored.length
    : 0;
  const criticalCount = items.filter((item) => item.risk_flag === "critical").length;
  const filtered = items
    .filter((item) => filter === "all" || item.risk_flag === filter)
    .sort((a, b) => (a.composite_score ?? 101) - (b.composite_score ?? 101));
  const hasCoordinates = filtered.some((item) => parsePointWkt(item.geometry_wkt));

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 px-6 py-8">
      <div className="grid gap-4 lg:grid-cols-[1fr_420px] lg:items-stretch">
        <div className="flex flex-col justify-center">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
            Audit workspace
          </p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight">Portfolio screening</h1>
          <p className="mt-2 text-muted">
            Review the weakest carbon claims first using independent satellite evidence.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <Card className="p-4">
            <Activity className="h-4 w-4 text-accent" />
            <p className="mt-3 font-mono text-2xl">{items.length}</p>
            <p className="mt-1 text-xs text-muted">Projects screened</p>
          </Card>
          <Card className="p-4">
            <ShieldAlert className="h-4 w-4 text-risk-critical" />
            <p className="mt-3 font-mono text-2xl">{criticalCount}</p>
            <p className="mt-1 text-xs text-muted">Critical review</p>
          </Card>
          <Card className="p-4">
            <Gauge className="h-4 w-4 text-accent" />
            <p className="mt-3 font-mono text-2xl">{average.toFixed(0)}</p>
            <p className="mt-1 text-xs text-muted">Average score</p>
          </Card>
        </div>
      </div>

      {data?.isDemo && <DemoNotice />}

      <div className="flex flex-wrap gap-2 border-y border-line py-4">
        {FILTERS.map(({ label, value }) => {
          const count =
            value === "all"
              ? items.length
              : items.filter((item) => item.risk_flag === value).length;
          return (
            <button
              key={value}
              type="button"
              onClick={() => setFilter(value)}
              className={`rounded-lg border px-3 py-1.5 text-sm transition-colors ${filter === value ? "border-accent bg-accent text-white shadow-sm" : "border-line bg-surface text-muted hover:border-accent/40 hover:text-ink"}`}
            >
              {label} <span className="font-mono">{count}</span>
            </button>
          );
        })}
      </div>

      {isError ? (
        <Card>Could not load projects.</Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-5">
          <div className="order-2 h-[500px] overflow-hidden rounded-xl border border-line bg-surface shadow-[0_8px_24px_rgba(30,59,99,0.045)] lg:col-span-3">
            {isLoading ? (
              <div className="h-full animate-pulse bg-surface-2" />
            ) : hasCoordinates ? (
              <PortfolioMapLazy items={filtered} />
            ) : (
              <Card className="flex h-full items-center justify-center rounded-none border-0 text-muted">
                Map unavailable: no coordinates
              </Card>
            )}
          </div>
          <div className="order-1 space-y-3 lg:col-span-2">
            {isLoading &&
              [1, 2, 3].map((key) => (
                <div key={key} className="h-32 animate-pulse rounded-xl bg-surface-2" />
              ))}
            {!isLoading &&
              filtered.map((item) => (
                <Link
                  key={item.project_id}
                  href={`/dashboard/${item.project_id}`}
                  className="block rounded-xl border border-line bg-surface p-4 shadow-[0_8px_24px_rgba(30,59,99,0.035)] transition-all hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-[0_12px_28px_rgba(30,59,99,0.08)]"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="font-medium">{item.name}</h2>
                      <p className="mt-1 text-xs text-muted">
                        {item.verra_id} · {item.country ?? "—"}
                      </p>
                    </div>
                    <RiskBadge risk={item.risk_flag} />
                  </div>
                  <div className="mt-4 flex items-end gap-3">
                    <span className="font-mono text-2xl">
                      {item.composite_score?.toFixed(0) ?? "—"}
                    </span>
                    <span className="pb-1 text-xs text-muted">/ 100 credibility</span>
                  </div>
                  <Progress
                    className="mt-2 h-1"
                    value={item.composite_score ?? 0}
                    colorClass={item.risk_flag ? BAR_COLORS[item.risk_flag] : "bg-muted"}
                  />
                </Link>
              ))}
          </div>
        </div>
      )}
    </main>
  );
}
