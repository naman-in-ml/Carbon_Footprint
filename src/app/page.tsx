"use client";

import Link from "next/link";
import { useProjectList } from "@/hooks/useProject";
import type { RiskFlag } from "@/types";

const RISK_STYLES: Record<RiskFlag, string> = {
  low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function Home() {
  const { data, isLoading, isError } = useProjectList();

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">CarbonProof</h1>
        <p className="mt-1 text-zinc-500">
          We verify carbon credit claims — comparing what a project reports against what
          satellites measure.
        </p>
      </header>

      {isLoading && <p className="text-zinc-500">Loading projects…</p>}
      {isError && (
        <p className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          Could not load projects.
        </p>
      )}

      {data?.isDemo && (
        <p className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300">
          <strong>Demo data</strong> — the API/backend isn&apos;t reachable, so precomputed results
          from the seed set are shown.
        </p>
      )}

      {data && data.items.length === 0 && (
        <p className="rounded-lg border bg-white p-6 text-zinc-500 dark:bg-zinc-900">
          No projects yet. Seed demo data with{" "}
          <code className="rounded bg-zinc-100 px-1.5 py-0.5 dark:bg-zinc-800">
            python scripts/seed_projects.py
          </code>
          .
        </p>
      )}

      {data && data.items.length > 0 && (
        <div className="overflow-hidden rounded-xl border bg-white dark:bg-zinc-900">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-zinc-50 text-xs uppercase text-zinc-500 dark:bg-zinc-800">
              <tr>
                <th className="px-4 py-3">Project</th>
                <th className="px-4 py-3">Registry</th>
                <th className="px-4 py-3">Country</th>
                <th className="px-4 py-3">Score</th>
                <th className="px-4 py-3">Risk</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((p) => (
                <tr
                  key={p.project_id}
                  className="border-b last:border-0 hover:bg-zinc-50 dark:hover:bg-zinc-800"
                >
                  <td className="px-4 py-3">
                    <Link
                      href={`/dashboard/${p.project_id}`}
                      className="font-medium text-emerald-700 hover:underline dark:text-emerald-400"
                    >
                      {p.name}
                    </Link>
                    <div className="text-xs text-zinc-500">{p.verra_id}</div>
                  </td>
                  <td className="px-4 py-3">{p.registry}</td>
                  <td className="px-4 py-3">{p.country ?? "—"}</td>
                  <td className="px-4 py-3">
                    {p.composite_score != null ? p.composite_score.toFixed(0) : "—"}
                  </td>
                  <td className="px-4 py-3">
                    {p.risk_flag ? (
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${RISK_STYLES[p.risk_flag]}`}
                      >
                        {p.risk_flag}
                      </span>
                    ) : (
                      <span className="text-xs text-zinc-400">{p.status}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}