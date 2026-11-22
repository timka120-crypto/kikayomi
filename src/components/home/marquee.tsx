const words = ["Pizza", "Pasta", "Antipasti", "Insalate", "Zuppe", "Dolci", "Caffè"];

/** Burgundy ribbon with slowly drifting Italian words. */
export function Marquee() {
  const row = [...words, ...words];
  return (
    <div
      className="relative overflow-hidden border-y border-burgundy-dark bg-burgundy py-4 text-cream sm:py-5"
      aria-hidden
    >
      <div className="flex w-max animate-marquee">
        {[0, 1].map((copy) => (
          <ul key={copy} className="flex shrink-0 items-center">
            {row.map((word, index) => (
              <li key={`${copy}-${index}`} className="flex items-center">
                <span className="px-6 font-serif text-3xl italic sm:px-8 sm:text-4xl">{word}</span>
                <span className="text-lg text-cream/50">✦</span>
              </li>
            ))}
          </ul>
        ))}
      </div>
    </div>
  );
}
