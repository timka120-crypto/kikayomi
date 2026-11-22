import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface FormFieldProps {
  id: string;
  label: string;
  required?: boolean;
  error?: string;
  hint?: ReactNode;
  className?: string;
  children: ReactNode;
}

export function FormField({ id, label, required, error, hint, className, children }: FormFieldProps) {
  return (
    <div className={cn("min-w-0", className)}>
      <label htmlFor={id} className="mb-2 block truncate text-sm font-semibold text-ink">
        {label}
        {required && (
          <span className="text-burgundy" aria-hidden>
            {" "}
            *
          </span>
        )}
      </label>
      {children}
      {error ? (
        <p id={`${id}-error`} role="alert" className="mt-1.5 text-sm text-[#b42318]">
          {error}
        </p>
      ) : hint ? (
        <p id={`${id}-hint`} className="mt-1.5 text-xs text-ink-muted">
          {hint}
        </p>
      ) : null}
    </div>
  );
}
