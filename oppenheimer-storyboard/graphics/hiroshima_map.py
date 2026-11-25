"""Storyboard shots 098-100: detailed map of Japan, smooth zoom into Hiroshima, location card.

Renders a 22-second documentary map animation straight to MP4 (H.264) with Skia + ffmpeg.
Data: Natural Earth 1:10m land (public domain, via world-atlas). Projection: Lambert
Conformal Conic (lat_1=30, lat_2=40, lat_0=35, lon_0=135), as in the storyboard map spec.

Usage: python3 hiroshima_map.py [--width 1920] [--fps 30] [--out ../renders/098-100_hiroshima_map.mp4]
       python3 hiroshima_map.py --stills 0,3,8,12,16,21   (PNG keyframes for review)
"""
import argparse, json, math, subprocess
from pathlib import Path

import numpy as np
import skia
from pyproj import Transformer

HERE = Path(__file__).parent
A = HERE / "assets"
DUR = 22.0

# ---------------------------------------------------------------- palette (cool slate, near-monochrome)
C = dict(
    sea=(14, 22, 30), sea2=(20, 31, 41), land=(44, 52, 60), land_hi=(52, 61, 70),
    coast=(150, 166, 178), grat=(255, 255, 255), text=(230, 226, 216), muted=(150, 160, 168),
    brass=(201, 164, 99), plate=(0, 0, 0),
)

# ---------------------------------------------------------------- places (lon, lat) - see storyboard COORDS table
HIRO = (132.4536, 34.3955)  # hypocentre, near Aioi Bridge
CITIES = [  # name, lon, lat, label anchor (dx, dy in px at 1080p), appear time
    ("TOKYO", 139.69, 35.68, (10, -8), 1.2),
    ("KYOTO", 135.77, 35.01, (9, -9), 1.45),
    ("OSAKA", 135.50, 34.69, (-9, 16), 1.7),
    ("KOKURA", 130.88, 33.88, (-9, -9), 1.95),
    ("NAGASAKI", 129.87, 32.75, (-9, 14), 2.2),
]
REGIONS = [  # text, lon, lat, size, visible window (t0, t1)
    ("SEA OF JAPAN", 134.6, 39.6, 15, (1.6, 8.5)),
    ("PACIFIC OCEAN", 141.6, 32.2, 15, (1.6, 8.5)),
    ("HOKKAIDO", 142.9, 43.35, 12, (2.0, 7.0)),
    ("HONSHU", 138.0, 36.45, 12, (2.0, 7.5)),
    ("SHIKOKU", 133.45, 33.62, 12, (2.0, 9.5)),
    ("KYUSHU", 131.15, 32.35, 12, (2.0, 9.5)),
    ("KOREAN PENINSULA", 127.6, 38.6, 11, (2.0, 7.0)),
    ("SETO INLAND SEA", 133.35, 34.05, 12, (8.5, 12.5)),
    ("HIROSHIMA BAY", 132.36, 34.215, 12, (12.0, 30)),
]

T = Transformer.from_crs("EPSG:4326",
                         "+proj=lcc +lat_1=30 +lat_2=40 +lat_0=35 +lon_0=135 +datum=WGS84 +units=m",
                         always_xy=True)


def P(lon, lat):
    return T.transform(lon, lat)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):  # cubic in-out
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def win(t, t0, t1, fade=0.6):
    """Opacity for an element visible between t0 and t1 with fades."""
    return clamp((t - t0) / fade) * clamp((t1 - t) / fade)


# ---------------------------------------------------------------- data: decode TopoJSON land, keep rings near Japan
def load_land():
    topo = json.loads((A / "land-10m.json").read_text())
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        out = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a[1:] if out else a)
        return out

    geoms = topo["objects"]["land"]["geometries"]
    rings = []
    for g in geoms:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        for poly in polys:
            for r in poly:
                pts = ring(r)
                lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
                if max(lons) < 100 or min(lons) > 170 or max(lats) < 10 or min(lats) > 62:
                    continue
                if min(lons) < 0:  # antimeridian pieces
                    continue
                xs, ys = T.transform(lons, lats)
                rings.append(np.column_stack([xs, ys]))
    return rings


def build_path(rings):
    path = skia.Path()
    path.setFillType(skia.PathFillType.kEvenOdd)
    for r in rings:
        path.moveTo(*r[0])
        for x, y in r[1:]:
            path.lineTo(x, y)
        path.close()
    return path


# ---------------------------------------------------------------- text helpers
TF = {k: skia.Typeface.MakeFromFile(str(A / f)) for k, f in {
    "reg": "IBMPlexSans_400Regular.ttf", "med": "IBMPlexSans_500Medium.ttf",
    "semi": "IBMPlexSans_600SemiBold.ttf", "mono": "IBMPlexMono_400Regular.ttf",
    "monom": "IBMPlexMono_500Medium.ttf"}.items()}


def rgba(c, a=1.0):
    return skia.Color(c[0], c[1], c[2], int(255 * clamp(a)))


def text(canvas, s, x, y, size, face="med", color=C["text"], alpha=1.0, track=0.0, align="left", k=1.0):
    font = skia.Font(TF[face], size * k)
    font.setSubpixel(True)
    font.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    paint = skia.Paint(AntiAlias=True, Color=rgba(color, alpha))
    widths = [font.measureText(ch) for ch in s]
    total = sum(widths) + track * size * k * (len(s) - 1)
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    for ch, w in zip(s, widths):
        canvas.drawString(ch, x, y, font, paint)
        x += w + track * size * k
    return total


# ---------------------------------------------------------------- camera
W0, C0 = 3_050_000.0, P(137.0, 37.7)        # full Japan, metres across the frame
W1 = 150_000.0                               # final city-region view
HX, HY = P(*HIRO)
TARGET_SCREEN = (0.60, 0.44)                 # where Hiroshima sits in the final frame (fraction of W, H)


def camera(t, Wpx, Hpx):
    """Return (metres_per_px, centre_x, centre_y)."""
    z = ease((t - 4.0) / 11.5)
    intro = 1.0 + 0.04 * (1 - eout(t / 2.5))          # slight settle on fade-in
    tail = 1.0 - 0.035 * clamp((t - 15.5) / 6.5)       # continued slow push at the end
    w = math.exp(math.log(W0) + (math.log(W1) - math.log(W0)) * z) * intro * tail
    m = w / Wpx
    # final centre puts Hiroshima at TARGET_SCREEN
    c1x = HX - (TARGET_SCREEN[0] - 0.5) * Wpx * (W1 / Wpx)
    c1y = HY + (TARGET_SCREEN[1] - 0.5) * Hpx * (W1 / Wpx)
    f = (w / intro / tail - W1) / (W0 - W1)              # 1 at start, 0 at end
    cx = c1x + (C0[0] - c1x) * f
    cy = c1y + (C0[1] - c1y) * f
    return m, cx, cy


def nice_scale(m, Wpx):
    target = 0.16 * Wpx * m / 1000.0  # km
    p = 10 ** math.floor(math.log10(target))
    for n in (1, 2, 5, 10):
        if n * p >= target * 0.7:
            return n * p
    return 10 * p


def dms(v, pos, neg):
    sec = round(abs(v) * 3600); d, r = divmod(sec, 3600); mnt, sc = divmod(r, 60)
    return f"{d}°{mnt:02d}′{sc:02d}″ {pos if v >= 0 else neg}"


# ---------------------------------------------------------------- frame
def make_grain(Wpx, Hpx, n=6, seed=7):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = rng.normal(0, 1, (Hpx // 2, Wpx // 2)).clip(-2.5, 2.5)
        g = ((g + 2.5) / 5 * 255).astype(np.uint8)
        img = np.dstack([g, g, g, np.full_like(g, 255)])
        out.append(skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType))
    return out


def draw(canvas, t, Wpx, Hpx, land, grain):
    k = Hpx / 1080.0
    m, cx, cy = camera(t, Wpx, Hpx)
    fade_in = eout(t / 1.4)

    def S(x, y):  # projected metres -> screen px
        return (Wpx / 2 + (x - cx) / m, Hpx / 2 - (y - cy) / m)

    def L(lon, lat):
        return S(*P(lon, lat))

    # sea with soft radial depth
    canvas.clear(rgba(C["sea"]))
    sea = skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (Wpx * 0.55, Hpx * 0.42), Wpx * 0.75, [rgba(C["sea2"]), rgba(C["sea"])]))
    canvas.drawRect(skia.Rect(0, 0, Wpx, Hpx), sea)

    # graticule (every 5° wide, every 1° / 0.25° when zoomed)
    step = 5 if m > 900 else (1 if m > 120 else 0.25)
    gp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.0 * k,
                    Color=rgba(C["grat"], 0.07 * fade_in))
    for lon in np.arange(100, 171, step):
        pts = [L(lon, la) for la in np.linspace(15, 60, 90)]
        pth = skia.Path(); pth.moveTo(*pts[0]); [pth.lineTo(*p) for p in pts[1:]]
        canvas.drawPath(pth, gp)
    for lat in np.arange(15, 61, step):
        pts = [L(lo, lat) for lo in np.linspace(100, 170, 140)]
        pth = skia.Path(); pth.moveTo(*pts[0]); [pth.lineTo(*p) for p in pts[1:]]
        canvas.drawPath(pth, gp)

    # land: transform once per frame
    mat = skia.Matrix()
    mat.setAll(1 / m, 0, Wpx / 2 - cx / m, 0, -1 / m, Hpx / 2 + cy / m, 0, 0, 1)
    lp = skia.Path(land); lp.transform(mat)
    canvas.drawPath(lp, skia.Paint(AntiAlias=True, Color=rgba(C["land"], fade_in)))
    # soft inner relief: offset lighter copy for a 2.5D edge
    hi = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.0 * k,
                    Color=rgba(C["land_hi"], 0.9 * fade_in))
    canvas.drawPath(lp, hi)
    canvas.drawPath(lp, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                   StrokeWidth=1.15 * k, Color=rgba(C["coast"], 0.85 * fade_in)))

    # region labels
    for name, lo, la, size, (t0, t1) in REGIONS:
        a = win(t, t0, t1, 0.8) * 0.55
        if a > 0.01:
            x, y = L(lo, la)
            text(canvas, name, x, y, size, "reg", C["muted"], a, track=0.32, align="center", k=k)

    # city markers
    zoom_out = 1 - clamp((t - 6.5) / 2.5)
    for name, lo, la, (dx, dy), t0 in CITIES:
        a = clamp((t - t0) / 0.5) * zoom_out
        if a <= 0.01:
            continue
        x, y = L(lo, la)
        canvas.drawCircle(x, y, 3.4 * k, skia.Paint(AntiAlias=True, Color=rgba(C["text"], a)))
        text(canvas, name, x + dx * k, y + dy * k + 4 * k, 13, "med", C["text"], a * 0.9, track=0.18,
             align="right" if dx < 0 else "left", k=k)

    # Hiroshima: present from the start as a brass city point, becomes the precise marker
    hx, hy = L(*HIRO)
    a_city = clamp((t - 1.0) / 0.5)
    drop = eout((t - 15.4) / 0.9)
    r_dot = (4.2 + 1.4 * drop) * k
    canvas.drawCircle(hx, hy, r_dot, skia.Paint(AntiAlias=True, Color=rgba(C["brass"], a_city)))
    a_lab = a_city * (1 - clamp((t - 14.4) / 0.8))
    if a_lab > 0.01:
        text(canvas, "HIROSHIMA", hx, hy - 14 * k, 13.5 + 3.5 * ease((t - 4) / 10), "semi", C["brass"],
             a_lab, track=0.18, align="center", k=k)
    # precise marker: crosshair ring + ticks
    if t > 15.2:
        a = clamp((t - 15.2) / 0.6)
        R = (26 - 10 * drop) * k + 16 * k
        rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.6 * k,
                        Color=rgba(C["brass"], a))
        canvas.drawCircle(hx, hy, R * 0.5, rp)
        for ang in range(0, 360, 90):
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            canvas.drawLine(hx + ca * R * 0.62, hy + sa * R * 0.62, hx + ca * R * 0.95, hy + sa * R * 0.95, rp)
        # single ring pulse
        pr = clamp((t - 16.0) / 1.6)
        if 0 < pr < 1:
            canvas.drawCircle(hx, hy, (18 + 70 * eout(pr)) * k,
                              skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                         StrokeWidth=1.3 * k, Color=rgba(C["brass"], 0.8 * (1 - pr))))
        # small marker label
        a2 = clamp((t - 16.6) / 0.7)
        text(canvas, "HYPOCENTRE · NEAR AIOI BRIDGE (AIMING POINT)", hx + 44 * k, hy + 4 * k, 11.5, "mono",
             C["text"], a2 * 0.85, track=0.06, k=k)

    # ---------------- overlays: vignette, title block, scale bar, north arrow, legend, card, tags
    vg = skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (Wpx / 2, Hpx / 2), Wpx * 0.72, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 120)], [0.55, 1.0]))
    canvas.drawRect(skia.Rect(0, 0, Wpx, Hpx), vg)

    M = 64 * k  # safe margin
    a_title = win(t, 0.8, 9.0, 0.9)
    if a_title > 0.01:
        text(canvas, "JAPAN", M, M + 40 * k, 40, "semi", C["text"], a_title, track=0.34, k=k)
        text(canvas, "WESTERN PACIFIC · AUGUST 1945", M, M + 66 * k, 13, "mono", C["muted"], a_title, track=0.12, k=k)

    # legend (bottom-left) before the card takes over
    a_leg = win(t, 2.0, 10.0, 0.8)
    if a_leg > 0.01:
        y0 = Hpx - M - 34 * k
        canvas.drawRoundRect(skia.Rect(M - 16 * k, y0 - 24 * k, M + 300 * k, y0 + 38 * k), 2 * k, 2 * k,
                             skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(110 * a_leg))))
        canvas.drawCircle(M + 5 * k, y0 - 4 * k, 3.4 * k, skia.Paint(AntiAlias=True, Color=rgba(C["text"], a_leg)))
        text(canvas, "CITY", M + 22 * k, y0, 12, "med", C["muted"], a_leg, track=0.16, k=k)
        canvas.drawCircle(M + 5 * k, y0 + 20 * k, 4.2 * k, skia.Paint(AntiAlias=True, Color=rgba(C["brass"], a_leg)))
        text(canvas, "TARGET CITY, 6 AUGUST 1945", M + 22 * k, y0 + 24 * k, 12, "med", C["muted"], a_leg, track=0.16, k=k)

    # scale bar (bottom-right), resizes live
    a_sc = clamp((t - 1.8) / 0.8)
    km = nice_scale(m, Wpx)
    blen = km * 1000 / m
    bx1 = Wpx - M; bx0 = bx1 - blen; by = Hpx - M - 6 * k
    sp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.5 * k, Color=rgba(C["text"], a_sc * 0.9))
    canvas.drawLine(bx0, by, bx1, by, sp)
    for x in (bx0, (bx0 + bx1) / 2, bx1):
        canvas.drawLine(x, by - 6 * k, x, by + (0 if x != (bx0 + bx1) / 2 else -2 * k), sp)
    text(canvas, f"{km:g} km", bx1, by - 12 * k, 12, "mono", C["text"], a_sc * 0.9, align="right", k=k)

    # north arrow, rotated by LCC meridian convergence at the view centre
    lon_c = T.transform(cx, cy, direction="INVERSE")[0]
    conv = math.radians((lon_c - 135.0) * math.sin(math.radians(35.0)))
    nx, ny = Wpx - M - 8 * k, M + 34 * k
    canvas.save(); canvas.translate(nx, ny); canvas.rotate(math.degrees(-conv))
    ap = skia.Path(); ap.moveTo(0, -22 * k); ap.lineTo(7 * k, 8 * k); ap.lineTo(0, 3 * k); ap.lineTo(-7 * k, 8 * k); ap.close()
    canvas.drawPath(ap, skia.Paint(AntiAlias=True, Color=rgba(C["text"], a_sc * 0.9)))
    text(canvas, "N", 0, 26 * k, 12, "semi", C["text"], a_sc * 0.9, align="center", k=k)
    canvas.restore()

    # source tag (top-right, under the arrow)
    text(canvas, "MAP · NATURAL EARTH 1:10M · LAMBERT CONFORMAL CONIC", Wpx - M, M + 84 * k, 10.5, "mono",
         C["muted"], a_sc * 0.75, track=0.08, align="right", k=k)
    text(canvas, "PRESENT-DAY COASTLINES; 1945 BOUNDARIES NOT SHOWN", Wpx - M, M + 100 * k, 10.5, "mono",
         C["muted"], a_sc * 0.6, track=0.08, align="right", k=k)

    # location card (lower-left), assembles line by line
    if t > 16.4:
        x0, y0 = M, Hpx - M - 176 * k
        a_pl = clamp((t - 16.4) / 0.8)
        plate = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(102 * a_pl)))
        canvas.drawRoundRect(skia.Rect(x0 - 22 * k, y0 - 54 * k, x0 + 520 * k, y0 + 168 * k), 2 * k, 2 * k, plate)
        rule = eout((t - 16.6) / 0.9)
        canvas.drawLine(x0, y0 - 30 * k, x0 + 440 * k * rule, y0 - 30 * k,
                        skia.Paint(AntiAlias=True, StrokeWidth=1.4 * k, Color=rgba(C["brass"], a_pl)))
        lines = [("HIROSHIMA, JAPAN", 38, "semi", 0.30, C["text"], 16.8),
                 ("6 AUGUST 1945", 26, "med", 0.22, C["text"], 17.4),
                 ("8:15 AM LOCAL TIME", 26, "med", 0.22, C["brass"], 18.0)]
        yy = y0 + 10 * k
        for s, size, face, tr, col, t0 in lines:
            a = eout((t - t0) / 0.7)
            text(canvas, s, x0, yy + (1 - a) * 14 * k, size, face, col, a, track=tr, k=k)
            yy += (size + 16) * k
        a = eout((t - 18.7) / 0.7)
        text(canvas, f"{dms(HIRO[1], 'N', 'S')}  ·  {dms(HIRO[0], 'E', 'W')}", x0, yy + 2 * k, 13, "mono",
             C["muted"], a, track=0.1, k=k)

    # tag
    text(canvas, "MOTION GRAPHICS", M, M - 26 * k, 10.5, "mono", C["muted"], 0.0 if t < 0.5 else 0.6, track=0.14, k=k)

    # film grain
    gi = grain[int(t * 24) % len(grain)]
    gp = skia.Paint(Alphaf=0.05, BlendMode=skia.BlendMode.kOverlay)
    canvas.drawImageRect(gi, skia.Rect(0, 0, Wpx, Hpx), skia.SamplingOptions(skia.FilterMode.kLinear), gp)
    # global fade from black
    if t < 0.8:
        canvas.drawRect(skia.Rect(0, 0, Wpx, Hpx), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * (1 - t / 0.8)))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", default=str(HERE.parent / "renders" / "098-100_hiroshima_map.mp4"))
    ap.add_argument("--stills", default="")
    a = ap.parse_args()
    Wpx = a.width; Hpx = Wpx * 9 // 16
    land = build_path(load_land())
    grain = make_grain(Wpx, Hpx)
    surf = skia.Surface(Wpx, Hpx)
    canvas = surf.getCanvas()
    if a.stills:
        for s in a.stills.split(","):
            draw(canvas, float(s), Wpx, Hpx, land, grain)
            p = HERE.parent / "renders" / f"still_{float(s):05.1f}.png"
            surf.makeImageSnapshot().save(str(p), skia.kPNG)
            print(p)
        return
    n = int(DUR * a.fps)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                           "-s", f"{Wpx}x{Hpx}", "-r", str(a.fps), "-i", "-", "-c:v", "libx264",
                           "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                           a.out], stdin=subprocess.PIPE)
    for i in range(n):
        draw(canvas, i / a.fps, Wpx, Hpx, land, grain)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close(); ff.wait()
    print(a.out, n, "frames")


if __name__ == "__main__":
    main()
