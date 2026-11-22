import { expect, test } from "@playwright/test";
import { addFromMenu, clearStorage, expectCartCount, parsePrice, productCard, visible } from "./helpers";

test.beforeEach(async ({ page }) => {
  await clearStorage(page);
});

test("добавление, количество, удаление, сумма и очистка корзины", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "pizza-margherita"); // 3 200
  await expectCartCount(page, 1);

  // Stepper appears on the card — increase to 3
  const stepper = productCard(page, "pizza-margherita").getByRole("group");
  await stepper.getByRole("button", { name: /Увеличить/ }).click();
  await stepper.getByRole("button", { name: /Увеличить/ }).click();
  await expect(stepper).toContainText("3");
  await expectCartCount(page, 3);

  await addFromMenu(page, "dessert-tiramisu"); // 2 200
  await expectCartCount(page, 4);

  await page.getByTestId("header-cart").click();
  const drawer = page.getByTestId("cart-drawer");
  await expect(drawer).toBeVisible();
  await expect(drawer.getByTestId("cart-line")).toHaveCount(2);

  const pizzaLine = drawer.locator('[data-testid="cart-line"][data-product-id="pizza-margherita"]');
  await expect(pizzaLine.getByTestId("cart-line-total")).toHaveText(/9\s?600/);
  expect(parsePrice(await drawer.getByTestId("summary-subtotal").textContent())).toBe(3 * 3200 + 2200);
  await expect(drawer.getByTestId("summary-delivery")).toHaveText("Рассчитает оператор");

  // Decrease in drawer
  await pizzaLine.getByRole("button", { name: /Уменьшить/ }).click();
  expect(parsePrice(await drawer.getByTestId("summary-subtotal").textContent())).toBe(2 * 3200 + 2200);

  // Remove a line
  await drawer
    .locator('[data-testid="cart-line"][data-product-id="dessert-tiramisu"]')
    .getByRole("button", { name: /Удалить/ })
    .click();
  await expect(drawer.getByTestId("cart-line")).toHaveCount(1);
  await expectCartCount(page, 2);

  // Clear with confirmation
  await drawer.getByRole("button", { name: "Очистить корзину" }).click();
  await drawer.getByRole("button", { name: "Да", exact: true }).click();
  await expect(drawer.getByText("Корзина пока пуста")).toBeVisible();
  await expectCartCount(page, 0);

  // Close drawer with Escape
  await page.keyboard.press("Escape");
  await expect(drawer).toBeHidden();
});

test("корзина сохраняется после перезагрузки страницы", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "pasta-carbonara");
  await addFromMenu(page, "drink-cappuccino");
  await expectCartCount(page, 2);
  await page.reload();
  await expectCartCount(page, 2);
  await page.goto("/cart");
  await expect(visible(page, '[data-testid="cart-line"]')).toHaveCount(2);
});

test("уменьшение до нуля убирает блюдо из корзины", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "soup-minestrone");
  await productCard(page, "soup-minestrone")
    .getByRole("button", { name: /Убрать/ })
    .click();
  await expectCartCount(page, 0);
  await expect(productCard(page, "soup-minestrone").getByRole("button", { name: /^Добавить/ })).toBeVisible();
});

test("категории и поиск в меню", async ({ page }) => {
  await page.goto("/menu");
  await expect(visible(page, '[data-testid="product-card"]')).toHaveCount(38);

  await page.getByTestId("category-desserts").click();
  await expect(page).toHaveURL(/category=desserts/);
  await expect(visible(page, '[data-testid="product-card"]')).toHaveCount(5);

  await page.getByTestId("category-all").click();
  const search = visible(page, '[data-testid="menu-search"]');
  await search.fill("тирамису");
  await expect(visible(page, '[data-testid="product-card"]')).toHaveCount(1);
  await expect(productCard(page, "dessert-tiramisu")).toBeVisible();

  await search.fill("пицца с ананасом");
  await expect(page.getByText(/блюд не найдено/)).toBeVisible();
  await page.getByRole("button", { name: "Сбросить поиск" }).click();
  await expect(visible(page, '[data-testid="product-card"]')).toHaveCount(38);

  // Deep link
  await page.goto("/menu?category=drinks");
  await expect(visible(page, '[data-testid="product-card"]')).toHaveCount(6);
});

test("«Заказать» ведёт к оформлению, когда в корзине есть блюда", async ({ page }) => {
  await page.goto("/menu");
  await addFromMenu(page, "starter-antipasti");
  await page.goto("/");
  await page.getByRole("link", { name: "Заказать доставку" }).first().click();
  await expect(page).toHaveURL(/\/checkout$/);
  await expect(page.getByTestId("checkout-items")).toContainText("Антипасти");
});
