import "server-only";
import { getProductById, isProductAvailable } from "@/lib/menu";
import { toE164 } from "@/lib/phone";
import { calculateTotals } from "@/lib/pricing";
import { dispatchOrder } from "./channels";
import { generateOrderNumber } from "./order-number";
import type { OrderRequest } from "./schema";
import type { Order, OrderConfirmation, OrderErrorResponse, OrderLine } from "./types";

export type CreateOrderResult =
  | { ok: true; status: 201; confirmation: OrderConfirmation }
  | { ok: false; status: number; error: OrderErrorResponse };

/**
 * Prices the request against the current menu (client prices are ignored),
 * builds the order and hands it to the configured order channels.
 */
export async function createOrder(request: OrderRequest): Promise<CreateOrderResult> {
  const lines: OrderLine[] = [];
  const unavailable: string[] = [];

  // Merge duplicate ids defensively.
  const quantities = new Map<string, number>();
  for (const item of request.items) {
    quantities.set(item.id, (quantities.get(item.id) ?? 0) + item.quantity);
  }

  for (const [id, quantity] of quantities) {
    const product = getProductById(id);
    if (!product || !isProductAvailable(product)) {
      unavailable.push(product?.name ?? id);
      continue;
    }
    lines.push({
      id: product.id,
      name: product.name,
      price: product.price,
      quantity,
      total: product.price * quantity,
    });
  }

  if (unavailable.length > 0) {
    return {
      ok: false,
      status: 409,
      error: {
        code: "ITEMS_UNAVAILABLE",
        message: "Некоторые блюда сейчас недоступны. Обновите корзину и попробуйте снова.",
        unavailableItems: unavailable,
      },
    };
  }

  const totals = calculateTotals(lines, request.fulfillment);

  if (request.fulfillment === "delivery" && totals.minOrderShortfall > 0) {
    return {
      ok: false,
      status: 422,
      error: {
        code: "MIN_ORDER",
        message: "Сумма заказа меньше минимальной для доставки. Добавьте блюда или выберите самовывоз.",
      },
    };
  }

  const order: Order = {
    number: generateOrderNumber(),
    createdAt: new Date().toISOString(),
    source: "website",
    customer: { name: request.customer.name, phone: toE164(request.customer.phone) },
    fulfillment: request.fulfillment,
    address: request.fulfillment === "delivery" ? { ...request.address } : null,
    comment: request.comment,
    items: lines,
    totals: {
      subtotal: totals.subtotal,
      deliveryFee: totals.deliveryFee,
      deliveryFeeStatus: totals.deliveryFeeStatus,
      total: totals.total,
      totalIsFinal: totals.totalIsFinal,
    },
    payment: { method: "to_be_confirmed", status: "unpaid" },
  };

  const result = await dispatchOrder(order);

  if (result.delivered.length === 0) {
    return {
      ok: false,
      status: 502,
      error: {
        code: "DELIVERY_FAILED",
        message: "Не удалось передать заказ в кафе. Корзина сохранена — попробуйте ещё раз через минуту.",
      },
    };
  }

  console.info(`[orders] ${order.number} accepted via ${result.delivered.join(", ")}`);

  return {
    ok: true,
    status: 201,
    confirmation: {
      orderNumber: order.number,
      createdAt: order.createdAt,
      fulfillment: order.fulfillment,
      items: order.items,
      totals: order.totals,
      customerName: order.customer.name,
    },
  };
}
