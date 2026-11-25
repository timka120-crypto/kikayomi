"""Scenes 1-4 (shots 1-33): opening, New York childhood, education, Berkeley."""
import math

import numpy as np
import skia

from engine import *  # noqa
from env import *  # noqa
from kit import *  # noqa
from reg import shot, Stage, track

GOLD = (201, 164, 99)
_G = {}


def globe():
    if "g" not in _G:
        _G["g"] = Globe(res=8192)
    return _G["g"]


def globe_scene(c, W, H, t, pal, lon0, lat0, R, cx=None, cy=None, points=(), stars_n=220):
    k = K(H)
    cx = W * 0.5 if cx is None else cx
    cy = H * 0.5 if cy is None else cy
    c.clear(col((7, 10, 15)))
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (cx, cy), W * 0.8, [col((22, 32, 44)), col((6, 9, 14))])))
    rng = np.random.default_rng(11)
    for _ in range(stars_n):
        c.drawCircle((rng.uniform(0, W) - t * 3 * k) % W, rng.uniform(0, H), rng.uniform(0.4, 1.3) * k,
                     P(c=col((220, 225, 235), rng.uniform(0.15, 0.55))))
    c.drawCircle(cx, cy, R * 1.12, skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (cx, cy), R * 1.12, [col((90, 140, 190), 0), col((90, 140, 190), 0), col((90, 140, 190), 0.28), col((90, 140, 190), 0)],
        [0, 0.86, 0.9, 1.0])))
    img = globe().render(W, H, cx, cy, R, lon0, lat0)
    c.drawImage(skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType), 0, 0)
    for lon, lat, name, a in points:
        x, y, vis = Globe.project(lon, lat, cx, cy, R, lon0, lat0)
        if a <= 0 or not vis:
            continue
        c.drawCircle(x, y, 4.5 * k, P(c=col(GOLD, a)))
        c.drawCircle(x, y, 11 * k, P(c=col(GOLD, a), stroke=1.3 * k))
        if name:
            text(c, name, x + 16 * k, y + 5 * k, 14 * k, "semi", GOLD, a, track=0.18)


def ping(t, t0):
    return clamp((t - t0) / 0.5)


# =========================================================== SCENE 1
@shot(1)
def s1(c, t, d, W, H):
    pal = PAL["title"]
    lon0 = lerp(-95, 10, ease((t - 2.4) / 1.6)) if t < 4.2 else lerp(10, 132, ease((t - 4.2) / 2.0))
    pts = [(-74.0, 40.7, "NEW YORK 1904", ping(t, 0.8)), (-122.3, 37.9, "BERKELEY 1929", ping(t, 1.3)),
           (-106.3, 35.9, "LOS ALAMOS 1943", ping(t, 1.8)), (9.9, 51.5, "GÖTTINGEN 1927", ping(t, 3.6)),
           (132.5, 34.4, "HIROSHIMA 1945", ping(t, 5.6)), (129.9, 32.8, "NAGASAKI 1945", ping(t, 6.0))]
    globe_scene(c, W, H, t, pal, lon0, lerp(28, 36, t / d), H * 0.36, points=pts)


@shot(2)
def s2(c, t, d, W, H):
    timeline(c, t, d, W, H, PAL["title"], events=[])


@shot(3)
def s3(c, t, d, W, H):
    photo_shot(c, t, d, W, H, "JROppenheimer-LosAlamos.jpg", PAL["title"], "LOS ALAMOS NATIONAL LABORATORY",
               start=(0.5, 0.5, 1.0), end=(0.5, 0.36, 1.25), fit="contain")


@shot(4)
def s4(c, t, d, W, H):
    title_card(c, t, d, W, H, PAL["title"], "OPPENHEIMER", "THE MAN WHO CREATED THE POWER TO DESTROY THE WORLD")


@shot(5)
def s5(c, t, d, W, H):
    pal = PAL["title"]; k = K(H)
    bg_fill(c, W, H, pal)
    items = [("ARCHIVAL", "real historical photographs"), ("RECREATION", "documents re-set from the originals"),
             ("2D RECONSTRUCTION", "dramatised illustration"), ("GRAPHICS", "maps, timelines and diagrams")]
    for i, (a_, b_) in enumerate(items):
        a = eout((t - 0.3 - i * 0.25) / 0.6)
        y = H * 0.36 + i * 70 * k
        c.drawRect(skia.Rect(W * 0.3, y - 22 * k, W * 0.3 + 10 * k, y + 2 * k), P(c=col(pal["accent"], a)))
        text(c, a_, W * 0.3 + 30 * k, y, 22 * k, "monom", pal["fg"], a, track=0.14)
        text(c, b_, W * 0.3 + 330 * k, y, 22 * k, "reg", pal["muted"], a)
    a = eout((t - 1.6) / 0.8)
    text(c, "Every shot in this film is labelled in the top-right corner.", W / 2, H * 0.72, 22 * k, "reg", pal["fg"], a, align="center")


@shot(6)
def s6(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.2, 0.2), y=-1.7, z=-0.8, f=1000)
    c.clear(col((30, 26, 22)))
    with st.at(2.2):
        wall(c, -6, 6, -4, (58, 50, 42), light=(-1.5, -2.4), light_r=2.5, light_a=0.25)
        blackboard(c, -3.2, -2.6, 3.4, -0.9, ["iħ ∂ψ/∂t = Ĥψ", "[x, p] = iħ", "H = p²/2m + V(x)", "ΔE · Δt ≥ ħ/2"],
                   size=0.2, start=(0.4, 0.38), gap=1.9)
        c.drawRect(skia.Rect(-2.5, -1.0, -2.2, -0.96), P(c=col((240, 238, 230))))  # chalk on ledge
        shaft = skia.Paint(Shader=skia.GradientShader.MakeLinear([(-3, -3), (1, 0)], [col((255, 230, 190), 0.16), col((255, 230, 190), 0)]))
        c.drawPath(poly([(-3.5, -3.2), (-2.2, -3.2), (1.5, 0.2), (-1.0, 0.2)]), shaft)
        rng = np.random.default_rng(3)
        for i in range(70):
            x = rng.uniform(-3, 1.5) + math.sin(t * 0.4 + i) * 0.1
            y = (rng.uniform(-3, 0) - t * 0.04 * rng.uniform(0.5, 1.5)) % 3.2 - 3.0
            c.drawCircle(x, y, 0.006, P(c=col((255, 240, 210), 0.5)))
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["title"])


# =========================================================== SCENE 2  (warm)
_MV = {}


def mv(key, proj, bbox, land="land-50m.json"):
    if key not in _MV:
        _MV[key] = MapView(proj, bbox, land)
    return _MV[key]


@shot(7)
def s7(c, t, d, W, H):
    pal = PAL["warm"]; k = K(H)
    m = mv("ne_us", "+proj=lcc +lat_1=38 +lat_2=44 +lat_0=41 +lon_0=-74 +datum=WGS84", (-82, 36, -66, 46), "land-10m.json")
    z = ease((t - 0.8) / 5.2)
    width = math.exp(lerp(math.log(900), math.log(70), z))
    center = (lerp(-74.6, -73.97, z), lerp(41.0, 40.79, z))
    mat, mpx = draw_map(c, W, H, m, center, width, pal, grat=2,
                        markers=[(-73.98, 40.79, "MANHATTAN", ping(t, 4.6), "key", (16, -12))],
                        labels=[(-72.6, 41.6, "CONNECTICUT", 13, 1 - z), (-75.3, 40.2, "PENNSYLVANIA", 13, 1 - z),
                                (-71.5, 39.6, "ATLANTIC OCEAN", 15, 1 - z)])
    scale_bar(c, W, H, mpx, pal, clamp(t / 1.2))
    date_counter(c, W, H, pal, "1904", clamp((t - 1) / 0.8))
    location_card(c, W, H, [("NEW YORK CITY, USA", 34, "semi", "fg"), ("22 APRIL 1904", 22, "med", "fg"),
                            ("J. Robert Oppenheimer is born", 18, "reg", "accent")], clamp((t - 4.8) / 0.9), pal)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", pal)


def riverside(c, st, t, d, opp=None):
    W, H = st.W, st.H
    sky(c, W, H, (176, 190, 196), (226, 222, 206))
    ground(c, W, H, st.cam, (110, 100, 86), (170, 162, 144))
    with st.at(220):
        c.drawPath(poly(ridge(np.random.default_rng(2), -400, 400, -18, 5, 80, 0.2)), P(c=col((150, 150, 140))))  # Palisades
    with st.at(90):
        c.drawRect(skia.Rect(-300, -1.2, 300, 0.5), P(c=col((140, 156, 160))))  # Hudson
        bx = -40 + t * 1.2
        c.drawRect(skia.Rect(bx, -3.2, bx + 9, -1.2), P(c=col((90, 80, 70))))
        c.drawRect(skia.Rect(bx + 5, -6.5, bx + 6, -3.2), P(c=col((60, 50, 44))))
        for i in range(10):
            life = (t * 0.3 + i / 10) % 1
            c.drawCircle(bx + 5.5 - life * 6, -7 - life * 4, 0.6 + life * 1.5, P(c=col((220, 220, 216), 0.3 * (1 - life)), blur=0.5))
    with st.at(32):
        for bx in (-40, -24, -8, 8, 24):
            building(c, bx, 14, 22, (206, 196, 176), rows=6, roof="flat", seed=int(bx) + 50)
    with st.at(14):
        for x in np.arange(-30, 30, 7):
            deciduous(c, x, 8, (96, 120, 70), t)
        c.drawRect(skia.Rect(-60, -1.05, 60, -1.0), P(c=col((40, 36, 32))))
        for x in np.arange(-60, 60, 0.6):
            c.drawLine(x, -1.0, x, 0, P(c=col((40, 36, 32)), stroke=0.04))
    with st.at(8):
        hx = -14 + t * 2.2
        horse(c, hx, t * 6, (90, 66, 46))
        c.drawRect(skia.Rect(hx - 4.6, -2.3, hx - 1.8, -0.9), P(c=col((30, 28, 26))))
        for wx in (hx - 4.0, hx - 2.2):
            c.drawCircle(wx, -0.6, 0.6, P(c=col((30, 28, 26)), stroke=0.06))
        car_1940(c, 18 - t * 3.0, (30, 30, 30), wheel_t=-t * 3, facing=-1)
    with st.at(5):
        if opp:
            opp(c, t)
        nx = -3 + t * 0.9
        draw_person(c, WOMAN, walk_pose(t * 4.8, 0.8), x=nx, facing=1)
        c.drawRect(skia.Rect(nx + 0.45, -0.9, nx + 1.2, -0.5), P(c=col((60, 50, 40))))
        c.drawCircle(nx + 0.6, -0.25, 0.2, P(c=col((30, 30, 30)), stroke=0.03))
        c.drawCircle(nx + 1.05, -0.25, 0.2, P(c=col((30, 30, 30)), stroke=0.03))
        draw_person(c, OFFICIAL, walk_pose(t * 5.0 + 1, 0.9), x=6 - t * 1.1, facing=-1)


@shot(8)
def s8(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1, 2), y=lerp(-7, -1.7, eout(t / 3.2)), z=0.0)
    riverside(c, st, t, d)
    location_card(c, W, H, [("RIVERSIDE DRIVE, MANHATTAN", 30, "semi", "fg"), ("c. 1912", 18, "mono", "fg")],
                  win(t, 0.8, d - 0.2, 0.7), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(9)
def s9(c, t, d, W, H):
    st = Stage(c, W, H, x=0.6, y=-1.15, z=track(t, d, -0.4, 0.6), f=1300)
    c.clear(col((60, 52, 44)))
    with st.at(3.4):
        wall(c, -5, 5, -4, (120, 104, 86), light=(1.2, -1.6), light_r=3, light_a=0.25)
        def view(cv, x0, y0, x1, y1):
            cv.drawRect(skia.Rect(x0, (y0 + y1) / 2 + 0.1, x1, y1), P(c=col((150, 166, 170))))
            cv.drawRect(skia.Rect(x0, (y0 + y1) / 2 - 0.08, x1, (y0 + y1) / 2 + 0.1), P(c=col((140, 140, 130))))
            sx = x0 + ((t * 0.06) % 1.2)
            cv.drawRect(skia.Rect(sx, (y0 + y1) / 2 - 0.02, sx + 0.25, (y0 + y1) / 2 + 0.08), P(c=col((70, 60, 54))))
        window(c, 0.3, -2.3, 2.0, -0.8, t, view=view, frame=(200, 190, 170))
        c.drawRect(skia.Rect(0.0, -2.45, 2.3, -2.35), P(c=col((210, 200, 180))))
        for i in range(2):
            c.drawRect(skia.Rect(0.0 + i * 2.0, -2.4, 0.3 + i * 2.0, 0), P(c=col((170, 120, 110), 0.9)))  # curtains
    with st.at(3.0):
        p = stand(head=-4, sh_r=40, el_r=80)
        idle(p, t, 1.0, 0.6)
        draw_person(c, OPP_CHILD, p, x=0.9, facing=1, rim=0.4)
    location_card(c, W, H, [("J. ROBERT OPPENHEIMER", 30, "semi", "fg"), ("c. 1912 · AGE 8", 18, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


def mineral_cabinet(c, x0, x1, y0, y1, seed=4):
    rng = np.random.default_rng(seed)
    c.drawRect(skia.Rect(x0, y0, x1, y1), P(c=col((74, 52, 36))))
    for r in range(4):
        yy = y0 + (r + 1) * (y1 - y0) / 4.3
        c.drawRect(skia.Rect(x0 + 0.05, yy, x1 - 0.05, yy + 0.03), P(c=col((54, 38, 28))))
        x = x0 + 0.12
        while x < x1 - 0.15:
            s = rng.uniform(0.05, 0.11)
            colr = [(200, 200, 210), (150, 100, 160), (210, 170, 90), (90, 140, 120), (180, 80, 60)][rng.integers(0, 5)]
            pts = [(x + s * math.cos(a) * rng.uniform(0.6, 1), yy - s + s * math.sin(a) * rng.uniform(0.6, 1)) for a in np.linspace(0, 6.28, 7)[:-1]]
            c.drawPath(poly(pts), P(c=col(colr)))
            text(c, "", x, yy, 1)
            x += s * 2.4
    c.drawRect(skia.Rect(x0, y0, x1, y1), P(c=col((220, 230, 240), 0.06)))


@shot(10)
def s10(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, 0.3, 0.6), y=-1.1, z=track(t, d, -0.6, 1.1), f=1250)
    c.clear(col((50, 40, 32)))
    with st.at(4.0):
        wall(c, -5, 5, -4, (110, 90, 70), light=(0.8, -1.4), light_r=2.6, light_a=0.32)
        mineral_cabinet(c, -2.6, -0.6, -2.6, -0.2)
        mineral_cabinet(c, 1.6, 3.4, -2.6, -0.2, seed=8)
    with st.at(3.2):
        table(c, -0.2, 1.4, top=-0.74, colr=(80, 52, 34))
        for i, (px, colr) in enumerate(((0.9, (210, 210, 220)), (1.15, (160, 110, 170)), (0.2, (200, 160, 80)))):
            c.drawPath(poly([(px - 0.05, -0.74), (px, -0.86), (px + 0.05, -0.74)]), P(c=col(colr)))
        g = 0.5 + 0.5 * math.sin(t * 2.4)
        c.drawCircle(0.9, -0.84, 0.03 + 0.02 * g, P(c=col((255, 255, 255), 0.5 * g), blur=0.02))
        chair(c, -0.45)
        p = sit(head=14, sh_r=lerp(40, 58, smooth((t - 1) / 2)), el_r=lerp(70, 92, smooth((t - 1) / 2)), lean=14)
        idle(p, t, 2, 0.5)
        draw_person(c, OPP_CHILD, p, x=-0.4, facing=1, rim=0.5)
        # magnifying glass in the front hand
        hx, hy = 0.42 + 0.06 * math.sin(t * 0.8), -0.98
        c.drawCircle(hx, hy, 0.07, P(c=col((200, 210, 220), 0.35)))
        c.drawCircle(hx, hy, 0.07, P(c=col((160, 130, 70)), stroke=0.012))
    with st.at(1.6):
        desk_fg(c, -3, 3, top=-0.5, items=False, blur=0.02)
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


def crystal_icon(c, t, x, y, k):
    pts3 = []
    for i in range(6):
        a = i / 6 * 6.283
        pts3 += [(math.cos(a), -1.0, math.sin(a)), (math.cos(a), 1.0, math.sin(a))]
    pts3 += [(0, -2.0, 0), (0, 2.0, 0)]
    rot = t * 0.8
    def pr(p):
        X, Y, Z = p
        X, Z = X * math.cos(rot) - Z * math.sin(rot), X * math.sin(rot) + Z * math.cos(rot)
        Y2 = Y * math.cos(0.3) - Z * math.sin(0.3)
        return x + 120 * k + X * 70 * k, y - 20 * k + Y2 * 70 * k
    sp = P(c=col((230, 214, 180), 0.9), stroke=1.4 * k)
    for i in range(6):
        j = (i + 1) % 6
        for a_, b_ in ((2 * i, 2 * j), (2 * i + 1, 2 * j + 1), (2 * i, 2 * i + 1), (2 * i, 12), (2 * i + 1, 13)):
            c.drawLine(*pr(pts3[a_]), *pr(pts3[b_]), sp)


@shot(11)
def s11(c, t, d, W, H):
    callout(c, t, d, W, H, PAL["warm"], ["Age 12 — presents a paper on minerals to the New York Mineralogical Club."],
            icon=crystal_icon, maxw=760)
    small_tag(c, W, H, "GRAPHICS", PAL["warm"])


@shot(12)
def s12(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.2, 0.6), y=-1.3, z=track(t, d, -1.5, -0.2))
    c.clear(col((70, 60, 50)))
    with st.at(7):
        wall(c, -8, 8, -4.5, (150, 134, 110), light=(0, -2.5), light_r=6, light_c=(255, 245, 225), light_a=0.25)
        window(c, -6.5, -3.4, -4.8, -1.0, t, frame=(210, 200, 180))
        window(c, 5.0, -3.4, 6.7, -1.0, t, frame=(210, 200, 180))
        blackboard(c, -2.6, -2.9, 2.8, -1.1, ["2 H₂ + O₂ → 2 H₂O", "CaCO₃ → CaO + CO₂", "PV = nRT"], size=0.22, gap=1.8,
                   reveal=0.75 + 0.25 * clamp(t / d))
        p = stand(sh_r=lerp(100, 115, 0.5 + 0.5 * math.sin(t * 6)), el_r=20, head=-6)
        draw_person(c, OFFICIAL if False else Look(height=1.78, build=1.1, suit=(60, 56, 52), suit_dark=(48, 44, 40), hat=None,
                                                   hair=(120, 110, 100), moustache=True), p, x=-1.1, facing=1)
    with st.at(4.6):
        for x in (-4, -2.4, -0.8, 0.8, 2.4):
            table(c, x - 0.1, x + 0.9, top=-0.76, colr=(90, 66, 46))
        crowd_row(c, -4.2, 3.4, [STUDENT, STUDENT2], seated=True, t=t, seed=3, spacing=1.6)
    with st.at(3.4):
        table(c, 0.3, 1.5, top=-0.76, colr=(90, 66, 46))
        p = sit(head=10, sh_r=lerp(50, 70, win(t, 3, 4.5, 0.4)), el_r=lerp(100, 60, win(t, 3, 4.5, 0.4)))
        idle(p, t, 4, 0.6)
        draw_person(c, OPP_TEEN, p, x=0.4, facing=1, rim=0.3)
        c.drawRect(skia.Rect(0.75, -0.8, 1.15, -0.77), P(c=col((230, 224, 210))))
    location_card(c, W, H, [("ETHICAL CULTURE SCHOOL, NEW YORK", 28, "semi", "fg"), ("1919", 18, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(13)
def s13(c, t, d, W, H):
    timeline(c, t, d, W, H, PAL["warm"], [(1904, "1904 — Born, New York City"), (1921, "1921 — Graduates, Ethical Culture School")],
             focus=(1900, 1925))
    small_tag(c, W, H, "GRAPHICS", PAL["warm"])


# =========================================================== SCENE 3
def leaves(c, t, x0, x1, top, n=40, seed=1, colr=(190, 120, 50)):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1) + math.sin(t * 1.3 + i) * 0.5 + t * 0.3
        y = (rng.uniform(top, 0) + t * rng.uniform(0.3, 0.7)) % (-top) + top
        c.save(); c.translate(x, y); c.rotate(t * 90 + i * 30)
        c.drawOval(skia.Rect(-0.06, -0.03, 0.06, 0.03), P(c=col(mix(colr, (120, 60, 20), rng.uniform(0, 0.5)))))
        c.restore()


@shot(14)
def s14(c, t, d, W, H):
    ox = -4 + 1.3 * t
    st = Stage(c, W, H, x=ox + 1.0, y=-1.4, z=0.2)
    sky(c, W, H, (150, 170, 186), (226, 214, 190))
    ground(c, W, H, st.cam, (96, 86, 64), (150, 140, 110))
    with st.at(40):
        for bx in (-40, -18, 4, 26):
            building(c, bx, 18, 14, (150, 70, 52), rows=4, seed=int(bx) + 9, brick=True)
    with st.at(16):
        for x in np.arange(-30, 40, 8):
            deciduous(c, x, 11, (190, 120, 50), t)
    with st.at(5):
        c.drawRect(skia.Rect(ox - 40, -0.02, ox + 40, 0.04), P(c=col((170, 156, 130))))
        for i, xx in enumerate((ox + 6 - t * 2.4, ox + 9 - t * 2.2)):
            draw_person(c, [STUDENT, STUDENT2][i], walk_pose(t * 5 + i, 0.9), x=xx, facing=-1)
        p = walk_pose(t * 5.4)
        p.sh_l, p.el_l = 5, 80
        draw_person(c, OPP_YOUNG, p, x=ox, facing=1)
        for j, colr in enumerate(((120, 40, 36), (40, 60, 90), (90, 80, 50))):
            c.drawRect(skia.Rect(ox - 0.12, -1.18 + j * 0.06, ox + 0.2, -1.12 + j * 0.06), P(c=col(colr)))
        leaves(c, t, ox - 6, ox + 6, -6)
    location_card(c, W, H, [("HARVARD UNIVERSITY, CAMBRIDGE, MASS.", 28, "semi", "fg"), ("1922", 18, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(15)
def s15(c, t, d, W, H):
    st = Stage(c, W, H, x=0.5, y=track(t, d, -3.2, -1.3), z=track(t, d, -1.2, 0.4))
    c.clear(col((30, 26, 22)))
    with st.at(6):
        wall(c, -8, 8, -6, (60, 48, 38))
        for x in (-6, -3.6, -1.2, 1.2, 3.6):
            bookshelf(c, x, x + 2.2, -4.5, -0.05, seed=abs(int(x * 3)) + 20)
    with st.at(3.6):
        table(c, -2, 3, top=-0.76, colr=(70, 50, 36))
        for lx in (-1.0, 1.8):
            c.drawLine(lx, -0.76, lx, -1.15, P(c=col((50, 60, 50)), stroke=0.02))
            c.drawPath(poly([(lx - 0.16, -1.12), (lx + 0.16, -1.12), (lx + 0.08, -1.24), (lx - 0.08, -1.24)]), P(c=col((40, 90, 60))))
            c.drawCircle(lx, -0.95, 0.6, P(c=col((255, 220, 160), 0.18), blur=0.3))
        for j in range(5):
            c.drawRect(skia.Rect(0.9 + j * 0.02, -0.82 - j * 0.05, 1.3, -0.77 - j * 0.05), P(c=col([(120, 40, 36), (40, 60, 90), (90, 80, 50)][j % 3])))
        chair(c, 0.1)
        p = sit(head=16, sh_r=58, el_r=86, lean=12)
        if (t % 2.2) < 0.35:
            p.sh_l, p.el_l = 60, 60
        idle(p, t, 5, 0.5)
        draw_person(c, OPP_YOUNG, p, x=0.1, facing=1, rim=0.5)
        c.drawRect(skia.Rect(0.45, -0.8, 0.85, -0.77), P(c=col((228, 220, 200))))
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(16)
def s16(c, t, d, W, H):
    callout(c, t, d, W, H, PAL["warm"], ["Degree in chemistry, summa cum laude, completed in three years."], title="HARVARD, 1922–1925")
    small_tag(c, W, H, "GRAPHICS", PAL["warm"])


@shot(17)
def s17(c, t, d, W, H):
    pal = PAL["warm"]
    m = mv("atl", "+proj=lcc +lat_1=40 +lat_2=55 +lat_0=48 +lon_0=-30 +datum=WGS84", (-80, 25, 25, 65))
    u = ease(t / d)
    draw_map(c, W, H, m, (lerp(-32, -28, u), lerp(46, 48, u)), lerp(8200, 7400, u), pal, grat=10,
             routes=[([(-71.06, 42.36), (-40, 50), (0.12, 52.2)], clamp((t - 0.8) / 2.6), pal["ink"]),
                     ([(0.12, 52.2), (9.93, 51.53)], clamp((t - 3.6) / 1.4), pal["ink"])],
             markers=[(-71.06, 42.36, "BOSTON 1925", ping(t, 0.6), "dot", (-12, 18)),
                      (0.12, 52.2, "CAMBRIDGE, ENGLAND 1925", ping(t, 3.2), "key", (-14, -14)),
                      (9.93, 51.53, "GÖTTINGEN 1926", ping(t, 4.9), "key", (14, 20))],
             labels=[(-40, 40, "ATLANTIC OCEAN", 16, 1.0)])
    text(c, "schematic route", W * 0.4, H * 0.3, 13 * K(H), "monom", pal["ink"], clamp((t - 2) / 1) * 0.8)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", pal)


@shot(18)
def s18(c, t, d, W, H):
    st = Stage(c, W, H, x=0.7, y=-1.3, z=track(t, d, -0.8, 0.5), f=1250)
    c.clear(col((40, 40, 40)))
    with st.at(4.5):
        wall(c, -6, 6, -4.5, (84, 80, 72), light=(-2.4, -2.4), light_r=3, light_c=(220, 226, 230), light_a=0.25)
        window(c, -3.4, -3.4, -1.6, -1.2, t, frame=(60, 50, 44), sky_c=((170, 176, 182), (200, 204, 206)))
        bookshelf(c, 2.0, 4.4, -3.6, -1.0, seed=3, wood=(70, 56, 44))
    with st.at(3.4):
        table(c, -0.6, 2.6, top=-0.9, colr=(70, 54, 40))
        for i, x in enumerate((0.0, 0.5, 1.6, 2.2)):
            c.drawRect(skia.Rect(x, -1.3, x + 0.12, -0.9), P(c=col((190, 210, 220), 0.5)))
            c.drawCircle(x + 0.06, -1.32, 0.08, P(c=col((190, 210, 220), 0.5)))
        c.drawLine(0.06, -1.3, 0.56, -1.3, P(c=col((160, 120, 70)), stroke=0.012))
        fl = 0.06 + 0.02 * math.sin(t * 20)
        c.drawPath(poly([(1.0, -0.98), (1.04, -0.98 - fl * 2), (1.08, -0.98)]), P(c=col((90, 140, 255), 0.8)))
        frustr = smooth((t - 3.2) / 0.8)
        p = stand(lean=lerp(18, -4, frustr), head=lerp(18, -6, frustr), sh_r=lerp(80, 30, frustr), el_r=lerp(60, 110, frustr),
                  sh_l=lerp(60, 10, frustr), el_l=lerp(50, 20, frustr))
        p.sh_r += math.sin(t * 7) * 3 * (1 - frustr)
        draw_person(c, OPP_YOUNG, p, x=-0.05, facing=1, rim=0.3)
    location_card(c, W, H, [("CAVENDISH LABORATORY, CAMBRIDGE", 28, "semi", "fg"), ("1925", 18, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


def timber_house(c, x, w, h, colr, seed=0):
    building(c, x, w, h, colr, rows=3, seed=seed, door=True)
    beam = (70, 48, 34)
    for xx in np.arange(x, x + w + 0.01, w / 4):
        c.drawLine(xx, -h, xx, 0, P(c=col(beam), stroke=0.12))
    for yy in (-h, -h * 0.66, -h * 0.33):
        c.drawLine(x, yy, x + w, yy, P(c=col(beam), stroke=0.12))
    c.drawPath(poly([(x - 0.3, -h), (x + w / 2, -h - w * 0.7), (x + w + 0.3, -h)]), P(c=col((150, 70, 50))))


def bicycle(c, x, t, look, facing=1):
    c.save(); c.translate(x, 0); c.scale(facing, 1)
    for wx in (-0.55, 0.55):
        c.drawCircle(wx, -0.34, 0.34, P(c=col((30, 30, 30)), stroke=0.03))
    c.drawPath(poly([(-0.55, -0.34), (-0.1, -0.34), (0.1, -0.8), (0.55, -0.34)], close=False), P(c=col((40, 40, 40)), stroke=0.03))
    c.restore()
    p = Pose(hip_l=70 + 25 * math.sin(t * 5), hip_r=70 - 25 * math.sin(t * 5), knee_l=70, knee_r=70, sh_r=60, el_r=20, sh_l=55, el_l=20,
             bob=0.05, lean=14)
    draw_person(c, look, p, x=x - 0.1 * facing, facing=facing)


@shot(19)
def s19(c, t, d, W, H):
    ox = -3 + 1.0 * t
    st = Stage(c, W, H, x=ox + 0.8, y=track(t, d, -1.5, -2.3), z=-1.2)
    sky(c, W, H, (150, 170, 190), (214, 214, 206))
    ground(c, W, H, st.cam, (110, 104, 96), (150, 146, 136))
    with st.at(70):
        for tx in (-2.5, 4.5):
            c.drawRect(skia.Rect(tx - 2.6, -50, tx + 2.6, 0), P(c=col((130, 100, 84))))
            c.drawPath(poly([(tx - 3.0, -50), (tx, -66), (tx + 3.0, -50)]), P(c=col((80, 90, 84))))
            for yy in (-46, -40):
                c.drawRect(skia.Rect(tx - 0.8, yy, tx + 0.8, yy + 3), P(c=col((60, 46, 40))))
    with st.at(18):
        for i, bx in enumerate(np.arange(-26, 30, 7.5)):
            timber_house(c, bx, 7, 9 + (i % 3), [(222, 210, 186), (214, 200, 170), (230, 218, 196)][i % 3], seed=i)
    with st.at(5):
        for xx in np.arange(math.floor(ox - 20), ox + 20, 0.4):
            c.drawOval(skia.Rect(xx, -0.02, xx + 0.36, 0.04), P(c=col((120, 112, 100))))
        bicycle(c, ox + 9 - t * 3.6, t, STUDENT2, facing=-1)
        for i, (L, dx) in enumerate(((STUDENT, -0.9), (OPP_YOUNG, 0.0), (STUDENT2, 0.85))):
            p = walk_pose(t * 5.2 + i * 0.8, 0.9)
            if L is OPP_YOUNG:
                gesture(p, t, 1.0, 0.7)
            draw_person(c, L, p, x=ox + dx, facing=1, shade=0.1 if i != 1 else 0)
    location_card(c, W, H, [("GÖTTINGEN, GERMANY", 30, "semi", "fg"), ("1926", 18, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(20)
def s20(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -0.4, 1.0), y=-1.4, z=track(t, d, -1.4, -0.3))
    c.clear(col((50, 48, 46)))
    with st.at(6.5):
        wall(c, -7, 7, -4.5, (120, 116, 106), light=(0, -3), light_r=5, light_c=(230, 236, 240), light_a=0.2)
        window(c, -6, -3.4, -4.4, -1.0, t, frame=(80, 70, 60))
        blackboard(c, -2.2, -3.0, 3.6, -1.1, ["⎡ q₁₁  q₁₂ ⎤", "⎣ q₂₁  q₂₂ ⎦", "pq − qp = h/2πi"], size=0.24, gap=1.8,
                   reveal=clamp(0.5 + t / d * 0.6))
        p = stand(sh_r=lerp(108, 30, smooth((t - 3.5) / 0.6)), el_r=20, head=lerp(-8, 8, smooth((t - 3.5) / 0.6)))
        p.sh_r += math.sin(t * 6) * 3 * (1 - smooth((t - 3.5) / 0.6))
        draw_person(c, BORN, p, x=-1.0, facing=1 if t < 3.5 else -1)
    with st.at(4.2):
        table(c, -3.5, 3.5, top=-0.76, colr=(90, 66, 46))
        crowd_row(c, -3.0, -0.5, [STUDENT, STUDENT2], t=t, seed=2, spacing=1.1)
        p = sit(lean=lerp(6, 22, smooth((t - 3.8) / 0.6)), head=-6)
        if t > 3.8:
            gesture(p, t, 0.5, 1.0); p.sh_r += 20
        draw_person(c, OPP_YOUNG, p, x=0.5, facing=-1, rim=0.3)
        crowd_row(c, 1.6, 3.4, [STUDENT2, STUDENT], t=t, seed=5, spacing=1.1, facing=-1)
    location_card(c, W, H, [("UNIVERSITY OF GÖTTINGEN", 28, "semi", "fg"), ("MAX BORN'S SEMINAR · 1927", 18, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(21)
def s21(c, t, d, W, H):
    if "zfp" not in _G:
        _G["zfp"] = journal_page(1300, 1800, "ZEITSCHRIFT FÜR PHYSIK", "Band 41 · 1927",
                                 ["Zur Quantentheorie", "kontinuierlicher Spektren."], "Von J. R. Oppenheimer in Göttingen.",
                                 "", cols=1)
    document_shot(c, t, d, W, H, _G["zfp"], PAL["warm"], focus=(0.5, 0.15), highlight=(0.1, 0.24),
                  tag="RECREATION · ZEITSCHRIFT FÜR PHYSIK 41 (1927)")


@shot(22)
def s22(c, t, d, W, H):
    timeline(c, t, d, W, H, PAL["warm"], [(1921, "1921 — Ethical Culture School"), (1925, "1925 — Harvard degree"),
                                          (1927, "1927 — Doctorate in physics, Göttingen (adviser: Max Born)")],
             focus=(1918, 1932))
    small_tag(c, W, H, "GRAPHICS", PAL["warm"])


@shot(23)
def s23(c, t, d, W, H):
    pal = PAL["warm"]; k = K(H)
    c.clear(col((22, 26, 30)))
    cx, cy = W / 2, H * 0.52
    rot = t * 0.5
    sep = 150 * k
    n1 = (cx + math.cos(rot) * sep, cy + math.sin(rot) * sep * 0.35)
    n2 = (cx - math.cos(rot) * sep, cy - math.sin(rot) * sep * 0.35)
    rng = np.random.default_rng(0)
    for i in range(900):
        ang = rng.uniform(0, 6.283) + t * rng.uniform(2, 5)
        r = abs(rng.normal(0, 1)) * 140 * k + 30 * k
        base = n1 if i % 2 else n2
        x = base[0] * 0.5 + cx * 0.5 + math.cos(ang) * r * 1.6
        y = cy + math.sin(ang) * r * 0.75
        c.drawCircle(x, y, 2.2 * k, P(c=col((110, 200, 230), 0.16)))
    for n in (n1, n2):
        vib = math.sin(t * 2.5) * 4 * k
        c.drawCircle(n[0] + vib, n[1], 22 * k, P(c=col((214, 150, 86))))
        c.drawCircle(n[0] + vib - 7 * k, n[1] - 7 * k, 8 * k, P(c=col((255, 255, 255), 0.3)))
    a = eout((t - 0.8) / 0.8)
    label_line(c, n1[0], n1[1] - 26 * k, n1[0] + 120 * k, n1[1] - 180 * k, "NUCLEI — HEAVY, SLOW", k, pal, a)
    label_line(c, cx - 300 * k, cy + 120 * k, cx - 420 * k, cy + 240 * k, "ELECTRONS — LIGHT, FAST", k, pal, a, align="right")
    text(c, "BORN–OPPENHEIMER APPROXIMATION, 1927", 64 * k, 90 * k, 28 * k, "semi", pal["fg"], eout(t / 0.8), track=0.18)
    small_tag(c, W, H, "GRAPHICS", pal)


# =========================================================== SCENE 4
@shot(24)
def s24(c, t, d, W, H):
    pal = PAL["warm"]
    m = mv("ca", "+proj=lcc +lat_1=33 +lat_2=40 +lat_0=36 +lon_0=-120 +datum=WGS84", (-126, 30, -112, 43), "land-10m.json")
    u = ease(t / d)
    draw_map(c, W, H, m, (-120.2, 36.0), lerp(1500, 1250, u), pal, grat=2,
             routes=[([(-122.26, 37.87), (-118.13, 34.14)], clamp((t - 1.6) / 1.8), pal["ink"])],
             markers=[(-122.26, 37.87, "BERKELEY", ping(t, 0.8), "key", (-16, -12)), (-118.13, 34.14, "PASADENA (CALTECH)", ping(t, 1.3), "key", (16, -12))],
             labels=[(-124.5, 35, "PACIFIC OCEAN", 15, 1.0), (-118.5, 37.6, "SIERRA NEVADA", 12, 1.0)],
             fills=[("840", pal["land"], 0.0, False)])
    location_card(c, W, H, [("1929", 34, "semi", "fg"), ("Joins UC Berkeley and Caltech", 20, "reg", "fg")], clamp((t - 2.2) / 0.8), pal)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", pal)


@shot(25)
def s25(c, t, d, W, H):
    st = Stage(c, W, H, x=1.0, y=track(t, d, -1.6, -26), z=-2.0)
    sky(c, W, H, (120, 160, 200), (230, 214, 180))
    ground(c, W, H, st.cam, (130, 120, 100), (170, 160, 136))
    with st.at(80):
        c.drawRect(skia.Rect(-5, -78, 5, 0), P(c=col((214, 206, 190))))
        for yy in (-70, -66):
            for xx in (-3.5, -0.5, 2.5):
                c.drawRect(skia.Rect(xx, yy, xx + 1.2, yy + 3.5), P(c=col((60, 56, 50))))
        c.drawPath(poly([(-5.5, -78), (0, -94), (5.5, -78)]), P(c=col((180, 176, 166))))
        building(c, -50, 30, 16, (220, 212, 196), rows=3, roof="flat", seed=4)
        building(c, 20, 30, 16, (220, 212, 196), rows=3, roof="flat", seed=6)
    with st.at(22):
        for x in (-20, -12, 12, 22):
            deciduous(c, x, 13, (90, 120, 80), t)
    with st.at(6):
        for i in range(6):
            xx = -8 + ((t * 1.2 * (1 if i % 2 else -1) + i * 3.1) % 18)
            draw_person(c, [STUDENT, STUDENT2, WOMAN, WOMAN2][i % 4], walk_pose(t * 5 + i, 0.9), x=xx, facing=1 if i % 2 else -1)
    location_card(c, W, H, [("UNIVERSITY OF CALIFORNIA, BERKELEY", 28, "semi", "fg"), ("1930s", 18, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


def smoke_puffs(c, t, x, y, n=16, seed=0, a=0.15):
    rng = np.random.default_rng(seed)
    for i in range(n):
        life = (t * 0.35 + rng.uniform()) % 1
        c.drawCircle(x + math.sin(life * 5 + i) * 0.08 + life * 0.2, y - life * 0.9, 0.02 + life * 0.12,
                     P(c=col((220, 220, 224), a * (1 - life)), blur=0.04))


@shot(26)
def s26(c, t, d, W, H):
    st = Stage(c, W, H, x=0.6, y=track(t, d, -1.6, -1.8), z=track(t, d, -2.0, -0.6))
    c.clear(col((40, 36, 32)))
    with st.at(7):
        wall(c, -8, 8, -5, (120, 108, 92), light=(0, -3), light_r=6, light_c=(255, 240, 210), light_a=0.25)
        blackboard(c, -3.6, -3.2, 4.4, -1.1, ["ψ = Σ cₙ φₙ e^{−iEₙt/ħ}", "(iγ^μ ∂_μ − m) ψ = 0", "e⁺ + e⁻ → 2γ", "∫ |ψ|² dV = 1"],
                   size=0.24, gap=1.75)
        if t < d * 0.6:
            p = stand(sh_r=110 + math.sin(t * 7) * 4, el_r=18, head=-6, hand_r="chalk")
        else:
            p = gesture(stand(head=4, hand_r="cig"), t, 0.2, 1.0)
        draw_person(c, OPP_30S, p, x=-0.3 + 0.4 * smooth((t - d * 0.6) / 0.6), facing=1 if t < d * 0.6 else -1, rim=0.3)
        smoke_puffs(c, t, 0.2, -1.6, seed=2)
    with st.at(3.6):
        for x in (-4, -1.2, 1.6):
            table(c, x - 0.1, x + 2.4, top=-0.76, colr=(80, 60, 44))
        crowd_row(c, -4, 4, [STUDENT, STUDENT2], t=t, seed=7, spacing=0.95, shade=0.25)
    location_card(c, W, H, [("LECONTE HALL, BERKELEY", 28, "semi", "fg"), ("J. ROBERT OPPENHEIMER · PROFESSOR OF PHYSICS", 16, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(27)
def s27(c, t, d, W, H):
    eq = "E² = p²c² + m²c⁴"
    st = Stage(c, W, H, x=track(t, d, -0.2, 0.1), y=-1.65, z=-0.4, f=950)
    c.clear(col((30, 40, 36)))
    with st.at(2.0):
        blackboard(c, -3, -2.6, 3, -0.6, [eq], size=0.26, start=(1.6, 1.08), reveal=clamp(t / (d * 0.8)))
        n = len(eq) * clamp(t / (d * 0.8))
        hx = -1.4 + measure(eq[:int(n)], 13.5, "reg") * 0.26 / 13.5 + math.sin(t * 9) * 0.004
        hy = -1.58 + math.sin(t * 13) * 0.008
        c.drawLine(hx, hy, hx + 0.09, hy + 0.06, P(c=col((240, 238, 230)), stroke=0.03, cap=1))
        c.drawRoundRect(skia.Rect(hx + 0.06, hy + 0.03, hx + 0.3, hy + 0.12), 0.045, 0.045, P(c=col((196, 168, 146))))
        c.drawRect(skia.Rect(hx + 0.26, hy + 0.0, hx + 0.9, hy + 0.18), P(c=col((96, 92, 84))))
        c.drawLine(hx + 0.12, hy + 0.1, hx + 0.32, hy + 0.08, P(c=col((236, 232, 224)), stroke=0.016, cap=1))
        smoke_puffs(c, t, hx + 0.33, hy + 0.06, n=10, seed=4, a=0.16)
        for i in range(10):
            life = (t * 0.7 + i / 10) % 1
            c.drawCircle(hx + 0.02, hy + life * 0.5, 0.004, P(c=col((240, 240, 236), 0.6 * (1 - life))))
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(28)
def s28(c, t, d, W, H):
    pal = PAL["warm"]; k = K(H)
    bg_fill(c, W, H, pal)
    cards = [("1935", "Oppenheimer–Phillips process", "deuteron reactions"),
             ("1939", "Oppenheimer–Volkoff", "upper mass limit of neutron stars"),
             ("1939", "Oppenheimer–Snyder", "continued gravitational collapse")]
    for i, (yr, a_, b_) in enumerate(cards):
        a = eout((t - 0.4 - i * 0.6) / 0.6)
        x = W * 0.12 + i * W * 0.27
        y = H * 0.32 + (1 - a) * 30 * k
        c.drawRect(skia.Rect(x, y, x + W * 0.24, y + H * 0.36), P(c=col(pal["paper"], a * 0.95)))
        text(c, yr, x + 24 * k, y + 60 * k, 40 * k, "serifb", pal["ink"], a)
        text(c, a_, x + 24 * k, y + 110 * k, 22 * k, "serifb", pal["ink"], a)
        text(c, b_, x + 24 * k, y + 142 * k, 18 * k, "serif", pal["ink"], a * 0.85)
        cx, cy = x + W * 0.12, y + H * 0.27
        if i == 0:
            particle(c, cx - 20 * k, cy, 14 * k, (214, 150, 86), a); particle(c, cx + 8 * k, cy, 14 * k, (150, 156, 166), a)
        elif i == 1:
            c.drawCircle(cx, cy, 34 * k, P(c=col((120, 130, 150), a)))
            c.drawCircle(cx, cy, 34 * k + 6 * k * math.sin(t * 3), P(c=col(pal["ink"], a * 0.5), stroke=1.2 * k))
        else:
            for j in range(4):
                r = (46 - j * 11) * k * (1 - 0.2 * ((t * 0.5) % 1))
                c.drawCircle(cx, cy, r, P(c=col(pal["ink"], a * (0.3 + j * 0.2)), stroke=1.5 * k))
    small_tag(c, W, H, "GRAPHICS", pal)


@shot(29)
def s29(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, 0.6, 1.1), y=-1.5, z=track(t, d, -0.6, 0.6))
    c.clear(col((36, 30, 26)))
    with st.at(4.6):
        wall(c, -6, 6, -4.5, (96, 82, 66), light=(1.4, -2.2), light_r=3, light_a=0.3)
        window(c, -3.8, -3.0, -2.4, -1.2, t, sky_c=((60, 70, 100), (200, 140, 110)))
        blackboard(c, -1.2, -2.8, 3.6, -1.0, ["dτ² = (1 − rₛ/r) dt² − …", "r → rₛ"], size=0.18, gap=1.8)
        cx, cy = 2.2, -1.9
        for j in range(4):
            r = (0.55 - j * 0.12) * (1 if t > 1 + j * 0.6 else 0)
            if r > 0:
                c.drawCircle(cx, cy, r, P(c=col((222, 224, 214), 0.8), stroke=0.012))
        p = stand(sh_r=lerp(100, 30, smooth((t - 3.6) / 0.6)), el_r=20, hand_r="chalk", head=-4)
        p.sh_r += math.sin(t * 5) * 4 * (1 - smooth((t - 3.6) / 0.6))
        draw_person(c, OPP_30S, p, x=1.2, facing=1, rim=0.4)
        p2 = stand(head=-8, sh_r=50, el_r=90)
        idle(p2, t, 3, 1)
        draw_person(c, Look(height=1.74, build=1.25, suit=(170, 160, 140), suit_dark=(140, 132, 116), hat=None, hair=(50, 42, 36)),
                    p2, x=-0.6, facing=1, rim=0.3)
    with st.at(2.0):
        desk_fg(c, -3, 3.6, top=-0.62, lamp=True)
    location_card(c, W, H, [("BERKELEY · 1939", 28, "semi", "fg"), ("WITH GRADUATE STUDENT HARTLAND SNYDER", 16, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


def cyclotron(c, x, glow=0.0):
    c.drawRect(skia.Rect(x - 2.2, -3.0, x + 2.2, -2.4), P(c=col((60, 66, 72))))
    c.drawRect(skia.Rect(x - 2.2, -0.9, x + 2.2, -0.3), P(c=col((60, 66, 72))))
    c.drawRect(skia.Rect(x - 2.2, -3.0, x - 1.6, -0.3), P(c=col((54, 60, 66))))
    c.drawRect(skia.Rect(x - 1.5, -2.4, x + 1.9, -2.05), P(c=col((170, 96, 50))))
    c.drawRect(skia.Rect(x - 1.5, -1.25, x + 1.9, -0.9), P(c=col((170, 96, 50))))
    c.drawRect(skia.Rect(x - 1.2, -2.05, x + 1.6, -1.25), P(c=col((120, 126, 132))))
    c.drawRect(skia.Rect(x - 0.6, -1.75, x + 1.0, -1.55), P(c=col((200, 160, 255), glow)))
    c.drawRect(skia.Rect(x - 2.4, -0.3, x + 2.4, 0), P(c=col((40, 44, 48))))


@shot(30)
def s30(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.8, 1.2), y=-1.6, z=-1.0)
    c.clear(col((30, 32, 34)))
    with st.at(7):
        wall(c, -10, 10, -6, (70, 74, 76), light=(0, -5), light_r=6, light_c=(220, 230, 236), light_a=0.18)
        for x in (-6, -4.6, 4.2, 5.6):
            c.drawRect(skia.Rect(x, -3.4, x + 1.0, 0), P(c=col((50, 54, 58))))
            for yy in np.arange(-3.2, -0.4, 0.4):
                c.drawCircle(x + 0.5, yy, 0.08, P(c=col((255, 180, 90), 0.5 + 0.3 * math.sin(t * 3 + yy * 7))))
    with st.at(5):
        cyclotron(c, 0.4, 0.25 + 0.15 * math.sin(t * 2))
        p = stand(sh_r=lerp(20, 95, smooth((t - 1) / 0.6)), el_r=10, head=-4)
        draw_person(c, LAWRENCE, p, x=3.2, facing=-1)
        p2 = stand(lean=lerp(0, 14, smooth((t - 2) / 1)), sh_r=-10, sh_l=-10, el_r=60, el_l=60)
        idle(p2, t, 1, 0.7)
        draw_person(c, OPP_30S, p2, x=4.4, facing=-1)
        p3 = stand(sh_r=70, el_r=60, head=10)
        draw_person(c, Look(height=1.74, build=1.05, suit=(80, 84, 92), suit_dark=(64, 68, 74), hat=None, hair=(60, 50, 40)),
                    idle(p3, t, 4, 1), x=-2.8, facing=1)
    location_card(c, W, H, [("RADIATION LABORATORY, BERKELEY", 28, "semi", "fg"), ("ERNEST O. LAWRENCE · INVENTOR OF THE CYCLOTRON", 16, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(31)
def s31(c, t, d, W, H):
    if have_photo("lawrence_cyclotron_0.jpg"):
        photo_shot(c, t, d, W, H, "lawrence_cyclotron_0.jpg", PAL["warm"], "LAWRENCE BERKELEY NATIONAL LABORATORY", mode="sepia")
        return
    st = Stage(c, W, H, x=track(t, d, -0.8, 0.8), y=-1.5, z=-0.4, f=1000)
    c.clear(col((24, 26, 28)))
    with st.at(2.4):
        c.drawRect(skia.Rect(-3, -2.4, 3, -0.6), P(c=col((54, 50, 44))))
        for i, x in enumerate(np.arange(-2.6, 2.6, 0.75)):
            c.drawCircle(x, -1.9, 0.26, P(c=col((230, 224, 206))))
            c.drawCircle(x, -1.9, 0.26, P(c=col((40, 36, 30)), stroke=0.03))
            a = -2.2 + 1.6 * (0.5 + 0.5 * math.sin(t * 1.4 + i))
            c.drawLine(x, -1.9, x + math.cos(a) * 0.2, -1.9 + math.sin(a) * 0.2, P(c=col((150, 30, 30)), stroke=0.015))
        for i, x in enumerate(np.arange(-2.5, 2.6, 0.5)):
            c.drawCircle(x, -1.05, 0.06, P(c=col((255, 160, 80), 0.5 + 0.4 * math.sin(t * 4 + i))))
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])


@shot(32)
def s32(c, t, d, W, H):
    if "pr39" not in _G:
        _G["pr39"] = journal_page(1300, 1800, "PHYSICAL REVIEW", "VOLUME 56 · SEPTEMBER 1, 1939",
                                  ["On Continued Gravitational", "Contraction"], "J. R. OPPENHEIMER AND H. SNYDER",
                                  "University of California, Berkeley, California", "(Received July 10, 1939)")
    def flag(cc, tt):
        k = K(H)
        a = clamp((tt - 2.5) / 0.6)
        location_card(cc, W, H, [("PUBLISHED 1 SEPTEMBER 1939", 26, "semi", "fg"), ("the day Germany invades Poland", 18, "reg", "accent")],
                      a, PAL["warm"])
    document_shot(c, t, d, W, H, _G["pr39"], PAL["warm"], focus=(0.5, 0.12), highlight=(0.04, 0.2),
                  tag="RECREATION · PHYS. REV. 56, 455 (1939)", shift=0.17)
    flag(c, t)


@shot(33)
def s33(c, t, d, W, H):
    hx = -6 + 1.2 * t
    st = Stage(c, W, H, x=hx + 1.5, y=track(t, d, -2.0, -4.0), z=track(t, d, -3, -8))
    sky(c, W, H, (90, 140, 196), (220, 214, 196))
    ground(c, W, H, st.cam, (110, 120, 70), (150, 150, 110))
    rng = np.random.default_rng(9)
    with st.at(600):
        c.drawPath(poly(ridge(np.random.default_rng(3), -1200, 1200, -60, 70, 120, 0.6)), P(c=col((110, 130, 160))))
    with st.at(200):
        c.drawPath(poly(ridge(np.random.default_rng(4), -500, 500, -25, 30, 100, 0.5)), P(c=col((90, 110, 100))))
        cloud_layer(c, -300, 300, -120, 2, (250, 250, 250), 0.5, scale=4, drift=t * 2)
    with st.at(40):
        for x in np.arange(-80, 80, 5):
            pine(c, x + rng.uniform(-2, 2), rng.uniform(8, 13), (60, 80, 56))
        c.drawRect(skia.Rect(20, -3, 26, 0), P(c=col((110, 80, 56))))
        c.drawPath(poly([(19.5, -3), (23, -5), (26.5, -3)]), P(c=col((80, 60, 44))))
    with st.at(6):
        by = horse(c, hx, t * 5.5, (120, 80, 50))
        p = Pose(hip_l=55, hip_r=55, knee_l=70, knee_r=70, sh_r=55, el_r=40, sh_l=50, el_l=40, lean=4,
                 head=-4 + 6 * math.sin(t * 0.5), bob=by + 1.2 - 0.58)
        draw_person(c, OPP_RANCH, p, x=hx + 0.1, facing=1)
    with st.at(2.5):
        for x in np.arange(math.floor(hx - 10), hx + 12, 3.0):
            c.drawPath(poly([(x, 0), (x + 0.3, -0.6), (x + 0.5, 0)]), P(c=col((70, 90, 50)), blur=0.03))
    location_card(c, W, H, [("PECOS VALLEY, NEW MEXICO", 28, "semi", "fg"), ("1930s · THE LANDSCAPE HE WILL RETURN TO IN 1942", 16, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), PAL["warm"])
    small_tag(c, W, H, "2D RECONSTRUCTION", PAL["warm"])
