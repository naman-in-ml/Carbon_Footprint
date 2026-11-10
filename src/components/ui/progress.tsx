import { cn } from "@/lib/utils";

export function Progress({
  value,
  className,
  colorClass = "bg-accent",
}: {
  value: number;
  className?: string;
  colorClass?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className={cn("h-2 w-full overflow-hidden rounded-full bg-surface-2", className)}>
      <div
        className={cn("h-full rounded-full transition-all", colorClass)}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
