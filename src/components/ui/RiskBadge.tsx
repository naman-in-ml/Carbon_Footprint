import { RISK } from "@/lib/risk";
import { cn } from "@/lib/utils";
import type { RiskFlag } from "@/types";

export function RiskBadge({ risk }: { risk: RiskFlag | null }) {
  if (!risk) {
    return (
      <span className="inline-flex rounded-full border border-line bg-surface-2 px-2.5 py-1 text-xs text-muted">
        Pending
      </span>
    );
  }
  const style = RISK[risk];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
        style.bg,
        style.text,
        style.border,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {style.label}
    </span>
  );
}
