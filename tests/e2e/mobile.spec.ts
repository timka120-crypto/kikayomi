import { devices, expect, test } from "@playwright/test";
import { addFromMenu, clearStorage, expectCartCount, visible } from "./helpers";

const PATHS = ["/", "/menu", "/about", "/delivery", "/contacts", "/cart", "/checkout"];
const DEVICES = [
  "iPhone SE",
  "iPhone 13",
  "Pixel 7",
  "Galaxy S9+",
  "iPad Mini",
  "iPad Pro 11 landscape",
] as const;

test.describe("адаптивность: нет горизонтального скролла", () => {
  for (const name of DEVICES) {
    test(name, async ({ browser }) => {
      const { defaultBrowserType: _ignored, ...device } = devices[name];
      void _ignored;
      const context = await browser.newContext(device);
      const page = await context.newPage();
      for (const path of PATHS) {
        await page.goto(path);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        expect(overflow, `${name} ${path}`).toBeLessThanOrEqual(0);
      }
      await context.close();
    });
  }
});

test("мобильное меню навигации", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Открыть меню" }).click();
  const mobileNav = page.getByRole("navigation", { name: "Мобильная навигация" });
  await expect(mobileNav).toBeVisible();
  await mobileNav.getByRole("link", { name: /Доставка/ }).click();
  await expect(page).toHaveURL(/\/delivery$/);
  await expect(mobileNav).toBeHidden();
});

test("нижняя панель корзины открывает корзину в один тап", async ({ page }) => {
  await clearStorage(page);
  await page.goto("/menu");
  await expect(page.getByTestId("mobile-cart-bar")).toHaveCount(0);
  await addFromMenu(page, "pizza-verde");
  await expectCartCount(page, 1);
  await page.getByTestId("mobile-cart-bar").click();
  await expect(page.getByTestId("cart-drawer")).toBeVisible();
  await page.getByTestId("cart-drawer").getByTestId("go-checkout").click();
  await expect(page).toHaveURL(/\/checkout$/);
  await expect(page.getByTestId("mobile-cart-bar")).toHaveCount(0);
  await expect(visible(page, "#checkout-name")).toBeVisible();
});
