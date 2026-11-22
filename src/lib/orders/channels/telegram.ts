import "server-only";
import { formatPrice } from "@/lib/format";
import { formatPhone } from "@/lib/phone";
import { formatAlmatyDateTime } from "../order-number";
import type { Order } from "../types";
import type { OrderChannel } from "./types";

/**
 * Telegram notifications to the owner / staff chat.
 *
 * Env:
 *   TELEGRAM_BOT_TOKEN — token from @BotFather
 *   TELEGRAM_CHAT_ID   — chat id(s), comma-separated (личный чат, группа или канал)
 */
function escapeHtml(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function formatTelegramMessage(order: Order): string {
  const lines: string[] = [];
  const isDelivery = order.fulfillment === "delivery";

  lines.push(`🍝 <b>Новый заказ ${escapeHtml(order.number)}</b>`);
  lines.push(`🕒 ${formatAlmatyDateTime(order.createdAt)} (Алматы)`);
  lines.push("");
  lines.push(`👤 ${escapeHtml(order.customer.name)}`);
  lines.push(`📞 ${escapeHtml(formatPhone(order.customer.phone))}`);
  lines.push(isDelivery ? "🚚 <b>Доставка</b>" : "🏃 <b>Самовывоз</b>");

  if (isDelivery && order.address) {
    const a = order.address;
    const parts = [
      a.street,
      a.house && `д. ${a.house}`,
      a.apartment && `кв./офис ${a.apartment}`,
      a.entrance && `подъезд ${a.entrance}`,
      a.floor && `этаж ${a.floor}`,
    ].filter(Boolean);
    lines.push(`📍 ${escapeHtml(parts.join(", "))}`);
  }

  lines.push("");
  lines.push("<b>Состав заказа:</b>");
  for (const item of order.items) {
    lines.push(`• ${escapeHtml(item.name)} × ${item.quantity} — ${formatPrice(item.total)}`);
  }
  lines.push("");
  lines.push(`Сумма: ${formatPrice(order.totals.subtotal)}`);
  if (isDelivery) {
    const fee =
      order.totals.deliveryFee === null
        ? "рассчитать и сообщить клиенту"
        : order.totals.deliveryFee === 0
          ? "бесплатно"
          : formatPrice(order.totals.deliveryFee);
    lines.push(`Доставка: ${fee}`);
  }
  lines.push(
    `<b>Итого: ${formatPrice(order.totals.total)}${order.totals.totalIsFinal ? "" : " + доставка"}</b>`,
  );

  if (order.comment) {
    lines.push("");
    lines.push(`💬 ${escapeHtml(order.comment)}`);
  }
  lines.push("");
  lines.push("Оплата: уточнить у клиента при подтверждении.");

  return lines.join("\n");
}

export const telegramChannel: OrderChannel = {
  id: "telegram",

  isConfigured() {
    return Boolean(process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID);
  },

  async send(order) {
    const token = process.env.TELEGRAM_BOT_TOKEN!;
    const chatIds = process.env
      .TELEGRAM_CHAT_ID!.split(",")
      .map((id) => id.trim())
      .filter(Boolean);
    const text = formatTelegramMessage(order);

    const results = await Promise.allSettled(
      chatIds.map(async (chatId) => {
        const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: chatId,
            text,
            parse_mode: "HTML",
            link_preview_options: { is_disabled: true },
          }),
          signal: AbortSignal.timeout(10_000),
        });
        if (!response.ok) {
          const details = await response.text().catch(() => "");
          throw new Error(`Telegram API ${response.status}: ${details.slice(0, 200)}`);
        }
      }),
    );

    if (results.every((result) => result.status === "rejected")) {
      throw (results[0] as PromiseRejectedResult).reason;
    }
  },
};
