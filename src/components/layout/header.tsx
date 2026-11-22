"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowRight, Menu, ShoppingBag, X } from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { useUI } from "@/components/providers/ui-provider";
import { buttonClasses } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { navigation, siteConfig } from "@/config/site";
import { useCart } from "@/lib/cart/use-cart";
import { cn } from "@/lib/cn";
import { getPhone } from "@/lib/contacts";

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

export function Header() {
  const pathname = usePathname();
  const { count, hydrated } = useCart();
  const { openCart } = useUI();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const phone = getPhone();
  const orderHref = count > 0 ? "/checkout" : "/menu";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && setMenuOpen(false);
    document.addEventListener("keydown", onKey);
    const media = window.matchMedia("(min-width: 1024px)");
    const onResize = () => media.matches && setMenuOpen(false);
    media.addEventListener("change", onResize);
    return () => {
      document.body.style.overflow = overflow;
      document.removeEventListener("keydown", onKey);
      media.removeEventListener("change", onResize);
    };
  }, [menuOpen]);

  const closeMenu = () => setMenuOpen(false);

  return (
    <>
      <header
        className={cn(
          "sticky top-0 z-50 transition-[background-color,box-shadow,border-color] duration-500",
          scrolled || menuOpen
            ? "border-b border-ink/10 bg-cream/90 backdrop-blur-md"
            : "border-b border-transparent bg-cream/0",
        )}
      >
        <Container className="flex h-16 items-center justify-between gap-4 sm:h-[76px]">
          <Logo showTagline className="relative z-10" />

          <nav aria-label="Основная навигация" className="hidden lg:block">
            <ul className="flex items-center gap-1 xl:gap-2">
              {navigation.map((item) => {
                const active = isActive(pathname, item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={active ? "page" : undefined}
                      className={cn(
                        "relative rounded-full px-4 py-2 text-[0.95rem] font-semibold transition-colors duration-300",
                        active ? "text-burgundy" : "text-ink/80 hover:text-ink",
                      )}
                    >
                      {item.label}
                      <span
                        aria-hidden
                        className={cn(
                          "absolute bottom-0 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full bg-burgundy transition-opacity duration-300",
                          active ? "opacity-100" : "opacity-0",
                        )}
                      />
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="relative z-10 flex items-center gap-1.5 sm:gap-3">
            <button
              type="button"
              onClick={openCart}
              className="relative grid h-11 w-11 place-items-center rounded-full text-ink transition-colors hover:bg-ink/5"
              aria-label={hydrated && count > 0 ? `Корзина, ${count} в корзине` : "Корзина"}
              data-testid="header-cart"
            >
              <ShoppingBag className="h-[1.4rem] w-[1.4rem]" strokeWidth={1.7} />
              {hydrated && count > 0 && (
                <span
                  key={count}
                  data-testid="cart-count"
                  className="absolute top-0.5 right-0 grid h-5 min-w-5 animate-pop place-items-center rounded-full bg-burgundy px-1 text-[0.7rem] font-bold text-cream ring-2 ring-cream"
                >
                  {count > 99 ? "99+" : count}
                </span>
              )}
            </button>
            <Link href={orderHref} className={buttonClasses("primary", "sm", "hidden px-5 sm:inline-flex")}>
              Заказать
            </Link>
            <button
              type="button"
              onClick={() => setMenuOpen((open) => !open)}
              className="grid h-11 w-11 place-items-center rounded-full text-ink transition-colors hover:bg-ink/5 lg:hidden"
              aria-label={menuOpen ? "Закрыть меню" : "Открыть меню"}
              aria-expanded={menuOpen}
              aria-controls="mobile-menu"
            >
              {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </Container>
      </header>

      {/* Mobile menu — rendered outside <header>: its backdrop-filter would trap position:fixed */}
      <div
        id="mobile-menu"
        className={cn(
          "grain fixed inset-x-0 top-16 bottom-0 z-40 overflow-y-auto bg-cream transition-[opacity,visibility] duration-300 sm:top-[76px] lg:hidden",
          menuOpen ? "visible opacity-100" : "invisible opacity-0",
        )}
        inert={!menuOpen}
      >
        <Container className="flex min-h-full flex-col pt-6 pb-[max(2rem,env(safe-area-inset-bottom))]">
          <nav aria-label="Мобильная навигация">
            <ul className="divide-y divide-ink/10 border-y border-ink/10">
              {navigation.map((item, index) => {
                const active = isActive(pathname, item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={closeMenu}
                      aria-current={active ? "page" : undefined}
                      className="flex items-center justify-between py-4"
                    >
                      <span className="flex items-baseline gap-4">
                        <span className="font-serif text-sm text-ink-muted italic">0{index + 1}</span>
                        <span
                          className={cn(
                            "font-serif text-[2rem] leading-none",
                            active ? "text-burgundy" : "text-ink",
                          )}
                        >
                          {item.label}
                        </span>
                      </span>
                      <ArrowRight className="h-5 w-5 text-ink/40" />
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
          <Link
            href={orderHref}
            onClick={closeMenu}
            className={buttonClasses("primary", "lg", "mt-8 w-full")}
          >
            Заказать
          </Link>
          <div className="mt-auto space-y-1 pt-10 text-sm text-ink-soft">
            <p>
              {siteConfig.address.street}, {siteConfig.address.city}
            </p>
            {phone.href ? (
              <a href={phone.href} className="font-semibold text-ink">
                {phone.display}
              </a>
            ) : (
              <p className="text-ink-muted">Телефон: {phone.display}</p>
            )}
          </div>
        </Container>
      </div>
    </>
  );
}
