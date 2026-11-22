"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { X } from "lucide-react";
import { useUI } from "@/components/providers/ui-provider";
import { useCart } from "@/lib/cart/use-cart";
import { cn } from "@/lib/cn";
import { CartContents } from "./cart-contents";

/** Slide-over cart, available from every page in one tap. */
export function CartDrawer() {
  const { cartOpen, closeCart } = useUI();
  const { count } = useCart();
  const pathname = usePathname();
  const panelRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  // Close on navigation.
  useEffect(() => {
    closeCart();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  // Esc to close, lock page scroll, focus management.
  useEffect(() => {
    if (!cartOpen) return;
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();

    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeCart();
      if (event.key === "Tab" && panelRef.current) {
        const focusable = panelRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])',
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = overflow;
      document.removeEventListener("keydown", onKey);
      previouslyFocused?.focus?.();
    };
  }, [cartOpen, closeCart]);

  return (
    <div
      className={cn("fixed inset-0 z-[60]", cartOpen ? "visible" : "invisible delay-500")}
      aria-hidden={!cartOpen}
      inert={!cartOpen}
    >
      <div
        className={cn(
          "absolute inset-0 bg-ink/45 backdrop-blur-[2px] transition-opacity duration-500",
          cartOpen ? "opacity-100" : "opacity-0",
        )}
        onClick={closeCart}
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="cart-drawer-title"
        data-testid="cart-drawer"
        className={cn(
          "absolute top-0 right-0 flex h-full w-full max-w-[460px] flex-col bg-cream shadow-[-30px_0_80px_-30px_rgb(37_35_31/0.5)] transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]",
          cartOpen ? "translate-x-0" : "translate-x-full",
        )}
      >
        <div className="flex items-center justify-between border-b border-ink/10 px-5 py-4 sm:px-7 sm:py-5">
          <h2 id="cart-drawer-title" className="font-serif text-3xl">
            Корзина
            {count > 0 && (
              <span className="ml-2 align-middle font-sans text-sm font-semibold text-ink-muted">
                ({count})
              </span>
            )}
          </h2>
          <button
            ref={closeRef}
            type="button"
            onClick={closeCart}
            className="grid h-11 w-11 place-items-center rounded-full transition-colors hover:bg-ink/5"
            aria-label="Закрыть корзину"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <CartContents onNavigate={closeCart} />
      </div>
    </div>
  );
}
