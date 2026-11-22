import Link from "next/link";
import { OliveSprig } from "@/components/brand/logo";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";

export default function NotFound() {
  return (
    <section className="grain">
      <Container className="flex min-h-[70svh] flex-col items-center justify-center py-20 text-center">
        <OliveSprig className="h-14 w-14 text-olive" />
        <p className="mt-6 font-serif text-8xl text-burgundy italic sm:text-9xl">404</p>
        <h1 className="mt-4 text-4xl sm:text-5xl">Mamma mia! Страница не найдена</h1>
        <p className="mt-4 max-w-md text-ink-soft">
          Возможно, ссылка устарела. Зато меню на месте — и пицца тоже.
        </p>
        <div className="mt-9 flex flex-col gap-3 sm:flex-row">
          <Link href="/menu" className={buttonClasses("primary", "lg")}>
            Открыть меню
          </Link>
          <Link href="/" className={buttonClasses("outline", "lg")}>
            На главную
          </Link>
        </div>
      </Container>
    </section>
  );
}
