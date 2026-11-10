import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export function Card({
  title,
  icon: Icon,
  children,
  className,
}: {
  title?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        "rounded-xl border border-line bg-surface p-5 shadow-[0_8px_24px_rgba(30,59,99,0.045)]",
        className,
      )}
    >
      {title && (
        <div className="mb-4 flex items-center gap-2 text-sm font-medium text-ink">
          {Icon && <Icon className="h-4 w-4 text-accent" />}
          <h2>{title}</h2>
        </div>
      )}
      {children}
    </section>
  );
}
