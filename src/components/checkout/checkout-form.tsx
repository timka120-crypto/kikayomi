"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { AlertCircle, ArrowRight, Bike, LoaderCircle, Lock, PencilLine, Store } from "lucide-react";
import { WhatsAppIcon } from "@/components/brand/social-icons";
import { CartEmpty } from "@/components/cart/cart-contents";
import { CartSummary } from "@/components/cart/cart-summary";
import { useUI } from "@/components/providers/ui-provider";
import { buttonClasses } from "@/components/ui/button";
import { siteConfig } from "@/config/site";
import { useCart } from "@/lib/cart/use-cart";
import { cn } from "@/lib/cn";
import { getPhone, getWhatsAppUrl } from "@/lib/contacts";
import { formatPrice } from "@/lib/format";
import { readSavedCustomer, saveCustomer, saveLastOrder, submitOrder } from "@/lib/orders/client";
import { orderRequestSchema, toFieldErrors, type OrderRequest } from "@/lib/orders/schema";
import type { OrderErrorResponse } from "@/lib/orders/types";
import { formatNationalInput, phoneDigits } from "@/lib/phone";
import type { FulfillmentMethod } from "@/lib/pricing";
import { FormField } from "./form-field";

interface FormState {
  name: string;
  phone: string;
  street: string;
  house: string;
  apartment: string;
  entrance: string;
  floor: string;
  comment: string;
  website: string;
}

const EMPTY: FormState = {
  name: "",
  phone: "",
  street: "",
  house: "",
  apartment: "",
  entrance: "",
  floor: "",
  comment: "",
  website: "",
};

/** Schema error path → form field name. */
const ERROR_FIELD: Record<string, keyof FormState> = {
  "customer.name": "name",
  "customer.phone": "phone",
  "address.street": "street",
  "address.house": "house",
  "address.apartment": "apartment",
  "address.entrance": "entrance",
  "address.floor": "floor",
  comment: "comment",
};

const FIELD_ORDER: (keyof FormState)[] = [
  "name",
  "phone",
  "street",
  "house",
  "apartment",
  "entrance",
  "floor",
  "comment",
];

type Errors = Partial<Record<keyof FormState, string>>;

function mapErrors(fieldErrors: Record<string, string>): Errors {
  const errors: Errors = {};
  for (const [path, message] of Object.entries(fieldErrors)) {
    const field = ERROR_FIELD[path];
    if (field && !errors[field]) errors[field] = message;
  }
  return errors;
}

function newClientOrderId() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function CheckoutForm({ orderingEnabled }: { orderingEnabled: boolean }) {
  const router = useRouter();
  const { lines, totals, fulfillment, actions, hydrated } = useCart();
  const { openCart } = useUI();
  const [form, setForm] = useState<FormState>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof FormState, boolean>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<OrderErrorResponse | null>(null);
  const clientOrderId = useRef<string | null>(null);
  const errorBoxRef = useRef<HTMLDivElement>(null);
  const phone = getPhone();

  // Prefill contact details saved on this device after a previous order.
  useEffect(() => {
    const saved = readSavedCustomer();
    if (!saved) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time prefill from localStorage
    setForm((current) => ({
      ...current,
      name: current.name || saved.name || "",
      phone: current.phone || formatNationalInput(saved.phone || ""),
      street: current.street || saved.street || "",
      house: current.house || saved.house || "",
      apartment: current.apartment || saved.apartment || "",
      entrance: current.entrance || saved.entrance || "",
      floor: current.floor || saved.floor || "",
    }));
  }, []);

  const buildPayload = (state: FormState, method: FulfillmentMethod, orderId: string): OrderRequest => ({
    clientOrderId: orderId,
    customer: { name: state.name, phone: `+7${phoneDigits(state.phone)}` },
    fulfillment: method,
    address: {
      street: method === "delivery" ? state.street : "",
      house: method === "delivery" ? state.house : "",
      apartment: method === "delivery" ? state.apartment : "",
      entrance: method === "delivery" ? state.entrance : "",
      floor: method === "delivery" ? state.floor : "",
    },
    comment: state.comment,
    items: lines.map((line) => ({ id: line.product.id, quantity: line.quantity })),
    website: state.website || undefined,
  });

  const validate = (state: FormState, method: FulfillmentMethod): Errors => {
    const result = orderRequestSchema.safeParse(buildPayload(state, method, "validation-only"));
    return result.success ? {} : mapErrors(toFieldErrors(result.error));
  };

  const update = (field: keyof FormState, value: string) => {
    const next = { ...form, [field]: value };
    setForm(next);
    if (touched[field] || errors[field]) {
      const nextErrors = validate(next, fulfillment);
      setErrors((current) => ({ ...current, [field]: nextErrors[field] }));
    }
  };

  const blur = (field: keyof FormState) => {
    setTouched((current) => ({ ...current, [field]: true }));
    const nextErrors = validate(form, fulfillment);
    setErrors((current) => ({ ...current, [field]: nextErrors[field] }));
  };

  const setMethod = (method: FulfillmentMethod) => {
    actions.setFulfillment(method);
    setServerError(null);
    if (method === "pickup") {
      setErrors((current) => ({ ...current, street: undefined, house: undefined }));
    }
  };

  const focusFirstError = (fieldErrors: Errors) => {
    const first = FIELD_ORDER.find((field) => fieldErrors[field]);
    if (first) document.getElementById(`checkout-${first}`)?.focus();
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setServerError(null);

    const fieldErrors = validate(form, fulfillment);
    setErrors(fieldErrors);
    setTouched(Object.fromEntries(FIELD_ORDER.map((field) => [field, true])));
    if (Object.keys(fieldErrors).length > 0) {
      focusFirstError(fieldErrors);
      return;
    }
    if (fulfillment === "delivery" && totals.minOrderShortfall > 0) {
      setServerError({
        code: "MIN_ORDER",
        message: `Минимальная сумма заказа на доставку — ещё ${formatPrice(totals.minOrderShortfall)}. Добавьте блюда или выберите самовывоз.`,
      });
      return;
    }

    clientOrderId.current ??= newClientOrderId();
    setSubmitting(true);
    const result = await submitOrder(buildPayload(form, fulfillment, clientOrderId.current));
    setSubmitting(false);

    if (result.ok) {
      saveLastOrder(result.confirmation);
      saveCustomer({
        name: form.name.trim(),
        phone: `+7${phoneDigits(form.phone)}`,
        street: form.street.trim(),
        house: form.house.trim(),
        apartment: form.apartment.trim(),
        entrance: form.entrance.trim(),
        floor: form.floor.trim(),
      });
      // Cart is cleared only after the server confirmed the order.
      actions.clear();
      clientOrderId.current = null;
      setForm(EMPTY);
      setErrors({});
      setTouched({});
      router.replace("/checkout/success");
      return;
    }

    if (result.error.fieldErrors) {
      const mapped = mapErrors(result.error.fieldErrors);
      setErrors(mapped);
      focusFirstError(mapped);
    }
    setServerError(result.error);
    requestAnimationFrame(() => errorBoxRef.current?.scrollIntoView({ behavior: "smooth", block: "center" }));
  };

  if (!hydrated) {
    return <CheckoutSkeleton />;
  }

  if (lines.length === 0) {
    return (
      <div className="rounded-card bg-white ring-1 ring-ink/5">
        <CartEmpty />
      </div>
    );
  }

  const isDelivery = fulfillment === "delivery";
  const whatsappText = [
    `Здравствуйте! Хочу сделать заказ (${isDelivery ? "доставка" : "самовывоз"}):`,
    ...lines.map((line) => `• ${line.product.name} × ${line.quantity}`),
    `Сумма: ${formatPrice(totals.subtotal)}`,
  ].join("\n");
  const whatsappUrl = getWhatsAppUrl(whatsappText);

  const inputProps = (field: keyof FormState) => ({
    id: `checkout-${field}`,
    name: field,
    value: form[field],
    onChange: (event: { target: { value: string } }) => update(field, event.target.value),
    onBlur: () => blur(field),
    "aria-invalid": errors[field] ? true : undefined,
    "aria-describedby": errors[field] ? `checkout-${field}-error` : undefined,
    className: "field",
  });

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      className="grid gap-8 lg:grid-cols-[1fr_420px] lg:items-start lg:gap-10"
      data-testid="checkout-form"
    >
      <div className="space-y-6">
        {!orderingEnabled && (
          <div
            className="flex gap-3 rounded-card border border-dashed border-burgundy/40 bg-burgundy-soft/60 p-5 text-sm leading-relaxed text-burgundy-dark"
            data-testid="ordering-disabled-notice"
          >
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">Онлайн-приём заказов скоро заработает</p>
              <p className="mt-1 text-burgundy-dark/85">
                Система обработки заказов ещё подключается, поэтому заказ с сайта пока не будет передан в
                кафе. Корзина сохранится.
                {phone.href && (
                  <>
                    {" "}
                    Оформить заказ можно по телефону{" "}
                    <a href={phone.href} className="font-semibold underline">
                      {phone.display}
                    </a>
                    .
                  </>
                )}
              </p>
            </div>
          </div>
        )}

        {/* 1. Fulfillment */}
        <fieldset className="rounded-card bg-white p-5 ring-1 ring-ink/5 sm:p-7">
          <legend className="sr-only">Способ получения</legend>
          <h2 className="flex items-baseline gap-3 font-serif text-[1.75rem]">
            <span className="font-serif text-base text-burgundy italic">01</span> Способ получения
          </h2>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {(
              [
                { value: "delivery", icon: Bike, title: "Доставка", text: "Привезём по вашему адресу" },
                { value: "pickup", icon: Store, title: "Самовывоз", text: siteConfig.address.street },
              ] as const
            ).map((option) => {
              const checked = fulfillment === option.value;
              return (
                <label
                  key={option.value}
                  className={cn(
                    "relative flex cursor-pointer items-center gap-4 rounded-2xl border p-4 transition-[border-color,background-color,box-shadow] duration-200",
                    checked
                      ? "border-burgundy bg-burgundy-soft/50 shadow-[0_0_0_3px_rgb(118_43_50/0.12)]"
                      : "border-ink/15 hover:border-ink/35",
                  )}
                >
                  <input
                    type="radio"
                    name="fulfillment"
                    value={option.value}
                    checked={checked}
                    onChange={() => setMethod(option.value)}
                    className="peer sr-only"
                    data-testid={`fulfillment-${option.value}`}
                  />
                  <span
                    className={cn(
                      "grid h-11 w-11 shrink-0 place-items-center rounded-full",
                      checked ? "bg-burgundy text-cream" : "bg-cream-deep text-ink",
                    )}
                  >
                    <option.icon className="h-5 w-5" strokeWidth={1.8} />
                  </span>
                  <span className="min-w-0">
                    <span className="block font-semibold text-ink">{option.title}</span>
                    <span className="block truncate text-sm text-ink-muted">{option.text}</span>
                  </span>
                  <span
                    aria-hidden
                    className={cn(
                      "ml-auto grid h-5 w-5 shrink-0 place-items-center rounded-full border-2",
                      checked ? "border-burgundy" : "border-ink/25",
                    )}
                  >
                    {checked && <span className="h-2.5 w-2.5 rounded-full bg-burgundy" />}
                  </span>
                </label>
              );
            })}
          </div>
        </fieldset>

        {/* 2. Contacts */}
        <section
          className="rounded-card bg-white p-5 ring-1 ring-ink/5 sm:p-7"
          aria-labelledby="contacts-heading"
        >
          <h2 id="contacts-heading" className="flex items-baseline gap-3 font-serif text-[1.75rem]">
            <span className="font-serif text-base text-burgundy italic">02</span> Контактные данные
          </h2>
          <p className="mt-1 text-xs text-ink-muted">
            Поля со звёздочкой <span className="text-burgundy">*</span> обязательны
          </p>
          <div className="mt-5 grid gap-5 sm:grid-cols-2">
            <FormField id="checkout-name" label="Имя" required error={errors.name}>
              <input
                {...inputProps("name")}
                type="text"
                autoComplete="given-name"
                placeholder="Как к вам обращаться"
                maxLength={60}
              />
            </FormField>
            <FormField
              id="checkout-phone"
              label="Телефон"
              required
              error={errors.phone}
              hint="Позвоним, чтобы подтвердить заказ"
            >
              <div className="relative">
                <span className="pointer-events-none absolute top-1/2 left-4 -translate-y-1/2 font-semibold text-ink">
                  +7
                </span>
                <input
                  {...inputProps("phone")}
                  onChange={(event) => update("phone", formatNationalInput(event.target.value))}
                  type="tel"
                  inputMode="tel"
                  autoComplete="tel-national"
                  placeholder="(700) 000-00-00"
                  className="field pl-11"
                />
              </div>
            </FormField>
          </div>
        </section>

        {/* 3. Address / pickup */}
        <section
          className="rounded-card bg-white p-5 ring-1 ring-ink/5 sm:p-7"
          aria-labelledby="address-heading"
        >
          <h2 id="address-heading" className="flex items-baseline gap-3 font-serif text-[1.75rem]">
            <span className="font-serif text-base text-burgundy italic">03</span>
            {isDelivery ? "Адрес доставки" : "Самовывоз"}
          </h2>

          {isDelivery ? (
            <div className="mt-5 grid grid-cols-2 gap-x-4 gap-y-5 sm:grid-cols-4">
              <FormField
                id="checkout-street"
                label="Улица или микрорайон"
                required
                error={errors.street}
                className="col-span-2 sm:col-span-4"
              >
                <input
                  {...inputProps("street")}
                  type="text"
                  autoComplete="address-line1"
                  placeholder="Например: ул. Абая"
                  maxLength={120}
                />
              </FormField>
              <FormField id="checkout-house" label="Дом" required error={errors.house}>
                <input {...inputProps("house")} type="text" placeholder="12А" maxLength={20} />
              </FormField>
              <FormField id="checkout-apartment" label="Кв. / офис" error={errors.apartment}>
                <input {...inputProps("apartment")} type="text" placeholder="45" maxLength={20} />
              </FormField>
              <FormField id="checkout-entrance" label="Подъезд" error={errors.entrance}>
                <input
                  {...inputProps("entrance")}
                  type="text"
                  inputMode="numeric"
                  placeholder="2"
                  maxLength={10}
                />
              </FormField>
              <FormField id="checkout-floor" label="Этаж" error={errors.floor}>
                <input
                  {...inputProps("floor")}
                  type="text"
                  inputMode="numeric"
                  placeholder="5"
                  maxLength={10}
                />
              </FormField>
              <FormField
                id="checkout-comment"
                label="Комментарий курьеру"
                error={errors.comment}
                className="col-span-2 sm:col-span-4"
              >
                <textarea
                  {...inputProps("comment")}
                  rows={3}
                  maxLength={500}
                  placeholder="Код домофона, ориентир, пожелания к заказу"
                  className="field resize-y"
                />
              </FormField>
            </div>
          ) : (
            <div className="mt-5 space-y-5">
              <div className="rounded-2xl bg-cream p-4">
                <p className="text-sm text-ink-muted">Заберите заказ по адресу</p>
                <p className="mt-1 font-semibold text-ink">
                  {siteConfig.address.street}, {siteConfig.address.city}
                </p>
                <p className="mt-1 text-sm text-ink-muted">Мы сообщим, когда заказ будет готов.</p>
              </div>
              <FormField id="checkout-comment" label="Комментарий к заказу" error={errors.comment}>
                <textarea
                  {...inputProps("comment")}
                  rows={3}
                  maxLength={500}
                  placeholder="Пожелания к заказу, удобное время"
                  className="field resize-y"
                />
              </FormField>
            </div>
          )}

          {/* Honeypot — hidden from people, bots fill it in */}
          <div aria-hidden className="absolute -left-[9999px] h-px w-px overflow-hidden">
            <label htmlFor="checkout-website">Website</label>
            <input
              id="checkout-website"
              name="website"
              tabIndex={-1}
              autoComplete="off"
              value={form.website}
              onChange={(event) => setForm({ ...form, website: event.target.value })}
            />
          </div>
        </section>
      </div>

      {/* Summary */}
      <aside className="lg:sticky lg:top-28" aria-labelledby="summary-heading">
        <div className="rounded-card bg-white p-5 ring-1 ring-ink/5 sm:p-7">
          <div className="flex items-center justify-between gap-3">
            <h2 id="summary-heading" className="font-serif text-[1.75rem]">
              Ваш заказ
            </h2>
            <button
              type="button"
              onClick={openCart}
              className="inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-semibold text-burgundy hover:bg-burgundy-soft"
            >
              <PencilLine className="h-4 w-4" />
              Изменить
            </button>
          </div>

          <ul className="mt-4 divide-y divide-ink/10" data-testid="checkout-items">
            {lines.map((line) => (
              <li key={line.product.id} className="flex items-center gap-3 py-3">
                <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-xl bg-cream-deep">
                  <Image src={line.product.image.src} alt="" fill sizes="56px" className="object-cover" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-semibold text-ink">{line.product.name}</p>
                  <p className="text-sm text-ink-muted tabular-nums">
                    {line.quantity} × {formatPrice(line.product.price)}
                  </p>
                </div>
                <p className="font-semibold text-ink tabular-nums">{formatPrice(line.lineTotal)}</p>
              </li>
            ))}
          </ul>

          <CartSummary totals={totals} className="mt-4 border-t border-ink/10 pt-5" />

          {serverError && (
            <div
              ref={errorBoxRef}
              role="alert"
              data-testid="checkout-error"
              data-error-code={serverError.code}
              className="mt-5 rounded-2xl border border-[#b42318]/25 bg-[#fdf1ef] p-4 text-sm leading-relaxed text-[#7a1d14]"
            >
              <p className="flex gap-2 font-semibold">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                {serverError.message}
              </p>
              {serverError.unavailableItems && serverError.unavailableItems.length > 0 && (
                <p className="mt-2 pl-6">Недоступно: {serverError.unavailableItems.join(", ")}</p>
              )}
              {serverError.code === "ORDERS_NOT_CONFIGURED" && (whatsappUrl || phone.href) && (
                <div className="mt-3 flex flex-wrap gap-2 pl-6">
                  {phone.href && (
                    <a
                      href={phone.href}
                      className="rounded-full bg-[#7a1d14] px-4 py-2 font-semibold text-white"
                    >
                      Позвонить {phone.display}
                    </a>
                  )}
                  {whatsappUrl && (
                    <a
                      href={whatsappUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 rounded-full bg-olive px-4 py-2 font-semibold text-white"
                    >
                      <WhatsAppIcon className="h-4 w-4" />
                      Отправить в WhatsApp
                    </a>
                  )}
                </div>
              )}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className={buttonClasses("primary", "lg", "mt-6 w-full")}
            data-testid="confirm-order"
          >
            {submitting ? (
              <>
                <LoaderCircle className="h-5 w-5 animate-spin" />
                Отправляем заказ…
              </>
            ) : (
              <>
                Подтвердить заказ
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>

          <p className="mt-4 flex gap-2 text-xs leading-relaxed text-ink-muted">
            <Lock className="mt-px h-3.5 w-3.5 shrink-0" />
            <span>
              {siteConfig.payment.note} Нажимая кнопку, вы соглашаетесь на обработку контактных данных для
              выполнения заказа.
            </span>
          </p>
        </div>
        <Link
          href="/menu"
          className="mt-4 block text-center text-sm font-semibold text-ink-soft underline-offset-4 hover:text-burgundy hover:underline"
        >
          Вернуться в меню
        </Link>
      </aside>
    </form>
  );
}

export function CheckoutSkeleton() {
  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_420px] lg:gap-10" aria-busy="true" aria-label="Загрузка">
      <div className="space-y-6">
        {[0, 1, 2].map((key) => (
          <div key={key} className="h-48 animate-pulse rounded-card bg-white/70 ring-1 ring-ink/5" />
        ))}
      </div>
      <div className="h-96 animate-pulse rounded-card bg-white/70 ring-1 ring-ink/5" />
    </div>
  );
}
