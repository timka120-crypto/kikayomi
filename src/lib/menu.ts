/**
 * Menu repository — the single place the app reads the menu from.
 *
 * Today the data comes from the static file src/data/menu.ts. To move the
 * menu into a database or headless CMS (admin panel), re-implement these
 * functions on top of your data source and keep the same return types.
 */
import { categories, MENU_IS_DEMO, products } from "@/data/menu";
import type { CategoryId, MenuCategory, Product } from "@/types/menu";

const productIndex = new Map(products.map((product) => [product.id, product]));

export const isDemoMenu = MENU_IS_DEMO;

export function getCategories(): MenuCategory[] {
  return categories;
}

export function getProducts(): Product[] {
  return products;
}

export function getProductById(id: string): Product | undefined {
  return productIndex.get(id);
}

export function getProductsByCategory(categoryId: CategoryId): Product[] {
  return products.filter((product) => product.categoryId === categoryId);
}

export function getPopularProducts(limit = 6): Product[] {
  return products.filter((product) => product.popular).slice(0, limit);
}

export function isProductAvailable(product: Product): boolean {
  return product.available !== false;
}
