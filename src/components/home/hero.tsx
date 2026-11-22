import Image from "next/image";
import { ArrowRight, MapPin } from "lucide-react";
import { OliveSprig } from "@/components/brand/logo";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { siteConfig } from "@/config/site";
import { OrderDeliveryLink } from "./order-delivery-link";
import Link from "next/link";

/** Circular rotating stamp — «fatto con amore». */
function Stamp({ className }: { className?: string }) {
  return (
    <div className={className} aria-hidden>
      <div className="relative grid h-32 w-32 place-items-center rounded-full bg-burgundy text-cream shadow-[0_20px_50px_-20px_rgb(118_43_50/0.9)] sm:h-36 sm:w-36">
        <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full animate-spin-slow">
          <defs>
            <path id="stamp-circle" d="M50,50 m-37,0 a37,37 0 1,1 74,0 a37,37 0 1,1 -74,0" />
          </defs>
          <text className="fill-current font-sans text-[8.6px] font-bold uppercase">
            <textPath href="#stamp-circle" textLength="226" lengthAdjust="spacing">
              Fatto con amore • BekaKotak •
            </textPath>
          </text>
        </svg>
        <OliveSprig className="h-11 w-11 text-cream" />
      </div>
    </div>
  );
}

export function Hero() {
  return (
    <section className="grain relative overflow-hidden">
      {/* Soft decorative shapes */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-40 -left-40 h-[34rem] w-[34rem] rounded-full bg-burgundy/[0.06] blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute right-0 bottom-0 h-[28rem] w-[28rem] rounded-full bg-olive/[0.08] blur-3xl"
      />

      <Container className="relative grid items-center gap-12 pt-6 pb-16 sm:pt-10 lg:min-h-[calc(100svh-76px)] lg:grid-cols-12 lg:gap-8 lg:pt-6 lg:pb-20">
        <div className="lg:col-span-6 xl:col-span-6">
          <p className="eyebrow flex animate-fade-up items-center gap-3 text-burgundy">
            <span aria-hidden className="h-px w-10 bg-burgundy/50" />
            Cucina italiana · Алматы
          </p>
          <h1 className="mt-6 animate-fade-up text-[3.4rem] leading-[0.95] text-ink [animation-delay:120ms] sm:text-7xl lg:text-[5.4rem] xl:text-[6.4rem]">
            Вкус настоящей <em className="font-medium text-burgundy">Италии</em>
          </h1>
          <p className="mt-7 max-w-md animate-fade-up text-lg leading-relaxed text-ink-soft [animation-delay:240ms] sm:text-xl">
            Итальянская кухня, созданная с любовью.
          </p>
          <div className="mt-10 flex animate-fade-up flex-col gap-3 [animation-delay:360ms] sm:flex-row sm:items-center">
            <Link href="/menu" className={buttonClasses("primary", "lg")}>
              Посмотреть меню
              <ArrowRight className="h-4 w-4" />
            </Link>
            <OrderDeliveryLink className={buttonClasses("outline", "lg")}>
              Заказать доставку
            </OrderDeliveryLink>
          </div>
          <p className="mt-10 flex animate-fade-up items-center gap-2 text-sm text-ink-muted [animation-delay:480ms]">
            <MapPin className="h-4 w-4 text-olive" />
            {siteConfig.address.street}, {siteConfig.address.city}
          </p>
        </div>

        <div className="relative lg:col-span-6 xl:col-span-6">
          <div className="relative mx-auto w-full max-w-[34rem] lg:mr-0">
            <div className="arch relative aspect-[4/4.6] animate-fade-in overflow-hidden bg-ink shadow-[0_40px_100px_-40px_rgb(37_35_31/0.6)] sm:aspect-[4/4.4]">
              <Image
                src="/images/site/hero-pizza-oven.jpg"
                alt="Неаполитанская пицца на деревянной доске у дровяной печи"
                fill
                preload
                sizes="(max-width: 1024px) 92vw, 560px"
                className="animate-ken-burns object-cover object-[60%_50%]"
              />
              <div
                aria-hidden
                className="absolute inset-0 bg-gradient-to-t from-ink/40 via-transparent to-transparent"
              />
            </div>

            {/* Small round inset */}
            <div className="absolute -bottom-8 -left-2 h-32 w-32 animate-fade-up overflow-hidden rounded-full border-[6px] border-cream shadow-xl [animation-delay:500ms] sm:-left-10 sm:h-44 sm:w-44">
              <Image
                src="/images/site/spaghetti-dark.jpg"
                alt="Спагетти на вилке"
                fill
                sizes="176px"
                className="object-cover object-[50%_35%]"
              />
            </div>

            <Stamp className="absolute -top-6 right-2 animate-fade-in [animation-delay:700ms] sm:-right-6" />
          </div>
        </div>
      </Container>
    </section>
  );
}
