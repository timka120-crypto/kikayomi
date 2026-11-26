"""v3 rework, scenes 5-8: living science animations, live-background callouts, countdown, yield."""
import math

import numpy as np
import skia

from engine import *  # noqa
from env import *  # noqa
from kit import *  # noqa
from reg import shot, Stage, track, PARTICLES, NO_KINETIC
from life import live, live_bg, draw_img, panel, big_title, para, callout_live, fly_timeline
import shots_b

WAR = PAL["war"]
COLD = PAL["cold"]
DES = PAL["desert"]
NEUT = (170, 180, 196)
PROT = (226, 150, 82)


# ------------------------------------------------------------------ shared science look
_FIELD = {}


def science_bg(c, W, H, t, tint=(18, 24, 34), drift=(1.0, 0.3), seed=3):
    k = K(H)
    c.clear(col(mix(tint, (0, 0, 0), 0.4)))
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (W * (0.5 + 0.08 * math.sin(t * 0.3)), H * 0.45), W * 0.75, [col(mix(tint, (255, 255, 255), 0.07)), col(mix(tint, (0, 0, 0), 0.5))])))
    if seed not in _FIELD:
        rng = np.random.default_rng(seed)
        _FIELD[seed] = [(rng.uniform(0, 1, 70), rng.uniform(0, 1, 70), rng.uniform(0, 6.28, 70)) for _ in range(3)]
    for layer, (xs, ys, ph) in enumerate(_FIELD[seed]):
        z = 0.35 + layer * 0.3
        for x, y, p in zip(xs, ys, ph):
            px = (x + t * 0.012 * z * drift[0]) % 1.0 * W
            py = (y + t * 0.012 * z * drift[1] + 0.01 * math.sin(t + p)) % 1.0 * H
            r = (2 + 5 * z) * k
            c.drawCircle(px, py, r, P(c=col(NEUT if p > 3 else PROT, 0.05 + 0.07 * z), blur=r * (1.2 - z)))
    # slow scanning grid
    gp = P(c=col((255, 255, 255), 0.035), stroke=1 * k)
    step = 90 * k
    off = (t * 14 * k) % step
    for i in range(-1, int(W / step) + 2):
        c.drawLine(i * step + off, 0, i * step + off, H, gp)
    for j in range(-1, int(H / step) + 2):
        c.drawLine(0, j * step + off * 0.4, W, j * step + off * 0.4, gp)


def glow(c, x, y, r, colr, a):
    if a <= 0:
        return
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (x, y), r, [col(colr, a), col(colr, a * 0.35), col(colr, 0)], [0, 0.35, 1])))


def neutron(c, x, y, vx, vy, k, a=1.0, r=13):
    sp = math.hypot(vx, vy) + 1e-6
    tx, ty = -vx / sp, -vy / sp
    for i in range(14):
        f = i / 14
        c.drawCircle(x + tx * f * 160 * k, y + ty * f * 160 * k, r * k * (1 - f * 0.7), P(c=col(NEUT, a * 0.22 * (1 - f))))
    glow(c, x, y, r * 3 * k, (190, 210, 255), 0.35 * a)
    particle(c, x, y, r * k, NEUT, a)


def wobble_nucleus(c, x, y, r, t, k, n_p=92, n_n=143, stretch=1.0, heat=0.0, seed=4, a=1.0):
    c.save()
    c.translate(x, y)
    w = 1 + 0.035 * math.sin(t * 5.1) + (stretch - 1)
    c.rotate(10 * math.sin(t * 0.7))
    c.scale(w, 1 / math.sqrt(w))
    glow(c, 0, 0, r * 2.2, mix((255, 170, 90), (255, 240, 200), heat), 0.18 + 0.5 * heat)
    nucleus(c, 0, 0, r, n_p, n_n, t, k, seed=seed, tremble=1.0 + 3 * heat, a=a)
    c.restore()


def heading(c, W, H, t, title, sub, pal):
    k = K(H)
    map_title(c, W, H, pal, title, sub, clamp(t / 0.8))


# ------------------------------------------------------------------ 36: U-235 nucleus, neutron incoming
@shot(36)
def v36(c, t, d, W, H):
    k = K(H)
    science_bg(c, W, H, t, tint=(22, 26, 30))
    cx, cy = W * 0.6, H * 0.52
    z = 1.0 + 0.25 * (t / d)
    R = 125 * k * z
    wobble_nucleus(c, cx, cy, R, t, k, a=eout(clamp(t / 0.8)))
    # neutron accelerating in from the left on a slightly curved path
    u = clamp(t / (d + 0.6))
    nx = lerp(-60 * k, cx - R * 1.25, u ** 1.4)
    ny = cy + math.sin(u * 3.1) * 40 * k * (1 - u)
    neutron(c, nx, ny, 1, 0.1, k)
    # a few stray neutrons drifting through the field for depth
    for i in range(4):
        sx = ((t * (90 + i * 30) * k + i * 500 * k) % (W + 400 * k)) - 200 * k
        neutron(c, sx, H * (0.15 + 0.22 * i), 1, 0, k, a=0.25, r=7)
    a = eout(clamp((t - 0.9) / 0.8))
    label_line(c, cx + R * 0.7, cy - R * 0.7, cx + R * 1.6, cy - R * 1.6, "URANIUM-235 · 92 PROTONS, 143 NEUTRONS", k, WAR, a, size=18)
    label_line(c, nx, ny + 24 * k, nx + 50 * k, ny + 130 * k, "FREE NEUTRON", k, WAR, a, size=18)
    heading(c, W, H, t, "A SLOW NEUTRON MEETS URANIUM-235", "SCIENTIFIC ANIMATION · SIMPLIFIED", WAR)
    small_tag(c, W, H, "GRAPHICS", WAR)


NO_KINETIC.add(36)


# ------------------------------------------------------------------ 37: fission with flash, fragments and three neutrons
@shot(37)
def v37(c, t, d, W, H):
    k = K(H)
    split = 2.0
    shake = 0.0
    if t > split:
        shake = 14 * k * math.exp(-(t - split) * 3) * math.sin(t * 60)
    c.save()
    c.translate(shake, shake * 0.6)
    science_bg(c, W, H, t, tint=(26, 24, 30))
    cx, cy = W * 0.5, H * 0.52
    if t < split:
        u = t / split
        wobble_nucleus(c, cx, cy, 125 * k, t, k, stretch=1 + 0.75 * u ** 2, heat=u, n_n=144)
        # absorbed neutron flash at the start
        glow(c, cx - 125 * k, cy, 90 * k, (200, 220, 255), 0.6 * (1 - clamp(t / 0.5)))
    else:
        v = t - split
        u = eout(clamp(v / 3.0))
        fl = math.exp(-v * 2.4)
        # fragments with trails
        for (dx, dy, r, npp, nn, sd, lab) in ((-1, -0.12, 95, 56, 85, 8, "BARIUM-141"), (1, 0.12, 82, 36, 56, 9, "KRYPTON-92")):
            fx = cx + dx * (110 + 420 * u) * k
            fy = cy + dy * (110 + 420 * u) * k
            for i in range(10):
                f = i / 10
                c.drawCircle(fx - dx * f * 220 * k * (1 - u * 0.6), fy - dy * f * 220 * k, r * k * (1 - f * 0.6), P(c=col(PROT, 0.05 * (1 - f))))
            wobble_nucleus(c, fx, fy, r * k, t, k, n_p=npp, n_n=nn, seed=sd, heat=fl)
            a = clamp((v - 0.8) / 0.6)
            text(c, lab, fx, fy - r * k - 26 * k, 22 * k, "semi", LIGHT, a, align="center", track=0.12, shadow=0.8)
        for i, ang in enumerate((-1.25, 0.45, 2.3)):
            rr = (40 + 1300 * clamp(v / 2.2)) * k
            neutron(c, cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, math.cos(ang), math.sin(ang), k)
        for j in range(3):
            rv = v - j * 0.25
            if rv > 0:
                rr = (60 + 900 * rv) * k
                c.drawCircle(cx, cy, rr, P(c=col((255, 214, 150), 0.5 * math.exp(-rv * 1.6)), stroke=(10 - 2 * j) * k))
        # sparks of energy
        rng = np.random.default_rng(5)
        for i in range(60):
            ang = rng.uniform(0, 6.28); sp = rng.uniform(300, 900)
            rr = sp * v * k
            a = math.exp(-v * 1.8)
            c.drawCircle(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, rng.uniform(2, 5) * k, P(c=col((255, 230, 180), a)))
        glow(c, cx, cy, 700 * k, (255, 240, 210), 0.95 * fl)
        if v < 0.12:
            c.drawRect(skia.Rect(0, 0, W, H), P(c=col((255, 250, 240), 0.8 * (1 - v / 0.12))))
        text(c, "3 NEUTRONS  ·  ABOUT 200 MeV OF ENERGY PER FISSION", W / 2, H * 0.92, 24 * k, "med", LIGHT,
             clamp((v - 1.4) / 0.6), align="center", track=0.12, shadow=0.8)
    c.restore()
    heading(c, W, H, t, "NUCLEAR FISSION", "THE NUCLEUS SPLITS · SCIENTIFIC ANIMATION · SIMPLIFIED", WAR)
    small_tag(c, W, H, "GRAPHICS", WAR)


NO_KINETIC.add(37)


# ------------------------------------------------------------------ 49: Groves chooses Oppenheimer (over the living train)
@shot(49)
def v49(c, t, d, W, H):
    callout_live(c, t, d, W, H, COLD, 48, 7.0 + t, "OCTOBER 1942", "PROJECT Y",
                 "Groves chooses Oppenheimer to direct a new, secret weapons laboratory: a theoretical physicist "
                 "with no Nobel Prize and no experience running anything this large.", side="left", dark=0.3, blur=2)
    small_tag(c, W, H, "GRAPHICS · OVER 2D RECONSTRUCTION", COLD)


# ------------------------------------------------------------------ 54: a real chain reaction, simulated
_CH = {}


def _chain(W, H, seed=2):
    key = (W, H)
    if key in _CH:
        return _CH[key]
    rng = np.random.default_rng(seed)
    # nuclei on a jittered lattice in world space (unit = 1080p pixels)
    nuc = []
    for gx in range(-14, 15):
        for gy in range(-9, 10):
            nuc.append([gx * 120 + rng.uniform(-30, 30), gy * 120 + rng.uniform(-30, 30), None])
    nuc = np.array([[a, b] for a, b, _ in nuc])
    fiss = {}           # index -> time
    neut = []           # (x0, y0, x1, y1, t0, t1, absorbed_by)
    # start neutron
    start = int(np.argmin(np.hypot(nuc[:, 0] + 0, nuc[:, 1])))
    neut.append((-900, 0, nuc[start, 0], nuc[start, 1], 0.0, 0.9, start))
    queue = [(0.9, start)]
    speed = 520.0
    while queue:
        queue.sort()
        tf, i = queue.pop(0)
        if i in fiss or tf > 7.5:
            continue
        fiss[i] = tf
        nout = 2 if rng.uniform() < 0.55 else 3
        for _ in range(nout):
            ang = rng.uniform(0, 6.283)
            dx, dy = math.cos(ang), math.sin(ang)
            # find first nucleus near the ray
            rel = nuc - nuc[i]
            proj = rel[:, 0] * dx + rel[:, 1] * dy
            perp = np.abs(rel[:, 0] * dy - rel[:, 1] * dx)
            cand = np.where((proj > 40) & (perp < 34))[0]
            if len(cand) and rng.uniform() < 0.8:
                j = cand[np.argmin(proj[cand])]
                dist = proj[j]
                t1 = tf + dist / speed
                neut.append((nuc[i, 0], nuc[i, 1], nuc[j, 0], nuc[j, 1], tf, t1, j))
                if j not in fiss:
                    queue.append((t1, j))
            else:
                L = 1600
                neut.append((nuc[i, 0], nuc[i, 1], nuc[i, 0] + dx * L, nuc[i, 1] + dy * L, tf, tf + L / speed, -1))
    _CH[key] = (nuc, fiss, neut)
    return _CH[key]


@shot(54)
def v54(c, t, d, W, H):
    k = K(H)
    science_bg(c, W, H, t, tint=(16, 22, 32), seed=6)
    nuc, fiss, neut = _chain(W, H)
    tt = t * 1.25
    nf = sum(1 for v in fiss.values() if v <= tt)
    zoom = clamp(1.6 / (1 + 0.55 * math.log1p(nf)), 0.42, 1.6)
    cx, cy = W / 2, H / 2

    def S(x, y):
        return cx + x * zoom * k, cy + y * zoom * k

    rods = clamp((t - (d - 1.8)) / 1.2)
    for i, (x, y) in enumerate(nuc):
        sx, sy = S(x, y)
        if not (-60 < sx < W + 60 and -60 < sy < H + 60):
            continue
        tf = fiss.get(i)
        if tf is not None and tf <= tt:
            v = tt - tf
            glow(c, sx, sy, (40 + 260 * min(v, 0.6)) * zoom * k, (255, 200, 120), 0.9 * math.exp(-v * 2.5))
            for s_ in (-1, 1):
                c.drawCircle(sx + s_ * (8 + 30 * min(v, 1)) * zoom * k, sy, 10 * zoom * k, P(c=col(PROT, 0.5)))
        else:
            r = 14 * zoom * k
            c.drawCircle(sx, sy, r, P(c=col(PROT, 0.85)))
            c.drawCircle(sx + r * 0.25, sy - r * 0.2, r * 0.55, P(c=col(NEUT, 0.85)))
    for x0, y0, x1, y1, t0, t1, j in neut:
        if not (t0 <= tt <= t1):
            continue
        u = (tt - t0) / (t1 - t0)
        x, y = lerp(x0, x1, u), lerp(y0, y1, u)
        sx, sy = S(x, y)
        if rods > 0 and int(x / 80) % 3 == 0 and rods > u:
            continue
        neutron(c, sx, sy, x1 - x0, y1 - y0, k * zoom, r=9)
    # control rods slide in from the top at the end
    if rods > 0:
        for i in range(7):
            rx = W * (0.1 + i * 0.133)
            c.drawRect(skia.Rect(rx - 18 * k, -10, rx + 18 * k, H * 0.9 * eout(rods)), P(c=col((60, 66, 74), 0.92)))
            c.drawRect(skia.Rect(rx - 18 * k, -10, rx - 10 * k, H * 0.9 * eout(rods)), P(c=col((120, 128, 136), 0.6)))
        text(c, "CONTROL RODS ABSORB NEUTRONS · THE REACTION IS HELD STEADY", W / 2, H * 0.95, 22 * k, "semi", LIGHT,
             rods, align="center", track=0.1, shadow=0.8)
    # counter
    date_counter(c, W, H, COLD, f"FISSIONS {nf:>4d}", 1.0)
    heading(c, W, H, t, "CHAIN REACTION", "EACH FISSION RELEASES NEUTRONS THAT SPLIT FURTHER NUCLEI · k > 1", COLD)
    small_tag(c, W, H, "GRAPHICS", COLD)


NO_KINETIC.add(54)


# ------------------------------------------------------------------ 55: 3:25 PM over the living pile
@shot(55)
def v55(c, t, d, W, H):
    k = K(H)
    live_bg(c, 53, 1.0 + t, W, H, blur=0, dark=0.3, sat=0.85)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, 0), (0, H * 0.6)], [col((0, 0, 0), 0.55), col((0, 0, 0), 0.0)])))
    # flip clock: 3:24:5x -> 3:25 PM
    sec = int(50 + t * 2.6)
    mm, ss = (24, sec) if sec < 60 else (25, sec - 60)
    s = f"3:{mm:02d}:{ss:02d} PM"
    text(c, s, W * 0.5, H * 0.28, 92 * k, "monom", (238, 210, 150), eout(clamp(t / 0.5)), align="center", shadow=0.9)
    pen = clamp((t - 1.0) / 3.0)
    location_card(c, W, H, [("CHICAGO PILE-1", 34, "semi", "fg"), ("2 DECEMBER 1942 · 3:25 PM LOCAL TIME", 20, "med", "fg"),
                            ("The first self-sustaining nuclear chain reaction", 18, "reg", "accent")], clamp((t - 0.8) / 0.8), COLD)
    small_tag(c, W, H, "GRAPHICS · OVER 2D RECONSTRUCTION", COLD)


# ------------------------------------------------------------------ 59: two production paths with flowing material
def _factory(c, x, y, k, t, colr, seed):
    c.drawRect(skia.Rect(x - 70 * k, y - 40 * k, x + 70 * k, y + 30 * k), P(c=col(mix(colr, (0, 0, 0), 0.55))))
    c.drawRect(skia.Rect(x - 70 * k, y - 40 * k, x + 70 * k, y + 30 * k), P(c=col(colr, 0.9), stroke=2 * k))
    for i in range(2):
        sx = x - 40 * k + i * 50 * k
        c.drawRect(skia.Rect(sx, y - 90 * k, sx + 16 * k, y - 40 * k), P(c=col(mix(colr, (0, 0, 0), 0.4))))
        for j in range(6):
            ph = (t * 0.6 + j / 6 + i * 0.3 + seed) % 1.0
            c.drawCircle(sx + 8 * k + ph * 40 * k, y - 96 * k - ph * 70 * k, (6 + 18 * ph) * k, P(c=col((200, 205, 210), 0.25 * (1 - ph))))
    for i in range(4):
        on = (math.sin(t * 3 + i * 1.7 + seed) > -0.3)
        c.drawRect(skia.Rect(x - 56 * k + i * 30 * k, y - 20 * k, x - 40 * k + i * 30 * k, y - 6 * k), P(c=col((255, 220, 140), 0.8 if on else 0.2)))


@shot(59)
def v59(c, t, d, W, H):
    k = K(H)
    science_bg(c, W, H, t * 0.6, tint=(16, 22, 30), seed=9)
    blue, amber = (110, 168, 214), (226, 150, 82)
    xs = [W * 0.17, W * 0.47, W * 0.8]
    y1, y2, ym = H * 0.33, H * 0.73, H * 0.53
    rows = ((y1, blue, "OAK RIDGE, TENNESSEE", "URANIUM-235", "GUN-TYPE DESIGN"),
            (y2, amber, "HANFORD, WASHINGTON", "PLUTONIUM-239", "IMPLOSION DESIGN"))
    for r, (y, colr, a_, b_, c_) in enumerate(rows):
        a = eout(clamp((t - 0.2 - r * 0.3) / 0.7))
        pts = [(xs[0], y), (xs[1], y), (xs[2], ym)]
        path = poly(pts, close=False)
        meas = skia.PathMeasure(path, False)
        L = meas.getLength()
        prog = eout(clamp((t - 0.6 - r * 0.3) / 1.6))
        seg = skia.Path(); meas.getSegment(0, L * prog, seg, True)
        c.drawPath(seg, P(c=col(colr, 0.35), stroke=10 * k, cap=1))
        c.drawPath(seg, P(c=col(colr, 0.9), stroke=2.5 * k, cap=1))
        # material flowing as glowing pellets
        for i in range(18):
            f = ((t * 0.16 + i / 18) % 1.0)
            if f > prog:
                continue
            pos = meas.getPosTan(L * f)
            if pos:
                glow(c, pos[0].x(), pos[0].y(), 16 * k, colr, 0.6)
                c.drawCircle(pos[0].x(), pos[0].y(), 4.5 * k, P(c=col((255, 255, 255), 0.9)))
        _factory(c, xs[0], y, k * (0.6 + 0.4 * a), t, colr, r)
        text(c, a_, xs[0], y + 72 * k, 22 * k, "semi", LIGHT, a, align="center", track=0.1, shadow=0.7)
        text(c, b_, (xs[0] + xs[1]) / 2, y - 26 * k, 20 * k, "monom", colr, clamp((t - 1.2) / 0.6), align="center", track=0.1)
        bx = xs[1]
        ab = clamp((t - 1.6 - r * 0.3) / 0.6)
        c.drawRect(skia.Rect(bx - 120 * k * ab, y - 6 * k - 22 * k, bx + 120 * k * ab, y + 22 * k), P(c=col((10, 14, 18), 0.85)))
        c.drawRect(skia.Rect(bx - 120 * k * ab, y - 28 * k, bx + 120 * k * ab, y + 22 * k), P(c=col(colr, ab), stroke=1.8 * k))
        text(c, c_, bx, y + 2 * k, 18 * k, "semi", LIGHT, ab, align="center", track=0.1)
    a = eout(clamp((t - 2.6) / 0.8))
    pulse = 1 + 0.15 * math.sin(t * 4)
    glow(c, xs[2], ym, 120 * k * pulse, (240, 210, 150), 0.4 * a)
    c.drawCircle(xs[2], ym, 20 * k, P(c=col(COLD["accent"], a)))
    text(c, "LOS ALAMOS", xs[2], ym - 44 * k, 28 * k, "semi", LIGHT, a, align="center", track=0.12, shadow=0.7)
    text(c, "WEAPON DESIGN AND ASSEMBLY", xs[2], ym + 56 * k, 17 * k, "mono", SOFT, a, align="center", track=0.1)
    heading(c, W, H, t, "TWO ROADS TO A BOMB", "FISSILE MATERIAL PRODUCTION, 1943–1945", COLD)
    small_tag(c, W, H, "GRAPHICS", COLD)


# ------------------------------------------------------------------ 72: gun-type, fired in a loop
def blueprint_bg(c, W, H, t):
    k = K(H)
    c.clear(col((12, 24, 38)))
    for i, step in enumerate((30 * k, 150 * k)):
        gp = P(c=col((140, 190, 230), 0.05 + 0.05 * i), stroke=1 * k)
        off = (t * 10 * k) % step
        for x in np.arange(-step, W + step, step):
            c.drawLine(x + off, 0, x + off, H, gp)
        for y in np.arange(-step, H + step, step):
            c.drawLine(0, y + off * 0.5, W, y + off * 0.5, gp)


@shot(72)
def v72(c, t, d, W, H):
    k = K(H)
    blueprint_bg(c, W, H, t)
    cx, cy = W * 0.5, H * 0.56
    zoom = 1.0 + 0.12 * t / d
    c.save(); c.translate(cx, cy); c.scale(zoom, zoom); c.translate(-cx, -cy)
    L = 900 * k
    ink = (200, 226, 246)
    # casing
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - L / 2 - 60 * k, cy - 95 * k, cx + L / 2 + 60 * k, cy + 95 * k), 95 * k, 95 * k),
                P(c=col(ink, 0.8), stroke=2.4 * k))
    c.drawRect(skia.Rect(cx - L / 2, cy - 18 * k, cx + L / 2 - 120 * k, cy + 18 * k), P(c=col(ink, 0.7), stroke=2 * k))
    # cycle: 0-1.6 charge glows, 1.6-2.3 fire, then hold critical glow, repeat from 4.2
    cyc = t % 4.2
    tx = cx + L / 2 - 120 * k
    c.drawRect(skia.Rect(tx, cy - 60 * k, tx + 120 * k, cy + 60 * k), P(c=col((226, 150, 82), 0.85)))
    if cyc < 1.6:
        px = cx - L / 2 + 20 * k
        glow(c, cx - L / 2 - 20 * k, cy, 70 * k, (255, 180, 100), 0.3 + 0.3 * math.sin(t * 12))
    elif cyc < 2.3:
        u = (cyc - 1.6) / 0.7
        px = lerp(cx - L / 2 + 20 * k, tx - 160 * k, u ** 2.2)
        glow(c, cx - L / 2, cy, 160 * k * (1 - u), (255, 220, 160), 0.9 * (1 - u))
        for i in range(8):
            c.drawLine(px - i * 30 * k, cy - 12 * k, px - i * 30 * k - 24 * k, cy - 12 * k, P(c=col((255, 230, 190), 0.4 * (1 - i / 8)), stroke=2 * k))
    else:
        px = tx - 160 * k
        v = cyc - 2.3
        glow(c, tx, cy, (120 + 80 * math.sin(v * 9)) * k, (255, 236, 200), 0.85 * math.exp(-v * 0.8))
        text(c, "SUPERCRITICAL", tx + 60 * k, cy - 120 * k, 22 * k, "semi", (255, 220, 170), math.exp(-v * 0.6), align="center", track=0.16)
    c.drawRect(skia.Rect(px, cy - 16 * k, px + 160 * k, cy + 16 * k), P(c=col((226, 150, 82), 0.95)))
    c.restore()
    aa = eout(clamp((t - 0.6) / 0.8))
    label_line(c, cx - 360 * k, cy, cx - 440 * k, cy - 220 * k, "URANIUM-235 PROJECTILE", k, COLD, aa, align="right", size=18)
    label_line(c, cx + 360 * k, cy - 60 * k, cx + 460 * k, cy - 220 * k, "URANIUM-235 TARGET", k, COLD, aa, size=18)
    label_line(c, cx - 40 * k, cy + 22 * k, cx + 30 * k, cy + 220 * k, "GUN BARREL", k, COLD, aa, size=18)
    label_line(c, cx - L / 2 - 30 * k, cy + 40 * k, cx - L / 2 - 80 * k, cy + 220 * k, "PROPELLANT CHARGE", k, COLD, aa, size=18)
    heading(c, W, H, t, "GUN-TYPE DESIGN · 'LITTLE BOY'", "SIMPLIFIED, AFTER PUBLISHED DECLASSIFIED DIAGRAMS", COLD)
    small_tag(c, W, H, "GRAPHICS", COLD)


NO_KINETIC.add(72)


# ------------------------------------------------------------------ 73: implosion, converging waves
@shot(73)
def v73(c, t, d, W, H):
    k = K(H)
    blueprint_bg(c, W, H, t)
    cx, cy = W * 0.5, H * 0.55
    R = 300 * k
    rot = t * 6
    cyc = t % 3.5
    ink = (200, 226, 246)
    c.drawCircle(cx, cy, R, P(c=col(ink, 0.8), stroke=2.4 * k))
    c.drawCircle(cx, cy, R * 0.55, P(c=col(ink, 0.6), stroke=1.8 * k))
    det = clamp((cyc - 0.6) / 0.15)
    for i in range(32):
        a0 = math.radians(rot + i * 360 / 32)
        a1 = math.radians(rot + (i + 1) * 360 / 32)
        pts = [(cx + math.cos(a0) * R, cy + math.sin(a0) * R), (cx + math.cos(a1) * R, cy + math.sin(a1) * R),
               (cx + math.cos((a0 + a1) / 2) * R * 0.58, cy + math.sin((a0 + a1) / 2) * R * 0.58)]
        fl = det * math.exp(-max(0, cyc - 0.75) * 3)
        c.drawPath(poly(pts), P(c=col(mix((60, 90, 120), (255, 210, 140), fl), 0.55 + 0.4 * fl)))
        c.drawPath(poly(pts), P(c=col(ink, 0.5), stroke=1.2 * k))
    # converging shock front
    v = cyc - 0.75
    core = R * 0.22
    if 0 < v < 0.9:
        rr = lerp(R * 0.55, core * 0.6, v / 0.9)
        c.drawCircle(cx, cy, rr, P(c=col((255, 220, 160), 0.9), stroke=8 * k))
        core = lerp(R * 0.22, R * 0.14, clamp(v / 0.9) ** 2)
    elif v >= 0.9:
        core = R * 0.14
        glow(c, cx, cy, R * (0.8 + 0.3 * math.sin(v * 12)), (255, 240, 210), 0.9 * math.exp(-(v - 0.9) * 1.2))
    c.drawCircle(cx, cy, core, P(c=col((226, 150, 82))))
    glow(c, cx, cy, core * 2.5, (255, 190, 120), 0.4)
    aa = eout(clamp((t - 0.6) / 0.8))
    label_line(c, cx + R * 0.8, cy - R * 0.6, cx + R * 1.35, cy - R * 0.95, "HIGH-EXPLOSIVE LENSES", k, COLD, aa, size=18)
    label_line(c, cx + core, cy, cx + R * 1.35, cy + R * 0.6, "PLUTONIUM-239 CORE", k, COLD, aa, size=18)
    label_line(c, cx - R * 0.5, cy + R * 0.3, cx - R * 1.35, cy + R * 0.8, "CONVERGING SHOCK WAVE", k, COLD, aa, align="right", size=18)
    heading(c, W, H, t, "IMPLOSION DESIGN · 'FAT MAN', 'THE GADGET'", "THE SHOCK WAVE SQUEEZES THE CORE TO CRITICAL DENSITY · SIMPLIFIED", COLD)
    small_tag(c, W, H, "GRAPHICS", COLD)


NO_KINETIC.add(73)


# ------------------------------------------------------------------ 74: Los Alamos timeline
@shot(74)
def v74(c, t, d, W, H):
    ev = [(1942.88, "16 Nov 1942 — the site is chosen", 61, 2.0), (1943.25, "April 1943 — the laboratory opens", 65, 2.0),
          (1944.55, "July 1944 — plutonium crisis: the lab reorganises around implosion", 71, 2.0),
          (1945.54, "16 July 1945 — Trinity", 88, 2.0)]
    fly_timeline(c, t, d, W, H, COLD, ev, 1942.3, 1945.9, ticks=(1943, 1944, 1945))
    small_tag(c, W, H, "GRAPHICS", COLD)


# ------------------------------------------------------------------ 83: countdown over the storm
@shot(83)
def v83(c, t, d, W, H):
    k = K(H)
    live_bg(c, 81, 4.0 + t, W, H, dark=0.45, sat=0.8)
    c.drawRect(skia.Rect(0, 0, W, H), P(c=col((4, 6, 14), 0.35)))
    s = min(45, 39 + int(t))
    frac = t % 1.0
    # pulse on each second
    pulse = math.exp(-frac * 5)
    size = (150 + 10 * pulse) * k
    text(c, f"5:29:{s:02d}", W / 2, H * 0.47, size, "monom", mix((240, 232, 216), (255, 200, 140), pulse * 0.5),
         1.0, align="center", shadow=0.9)
    text(c, "AM", W / 2 + 400 * k, H * 0.47, 38 * k, "mono", DES["muted"], 1.0)
    # sweeping second ring
    R = 330 * k
    c.drawArc(skia.Rect(W / 2 - R, H * 0.43 - R, W / 2 + R, H * 0.43 + R), -90, 360 * frac, False,
              P(c=col((255, 200, 140), 0.55), stroke=3 * k))
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = R + (10 if i % 5 else 18) * k
        c.drawLine(W / 2 + math.cos(a) * R, H * 0.43 + math.sin(a) * R, W / 2 + math.cos(a) * r0, H * 0.43 + math.sin(a) * r0,
                   P(c=col(LIGHT, 0.35), stroke=1.5 * k))
    left = 45 - s
    text(c, f"T – {left}", W / 2, H * 0.62, 40 * k, "monom", (255, 200, 140), 1.0, align="center", track=0.2, shadow=0.8)
    location_card(c, W, H, [("TRINITY TEST SITE, NEW MEXICO, USA", 30, "semi", "fg"), ("16 JULY 1945", 22, "med", "fg"),
                            ("ZERO HOUR: 5:29:45 AM LOCAL TIME", 22, "med", "accent")], clamp((t - 0.6) / 0.8), DES)
    small_tag(c, W, H, "GRAPHICS · OVER 2D RECONSTRUCTION", DES)


# ------------------------------------------------------------------ 85: Oppenheimer at the post, last seconds
@shot(85)
def v85(c, t, d, W, H):
    k = K(H)
    st = Stage(c, W, H, x=track(t, d, 0.5, 0.05), y=track(t, d, -1.5, -1.62), z=track(t, d, 0.9, 2.5), f=1100)
    c.clear(col((14, 14, 16)))
    flick = 0.85 + 0.15 * math.sin(t * 23) * math.sin(t * 7.3)
    with st.at(6.0):
        wall(c, -6, 6, -4, (46, 46, 48), light=(-1.2, -2.4), light_r=2.2, light_c=(255, 200, 150), light_a=0.28 * flick)
        # instrument panels with blinking lamps in the background
        for i in range(5):
            x0 = -4.8 + i * 1.5
            c.drawRect(skia.Rect(x0, -2.2, x0 + 1.3, -0.9), P(c=col((34, 38, 36))))
            for j in range(6):
                on = math.sin(t * (2 + j) + i * 1.3) > 0.2
                c.drawCircle(x0 + 0.2 + j * 0.18, -1.9, 0.04, P(c=col((255, 120, 60) if j % 2 else (120, 255, 140), 0.9 if on else 0.15)))
            for j in range(3):
                ang = math.sin(t * 1.5 + i + j) * 40
                cxm, cym = x0 + 0.3 + j * 0.38, -1.35
                c.drawCircle(cxm, cym, 0.14, P(c=col((210, 206, 190))))
                c.drawLine(cxm, cym, cxm + math.sin(math.radians(ang)) * 0.12, cym - math.cos(math.radians(ang)) * 0.12,
                           P(c=col((180, 40, 30)), stroke=0.015))
        # lamp hanging, swaying a little
        sw = math.sin(t * 1.4) * 0.12
        c.drawLine(-1.2, -4, -1.2 + sw, -2.9, P(c=col((20, 20, 20)), stroke=0.02))
        c.drawCircle(-1.2 + sw, -2.85, 0.1, P(c=col((255, 220, 170), flick)))
        for x, look, ph in ((-3.4, OFFICIAL, 0.0), (2.9, SCIENTIST, 1.3)):
            draw_person(c, look, idle(stand(sh_r=40, el_r=80), t, ph, 1.5), x=x, facing=1 if x < 0 else -1, shade=0.35)
    with st.at(4.0):
        c.drawRect(skia.Rect(0.55, -3.2, 0.78, 0.2), P(c=col((92, 70, 50))))
        c.drawRect(skia.Rect(0.55, -3.2, 0.6, 0.2), P(c=col((130, 100, 70))))
        grip = 0.5 + 0.5 * math.sin(t * 2.6)
        p = stand(sh_r=lerp(66, 76, grip), el_r=lerp(64, 78, grip), sh_l=12, el_l=40, head=-4 + 2 * math.sin(t * 0.9), lean=2 + grip)
        draw_person(c, OPP_TRINITY, p, x=0.0, facing=1, rim=0.6 * flick, light=(255, 200, 150))
    # dust drifting down from the ceiling
    rng = np.random.default_rng(3)
    for i in range(50):
        x = rng.uniform(0, W)
        y = (rng.uniform(0, H) + t * rng.uniform(10, 40) * k) % H
        c.drawCircle(x, y, rng.uniform(1, 2.5) * k, P(c=col((230, 210, 180), 0.25)))
    location_card(c, W, H, [("S-10000 CONTROL BUNKER", 26, "semi", "fg"), ("5:29 AM · 16 JULY 1945", 18, "mono", "accent")],
                  clamp((t - 0.6) / 0.8), DES)
    small_tag(c, W, H, "2D RECONSTRUCTION", DES)


# ------------------------------------------------------------------ 90: 20,000 tons of TNT as a freight train
@shot(90)
def v90(c, t, d, W, H):
    k = K(H)
    sky(c, W, H, (60, 46, 54), (196, 140, 110), 0.6)
    c.drawRect(skia.Rect(0, H * 0.62, W, H), P(c=col((70, 56, 50))))
    # distant mesas parallax
    off = t * 30 * k
    for i in range(6):
        x = (i * 420 * k - off) % (W + 600 * k) - 300 * k
        c.drawPath(poly([(x, H * 0.62), (x + 60 * k, H * 0.5), (x + 300 * k, H * 0.49), (x + 380 * k, H * 0.62)]), P(c=col((110, 80, 76))))
    # train of boxcars rolling by: each car 50 t, so 400 cars = 20,000 t
    speed = 520 * k
    car = 150 * k
    gy = H * 0.74
    c.drawRect(skia.Rect(0, gy + 18 * k, W, gy + 24 * k), P(c=col((40, 34, 30))))
    head = W + 200 * k - t * speed
    for i in range(80):
        x = head + i * (car + 10 * k)
        if x > W + car or x < -car:
            continue
        c.drawRect(skia.Rect(x, gy - 70 * k, x + car, gy + 6 * k), P(c=col((120, 60, 44))))
        c.drawRect(skia.Rect(x + 6 * k, gy - 64 * k, x + car - 6 * k, gy), P(c=col((140, 74, 54))))
        text(c, "TNT", x + car / 2, gy - 22 * k, 26 * k, "semi", (240, 220, 180), 0.9, align="center", track=0.1)
        for wx in (x + 26 * k, x + car - 26 * k):
            c.save(); c.translate(wx, gy + 12 * k); c.rotate(t * 400)
            c.drawCircle(0, 0, 11 * k, P(c=col((30, 26, 24))))
            c.drawLine(-9 * k, 0, 9 * k, 0, P(c=col((90, 80, 70)), stroke=2 * k))
            c.restore()
    cars = int(clamp(t / (d - 0.5)) * 400)
    tons = cars * 50
    text(c, f"{tons:,} TONS".replace(",", " "), W / 2, H * 0.3, 96 * k, "monom", (255, 214, 160), 1.0, align="center", shadow=0.9)
    text(c, "OF TNT", W / 2, H * 0.37, 30 * k, "semi", LIGHT, 1.0, align="center", track=0.3, shadow=0.8)
    text(c, f"≈ {cars} FREIGHT CARS OF 50 TONS EACH", W / 2, H * 0.43, 22 * k, "mono", SOFT, clamp(t / 0.8), align="center", track=0.12, shadow=0.8)
    heading(c, W, H, t, "ESTIMATED YIELD: ABOUT 20 KILOTONS", "LATER ESTIMATES UP TO ABOUT 25 kt · LOS ALAMOS NATIONAL LABORATORY", DES)
    small_tag(c, W, H, "GRAPHICS", DES)


NO_KINETIC.add(90)
