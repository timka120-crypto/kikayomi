import { expect, test } from "@playwright/test";
import { visible } from "./helpers";

const PAGES = [
  { path: "/", h1: /Вкус настоящей/ },
  { path: "/menu", h1: /Наше меню/ },
  { path: "/about", h1: /О кафе/ },
  { path: "/delivery", h1: /Доставка/ },
  { path: "/contacts", h1: /Как нас найти/ },
  { path: "/cart", h1: /Корзина/ },
  { path: "/checkout", h1: /Оформление/ },
];

test.describe("Страницы", () => {
  for (const { path, h1 } of PAGES) {
    test(`${path} открывается без ошибок, все изображения загружены`, async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("console", (message) => {
        // External map iframe may be blocked in CI sandboxes — ignore third-party noise.
        if (message.type() === "error" && !/google|maps|gstatic/i.test(message.text()))
          errors.push(message.text());
      });

      const response = await page.goto(path);
      expect(response?.status()).toBe(200);
      await expect(visible(page, "h1").first()).toHaveText(h1);

      // Scroll through the page so lazy images load.
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 600) {
          window.scrollTo(0, y);
          await new Promise((r) => setTimeout(r, 40));
        }
      });
      await page.waitForLoadState("networkidle");
      const broken = await page.evaluate(() =>
        Array.from(document.images)
          .filter((img) => img.complete && img.naturalWidth === 0)
          .map((img) => img.currentSrc || img.src),
      );
      expect(broken, "broken images").toEqual([]);
      expect(errors, "console errors").toEqual([]);
    });
  }

  test("404 для несуществующей страницы", async ({ page }) => {
    const response = await page.goto("/no-such-page");
    expect(response?.status()).toBe(404);
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Страница не найдена");
  });
});

test("все внутренние ссылки рабочие", async ({ page, request }) => {
  const links = new Set<string>();
  for (const { path } of PAGES) {
    await page.goto(path);
    const hrefs = await page.$$eval('a[href^="/"]', (anchors) => anchors.map((a) => a.getAttribute("href")!));
    hrefs.forEach((href) => links.add(href.split("#")[0]));
  }
  expect(links.size).toBeGreaterThanOrEqual(5);
  for (const href of links) {
    const response = await request.get(href);
    expect(response.status(), href).toBeLessThan(400);
  }
});

test("внешние ссылки открываются в новой вкладке и безопасны", async ({ page }) => {
  await page.goto("/contacts");
  const external = page.locator('a[href^="http"]');
  const count = await external.count();
  expect(count).toBeGreaterThan(0);
  for (let i = 0; i < count; i++) {
    await expect(external.nth(i)).toHaveAttribute("target", "_blank");
    await expect(external.nth(i)).toHaveAttribute("rel", /noopener/);
  }
});

test("навигация в шапке ведёт на нужные страницы", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Основная навигация" });
  for (const [label, path, h1] of [
    ["Меню", "/menu", /Наше меню/],
    ["О кафе", "/about", /О кафе/],
    ["Доставка", "/delivery", /Доставка/],
    ["Контакты", "/contacts", /Как нас найти/],
    ["Главная", "/", /Вкус настоящей/],
  ] as const) {
    await nav.getByRole("link", { name: label, exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`${path}$`));
    await expect(visible(page, "h1").first()).toHaveText(h1);
  }
});

test("кнопки на главной: «Посмотреть меню», «Заказать доставку», «Заказать»", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Посмотреть меню" }).click();
  await expect(page).toHaveURL(/\/menu$/);

  await page.goto("/");
  await visible(page, "a").filter({ hasText: "Заказать доставку" }).first().click();
  await expect(page).toHaveURL(/\/menu$/); // корзина пуста → меню

  await page.goto("/");
  await page.getByRole("banner").getByRole("link", { name: "Заказать" }).click();
  await expect(page).toHaveURL(/\/menu$/);
});

test("SEO: robots, sitemap, manifest, JSON-LD", async ({ page, request }) => {
  expect((await request.get("/robots.txt")).status()).toBe(200);
  const sitemap = await (await request.get("/sitemap.xml")).text();
  expect(sitemap).toContain("/menu");
  expect((await request.get("/manifest.webmanifest")).status()).toBe(200);
  await page.goto("/");
  const jsonLd = await page.locator('script[type="application/ld+json"]').first().textContent();
  expect(JSON.parse(jsonLd!)).toMatchObject({ "@type": "Restaurant", servesCuisine: "Italian" });
});
