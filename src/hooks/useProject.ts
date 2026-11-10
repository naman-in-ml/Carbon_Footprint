"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { DEMO_PROJECTS, demoDetail } from "@/lib/demoData";
import type { ProjectDetail, ScoreListItem } from "@/types";

export type ProjectListResult = { items: ScoreListItem[]; isDemo: boolean };
export type ProjectDetailResult = { detail: ProjectDetail; isDemo: boolean };

export function useProjectList() {
  return useQuery<ProjectListResult>({
    queryKey: ["scores"],
    queryFn: async () => {
      try {
        const { data } = await api.get<ScoreListItem[]>("/scores/");
        return { items: data, isDemo: false };
      } catch {
        return { items: DEMO_PROJECTS, isDemo: true };
      }
    },
  });
}

export function useProjectDetail(projectId: string) {
  return useQuery<ProjectDetailResult>({
    queryKey: ["score", projectId],
    enabled: !!projectId,
    queryFn: async () => {
      try {
        const { data } = await api.get<ProjectDetail>(`/scores/${projectId}`);
        return { detail: data, isDemo: false };
      } catch {
        const detail = demoDetail(projectId);
        if (!detail) throw new Error(`Project ${projectId} not found`);
        return { detail, isDemo: true };
      }
    },
  });
}
