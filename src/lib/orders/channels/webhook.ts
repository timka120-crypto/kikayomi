import "server-only";
import { createHmac } from "node:crypto";
import type { OrderChannel } from "./types";

/**
 * Generic JSON webhook — connect a CRM, POS (iiko, r_keeper, Poster…),
 * Google Sheets via Make / n8n / Zapier, or your own backend.
 *
 * Env:
 *   ORDER_WEBHOOK_URL    — HTTPS endpoint that receives POST { event, order }
 *   ORDER_WEBHOOK_SECRET — optional; adds header
 *                          X-BekaKotak-Signature: sha256=<HMAC of the raw body>
 */
export const webhookChannel: OrderChannel = {
  id: "webhook",

  isConfigured() {
    return Boolean(process.env.ORDER_WEBHOOK_URL);
  },

  async send(order) {
    const body = JSON.stringify({ event: "order.created", order });
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "User-Agent": "BekaKotak-Orders/1.0",
    };

    const secret = process.env.ORDER_WEBHOOK_SECRET;
    if (secret) {
      headers["X-BekaKotak-Signature"] = `sha256=${createHmac("sha256", secret).update(body).digest("hex")}`;
    }

    const response = await fetch(process.env.ORDER_WEBHOOK_URL!, {
      method: "POST",
      headers,
      body,
      signal: AbortSignal.timeout(10_000),
    });

    if (!response.ok) {
      throw new Error(`Webhook responded with ${response.status}`);
    }
  },
};
