"use client";

import type { OrderRequest } from "./schema";
import type { OrderConfirmation, OrderErrorResponse } from "./types";

const LAST_ORDER_KEY = "bekakotak:last-order";
const CUSTOMER_KEY = "bekakotak:customer";

export type SubmitResult =
  | { ok: true; confirmation: OrderConfirmation }
  | { ok: false; error: OrderErrorResponse; status: number };

export async function submitOrder(payload: OrderRequest): Promise<SubmitResult> {
  try {
    const response = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => null);
    if (response.ok && data?.orderNumber) {
      return { ok: true, confirmation: data as OrderConfirmation };
    }
    return {
      ok: false,
      status: response.status,
      error: (data as OrderErrorResponse) ?? {
        code: "DELIVERY_FAILED",
        message: "Сервер вернул неожиданный ответ. Корзина сохранена — попробуйте ещё раз.",
      },
    };
  } catch {
    return {
      ok: false,
      status: 0,
      error: {
        code: "DELIVERY_FAILED",
        message: "Нет соединения с сервером. Проверьте интернет и попробуйте ещё раз — корзина сохранена.",
      },
    };
  }
}

export function saveLastOrder(confirmation: OrderConfirmation) {
  try {
    window.sessionStorage.setItem(LAST_ORDER_KEY, JSON.stringify(confirmation));
  } catch {
    /* storage unavailable */
  }
}

export function readLastOrderRaw(): string | null {
  try {
    return window.sessionStorage.getItem(LAST_ORDER_KEY);
  } catch {
    return null;
  }
}

export interface SavedCustomer {
  name: string;
  phone: string;
  street: string;
  house: string;
  apartment: string;
  entrance: string;
  floor: string;
}

/** Remember contact details on this device after a successful order. */
export function saveCustomer(customer: SavedCustomer) {
  try {
    window.localStorage.setItem(CUSTOMER_KEY, JSON.stringify(customer));
  } catch {
    /* storage unavailable */
  }
}

export function readSavedCustomer(): Partial<SavedCustomer> | null {
  try {
    const raw = window.localStorage.getItem(CUSTOMER_KEY);
    return raw ? (JSON.parse(raw) as Partial<SavedCustomer>) : null;
  } catch {
    return null;
  }
}
