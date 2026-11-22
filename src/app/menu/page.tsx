import type { Metadata } from "next";
import { DemoMenuNotice } from "@/components/menu/demo-menu-notice";
import { MenuBrowser } from "@/components/menu/menu-browser";
import { PageHero } from "@/components/ui/page-hero";
import { getCategories, getProducts } from "@/lib/menu";

export const metadata: Metadata = {
  title: "Меню",
  description:
    "Меню итальянского кафе BekaKotak: пицца, паста, салаты, закуски, супы, десерты и напитки. Заказ с доставкой и самовывозом в Алматы.",
  alternates: { canonical: "/menu" },
};

export default function MenuPage() {
  return (
    <>
      <PageHero
        eyebrow="Il nostro menù"
        title={
          <>
            Наше <em className="text-burgundy">меню</em>
          </>
        }
        description="Пицца, паста, антипасти и dolci. Выберите блюда, укажите количество — и оформите заказ с доставкой или самовывозом."
        image={{
          src: "/images/site/spaghetti-fork.jpg",
          alt: "Спагетти с томатным соусом на вилке",
          position: "object-[50%_55%]",
        }}
      >
        <DemoMenuNotice className="mt-8 max-w-xl" />
      </PageHero>
      <MenuBrowser categories={getCategories()} products={getProducts()} />
    </>
  );
}
