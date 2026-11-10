import type { RiskFlag } from "@/types";

export const RISK: Record<
  RiskFlag,
  { label: string; text: string; bg: string; border: string; hex: string; verdict: string }
> = {
  low: {
    label: "Low risk",
    text: "text-risk-low",
    bg: "bg-risk-low/10",
    border: "border-risk-low/30",
    hex: "#2f9e6d",
    verdict: "Satellite evidence supports the project's claims.",
  },
  medium: {
    label: "Medium risk",
    text: "text-risk-medium",
    bg: "bg-risk-medium/10",
    border: "border-risk-medium/30",
    hex: "#c78512",
    verdict: "Some claims are not fully supported. Human review recommended.",
  },
  high: {
    label: "High risk",
    text: "text-risk-high",
    bg: "bg-risk-high/10",
    border: "border-risk-high/30",
    hex: "#e27b32",
    verdict: "Significant discrepancies between claims and satellite evidence.",
  },
  critical: {
    label: "Critical risk",
    text: "text-risk-critical",
    bg: "bg-risk-critical/10",
    border: "border-risk-critical/30",
    hex: "#d85b63",
    verdict: "Claims are not supported by satellite evidence. Route to an auditor.",
  },
};
