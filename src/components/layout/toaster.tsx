"use client";

import { Check, X } from "lucide-react";
import { useUI } from "@/components/providers/ui-provider";

export function Toaster() {
  const { toasts, dismiss, openCart } = useUI();

  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-[calc(6.5rem+env(safe-area-inset-bottom))] z-[55] flex flex-col items-center gap-2 px-4 lg:top-24 lg:right-6 lg:bottom-auto lg:left-auto lg:items-end"
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role="status"
          className="pointer-events-auto flex w-full max-w-sm animate-fade-up items-center gap-3 rounded-2xl bg-ink py-3 pr-2 pl-4 text-cream shadow-[0_20px_50px_-20px_rgb(0_0_0/0.6)]"
        >
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-olive">
            <Check className="h-4 w-4" strokeWidth={2.6} />
          </span>
          <div className="min-w-0 flex-1">
            <p className="line-clamp-2 text-sm font-semibold">{toast.title}</p>
            {toast.description && <p className="text-xs text-cream/65">{toast.description}</p>}
          </div>
          {toast.cartAction && (
            <button
              type="button"
              onClick={() => {
                dismiss(toast.id);
                openCart();
              }}
              className="shrink-0 rounded-full bg-cream px-3.5 py-2 text-xs font-bold text-ink transition-colors hover:bg-white"
            >
              Корзина
            </button>
          )}
          <button
            type="button"
            onClick={() => dismiss(toast.id)}
            className="grid h-8 w-8 shrink-0 place-items-center rounded-full text-cream/60 hover:bg-white/10 hover:text-cream"
            aria-label="Закрыть уведомление"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
