"""v3 rework, scenes 1-4: living timelines, live-background callouts, animated title and legend."""
import math

import skia

from engine import *  # noqa
from kit import *  # noqa
from reg import shot, PARTICLES
from life import live, live_bg, draw_img, panel, big_title, para, callout_live, fly_timeline
import engine

TITLE = PAL["title"]
WARM = PAL["warm"]


# ------------------------------------------------------------------ 2: master timeline fly-through
@shot(2)
def v2(c, t, d, W, H):
    ev = [(1904, "Born, New York City", 8, 1.0), (1927, "Doctorate, Göttingen", 20, 1.0),
          (1929, "Professor, Berkeley", 26, 1.0), (1943, "Director, Los Alamos", 63, 1.0),
          (1945, "Trinity · Hiroshima · Nagasaki", 88, 2.0), (1954, "Security hearing", 131, 1.0),
          (1967, "Dies in Princeton", 145, 1.0)]
    fly_timeline(c, t, d, W, H, TITLE, ev, 1898, 1972, ticks=(1904, 1927, 1943, 1945, 1954, 1967))
    small_tag(c, W, H, "GRAPHICS", TITLE)


# ------------------------------------------------------------------ 4: title over the living Trinity dawn
@shot(4)
def v4(c, t, d, W, H):
    k = K(H)
    live_bg(c, 88, 2.0 + t, W, H, blur=0, dark=0.5, sat=0.9)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, H * 0.25), (0, H * 0.75)], [col((0, 0, 0), 0.1), col((0, 0, 0), 0.6), col((0, 0, 0), 0.15)])))
    big_title(c, "OPPENHEIMER", W / 2, H * 0.5, 124 * k, t, 0.3, fc="semi", track=0.32, align="center", dur=1.6, drift=0.012)
    a = eout(clamp((t - 1.6) / 1.0))
    c.drawLine(W / 2 - 330 * k * a, H * 0.555, W / 2 + 330 * k * a, H * 0.555, P(c=col(TITLE["accent"], a), stroke=2 * k))
    big_title(c, "THE MAN WHO CREATED THE POWER TO DESTROY THE WORLD", W / 2, H * 0.61, 26 * k, t, 2.0, fc="med",
              color=(222, 214, 198), track=0.2, align="center", dur=1.8, drift=0.004)


PARTICLES[4] = "embers"


# ------------------------------------------------------------------ 5: what the tags mean, with live examples
@shot(5)
def v5(c, t, d, W, H):
    k = K(H)
    bg_fill(c, W, H, TITLE)
    items = [("ARCHIVAL", "real historical photographs and film", 3, 2.0),
             ("RECREATION", "documents re-set from the originals", 40, 2.0),
             ("2D RECONSTRUCTION", "dramatised illustration", 26, 2.0),
             ("GRAPHICS", "maps, timelines and diagrams", 50, 3.0)]
    pw, ph = 600 * k, 338 * k
    gx, gy = 120 * k, 70 * k
    x0 = W / 2 - pw - gx / 2
    y0 = H * 0.13
    for i, (lab, desc, n, ts) in enumerate(items):
        a = eout(clamp((t - 0.15 - i * 0.35) / 0.7))
        if a <= 0:
            continue
        col_i, row = i % 2, i // 2
        x = x0 + col_i * (pw + gx) + (1 - a) * (-80 if col_i == 0 else 80) * k
        y = y0 + row * (ph + gy + 40 * k)
        img = live(n, ts + t, pw, ph)
        panel(c, img, x, y, pw, ph, a=a, k=k, border=4 * k, frame=(40, 46, 54))
        c.drawRect(skia.Rect(x, y + ph + 14 * k, x + 10 * k, y + ph + 38 * k), P(c=col(TITLE["accent"], a)))
        reveal_text(c, lab, x + 26 * k, y + ph + 36 * k, 24 * k, "monom", LIGHT, a, track=0.14, shadow=0)
        reveal_text(c, desc, x + 26 * k, y + ph + 66 * k, 21 * k, "reg", SOFT, clamp(a * 1.2 - 0.2), shadow=0)
    text(c, "Every shot is labelled in the top-right corner.", W / 2, H * 0.965, 22 * k, "reg", LIGHT,
         eout(clamp((t - 2.0) / 0.8)), align="center")


# ------------------------------------------------------------------ 11: mineral club, over the living study
@shot(11)
def v11(c, t, d, W, H):
    callout_live(c, t, d, W, H, WARM, 10, 6.0 + t, "NEW YORK · 1916", "THE MINERALOGIST, AGE 12",
                 "Robert presents a paper on minerals to the New York Mineralogical Club; the members, by letter, "
                 "had assumed he was an adult.", side="left", dark=0.35, blur=3)
    small_tag(c, W, H, "GRAPHICS · OVER 2D RECONSTRUCTION", WARM)


# ------------------------------------------------------------------ 13: early-years timeline
@shot(13)
def v13(c, t, d, W, H):
    ev = [(1904, "22 April 1904 — born, New York City", 8, 3.0), (1911, "Enters the Ethical Culture School", 12, 1.0),
          (1921, "Graduates, Ethical Culture School", 12, 4.0)]
    fly_timeline(c, t, d, W, H, WARM, ev, 1901, 1923, ticks=(1904, 1911, 1921))
    small_tag(c, W, H, "GRAPHICS", WARM)


# ------------------------------------------------------------------ 16: Harvard degree, over the living library
@shot(16)
def v16(c, t, d, W, H):
    callout_live(c, t, d, W, H, WARM, 15, 5.0 + t, "HARVARD UNIVERSITY · 1922–1925", "SUMMA CUM LAUDE",
                 "A degree in chemistry, completed in three years, while reading physics, mathematics, "
                 "philosophy and literature in several languages.", side="left", dark=0.35, blur=3)
    small_tag(c, W, H, "GRAPHICS · OVER 2D RECONSTRUCTION", WARM)


# ------------------------------------------------------------------ 22: to the doctorate
@shot(22)
def v22(c, t, d, W, H):
    ev = [(1921, "Ethical Culture School", 12, 3.0), (1925, "Harvard degree", 14, 2.0),
          (1926, "Cambridge, then Göttingen", 19, 2.0), (1927, "Doctorate in physics, Göttingen (adviser: Max Born)", 20, 3.0)]
    fly_timeline(c, t, d, W, H, WARM, ev, 1919.5, 1928.5, ticks=(1921, 1925, 1926, 1927))
    small_tag(c, W, H, "GRAPHICS", WARM)
