import "server-only";

// No 0/O, 1/I/L — easy to read out over the phone.
const ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";

/**
 * Human-friendly unique order number: BK-261122-7KQ3M
 * (date in Almaty time + 5 random characters ≈ 28.6M combinations per day).
 * When a database is connected, also enforce a UNIQUE constraint on it.
 */
export function generateOrderNumber(date = new Date()): string {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Almaty",
    year: "2-digit",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? "00";
  const datePart = `${get("year")}${get("month")}${get("day")}`;

  const bytes = new Uint8Array(5);
  crypto.getRandomValues(bytes);
  const suffix = Array.from(bytes, (b) => ALPHABET[b % ALPHABET.length]).join("");

  return `BK-${datePart}-${suffix}`;
}

export function formatAlmatyDateTime(iso: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    timeZone: "Asia/Almaty",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}
