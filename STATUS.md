# Shorts @ricksclips3000: статус

## Итог
Шортсы не скачаны. YouTube отказывает облачному контейнеру по IP («Sign in to confirm you're not a bot»). Ошибка повторяется на всех клиентах плеера: android_vr, tv, tv_simply, ios, mweb, web_embedded. Это блокировка дата-центров со стороны YouTube, а не настройки сети. Поэтому в `shorts/` пока нет видео, и анализ ещё не запускался.

## Что готово
- **Доступ к сети.** Создано личное окружение `kikayomi` с доступом к YouTube, сессия переведена на него. Список канала и превью грузятся.
- **Отобраны 20 роликов** (`shorts/selection.txt`). Я просмотрел превью и по три кадра из каждого из 31 свежего шортса. Отбирал те, где плоские персонажи стоят в полностью отрендеренных 3D-локациях. Не взял:
  - более плоские: розовая камера, таблетка, однотонный фон, иллюстрированные;
  - чужие по стилю: комиксы поверх Minecraft, пиксель-арт.
- **`tools/download.sh`** скачивает эти 20 в лучшем качестве с оригинальной английской дорожкой, без автодубляжа YouTube. Можно передать файл cookies: `COOKIES=cookies.txt tools/download.sh`.
- **`tools/analyze.py`** декодирует каждый кадр на 30 fps и измеряет:
  - свет и контраст: яркость (среднее, p1/p5/p50/p95/p99), RMS-контраст, провалы в чёрное и пересветы, виньетка, насыщенность, тёплый/холодный баланс;
  - тени: доля пикселей в глубокой тени и их цветовой оттенок;
  - камеру: панорама, тилт, наезд/отъезд, крен, тряска — по кадрам и по шотам; отдельно движение внутри кадра, то есть анимация персонажей;
  - эффекты: вспышки, моушн-блюр, повторяющиеся кадры (показывают, анимированы ли персонажи «на двойках»);
  - склейки: жёсткие склейки, наплывы и затемнения, флэш-склейки.

  Результаты по каждому видео: `analysis/<видео>/frames.csv` (строка на кадр), `shots.json` (список шотов), `cuts.jpg` (каждая склейка как кадры −2…+2), `shots.jpg` (первый, средний и последний кадр каждого шота). Общая сводка: `analysis/summary.md`.
- **Проверка.** Скрипт прогнан на синтетическом ролике с известными панорамой, наездом, тилтом, двумя склейками и вспышкой. Всё определилось верно: наезд ×1.21 при реальном ×1.24.

Про «просмотр всех кадров»: цифры считаются по каждому кадру без исключения. Глазами я смотрю кадры вокруг каждой склейки и ключевые кадры каждого шота. Перебрать вручную ~30 000 картинок по одной нереально.

Всё закоммичено и запушено в ветку `claude/relaxed-dirac-p8nnlx`.

## Как получить видео: выберите один вариант
1. **Скачать на своём компьютере (проще всего).** Установите yt-dlp, запустите `tools/download.sh` в репозитории и запушьте `shorts/` в ветку. После этого я сразу запущу полный анализ.
2. **Подключить компьютер через Remote Control** (приложение Claude → Settings → Claude Code → Remote Control). Я скачаю ролики через ваше подключение и сделаю всё сам.
3. **Прислать YouTube `cookies.txt` файлом**, не вставляя его в чат. Лучше от одноразового аккаунта, потому что файл — это вход в аккаунт. С нашего IP может не сработать и так. Ещё понадобится одно подтверждение, чтобы открыть окружению видеосерверы.

## 20 выбранных роликов
| # | ID | Название |
|---|---|---|
| 01 | R-mWVMM-LAs | Why Samurai Feared The Flying Thunder |
| 02 | aD73kaL_PtY | The Instinct That Makes You Crash |
| 03 | TRUkQ1wbV2E | How Mine Salting Worked |
| 04 | i4hYq1oSXTg | How One Cart Stopped an Entire Army |
| 05 | e9NoHjAXYIY | Why Drivers Started Filming The Road |
| 06 | QlDPMzGmYac | This Shape Saved Roller Coasters |
| 07 | 7xS87iActkU | Why Perfect Railroads Don't Work |
| 08 | Mz72MuPgnGY | Why Sailors Carried Storm Oil |
| 09 | 5WMQhPObNqQ | How a Mirror Rigged a Horse Race |
| 10 | LC8hYwUZ-kU | Why the Second Draw Always Wins |
| 11 | t3OXkhlI6NQ | Every Memory Has a Price |
| 12 | DEe0iKH4KIw | He Could Spot Winning Tickets Just by Looking |
| 13 | GM9UKnZ6JFw | What the Grave Bell Really Meant |
| 14 | VKsamN3Fk4U | Why Cashiers Keep Winning The Lottery |
| 15 | VS1Z_Q-Klt8 | The Ancient Jar That Warned an Empire |
| 16 | lnYLIWP2l-I | Levels of Pirate Cannonballs |
| 17 | jpFJ8Z_F-qU | This Knight Found the Ultimate Loophole |
| 18 | PLe2Gu3FDuA | An Unstoppable Spear vs an Unbreakable Shield |
| 19 | eQR3pgMiUF0 | The Window That Breaks Japan's Gambling Law |
| 20 | CJwgTrfrHL0 | The Science Behind Slot Machines |
