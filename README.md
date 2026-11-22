# BEKAKOTAK — сайт итальянского кафе

Сайт итальянского кафе **BekaKotak** (Алматы, ул. Розыбакиева, 66) с онлайн-заказом: меню с поиском и
категориями, корзина, оформление заказа с доставкой или самовывозом, передача заказа в кафе (Telegram,
webhook) и страница подтверждения с номером заказа.

**Стек:** Next.js 16 (App Router, Cache Components) · React 19 · TypeScript · Tailwind CSS 4 · Lucide · Zod.

---

## Быстрый старт

Нужен Node.js 20.9+ (рекомендуется 22).

```bash
npm install
npm run dev          # http://localhost:3000
```

Production-сборка:

```bash
npm run build
npm run start        # http://localhost:3000
```

### Проверить приём заказов локально

По умолчанию ни один канал заказов не подключён, и сайт **честно** сообщает на странице оформления:
«Онлайн-приём заказов скоро заработает», а корзина при этом не очищается. Чтобы прогнать весь путь заказа
локально, включите запись заказов в файл:

```bash
cp .env.example .env.local
# в .env.local: ORDERS_LOCAL_FILE=true
npm run dev
```

Каждый заказ появится одной строкой JSON в `.data/orders.jsonl`.

---

## Что заполнить перед запуском

| Что | Где | Сейчас |
| --- | --- | --- |
| Телефон, WhatsApp, e-mail | `src/config/site.ts` → `contacts` | заглушка `+7 (XXX) XXX-XX-XX` — ссылка не активна |
| График работы | `src/config/site.ts` → `hours`, `openingHoursSchema` | заглушка `XX:XX – XX:XX` |
| Соцсети | `src/config/site.ts` → `socials` | `url: null` — иконки не кликабельны, подпись «скоро появятся» |
| Стоимость, минимум, время и зона доставки | `src/config/site.ts` → `delivery` | `null` — на сайте «Уточняется», доставка «Рассчитает оператор» |
| Меню и цены | `src/data/menu.ts` | **демо-данные**, на сайте пометка «Демо-меню». После замены: `MENU_IS_DEMO = false` |
| Фото | `public/images/menu`, `public/images/site` | стоковые фото Unsplash (см. `public/images/CREDITS.md`) — интерьер и повар не из BekaKotak, замените на свои |
| Тексты «О кафе» | `src/content/about.ts` | нейтральные тексты без выдуманных фактов |
| Адрес сайта | переменная `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` |
| Канал заказов | переменные окружения (см. ниже) | не подключён |

Сайт сам подстраивается под заполненные данные: когда указана стоимость доставки, она включается в итог;
когда указан телефон, он становится кликабельным (`tel:`); когда указан WhatsApp, появляются кнопки WhatsApp.

---

## Структура проекта

```
src/
├── app/                          Страницы (App Router)
│   ├── page.tsx                  Главная
│   ├── menu/page.tsx             Меню: категории, поиск, количество
│   ├── about/page.tsx            О кафе
│   ├── delivery/page.tsx         Доставка и самовывоз
│   ├── contacts/page.tsx         Контакты и карта
│   ├── cart/page.tsx             Корзина (страница; также есть выезжающая панель)
│   ├── checkout/page.tsx         Оформление заказа
│   ├── checkout/success/page.tsx Подтверждение с номером заказа
│   ├── api/orders/route.ts       POST /api/orders — приём заказа
│   ├── layout.tsx                Шрифты, SEO, JSON-LD, шапка, подвал, корзина
│   ├── globals.css               Дизайн-токены (палитра, шрифты, анимации)
│   └── sitemap.ts, robots.ts, manifest.ts, icon.svg, not-found.tsx
├── components/
│   ├── layout/                   Header, Footer, MobileCartBar, Toaster, SocialLinks
│   ├── home/                     Hero, Marquee, PopularDishes, AboutSection, Advantages, LocationSection, CtaBanner
│   ├── menu/                     MenuBrowser, ProductCard, DemoMenuNotice
│   ├── cart/                     CartDrawer, CartContents, CartLineItem, CartSummary, QuantityStepper
│   ├── checkout/                 CheckoutForm, OrderSuccess, FormField
│   ├── location/                 ContactDetails, DeliveryTerms, LocationMap (блок «Доставка»)
│   ├── brand/                    Logo, иконки соцсетей
│   ├── providers/ui-provider.tsx Состояние корзины-панели и уведомлений
│   └── ui/                       Button, Container, PageHero, SectionHeading, Reveal
├── config/site.ts                ⚙️ Контакты, график, доставка, оплата — всё редактируемое
├── data/menu.ts                  🍕 Меню (демо) — категории и блюда
├── content/about.ts              Тексты о кафе
├── lib/
│   ├── menu.ts                   Репозиторий меню (точка подключения БД / CMS)
│   ├── pricing.ts                Расчёт суммы, доставки, минимального заказа (общий для клиента и сервера)
│   ├── cart/                     Корзина: хранилище в localStorage + хук useCart
│   ├── orders/                   Заказы: схема (Zod), номер заказа, создание, защита, клиент
│   │   └── channels/             Каналы передачи заказа: telegram, webhook, local-file
│   ├── payments/types.ts         Точка подключения онлайн-оплаты
│   ├── phone.ts, format.ts, contacts.ts, cn.ts
└── types/menu.ts
tests/e2e/                        Сквозные тесты Playwright
public/images/                    Фото блюд (38) и атмосферы (7), CREDITS.md
```

---

## Как устроен заказ

1. Гость добавляет блюда в корзину. Корзина хранится в `localStorage` (переживает перезагрузку,
   синхронизируется между вкладками). Хранятся только `id` и количество: цены и названия всегда берутся из
   актуального меню.
2. На странице оформления форма проверяется сразу (та же Zod-схема, что и на сервере). Телефон вводится с
   маской `+7 (7XX) XXX-XX-XX`.
3. `POST /api/orders`:
   - проверяет данные и отсекает ботов (скрытое поле-ловушка, ограничение частоты запросов);
   - **пересчитывает цены на сервере** по меню (цены от браузера не принимаются), проверяет доступность блюд
     и минимальную сумму доставки;
   - присваивает уникальный номер вида `BK-261122-7KQ3M`;
   - отправляет заказ во все настроенные каналы. Заказ принят, если его доставил хотя бы один канал;
   - повторная отправка того же оформления (двойной клик, сбой сети) не создаёт дубль.
4. **Корзина очищается только после ответа сервера «заказ принят».** При любой ошибке (канал не
   настроен, сбой Telegram, нет сети) гость видит понятное сообщение, а корзина остаётся на месте.
5. Страница подтверждения показывает номер заказа и состав; контактные данные запоминаются на устройстве
   гостя для следующего заказа.

Коды ответа API: `201` принят · `422` ошибка в форме · `409` блюдо недоступно · `503` канал заказов не
подключён · `502` каналы не ответили · `429` слишком много запросов.

---

## Интеграции для реального приёма заказов

### 1. Telegram-уведомления владельцу (рекомендуется начать с этого)

1. Создайте бота у [@BotFather](https://t.me/BotFather) → получите токен.
2. Добавьте бота в чат сотрудников (или напишите ему лично) и узнайте `chat_id` — например, через
   `https://api.telegram.org/bot<ТОКЕН>/getUpdates` после любого сообщения в чат.
3. Задайте переменные окружения:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC...
   TELEGRAM_CHAT_ID=-1001234567890      # можно несколько через запятую
   ```
4. Перезапустите сайт — предупреждение на странице оформления исчезнет, заказы начнут приходить в чат
   (номер, имя, телефон, адрес, состав, суммы, комментарий).

### 2. Webhook: CRM, кассовая система, таблицы

`ORDER_WEBHOOK_URL` получает `POST { "event": "order.created", "order": {...} }`. Подходит для n8n, Make,
Zapier, Google Sheets, amoCRM/Bitrix24, собственного бэкенда или POS (iiko, r_keeper, Poster — через их API
или посредника). Если задать `ORDER_WEBHOOK_SECRET`, запрос подписывается заголовком
`X-BekaKotak-Signature: sha256=<HMAC-SHA256 тела>`.

### 3. База данных и система управления заказами

Добавьте новый канал в `src/lib/orders/channels/` (интерфейс `OrderChannel` — 2 метода) и зарегистрируйте
его в `channels/index.ts`. Например, запись в PostgreSQL (Supabase, Neon) через Prisma/Drizzle — тогда
заказы хранятся постоянно, а на номер заказа стоит поставить `UNIQUE`.

### 4. WhatsApp

- Уже работает: укажите `contacts.whatsapp` в `src/config/site.ts` — появятся кнопки «Написать в WhatsApp», а
  если онлайн-приём не подключён, гость сможет отправить состав заказа в WhatsApp одной кнопкой.
- Автоматические уведомления через WhatsApp Business Cloud API — отдельный канал заказов (нужен аккаунт
  Meta Business и одобренный шаблон сообщения).

### 5. Онлайн-оплата

Точка подключения — `src/lib/payments/types.ts` (интерфейс `PaymentProvider` и пошаговая инструкция):
Kaspi Pay, Halyk ePay, CloudPayments, Freedom Pay. Пока оплата не подключена, заказ создаётся со статусом
«оплата согласуется с оператором», и это написано гостю.

### 6. Админ-панель для меню

Весь код читает меню через `src/lib/menu.ts`. Чтобы управлять меню без программиста, подключите headless
CMS (Sanity, Strapi, Directus) или таблицу в БД и перепишите функции этого файла — компоненты менять не
нужно. Для внешних фото добавьте хост CDN в `images.remotePatterns` в `next.config.ts`.

---

## Тесты

Сквозные тесты Playwright проверяют реальный браузер против production-сборки: все страницы и внутренние
ссылки, загрузку изображений, кнопки шапки и главной, корзину (добавление, количество, удаление, очистка,
сохранение после перезагрузки), категории и поиск, валидацию формы, честное сообщение без подключённого
канала, полный заказ с номером и записью в канал, самовывоз, пересчёт цен на сервере, защиту от дублей,
отсутствие горизонтального скролла на iPhone SE / iPhone 13 / Pixel 7 / Galaxy S9+ / iPad.

```bash
npm run test:e2e:install   # один раз: браузер Chromium для Playwright
npm run build
npm run test:e2e
```

Также: `npm run lint`, `npm run typecheck`, `npm run format`.

---

## Размещение в интернете

### Vercel (проще всего)

1. Загрузите репозиторий на GitHub и импортируйте его на [vercel.com](https://vercel.com).
2. В *Settings → Environment Variables* задайте `NEXT_PUBLIC_SITE_URL` и переменные канала заказов
   (Telegram / webhook). `ORDERS_LOCAL_FILE` на Vercel не используйте.
3. Подключите домен в *Settings → Domains*.

### VPS / Docker

```bash
docker build -t bekakotak .
docker run -d -p 3000:3000 --env-file .env.production --name bekakotak bekakotak
```

Образ собирается из `output: "standalone"` и запускается от непривилегированного пользователя. Перед
контейнером поставьте Nginx или Caddy с HTTPS. Без Docker: `npm ci && npm run build && npm run start`
(например, под pm2 или systemd).

### Чек-лист перед запуском

- [ ] Заполнены телефон, график, соцсети, условия доставки в `src/config/site.ts`
- [ ] Реальное меню и цены в `src/data/menu.ts`, `MENU_IS_DEMO = false`
- [ ] Свои фото интерьера и блюд
- [ ] Настроен Telegram (или webhook) — тестовый заказ дошёл
- [ ] `NEXT_PUBLIC_SITE_URL` указывает на боевой домен
- [ ] Проверена карта на странице «Контакты» (при желании — свой embed в `map.embedUrl`)
- [ ] Текст о согласии на обработку данных согласован (страница оформления)
