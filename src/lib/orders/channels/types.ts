import type { Order } from "../types";

/**
 * An order channel delivers a confirmed order to the restaurant:
 * Telegram chat, CRM / POS webhook, database, WhatsApp Business API, …
 *
 * To add a new channel: implement this interface in a new file and register
 * it in ./index.ts. An order is accepted when at least one configured
 * channel delivers it successfully.
 */
export interface OrderChannel {
  /** Short id for logs, e.g. "telegram". */
  id: string;
  /** True when the required environment variables are present. */
  isConfigured(): boolean;
  /** Must throw on failure. */
  send(order: Order): Promise<void>;
}
