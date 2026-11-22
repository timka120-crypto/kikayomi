import Link from "next/link";
import { cn } from "@/lib/cn";

/** Olive sprig emblem — drawn by hand in SVG, inherits currentColor. */
export function OliveSprig({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" fill="none" aria-hidden className={className}>
      <path d="M8 33C14 26 20 19 32 7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M14.5 25.5c-4.6-.2-7.4-2.6-8.2-6.4 4.3-.3 7.4 2.1 8.2 6.4Z" fill="currentColor" opacity=".9" />
      <path d="M15.2 24.4c.6-4.6 3.2-7.3 7-8 .2 4.3-2.4 7.3-7 8Z" fill="currentColor" opacity=".55" />
      <path d="M21.6 17.6c-4.4-.6-6.8-3.4-7.2-7.3 4.2.1 7 2.9 7.2 7.3Z" fill="currentColor" opacity=".9" />
      <path d="M22.6 16.4c1-4.4 3.9-6.8 7.8-7.1-.3 4.2-3.3 7-7.8 7.1Z" fill="currentColor" opacity=".55" />
      <ellipse cx="9.8" cy="31.6" rx="2.4" ry="3" transform="rotate(35 9.8 31.6)" fill="currentColor" />
    </svg>
  );
}

interface LogoProps {
  className?: string;
  tone?: "dark" | "light";
  showTagline?: boolean;
}

export function Logo({ className, tone = "dark", showTagline = true }: LogoProps) {
  const light = tone === "light";
  return (
    <Link
      href="/"
      aria-label="BEKAKOTAK — на главную"
      className={cn("group inline-flex items-center gap-2.5", className)}
    >
      <OliveSprig
        className={cn(
          "h-9 w-9 shrink-0 transition-transform duration-500 group-hover:-rotate-12",
          light ? "text-cream" : "text-olive",
        )}
      />
      <span className="flex flex-col leading-none">
        <span
          className={cn(
            "font-serif text-[1.55rem] font-semibold tracking-[0.14em]",
            light ? "text-cream" : "text-burgundy",
          )}
        >
          BEKAKOTAK
        </span>
        {showTagline && (
          <span
            className={cn(
              "mt-1 text-[0.58rem] font-bold tracking-[0.42em] uppercase",
              light ? "text-cream/60" : "text-ink-muted",
            )}
          >
            Cucina italiana
          </span>
        )}
      </span>
    </Link>
  );
}
