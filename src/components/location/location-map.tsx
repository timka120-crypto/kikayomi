import { ExternalLink, MapPin } from "lucide-react";
import { siteConfig } from "@/config/site";
import { getMapEmbedUrl, getMapLinks } from "@/lib/contacts";
import { cn } from "@/lib/cn";

export function MapLinks({ className }: { className?: string }) {
  const links = getMapLinks();
  const items = [
    { href: links.twoGis, label: "2ГИС" },
    { href: links.yandex, label: "Яндекс Карты" },
    { href: links.google, label: "Google Maps" },
  ];
  return (
    <ul className={cn("flex flex-wrap gap-2", className)}>
      {items.map((item) => (
        <li key={item.label}>
          <a
            href={item.href}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-10 items-center gap-1.5 rounded-full border border-ink/15 bg-white px-4 text-sm font-semibold text-ink transition-colors hover:border-ink hover:bg-ink hover:text-cream"
          >
            {item.label}
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </li>
      ))}
    </ul>
  );
}

export function LocationMap({ className }: { className?: string }) {
  return (
    <div className={cn("relative overflow-hidden rounded-card bg-cream-deep ring-1 ring-ink/10", className)}>
      {/* Fallback underneath the map (visible while it loads or if maps are blocked) */}
      <div className="absolute inset-0 grid place-items-center p-6 text-center">
        <div>
          <span className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-burgundy text-cream shadow-lg">
            <MapPin className="h-6 w-6" />
          </span>
          <p className="mt-4 font-serif text-2xl text-ink">{siteConfig.address.street}</p>
          <p className="text-sm text-ink-soft">
            {siteConfig.address.city}, {siteConfig.address.country}
          </p>
          <MapLinks className="mt-5 justify-center" />
        </div>
      </div>
      <iframe
        title={`Карта: ${siteConfig.brand}, ${siteConfig.address.street}, ${siteConfig.address.city}`}
        src={getMapEmbedUrl()}
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        className="absolute inset-0 h-full w-full border-0 grayscale-[35%] sepia-[12%]"
        allowFullScreen
      />
    </div>
  );
}
