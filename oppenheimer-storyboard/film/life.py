"""v3 helpers: live picture-in-picture of other shots, kinetic typography, fly-through timeline."""
import math

import numpy as np
import skia

import engine
import kit
from engine import col, mix, clamp, lerp, ease, eout, text, measure, P, poly
from kit import K, LIGHT, SOFT, wrap_m, reveal_text
from reg import SHOTS

_SURF = {}


def live(n, t, w, h, d=None):
    """Render shot n at local time t into an offscreen image of size w x h (its own overlays dropped)."""
    w, h = int(w), int(h)
    key = (w, h)
    if key not in _SURF:
        _SURF[key] = skia.Surface(w, h)
    s = _SURF[key]
    cv = s.getCanvas()
    cv.save()
    mark = len(kit.OVL)
    was = kit.DEFER[0]
    kit.DEFER[0] = True
    fn = SHOTS[n]
    import render
    dd = d if d is not None else next(x["d"] for x in render.TL if x["n"] == n)
    fn(cv, max(0.0, t), dd, w, h)
    del kit.OVL[mark:]
    kit.DEFER[0] = was
    cv.restore()
    return s.makeImageSnapshot()


def draw_img(c, img, x, y, w, h, a=1.0, blur=0.0, dark=0.0, sat=1.0):
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(a)
    filt = None
    if sat != 1.0 or dark:
        s, dk = sat, 1 - dark
        lr, lg, lb = 0.2126 * (1 - s), 0.7152 * (1 - s), 0.0722 * (1 - s)
        m = [(lr + s) * dk, lg * dk, lb * dk, 0, 0,
             lr * dk, (lg + s) * dk, lb * dk, 0, 0,
             lr * dk, lg * dk, (lb + s) * dk, 0, 0,
             0, 0, 0, 1, 0]
        filt = skia.ImageFilters.ColorFilter(skia.ColorFilters.Matrix(m))
    if blur > 0:
        filt = skia.ImageFilters.Blur(blur, blur, skia.TileMode.kClamp, filt)
    if filt:
        p.setImageFilter(filt)
    c.drawImageRect(img, skia.Rect(x, y, x + w, y + h), skia.SamplingOptions(skia.FilterMode.kLinear), p)


def live_bg(c, n, t, W, H, blur=0.0, dark=0.35, sat=0.85, scale=0.5, a=1.0):
    """Full-frame living background from another shot (rendered at reduced size for speed)."""
    img = live(n, t, W * scale, H * scale)
    draw_img(c, img, 0, 0, W, H, a=a, blur=blur * scale, dark=dark, sat=sat)


def panel(c, img, x, y, w, h, a=1.0, frame=(236, 230, 214), border=6.0, shadow=True, k=1.0):
    """Framed photo-print panel (picture in picture)."""
    if a <= 0.01:
        return
    if shadow:
        c.drawRect(skia.Rect(x - border + 10 * k, y - border + 14 * k, x + w + border + 10 * k, y + h + border + 14 * k),
                   P(c=col((0, 0, 0), 0.45 * a), blur=14 * k))
    c.drawRect(skia.Rect(x - border, y - border, x + w + border, y + h + border), P(c=col(frame, a)))
    draw_img(c, img, x, y, w, h, a=a)


def big_title(c, s, x, y, size, t, t0=0.0, fc="semi", color=LIGHT, track=0.12, align="left", dur=1.0, drift=0.02):
    """Kinetic headline: each letter rises and sharpens in sequence, then the tracking keeps opening slowly."""
    k = 1.0
    tr = track + drift * max(0.0, t - t0)
    w = measure(s, size, fc, tr)
    x0 = x - (w / 2 if align == "center" else (w if align == "right" else 0))
    xx = x0
    n = max(1, len(s))
    for i, ch in enumerate(s):
        cw = measure(ch, size, fc, 0) + tr * size
        p = clamp((t - t0 - i * dur * 0.5 / n) / (dur * 0.6))
        if p > 0 and ch != " ":
            e = eout(p)
            text(c, ch, xx, y + (1 - e) * size * 0.45, size, fc, color, clamp(p * 1.6), shadow=0.7)
        xx += cw
    return w


def para(c, s, x, y, size, t, t0, maxw, fc="reg", color=SOFT, lh=1.45, align="left"):
    lines = wrap_m(s, size, fc, maxw)
    for j, ln in enumerate(lines):
        reveal_text(c, ln, x, y + j * size * lh, size, fc, color, clamp((t - t0 - j * 0.16) / 0.7), align=align)
    return len(lines) * size * lh


def plate(c, x0, y0, x1, y1, a, colr=(8, 10, 12), alpha=0.6, k=1.0):
    if a <= 0:
        return
    c.drawRect(skia.Rect(x0, y0, x0 + (x1 - x0) * eout(clamp(a / 0.5)), y1), P(c=col(colr, alpha * clamp(a * 2))))


def callout_live(c, t, d, W, H, pal, n, t_src, kicker, title, body, side="left", dark=0.5, blur=5.0):
    """Editorial callout over a living, slightly defocused scene."""
    k = K(H)
    live_bg(c, n, t_src, W, H, blur=blur, dark=dark, sat=0.8)
    # gradient to seat the type
    g0 = (0, 0) if side == "left" else (W, 0)
    g1 = (W * 0.75, 0) if side == "left" else (W * 0.25, 0)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [g0, g1], [col((6, 8, 10), 0.82), col((6, 8, 10), 0.0)])))
    x = 120 * k if side == "left" else W * 0.5
    y = H * 0.36
    acc = mix(pal.get("accent", (201, 164, 99)), (255, 255, 255), 0.12)
    a0 = eout(clamp((t - 0.1) / 0.7))
    c.drawLine(x, y - 70 * k, x + 160 * k * a0, y - 70 * k, P(c=col(acc, a0), stroke=3 * k))
    reveal_text(c, kicker, x, y - 30 * k, 22 * k, "mono", acc, clamp((t - 0.2) / 0.6), track=0.18, shadow=0)
    big_title(c, title, x, y + 40 * k, 64 * k, t, 0.35, fc="semi", track=0.04, drift=0.004)
    para(c, body, x, y + 120 * k, 32 * k, t, 1.2, 780 * k)


# ------------------------------------------------------------------ fly-through timeline
def fly_timeline(c, t, d, W, H, pal, events, y0, y1, ticks=None, lit_all=False, bg=None, title=None, sub=None,
                 years=(1900, 1970)):
    """A long timeline ribbon in perspective; the camera flies continuously from year y0 to y1.
    events: [(year, label, shot_n or None, t_src)] - a live picture panel stands over each event."""
    k = K(H)
    if bg is not None:
        bg(c, t)
    else:
        c.clear(col(mix(pal["bg"], (0, 0, 0), 0.25)))
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
            (W * 0.5, H * 0.42), W * 0.75, [col(mix(pal["bg"], (255, 255, 255), 0.07)), col(mix(pal["bg"], (0, 0, 0), 0.35))])))
    acc = mix(pal.get("accent", (201, 164, 99)), (255, 255, 255), 0.1)
    u = t / d
    cur = lerp(y0, y1, 0.75 * u + 0.25 * ease(u))           # camera year
    px_per_year = W * 0.11 if y1 - y0 <= 20 else W * 0.026
    horizon = H * 0.30
    base = H * 0.70

    def X(yr):
        return W * 0.5 + (yr - cur) * px_per_year

    # receding floor grid for depth and motion
    for i in range(-30, 31):
        yr = math.floor(cur) + i
        xg = X(yr)
        a = 0.05 if yr % 5 else 0.12
        c.drawLine(xg, base + 4 * k, W * 0.5 + (xg - W * 0.5) * 0.25, horizon, P(c=col(LIGHT, a), stroke=1 * k))
    for j in range(1, 7):
        yy = base + (H - base) * (j / 6) ** 1.6
        c.drawLine(0, yy, W, yy, P(c=col(LIGHT, 0.04), stroke=1 * k))
    # ribbon
    c.drawRect(skia.Rect(0, base - 2 * k, W, base + 2 * k), P(c=col(LIGHT, 0.55)))
    lit_to = cur if not lit_all else years[1]
    c.drawRect(skia.Rect(0, base - 2.5 * k, clamp(X(lit_to) / W) * W, base + 2.5 * k), P(c=col(acc, 0.95)))
    # years
    lastx = -1e9
    for yr in range(int(cur) - 40, int(cur) + 41):
        if not (years[0] <= yr <= years[1]):
            continue
        xx = X(yr)
        if xx < -50 or xx > W + 50:
            continue
        major = (ticks and yr in ticks) or yr % 10 == 0
        if major and xx - lastx < 56 * k:
            major = False
        if major:
            lastx = xx
        c.drawLine(xx, base - (14 if major else 6) * k, xx, base + (14 if major else 6) * k, P(c=col(LIGHT, 0.7 if major else 0.3), stroke=1.4 * k))
        if major or (px_per_year > 120 * k and xx - lastx >= 56 * k):
            text(c, str(yr), xx, base + 44 * k, (20 if major else 15) * k, "mono", (190, 194, 198), 0.85 if major else 0.55, align="center")
    # giant ghost numeral of the current year
    text(c, str(int(round(cur))), W * 0.5, H * 0.93, 210 * k, "semi", LIGHT, 0.05, align="center", track=0.05)
    # events: greedy level layout so panels never overlap (two rows above the ribbon, one below)
    pw, ph = 360 * k, 202 * k
    vis = sorted([e for e in events if -pw * 1.5 < X(e[0]) < W + pw * 1.5], key=lambda e: e[0])
    rows_x = {0: -1e9, 1: -1e9, 2: -1e9}
    lay = []
    for e in vis:
        xx = X(e[0])
        for lv in (0, 1, 2):
            if xx - pw / 2 > rows_x[lv] + 24 * k:
                rows_x[lv] = xx + pw / 2
                lay.append((e, lv)); break
        else:
            lay.append((e, 3))
    for (yr, label, n, tsrc), lv in sorted(lay, key=lambda z: -z[1]):
        if lv == 3:
            continue
        xx = X(yr)
        dist = abs(xx - W * 0.5) / (W * 0.5)
        a = clamp(1.4 - dist * 0.9) if not lit_all else 1.0
        reached = cur >= yr - 0.15 or lit_all
        dot = acc if reached else LIGHT
        pulse = 1 + 0.25 * math.sin(engine.CLOCK[0] * 4 + yr)
        c.drawCircle(xx, base, 8 * k * (pulse if reached else 1), P(c=col(dot, 0.95)))
        c.drawCircle(xx, base, 18 * k * pulse, P(c=col(dot, 0.35), stroke=1.5 * k))
        lines = wrap_m(label, 20 * k, "med", pw + 30 * k)
        lab_h = len(lines) * 26 * k + 40 * k
        if lv == 0:
            top = base - 56 * k - ph
        elif lv == 1:
            top = base - 56 * k - ph - lab_h - ph - 34 * k
        else:
            top = base + 70 * k + lab_h
        sc = 0.6 if lv == 2 else 1.0
        stem_end = top + ph if lv < 2 else top - lab_h
        c.drawLine(xx, base + (-10 if lv < 2 else 10) * k, xx, stem_end, P(c=col(dot, 0.6 * a), stroke=1.4 * k))
        if n is not None and a > 0.05:
            img = live(n, tsrc + t, pw * sc, ph * sc)
            panel(c, img, xx - pw * sc / 2, top, pw * sc, ph * sc, a=a, k=k, border=5 * k)
        ly = top - 18 * k
        for j, ln in enumerate(reversed(lines)):
            text(c, ln, xx, ly - j * 26 * k, 20 * k, "med", LIGHT, a, align="center", shadow=0.8)
        text(c, str(int(yr)), xx, ly - len(lines) * 26 * k - 4 * k, 28 * k, "semi", acc, a, align="center", shadow=0.8)
    if title:
        kit.map_title(c, W, H, pal, title, sub, clamp(t / 0.8))
