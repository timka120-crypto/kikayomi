import { AboutSection } from "@/components/home/about-section";
import { Advantages } from "@/components/home/advantages";
import { CtaBanner } from "@/components/home/cta-banner";
import { Hero } from "@/components/home/hero";
import { LocationSection } from "@/components/home/location-section";
import { Marquee } from "@/components/home/marquee";
import { PopularDishes } from "@/components/home/popular-dishes";

export default function HomePage() {
  return (
    <>
      <Hero />
      <Marquee />
      <PopularDishes />
      <AboutSection />
      <Advantages />
      <LocationSection />
      <CtaBanner />
    </>
  );
}
