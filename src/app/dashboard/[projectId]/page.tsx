"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ClaimVsSatellite } from "@/components/dashboard/ClaimVsSatellite";
import { CredibilityScore } from "@/components/dashboard/CredibilityScore";
import { NDVIChart } from "@/components/dashboard/NDVIChart";
import { useProjectDetail } from "@/hooks/useProject";

export default function ProjectDashboard() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data, isLoading, isError } = useProjectDetail(projectId);

  if (isLoading) return <div className="p-8 text-zinc-500">Running pipeline…</div>;
  if (isError || !data)
    return <div className="p-8 text-zinc-500">Project not found.</div>;

  const { project, claim, verification, score } = data.detail;

  return (
    <main className="mx-auto w-full max-w-6xl space-y-6 px-6 py-10">
      <div>
        <Link href="/" className="text-sm text-emerald-700 hover:underline dark:text-emerald-400">
          ← All projects
        </Link>
        <h1 className="mt-2 text-2xl font-bold">{project.name}</h1>
        <p className="text-sm text-zinc-500">
          {project.verra_id} · {project.country ?? "—"} · {project.registry}
        </p>
        {data.isDemo && (
          <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300">
            <strong>Demo data</strong> — precomputed results; the live API/backend isn&apos;t
            reachable from this deployment.
          </p>
        )}
      </div>

      {!score && (
        <p className="rounded-lg border bg-white p-6 text-zinc-500 dark:bg-zinc-900">
          Analysis in progress (status: <strong>{project.status}</strong>). This page refreshes
          automatically.
        </p>
      )}

      {score && (
        <>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <CredibilityScore
              composite_score={score.composite_score}
              risk_flag={score.risk_flag}
              flag_reasons={score.flag_reasons ?? {}}
              extraction_score={score.extraction_score}
              planting_score={score.planting_score}
              permanence_score={score.permanence_score}
              credit_math_score={score.credit_math_score}
            />
            {verification?.ndvi_time_series && (
              <NDVIChart
                timeSeries={verification.ndvi_time_series}
                startYear={claim?.start_year ?? 2020}
                declineYear={verification.decline_detected_since ?? undefined}
              />
            )}
          </div>
          <ClaimVsSatellite claim={claim} verification={verification} />
        </>
      )}
    </main>
  );
}