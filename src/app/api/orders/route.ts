import { getOrderingStatus } from "@/lib/orders/channels";
import { createOrder, type CreateOrderResult } from "@/lib/orders/create-order";
import { checkRateLimit, once } from "@/lib/orders/guard";
import { orderRequestSchema, toFieldErrors } from "@/lib/orders/schema";
import type { OrderErrorResponse } from "@/lib/orders/types";

function error(status: number, body: OrderErrorResponse) {
  return Response.json(body, { status, headers: { "Cache-Control": "no-store" } });
}

function clientKey(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  return forwarded?.split(",")[0]?.trim() || request.headers.get("x-real-ip") || "unknown";
}

/**
 * POST /api/orders — accept an order from the checkout page.
 *
 * 201 → { orderNumber, createdAt, items, totals, … }
 * 422 → validation error (fieldErrors), 409 → unavailable dishes,
 * 503 → no order channel configured yet, 502 → channels failed, 429 → rate limit.
 */
export async function POST(request: Request) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return error(400, { code: "BAD_REQUEST", message: "Некорректный запрос." });
  }

  const parsed = orderRequestSchema.safeParse(payload);
  if (!parsed.success) {
    return error(422, {
      code: "VALIDATION_ERROR",
      message: "Проверьте правильность заполнения формы.",
      fieldErrors: toFieldErrors(parsed.error),
    });
  }

  // Honeypot filled → bot.
  if (parsed.data.website) {
    return error(400, { code: "BAD_REQUEST", message: "Некорректный запрос." });
  }

  if (!getOrderingStatus().enabled) {
    return error(503, {
      code: "ORDERS_NOT_CONFIGURED",
      message:
        "Онлайн-приём заказов ещё не подключён. Ваша корзина сохранена — пожалуйста, оформите заказ по телефону.",
    });
  }

  if (!checkRateLimit(clientKey(request))) {
    return error(429, {
      code: "RATE_LIMITED",
      message: "Слишком много заказов за короткое время. Попробуйте через несколько минут.",
    });
  }

  let result: CreateOrderResult;
  try {
    result = await once(
      parsed.data.clientOrderId,
      () => createOrder(parsed.data),
      (value) => value.ok,
    );
  } catch (cause) {
    console.error("[orders] unexpected error", cause);
    return error(500, {
      code: "DELIVERY_FAILED",
      message: "Что-то пошло не так. Корзина сохранена — попробуйте ещё раз.",
    });
  }

  if (!result.ok) return error(result.status, result.error);

  return Response.json(result.confirmation, {
    status: 201,
    headers: { "Cache-Control": "no-store" },
  });
}
