import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Reveal } from "@/components/ui/reveal";
import { OrderDeliveryLink } from "./order-delivery-link";

export function CtaBanner() {
  return (
    <section className="pb-20 sm:pb-28">
      <Container>
        <Reveal>
          <div className="relative isolate overflow-hidden rounded-[2rem] bg-ink text-cream">
            <Image
              src="/images/site/about-table.jpg"
              alt=""
              fill
              sizes="(max-width: 1320px) 100vw, 1320px"
              className="-z-10 object-cover opacity-45"
            />
            <div
              aria-hidden
              className="absolute inset-0 -z-10 bg-gradient-to-r from-ink via-ink/80 to-ink/20"
            />
            <div className="max-w-2xl px-6 py-16 sm:px-12 sm:py-20 lg:px-16 lg:py-24">
              <p className="eyebrow text-cream/70">Buon appetito</p>
              <h2 className="mt-5 text-[2.6rem] leading-[1.02] sm:text-6xl">
                Итальянский ужин — <em>без лишних хлопот</em>
              </h2>
              <p className="mt-5 max-w-lg text-lg leading-relaxed text-cream/75">
                Соберите заказ из любимых блюд — доставим домой или подготовим к самовывозу.
              </p>
              <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                <Link href="/menu" className={buttonClasses("light", "lg")}>
                  Открыть меню
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <OrderDeliveryLink className={buttonClasses("outlineLight", "lg")}>
                  Заказать доставку
                </OrderDeliveryLink>
              </div>
            </div>
          </div>
        </Reveal>
      </Container>
    </section>
  );
}
