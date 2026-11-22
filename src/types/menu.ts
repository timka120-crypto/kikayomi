export type CategoryId = "pizza" | "pasta" | "salads" | "starters" | "soups" | "desserts" | "drinks";

export interface MenuCategory {
  id: CategoryId;
  /** Название на русском — показывается в навигации. */
  name: string;
  /** Итальянское название — декоративная подпись. */
  italian: string;
  description: string;
}

export type ProductTag = "hit" | "vegetarian" | "spicy" | "new";

export interface ProductImage {
  /** Путь от /public или абсолютный URL (хост добавить в next.config.ts → images.remotePatterns). */
  src: string;
  alt: string;
}

export interface Product {
  /** Стабильный идентификатор. Используется в корзине и в заказе. */
  id: string;
  categoryId: CategoryId;
  name: string;
  italianName?: string;
  description: string;
  /** Цена в тенге, целое число. */
  price: number;
  /** Вес / объём / размер — свободная строка: «30 см · 520 г». */
  portion?: string;
  image: ProductImage;
  tags?: ProductTag[];
  /** Показывать в блоке «Популярные блюда» на главной. */
  popular?: boolean;
  /** false — позиция временно недоступна (видна, но не добавляется в корзину). */
  available?: boolean;
}
