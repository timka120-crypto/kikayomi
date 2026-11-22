import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { DemoMenuNotice } from "@/components/menu/demo-menu-notice";
import { ProductCard } from "@/components/menu/product-card";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";
import { getPopularProducts } from "@/lib/menu";

export function PopularDishes() {
  const products = getPopularProducts(6);

  return (
    <section className="py-20 sm:py-28" aria-labelledby="popular-title">
      <Container>
        <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
          <Reveal>
            <SectionHeading
              index="01"
              eyebrow="Популярное"
              title={
                <span id="popular-title">
                  Блюда, ради которых <em className="text-burgundy">возвращаются</em>
                </span>
              }
              description="Классика итальянской кухни: пицца на тонком тесте, паста с правильными соусами и тирамису на десерт."
            />
          </Reveal>
          <Reveal delay={150} className="shrink-0">
            <Link href="/menu" className={buttonClasses("outline", "md")}>
              Всё меню
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Reveal>
        </div>

        <DemoMenuNotice className="mt-8" />

        <ul className="mt-10 grid gap-5 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3 lg:gap-7">
          {products.map((product, index) => (
            <Reveal as="li" key={product.id} delay={(index % 3) * 110}>
              <ProductCard product={product} />
            </Reveal>
          ))}
        </ul>
      </Container>
    </section>
  );
}
