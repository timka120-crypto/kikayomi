import type { Metadata } from "next";
import { CartContents } from "@/components/cart/cart-contents";
import { Container } from "@/components/ui/container";

export const metadata: Metadata = {
  title: "Корзина",
  robots: { index: false, follow: false },
};

export default function CartPage() {
  return (
    <section className="grain">
      <Container className="pt-8 pb-20 sm:pt-12 sm:pb-28">
        <p className="eyebrow flex items-center gap-3 text-burgundy">
          <span aria-hidden className="h-px w-10 bg-burgundy/50" />
          Il carrello
        </p>
        <h1 className="mt-4 mb-6 text-[2.75rem] leading-none sm:text-6xl">Корзина</h1>
        <div className="flex min-h-[20rem] flex-col">
          <CartContents variant="page" />
        </div>
      </Container>
    </section>
  );
}
