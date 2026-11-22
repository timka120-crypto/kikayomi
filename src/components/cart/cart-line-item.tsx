"use client";

import Image from "next/image";
import { Trash2 } from "lucide-react";
import type { CartLine } from "@/lib/cart/use-cart";
import { cartActions } from "@/lib/cart/store";
import { formatPrice } from "@/lib/format";
import { QuantityStepper } from "./quantity-stepper";

export function CartLineItem({ line }: { line: CartLine }) {
  const { product, quantity, lineTotal } = line;
  return (
    <li data-testid="cart-line" data-product-id={product.id} className="flex gap-4 py-5">
      <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-2xl bg-cream-deep sm:h-24 sm:w-24">
        <Image src={product.image.src} alt={product.image.alt} fill sizes="96px" className="object-cover" />
      </div>
      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="font-serif text-xl leading-tight text-ink">{product.name}</h3>
            <p className="mt-0.5 text-xs text-ink-muted">
              {formatPrice(product.price)} за шт.{product.portion ? ` · ${product.portion}` : ""}
            </p>
          </div>
          <button
            type="button"
            onClick={() => cartActions.remove(product.id)}
            className="-mt-1 -mr-1 grid h-9 w-9 shrink-0 place-items-center rounded-full text-ink-muted transition-colors hover:bg-burgundy-soft hover:text-burgundy"
            aria-label={`Удалить «${product.name}» из корзины`}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
        <div className="mt-auto flex items-center justify-between gap-3 pt-3">
          <QuantityStepper
            value={quantity}
            onChange={(value) => cartActions.setQuantity(product.id, value)}
            label={product.name}
            size="sm"
          />
          <p className="font-semibold text-ink tabular-nums" data-testid="cart-line-total">
            {formatPrice(lineTotal)}
          </p>
        </div>
      </div>
    </li>
  );
}
