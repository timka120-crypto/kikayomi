import { socialIcons } from "@/components/brand/social-icons";
import { siteConfig } from "@/config/site";
import { cn } from "@/lib/cn";

/** Social icons from config. Icons without a URL are shown muted and are not links. */
export function SocialLinks({ tone = "light", className }: { tone?: "light" | "dark"; className?: string }) {
  const anyLinked = siteConfig.socials.some((social) => social.url);
  const light = tone === "light";
  return (
    <div className={className}>
      <ul className="flex items-center gap-2.5">
        {siteConfig.socials.map((social) => {
          const Icon = socialIcons[social.id as keyof typeof socialIcons];
          const base = cn(
            "grid h-11 w-11 place-items-center rounded-full border transition-colors duration-300",
            light ? "border-cream/20" : "border-ink/15",
          );
          return (
            <li key={social.id}>
              {social.url ? (
                <a
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={social.label}
                  className={cn(
                    base,
                    light
                      ? "text-cream hover:border-cream hover:bg-cream hover:text-ink"
                      : "text-ink hover:border-ink hover:bg-ink hover:text-cream",
                  )}
                >
                  <Icon className="h-5 w-5" />
                </a>
              ) : (
                <span
                  className={cn(base, "opacity-45")}
                  title={`${social.label} — ссылка появится позже`}
                  aria-label={`${social.label} — ссылка появится позже`}
                  role="img"
                >
                  <Icon className={cn("h-5 w-5", light ? "text-cream" : "text-ink")} />
                </span>
              )}
            </li>
          );
        })}
      </ul>
      {!anyLinked && (
        <p className={cn("mt-3 text-xs", light ? "text-cream/50" : "text-ink-muted")}>
          Ссылки на соцсети скоро появятся
        </p>
      )}
    </div>
  );
}
