import type { Metadata } from "next";
import { connection } from "next/server";
import { Suspense } from "react";
import { CheckoutForm, CheckoutSkeleton } from "@/components/checkout/checkout-form";
import { Container } from "@/components/ui/container";
import { getOrderingStatus } from "@/lib/orders/channels";

export const metadata: Metadata = {
  title: "Оформление заказа",
  robots: { index: false, follow: false },
};

/** Reads server configuration at request time (env vars can change without a rebuild). */
async function CheckoutWithStatus() {
  await connection();
  const { enabled } = getOrderingStatus();
  return <CheckoutForm orderingEnabled={enabled} />;
}

export default function CheckoutPage() {
  return (
    <section className="grain">
      <Container className="pt-8 pb-20 sm:pt-12 sm:pb-28">
        <p className="eyebrow flex items-center gap-3 text-burgundy">
          <span aria-hidden className="h-px w-10 bg-burgundy/50" />
          Ordinare
        </p>
        <h1 className="mt-4 mb-8 text-[2.75rem] leading-none sm:mb-10 sm:text-6xl">
          Оформление <em className="text-burgundy">заказа</em>
        </h1>
        <Suspense fallback={<CheckoutSkeleton />}>
          <CheckoutWithStatus />
        </Suspense>
      </Container>
    </section>
  );
}
