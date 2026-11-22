/**
 * Order request schema — shared by the checkout form (instant feedback)
 * and the /api/orders route handler (authoritative validation).
 */
import { z } from "zod";
import { isValidPhone } from "@/lib/phone";
import { MAX_QUANTITY_PER_ITEM } from "@/lib/pricing";

export const orderRequestSchema = z
  .object({
    /** Generated once per checkout attempt — protects against double submits. */
    clientOrderId: z.string().min(8).max(64),
    customer: z.object({
      name: z.string().trim().min(2, "Укажите имя — минимум 2 символа").max(60, "Имя слишком длинное"),
      phone: z.string().trim().refine(isValidPhone, "Введите номер полностью: +7 (7XX) XXX-XX-XX"),
    }),
    fulfillment: z.enum(["delivery", "pickup"]),
    address: z.object({
      street: z.string().trim().max(120, "Слишком длинный адрес"),
      house: z.string().trim().max(20, "Слишком длинное значение"),
      apartment: z.string().trim().max(20, "Слишком длинное значение"),
      entrance: z.string().trim().max(10, "Слишком длинное значение"),
      floor: z.string().trim().max(10, "Слишком длинное значение"),
    }),
    comment: z.string().trim().max(500, "Комментарий — не длиннее 500 символов"),
    items: z
      .array(
        z.object({
          id: z.string().min(1).max(64),
          quantity: z.number().int().min(1).max(MAX_QUANTITY_PER_ITEM),
        }),
      )
      .min(1, "Корзина пуста")
      .max(60),
    /** Honeypot: real users never see or fill this field. */
    website: z.string().max(200).optional(),
  })
  .superRefine((data, ctx) => {
    if (data.fulfillment !== "delivery") return;
    if (data.address.street.length < 3) {
      ctx.addIssue({ code: "custom", path: ["address", "street"], message: "Укажите улицу или микрорайон" });
    }
    if (data.address.house.length === 0) {
      ctx.addIssue({ code: "custom", path: ["address", "house"], message: "Укажите номер дома" });
    }
  });

export type OrderRequest = z.infer<typeof orderRequestSchema>;

/** Field path → first error message, e.g. { "customer.phone": "…" }. */
export type FieldErrors = Record<string, string>;

export function toFieldErrors(error: z.ZodError): FieldErrors {
  const result: FieldErrors = {};
  for (const issue of error.issues) {
    const key = issue.path.join(".");
    if (!(key in result)) result[key] = issue.message;
  }
  return result;
}
