"use client";

import Link from "next/link";
import { useMemo, useState, useSyncExternalStore } from "react";
import { Check, Copy, PhoneCall } from "lucide-react";
import { deliveryFeeLabel } from "@/components/cart/cart-summary";
import { buttonClasses } from "@/components/ui/button";
import { siteConfig } from "@/config/site";
import { formatPrice } from "@/lib/format";
import { readLastOrderRaw } from "@/lib/orders/client";
import type { OrderConfirmation } from "@/lib/orders/types";

const noopSubscribe = () => () => {};

export function OrderSuccess() {
  const raw = useSyncExternalStore(noopSubscribe, readLastOrderRaw, () => undefined);
  const [copied, setCopied] = useState(false);

  const order = useMemo<OrderConfirmation | null>(() => {
    if (!raw) return null;
    try {
      return JSON.parse(raw) as OrderConfirmation;
    } catch {
      return null;
    }
  }, [raw]);

  // Server render / before hydration.
  if (raw === undefined) {
    return (
      <div className="mx-auto h-[28rem] max-w-2xl animate-pulse rounded-card bg-white/70" aria-busy="true" />
    );
  }

  if (!order) {
    return (
      <div className="mx-auto max-w-xl rounded-card bg-white p-8 text-center ring-1 ring-ink/5 sm:p-12">
        <h1 className="font-serif text-4xl">Заказ не найден</h1>
        <p className="mt-3 text-ink-soft">
          Подтверждение показывается сразу после оформления заказа. Если вы уже сделали заказ — мы свяжемся с
          вами.
        </p>
        <Link href="/menu" className={buttonClasses("primary", "md", "mt-8")}>
          Перейти в меню
        </Link>
      </div>
    );
  }

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(order.orderNumber);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  };

  const isDelivery = order.fulfillment === "delivery";

  return (
    <div className="mx-auto max-w-2xl" data-testid="order-success">
      <div className="relative overflow-hidden rounded-card bg-white p-6 text-center ring-1 ring-ink/5 sm:p-12">
        <div className="mx-auto grid h-20 w-20 animate-pop place-items-center rounded-full bg-olive text-white shadow-[0_18px_40px_-16px_rgb(105_115_75/0.9)]">
          <Check className="h-9 w-9" strokeWidth={2.4} />
        </div>
        <p className="eyebrow mt-8 text-burgundy">Grazie mille!</p>
        <h1 className="mt-3 text-[2.6rem] leading-none sm:text-6xl">Заказ принят</h1>
        <p className="mx-auto mt-4 max-w-md text-lg leading-relaxed text-ink-soft">
          Спасибо, {order.customerName}! Заказ передан в кафе. Мы позвоним вам, чтобы подтвердить детали
          {isDelivery ? " и время доставки" : " и время, когда заказ будет готов"}.
        </p>

        <div className="mx-auto mt-8 inline-flex flex-col items-center rounded-2xl border border-dashed border-burgundy/35 bg-burgundy-soft/40 px-6 py-4">
          <span className="text-xs font-semibold tracking-[0.2em] text-ink-muted uppercase">
            Номер заказа
          </span>
          <span className="mt-1 flex items-center gap-2">
            <span
              className="font-mono text-2xl font-bold tracking-wider text-burgundy sm:text-3xl"
              data-testid="order-number"
            >
              {order.orderNumber}
            </span>
            <button
              type="button"
              onClick={copy}
              className="grid h-9 w-9 place-items-center rounded-full text-burgundy hover:bg-burgundy-soft"
              aria-label="Скопировать номер заказа"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </button>
          </span>
        </div>

        <div className="mt-10 text-left">
          <h2 className="font-serif text-2xl">{isDelivery ? "Доставка" : "Самовывоз"}</h2>
          <ul className="mt-3 divide-y divide-ink/10 border-y border-ink/10">
            {order.items.map((item) => (
              <li key={item.id} className="flex items-center justify-between gap-4 py-3 text-[0.95rem]">
                <span className="min-w-0">
                  {item.name} <span className="text-ink-muted">× {item.quantity}</span>
                </span>
                <span className="font-semibold tabular-nums">{formatPrice(item.total)}</span>
              </li>
            ))}
          </ul>
          <dl className="mt-4 space-y-2 text-[0.95rem]">
            <div className="flex justify-between gap-4">
              <dt className="text-ink-soft">Сумма заказа</dt>
              <dd className="font-semibold tabular-nums">{formatPrice(order.totals.subtotal)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-ink-soft">Доставка</dt>
              <dd className="font-semibold">
                {deliveryFeeLabel(order.totals.deliveryFeeStatus, order.totals.deliveryFee)}
              </dd>
            </div>
            <div className="flex items-baseline justify-between gap-4 pt-2">
              <dt className="font-serif text-xl">
                {order.totals.totalIsFinal ? "Итого" : "Итого без доставки"}
              </dt>
              <dd className="font-serif text-2xl font-semibold text-burgundy tabular-nums">
                {formatPrice(order.totals.total)}
              </dd>
            </div>
          </dl>
          <p className="mt-6 flex gap-2.5 rounded-2xl bg-cream p-4 text-sm leading-relaxed text-ink-soft">
            <PhoneCall className="mt-0.5 h-4 w-4 shrink-0 text-olive" />
            {siteConfig.payment.note}
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
        <Link href="/menu" className={buttonClasses("primary", "lg")}>
          Вернуться в меню
        </Link>
        <Link href="/" className={buttonClasses("outline", "lg")}>
          На главную
        </Link>
      </div>
    </div>
  );
}
