import { Clock, MapPin, Phone, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { WhatsAppIcon } from "@/components/brand/social-icons";
import { siteConfig } from "@/config/site";
import { getPhone, getWhatsAppUrl, isPlaceholder } from "@/lib/contacts";
import { cn } from "@/lib/cn";

function Row({ icon: Icon, label, children }: { icon: LucideIcon; label: string; children: ReactNode }) {
  return (
    <div className="flex gap-4 py-5 first:pt-0 last:pb-0">
      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-burgundy-soft text-burgundy">
        <Icon className="h-5 w-5" strokeWidth={1.7} />
      </span>
      <div className="min-w-0">
        <p className="eyebrow text-ink-muted">{label}</p>
        <div className="mt-1.5 text-[1.05rem] text-ink">{children}</div>
      </div>
    </div>
  );
}

function Pending({ children }: { children: ReactNode }) {
  return <span className="mt-1 block text-xs text-ink-muted">{children}</span>;
}

/** Address, phone and opening hours from src/config/site.ts. */
export function ContactDetails({ className }: { className?: string }) {
  const phone = getPhone();
  const whatsapp = getWhatsAppUrl();

  return (
    <div className={cn("divide-y divide-ink/10", className)}>
      <Row icon={MapPin} label="Адрес">
        <address className="not-italic">
          {siteConfig.address.street}
          <br />
          {siteConfig.address.city}, {siteConfig.address.country}
        </address>
      </Row>
      <Row icon={Phone} label="Телефон">
        {phone.href ? (
          <a href={phone.href} className="font-semibold hover:text-burgundy">
            {phone.display}
          </a>
        ) : (
          <>
            <span className="text-ink-soft">{phone.display}</span>
            <Pending>Номер телефона скоро появится</Pending>
          </>
        )}
        {whatsapp && (
          <a
            href={whatsapp}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-flex items-center gap-2 text-sm font-semibold text-olive-deep hover:text-olive"
          >
            <WhatsAppIcon className="h-4 w-4" />
            Написать в WhatsApp
          </a>
        )}
      </Row>
      <Row icon={Clock} label="График работы">
        <ul className="space-y-0.5">
          {siteConfig.hours.map((row) => (
            <li key={row.days}>
              {row.days}:{" "}
              <span className={isPlaceholder(row.time) ? "text-ink-soft" : "font-semibold"}>{row.time}</span>
            </li>
          ))}
        </ul>
        {siteConfig.hours.some((row) => isPlaceholder(row.time)) && <Pending>График уточняется</Pending>}
      </Row>
    </div>
  );
}
