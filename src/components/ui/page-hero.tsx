import Image from "next/image";
import type { ReactNode } from "react";
import { Container } from "@/components/ui/container";
import { cn } from "@/lib/cn";

interface PageHeroProps {
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  image?: { src: string; alt: string; position?: string };
  children?: ReactNode;
  className?: string;
}

/** Inner-page header: big serif title, optional arched photo on the right. */
export function PageHero({ eyebrow, title, description, image, children, className }: PageHeroProps) {
  return (
    <section className={cn("grain relative overflow-hidden", className)}>
      <div
        aria-hidden
        className="pointer-events-none absolute -top-32 -right-32 h-[26rem] w-[26rem] rounded-full bg-burgundy/[0.06] blur-3xl"
      />
      <Container
        className={cn(
          "relative grid items-end gap-10 pt-10 pb-12 sm:pt-14 sm:pb-16",
          image && "lg:grid-cols-[1.2fr_1fr] lg:items-center lg:gap-16",
        )}
      >
        <div className="animate-fade-up">
          <p className="eyebrow flex items-center gap-3 text-burgundy">
            <span aria-hidden className="h-px w-10 bg-burgundy/50" />
            {eyebrow}
          </p>
          <h1 className="mt-5 text-[3.1rem] leading-[0.98] text-ink sm:text-7xl lg:text-[5.2rem]">{title}</h1>
          {description && (
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink-soft">{description}</p>
          )}
          {children}
        </div>
        {image && (
          <div className="arch relative hidden aspect-[4/3.4] animate-fade-in overflow-hidden bg-cream-deep shadow-[0_40px_90px_-40px_rgb(37_35_31/0.55)] lg:block">
            <Image
              src={image.src}
              alt={image.alt}
              fill
              preload
              sizes="(max-width: 1320px) 40vw, 520px"
              className={cn("animate-ken-burns object-cover", image.position)}
            />
          </div>
        )}
      </Container>
    </section>
  );
}
