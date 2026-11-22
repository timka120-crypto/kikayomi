import Link from "next/link";
import { Clock, MapPin, Phone } from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { Container } from "@/components/ui/container";
import { navigation, siteConfig } from "@/config/site";
import { getMapLinks, getPhone, getWhatsAppUrl, isPlaceholder } from "@/lib/contacts";
import { SocialLinks } from "./social-links";

export function Footer() {
  const phone = getPhone();
  const whatsapp = getWhatsAppUrl();
  const maps = getMapLinks();

  return (
    <footer className="relative overflow-hidden bg-ink text-cream">
      {/* Oversized wordmark */}
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-[0.18em] left-1/2 -translate-x-1/2 font-serif text-[22vw] leading-none font-semibold tracking-[0.06em] whitespace-nowrap text-cream/[0.035] select-none"
      >
        BEKAKOTAK
      </div>

      <Container className="relative pt-16 pb-10 sm:pt-20">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-[1.3fr_1fr_1fr_1fr] lg:gap-10">
          <div>
            <Logo tone="light" />
            <p className="mt-6 max-w-xs text-sm leading-relaxed text-cream/65">
              Итальянское кафе в Алматы. Пицца, паста и десерты — в зале, навынос и с доставкой.
            </p>
            <SocialLinks className="mt-7" />
          </div>

          <div>
            <h2 className="eyebrow text-cream/50">Адрес</h2>
            <address className="mt-5 space-y-3 text-[0.95rem] not-italic">
              <p className="flex gap-3">
                <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-cream/50" />
                <span>
                  {siteConfig.address.street}
                  <br />
                  {siteConfig.address.city}, {siteConfig.address.country}
                </span>
              </p>
              <p className="flex flex-wrap gap-x-3 gap-y-1 pl-7 text-sm">
                <a
                  href={maps.twoGis}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cream/65 underline-offset-4 hover:text-cream hover:underline"
                >
                  2ГИС
                </a>
                <a
                  href={maps.yandex}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cream/65 underline-offset-4 hover:text-cream hover:underline"
                >
                  Яндекс Карты
                </a>
                <a
                  href={maps.google}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cream/65 underline-offset-4 hover:text-cream hover:underline"
                >
                  Google Maps
                </a>
              </p>
            </address>
          </div>

          <div>
            <h2 className="eyebrow text-cream/50">Контакты</h2>
            <ul className="mt-5 space-y-3 text-[0.95rem]">
              <li className="flex gap-3">
                <Phone className="mt-0.5 h-4 w-4 shrink-0 text-cream/50" />
                {phone.href ? (
                  <a href={phone.href} className="hover:underline">
                    {phone.display}
                  </a>
                ) : (
                  <span className="text-cream/60">
                    {phone.display}
                    <span className="block text-xs text-cream/40">номер скоро появится</span>
                  </span>
                )}
              </li>
              {whatsapp && (
                <li className="pl-7">
                  <a href={whatsapp} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    Написать в WhatsApp
                  </a>
                </li>
              )}
              {siteConfig.contacts.email && (
                <li className="pl-7">
                  <a href={`mailto:${siteConfig.contacts.email}`} className="hover:underline">
                    {siteConfig.contacts.email}
                  </a>
                </li>
              )}
            </ul>
          </div>

          <div>
            <h2 className="eyebrow text-cream/50">График работы</h2>
            <ul className="mt-5 space-y-3 text-[0.95rem]">
              {siteConfig.hours.map((row) => (
                <li key={row.days} className="flex gap-3">
                  <Clock className="mt-0.5 h-4 w-4 shrink-0 text-cream/50" />
                  <span>
                    {row.days}
                    <br />
                    <span className={isPlaceholder(row.time) ? "text-cream/60" : ""}>{row.time}</span>
                    {isPlaceholder(row.time) && (
                      <span className="block text-xs text-cream/40">график уточняется</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-16 flex flex-col gap-6 border-t border-cream/10 pt-8 text-sm text-cream/50 lg:flex-row lg:items-center lg:justify-between">
          <nav aria-label="Навигация в подвале">
            <ul className="flex flex-wrap gap-x-6 gap-y-2">
              {navigation.map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className="transition-colors hover:text-cream">
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <p>© {siteConfig.brand}. Фото блюд и интерьера — Unsplash.</p>
        </div>
      </Container>
    </footer>
  );
}
