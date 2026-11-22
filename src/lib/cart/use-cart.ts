"use client";

import { useMemo, useSyncExternalStore } from "react";
import { getProductById, isProductAvailable } from "@/lib/menu";
import { calculateTotals, type OrderTotals } from "@/lib/pricing";
import type { Product } from "@/types/menu";
import { cartActions, getServerSnapshot, getSnapshot, subscribe, type CartState } from "./store";

export interface CartLine {
  product: Product;
  quantity: number;
  lineTotal: number;
}

export interface UseCart {
  hydrated: boolean;
  lines: CartLine[];
  /** Total number of portions in the cart. */
  count: number;
  fulfillment: CartState["fulfillment"];
  totals: OrderTotals;
  quantityOf: (id: string) => number;
  actions: typeof cartActions;
}

export function useCart(): UseCart {
  const state = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  return useMemo(() => {
    const lines: CartLine[] = [];
    for (const item of state.items) {
      const product = getProductById(item.id);
      // Dishes removed from the menu or temporarily unavailable drop out of the cart.
      if (!product || !isProductAvailable(product)) continue;
      lines.push({ product, quantity: item.quantity, lineTotal: product.price * item.quantity });
    }
    const count = lines.reduce((sum, line) => sum + line.quantity, 0);
    const totals = calculateTotals(
      lines.map((line) => ({ price: line.product.price, quantity: line.quantity })),
      state.fulfillment,
    );
    const quantities = new Map(lines.map((line) => [line.product.id, line.quantity]));

    return {
      hydrated: state.hydrated,
      lines,
      count,
      fulfillment: state.fulfillment,
      totals,
      quantityOf: (id: string) => quantities.get(id) ?? 0,
      actions: cartActions,
    };
  }, [state]);
}
