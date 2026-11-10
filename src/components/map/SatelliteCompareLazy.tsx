"use client";

import dynamic from "next/dynamic";

export const SatelliteCompareLazy = dynamic(
  () => import("./SatelliteCompare").then((module) => module.SatelliteCompare),
  {
    ssr: false,
    loading: () => <div className="h-[440px] w-full animate-pulse rounded-xl bg-surface-2" />,
  },
);
