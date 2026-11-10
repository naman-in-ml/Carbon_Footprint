"use client";

import dynamic from "next/dynamic";

export const PortfolioMapLazy = dynamic(
  () => import("./PortfolioMap").then((module) => module.PortfolioMap),
  { ssr: false, loading: () => <div className="h-full w-full animate-pulse bg-surface-2" /> },
);
