import { defineConfig, devices } from "@playwright/test";

/**
 * End-to-end tests run against the production build (`npm run build` first).
 *
 * Two servers are started from the same build:
 *  - :3100 — default configuration, no order channel (checks the honest
 *            «приём заказов не подключён» path, cart must be kept);
 *  - :3101 — ORDERS_LOCAL_FILE=true, orders are written to .data/e2e-orders.jsonl
 *            (checks the full order flow end to end).
 */
const DEFAULT_PORT = 3100;
const ORDERING_PORT = 3101;
export const E2E_ORDERS_FILE = ".data/e2e-orders.jsonl";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  use: {
    trace: "off",
    locale: "ru-RU",
  },
  projects: [
    {
      name: "desktop",
      testIgnore: /(ordering-enabled|mobile)\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], baseURL: `http://localhost:${DEFAULT_PORT}` },
    },
    {
      name: "mobile",
      testMatch: /(mobile|cart)\.spec\.ts/,
      use: { ...devices["Pixel 7"], baseURL: `http://localhost:${DEFAULT_PORT}` },
    },
    {
      name: "ordering-enabled",
      testMatch: /ordering-enabled\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], baseURL: `http://localhost:${ORDERING_PORT}` },
    },
  ],
  webServer: [
    {
      command: `npx next start -p ${DEFAULT_PORT}`,
      url: `http://localhost:${DEFAULT_PORT}`,
      reuseExistingServer: !process.env.CI,
      env: { ORDERS_LOCAL_FILE: "", TELEGRAM_BOT_TOKEN: "", ORDER_WEBHOOK_URL: "" },
    },
    {
      command: `npx next start -p ${ORDERING_PORT}`,
      url: `http://localhost:${ORDERING_PORT}`,
      reuseExistingServer: !process.env.CI,
      env: {
        ORDERS_LOCAL_FILE: "true",
        ORDERS_LOCAL_FILE_PATH: E2E_ORDERS_FILE,
        TELEGRAM_BOT_TOKEN: "",
        ORDER_WEBHOOK_URL: "",
      },
    },
  ],
});
