import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface SectionHeadingProps {
  index?: string;
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  align?: "left" | "center";
  tone?: "dark" | "light";
  className?: string;
  as?: "h1" | "h2";
}

/** Numbered eyebrow + serif title — the recurring section header. */
export function SectionHeading({
  index,
  eyebrow,
  title,
  description,
  align = "left",
  tone = "dark",
  className,
  as: Tag = "h2",
}: SectionHeadingProps) {
  const light = tone === "light";
  return (
    <div className={cn(align === "center" && "mx-auto text-center", "max-w-3xl", className)}>
      <p
        className={cn(
          "eyebrow flex items-center gap-3",
          align === "center" && "justify-center",
          light ? "text-cream/80" : "text-burgundy",
        )}
      >
        {index && <span className="font-serif text-base italic tracking-normal normal-case">{index}</span>}
        <span aria-hidden className={cn("h-px w-8", light ? "bg-cream/50" : "bg-burgundy/50")} />
        <span>{eyebrow}</span>
      </p>
      <Tag
        className={cn(
          "mt-5 text-[2.5rem] leading-[1.02] sm:text-5xl lg:text-[3.6rem]",
          light ? "text-cream" : "text-ink",
        )}
      >
        {title}
      </Tag>
      {description && (
        <p
          className={cn(
            "mt-5 text-base leading-relaxed sm:text-lg",
            light ? "text-cream/80" : "text-ink-soft",
            align === "center" && "mx-auto max-w-2xl",
          )}
        >
          {description}
        </p>
      )}
    </div>
  );
}
