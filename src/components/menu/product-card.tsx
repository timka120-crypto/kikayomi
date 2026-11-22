"use client";

import Image from "next/image";
import { Plus } from "lucide-react";
import { QuantityStepper } from "@/components/cart/quantity-stepper";
import { useUI } from "@/components/providers/ui-provider";
import { useCart } from "@/lib/cart/use-cart";
import { cn } from "@/lib/cn";
import { formatPrice } from "@/lib/format";
import { isProductAvailable } from "@/lib/menu";
import type { Product, ProductTag } from "@/types/menu";

const tagLabels: Record<ProductTag, { label: string; className: string }> = {
  hit: { label: "Хит", className: "bg-burgundy text-cream" },
  new: { label: "Новинка", className: "bg-ink text-cream" },
  vegetarian: { label: "Вегетарианское", className: "bg-olive text-white" },
  spicy: { label: "Острое", className: "bg-[#b4532a] text-white" },
};

interface ProductCardProps {
  product: Product;
  /**
   * stacked — vertical card everywhere (home showcase).
   * responsive — compact horizontal row on phones, vertical card from 640px (menu page).
   */
  layout?: "stacked" | "responsive";
  className?: string;
}

export function ProductCard({ product, layout = "stacked", className }: ProductCardProps) {
  const { quantityOf, actions } = useCart();
  const { notify } = useUI();
  const quantity = quantityOf(product.id);
  const available = isProductAvailable(product);
  const row = layout === "responsive";

  const add = () => {
    actions.add(product.id);
    notify({
      title: `«${product.name}» в корзине`,
      description: formatPrice(product.price),
      cartAction: true,
    });
  };

  return (
    <article
      data-testid="product-card"
      data-product-id={product.id}
      className={cn(
        "group relative flex h-full overflow-hidden rounded-card bg-white ring-1 ring-ink/5 transition-[box-shadow,transform] duration-500 ease-out hover:-translate-y-1 hover:shadow-[0_24px_60px_-28px_rgb(37_35_31/0.35)]",
        row ? "flex-row gap-3.5 p-3 sm:flex-col sm:gap-0 sm:p-0" : "flex-col",
        className,
      )}
    >
      <div
        className={cn(
          "relative shrink-0 overflow-hidden bg-cream-deep",
          row
            ? "w-[7.25rem] self-stretch rounded-2xl max-sm:min-h-[8.5rem] sm:aspect-[4/3] sm:w-full sm:rounded-none"
            : "aspect-[4/3] w-full",
        )}
      >
        <Image
          src={product.image.src}
          alt={product.image.alt}
          fill
          sizes={
            row
              ? "(max-width: 640px) 120px, (max-width: 1024px) 50vw, 33vw"
              : "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          }
          className="object-cover transition-transform duration-[1.2s] ease-out group-hover:scale-[1.06]"
        />
        {product.tags && product.tags.length > 0 && (
          <ul
            className={cn(
              "absolute top-3 left-3 flex flex-wrap gap-1.5",
              row && "max-sm:top-2 max-sm:left-2 max-sm:right-2",
            )}
          >
            {product.tags.slice(0, row ? 1 : 2).map((tag) => (
              <li
                key={tag}
                className={cn(
                  "rounded-full px-2.5 py-1 text-[0.68rem] font-bold tracking-wide uppercase shadow-sm",
                  tagLabels[tag].className,
                  row && "max-sm:px-2 max-sm:text-[0.6rem]",
                )}
              >
                {tagLabels[tag].label}
              </li>
            ))}
          </ul>
        )}
        {!available && (
          <div className="absolute inset-0 grid place-items-center bg-ink/55 text-sm font-semibold text-cream">
            Временно нет
          </div>
        )}
      </div>

      <div
        className={cn(
          "flex min-w-0 flex-1 flex-col",
          row ? "py-0.5 pr-0.5 sm:p-5 sm:pt-4" : "p-5 pt-4 sm:p-6 sm:pt-5",
        )}
      >
        {product.italianName && (
          <p
            className={cn(
              "truncate font-serif text-[0.95rem] text-olive-deep italic",
              row && "max-sm:text-[0.82rem]",
            )}
          >
            {product.italianName}
          </p>
        )}
        <h3
          className={cn("font-serif text-[1.55rem] leading-tight text-ink", row && "max-sm:text-[1.25rem]")}
        >
          {product.name}
        </h3>
        <p
          className={cn(
            "mt-2 line-clamp-2 text-sm leading-relaxed text-ink-soft",
            row && "max-sm:mt-1 max-sm:text-[0.8rem] max-sm:leading-snug",
          )}
        >
          {product.description}
        </p>

        <div className={cn("mt-auto flex items-end justify-between gap-3 pt-4", row && "max-sm:pt-2.5")}>
          <div className="min-w-0">
            <p
              className={cn("text-lg font-bold text-ink tabular-nums", row && "max-sm:text-base")}
              data-testid="product-price"
            >
              {formatPrice(product.price)}
            </p>
            {product.portion && <p className="truncate text-xs text-ink-muted">{product.portion}</p>}
          </div>

          {!available ? (
            <span className="text-xs font-semibold text-ink-muted">Нет в наличии</span>
          ) : quantity > 0 ? (
            <QuantityStepper
              value={quantity}
              onChange={(value) => actions.setQuantity(product.id, value)}
              label={product.name}
              tone="solid"
              size={row ? "sm" : "md"}
              className={cn(row && "sm:[&_button]:h-10 sm:[&_button]:w-10")}
            />
          ) : (
            <button
              type="button"
              onClick={add}
              aria-label={`Добавить «${product.name}» в корзину`}
              className={cn(
                "inline-flex shrink-0 items-center justify-center gap-1.5 rounded-full bg-ink font-semibold text-cream transition-[background-color,transform] duration-300 hover:bg-burgundy active:scale-95",
                row ? "h-10 w-10 sm:h-11 sm:w-auto sm:px-5 sm:text-sm" : "h-11 px-5 text-sm",
              )}
            >
              <Plus className="h-4 w-4" strokeWidth={2.4} />
              <span className={cn(row && "max-sm:sr-only")}>В корзину</span>
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
