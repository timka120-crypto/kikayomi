import { expect, test } from "@playwright/test";
import { addFromMenu, clearStorage, expectCartCount } from "./helpers";

test.beforeEach(async ({ page }) => {
  await clearStorage(page);
});

test("пустая корзина на странице оформления", async ({ page }) => {
  await page.goto("/checkout");
  await expect(page.getByRole("main").getByText("Корзина пока пуста")).toBeVisible();
  await page.getByRole("main").getByRole("link", { name: "Перейти в меню" }).click();
  await expect(page).toHaveURL(/\/menu$/);
});

test("валидация формы и маска телефона", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "pizza-funghi");
  await page.goto("/checkout");

  await page.getByTestId("confirm-order").click();
  await expect(page.getByText("Укажите имя — минимум 2 символа")).toBeVisible();
  await expect(page.getByText(/Введите номер полностью/)).toBeVisible();
  await expect(page.getByText("Укажите улицу или микрорайон")).toBeVisible();
  await expect(page.getByText("Укажите номер дома")).toBeVisible();
  // Focus moves to the first invalid field
  await expect(page.locator("#checkout-name")).toBeFocused();

  const phone = page.locator("#checkout-phone");
  await phone.fill("87011234567");
  await expect(phone).toHaveValue("(701) 123-45-67");

  // Pickup removes the address requirement
  await page.locator('label:has([data-testid="fulfillment-pickup"])').click();
  await expect(page.getByText("Укажите номер дома")).toHaveCount(0);
  await expect(page.locator("#checkout-house")).toHaveCount(0);
});

test("без подключённой системы заказов: честное сообщение, корзина не очищается", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "pasta-bolognese");
  await addFromMenu(page, "salad-caesar");
  await page.goto("/checkout");
  await expect(page.getByTestId("ordering-disabled-notice")).toBeVisible();

  await page.locator("#checkout-name").fill("Айгерим");
  await page.locator("#checkout-phone").fill("7011234567");
  await page.locator("#checkout-street").fill("ул. Абая");
  await page.locator("#checkout-house").fill("10");
  await page.getByTestId("confirm-order").click();

  const error = page.getByTestId("checkout-error");
  await expect(error).toBeVisible();
  await expect(error).toHaveAttribute("data-error-code", "ORDERS_NOT_CONFIGURED");
  await expect(page).toHaveURL(/\/checkout$/);
  await expectCartCount(page, 2);
});

test("API: валидация и подтверждение без каналов возвращает 503", async ({ request }) => {
  const bad = await request.post("/api/orders", { data: { items: [] } });
  expect(bad.status()).toBe(422);
  expect((await bad.json()).code).toBe("VALIDATION_ERROR");

  const valid = await request.post("/api/orders", {
    data: {
      clientOrderId: "test-0000-0001",
      customer: { name: "Тест", phone: "+77011234567" },
      fulfillment: "pickup",
      address: { street: "", house: "", apartment: "", entrance: "", floor: "" },
      comment: "",
      items: [{ id: "pizza-margherita", quantity: 1 }],
    },
  });
  expect(valid.status()).toBe(503);
  expect((await valid.json()).code).toBe("ORDERS_NOT_CONFIGURED");
});
