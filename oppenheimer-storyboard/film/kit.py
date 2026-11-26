"""Reusable shot templates: palettes, title/callout/timeline graphics, flat maps, documents
(newspapers, letters, journal pages), archival photo moves and scientific diagrams."""
import json, math
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia
from pyproj import Transformer

from engine import (ASSETS, clamp, lerp, ease, eout, ein, smooth, win, col, mix, text, P, poly, Globe, face)

ARCHIVE = Path(__file__).parent / "archive"

# ------------------------------------------------------------------ palettes (colour grade by era)
PAL = {
    "title": dict(bg=(13, 17, 22), bg2=(24, 31, 40), fg=(236, 232, 222), accent=(201, 164, 99), muted=(140, 150, 160),
                  land=(44, 52, 60), sea=(14, 20, 28), coast=(150, 166, 178)),
    "warm": dict(bg=(40, 34, 28), bg2=(62, 52, 42), fg=(240, 228, 206), accent=(196, 146, 78), muted=(170, 152, 128),
                 land=(196, 178, 146), sea=(150, 160, 152), coast=(96, 80, 62), paper=(222, 208, 180), ink=(70, 54, 40)),
    "war": dict(bg=(20, 24, 25), bg2=(34, 40, 40), fg=(230, 228, 220), accent=(178, 92, 68), muted=(146, 152, 150),
                land=(52, 58, 56), sea=(18, 25, 28), coast=(130, 140, 138), allied=(86, 116, 138), neutral=(84, 86, 84)),
    "cold": dict(bg=(16, 21, 28), bg2=(28, 36, 46), fg=(226, 230, 234), accent=(201, 164, 99), muted=(140, 152, 164),
                 land=(46, 54, 62), sea=(14, 20, 28), coast=(146, 162, 176)),
    "desert": dict(bg=(26, 20, 28), bg2=(48, 34, 40), fg=(242, 232, 216), accent=(226, 128, 62), muted=(176, 156, 144),
                   land=(96, 78, 64), sea=(30, 30, 44), coast=(170, 140, 116)),
    "mono": dict(bg=(16, 18, 20), bg2=(30, 33, 36), fg=(230, 230, 226), accent=(201, 164, 99), muted=(150, 152, 154),
                 land=(48, 52, 56), sea=(16, 20, 24), coast=(150, 160, 168)),
    "coldwar": dict(bg=(13, 19, 27), bg2=(26, 36, 48), fg=(220, 228, 236), accent=(214, 176, 112), muted=(130, 146, 162),
                    land=(40, 50, 62), sea=(12, 18, 26), coast=(120, 142, 164)),
    "dark": dict(bg=(10, 12, 15), bg2=(22, 26, 32), fg=(232, 228, 220), accent=(201, 164, 99), muted=(128, 134, 142),
                 land=(36, 42, 48), sea=(10, 14, 18), coast=(120, 132, 144)),
}
SCENE_PAL = {1: "title", 2: "warm", 3: "warm", 4: "warm", 5: "war", 6: "cold", 7: "cold", 8: "desert",
             9: "mono", 10: "mono", 11: "coldwar", 12: "dark"}


def K(H):
    return H / 1080


def bg_fill(c, W, H, pal, glow=(0.55, 0.45)):
    c.clear(col(pal["bg"]))
    p = skia.Paint(Shader=skia.GradientShader.MakeRadial((W * glow[0], H * glow[1]), W * 0.8,
                                                         [col(pal["bg2"]), col(pal["bg"])]))
    c.drawRect(skia.Rect(0, 0, W, H), p)


def small_tag(c, W, H, s, pal, a=0.7):
    k = K(H)
    text(c, s, W - 64 * k, 52 * k, 11 * k, "mono", pal["muted"], a, track=0.14, align="right")


def wrap(s, fc, size, maxw, track=0.0):
    font = skia.Font(face(fc), size)
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.measureText(trial) + track * size * len(trial) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ text graphics
def equations_backdrop(c, W, H, t, pal, seed=1, a=0.07):
    rng = np.random.default_rng(seed)
    eqs = ["iħ ∂ψ/∂t = Ĥψ", "E = mc²", "H = p²/2m + V", "[x, p] = iħ", "λ = h/p", "∇²φ = 4πGρ", "ΔE·Δt ≥ ħ/2",
           "n + U-235 → 2 fragments + 2.5 n", "k = η f p ε", "ψ(x,t)"]
    k = K(H)
    for i in range(18):
        layer = i % 3
        x = (rng.uniform(-0.1, 1.1) * W - t * (6 + layer * 8) * k) % (W * 1.2) - W * 0.1
        y = rng.uniform(0.05, 0.95) * H
        text(c, eqs[i % len(eqs)], x, y, (22 + layer * 12) * k, "reg", pal["fg"], a * (0.6 + layer * 0.3))


def title_card(c, t, d, W, H, pal, main, sub=None, tag=None, main_size=96, sub_size=24):
    k = K(H)
    bg_fill(c, W, H, pal)
    equations_backdrop(c, W, H, t, pal)
    n = len(main)
    font = skia.Font(face("semi"), main_size * k)
    track = 0.32
    total = sum(font.measureText(ch) for ch in main) + track * main_size * k * (n - 1)
    x = W / 2 - total / 2
    push = 1 + 0.03 * t / d
    c.save(); c.translate(W / 2, H / 2); c.scale(push, push); c.translate(-W / 2, -H / 2)
    for i, ch in enumerate(main):
        a = eout((t - 0.3 - i * 0.08) / 0.7)
        text(c, ch, x, H * 0.5 + (1 - a) * 10 * k, main_size * k, "semi", pal["fg"], a)
        x += font.measureText(ch) + track * main_size * k
    if sub:
        a = eout((t - 1.2) / 0.9)
        for j, line in enumerate(sub if isinstance(sub, list) else [sub]):
            text(c, line, W / 2, H * 0.5 + (70 + j * 36) * k, sub_size * k, "med", pal["muted"], a, track=0.18, align="center")
    c.restore()
    if tag:
        small_tag(c, W, H, tag, pal)


def callout(c, t, d, W, H, pal, lines, plate=True, icon=None, x=None, y=None, maxw=900, bg=True, title=None):
    """lines: list of strings; first can be emphasized via title."""
    k = K(H)
    if bg:
        bg_fill(c, W, H, pal)
    x = (x if x is not None else 0.14 * W)
    y = (y if y is not None else 0.42 * H)
    if icon:
        icon(c, t, x - 0.0 * W, y, k)
        x += 300 * k
    a0 = eout((t - 0.2) / 0.8)
    c.drawLine(x, y - 40 * k, x + 520 * k * a0, y - 40 * k, P(c=col(pal["accent"], a0), stroke=1.6 * k))
    yy = y
    if title:
        a = eout((t - 0.3) / 0.7)
        text(c, title, x, yy + (1 - a) * 10 * k, 40 * k, "semi", pal["fg"], a, track=0.12)
        yy += 64 * k
    for i, s in enumerate(lines):
        for line in wrap(s, "reg", 30 * k, maxw * k):
            a = eout((t - 0.5 - i * 0.35) / 0.7)
            text(c, line, x, yy + (1 - a) * 10 * k, 30 * k, "reg", pal["fg"], a * 0.95)
            yy += 44 * k
        yy += 14 * k


TL_YEARS = (1900, 1970)


def timeline(c, t, d, W, H, pal, events, focus=None, ticks=(1904, 1927, 1939, 1942, 1943, 1945, 1949, 1954, 1963, 1967),
             reveal_all=False, bg=True, ghost=None):
    """events: list of (year_float, label). The camera trucks toward the focused years."""
    k = K(H)
    if bg:
        bg_fill(c, W, H, pal)
    if ghost:
        ghost(c, t)
    y = H * 0.56
    span = W * 2.2 if focus else W * 0.82
    fx = (focus[0] + focus[1]) / 2 if focus else sum(TL_YEARS) / 2
    pan = (t / d - 0.5) * 0.06 * W

    def X(year):
        return W / 2 + (year - fx) / (TL_YEARS[1] - TL_YEARS[0]) * span - pan

    draw_to = lerp(TL_YEARS[0], TL_YEARS[1], eout(t / 1.2)) if not focus else TL_YEARS[1]
    c.drawLine(X(TL_YEARS[0]), y, X(draw_to), y, P(c=col(pal["fg"], 0.6), stroke=1.6 * k))
    for yr in ticks:
        if yr <= draw_to:
            c.drawLine(X(yr), y - 8 * k, X(yr), y + 8 * k, P(c=col(pal["fg"], 0.6), stroke=1.4 * k))
            text(c, str(yr), X(yr), y + 34 * k, 16 * k, "mono", pal["muted"], 0.9, align="center")
    for i, (yr, label) in enumerate(events):
        a = eout((t - 0.6 - i * 0.55) / 0.7) if not reveal_all else eout((t - 0.2 - i * 0.12) / 0.5)
        if a <= 0:
            continue
        xx = X(yr)
        up = i % 2 == 0
        ly = y - (70 if up else -80) * k - (i % 4 // 2) * 46 * k * (1 if up else -1)
        c.drawLine(xx, y, xx, lerp(y, ly + (14 if up else -26) * k, a), P(c=col(pal["accent"], a), stroke=1.2 * k))
        c.drawCircle(xx, y, 6 * k, P(c=col(pal["accent"], a)))
        lines = wrap(label, "med", 19 * k, 330 * k)
        for j, ln in enumerate(lines):
            text(c, ln, xx, ly + j * 25 * k + (1 - a) * 8 * k, 19 * k, "med", pal["fg"], a, align="center")


def location_card(c, W, H, lines, a, pal, x=None, y=None, plate=True):
    """lines: [(text, size, face, colour_key)] lower-left documentary card."""
    if a <= 0.01:
        return
    k = K(H)
    x = 64 * k if x is None else x
    total = sum(s for _, s, _, _ in lines) * 1.5 * k
    y = (H - 70 * k - total) if y is None else y
    if plate:
        c.drawRect(skia.Rect(x - 24 * k, y - 46 * k, x + 620 * k, y + total + 26 * k), P(c=col((0, 0, 0), 0.42 * a)))
    c.drawLine(x, y - 22 * k, x + 420 * k * eout(a), y - 22 * k, P(c=col(pal["accent"], a), stroke=1.4 * k))
    yy, prev = y, 0
    for i, (s, size, fc, ck) in enumerate(lines):
        aa = clamp(a * 1.5 - i * 0.25)
        yy += (size * 1.1 + prev * 0.4) * k
        prev = size
        text(c, s, x, yy + (1 - aa) * 10 * k, size * k, fc, pal.get(ck, pal["fg"]), aa, track=0.2)


# ------------------------------------------------------------------ flat maps
@lru_cache(maxsize=None)
def _topo_rings(name):
    topo = json.loads((ASSETS / name).read_text())
    sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    out = {}
    obj = list(topo["objects"].values())[0]
    for gi, g in enumerate(obj["geometries"]):
        if g.get("type") is None:
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        rings = []
        for pl in polys:
            for r in pl:
                pts = []
                for i in r:
                    a = arcs[i] if i >= 0 else arcs[~i][::-1]
                    pts.extend(a[1:] if pts else a)
                rings.append(np.array(pts))
        out[str(g.get("id", gi))] = rings
    return out


@lru_cache(maxsize=None)
def _hist_rings():
    d = json.loads((ASSETS / "world_1938.geojson").read_text())
    out = {}
    for f in d["features"]:
        n = f["properties"].get("NAME")
        g = f["geometry"]
        if not n or not g:
            continue
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        out.setdefault(n, []).extend(np.array(r) for pl in polys for r in pl)
    return out


class MapView:
    """Flat map in a given projection. Geometry is projected once; each frame applies a 2D view matrix."""
    def __init__(self, proj, bbox=(-180, -60, 180, 85), land="land-50m.json"):
        self.T = Transformer.from_crs("EPSG:4326", proj, always_xy=True)
        self.bbox = bbox
        self.land = self._path(_topo_rings(land)["0"] if "0" in _topo_rings(land) else
                               [r for rs in _topo_rings(land).values() for r in rs])
        self.cache = {}

    def _ok(self, r):
        b = self.bbox
        return not (r[:, 0].max() < b[0] or r[:, 0].min() > b[2] or r[:, 1].max() < b[1] or r[:, 1].min() > b[3]) \
            and not (r[:, 0].min() < -170 and r[:, 0].max() > 170)

    def _path(self, rings):
        path = skia.Path(); path.setFillType(skia.PathFillType.kEvenOdd)
        for r in rings:
            if len(r) < 3 or not self._ok(r):
                continue
            xs, ys = self.T.transform(r[:, 0], r[:, 1])
            if not np.all(np.isfinite(xs)):
                continue
            path.moveTo(xs[0], -ys[0])
            for x, y in zip(xs[1:], ys[1:]):
                path.lineTo(x, -y)
            path.close()
        return path

    def country(self, key):
        """key: ISO numeric string from countries-50m, or ('hist', NAME) from the 1938 basemap."""
        if key not in self.cache:
            if isinstance(key, tuple):
                rings = _hist_rings().get(key[1], [])
            else:
                rings = _topo_rings("countries-50m.json").get(key, [])
            self.cache[key] = self._path(rings)
        return self.cache[key]

    def xy(self, lon, lat):
        x, y = self.T.transform(lon, lat)
        return x, -y

    def view(self, W, H, center, width_km):
        cx, cy = self.xy(*center)
        m = width_km * 1000 / W
        mat = skia.Matrix()
        mat.setAll(1 / m, 0, W / 2 - cx / m, 0, 1 / m, H / 2 - cy / m, 0, 0, 1)
        return mat, m

    def S(self, mat, lon, lat):
        x, y = self.xy(lon, lat)
        return mat.mapXY(x, y)


@lru_cache(maxsize=None)
def hatch_shader(r, g, b, a, spacing=14, width=5):
    n = spacing * 4
    s = skia.Surface(n, n)
    cv = s.getCanvas(); cv.clear(skia.Color(0, 0, 0, 0))
    p = P(c=skia.Color(r, g, b, a), stroke=width)
    for i in range(-n, 2 * n, spacing):
        cv.drawLine(i, n, i + n, 0, p)
    return s.makeImageSnapshot().makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat)


def draw_map(c, W, H, mv, center, width_km, pal, fills=(), markers=(), labels=(), routes=(), rings=(), t=0.0,
             grat=10, land_a=1.0, coast_w=1.1):
    """fills: [(key, colour, alpha, hatched)], markers: [(lon, lat, name, a, style, (dx,dy))],
    labels: [(lon, lat, text, size, a)], routes: [(list of lonlat, progress, colour)], rings: [(lon, lat, km, a)]."""
    k = K(H)
    mat, m = mv.view(W, H, center, width_km)
    c.clear(col(pal["sea"]))
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (W * 0.55, H * 0.45), W * 0.8, [col(mix(pal["sea"], (255, 255, 255), 0.05)), col(pal["sea"])])))
    # graticule
    gp = P(c=col((255, 255, 255), 0.06), stroke=k)
    b = mv.bbox
    for lon in np.arange(math.floor(b[0] / grat) * grat, b[2] + 1, grat):
        pts = [mv.S(mat, lon, la) for la in np.linspace(max(b[1], -80), min(b[3], 85), 60)]
        c.drawPath(poly([(p.x(), p.y()) for p in pts], close=False), gp)
    for lat in np.arange(math.floor(b[1] / grat) * grat, b[3] + 1, grat):
        pts = [mv.S(mat, lo, lat) for lo in np.linspace(b[0], b[2], 120)]
        c.drawPath(poly([(p.x(), p.y()) for p in pts], close=False), gp)
    lp = skia.Path(mv.land); lp.transform(mat)
    c.drawPath(lp, P(c=col(pal["land"], land_a)))
    for key, colr, a, hatched in fills:
        if a <= 0.01:
            continue
        fp = skia.Path(mv.country(key)); fp.transform(mat)
        c.drawPath(fp, P(c=col(colr, a * (0.55 if hatched else 0.9))))
        if hatched:
            hp = skia.Paint(AntiAlias=True, Shader=hatch_shader(*[int(v) for v in mix(colr, (255, 255, 255), 0.25)],
                                                                 int(200 * a), int(14 * k) or 1, max(1, int(4 * k))))
            c.drawPath(fp, hp)
        c.drawPath(fp, P(c=col(mix(colr, (255, 255, 255), 0.35), a * 0.8), stroke=1.0 * k))
    c.drawPath(lp, P(c=col(pal["coast"], 0.8 * land_a), stroke=coast_w * k))
    for pts, prog, colr in routes:
        if prog <= 0:
            continue
        dense = []
        for (a1, b1), (a2, b2) in zip(pts[:-1], pts[1:]):
            for u in np.linspace(0, 1, 30, endpoint=False):
                dense.append(mv.S(mat, lerp(a1, a2, u), lerp(b1, b2, u)))
        dense.append(mv.S(mat, *pts[-1]))
        path = poly([(p.x(), p.y()) for p in dense], close=False)
        meas = skia.PathMeasure(path, False)
        L = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L * clamp(prog), seg, True)
        rp = P(c=col(colr), stroke=2.0 * k)
        rp.setPathEffect(skia.DashPathEffect.Make([10 * k, 7 * k], 0))
        c.drawPath(seg, rp)
        pos = meas.getPosTan(L * clamp(prog))
        if pos and prog < 1:
            c.drawCircle(pos[0].x(), pos[0].y(), 4.5 * k, P(c=col(colr)))
    for lon, lat, km, a in rings:
        p = mv.S(mat, lon, lat)
        c.drawCircle(p.x(), p.y(), km * 1000 / m, P(c=col(pal["accent"], a * 0.7), stroke=1.3 * k))
    for lon, lat, txt, size, a in labels:
        if a > 0.01:
            p = mv.S(mat, lon, lat)
            text(c, txt, p.x(), p.y(), size * k, "reg", pal["muted"], a * 0.75, track=0.3, align="center")
    for mk in markers:
        lon, lat, name, a = mk[:4]
        style = mk[4] if len(mk) > 4 else "dot"
        off = mk[5] if len(mk) > 5 else (12, -10)
        if a <= 0.01:
            continue
        p = mv.S(mat, lon, lat)
        colr = pal["accent"] if style in ("key", "target") else pal["fg"]
        r = (6 if style != "dot" else 4) * k
        c.drawCircle(p.x(), p.y(), r, P(c=col(colr, a)))
        if style in ("key", "target"):
            c.drawCircle(p.x(), p.y(), r * 2.4, P(c=col(colr, a), stroke=1.4 * k))
        if name:
            text(c, name, p.x() + off[0] * k, p.y() + off[1] * k, (15 if style != "dot" else 13) * k,
                 "semi" if style != "dot" else "med", colr, a, track=0.16, align="right" if off[0] < 0 else "left")
    return mat, m


def scale_bar(c, W, H, m, pal, a=1.0):
    k = K(H)
    target = 0.15 * W * m / 1000.0
    p10 = 10 ** math.floor(math.log10(target))
    km = next(n * p10 for n in (1, 2, 5, 10) if n * p10 >= target * 0.7)
    L = km * 1000 / m
    x1, y = W - 64 * k, H - 70 * k
    sp = P(c=col(pal["fg"], 0.85 * a), stroke=1.5 * k)
    c.drawLine(x1 - L, y, x1, y, sp)
    for x in (x1 - L, x1):
        c.drawLine(x, y - 6 * k, x, y, sp)
    text(c, f"{km:g} km", x1, y - 12 * k, 12 * k, "mono", pal["fg"], 0.85 * a, align="right")


def legend(c, W, H, items, pal, a, x=None, y=None):
    """items: [(colour, label, kind)] kind in fill/hatch/dot/key/line"""
    if a <= 0.01:
        return
    k = K(H)
    x = 64 * k if x is None else x
    y = 120 * k if y is None else y
    c.drawRect(skia.Rect(x - 16 * k, y - 28 * k, x + 400 * k, y + len(items) * 30 * k + 4 * k), P(c=col((0, 0, 0), 0.4 * a)))
    for i, (colr, label, kind) in enumerate(items):
        yy = y + i * 30 * k
        if kind in ("fill", "hatch"):
            c.drawRect(skia.Rect(x, yy - 12 * k, x + 22 * k, yy + 2 * k), P(c=col(colr, a)))
        elif kind == "line":
            c.drawLine(x, yy - 5 * k, x + 22 * k, yy - 5 * k, P(c=col(colr, a), stroke=2 * k))
        else:
            c.drawCircle(x + 11 * k, yy - 5 * k, 5 * k, P(c=col(colr, a)))
        text(c, label, x + 36 * k, yy, 14 * k, "med", pal["fg"], a * 0.9, track=0.08)


def map_title(c, W, H, pal, title, sub, a):
    if a <= 0.01:
        return
    k = K(H)
    text(c, title, 64 * k, 84 * k, 30 * k, "semi", pal["fg"], a, track=0.24)
    if sub:
        text(c, sub, 64 * k, 112 * k, 13 * k, "mono", pal["muted"], a, track=0.12)


def date_counter(c, W, H, pal, s, a):
    k = K(H)
    text(c, s, W - 64 * k, 110 * k, 30 * k, "monom", pal["accent"], a, align="right", track=0.06)


# ------------------------------------------------------------------ documents (recreated) on a desk, in perspective
def desk(c, W, H, tone=(46, 36, 28)):
    c.clear(col(tone))
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (W * 0.5, H * 0.45), W * 0.7, [col(mix(tone, (255, 230, 200), 0.12)), col(mix(tone, (0, 0, 0), 0.45))])))


def paper_surface(w, h, tone=(226, 214, 190)):
    s = skia.Surface(w, h)
    cv = s.getCanvas()
    cv.clear(col(tone))
    rng = np.random.default_rng(w + h)
    for _ in range(140):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        cv.drawCircle(x, y, rng.uniform(2, 40), P(c=col(mix(tone, (120, 96, 60), 0.5), rng.uniform(0.01, 0.04)), blur=8))
    cv.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (w / 2, h / 2), max(w, h) * 0.75, [col((0, 0, 0), 0), col((90, 60, 30), 0.25)], [0.6, 1.0])))
    return s


def greek(cv, x, y, w, h, line=14, ink=(60, 50, 40), a=0.35, seed=0, gap=6):
    rng = np.random.default_rng(seed)
    yy = y
    while yy < y + h:
        ww = w * (rng.uniform(0.55, 1.0) if rng.uniform() < 0.15 else 1.0)
        cv.drawRect(skia.Rect(x, yy, x + ww, yy + line * 0.45), P(c=col(ink, a)))
        yy += line + gap * 0.1


def newspaper(w, h, masthead, date_line, headline_lines, decks=(), photo=False, tone=(224, 214, 192), seed=1):
    s = paper_surface(w, h, tone)
    cv = s.getCanvas()
    ink = (34, 30, 26)
    text(cv, masthead, w / 2, 120, 92, "frak", ink, 1.0, align="center")
    cv.drawLine(40, 150, w - 40, 150, P(c=col(ink), stroke=3))
    text(cv, date_line, w / 2, 178, 20, "news", ink, 0.9, align="center", track=0.1)
    cv.drawLine(40, 192, w - 40, 192, P(c=col(ink), stroke=1.5))
    y = 262
    for ln, size in headline_lines:
        text(cv, ln, w / 2, y, size, "newsb", ink, 1.0, align="center")
        y += size * 1.12
    for dk in decks:
        text(cv, dk, w / 2, y + 6, 26, "news", ink, 0.95, align="center")
        y += 36
    cv.drawLine(40, y + 6, w - 40, y + 6, P(c=col(ink), stroke=1.5))
    cols = 6
    cw = (w - 80) / cols
    for i in range(cols):
        x0 = 40 + i * cw + 8
        top = y + 24
        if photo and i in (2, 3):
            if i == 2:
                cv.drawRect(skia.Rect(x0, top, x0 + cw * 2 - 16, top + 280), P(c=col((70, 66, 60))))
            top += 300
        greek(cv, x0, top, cw - 16, h - top - 40, line=13, ink=ink, a=0.28, seed=seed + i)
        if i:
            cv.drawLine(40 + i * cw, y + 20, 40 + i * cw, h - 40, P(c=col(ink, 0.5), stroke=1))
    return s


def typed_letter(w, h, header, lines, sign=None, tone=(232, 226, 210), seed=2):
    s = paper_surface(w, h, tone)
    cv = s.getCanvas()
    ink = (40, 38, 46)
    y = 140
    for ln in header:
        text(cv, ln, 120, y, 24, "type", ink, 0.9); y += 34
    y += 50
    for para in lines:
        for ln in wrap(para, "type", 26, w - 240):
            text(cv, ln, 120, y, 26, "type", ink, 0.92); y += 40
        y += 26
    greek(cv, 120, y, w - 240, h * 0.78 - y, line=40, ink=ink, a=0.12, seed=seed, gap=0)
    if sign:
        yy = h * 0.82
        for ln in sign:
            text(cv, ln, w * 0.55, yy, 26, "type", ink, 0.92); yy += 40
    return s


def journal_page(w, h, journal, ref, title_lines, authors, affil, received=None, tone=(232, 228, 216), seed=3, cols=2):
    s = paper_surface(w, h, tone)
    cv = s.getCanvas()
    ink = (30, 30, 34)
    text(cv, journal, 90, 90, 22, "serif", ink, 0.85, track=0.12)
    text(cv, ref, w - 90, 90, 20, "serif", ink, 0.8, align="right")
    cv.drawLine(90, 108, w - 90, 108, P(c=col(ink), stroke=1.4))
    y = 200
    for ln in title_lines:
        text(cv, ln, w / 2, y, 40, "serifb", ink, 1.0, align="center"); y += 52
    y += 10
    text(cv, authors, w / 2, y, 26, "serif", ink, 0.95, align="center", track=0.08); y += 38
    text(cv, affil, w / 2, y, 20, "news", ink, 0.85, align="center"); y += 30
    if received:
        text(cv, received, w / 2, y, 20, "newsi", ink, 0.85, align="center"); y += 30
    y += 30
    cw = (w - 180 - 40) / cols
    for i in range(cols):
        greek(cv, 90 + i * (cw + 40), y, cw, h - y - 90, line=24, ink=ink, a=0.22, seed=seed + i)
    return s


def report_cover(w, h, top_lines, title_lines, bottom_lines, stamp=None, tone=(220, 210, 184)):
    s = paper_surface(w, h, tone)
    cv = s.getCanvas()
    ink = (34, 32, 30)
    y = 160
    for ln, size in top_lines:
        text(cv, ln, w / 2, y, size, "type", ink, 0.9, align="center"); y += size * 1.6
    y = h * 0.42
    for ln, size in title_lines:
        text(cv, ln, w / 2, y, size, "serifb", ink, 1.0, align="center"); y += size * 1.3
    y = h * 0.78
    for ln, size in bottom_lines:
        text(cv, ln, w / 2, y, size, "type", ink, 0.9, align="center"); y += size * 1.6
    if stamp:
        cv.save(); cv.translate(w * 0.7, h * 0.2); cv.rotate(-12)
        cv.drawRect(skia.Rect(-170, -40, 170, 30), P(c=col((150, 40, 36), 0.75), stroke=5))
        text(cv, stamp, 0, 8, 38, "type", (150, 40, 36), 0.8, align="center", track=0.1)
        cv.restore()
    return s


def document_shot(c, t, d, W, H, surf, pal, focus=(0.5, 0.3), tag="RECREATION", tone=(46, 36, 28),
                  tilt=6.0, push=(1.0, 1.35), highlight=None, caption_lines=None, under=None):
    """Lay a document surface on a desk with a slight perspective tilt; slow push toward `focus` (0..1 of page)."""
    k = K(H)
    desk(c, W, H, tone)
    img = surf.makeImageSnapshot()
    pw, ph = img.width(), img.height()
    a_in = eout(t / 0.9)
    z = lerp(push[0], push[1], ease(t / d))
    base_h = H * 0.92
    sc = base_h / ph * z
    # page centre moves so that focus point drifts toward screen centre
    fx, fy = focus
    cx = W / 2 - (fx - 0.5) * pw * sc * ease(t / d) * 0.9
    cy = H / 2 - (fy - 0.5) * ph * sc * ease(t / d) * 0.9 + (1 - a_in) * 60 * k
    # perspective quad (top edge slightly narrower)
    hw, hh = pw * sc / 2, ph * sc / 2
    tl = math.radians(tilt * (1 - 0.4 * ease(t / d)))
    inset = hw * 0.05 * math.sin(tl) * 4
    dst = [skia.Point(cx - hw + inset, cy - hh), skia.Point(cx + hw - inset, cy - hh),
           skia.Point(cx + hw, cy + hh), skia.Point(cx - hw, cy + hh)]
    src = [skia.Point(0, 0), skia.Point(pw, 0), skia.Point(pw, ph), skia.Point(0, ph)]
    mat = skia.Matrix()
    mat.setPolyToPoly(src, dst)
    if under:
        under(c, t)
    c.save()
    c.drawRect(skia.Rect(cx - hw + 12 * k, cy - hh + 18 * k, cx + hw + 18 * k, cy + hh + 24 * k),
               P(c=col((0, 0, 0), 0.45 * a_in), blur=18 * k))
    c.concat(mat)
    c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear),
                skia.Paint(Alphaf=a_in))
    if highlight:
        y0, y1 = highlight
        hx = lerp(-0.3, 1.3, clamp((t - 1.2) / 2.0)) * pw
        hp = skia.Paint(Shader=skia.GradientShader.MakeLinear([(hx - 200, 0), (hx + 200, 0)],
                        [col((255, 240, 200), 0), col((255, 240, 200), 0.35), col((255, 240, 200), 0)]))
        c.drawRect(skia.Rect(0, y0 * ph, pw, y1 * ph), hp)
    c.restore()
    if caption_lines:
        location_card(c, W, H, caption_lines, clamp((t - 1.0) / 0.8) * clamp((d - t) / 0.4), pal)
    if tag:
        small_tag(c, W, H, tag, pal)


# ------------------------------------------------------------------ archival photos
@lru_cache(maxsize=None)
def load_photo(name):
    p = ARCHIVE / name
    if not p.exists():
        return None
    data = skia.Data.MakeFromFileName(str(p))
    img = skia.Image.MakeFromEncoded(data)
    if img is None:
        return None
    arr = img.toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3].astype(np.float32)
    return arr


@lru_cache(maxsize=None)
def graded(name, mode, crop=None):
    arr = load_photo(name)
    if arr is None:
        return None
    if crop:
        h, w = arr.shape[:2]
        x0, y0, x1, y1 = crop
        arr = arr[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    g = arr.mean(axis=2, keepdims=True)
    if mode == "mono":
        out = np.repeat(g, 3, axis=2)
    elif mode == "sepia":
        out = np.concatenate([g * 1.07, g * 0.98, g * 0.84], axis=2)
    elif mode == "cool":
        out = np.concatenate([g * 0.95, g * 1.0, g * 1.06], axis=2)
    else:
        out = arr
    out = np.clip((out - 128) * 1.08 + 124, 0, 255).astype(np.uint8)
    rgba = np.dstack([out, np.full(out.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)


def photo_shot(c, t, d, W, H, name, pal, credit, mode="mono", start=(0.5, 0.5, 1.0), end=(0.5, 0.45, 1.12),
               crop=None, caption_lines=None, fit="cover"):
    """Ken Burns move: start/end = (fx, fy, zoom) where fx, fy is the image point at screen centre."""
    k = K(H)
    img = graded(name, mode, crop)
    c.clear(col((8, 8, 8)))
    if img is None:
        return False
    iw, ih = img.width(), img.height()
    u = ease(t / d)
    fx, fy, z = (lerp(a, b, u) for a, b in zip(start, end))
    cover = max(W / iw, H / ih)
    contain = min(W / iw, H / ih)
    samp = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
    if fit == "contain" and contain < cover * 0.9:
        # blurred backfill + sharp contained image
        s0 = cover * 1.1
        c.save(); c.translate(W / 2, H / 2); c.scale(s0, s0); c.translate(-iw / 2, -ih / 2)
        c.drawImage(img, 0, 0, samp, skia.Paint(ImageFilter=skia.ImageFilters.Blur(30, 30), Alphaf=0.5))
        c.restore()
        s = contain * z * 0.94
    else:
        s = cover * z
    c.save()
    c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-fx * iw, -fy * ih)
    c.drawImage(img, 0, 0, samp)
    c.restore()
    if caption_lines:
        location_card(c, W, H, caption_lines, clamp((t - 0.8) / 0.8) * clamp((d - t) / 0.4), pal)
    small_tag(c, W, H, "ARCHIVAL · " + credit, pal, 0.8)
    return True


def have_photo(name):
    return (ARCHIVE / name).exists()


# ------------------------------------------------------------------ scientific diagrams
def nucleus(c, x, y, r, n_p, n_n, t, k, seed=4, tremble=1.0, a=1.0):
    rng = np.random.default_rng(seed)
    pts = []
    total = n_p + n_n
    for i in range(total):
        rr = r * math.sqrt(rng.uniform(0, 1))
        th = rng.uniform(0, 6.283)
        pts.append((rr * math.cos(th), rr * math.sin(th), i < n_p, rng.uniform(0, 6.28)))
    pts.sort(key=lambda p: p[1])
    br = r * 0.16
    for px, py, is_p, ph in pts:
        jx = math.sin(t * 9 + ph) * br * 0.12 * tremble
        jy = math.cos(t * 8 + ph) * br * 0.12 * tremble
        colr = (214, 150, 86) if is_p else (150, 156, 166)
        c.drawCircle(x + px + jx, y + py + jy, br, P(c=col(colr, a)))
        c.drawCircle(x + px + jx - br * 0.3, y + py + jy - br * 0.3, br * 0.35, P(c=col((255, 255, 255), 0.25 * a)))


def particle(c, x, y, r, colr, a=1.0):
    c.drawCircle(x, y, r, P(c=col(colr, a)))
    c.drawCircle(x - r * 0.3, y - r * 0.3, r * 0.35, P(c=col((255, 255, 255), 0.3 * a)))


def label_line(c, x0, y0, x1, y1, s, k, pal, a=1.0, align="left", size=16):
    c.drawLine(x0, y0, x1, y1, P(c=col(pal["fg"], 0.7 * a), stroke=1.1 * k))
    text(c, s, x1 + (8 if align == "left" else -8) * k, y1 + 5 * k, size * k, "med", pal["fg"], a, track=0.12, align=align)


def energy_ring(c, x, y, r, a, k):
    c.drawCircle(x, y, r, P(c=col((255, 220, 170), a * 0.6), stroke=2.2 * k))
    c.drawCircle(x, y, r * 0.7, P(c=col((255, 220, 170), a * 0.2), blur=12 * k))


# =====================================================================================
# v2 TEXT SYSTEM (overrides the first-pass helpers above)
#  - every overlay line is measured; plates size to their text; long lines wrap
#  - one consistent reveal: soft left-to-right wipe + short slide + fade, eased
#  - labels on maps/timelines are placed without collisions and drawn with a halo
# =====================================================================================
from engine import measure  # noqa: E402

CARD_POS = ["bl"]          # set per shot by the renderer: "tl" for 2D scenes, "bl" otherwise
LIGHT = (242, 238, 228)
SOFT = (206, 210, 212)


def reveal_text(c, s, x, y, size, fc, color, prog, track=0.0, align="left", shadow=0.6, halo=None):
    """Wipe-reveal a line of text. prog 0..1 (already eased by caller or raw)."""
    if prog <= 0.001 or not s:
        return measure(s, size, fc, track) if s else 0
    w = measure(s, size, fc, track)
    x0 = x - (w / 2 if align == "center" else (w if align == "right" else 0))
    p = eout(prog)
    slide = (1 - p) * size * 0.35
    c.save()
    c.clipRect(skia.Rect(x0 - size, y - size * 1.3, x0 + (w + size * 2) * p, y + size * 0.6))
    text(c, s, x0 + slide, y, size, fc, color, clamp(prog * 1.8), track=track, shadow=shadow, halo=halo)
    c.restore()
    return w


def wrap_m(s, size, fc, maxw, track=0.0):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if measure(trial, size, fc, track) > maxw and cur:
            lines.append(cur); cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def small_tag(c, W, H, s, pal, a=0.7):
    k = K(H)
    text(c, s, W - 64 * k, 56 * k, 12 * k, "mono", (214, 216, 216), a * 0.9, track=0.14, align="right", shadow=0.8)


def location_card(c, W, H, lines, a, pal, x=None, y=None, plate=True, pos=None):
    """Documentary location card. lines: [(text, size, face, colour_key)]. a: visibility 0..1."""
    if a <= 0.01:
        return
    k = K(H)
    pos = pos or CARD_POS[0]
    accent = mix(pal.get("accent", (201, 164, 99)), (255, 255, 255), 0.15)
    maxw = W * 0.46
    rows = []
    for i, (s, size, fc, ck) in enumerate(lines):
        sz = size * k
        tr = 0.16 if i == 0 else (0.1 if fc.startswith("mono") else 0.04)
        colr = LIGHT if i == 0 else (accent if ck == "accent" else (SOFT if ck != "muted" else (170, 176, 180)))
        for ln in wrap_m(s, sz, fc, maxw, tr):
            rows.append((ln, sz, fc, colr, tr))
    padx, pady = 28 * k, 22 * k
    widths = [measure(r[0], r[1], r[2], r[4]) for r in rows]
    bw = max(widths) + padx * 2
    gaps = [r[1] * (1.25 if j else 1.0) for j, r in enumerate(rows)]
    bh = sum(gaps) + pady * 2 + 14 * k
    x = (64 * k if x is None else x)
    if y is None:
        y = (H - 64 * k - bh) if pos == "bl" else 96 * k
    grow = eout(clamp(a / 0.45))
    if plate:
        c.drawRect(skia.Rect(x, y, x + bw * grow, y + bh), P(c=col((8, 10, 12), 0.66 * clamp(a * 2))))
        c.drawRect(skia.Rect(x, y, x + 3 * k, y + bh * grow), P(c=col(accent, clamp(a * 2))))
    yy = y + pady + 14 * k
    for j, (ln, sz, fc, colr, tr) in enumerate(rows):
        yy += gaps[j] if j else rows[0][1] * 0.82
        prog = clamp((a - 0.15 - j * 0.1) / 0.55)
        reveal_text(c, ln, x + padx, yy, sz, fc, colr, prog, track=tr, shadow=0.0 if plate else 0.7)


def callout(c, t, d, W, H, pal, lines, plate=True, icon=None, x=None, y=None, maxw=900, bg=True, title=None):
    k = K(H)
    if bg:
        bg_fill(c, W, H, pal)
    x = 0.14 * W if x is None else x
    y = 0.4 * H if y is None else y
    if icon:
        icon(c, t, x, y, k)
        x += 300 * k
    a0 = eout((t - 0.2) / 0.8)
    c.drawLine(x, y - 46 * k, x + 120 * k * a0, y - 46 * k, P(c=col(pal["accent"], a0), stroke=2.0 * k))
    yy = y
    if title:
        reveal_text(c, title, x, yy, 44 * k, "semi", LIGHT, clamp((t - 0.3) / 0.8), track=0.1)
        yy += 70 * k
    n = 0
    for s in lines:
        for ln in wrap_m(s, 32 * k, "reg", maxw * k):
            reveal_text(c, ln, x, yy, 32 * k, "reg", SOFT, clamp((t - 0.7 - n * 0.18) / 0.8))
            yy += 48 * k
            n += 1
        yy += 12 * k


def title_card(c, t, d, W, H, pal, main, sub=None, tag=None, main_size=104, sub_size=24):
    k = K(H)
    bg_fill(c, W, H, pal)
    equations_backdrop(c, W, H, t, pal)
    push = 1 + 0.025 * t / max(d, 0.1)
    c.save(); c.translate(W / 2, H / 2); c.scale(push, push); c.translate(-W / 2, -H / 2)
    p = eout((t - 0.3) / 1.6)
    tr = lerp(0.6, 0.34, p)
    text(c, main, W / 2, H * 0.5, main_size * k, "semi", LIGHT, clamp((t - 0.3) / 1.2), track=tr, align="center", shadow=0.6)
    if sub:
        wl = measure(main, main_size * k, "semi", tr)
        c.drawLine(W / 2 - wl / 2 * p, H * 0.5 + 36 * k, W / 2 + wl / 2 * p, H * 0.5 + 36 * k, P(c=col(pal["accent"], p), stroke=1.6 * k))
        for j, line in enumerate(sub if isinstance(sub, list) else [sub]):
            reveal_text(c, line, W / 2, H * 0.5 + (84 + j * 38) * k, sub_size * k, "med", SOFT, clamp((t - 1.3 - j * 0.2) / 1.0),
                        track=0.2, align="center")
    c.restore()
    if tag:
        small_tag(c, W, H, tag, pal)


def timeline(c, t, d, W, H, pal, events, focus=None, ticks=(1904, 1927, 1939, 1942, 1943, 1945, 1949, 1954, 1963, 1967),
             reveal_all=False, bg=True, ghost=None):
    k = K(H)
    if bg:
        bg_fill(c, W, H, pal)
    if ghost:
        ghost(c, t)
    y = H * 0.55
    lo, hi = (focus if focus else (1900, 1970))
    span = W * 0.84
    pan = (t / max(d, 0.1) - 0.5) * 0.02 * W

    def X(year):
        return W * 0.08 + (year - lo) / (hi - lo) * span - pan

    draw = eout(t / 1.0)
    c.drawLine(X(lo), y, lerp(X(lo), X(hi), draw), y, P(c=col(LIGHT, 0.55), stroke=1.8 * k))
    last = -1e9
    for yr in ticks:
        if not (lo <= yr <= hi):
            continue
        xx = X(yr)
        if xx > lerp(X(lo), X(hi), draw):
            continue
        c.drawLine(xx, y - 8 * k, xx, y + 8 * k, P(c=col(LIGHT, 0.55), stroke=1.4 * k))
        if xx - last >= 64 * k:
            text(c, str(yr), xx, y + 36 * k, 17 * k, "mono", (180, 186, 190), 0.95, align="center")
            last = xx
    # collision-free label layout
    placed = []
    levels = [1, -1, 2, -2, 3, -3]
    order = sorted(range(len(events)), key=lambda i: events[i][0])
    lay = {}
    for i in order:
        yr, label = events[i]
        lines = wrap_m(label, 20 * k, "med", 300 * k)
        w = max(measure(ln, 20 * k, "med") for ln in lines) + 24 * k
        h = len(lines) * 27 * k
        xx = X(yr)
        for lv in levels:
            top = (y - (64 + (abs(lv) - 1) * 74) * k - h) if lv > 0 else (y + (62 + (abs(lv) - 1) * 74) * k)
            box = (xx - w / 2, top, xx + w / 2, top + h)
            if all(not (box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3]) for b in placed):
                placed.append(box); lay[i] = (lv, top, lines); break
        else:
            lay[i] = (1, y - 64 * k - h, lines)
    for rank, i in enumerate(order):
        yr, label = events[i]
        lv, top, lines = lay[i]
        a = clamp((t - 0.5 - rank * (0.18 if reveal_all else 0.5)) / 0.7)
        if a <= 0:
            continue
        xx = X(yr)
        end = top + len(lines) * 27 * k + 6 * k if lv > 0 else top - 14 * k
        c.drawLine(xx, y, xx, lerp(y, end, eout(a)), P(c=col(pal["accent"], a), stroke=1.3 * k))
        c.drawCircle(xx, y, 6.5 * k * eout(a), P(c=col(pal["accent"])))
        for j, ln in enumerate(lines):
            reveal_text(c, ln, xx, top + (j + 0.8) * 27 * k, 20 * k, "med", LIGHT, clamp(a * 1.2 - j * 0.15), align="center")


def legend(c, W, H, items, pal, a, x=None, y=None):
    if a <= 0.01:
        return
    k = K(H)
    x = 64 * k if x is None else x
    y = 120 * k if y is None else y
    w = max(measure(lb, 16 * k, "med", 0.04) for _, lb, _ in items) + 80 * k
    c.drawRect(skia.Rect(x - 18 * k, y - 30 * k, x - 18 * k + w * eout(clamp(a / 0.5)), y + len(items) * 34 * k), P(c=col((8, 10, 12), 0.62 * a)))
    for i, (colr, label, kind) in enumerate(items):
        yy = y + i * 34 * k
        if kind in ("fill", "hatch"):
            c.drawRect(skia.Rect(x, yy - 14 * k, x + 24 * k, yy + 2 * k), P(c=col(colr, a)))
        elif kind == "line":
            c.drawLine(x, yy - 6 * k, x + 24 * k, yy - 6 * k, P(c=col(colr, a), stroke=2 * k))
        else:
            c.drawCircle(x + 12 * k, yy - 6 * k, 6 * k, P(c=col(colr, a)))
        reveal_text(c, label, x + 40 * k, yy, 16 * k, "med", LIGHT, clamp((a - 0.2 - i * 0.1) / 0.6), track=0.04, shadow=0)


def map_title(c, W, H, pal, title, sub, a):
    if a <= 0.01:
        return
    k = K(H)
    reveal_text(c, title, 64 * k, 92 * k, 34 * k, "semi", LIGHT, a, track=0.2)
    if sub:
        reveal_text(c, sub, 64 * k, 124 * k, 14 * k, "mono", SOFT, clamp(a * 1.3 - 0.2), track=0.12)


def date_counter(c, W, H, pal, s, a):
    k = K(H)
    text(c, s, W - 64 * k, 118 * k, 32 * k, "monom", mix(pal["accent"], (255, 255, 255), 0.15), a, align="right", track=0.06, shadow=0.7)


def _overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def draw_map(c, W, H, mv, center, width_km, pal, fills=(), markers=(), labels=(), routes=(), rings=(), t=0.0,
             grat=10, land_a=1.0, coast_w=1.1):
    k = K(H)
    mat, m = mv.view(W, H, center, width_km)
    c.clear(col(pal["sea"]))
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (W * 0.55, H * 0.45), W * 0.8, [col(mix(pal["sea"], (255, 255, 255), 0.05)), col(pal["sea"])])))
    gp = P(c=col((255, 255, 255), 0.06), stroke=k)
    b = mv.bbox
    for lon in np.arange(math.floor(b[0] / grat) * grat, b[2] + 1, grat):
        pts = [mv.S(mat, lon, la) for la in np.linspace(max(b[1], -80), min(b[3], 85), 60)]
        c.drawPath(poly([(p.x(), p.y()) for p in pts], close=False), gp)
    for lat in np.arange(math.floor(b[1] / grat) * grat, b[3] + 1, grat):
        pts = [mv.S(mat, lo, lat) for lo in np.linspace(b[0], b[2], 120)]
        c.drawPath(poly([(p.x(), p.y()) for p in pts], close=False), gp)
    import engine as _e
    _tt = _e.CLOCK[0]
    # sea shimmer: faint drifting swell lines (land is drawn over them)
    sp = P(c=col((255, 255, 255), 0.055), stroke=1.2 * k)
    for j in range(int(H / (26 * k)) + 2):
        yy = j * 26 * k + 6 * k * math.sin(_tt * 0.5 + j)
        x0 = ((j * 137 * k + _tt * 22 * k) % (180 * k)) - 180 * k
        while x0 < W:
            c.drawLine(x0, yy, x0 + 60 * k, yy, sp)
            x0 += 180 * k
    lp = skia.Path(mv.land); lp.transform(mat)
    c.drawPath(lp, P(c=col(pal["land"], land_a)))
    # drifting cloud shadows over everything on the map
    for i in range(7):
        cxs = ((i * 0.37 + _tt * 0.012) % 1.4 - 0.2) * W
        cys = (0.15 + (i * 0.29) % 0.8) * H
        rr = (160 + 90 * (i % 3)) * k
        dark_map = sum(pal["sea"]) / 3 < 60
        c.drawOval(skia.Rect(cxs - rr * 1.6, cys - rr * 0.7, cxs + rr * 1.6, cys + rr * 0.7),
                   P(c=col((200, 210, 220), 0.045) if dark_map else col((0, 0, 0), 0.07), blur=rr * 0.5))
    for key, colr, a, hatched in fills:
        if a <= 0.01:
            continue
        fp = skia.Path(mv.country(key)); fp.transform(mat)
        c.drawPath(fp, P(c=col(colr, a * (0.55 if hatched else 0.9))))
        if hatched:
            hp = skia.Paint(AntiAlias=True, Shader=hatch_shader(*[int(v) for v in mix(colr, (255, 255, 255), 0.25)],
                                                                 int(200 * a), max(4, int(14 * k)), max(1, int(4 * k))))
            c.drawPath(fp, hp)
        c.drawPath(fp, P(c=col(mix(colr, (255, 255, 255), 0.35), a * 0.8), stroke=1.0 * k))
    c.drawPath(lp, P(c=col(pal["coast"], 0.8 * land_a), stroke=coast_w * k))
    for pts, prog, colr in routes:
        if prog <= 0:
            continue
        dense = []
        for (a1, b1), (a2, b2) in zip(pts[:-1], pts[1:]):
            for u in np.linspace(0, 1, 30, endpoint=False):
                dense.append(mv.S(mat, lerp(a1, a2, u), lerp(b1, b2, u)))
        dense.append(mv.S(mat, *pts[-1]))
        path = poly([(p.x(), p.y()) for p in dense], close=False)
        meas = skia.PathMeasure(path, False)
        L = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L * clamp(prog), seg, True)
        c.drawPath(seg, P(c=col(colr, 0.25), stroke=7 * k, cap=1))
        rp = P(c=col(colr), stroke=2.6 * k)
        rp.setPathEffect(skia.DashPathEffect.Make([12 * k, 8 * k], -_tt * 40 * k))
        c.drawPath(seg, rp)
        pos = meas.getPosTan(L * clamp(prog))
        if pos and prog < 1:
            px_, py_ = pos[0].x(), pos[0].y()
            ang = math.degrees(math.atan2(pos[1].y(), pos[1].x()))
            c.drawCircle(px_, py_, 22 * k, P(c=col(colr, 0.25), blur=10 * k))
            c.save(); c.translate(px_, py_); c.rotate(ang); c.scale(k * 1.3, k * 1.3)
            c.drawPath(poly([(14, 0), (4, -2), (-2, -16), (-6, -16), (-3, -2), (-10, -2), (-14, -7), (-16, -7), (-14, 0),
                             (-16, 7), (-14, 7), (-10, 2), (-3, 2), (-6, 16), (-2, 16), (4, 2)]), P(c=col((250, 246, 236))))
            c.restore()
    for lon, lat, km, a in rings:
        p = mv.S(mat, lon, lat)
        c.drawCircle(p.x(), p.y(), km * 1000 / m, P(c=col(pal["accent"], a * 0.8), stroke=1.6 * k))
    # ---- markers + collision-free labels
    occupied = [(0, 0, W, 135 * k), (0, H - 40 * k, W, H)]
    light_map = sum(pal["sea"]) / 3 > 110
    halo = mix(pal["sea"], (255, 255, 255), 0.55) if light_map else mix(pal["sea"], (0, 0, 0), 0.45)
    ink = pal.get("ink", (50, 42, 34)) if light_map else LIGHT
    region_c = mix(ink, pal["sea"], 0.35) if light_map else (196, 202, 206)
    todo = []
    mrects = []
    for mk in markers:
        lon, lat, name, a = mk[:4]
        style = mk[4] if len(mk) > 4 else "dot"
        off = mk[5] if len(mk) > 5 else (14, -12)
        if a <= 0.01:
            continue
        p = mv.S(mat, lon, lat)
        colr = (mix(pal["accent"], (255, 255, 255), 0.1) if not light_map else mix(pal["accent"], (0, 0, 0), 0.25)) if style in ("key", "target") else ink
        r = (7 if style != "dot" else 4.5) * k
        c.drawCircle(p.x(), p.y(), r * (0.6 + 0.4 * eout(a)), P(c=col(colr, a)))
        if style in ("key", "target"):
            c.drawCircle(p.x(), p.y(), r * 2.3, P(c=col(colr, a), stroke=1.6 * k))
            for q in range(2):
                ph = ((_tt * 0.6 + q * 0.5 + p.x() * 0.001) % 1.0)
                c.drawCircle(p.x(), p.y(), r * (2.3 + 5 * ph), P(c=col(colr, a * 0.6 * (1 - ph)), stroke=1.4 * k))
        mrects.append((p.x() - r * 1.6, p.y() - r * 1.6, p.x() + r * 1.6, p.y() + r * 1.6))
        if name:
            todo.append((p, name, a, style, off, colr))
    occupied += mrects
    for p, name, a, style, off, colr in sorted(todo, key=lambda z: z[3] == "dot"):
        size = (18 if style != "dot" else 16) * k
        fc = "semi" if style != "dot" else "med"
        w = measure(name, size, fc, 0.12)
        cands = [off, (20, -14), (20, 24), (-20, -14), (-20, 24), (0, -26), (0, 38)]
        chosen = None
        for ox, oy in cands:
            ox, oy = ox * k, oy * k
            x0 = p.x() + ox - (w if ox < 0 else (w / 2 if ox == 0 else 0))
            box = (x0 - 4 * k, p.y() + oy - size, x0 + w + 4 * k, p.y() + oy + size * 0.3)
            if box[0] > 20 * k and box[2] < W - 20 * k and all(not _overlap(box, o) for o in occupied):
                chosen = (x0, p.y() + oy, box); break
        if chosen is None:
            continue
        occupied.append(chosen[2])
        reveal_text(c, name, chosen[0], chosen[1], size, fc, colr, a, track=0.12, shadow=0, halo=halo)
    for lon, lat, txt, size, a in labels:
        if a <= 0.01:
            continue
        p = mv.S(mat, lon, lat)
        sz = (size + 2) * k
        w = measure(txt, sz, "reg", 0.3)
        box = (p.x() - w / 2, p.y() - sz, p.x() + w / 2, p.y() + sz * 0.3)
        if any(_overlap(box, o) for o in occupied):
            continue
        occupied.append(box)
        text(c, txt, p.x(), p.y(), sz, "reg", region_c, a * 0.85, track=0.3, align="center", halo=halo)
    return mat, m


_document_shot_v1 = document_shot


def document_shot(c, t, d, W, H, surf, pal, focus=(0.5, 0.3), tag="RECREATION", tone=(46, 36, 28),
                  tilt=6.0, push=(1.0, 1.35), highlight=None, caption_lines=None, under=None, shift=0.0):
    if shift:
        c.save(); c.translate(W * shift, 0)
        _document_shot_v1(c, t, d, W, H, surf, pal, focus, None, tone, tilt, (push[0], min(push[1], 1.15)), highlight, None, under)
        c.restore()
        desk_edge = P(c=col(tone))
        c.drawRect(skia.Rect(0, 0, W * shift, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [(0, 0), (W * shift, 0)], [col(mix(tone, (0, 0, 0), 0.45)), col(mix(tone, (0, 0, 0), 0.45), 0)])))
        if tag:
            small_tag(c, W, H, tag, pal)
        return
    _document_shot_v1(c, t, d, W, H, surf, pal, focus, tag, tone, tilt, push, highlight, caption_lines, under)


# =====================================================================================
# v3: overlays (tags, cards, titles, legends) are deferred so the renderer can draw them
# steady on top of the moving camera and the ambient particle layer.
DEFER = [False]
OVL = []


def _deferrable(fn):
    def wrapper(*a, **kw):
        if DEFER[0]:
            OVL.append((fn, a, kw))
        else:
            fn(*a, **kw)
    wrapper.__wrapped__ = fn
    return wrapper


small_tag = _deferrable(small_tag)
location_card = _deferrable(location_card)
map_title = _deferrable(map_title)
legend = _deferrable(legend)
date_counter = _deferrable(date_counter)


def flush_overlays(c):
    items = OVL[:]
    OVL.clear()
    for fn, a, kw in items:
        a = (c,) + tuple(a[1:])
        fn(*a, **kw)
