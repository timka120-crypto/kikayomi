import { Banknote, Clock3, MapPinned, ShoppingBasket, type LucideIcon } from "lucide-react";
import { siteConfig } from "@/config/site";
import { formatPrice } from "@/lib/format";
import { cn } from "@/lib/cn";

interface Term {
  icon: LucideIcon;
  label: string;
  value: string | null;
}

function getTerms(): Term[] {
  const { fee, freeFrom, minOrder, estimatedTime, zone } = siteConfig.delivery;
  return [
    {
      icon: Banknote,
      label: "Стоимость доставки",
      value:
        fee === null
          ? null
          : fee === 0
            ? "Бесплатно"
            : `${formatPrice(fee)}${freeFrom !== null ? ` · бесплатно от ${formatPrice(freeFrom)}` : ""}`,
    },
    {
      icon: ShoppingBasket,
      label: "Минимальный заказ",
      value: minOrder === null ? null : formatPrice(minOrder),
    },
    { icon: Clock3, label: "Время доставки", value: estimatedTime },
    { icon: MapPinned, label: "Зона доставки", value: zone },
  ];
}

/** Delivery conditions from config; unknown values render as «уточняется». */
export function DeliveryTerms({ className, columns = 2 }: { className?: string; columns?: 1 | 2 }) {
  const terms = getTerms();
  return (
    <dl className={cn("grid gap-3", columns === 2 && "sm:grid-cols-2", className)}>
      {terms.map(({ icon: Icon, label, value }) => (
        <div key={label} className="flex gap-3.5 rounded-2xl bg-white p-4 ring-1 ring-ink/5">
          <Icon className="mt-0.5 h-5 w-5 shrink-0 text-olive" strokeWidth={1.7} />
          <div className="min-w-0">
            <dt className="text-xs font-semibold tracking-wide text-ink-muted uppercase">{label}</dt>
            <dd className={cn("mt-1 font-semibold", value ? "text-ink" : "text-ink-soft")}>
              {value ?? "Уточняется"}
            </dd>
          </div>
        </div>
      ))}
    </dl>
  );
}

export function hasUnknownDeliveryTerms(): boolean {
  return getTerms().some((term) => term.value === null);
}
