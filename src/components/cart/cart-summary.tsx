import { Info } from "lucide-react";
import { formatPrice } from "@/lib/format";
import type { DeliveryFeeStatus, OrderTotals } from "@/lib/pricing";
import { cn } from "@/lib/cn";

export function deliveryFeeLabel(status: DeliveryFeeStatus, fee: number | null): string {
  switch (status) {
    case "pickup":
      return "Самовывоз — 0 ₸";
    case "free":
      return "Бесплатно";
    case "fixed":
      return formatPrice(fee ?? 0);
    case "unknown":
      return "Рассчитает оператор";
  }
}

interface CartSummaryProps {
  totals: OrderTotals;
  className?: string;
  tone?: "plain" | "card";
}

export function CartSummary({ totals, className, tone = "plain" }: CartSummaryProps) {
  return (
    <div className={cn(tone === "card" && "rounded-card bg-white p-5 ring-1 ring-ink/5 sm:p-6", className)}>
      <dl className="space-y-2.5 text-[0.95rem]">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-ink-soft">Сумма заказа</dt>
          <dd className="font-semibold tabular-nums" data-testid="summary-subtotal">
            {formatPrice(totals.subtotal)}
          </dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-ink-soft">Доставка</dt>
          <dd
            className={cn(
              "text-right font-semibold",
              totals.deliveryFeeStatus === "unknown" && "text-olive-deep",
            )}
            data-testid="summary-delivery"
          >
            {deliveryFeeLabel(totals.deliveryFeeStatus, totals.deliveryFee)}
          </dd>
        </div>
        <div className="flex items-baseline justify-between gap-4 border-t border-dashed border-ink/20 pt-3.5">
          <dt className="font-serif text-xl text-ink">
            {totals.totalIsFinal ? "Итого" : "Итого без доставки"}
          </dt>
          <dd
            className="font-serif text-[1.75rem] leading-none font-semibold text-burgundy tabular-nums"
            data-testid="summary-total"
          >
            {formatPrice(totals.total)}
          </dd>
        </div>
      </dl>
      {!totals.totalIsFinal && (
        <p className="mt-3 flex gap-2 text-xs leading-relaxed text-ink-muted">
          <Info className="mt-px h-3.5 w-3.5 shrink-0" />
          Стоимость доставки зависит от адреса — оператор сообщит её при подтверждении заказа.
        </p>
      )}
    </div>
  );
}
