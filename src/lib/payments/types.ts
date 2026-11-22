/**
 * Online payment — extension point (not connected yet).
 *
 * Until a provider is connected, orders are created with
 * `payment: { method: "to_be_confirmed", status: "unpaid" }` and the operator
 * agrees the payment method with the customer.
 *
 * To connect a provider (Kaspi Pay, Halyk ePay, CloudPayments, Freedom Pay…):
 *  1. Implement `PaymentProvider` in src/lib/payments/<provider>.ts.
 *  2. After `createOrder` succeeds, call `createPayment` and return
 *     `redirectUrl` to the checkout page instead of the confirmation.
 *  3. Add a route handler for the provider's callback (e.g.
 *     src/app/api/payments/<provider>/route.ts), verify its signature,
 *     then mark the order as paid in your order storage.
 */
import type { Order } from "@/lib/orders/types";

export interface PaymentSession {
  /** Where to send the customer to pay. */
  redirectUrl: string;
  /** Provider-side payment id, store it with the order. */
  paymentId: string;
}

export interface PaymentProvider {
  id: string;
  isConfigured(): boolean;
  createPayment(order: Order, options: { returnUrl: string }): Promise<PaymentSession>;
}
