import "server-only";
import { appendFile, mkdir } from "node:fs/promises";
import path from "node:path";
import type { OrderChannel } from "./types";

/**
 * Appends every order as one JSON line to a local file.
 *
 * Meant for local development and end-to-end testing, or a single VPS where
 * staff read the file. NOT suitable for serverless hosting (Vercel etc.),
 * where the filesystem is temporary — use Telegram / webhook / a database there.
 *
 * Env:
 *   ORDERS_LOCAL_FILE=true
 *   ORDERS_LOCAL_FILE_PATH — optional, default ".data/orders.jsonl"
 */
export const localFileChannel: OrderChannel = {
  id: "local-file",

  isConfigured() {
    return process.env.ORDERS_LOCAL_FILE === "true";
  },

  async send(order) {
    const file = path.resolve(
      /* turbopackIgnore: true */ process.cwd(),
      process.env.ORDERS_LOCAL_FILE_PATH || ".data/orders.jsonl",
    );
    await mkdir(path.dirname(file), { recursive: true });
    await appendFile(file, JSON.stringify(order) + "\n", "utf8");
  },
};
