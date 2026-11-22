/**
 * Order pricing. Pure functions shared by the browser (cart, checkout) and
 * the server (order API recomputes everything — client totals are never trusted).
 */
import { siteConfig } from "@/config/site";

export type FulfillmentMethod = "delivery" | "pickup";

export interface PricedLine {
  price: number;
  quantity: number;
}

export interface DeliverySettings {
  fee: number | null;
  freeFrom: number | null;
  minOrder: number | null;
}

export type DeliveryFeeStatus = "pickup" | "free" | "fixed" | "unknown";

export interface OrderTotals {
  subtotal: number;
  /** null — стоимость доставки неизвестна и будет сообщена оператором. */
  deliveryFee: number | null;
  deliveryFeeStatus: DeliveryFeeStatus;
  total: number;
  /** false — итог не включает доставку (её стоимость ещё неизвестна). */
  totalIsFinal: boolean;
  /** Сколько не хватает до минимальной суммы доставки (0 — достаточно). */
  minOrderShortfall: number;
}

export const MAX_QUANTITY_PER_ITEM = 50;

export function defaultDeliverySettings(): DeliverySettings {
  const { fee, freeFrom, minOrder } = siteConfig.delivery;
  return { fee, freeFrom, minOrder };
}

export function calculateTotals(
  lines: PricedLine[],
  method: FulfillmentMethod,
  settings: DeliverySettings = defaultDeliverySettings(),
): OrderTotals {
  const subtotal = lines.reduce((sum, line) => sum + line.price * line.quantity, 0);

  if (method === "pickup") {
    return {
      subtotal,
      deliveryFee: 0,
      deliveryFeeStatus: "pickup",
      total: subtotal,
      totalIsFinal: true,
      minOrderShortfall: 0,
    };
  }

  const minOrderShortfall =
    settings.minOrder !== null && subtotal < settings.minOrder ? settings.minOrder - subtotal : 0;

  if (settings.freeFrom !== null && subtotal >= settings.freeFrom) {
    return {
      subtotal,
      deliveryFee: 0,
      deliveryFeeStatus: "free",
      total: subtotal,
      totalIsFinal: true,
      minOrderShortfall,
    };
  }

  if (settings.fee !== null) {
    return {
      subtotal,
      deliveryFee: settings.fee,
      deliveryFeeStatus: "fixed",
      total: subtotal + settings.fee,
      totalIsFinal: true,
      minOrderShortfall,
    };
  }

  return {
    subtotal,
    deliveryFee: null,
    deliveryFeeStatus: "unknown",
    total: subtotal,
    totalIsFinal: false,
    minOrderShortfall,
  };
}
