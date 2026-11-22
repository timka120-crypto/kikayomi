import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";
import { aboutContent } from "@/content/about";

export function AboutSection() {
  return (
    <section className="relative overflow-hidden bg-parchment py-20 sm:py-28" aria-labelledby="about-title">
      <Container className="grid items-center gap-16 lg:grid-cols-2 lg:gap-20">
        {/* Arched photo collage */}
        <Reveal className="relative mx-auto w-full max-w-[32rem] pb-16 sm:pb-24 lg:mx-0">
          <div className="arch relative aspect-[3/4] w-[78%] overflow-hidden bg-cream-deep shadow-[0_40px_90px_-40px_rgb(37_35_31/0.55)]">
            <Image
              src="/images/site/about-interior.jpg"
              alt="Уютный зал итальянского кафе с зеленью и мягкими диванами"
              fill
              sizes="(max-width: 1024px) 70vw, 400px"
              className="object-cover"
            />
          </div>
          <div className="arch absolute right-0 bottom-0 aspect-[3/4] w-[50%] overflow-hidden border-[6px] border-parchment bg-cream-deep shadow-[0_30px_70px_-30px_rgb(37_35_31/0.6)]">
            <Image
              src="/images/site/about-chef.jpg"
              alt="Повар выкладывает блюдо на кухне"
              fill
              sizes="(max-width: 1024px) 45vw, 260px"
              className="object-cover"
            />
          </div>
          <p
            aria-hidden
            className="absolute top-6 right-[6%] hidden font-serif text-sm tracking-[0.5em] text-ink-muted uppercase [writing-mode:vertical-rl] sm:block"
          >
            Benvenuti
          </p>
        </Reveal>

        <div>
          <Reveal>
            <SectionHeading
              index="02"
              eyebrow="О кафе"
              title={<span id="about-title">{aboutContent.title}</span>}
            />
          </Reveal>
          <Reveal delay={120}>
            <p className="mt-7 font-serif text-[1.6rem] leading-snug text-ink sm:text-[1.85rem]">
              {aboutContent.lead}
            </p>
          </Reveal>
          {aboutContent.paragraphs.map((paragraph, index) => (
            <Reveal key={index} delay={180 + index * 60}>
              <p className="mt-5 text-base leading-relaxed text-ink-soft sm:text-[1.05rem]">{paragraph}</p>
            </Reveal>
          ))}
          <Reveal delay={320}>
            <div className="mt-10 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
              <p className="font-serif text-2xl text-burgundy italic">— {aboutContent.signature}</p>
              <Link href="/about" className={buttonClasses("outline", "md", "self-start sm:self-auto")}>
                Подробнее о кафе
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Reveal>
        </div>
      </Container>
    </section>
  );
}
