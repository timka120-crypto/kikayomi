import { siteConfig } from "@/config/site";

/** A config value still holding a template placeholder ("XX:XX", "+7 (XXX) …"). */
export function isPlaceholder(value: string | null | undefined): boolean {
  return !value || /X{2,}/.test(value);
}

export function getPhone(): { display: string; href: string | null } {
  const phone = siteConfig.contacts.phone;
  if (isPlaceholder(phone)) return { display: phone, href: null };
  return { display: phone, href: `tel:+${phone.replace(/\D/g, "")}` };
}

export function getWhatsAppUrl(text?: string): string | null {
  const number = siteConfig.contacts.whatsapp?.replace(/\D/g, "");
  if (!number) return null;
  const query = text ? `?text=${encodeURIComponent(text)}` : "";
  return `https://wa.me/${number}${query}`;
}

export function hasRealHours(): boolean {
  return siteConfig.hours.every((row) => !isPlaceholder(row.time));
}

export function getFullAddress(): string {
  const { street, city, country } = siteConfig.address;
  return `${street}, ${city}, ${country}`;
}

export function getMapLinks() {
  const q = encodeURIComponent(siteConfig.address.mapQuery);
  return {
    google: `https://www.google.com/maps/search/?api=1&query=${q}`,
    yandex: `https://yandex.kz/maps/?text=${q}`,
    twoGis: `https://2gis.kz/almaty/search/${encodeURIComponent("Розыбакиева 66")}`,
  };
}

export function getMapEmbedUrl(): string {
  return (
    siteConfig.map.embedUrl ??
    `https://maps.google.com/maps?q=${encodeURIComponent(siteConfig.address.mapQuery)}&z=16&hl=ru&output=embed`
  );
}
