"use client";

import { FileText, Flame, Ruler, Scale, Sprout } from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { useProjectDetail, useProjectList } from "@/hooks/useProject";

const STEPS = [
  {
    icon: FileText,
    title: "Extract claims",
    text: "Nugen AI turns the project document into structured claims: location, hectares, species, CO₂.",
  },
  {
    icon: Ruler,
    title: "Measure the area",
    text: "ESA WorldCover measures the actual tree cover inside the project area, independent of the claimed hectares.",
  },
  {
    icon: Sprout,
    title: "Verify planting",
    text: "Sentinel-2 NDVI before vs after planting, compared with a control region nearby.",
  },
  {
    icon: Flame,
    title: "Check permanence",
    text: "NASA FIRMS fire detections and Hansen forest-loss data since the project started.",
  },
  {
    icon: Scale,
    title: "Score & route",
    text: "A weighted, explainable 0–100 score. Ambiguous or risky cases go to a human auditor.",
  },
];

export default function Home() {
  const list = useProjectList();
  const items = list.data?.items ?? [];
  const critical = items.find((item) => item.risk_flag === "critical");
  const detail = useProjectDetail(critical ? String(critical.project_id) : "");
  const flagged = items.filter(
    (item) => item.risk_flag === "high" || item.risk_flag === "critical",
  ).length;
  const scored = items.filter((item) => item.composite_score != null);
  const average = scored.length
    ? scored.reduce((sum, item) => sum + (item.composite_score ?? 0), 0) / scored.length
    : 0;
  const reasons = Object.values(detail.data?.detail.score?.flag_reasons ?? {}).slice(0, 3);

  return (
    <main>
      <section className="relative mx-auto grid max-w-7xl gap-12 overflow-hidden px-6 py-20 lg:grid-cols-2 lg:items-center">
        <div className="pointer-events-none absolute right-0 top-8 -z-10 h-80 w-80 rounded-full bg-accent/8 blur-3xl" />
        <div>
          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
            AI for Climate Change · Carbon MRV
          </span>
          <h1 className="mt-6 text-5xl font-semibold tracking-tight md:text-6xl">
            Carbon credits,
            <br />
            <span className="text-accent">fact-checked from orbit.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-muted">
            CarbonProof reads what a carbon project claims, then checks it against what Sentinel-2
            satellites actually measured: planting, permanence, fire and forest loss. It&apos;s a
            verifier, not a summarizer.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/projects"
              className="rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-accent-strong"
            >
              Open audit portfolio
            </Link>
            <Link
              href={critical ? `/dashboard/${critical.project_id}` : "/projects"}
              className="rounded-lg border border-line bg-surface px-5 py-2.5 text-sm shadow-sm transition-colors hover:border-accent/50"
            >
              See a phantom forest
            </Link>
          </div>
        </div>
        {list.isLoading || (critical && detail.isLoading) ? (
          <div className="h-72 animate-pulse rounded-xl bg-surface-2" />
        ) : (
          <Card className="relative overflow-hidden border-accent/15 p-8 shadow-[0_16px_40px_rgba(30,59,99,0.08)]">
            <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-risk-critical/10 blur-3xl" />
            <p className="text-sm text-muted">Lowest-credibility claim</p>
            <p className="mt-5 font-mono text-7xl text-risk-critical">
              {critical?.composite_score?.toFixed(0) ?? "—"}
            </p>
            <h2 className="mt-4 text-xl font-medium">
              {critical?.name ?? "Awaiting project data"}
            </h2>
            <div className="mt-5 space-y-2 text-sm text-muted">
              {reasons.map((reason) => (
                <p key={reason}>— {reason}</p>
              ))}
            </div>
          </Card>
        )}
      </section>

      <section className="border-y border-line bg-surface">
        <div className="mx-auto grid max-w-7xl grid-cols-2 px-6 md:grid-cols-4">
          {[
            ["Projects screened", items.length],
            ["Flagged high/critical", flagged],
            ["Average credibility", average.toFixed(0)],
            ["Data sources", "5"],
          ].map(([label, value]) => (
            <div key={label} className="border-line px-4 py-7 md:border-r md:last:border-0">
              <p className="font-mono text-3xl text-accent">{value}</p>
              <p className="mt-1 text-xs text-muted">{label}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="how" className="mx-auto max-w-7xl px-6 py-20">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
          Five-stage verification
        </p>
        <h2 className="mt-2 text-3xl font-semibold">From claim document to audit queue</h2>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {STEPS.map(({ icon: Icon, title, text }, index) => (
            <Card key={title}>
              <div className="flex items-center justify-between">
                <Icon className="h-5 w-5 text-accent" />
                <span className="font-mono text-xs text-muted">0{index + 1}</span>
              </div>
              <h3 className="mt-5 font-medium">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{text}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="flex flex-wrap gap-2">
          {["Sentinel-2 L2A", "ESA WorldCover", "Hansen GFC", "NASA FIRMS", "Nugen AI"].map(
            (source) => (
              <span
                key={source}
                className="rounded-full border border-line bg-surface px-3 py-1.5 text-xs text-muted"
              >
                {source}
              </span>
            ),
          )}
        </div>
      </section>
    </main>
  );
}
