/**
 * Cart store: a tiny external store persisted to localStorage.
 *
 * - Only `{ id, quantity }` pairs are stored; names, photos and prices are
 *   always resolved from the current menu, so price edits apply immediately.
 * - Survives page reloads and syncs between open tabs (`storage` event).
 * - Server render and the first client render use an empty, non-hydrated
 *   snapshot, which keeps hydration consistent.
 */
import { MAX_QUANTITY_PER_ITEM, type FulfillmentMethod } from "@/lib/pricing";

export interface CartItem {
  id: string;
  quantity: number;
}

export interface CartState {
  items: CartItem[];
  fulfillment: FulfillmentMethod;
  hydrated: boolean;
}

const STORAGE_KEY = "bekakotak:cart:v1";

const SERVER_STATE: CartState = Object.freeze({
  items: [],
  fulfillment: "delivery",
  hydrated: false,
}) as CartState;

let state: CartState = SERVER_STATE;
const listeners = new Set<() => void>();

function clampQuantity(quantity: number): number {
  if (!Number.isFinite(quantity)) return 0;
  return Math.max(0, Math.min(MAX_QUANTITY_PER_ITEM, Math.floor(quantity)));
}

function parse(raw: string | null): Omit<CartState, "hydrated"> {
  const fallback = { items: [], fulfillment: "delivery" as const };
  if (!raw) return fallback;
  try {
    const data = JSON.parse(raw) as Partial<CartState>;
    const items = Array.isArray(data.items)
      ? data.items
          .filter(
            (item): item is CartItem => typeof item?.id === "string" && typeof item?.quantity === "number",
          )
          .map((item) => ({ id: item.id, quantity: clampQuantity(item.quantity) }))
          .filter((item) => item.quantity > 0)
      : [];
    const fulfillment = data.fulfillment === "pickup" ? "pickup" : "delivery";
    return { items, fulfillment };
  } catch {
    return fallback;
  }
}

function readStorage(): Omit<CartState, "hydrated"> {
  try {
    return parse(window.localStorage.getItem(STORAGE_KEY));
  } catch {
    return { items: [], fulfillment: "delivery" };
  }
}

function writeStorage(next: CartState) {
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ items: next.items, fulfillment: next.fulfillment }),
    );
  } catch {
    // Private mode / quota exceeded — the cart still works for this tab.
  }
}

function ensureHydrated() {
  if (state.hydrated || typeof window === "undefined") return;
  state = { ...readStorage(), hydrated: true };
}

function emit() {
  listeners.forEach((listener) => listener());
}

function setState(updater: (current: CartState) => Omit<CartState, "hydrated">) {
  ensureHydrated();
  const next = { ...updater(state), hydrated: true };
  state = next;
  writeStorage(next);
  emit();
}

function onStorage(event: StorageEvent) {
  if (event.key !== STORAGE_KEY) return;
  state = { ...parse(event.newValue), hydrated: true };
  emit();
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  if (listeners.size === 1) window.addEventListener("storage", onStorage);
  return () => {
    listeners.delete(listener);
    if (listeners.size === 0) window.removeEventListener("storage", onStorage);
  };
}

export function getSnapshot(): CartState {
  ensureHydrated();
  return state;
}

export function getServerSnapshot(): CartState {
  return SERVER_STATE;
}

export const cartActions = {
  add(id: string, quantity = 1) {
    setState((current) => {
      const existing = current.items.find((item) => item.id === id);
      const items = existing
        ? current.items.map((item) =>
            item.id === id ? { ...item, quantity: clampQuantity(item.quantity + quantity) } : item,
          )
        : [...current.items, { id, quantity: clampQuantity(quantity) }];
      return { ...current, items: items.filter((item) => item.quantity > 0) };
    });
  },

  setQuantity(id: string, quantity: number) {
    setState((current) => {
      const nextQuantity = clampQuantity(quantity);
      const items =
        nextQuantity === 0
          ? current.items.filter((item) => item.id !== id)
          : current.items.some((item) => item.id === id)
            ? current.items.map((item) => (item.id === id ? { ...item, quantity: nextQuantity } : item))
            : [...current.items, { id, quantity: nextQuantity }];
      return { ...current, items };
    });
  },

  remove(id: string) {
    setState((current) => ({ ...current, items: current.items.filter((item) => item.id !== id) }));
  },

  clear() {
    setState((current) => ({ ...current, items: [] }));
  },

  setFulfillment(fulfillment: FulfillmentMethod) {
    setState((current) => ({ ...current, fulfillment }));
  },
};
