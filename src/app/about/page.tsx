import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Advantages } from "@/components/home/advantages";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { PageHero } from "@/components/ui/page-hero";
import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";
import { aboutContent } from "@/content/about";

export const metadata: Metadata = {
  title: "О кафе",
  description:
    "BekaKotak — итальянское кафе в Алматы на ул. Розыбакиева, 66. Уютная атмосфера, классическая итальянская кухня, доставка и самовывоз.",
  alternates: { canonical: "/about" },
};

const gallery = [
  {
    src: "/images/site/interior-plants.jpg",
    alt: "Светлый зал кафе с растениями",
    className: "sm:col-span-2 aspect-[16/10]",
  },
  {
    src: "/images/site/about-chef.jpg",
    alt: "Повар за работой на кухне",
    className: "aspect-[4/5] sm:row-span-2 sm:aspect-auto",
  },
  {
    src: "/images/site/about-table.jpg",
    alt: "Ужин с друзьями за накрытым столом",
    className: "aspect-[4/3]",
  },
  {
    src: "/images/site/spaghetti-fork.jpg",
    alt: "Спагетти с томатным соусом на вилке",
    className: "aspect-[4/3]",
  },
];

export default function AboutPage() {
  return (
    <>
      <PageHero
        eyebrow="Chi siamo"
        title={
          <>
            О кафе <em className="text-burgundy">BekaKotak</em>
          </>
        }
        description={aboutContent.lead}
        image={{
          src: "/images/site/about-interior.jpg",
          alt: "Зал итальянского кафе с зеленью",
          position: "object-[50%_60%]",
        }}
      />

      <section className="py-20 sm:py-28">
        <Container className="grid gap-12 lg:grid-cols-[1fr_1.1fr] lg:gap-20">
          <Reveal>
            <SectionHeading index="01" eyebrow="Наша история" title={aboutContent.title} />
            <p className="mt-8 font-serif text-2xl text-burgundy italic">— {aboutContent.signature}</p>
          </Reveal>
          <div className="space-y-6 text-lg leading-relaxed text-ink-soft">
            {aboutContent.paragraphs.map((paragraph, index) => (
              <Reveal key={index} delay={index * 100}>
                <p
                  className={
                    index === 0
                      ? "first-letter:float-left first-letter:mr-3 first-letter:font-serif first-letter:text-7xl first-letter:leading-[0.8] first-letter:text-burgundy"
                      : ""
                  }
                >
                  {paragraph}
                </p>
              </Reveal>
            ))}
          </div>
        </Container>
      </section>

      <section className="pb-20 sm:pb-28" aria-label="Фотографии кафе">
        <Container>
          <ul className="grid gap-4 sm:grid-cols-3 sm:gap-5">
            {gallery.map((photo, index) => (
              <Reveal
                as="li"
                key={photo.src}
                delay={index * 90}
                className={`relative overflow-hidden rounded-card bg-cream-deep ${photo.className}`}
              >
                <Image
                  src={photo.src}
                  alt={photo.alt}
                  fill
                  sizes="(max-width: 640px) 100vw, (max-width: 1320px) 66vw, 860px"
                  className="object-cover transition-transform duration-[1.5s] ease-out hover:scale-105"
                />
              </Reveal>
            ))}
          </ul>
        </Container>
      </section>

      <section className="bg-parchment py-20 sm:py-28">
        <Container>
          <Reveal>
            <SectionHeading
              index="02"
              eyebrow="Атмосфера"
              title="Что делает BekaKotak особенным"
              align="center"
            />
          </Reveal>
          <ul className="mt-14 grid gap-6 md:grid-cols-3">
            {aboutContent.values.map((value, index) => (
              <Reveal as="li" key={value.title} delay={index * 120}>
                <div className="h-full rounded-card bg-white p-8 ring-1 ring-ink/5">
                  <span className="font-serif text-5xl text-burgundy/30 italic">0{index + 1}</span>
                  <h3 className="mt-6 font-serif text-3xl">{value.title}</h3>
                  <p className="mt-3 leading-relaxed text-ink-soft">{value.text}</p>
                </div>
              </Reveal>
            ))}
          </ul>
        </Container>
      </section>

      <Advantages />

      <section className="py-20 text-center sm:py-28">
        <Container>
          <Reveal>
            <p className="eyebrow text-burgundy">A tavola!</p>
            <h2 className="mx-auto mt-5 max-w-2xl text-[2.6rem] leading-[1.02] sm:text-6xl">
              Приходите в гости или закажите домой
            </h2>
            <div className="mt-10 flex flex-col justify-center gap-3 sm:flex-row">
              <Link href="/menu" className={buttonClasses("primary", "lg")}>
                Смотреть меню
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/contacts" className={buttonClasses("outline", "lg")}>
                Как нас найти
              </Link>
            </div>
          </Reveal>
        </Container>
      </section>
    </>
  );
}
