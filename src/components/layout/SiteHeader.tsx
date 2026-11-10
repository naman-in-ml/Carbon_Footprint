import { ScanSearch } from "lucide-react";
import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-[1000] h-16 border-b border-line bg-surface/90 shadow-[0_1px_12px_rgba(30,59,99,0.04)] backdrop-blur">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10">
            <ScanSearch className="h-4 w-4 text-accent" />
          </span>
          CarbonProof
        </Link>
        <nav className="flex items-center gap-4 text-sm text-muted sm:gap-6">
          <Link href="/" className="transition-colors hover:text-ink">
            Overview
          </Link>
          <Link href="/projects" className="transition-colors hover:text-ink">
            Projects
          </Link>
          <Link href="/#how" className="hidden transition-colors hover:text-ink sm:inline">
            How it works
          </Link>
          <span className="hidden rounded-lg border border-line bg-bg px-3 py-1.5 text-xs text-muted md:inline">
            Prototype · Indradhanu 2026
          </span>
        </nav>
      </div>
    </header>
  );
}
