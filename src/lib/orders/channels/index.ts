import "server-only";
import type { Order } from "../types";
import { localFileChannel } from "./local-file";
import { telegramChannel } from "./telegram";
import type { OrderChannel } from "./types";
import { webhookChannel } from "./webhook";

/** Register new channels (database, WhatsApp Business API, e-mail…) here. */
const channels: OrderChannel[] = [telegramChannel, webhookChannel, localFileChannel];

export function getConfiguredChannels(): OrderChannel[] {
  return channels.filter((channel) => channel.isConfigured());
}

export interface OrderingStatus {
  /** At least one real order channel is configured on the server. */
  enabled: boolean;
  channels: string[];
}

export function getOrderingStatus(): OrderingStatus {
  const configured = getConfiguredChannels().map((channel) => channel.id);
  return { enabled: configured.length > 0, channels: configured };
}

export interface DispatchResult {
  delivered: string[];
  failed: { channel: string; error: string }[];
}

/** Sends the order to every configured channel in parallel. */
export async function dispatchOrder(order: Order): Promise<DispatchResult> {
  const active = getConfiguredChannels();
  const results = await Promise.allSettled(active.map((channel) => channel.send(order)));

  const delivered: string[] = [];
  const failed: DispatchResult["failed"] = [];
  results.forEach((result, index) => {
    const id = active[index].id;
    if (result.status === "fulfilled") {
      delivered.push(id);
    } else {
      const error = result.reason instanceof Error ? result.reason.message : String(result.reason);
      failed.push({ channel: id, error });
      console.error(`[orders] channel "${id}" failed for ${order.number}: ${error}`);
    }
  });

  return { delivered, failed };
}
