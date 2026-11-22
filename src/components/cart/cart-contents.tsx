"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowRight, ShoppingBag } from "lucide-react";
import { buttonClasses } from "@/components/ui/button";
import { useCart } from "@/lib/cart/use-cart";
import { cn } from "@/lib/cn";
import { formatPrice, pluralize } from "@/lib/format";
import { CartLineItem } from "./cart-line-item";
import { CartSummary } from "./cart-summary";

interface CartContentsProps {
  /** Called when the user follows a link out of the cart (closes the drawer). */
  onNavigate?: () => void;
  variant?: "drawer" | "page";
}

export function CartEmpty({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <div className="grid h-20 w-20 place-items-center rounded-full bg-cream-deep text-burgundy">
        <ShoppingBag className="h-8 w-8" strokeWidth={1.5} />
      </div>
      <h3 className="mt-6 font-serif text-3xl">Корзина пока пуста</h3>
      <p className="mt-2 max-w-xs text-sm leading-relaxed text-ink-soft">
        Загляните в меню — пицца, паста и десерты уже ждут.
      </p>
      <Link href="/menu" onClick={onNavigate} className={buttonClasses("primary", "md", "mt-7")}>
        Перейти в меню
        <ArrowRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

export function CartContents({ onNavigate, variant = "drawer" }: CartContentsProps) {
  const { lines, count, totals, actions, hydrated } = useCart();
  const [confirmClear, setConfirmClear] = useState(false);

  if (!hydrated) {
    return <div className="flex-1 animate-pulse p-6" aria-busy="true" aria-label="Загрузка корзины" />;
  }

  if (lines.length === 0) return <CartEmpty onNavigate={onNavigate} />;

  const drawer = variant === "drawer";

  return (
    <div
      className={cn(
        "flex min-h-0 flex-1 flex-col",
        !drawer && "lg:grid lg:grid-cols-[1fr_380px] lg:items-start lg:gap-10",
      )}
    >
      <div className={cn(drawer && "min-h-0 flex-1 overflow-y-auto overscroll-contain px-5 sm:px-7")}>
        <div className="flex items-center justify-between gap-3 pt-2">
          <p className="text-sm text-ink-muted">
            {count} {pluralize(count, ["порция", "порции", "порций"])} на {formatPrice(totals.subtotal)}
          </p>
          {confirmClear ? (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-ink-soft">Очистить?</span>
              <button
                type="button"
                className="rounded-full bg-burgundy px-3 py-1.5 font-semibold text-cream"
                onClick={() => {
                  actions.clear();
                  setConfirmClear(false);
                }}
              >
                Да
              </button>
              <button
                type="button"
                className="rounded-full px-3 py-1.5 font-semibold text-ink hover:bg-ink/5"
                onClick={() => setConfirmClear(false)}
              >
                Нет
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmClear(true)}
              className="text-sm font-semibold text-ink-muted underline-offset-4 transition-colors hover:text-burgundy hover:underline"
            >
              Очистить корзину
            </button>
          )}
        </div>
        <ul className="divide-y divide-ink/10">
          {lines.map((line) => (
            <CartLineItem key={line.product.id} line={line} />
          ))}
        </ul>
      </div>

      <div
        className={cn(
          drawer
            ? "border-t border-ink/10 bg-parchment px-5 pt-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] sm:px-7"
            : "mt-6 lg:sticky lg:top-28 lg:mt-0",
        )}
      >
        <CartSummary totals={totals} tone={drawer ? "plain" : "card"} />
        <Link
          href="/checkout"
          onClick={onNavigate}
          className={buttonClasses("primary", "lg", "mt-5 w-full")}
          data-testid="go-checkout"
        >
          Оформить заказ
          <ArrowRight className="h-4 w-4" />
        </Link>
        {drawer && (
          <Link
            href="/menu"
            onClick={onNavigate}
            className="mt-3 block text-center text-sm font-semibold text-ink-soft underline-offset-4 hover:text-burgundy hover:underline"
          >
            Продолжить выбор
          </Link>
        )}
      </div>
    </div>
  );
}
