import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  ClipboardCheck,
  PhoneCall,
  ShoppingBag,
  Store,
  Truck,
  type LucideIcon,
} from "lucide-react";
import { DeliveryTerms, hasUnknownDeliveryTerms } from "@/components/location/delivery-terms";
import { LocationMap, MapLinks } from "@/components/location/location-map";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { PageHero } from "@/components/ui/page-hero";
import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: "Доставка",
  description:
    "Доставка и самовывоз из итальянского кафе BekaKotak в Алматы. Как оформить заказ, условия доставки и адрес для самовывоза.",
  alternates: { canonical: "/delivery" },
};

const steps: { icon: LucideIcon; title: string; text: string }[] = [
  {
    icon: ShoppingBag,
    title: "Выберите блюда",
    text: "Добавьте в корзину блюда из меню и укажите количество.",
  },
  {
    icon: ClipboardCheck,
    title: "Оформите заказ",
    text: "Укажите имя, телефон и адрес или выберите самовывоз.",
  },
  { icon: PhoneCall, title: "Подтверждение", text: "Мы свяжемся с вами, подтвердим заказ, сумму и время." },
  { icon: Truck, title: "Получите заказ", text: "Курьер привезёт заказ — или заберите его в кафе." },
];

export default function DeliveryPage() {
  return (
    <>
      <PageHero
        eyebrow="Consegna a domicilio"
        title={
          <>
            Доставка и <em className="text-burgundy">самовывоз</em>
          </>
        }
        description="Любимые итальянские блюда — у вас дома. Оформите заказ на сайте, а мы свяжемся с вами для подтверждения."
        image={{
          src: "/images/site/spaghetti-dark.jpg",
          alt: "Спагетти болоньезе на тёмном фоне",
          position: "object-[50%_45%]",
        }}
      >
        <div className="mt-9 flex flex-col gap-3 sm:flex-row">
          <Link href="/menu" className={buttonClasses("primary", "lg")}>
            Выбрать блюда
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </PageHero>

      <section className="py-20 sm:py-24" aria-labelledby="steps-title">
        <Container>
          <Reveal>
            <SectionHeading
              index="01"
              eyebrow="Как заказать"
              title={<span id="steps-title">Четыре простых шага</span>}
            />
          </Reveal>
          <ol className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map(({ icon: Icon, title, text }, index) => (
              <Reveal as="li" key={title} delay={index * 100}>
                <div className="relative h-full rounded-card bg-white p-7 ring-1 ring-ink/5">
                  <span className="absolute top-6 right-7 font-serif text-5xl text-ink/10 italic">
                    {index + 1}
                  </span>
                  <span className="grid h-12 w-12 place-items-center rounded-full bg-burgundy text-cream">
                    <Icon className="h-5 w-5" strokeWidth={1.7} />
                  </span>
                  <h3 className="mt-8 font-serif text-2xl">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-ink-soft">{text}</p>
                </div>
              </Reveal>
            ))}
          </ol>
        </Container>
      </section>

      <section className="bg-parchment py-20 sm:py-24" aria-labelledby="terms-title">
        <Container className="grid gap-12 lg:grid-cols-2 lg:gap-16">
          <Reveal>
            <SectionHeading
              index="02"
              eyebrow="Условия"
              title={<span id="terms-title">Условия доставки</span>}
            />
            <DeliveryTerms className="mt-10" />
            {hasUnknownDeliveryTerms() && (
              <p className="mt-5 text-sm leading-relaxed text-ink-muted">
                Точные условия зависят от адреса — оператор сообщит стоимость и время доставки при
                подтверждении заказа.
              </p>
            )}
            <p className="mt-5 text-sm leading-relaxed text-ink-muted">{siteConfig.payment.note}</p>
          </Reveal>

          <Reveal delay={120}>
            <div className="h-full rounded-card bg-white p-7 ring-1 ring-ink/5 sm:p-9">
              <span className="grid h-12 w-12 place-items-center rounded-full bg-olive text-white">
                <Store className="h-5 w-5" strokeWidth={1.7} />
              </span>
              <h3 className="mt-6 font-serif text-3xl">Самовывоз</h3>
              <p className="mt-3 leading-relaxed text-ink-soft">
                Выберите «Самовывоз» при оформлении — мы подготовим заказ, а вы заберёте его в кафе без
                доплаты за доставку.
              </p>
              <p className="mt-6 font-semibold text-ink">
                {siteConfig.address.street}, {siteConfig.address.city}
              </p>
              <MapLinks className="mt-4" />
            </div>
          </Reveal>
        </Container>
      </section>

      <section className="py-20 sm:py-24" aria-label="Карта">
        <Container>
          <Reveal>
            <LocationMap className="h-[24rem] sm:h-[30rem]" />
          </Reveal>
        </Container>
      </section>
    </>
  );
}
