import type { FulfillmentMethod, OrderTotals } from "@/lib/pricing";

export interface OrderLine {
  id: string;
  name: string;
  price: number;
  quantity: number;
  total: number;
}

/** A validated, server-priced order — the shape every order channel receives. */
export interface Order {
  number: string;
  createdAt: string;
  source: "website";
  customer: {
    name: string;
    /** E.164, e.g. +77012345678 */
    phone: string;
  };
  fulfillment: FulfillmentMethod;
  address: {
    street: string;
    house: string;
    apartment: string;
    entrance: string;
    floor: string;
  } | null;
  comment: string;
  items: OrderLine[];
  totals: Pick<OrderTotals, "subtotal" | "deliveryFee" | "deliveryFeeStatus" | "total" | "totalIsFinal">;
  /** Payment is arranged with the operator until online payment is connected. */
  payment: { method: "to_be_confirmed"; status: "unpaid" };
}

/** What the API returns to the browser after a successful order. */
export interface OrderConfirmation {
  orderNumber: string;
  createdAt: string;
  fulfillment: FulfillmentMethod;
  items: OrderLine[];
  totals: Order["totals"];
  customerName: string;
}

export type OrderErrorCode =
  | "VALIDATION_ERROR"
  | "ORDERS_NOT_CONFIGURED"
  | "ITEMS_UNAVAILABLE"
  | "MIN_ORDER"
  | "RATE_LIMITED"
  | "DELIVERY_FAILED"
  | "BAD_REQUEST";

export interface OrderErrorResponse {
  code: OrderErrorCode;
  message: string;
  fieldErrors?: Record<string, string>;
  unavailableItems?: string[];
}
