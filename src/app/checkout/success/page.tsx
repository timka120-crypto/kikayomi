import type { Metadata } from "next";
import { OrderSuccess } from "@/components/checkout/order-success";
import { Container } from "@/components/ui/container";

export const metadata: Metadata = {
  title: "Заказ принят",
  robots: { index: false, follow: false },
};

export default function CheckoutSuccessPage() {
  return (
    <section className="grain">
      <Container className="pt-10 pb-20 sm:pt-14 sm:pb-28">
        <OrderSuccess />
      </Container>
    </section>
  );
}
