import { FlaskConical } from "lucide-react";
import { isDemoMenu } from "@/lib/menu";
import { cn } from "@/lib/cn";

/** Shown while src/data/menu.ts still contains test dishes and prices. */
export function DemoMenuNotice({ className }: { className?: string }) {
  if (!isDemoMenu) return null;
  return (
    <p
      className={cn(
        "flex items-start gap-2.5 rounded-2xl border border-dashed border-olive/40 bg-olive-soft/60 px-4 py-3 text-sm leading-relaxed text-olive-deep",
        className,
      )}
      data-testid="demo-menu-notice"
    >
      <FlaskConical className="mt-0.5 h-4 w-4 shrink-0" />
      <span>
        <strong className="font-semibold">Демо-меню.</strong> Блюда, состав и цены — тестовые и будут заменены
        на актуальные.
      </span>
    </p>
  );
}
