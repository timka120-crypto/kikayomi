import { readFile } from "node:fs/promises";
import path from "node:path";
import { expect, test } from "@playwright/test";
import { E2E_ORDERS_FILE } from "../../playwright.config";
import { addFromMenu, clearStorage, expectCartCount, parsePrice, productCard } from "./helpers";

async function readOrders(): Promise<Array<Record<string, unknown> & { number: string }>> {
  try {
    const raw = await readFile(path.resolve(E2E_ORDERS_FILE), "utf8");
    return raw
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line));
  } catch {
    return [];
  }
}

test.beforeEach(async ({ page }) => {
  await clearStorage(page);
});

test("доставка: заказ оформляется, номер выдаётся, корзина очищается", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "pizza-pepperoni"); // 3 700
  await productCard(page, "pizza-pepperoni")
    .getByRole("button", { name: /Увеличить/ })
    .click(); // ×2
  await addFromMenu(page, "drink-lemonade"); // 1 200
  await expectCartCount(page, 3);

  await page.goto("/checkout");
  await expect(page.getByTestId("ordering-disabled-notice")).toHaveCount(0);
  expect(parsePrice(await page.getByTestId("checkout-form").getByTestId("summary-total").textContent())).toBe(
    2 * 3700 + 1200,
  );

  await page.locator("#checkout-name").fill("Данияр");
  await page.locator("#checkout-phone").fill("7771234567");
  await page.locator("#checkout-street").fill("ул. Розыбакиева");
  await page.locator("#checkout-house").fill("100");
  await page.locator("#checkout-apartment").fill("12");
  await page.locator("#checkout-entrance").fill("2");
  await page.locator("#checkout-floor").fill("4");
  await page.locator("#checkout-comment").fill("Домофон 12");
  await page.getByTestId("confirm-order").click();

  await expect(page).toHaveURL(/\/checkout\/success$/);
  await expect(page.getByTestId("order-success")).toBeVisible();
  const orderNumber = (await page.getByTestId("order-number").textContent())!.trim();
  expect(orderNumber).toMatch(/^BK-\d{6}-[2-9A-HJKMNP-Z]{5}$/);
  await expectCartCount(page, 0);

  // The order really reached the order channel, priced on the server.
  const order = (await readOrders()).find((o) => o.number === orderNumber);
  expect(order).toBeTruthy();
  expect(order).toMatchObject({
    fulfillment: "delivery",
    customer: { name: "Данияр", phone: "+77771234567" },
    address: { street: "ул. Розыбакиева", house: "100", apartment: "12", entrance: "2", floor: "4" },
    comment: "Домофон 12",
    totals: { subtotal: 8600, deliveryFee: null, totalIsFinal: false },
  });

  // Success page survives a reload (sessionStorage)
  await page.reload();
  await expect(page.getByTestId("order-number")).toHaveText(orderNumber);

  // Contact details are remembered on this device for next time
  await page.goto("/menu");
  await addFromMenu(page, "dessert-gelato");
  await page.goto("/checkout");
  await expect(page.locator("#checkout-name")).toHaveValue("Данияр");
  await expect(page.locator("#checkout-phone")).toHaveValue("(777) 123-45-67");
});

test("самовывоз: адрес не требуется", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "dessert-tiramisu");
  await page.goto("/checkout");
  await page.locator('label:has([data-testid="fulfillment-pickup"])').click();
  await expect(page.getByTestId("checkout-form").getByTestId("summary-delivery")).toHaveText(
    "Самовывоз — 0 ₸",
  );
  await page.locator("#checkout-name").fill("Алия");
  await page.locator("#checkout-phone").fill("7051112233");
  await page.getByTestId("confirm-order").click();
  await expect(page).toHaveURL(/\/checkout\/success$/);
  const orderNumber = (await page.getByTestId("order-number").textContent())!.trim();
  const order = (await readOrders()).find((o) => o.number === orderNumber);
  expect(order).toMatchObject({
    fulfillment: "pickup",
    address: null,
    totals: { total: 2200, totalIsFinal: true },
  });
});

test("API: цены считаются на сервере, неизвестные блюда отклоняются, повторная отправка не дублирует заказ", async ({
  request,
}) => {
  const base = {
    customer: { name: "Тест", phone: "+77011234567" },
    fulfillment: "pickup",
    address: { street: "", house: "", apartment: "", entrance: "", floor: "" },
    comment: "",
  };

  const unknown = await request.post("/api/orders", {
    data: {
      ...base,
      clientOrderId: `e2e-unknown-${Date.now()}`,
      items: [{ id: "pizza-hawaii", quantity: 1 }],
    },
  });
  expect(unknown.status()).toBe(409);
  expect((await unknown.json()).code).toBe("ITEMS_UNAVAILABLE");

  const clientOrderId = `e2e-idem-${Date.now()}`;
  const payload = {
    ...base,
    clientOrderId,
    // A client-side "price" field is ignored — only id and quantity are accepted.
    items: [{ id: "drink-espresso", quantity: 2, price: 1 }],
  };
  const first = await request.post("/api/orders", { data: payload });
  expect(first.status()).toBe(201);
  const firstBody = await first.json();
  expect(firstBody.totals.total).toBe(1400);

  const second = await request.post("/api/orders", { data: payload });
  expect(second.status()).toBe(201);
  expect((await second.json()).orderNumber).toBe(firstBody.orderNumber);

  const matching = (await readOrders()).filter((o) => o.number === firstBody.orderNumber);
  expect(matching).toHaveLength(1);
});
