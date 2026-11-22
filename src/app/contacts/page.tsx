import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { SocialLinks } from "@/components/layout/social-links";
import { ContactDetails } from "@/components/location/contact-details";
import { LocationMap, MapLinks } from "@/components/location/location-map";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { PageHero } from "@/components/ui/page-hero";
import { Reveal } from "@/components/ui/reveal";

export const metadata: Metadata = {
  title: "Контакты",
  description: "Адрес, телефон и график работы итальянского кафе BekaKotak: Алматы, ул. Розыбакиева, 66.",
  alternates: { canonical: "/contacts" },
};

export default function ContactsPage() {
  return (
    <>
      <PageHero
        eyebrow="Contatti"
        title={
          <>
            Как нас <em className="text-burgundy">найти</em>
          </>
        }
        description="Алматы, улица Розыбакиева, 66. Приходите в гости или закажите любимые блюда с доставкой."
      />

      <section className="pb-20 sm:pb-28">
        <Container className="grid gap-8 lg:grid-cols-[1fr_1.4fr] lg:gap-10">
          <Reveal className="flex flex-col gap-6">
            <div className="rounded-card bg-white p-6 ring-1 ring-ink/5 sm:p-8">
              <ContactDetails />
            </div>
            <div className="rounded-card bg-white p-6 ring-1 ring-ink/5 sm:p-8">
              <h2 className="font-serif text-2xl">Проложить маршрут</h2>
              <MapLinks className="mt-4" />
            </div>
            <div className="rounded-card bg-ink p-6 text-cream sm:p-8">
              <h2 className="font-serif text-2xl">Мы в соцсетях</h2>
              <SocialLinks className="mt-4" />
            </div>
            <Link href="/menu" className={buttonClasses("primary", "lg", "w-full")}>
              Заказать онлайн
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Reveal>
          <Reveal delay={120}>
            <LocationMap className="h-[26rem] sm:h-[34rem] lg:h-full lg:min-h-[40rem]" />
          </Reveal>
        </Container>
      </section>
    </>
  );
}
