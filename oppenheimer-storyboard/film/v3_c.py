"""v3 rework, scenes 8-12: rising Trinity cloud, bombsight run, fall graphic, late-life timelines, finale."""
import math

import numpy as np
import skia

from engine import *  # noqa
from env import *  # noqa
from kit import *  # noqa
from reg import shot, Stage, track, PARTICLES, NO_KINETIC
from life import live, live_bg, draw_img, panel, big_title, para, callout_live, fly_timeline
import shots_b
import shots_c
from shots_c import aerial, mono_layer, HIRO

DES = PAL["desert"]
MONO, CW, DARK = PAL["mono"], PAL["coldwar"], PAL["dark"]
TITLE = PAL["title"]


# ------------------------------------------------------------------ 88: the cloud climbs into the dawn
@shot(88)
def v88(c, t, d, W, H):
    k = K(H)
    cz = lerp(-200, -150, t / d)
    st = shots_b.trinity_view(c, W, H, 3.0 + t * 2.4, cam_z=cz)
    with st.at(-40):
        rng = np.random.default_rng(5)
        for x in np.arange(-120, 120, 3.0):
            c.drawCircle(x + rng.uniform(-1, 1), -0.4, rng.uniform(0.4, 0.8), P(c=col((40, 30, 28))))
    with st.at(cz + 14):
        # silhouettes of observers standing up and pointing
        for i, x in enumerate((-6.5, -5.2, -3.6, 3.4, 5.0)):
            draw_person(c, [CREW, SCIENTIST, OFFICIAL][i % 3], idle(stand(sh_r=150 if i % 2 else 20, el_r=10), t, i, 1.5),
                        x=x, facing=1 if x < 0 else -1, shade=0.85)
    # dust front racing across the desert toward the camera
    front = clamp((t - 1.0) / (d - 1.0))
    if front > 0:
        y = lerp(H * 0.64, H * 1.1, front)
        c.drawRect(skia.Rect(0, H * 0.6, W, y), P(c=col((150, 110, 80), 0.35 * (1 - front * 0.5)), blur=40 * k))
    shots_b.card(c, W, H, t, d, DES, "VIEW FROM ABOUT 10,000 YARDS", "5:30 AM, 16 JULY 1945")
    shots_b.tag2d(c, W, H, DES)


PARTICLES[88] = "embers"


# ------------------------------------------------------------------ 106: bombsight run toward the T-shaped bridge
@shot(106)
def v106(c, t, d, W, H):
    k = K(H)
    u = t / d
    off = (lerp(-0.09, 0.006, u), lerp(0.07, -0.004, u))
    jit = (math.sin(t * 13) * 0.0015, math.cos(t * 11) * 0.0015)
    c.clear(col((0, 0, 0)))
    c.save()
    path = skia.Path(); path.addCircle(W / 2, H / 2, H * 0.42)
    c.clipPath(path, doAntiAlias=True)
    aerial(c, W, H, t * 3.0, 1.0, scale=lerp(1.7, 2.6, u), center_off=(off[0] + jit[0], off[1] + jit[1]))
    c.restore()
    c.drawCircle(W / 2, H / 2, H * 0.42, P(c=col((0, 0, 0)), stroke=12 * k))
    c.drawCircle(W / 2, H / 2, H * 0.44, P(c=col((0, 0, 0), 0.8), blur=30 * k, stroke=40 * k))
    cp = P(c=col((20, 20, 20), 0.85), stroke=1.6 * k)
    c.drawLine(W / 2 - H * 0.4, H / 2, W / 2 + H * 0.4, H / 2, cp)
    c.drawLine(W / 2, H / 2 - H * 0.4, W / 2, H / 2 + H * 0.4, cp)
    for i in range(1, 8):
        r = i * H * 0.05
        c.drawLine(W / 2 - 8 * k, H / 2 + r, W / 2 + 8 * k, H / 2 + r, cp)
    mono_layer(c, W, H, 0.5)
    text(c, "AIMING POINT: AIOI BRIDGE", W / 2 + H * 0.46, H * 0.85, 17 * k, "mono", MONO["fg"], clamp((t - 0.6) / 0.6), track=0.1)
    text(c, f"8:{14 + int(u * 0.99)}:{int(20 + u * 37):02d} AM", W / 2 + H * 0.46, H * 0.85 + 30 * k, 22 * k, "monom",
         MONO["accent"], clamp((t - 0.6) / 0.6), track=0.06)
    shots_c.tag2d(c, W, H, MONO) if hasattr(shots_c, "tag2d") else small_tag(c, W, H, "2D RECONSTRUCTION", MONO)


NO_KINETIC.add(106)


# ------------------------------------------------------------------ 108: 43 seconds of fall
@shot(108)
def v108(c, t, d, W, H):
    k = K(H)
    aerial(c, W, H, t * 4, 1.0, scale=lerp(1.0, 1.4, t / d))
    mono_layer(c, W, H, 0.6)
    c.drawRect(skia.Rect(0, 0, W, H), P(c=col((0, 0, 0), 0.45)))
    x = W * 0.7
    top, bot = H * 0.16, H * 0.86
    c.drawLine(x, top, x, bot, P(c=col(MONO["fg"], 0.7), stroke=1.6 * k))
    det_y = lerp(bot, top, 600 / 9400)
    for i in range(10):
        yy = lerp(top, bot, i / 9)
        c.drawLine(x - 6 * k, yy, x + 6 * k, yy, P(c=col(MONO["fg"], 0.5), stroke=1.2 * k))
    for yy, lab in ((top, "31,000 FT · ABOUT 9,400 M — RELEASE, 8:15 AM"), (det_y, "ABOUT 600 M — DETONATION")):
        c.drawLine(x - 14 * k, yy, x + 14 * k, yy, P(c=col(MONO["fg"]), stroke=2 * k))
        text(c, lab, x + 26 * k, yy + 6 * k, 18 * k, "mono", MONO["fg"], 0.95, track=0.06, shadow=0.8)
    u = clamp((t - 0.2) / (d - 0.6))
    by = lerp(top, det_y, u * u)
    # falling bomb with streaks
    for i in range(10):
        c.drawLine(x - 30 * k, by - i * 14 * k * (0.3 + u), x - 30 * k, by - i * 14 * k * (0.3 + u) - 10 * k,
                   P(c=col((255, 255, 255), 0.4 * (1 - i / 10)), stroke=2 * k))
    c.save(); c.translate(x - 30 * k, by); c.rotate(90 + math.sin(t * 8) * 3)
    shots_c.little_boy(c, 0, 0, 34 * k, colr=(210, 206, 196))
    c.restore()
    secs = 43 * u
    text(c, f"{secs:4.1f} s", x - 70 * k, by + 8 * k, 30 * k, "monom", MONO["accent"], 1, align="right", shadow=0.9)
    alt = int(9400 - (9400 - 600) * u * u)
    text(c, f"{alt:,} m".replace(",", " "), x - 70 * k, by + 40 * k, 20 * k, "mono", MONO["fg"], 0.9, align="right", shadow=0.9)
    location_card(c, W, H, [("8:15 AM LOCAL TIME", 30, "semi", "fg"), ("Fall time about 43 seconds", 18, "reg", "accent"),
                            ("Source: U.S. Strategic Bombing Survey, 1946", 14, "mono", "muted")], clamp((t - 0.4) / 0.8), MONO)
    small_tag(c, W, H, "GRAPHICS", MONO)


NO_KINETIC.add(108)


# ------------------------------------------------------------------ 127: the H-bomb debate over Ivy Mike
@shot(127)
def v127(c, t, d, W, H):
    k = K(H)
    live_bg(c, 128, 2.0 + t, W, H, blur=3, dark=0.45, sat=0.9)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, 0), (W * 0.8, 0)], [col((6, 8, 12), 0.85), col((6, 8, 12), 0.1)])))
    acc = mix(CW["accent"], (255, 255, 255), 0.1)
    cards = [("OCTOBER 1949", "The AEC's General Advisory Committee, chaired by Oppenheimer, advises against a crash programme to build the hydrogen bomb.", 0.2),
             ("31 JANUARY 1950", "President Truman orders work on the hydrogen bomb to proceed.", 2.4)]
    for i, (a_, b_, t0) in enumerate(cards):
        x, y = 120 * k, H * (0.3 + i * 0.32)
        a = clamp((t - t0) / 0.6)
        c.drawLine(x, y - 54 * k, x + 140 * k * eout(a), y - 54 * k, P(c=col(acc, a), stroke=3 * k))
        big_title(c, a_, x, y, 52 * k, t, t0, fc="semi", color=acc, track=0.08, drift=0.003)
        para(c, b_, x, y + 56 * k, 30 * k, t, t0 + 0.5, 820 * k, color=LIGHT)
    small_tag(c, W, H, "GRAPHICS · OVER ARCHIVAL FILM", CW)


# ------------------------------------------------------------------ 136 / 139 / 141: late-life timelines
@shot(136)
def v136(c, t, d, W, H):
    ev = [(1954.28, "12 April – 6 May 1954 — the security hearing", 131, 3.0),
          (1954.5, "29 June 1954 — the AEC refuses to restore his clearance", 134, 1.0)]
    fly_timeline(c, t, d, W, H, CW, ev, 1953.6, 1955.0, ticks=(1954, 1955))
    small_tag(c, W, H, "GRAPHICS", CW)


@shot(139)
def v139(c, t, d, W, H):
    ev = [(1954.4, "1954 — clearance revoked", 131, 2.0), (1958, "Princeton: the Institute for Advanced Study", 137, 2.0),
          (1963.92, "2 Dec 1963 — Enrico Fermi Award, presented by President Johnson", 138, 2.0)]
    fly_timeline(c, t, d, W, H, DARK, ev, 1953, 1965.5, ticks=(1954, 1958, 1963))
    small_tag(c, W, H, "GRAPHICS", DARK)


@shot(141)
def v141(c, t, d, W, H):
    ev = [(1904, "Born, New York City", 8, 2.0), (1927, "Doctorate, Göttingen", 20, 2.0),
          (1939, "Second World War begins", 41, 2.0), (1942, "Manhattan Project", 56, 2.0),
          (1945, "Trinity · Hiroshima · Nagasaki", 88, 3.0), (1949, "Soviet atomic test", 125, 3.0),
          (1954, "Security hearing", 131, 2.0), (1963, "Enrico Fermi Award", 138, 2.0),
          (1967.13, "18 Feb 1967 — dies in Princeton, aged 62", 145, 3.0)]
    fly_timeline(c, t, d, W, H, TITLE, ev, 1900, 1968, ticks=(1904, 1927, 1939, 1942, 1945, 1949, 1954, 1963, 1967), lit_all=False)
    small_tag(c, W, H, "GRAPHICS", DARK)


# ------------------------------------------------------------------ 144: 2022, over the Trinity obelisk at dusk
@shot(144)
def v144(c, t, d, W, H):
    callout_live(c, t, d, W, H, DARK, 142, 6.0 + t, "16 DECEMBER 2022", "THE 1954 DECISION IS VACATED",
                 "The U.S. Department of Energy vacates the 1954 decision to revoke Oppenheimer's security clearance, "
                 "calling the process flawed.", side="left", dark=0.3, blur=2)
    small_tag(c, W, H, "GRAPHICS · OVER 2D ILLUSTRATION", DARK)


# ------------------------------------------------------------------ 145: the mesa at night, alive
@shot(145)
def v145(c, t, d, W, H):
    k = K(H)
    st = Stage(c, W, H, x=0, y=track(t, d, -2, -10), z=track(t, d, -4, -30))
    sky(c, W, H, (4, 6, 14), (20, 26, 44))
    # stars wheel slowly around a pole above the frame
    rng = np.random.default_rng(31)
    cxp, cyp = W * 0.5, -H * 0.6
    rot = t * 0.02
    for i in range(420):
        r = rng.uniform(H * 0.6, H * 1.9)
        a0 = rng.uniform(-1.2, 1.2) + rot
        x, y = cxp + math.sin(a0) * r, cyp + math.cos(a0) * r
        if y > H * 0.78:
            continue
        tw = 0.6 + 0.4 * math.sin(t * rng.uniform(1, 4) + i)
        c.drawCircle(x, y, rng.uniform(0.5, 1.6) * k, P(c=col((225, 230, 240), rng.uniform(0.3, 0.9) * tw)))
    # a meteor
    mt = (t - 2.2)
    if 0 < mt < 0.8:
        x0, y0 = W * 0.25 + mt * 900 * k, H * 0.12 + mt * 260 * k
        c.drawLine(x0, y0, x0 - 160 * k, y0 - 46 * k, P(c=col((255, 255, 255), 0.7 * (1 - mt / 0.8)), stroke=2 * k, cap=1))
    ground(c, W, H, st.cam, (6, 8, 10), (14, 16, 20))
    with st.at(300):
        c.drawPath(poly(ridge(np.random.default_rng(5), -900, 900, -30, 55, 160, 0.6)), P(c=col((14, 16, 22))))
    with st.at(80):
        rng = np.random.default_rng(2)
        c.drawRect(skia.Rect(-300, -6, 300, 0), P(c=col((10, 12, 14))))
        for i in range(140):
            c.drawCircle(rng.uniform(-60, 60), rng.uniform(-6, -1), rng.uniform(0.08, 0.2),
                         P(c=col((255, 214, 150), 0.55 + 0.35 * math.sin(t * rng.uniform(0.5, 3) + i))))
        # a car with headlights crossing the mesa road
        cx_ = lerp(-50, 50, t / d)
        c.drawCircle(cx_, -0.6, 0.35, P(c=col((255, 240, 200), 0.9)))
        c.drawCircle(cx_, -0.6, 2.2, P(c=col((255, 230, 180), 0.12), blur=1.0))
        # beacon on the water tower
        bl = 1.0 if (t % 1.6) < 0.3 else 0.15
        c.drawCircle(-20, -9, 0.35, P(c=col((255, 60, 50), bl)))
    with st.at(10):
        rng = np.random.default_rng(8)
        for x in np.arange(-30, 30, 2.2):
            c.save(); c.translate(x + rng.uniform(-0.6, 0.6), 0); c.skew(0.02 * math.sin(t * 0.8 + x), 0)
            pine(c, 0, rng.uniform(5, 8), (4, 6, 6))
            c.restore()
    small_tag(c, W, H, "2D ILLUSTRATION", DARK)


# ------------------------------------------------------------------ 146: end title over the living night mesa
@shot(146)
def v146(c, t, d, W, H):
    k = K(H)
    live_bg(c, 145, 7.0 + t, W, H, dark=0.35, sat=0.9)
    big_title(c, "OPPENHEIMER", W / 2, H * 0.48, 124 * k, t, 0.3, fc="semi", track=0.32, align="center", dur=1.6, drift=0.01)
    a = eout(clamp((t - 1.5) / 1.0))
    c.drawLine(W / 2 - 330 * k * a, H * 0.535, W / 2 + 330 * k * a, H * 0.535, P(c=col(TITLE["accent"], a), stroke=2 * k))
    big_title(c, "THE MAN WHO CREATED THE POWER TO DESTROY THE WORLD", W / 2, H * 0.59, 26 * k, t, 1.9, fc="med",
              color=(222, 214, 198), track=0.2, align="center", dur=1.8, drift=0.004)
    big_title(c, "1904 – 1967", W / 2, H * 0.66, 24 * k, t, 3.0, fc="mono", color=TITLE["accent"], track=0.3, align="center", dur=0.8, drift=0.0)


# ------------------------------------------------------------------ 147: rolling credits over the stars
@shot(147)
def v147(c, t, d, W, H):
    k = K(H)
    live_bg(c, 145, 14.0 + t, W, H, dark=0.6, sat=0.8)
    lines = [("SOURCES AND DATA", 30, "semi", LIGHT), ("", 16, "reg", SOFT),
             ("Archival photographs", 20, "semi", TITLE["accent"]),
             ("U.S. National Archives · U.S. Air Force (Hiroshima and Nagasaki, 1945)", 20, "reg", SOFT),
             ("Los Alamos National Laboratory (identification photograph)", 20, "reg", SOFT),
             ("Trinity fireball: Berlyn Brixner, Jack Aeby", 20, "reg", SOFT), ("", 14, "reg", SOFT),
             ("Maps", 20, "semi", TITLE["accent"]),
             ("Natural Earth · world-atlas · us-atlas · Historical Basemaps (1938 boundaries)", 20, "reg", SOFT), ("", 14, "reg", SOFT),
             ("Figures", 20, "semi", TITLE["accent"]),
             ("U.S. Strategic Bombing Survey (1946) · City of Hiroshima · Los Alamos National Laboratory", 20, "reg", SOFT), ("", 14, "reg", SOFT),
             ("Documents marked RECREATION are re-set from the originals.", 20, "reg", SOFT),
             ("2D reconstructions are dramatised illustrations, not historical records.", 20, "med", LIGHT)]
    total = sum((sz + 26) for _, sz, _, _ in lines) * k
    y = H * 0.92 - (t / d) * (total + H * 0.2)
    for s_, sz, fc, colr in lines:
        if -40 * k < y < H + 40 * k:
            a = clamp(min((y - H * 0.08) / (H * 0.12), (H * 0.95 - y) / (H * 0.1)))
            text(c, s_, W / 2, y, sz * k, fc, colr, a, align="center", track=0.08 if fc == "semi" else 0.0, shadow=0.8)
        y += (sz + 26) * k


# ------------------------------------------------------------------ 142: Trinity obelisk at dusk, wind and birds
@shot(142)
def v142(c, t, d, W, H):
    k = K(H)
    st = Stage(c, W, H, x=track(t, d, -1.4, -0.4), y=-1.6, z=track(t, d, -7.0, -4.6))
    sun = t / d
    sky(c, W, H, mix((24, 34, 66), (16, 22, 46), sun), mix((236, 150, 100), (190, 100, 80), sun))
    # sinking sun disc behind the ridge
    sx, sy = W * 0.8, H * (0.36 + 0.05 * sun)
    c.drawCircle(sx, sy, 160 * k, P(c=col((255, 190, 120), 0.25), blur=60 * k))
    c.drawCircle(sx, sy, 34 * k, P(c=col((255, 214, 160), 0.9)))
    # drifting clouds
    rng = np.random.default_rng(4)
    for i in range(7):
        x = (rng.uniform(0, W * 1.4) + t * 18 * k * (1 + i % 3)) % (W * 1.4) - W * 0.2
        y = H * rng.uniform(0.08, 0.36)
        r = rng.uniform(80, 180) * k
        c.drawOval(skia.Rect(x - r * 2, y - r * 0.25, x + r * 2, y + r * 0.25), P(c=col((255, 170, 130), 0.25), blur=r * 0.2))
    ground(c, W, H, st.cam, (60, 50, 50), (110, 80, 70))
    with st.at(600):
        c.drawPath(poly(ridge(np.random.default_rng(12), -1600, 1600, -26, 40, 140, 0.55)), P(c=col((40, 34, 50))))
    with st.at(6):
        c.drawPath(poly([(-0.9, 0), (-0.6, -3.6), (0, -3.9), (0.6, -3.6), (0.9, 0)]), P(c=col((30, 28, 30))))
        c.drawPath(poly([(0.25, 0), (0.45, -3.6), (0, -3.9), (0.6, -3.6), (0.9, 0)]), P(c=col((255, 170, 120), 0.12)))
        c.drawRect(skia.Rect(-0.35, -2.2, 0.35, -1.7), P(c=col((90, 80, 60))))
        c.drawLine(-12, -1.0, 12, -1.0, P(c=col((30, 30, 30), 0.6), stroke=0.01))
        # ravens circling high above
        for i in range(3):
            a = t * 0.6 + i * 2.1
            bx, by = math.cos(a) * 4 + i, -7 - math.sin(a) * 1.2
            fl = math.sin(t * 9 + i) * 0.12
            c.drawPath(poly([(bx - 0.25, by - fl), (bx, by), (bx + 0.25, by - fl)], close=False), P(c=col((20, 16, 20)), stroke=0.05, cap=1))
    # tumbleweeds rolling through on the wind
    with st.at(3.5):
        for i in range(3):
            x = -9 + ((t * (2.2 + i * 0.6) + i * 5) % 18)
            r = 0.22 + 0.08 * i
            y = -r - abs(math.sin(t * 4 + i)) * 0.25
            c.save(); c.translate(x, y); c.rotate(t * 300 + i * 50)
            for j in range(9):
                c.drawCircle(math.cos(j) * r * 0.4, math.sin(j * 1.7) * r * 0.4, r * 0.7, P(c=col((90, 70, 54), 0.9), stroke=0.025))
            c.restore()
    with st.at(-1.5):
        rng = np.random.default_rng(21)
        for i in range(70):
            x = rng.uniform(-9, 9)
            h = rng.uniform(0.15, 0.5)
            sway = math.sin(t * 2.6 + x * 1.7) * 0.06 * h / 0.3
            for j in range(3):
                dx = (j - 1) * 0.03
                c.drawLine(x + dx, 0, x + dx * 3 + sway, -h * (0.8 + 0.2 * j), P(c=col((54, 44, 38)), stroke=0.012, cap=1))
    shots_b.card(c, W, H, t, d, DARK, "TRINITY SITE GROUND ZERO MONUMENT", "ERECTED 1965 · TODAY")
    small_tag(c, W, H, "2D ILLUSTRATION · PRESENT DAY", DARK)


PARTICLES[142] = "dust"


# ------------------------------------------------------------------ 129: arms race with a flash for every first test
@shot(129)
def v129(c, t, d, W, H):
    k = K(H)
    m = shots_c.mv("world", "+proj=robin +datum=WGS84", (-180, -60, 180, 85))
    tests = [(-106.48, 33.68, "USA 1945", 0.4), (77.82, 50.44, "USSR 1949", 1.4), (115.55, -20.4, "UK 1952", 2.4),
             (162.19, 11.67, "USA 1952 · H-BOMB", 3.2), (0.06, 26.31, "FRANCE 1960", 4.4), (89.8, 40.82, "CHINA 1964", 5.6)]
    mat, mpx = draw_map(c, W, H, m, (track(t, d, 20, 50), 22), track(t, d, 38000, 30000), CW, grat=30,
                        markers=[(lo, la, name, shots_c.ping(t, t0), "key", (12, -10)) for lo, la, name, t0 in tests])
    for lo, la, name, t0 in tests:
        v = t - t0
        if v < 0:
            continue
        p = m.S(mat, lo, la)
        r = (30 + 260 * eout(clamp(v / 1.5))) * k
        c.drawCircle(p.x(), p.y(), r, P(c=col((255, 214, 150), 0.7 * math.exp(-v * 1.6)), stroke=4 * k))
        c.drawCircle(p.x(), p.y(), 60 * k, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            (p.x(), p.y()), 60 * k, [col((255, 240, 200), 0.9 * math.exp(-v * 2.5)), col((255, 200, 120), 0)])))
    n = sum(1 for lo, la, name, t0 in tests if t >= t0 and "H-BOMB" not in name)
    # running bar of nuclear-armed states
    bx, by = W - 380 * k, H - 120 * k
    for i in range(5):
        on = i < n
        c.drawRect(skia.Rect(bx + i * 62 * k, by, bx + i * 62 * k + 48 * k, by + 20 * k), P(c=col(CW["accent"] if on else (60, 70, 80), 0.95 if on else 0.5)))
    text(c, f"NUCLEAR-ARMED STATES: {n}", W - 64 * k, by - 18 * k, 24 * k, "monom", CW["accent"], 1, align="right", shadow=0.8)
    map_title(c, W, H, CW, "THE NUCLEAR ARMS RACE, 1945–1964", "FIRST TESTS BY EACH NUCLEAR POWER", clamp(t / 0.8))
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", CW)


# ------------------------------------------------------------------ 106 (v2): bombsight over a readable delta with the T-bridge
def _delta_ground(c, W, H, ox, oy, s, t, k):
    """Stylised plan view of the Ota delta: seven river channels fanning south to the bay, city blocks,
    and the T-shaped Aioi Bridge at the origin. Units: 1 = ~1 km, scaled by s px."""
    c.save(); c.translate(ox, oy); c.scale(s, s)
    c.drawRect(skia.Rect(-12, -12, 12, 12), P(c=col((120, 124, 106))))
    rng = np.random.default_rng(7)
    for i in range(900):
        x, y = rng.uniform(-11, 11), rng.uniform(-11, 9)
        c.drawRect(skia.Rect(x, y, x + rng.uniform(0.08, 0.22), y + rng.uniform(0.06, 0.16)), P(c=col(mix((150, 146, 132), (96, 98, 86), rng.uniform()), 0.8)))
    c.drawRect(skia.Rect(-12, 6.5, 12, 12), P(c=col((84, 104, 116))))
    river = P(c=col((96, 118, 128)), stroke=0.32, cap=1)
    for x0, x1 in ((-0.2, -4.5), (-0.2, -2.0), (0.0, 0.2), (0.15, 2.0), (0.2, 3.6), (0.3, 5.4)):
        path = skia.Path(); path.moveTo(0, -11); path.lineTo(0, -1.5)
        path.cubicTo(x0, 0.5, x1 * 0.6, 3, x1, 6.8)
        c.drawPath(path, river)
    # Aioi Bridge: the T where the river forks
    c.drawLine(-0.7, 0.0, 0.7, 0.0, P(c=col((200, 196, 184)), stroke=0.09))
    c.drawLine(0.0, 0.0, 0.0, 0.5, P(c=col((200, 196, 184)), stroke=0.09))
    c.restore()


@shot(106)
def v106b(c, t, d, W, H):
    k = K(H)
    u = t / d
    R = H * 0.42
    c.clear(col((0, 0, 0)))
    c.save()
    path = skia.Path(); path.addCircle(W / 2, H / 2, R)
    c.clipPath(path, doAntiAlias=True)
    s = lerp(70, 110, u) * k
    jit = (math.sin(t * 13) * 2 * k, math.cos(t * 11) * 2 * k)
    ox = W / 2 + lerp(-1.2, 0.0, u) * s + jit[0]
    oy = H / 2 + lerp(-5.5, 0.0, u) * s + jit[1]
    _delta_ground(c, W, H, ox, oy, s, t, k)
    rng = np.random.default_rng(3)
    for i in range(10):
        y = (rng.uniform(0, H * 1.5) + t * 260 * k) % (H * 1.5) - H * 0.25
        x = rng.uniform(W * 0.3, W * 0.7)
        r = rng.uniform(60, 140) * k
        c.drawOval(skia.Rect(x - r, y - r * 0.6, x + r, y + r * 0.6), P(c=col((240, 242, 244), 0.55), blur=r * 0.4))
    c.restore()
    c.drawCircle(W / 2, H / 2, R, P(c=col((0, 0, 0)), stroke=12 * k))
    c.drawCircle(W / 2, H / 2, R * 1.05, P(c=col((0, 0, 0), 0.8), blur=30 * k, stroke=40 * k))
    cp = P(c=col((20, 20, 20), 0.9), stroke=1.8 * k)
    c.drawLine(W / 2 - R, H / 2, W / 2 + R, H / 2, cp)
    c.drawLine(W / 2, H / 2 - R, W / 2, H / 2 + R, cp)
    for i in range(1, 8):
        r = i * R / 8
        c.drawLine(W / 2 - 8 * k, H / 2 + r, W / 2 + 8 * k, H / 2 + r, cp)
        c.drawLine(W / 2 + r, H / 2 - 8 * k, W / 2 + r, H / 2 + 8 * k, cp)
    mono_layer(c, W, H, 0.5)
    text(c, "AIMING POINT: AIOI BRIDGE", W / 2 + R * 1.1, H * 0.84, 18 * k, "mono", MONO["fg"], clamp((t - 0.4) / 0.6), track=0.1, shadow=0.8)
    text(c, f"8:14:{int(25 + u * 30):02d} AM", W / 2 + R * 1.1, H * 0.84 + 32 * k, 24 * k, "monom",
         MONO["accent"], clamp((t - 0.4) / 0.6), track=0.06, shadow=0.8)
    small_tag(c, W, H, "2D RECONSTRUCTION", MONO)


NO_KINETIC.add(106)


def _inset(c, W, H, n, tsrc, px, py, x, y, w, h, a, k, label=None):
    if a <= 0.01:
        return
    c.drawLine(px, py, x + (0 if x > px else w), y + h / 2, P(c=col((236, 228, 210), 0.7 * a), stroke=1.6 * k))
    img = live(n, tsrc, w, h)
    panel(c, img, x, y + (1 - eout(a)) * 30 * k, w, h, a=a, k=k, border=5 * k)
    if label:
        text(c, label, x, y + h + 34 * k, 18 * k, "semi", LIGHT, a, track=0.1, shadow=0.8)


# ------------------------------------------------------------------ 92: Marianas, with North Field coming alive
@shot(92)
def v92(c, t, d, W, H):
    k = K(H)
    m = shots_c.mv("pac", "+proj=lcc +lat_1=12 +lat_2=30 +lat_0=22 +lon_0=140 +datum=WGS84", (120, 5, 160, 40), "land-10m.json")
    z = ease((t - 0.3) / 3.6)
    ping = shots_c.ping
    mat, mpx = draw_map(c, W, H, m, (lerp(140, 145.4, z), lerp(22, 15.0, z)), math.exp(lerp(math.log(4200), math.log(300), z)), MONO, grat=5,
                        markers=[(144.79, 13.44, "GUAM", ping(t, 1.0), "dot", (12, 4)), (145.75, 15.18, "SAIPAN", ping(t, 1.0), "dot", (12, -8)),
                                 (145.63, 14.99, "TINIAN", ping(t, 2.6), "key", (-14, 16)), (141.32, 24.78, "IWO JIMA", ping(t, 0.6) * (1 - z), "dot", (12, -8)),
                                 (135.5, 34.7, "JAPAN", (1 - z), "dot", (12, -8))],
                        routes=[([(145.63, 14.99), (141.32, 24.78), (135.5, 34.7)], clamp(t / 2.4) * (1 - z) + 0.0, (150, 150, 150))])
    p = m.S(mat, 145.63, 14.99)
    _inset(c, W, H, 94, 1.0 + t, p.x(), p.y(), W * 0.6, H * 0.2, 560 * k, 315 * k, clamp((t - 3.2) / 0.7), k,
           label="NORTH FIELD, TINIAN · AUGUST 1945")
    location_card(c, W, H, [("TINIAN, NORTHERN MARIANA ISLANDS", 26, "semi", "fg"), ("NORTH FIELD · 509th COMPOSITE GROUP", 16, "mono", "fg"),
                            ("26 July 1945 — USS Indianapolis delivers Little Boy components", 16, "reg", "accent")], clamp((t - 3.8) / 0.8), MONO)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", MONO)


# ------------------------------------------------------------------ 120: both cities, with the two clouds
@shot(120)
def v120(c, t, d, W, H):
    k = K(H)
    m = shots_c.mv("jp", shots_c.JAPAN, (125, 28, 146, 46))
    HI, NA = shots_c.HIRO, shots_c.NAGA
    mat, mpx = draw_map(c, W, H, m, (track(t, d, 131.0, 131.4), track(t, d, 33.4, 33.7)), track(t, d, 1250, 1050), MONO, grat=2,
                        markers=[(HI[0], HI[1], "HIROSHIMA", 1.0, "target", (14, -12)), (NA[0], NA[1], "NAGASAKI", 1.0, "target", (-14, 18))])
    ph, pn = m.S(mat, *HI), m.S(mat, *NA)
    pw, phh = 420 * k, 236 * k
    _inset(c, W, H, 110, 1.0 + t, ph.x(), ph.y(), W - pw - 90 * k, H * 0.16, pw, phh, clamp((t - 0.6) / 0.7), k)
    _inset(c, W, H, 118, 1.0 + t, pn.x(), pn.y(), 90 * k, H * 0.2, pw, phh, clamp((t - 1.4) / 0.7), k)
    legend(c, W, H, [(MONO["accent"], "HIROSHIMA — 6 AUG 1945 — 8:15 AM — 'LITTLE BOY' (uranium, gun-type)", "dot"),
                     (MONO["accent"], "NAGASAKI — 9 AUG 1945 — 11:02 AM — 'FAT MAN' (plutonium, implosion)", "dot")],
           MONO, clamp((t - 2.0) / 0.8), y=H * 0.84)
    map_title(c, W, H, MONO, "THE TWO ATOMIC BOMBINGS", "AUGUST 1945", clamp(t / 0.8))
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH · ARCHIVAL INSETS", MONO)
