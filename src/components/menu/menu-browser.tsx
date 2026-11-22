"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Search, SearchX, X } from "lucide-react";
import { Container } from "@/components/ui/container";
import { cn } from "@/lib/cn";
import { normalizeSearch, pluralize } from "@/lib/format";
import type { CategoryId, MenuCategory, Product } from "@/types/menu";
import { ProductCard } from "./product-card";

type Filter = "all" | CategoryId;

interface MenuBrowserProps {
  categories: MenuCategory[];
  products: Product[];
}

function readCategoryFromUrl(categories: MenuCategory[]): Filter {
  const value = new URLSearchParams(window.location.search).get("category");
  return categories.some((category) => category.id === value) ? (value as CategoryId) : "all";
}

function ProductGrid({ products }: { products: Product[] }) {
  return (
    <ul className="grid gap-3 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3 lg:gap-7">
      {products.map((product) => (
        <li key={product.id}>
          <ProductCard product={product} layout="responsive" />
        </li>
      ))}
    </ul>
  );
}

export function MenuBrowser({ categories, products }: MenuBrowserProps) {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  const toolbarRef = useRef<HTMLDivElement>(null);

  // Deep links: /menu?category=pasta
  useEffect(() => {
    const fromUrl = readCategoryFromUrl(categories);
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sync with URL once after hydration
    if (fromUrl !== "all") setFilter(fromUrl);
  }, [categories]);

  const selectFilter = (next: Filter) => {
    setFilter(next);
    const url = new URL(window.location.href);
    if (next === "all") url.searchParams.delete("category");
    else url.searchParams.set("category", next);
    window.history.replaceState(window.history.state, "", url);

    // If the sticky toolbar is already stuck, jump back to the top of the list.
    const list = listRef.current;
    const toolbar = toolbarRef.current;
    if (list && toolbar) {
      const offset = toolbar.getBoundingClientRect().bottom + 8;
      const listTop = list.getBoundingClientRect().top;
      if (listTop < offset) {
        window.scrollTo({ top: window.scrollY + listTop - offset, behavior: "smooth" });
      }
    }
  };

  const normalizedQuery = normalizeSearch(query);

  const visible = useMemo(() => {
    return products.filter((product) => {
      if (filter !== "all" && product.categoryId !== filter) return false;
      if (!normalizedQuery) return true;
      const haystack = normalizeSearch(
        [product.name, product.italianName ?? "", product.description].join(" "),
      );
      return normalizedQuery.split(/\s+/).every((word) => haystack.includes(word));
    });
  }, [products, filter, normalizedQuery]);

  const counts = useMemo(() => {
    const map = new Map<CategoryId, number>();
    for (const product of products) map.set(product.categoryId, (map.get(product.categoryId) ?? 0) + 1);
    return map;
  }, [products]);

  const grouped = filter === "all" && !normalizedQuery;
  const activeCategory = categories.find((category) => category.id === filter);

  const tabs: { id: Filter; label: string; count: number }[] = [
    { id: "all", label: "Все блюда", count: products.length },
    ...categories.map((category) => ({
      id: category.id,
      label: category.name,
      count: counts.get(category.id) ?? 0,
    })),
  ];

  const searchField = (
    <label className="relative block lg:w-80 lg:shrink-0">
      <span className="sr-only">Поиск по меню</span>
      <Search className="pointer-events-none absolute top-1/2 left-4 h-4 w-4 -translate-y-1/2 text-ink-muted" />
      <input
        type="search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Найти блюдо: паста, тирамису…"
        className="h-12 w-full rounded-full border border-ink/15 bg-white pr-11 pl-11 text-ink transition-[border-color,box-shadow] outline-none placeholder:text-ink-muted/80 focus:border-burgundy focus:shadow-[0_0_0_4px_rgb(118_43_50/0.12)] [&::-webkit-search-cancel-button]:hidden"
        data-testid="menu-search"
        enterKeyHint="search"
      />
      {query && (
        <button
          type="button"
          onClick={() => setQuery("")}
          className="absolute top-1/2 right-2 grid h-8 w-8 -translate-y-1/2 place-items-center rounded-full text-ink-muted hover:bg-ink/5 hover:text-ink"
          aria-label="Очистить поиск"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </label>
  );

  return (
    <>
      {/* Phones/tablets: search scrolls with the page to save screen height */}
      <Container className="pb-4 lg:hidden">{searchField}</Container>

      {/* Sticky toolbar: categories (+ search on desktop) */}
      <div
        ref={toolbarRef}
        className="sticky top-16 z-30 border-y border-ink/10 bg-cream/92 backdrop-blur-md sm:top-[76px]"
      >
        <Container className="flex flex-col gap-3 py-3 lg:flex-row lg:items-center lg:gap-6">
          <div className="hidden lg:block">{searchField}</div>

          <nav aria-label="Категории меню" className="-mx-4 min-w-0 sm:-mx-6 lg:mx-0 lg:flex-1">
            <ul className="no-scrollbar flex snap-x gap-2 overflow-x-auto px-4 sm:px-6 lg:px-0">
              {tabs.map((tab) => {
                const active = filter === tab.id;
                return (
                  <li key={tab.id} className="snap-start">
                    <button
                      type="button"
                      onClick={() => selectFilter(tab.id)}
                      aria-pressed={active}
                      data-testid={`category-${tab.id}`}
                      className={cn(
                        "inline-flex h-11 items-center gap-1.5 rounded-full px-4 text-sm font-semibold whitespace-nowrap transition-colors duration-300",
                        active
                          ? "bg-burgundy text-cream"
                          : "bg-white text-ink ring-1 ring-ink/10 hover:ring-ink/30",
                      )}
                    >
                      {tab.label}
                      <span
                        className={cn("text-xs tabular-nums", active ? "text-cream/70" : "text-ink-muted")}
                      >
                        {tab.count}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>
        </Container>
      </div>

      <Container className="pt-8 pb-20 sm:pt-12 sm:pb-28">
        <div ref={listRef} className="scroll-mt-40">
          {!grouped && (
            <div className="mb-6 flex flex-wrap items-end justify-between gap-3 sm:mb-8">
              <div>
                {activeCategory && !normalizedQuery ? (
                  <>
                    <p className="font-serif text-lg text-olive-deep italic">{activeCategory.italian}</p>
                    <h2 className="text-4xl sm:text-5xl">{activeCategory.name}</h2>
                    <p className="mt-2 text-ink-soft">{activeCategory.description}</p>
                  </>
                ) : (
                  <h2 className="text-3xl sm:text-4xl" data-testid="search-summary">
                    {visible.length > 0
                      ? `Найдено ${visible.length} ${pluralize(visible.length, ["блюдо", "блюда", "блюд"])}`
                      : "Ничего не нашлось"}
                    {activeCategory && (
                      <span className="text-ink-muted"> в разделе «{activeCategory.name}»</span>
                    )}
                  </h2>
                )}
              </div>
            </div>
          )}

          {visible.length === 0 ? (
            <div className="flex flex-col items-center rounded-card border border-dashed border-ink/20 px-6 py-16 text-center">
              <SearchX className="h-10 w-10 text-ink-muted" strokeWidth={1.4} />
              <p className="mt-4 font-serif text-2xl">По запросу «{query}» блюд не найдено</p>
              <p className="mt-2 text-sm text-ink-soft">
                Попробуйте другое слово или посмотрите все разделы.
              </p>
              <button
                type="button"
                onClick={() => {
                  setQuery("");
                  selectFilter("all");
                }}
                className="mt-6 rounded-full bg-ink px-6 py-3 text-sm font-semibold text-cream hover:bg-burgundy"
              >
                Сбросить поиск
              </button>
            </div>
          ) : grouped ? (
            <div className="space-y-16 sm:space-y-20">
              {categories.map((category) => {
                const items = visible.filter((product) => product.categoryId === category.id);
                if (items.length === 0) return null;
                return (
                  <section key={category.id} aria-labelledby={`cat-${category.id}`}>
                    <div className="mb-6 flex items-end justify-between gap-4 border-b border-ink/10 pb-4 sm:mb-8">
                      <div>
                        <p className="font-serif text-lg text-olive-deep italic">{category.italian}</p>
                        <h2 id={`cat-${category.id}`} className="text-4xl sm:text-5xl">
                          {category.name}
                        </h2>
                      </div>
                      <p className="hidden max-w-xs text-right text-sm text-ink-soft sm:block">
                        {category.description}
                      </p>
                    </div>
                    <ProductGrid products={items} />
                  </section>
                );
              })}
            </div>
          ) : (
            <ProductGrid products={visible} />
          )}
        </div>
      </Container>
    </>
  );
}
