"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useCart } from "@/lib/cart/use-cart";

/**
 * «Заказать доставку»: selects delivery as the fulfillment method, then goes
 * to checkout if the cart has dishes, otherwise to the menu.
 */
export function OrderDeliveryLink({ className, children }: { className?: string; children: ReactNode }) {
  const { count, actions } = useCart();
  return (
    <Link
      href={count > 0 ? "/checkout" : "/menu"}
      onClick={() => actions.setFulfillment("delivery")}
      className={className}
    >
      {children}
    </Link>
  );
}
