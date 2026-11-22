import { BookOpen, Leaf, Truck, type LucideIcon } from "lucide-react";
import { Container } from "@/components/ui/container";
import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";

const advantages: { icon: LucideIcon; title: string; text: string }[] = [
  {
    icon: Leaf,
    title: "Свежие ингредиенты",
    text: "Спелые томаты, ароматная зелень, моцарелла и пармезан — простые продукты, из которых рождается вкус.",
  },
  {
    icon: BookOpen,
    title: "Итальянские рецепты",
    text: "Классические сочетания и техники итальянской кухни — от карбонары и лазаньи до тирамису.",
  },
  {
    icon: Truck,
    title: "Удобная доставка",
    text: "Оформите заказ онлайн за пару минут — привезём домой или подготовим к самовывозу.",
  },
];

export function Advantages() {
  return (
    <section
      className="relative overflow-hidden bg-olive py-20 text-white sm:py-28"
      aria-labelledby="advantages-title"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 -right-24 h-96 w-96 rounded-full border border-white/10"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -top-10 -right-10 h-64 w-64 rounded-full border border-white/10"
      />
      <Container className="relative">
        <Reveal>
          <SectionHeading
            index="03"
            eyebrow="Почему мы"
            tone="light"
            title={
              <span id="advantages-title">
                Просто, честно, <em>по-итальянски</em>
              </span>
            }
          />
        </Reveal>
        <ul className="mt-14 grid gap-px overflow-hidden rounded-card bg-white/15 md:grid-cols-3">
          {advantages.map(({ icon: Icon, title, text }, index) => (
            <Reveal as="li" key={title} delay={index * 120} className="bg-olive">
              <div className="flex h-full flex-col p-7 sm:p-9">
                <div className="flex items-center justify-between">
                  <span className="grid h-14 w-14 place-items-center rounded-full bg-cream text-olive-deep">
                    <Icon className="h-6 w-6" strokeWidth={1.6} />
                  </span>
                  <span className="font-serif text-5xl text-white/25 italic">0{index + 1}</span>
                </div>
                <h3 className="mt-10 font-serif text-[2rem] leading-tight">{title}</h3>
                <p className="mt-3 leading-relaxed text-white/85">{text}</p>
              </div>
            </Reveal>
          ))}
        </ul>
      </Container>
    </section>
  );
}
