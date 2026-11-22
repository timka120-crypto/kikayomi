/**
 * ─────────────────────────────────────────────────────────────────────
 *  BEKAKOTAK — настройки сайта
 * ─────────────────────────────────────────────────────────────────────
 *  Все контактные данные, график и условия доставки — здесь.
 *
 *  ⚠️  Значения с «X» и `null` — это ЗАГЛУШКИ. Замените их реальными
 *  данными перед запуском. Пока значение не заполнено, сайт честно
 *  показывает «уточняется» и не делает ссылку кликабельной.
 * ─────────────────────────────────────────────────────────────────────
 */

export const siteConfig = {
  name: "BEKAKOTAK",
  brand: "BekaKotak",
  tagline: "Cucina italiana",
  description:
    "BekaKotak — итальянское кафе в Алматы: пицца, паста, антипасти и десерты. Онлайн-заказ с доставкой и самовывозом.",
  /** Публичный адрес сайта. Задаётся переменной окружения NEXT_PUBLIC_SITE_URL. */
  url: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  locale: "ru_RU",

  address: {
    street: "ул. Розыбакиева, 66",
    city: "Алматы",
    country: "Казахстан",
    countryCode: "KZ",
    /** Строка для поиска на картах. */
    mapQuery: "Розыбакиева 66, Алматы, Казахстан",
  },

  contacts: {
    /** TODO: реальный номер, например "+7 (727) 000-00-00". Пока есть «X» — ссылка не активна. */
    phone: "+7 (XXX) XXX-XX-XX",
    /** TODO: номер WhatsApp только цифрами, например "77010000000". null — кнопка WhatsApp скрыта. */
    whatsapp: null as string | null,
    /** TODO: e-mail для связи (необязательно). */
    email: null as string | null,
  },

  /** TODO: реальный график работы. */
  hours: [{ days: "Ежедневно", time: "XX:XX – XX:XX" }],
  /** TODO: тот же график для поисковиков (schema.org), например ["Mo-Su 10:00-23:00"]. */
  openingHoursSchema: null as string[] | null,

  /** TODO: ссылки на соцсети. Пока url = null, иконка не кликабельна. */
  socials: [
    { id: "instagram", label: "Instagram", url: null as string | null },
    { id: "telegram", label: "Telegram", url: null as string | null },
    { id: "whatsapp", label: "WhatsApp", url: null as string | null },
  ],

  delivery: {
    /**
     * Стоимость доставки в тенге. null — неизвестна: в корзине будет
     * «рассчитает оператор», итоговая сумма показывается без доставки.
     */
    fee: null as number | null,
    /** Сумма заказа, от которой доставка бесплатна. null — не используется. */
    freeFrom: null as number | null,
    /** Минимальная сумма заказа на доставку. null — без ограничения. */
    minOrder: null as number | null,
    /** Время доставки, например "60–90 минут". null — «уточняется». */
    estimatedTime: null as string | null,
    /** Зона доставки, например "в пределах ул. Саина — пр. Достык". null — «уточняется». */
    zone: null as string | null,
  },

  payment: {
    note: "Способ оплаты уточнит оператор при подтверждении заказа. Онлайн-оплата будет подключена позже.",
  },

  map: {
    /**
     * Можно заменить на собственный embed-URL (Google Maps / Яндекс / 2ГИС).
     * По умолчанию карта строится по адресу.
     */
    embedUrl: null as string | null,
  },
} as const;

export const navigation = [
  { href: "/", label: "Главная" },
  { href: "/menu", label: "Меню" },
  { href: "/about", label: "О кафе" },
  { href: "/delivery", label: "Доставка" },
  { href: "/contacts", label: "Контакты" },
] as const;

export type SiteConfig = typeof siteConfig;
