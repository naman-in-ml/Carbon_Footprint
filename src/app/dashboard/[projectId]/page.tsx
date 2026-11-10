"use client";

import { Loader2, Satellite } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { CredibilityScore } from "@/components/dashboard/CredibilityScore";
import { EvidenceCards } from "@/components/dashboard/EvidenceCards";
import { ExtractionDetails } from "@/components/dashboard/ExtractionDetails";
import { NDVIChart } from "@/components/dashboard/NDVIChart";
import { PipelineTimeline } from "@/components/dashboard/PipelineTimeline";
import { VerdictBanner } from "@/components/dashboard/VerdictBanner";
import { SatelliteCompareLazy } from "@/components/map/SatelliteCompareLazy";
import { Card } from "@/components/ui/Card";
import { DemoNotice } from "@/components/ui/DemoNotice";
import { useProjectDetail } from "@/hooks/useProject";
import { parsePointWkt } from "@/lib/geo";

export default function ProjectDashboard() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data, isLoading, isError } = useProjectDetail(projectId);
  if (isLoading)
    return (
      <main className="mx-auto max-w-7xl space-y-6 px-6 py-10">
        <div className="flex items-center gap-2 text-muted">
          <Loader2 className="h-5 w-5 animate-spin" />
          Running verification pipeline…
        </div>
        <div className="h-40 animate-pulse rounded-2xl bg-surface-2" />
        <div className="h-96 animate-pulse rounded-2xl bg-surface-2" />
      </main>
    );
  if (isError || !data)
    return (
      <main className="mx-auto max-w-7xl px-6 py-10">
        <Card>Project not found.</Card>
      </main>
    );
  const { project, claim, verification, score } = data.detail;
  if (!score || !claim || !verification)
    return (
      <main className="mx-auto max-w-7xl px-6 py-10">
        <Card>
          Analysis in progress (status: <strong>{project.status}</strong>). This page refreshes
          automatically.
        </Card>
      </main>
    );
  const point = parsePointWkt(claim.geometry_wkt);
  const fireYears = verification.fire_dates?.dates.map((date) => date.slice(0, 4)) ?? [];
  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 px-6 py-8">
      <header>
        <Link
          href="/projects"
          className="inline-flex rounded-lg border border-line bg-surface px-3 py-1.5 text-sm text-muted shadow-sm transition-colors hover:border-accent/40 hover:text-accent"
        >
          ← Portfolio
        </Link>
        <p className="mt-6 text-xs font-semibold uppercase tracking-[0.16em] text-accent">
          Project evidence report
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">{project.name}</h1>
        <p className="mt-1 text-sm text-muted">
          {project.verra_id} · {project.country ?? "—"} · {project.registry} · start{" "}
          {claim.start_year ?? "—"}
        </p>
        {data.isDemo && (
          <div className="mt-3">
            <DemoNotice />
          </div>
        )}
      </header>
      <VerdictBanner
        score={score.composite_score}
        risk={score.risk_flag}
        reasons={score.flag_reasons ?? {}}
        requiresReview={claim.requires_review}
      />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card
          title="Satellite evidence: before vs after"
          icon={Satellite}
          className="lg:col-span-2"
        >
          {point ? (
            <SatelliteCompareLazy
              lat={point.lat}
              lon={point.lon}
              startYear={claim.start_year}
              areaHa={verification.aoi_ha ?? claim.claimed_hectares}
              boundary={claim.boundary_geojson}
            />
          ) : (
            <div className="flex h-[440px] items-center justify-center text-muted">
              No coordinates resolved for this project
            </div>
          )}
        </Card>
        <Card title="Score breakdown">
          <CredibilityScore
            extraction_score={score.extraction_score}
            planting_score={score.planting_score}
            permanence_score={score.permanence_score}
            credit_math_score={score.credit_math_score}
          />
        </Card>
      </div>
      <EvidenceCards claim={claim} verification={verification} />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Vegetation index over time (NDVI)" className="lg:col-span-2">
          {verification.ndvi_time_series ? (
            <NDVIChart
              timeSeries={verification.ndvi_time_series}
              startYear={claim.start_year ?? 2020}
              declineYear={verification.decline_detected_since ?? undefined}
              controlNdvi={verification.ndvi_control}
              fireYears={fireYears}
            />
          ) : (
            <p className="text-muted">No NDVI series available.</p>
          )}
        </Card>
        <PipelineTimeline claim={claim} verification={verification} score={score} />
      </div>
      <ExtractionDetails claim={claim} />
    </main>
  );
}
