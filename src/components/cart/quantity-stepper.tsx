"use client";

import { Minus, Plus } from "lucide-react";
import { MAX_QUANTITY_PER_ITEM } from "@/lib/pricing";
import { cn } from "@/lib/cn";

interface QuantityStepperProps {
  value: number;
  onChange: (value: number) => void;
  label: string;
  size?: "sm" | "md";
  tone?: "solid" | "soft";
  className?: string;
}

/** − 2 + control. Decreasing to 0 removes the dish. */
export function QuantityStepper({
  value,
  onChange,
  label,
  size = "md",
  tone = "soft",
  className,
}: QuantityStepperProps) {
  const solid = tone === "solid";
  const btn = cn(
    "grid place-items-center rounded-full transition-colors duration-200 disabled:opacity-40",
    size === "sm" ? "h-9 w-9" : "h-11 w-11",
    solid ? "text-cream hover:bg-white/15" : "text-ink hover:bg-ink/8",
  );
  return (
    <div
      role="group"
      aria-label={`Количество: ${label}`}
      className={cn(
        "inline-flex items-center rounded-full",
        size === "sm" ? "gap-0.5 p-0.5" : "gap-1 p-0.5",
        solid ? "bg-burgundy text-cream" : "border border-line bg-white",
        className,
      )}
    >
      <button
        type="button"
        className={btn}
        onClick={() => onChange(value - 1)}
        aria-label={value === 1 ? `Убрать «${label}» из корзины` : `Уменьшить количество «${label}»`}
      >
        <Minus className={size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4"} strokeWidth={2.2} />
      </button>
      <span
        aria-live="polite"
        className={cn(
          "min-w-[1.75rem] text-center font-semibold tabular-nums",
          size === "sm" ? "text-sm" : "text-base",
        )}
      >
        {value}
      </span>
      <button
        type="button"
        className={btn}
        onClick={() => onChange(value + 1)}
        disabled={value >= MAX_QUANTITY_PER_ITEM}
        aria-label={`Увеличить количество «${label}»`}
      >
        <Plus className={size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4"} strokeWidth={2.2} />
      </button>
    </div>
  );
}
