"use client";

import { usePathname } from "next/navigation";
import { ShoppingBag } from "lucide-react";
import { useUI } from "@/components/providers/ui-provider";
import { useCart } from "@/lib/cart/use-cart";
import { formatPrice, pluralize } from "@/lib/format";

const HIDDEN_ON = ["/checkout", "/cart"];

/** Sticky bottom bar on phones/tablets: the cart is always one tap away. */
export function MobileCartBar() {
  const { count, totals, hydrated } = useCart();
  const { openCart, cartOpen } = useUI();
  const pathname = usePathname();

  const hidden = !hydrated || count === 0 || HIDDEN_ON.some((path) => pathname.startsWith(path));
  if (hidden) return null;

  return (
    <>
      {/* Spacer so the bar never covers the end of the page */}
      <div aria-hidden className="h-24 lg:hidden" />
      <div
        className={`fixed inset-x-0 bottom-0 z-50 px-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] transition-transform duration-300 lg:hidden ${cartOpen ? "translate-y-full" : "translate-y-0"}`}
      >
        <button
          type="button"
          onClick={openCart}
          data-testid="mobile-cart-bar"
          className="flex h-16 w-full animate-fade-up items-center gap-3 rounded-2xl bg-burgundy px-4 text-left text-cream shadow-[0_18px_40px_-14px_rgb(118_43_50/0.85)] active:scale-[0.99]"
        >
          <span className="relative grid h-10 w-10 shrink-0 place-items-center rounded-full bg-white/12">
            <ShoppingBag className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 grid h-5 min-w-5 place-items-center rounded-full bg-cream px-1 text-[0.7rem] font-bold text-burgundy">
              {count}
            </span>
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-sm font-semibold">Корзина</span>
            <span className="block text-xs text-cream/75">
              {count} {pluralize(count, ["порция", "порции", "порций"])}
            </span>
          </span>
          <span className="font-serif text-xl font-semibold tabular-nums">
            {formatPrice(totals.subtotal)}
          </span>
        </button>
      </div>
    </>
  );
}
