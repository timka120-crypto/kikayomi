import { expect, type Page } from "@playwright/test";

/** Visible element only: Next.js keeps recently visited routes in the DOM (hidden) for instant back-navigation. */
export const visible = (page: Page, selector: string) => page.locator(selector).filter({ visible: true });

export const productCard = (page: Page, id: string) =>
  visible(page, `[data-product-id="${id}"][data-testid="product-card"]`);

export async function addFromMenu(page: Page, id: string) {
  await productCard(page, id)
    .getByRole("button", { name: /^Добавить/ })
    .click();
}

export async function expectCartCount(page: Page, count: number) {
  const badge = page.getByTestId("cart-count");
  if (count === 0) await expect(badge).toHaveCount(0);
  else await expect(badge).toHaveText(String(count));
}

/** "12 400 ₸" → 12400 */
export function parsePrice(text: string | null): number {
  return Number((text ?? "").replace(/[^\d]/g, ""));
}

export async function clearStorage(page: Page) {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}
