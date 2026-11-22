import type { Metadata, Viewport } from "next";
import { Cormorant_Garamond, Manrope } from "next/font/google";
import { CartDrawer } from "@/components/cart/cart-drawer";
import { Footer } from "@/components/layout/footer";
import { Header } from "@/components/layout/header";
import { MobileCartBar } from "@/components/layout/mobile-cart-bar";
import { Toaster } from "@/components/layout/toaster";
import { UIProvider } from "@/components/providers/ui-provider";
import { siteConfig } from "@/config/site";
import { getPhone } from "@/lib/contacts";
import "./globals.css";

const cormorant = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin", "cyrillic"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: "BEKAKOTAK — итальянское кафе в Алматы",
    template: "%s · BEKAKOTAK",
  },
  description: siteConfig.description,
  applicationName: siteConfig.name,
  keywords: ["итальянское кафе", "пицца Алматы", "паста", "доставка еды Алматы", "BekaKotak"],
  openGraph: {
    type: "website",
    locale: siteConfig.locale,
    siteName: siteConfig.name,
    title: "BEKAKOTAK — итальянское кафе в Алматы",
    description: siteConfig.description,
    images: [{ url: "/images/site/hero-pizza-oven.jpg", width: 2200, height: 1469, alt: "Пицца BekaKotak" }],
  },
  twitter: { card: "summary_large_image" },
  alternates: { canonical: "/" },
};

export const viewport: Viewport = {
  themeColor: "#f6f0e5",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

function RestaurantJsonLd() {
  const phone = getPhone();
  const data = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    name: siteConfig.brand,
    url: siteConfig.url,
    image: `${siteConfig.url}/images/site/hero-pizza-oven.jpg`,
    servesCuisine: "Italian",
    hasMenu: `${siteConfig.url}/menu`,
    address: {
      "@type": "PostalAddress",
      streetAddress: siteConfig.address.street,
      addressLocality: siteConfig.address.city,
      addressCountry: siteConfig.address.countryCode,
    },
    ...(phone.href ? { telephone: phone.display } : {}),
    ...(siteConfig.openingHoursSchema ? { openingHours: siteConfig.openingHoursSchema } : {}),
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ru" className={`${cormorant.variable} ${manrope.variable} antialiased`}>
      <body className="flex min-h-dvh flex-col">
        <noscript>
          <style>{`.reveal{opacity:1!important;transform:none!important}`}</style>
        </noscript>
        <RestaurantJsonLd />
        <UIProvider>
          <a
            href="#main"
            className="sr-only z-[100] rounded-full bg-ink px-4 py-2 text-cream focus:not-sr-only focus:fixed focus:top-3 focus:left-3"
          >
            Перейти к содержимому
          </a>
          <Header />
          <main id="main" className="flex-1">
            {children}
          </main>
          <Footer />
          <MobileCartBar />
          <CartDrawer />
          <Toaster />
        </UIProvider>
      </body>
    </html>
  );
}
