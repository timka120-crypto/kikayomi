import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";

const routes = [
  { path: "", priority: 1 },
  { path: "/menu", priority: 0.9 },
  { path: "/delivery", priority: 0.7 },
  { path: "/about", priority: 0.6 },
  { path: "/contacts", priority: 0.6 },
];

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map(({ path, priority }) => ({
    url: `${siteConfig.url}${path}`,
    changeFrequency: "weekly",
    priority,
  }));
}
