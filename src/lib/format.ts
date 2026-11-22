const priceFormatter = new Intl.NumberFormat("ru-RU", {
  maximumFractionDigits: 0,
});

/** 12400 → "12 400 ₸" (non-breaking spaces so the price never wraps). */
export function formatPrice(value: number): string {
  return `${priceFormatter.format(value).replace(/\s/g, " ")} ₸`;
}

/** Russian plural forms: pluralize(3, ["позиция", "позиции", "позиций"]). */
export function pluralize(count: number, forms: [string, string, string]): string {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return forms[0];
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return forms[1];
  return forms[2];
}

/** Lower-case + ё→е, for forgiving search. */
export function normalizeSearch(value: string): string {
  return value.toLocaleLowerCase("ru-RU").replace(/ё/g, "е").trim();
}
