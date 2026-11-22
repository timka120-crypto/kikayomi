import Link from "next/link";
import type { ComponentProps, ReactNode } from "react";
import { cn } from "@/lib/cn";

type Variant = "primary" | "outline" | "outlineLight" | "ghost" | "light" | "olive";
type Size = "sm" | "md" | "lg";

const base =
  "inline-flex items-center justify-center gap-2 rounded-full font-semibold tracking-[0.01em] whitespace-nowrap transition-[background-color,color,border-color,box-shadow,transform] duration-300 ease-out active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none select-none";

const variants: Record<Variant, string> = {
  primary:
    "bg-burgundy text-cream shadow-[0_10px_30px_-12px_rgb(118_43_50/0.7)] hover:bg-burgundy-dark hover:shadow-[0_14px_34px_-12px_rgb(118_43_50/0.8)]",
  outline: "border border-ink/25 text-ink hover:border-ink hover:bg-ink hover:text-cream",
  outlineLight: "border border-cream/35 text-cream hover:border-cream hover:bg-cream hover:text-ink",
  ghost: "text-ink hover:bg-ink/5",
  light: "bg-cream text-ink hover:bg-white",
  olive: "bg-olive text-white hover:bg-olive-deep",
};

const sizes: Record<Size, string> = {
  sm: "h-10 px-4 text-sm",
  md: "h-12 px-6 text-[0.95rem]",
  lg: "h-14 px-8 text-base",
};

export function buttonClasses(variant: Variant = "primary", size: Size = "md", className?: string) {
  return cn(base, variants[variant], sizes[size], className);
}

type ButtonProps = ComponentProps<"button"> & { variant?: Variant; size?: Size };

export function Button({ variant, size, className, type = "button", ...props }: ButtonProps) {
  return <button type={type} className={buttonClasses(variant, size, className)} {...props} />;
}

type ButtonLinkProps = ComponentProps<typeof Link> & {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
};

export function ButtonLink({ variant, size, className, ...props }: ButtonLinkProps) {
  return <Link className={buttonClasses(variant, size, className)} {...props} />;
}
