import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { ContactDetails } from "@/components/location/contact-details";
import { DeliveryTerms } from "@/components/location/delivery-terms";
import { LocationMap, MapLinks } from "@/components/location/location-map";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";

/** Delivery & contacts block on the home page. */
export function LocationSection() {
  return (
    <section className="py-20 sm:py-28" aria-labelledby="location-title">
      <Container>
        <Reveal>
          <SectionHeading
            index="04"
            eyebrow="Доставка и контакты"
            title={
              <span id="location-title">
                Ждём в гости — <em className="text-burgundy">или привезём</em> к вам
              </span>
            }
          />
        </Reveal>

        <div className="mt-12 grid gap-8 lg:grid-cols-[1fr_1.15fr] lg:gap-10">
          <Reveal className="flex flex-col gap-8">
            <div className="rounded-card bg-white p-6 ring-1 ring-ink/5 sm:p-8">
              <ContactDetails />
              <MapLinks className="mt-7" />
            </div>
            <div>
              <h3 className="font-serif text-3xl">Доставка</h3>
              <p className="mt-2 text-ink-soft">
                Оформите заказ на сайте — мы свяжемся с вами для подтверждения.
              </p>
              <DeliveryTerms className="mt-5" />
              <Link href="/delivery" className={buttonClasses("outline", "md", "mt-6")}>
                Подробнее о доставке
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Reveal>
          <Reveal delay={150}>
            <LocationMap className="h-[22rem] sm:h-[28rem] lg:h-full lg:min-h-[36rem]" />
          </Reveal>
        </div>
      </Container>
    </section>
  );
}
