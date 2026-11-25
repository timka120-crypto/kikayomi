"""Environment kit for 2.5D scenes: skies, rooms, blackboards, furniture, buildings, trees, vehicles,
a rigged horse, a side-profile B-29, explosion clouds and crowds. All coordinates in metres in the
current depth plane (call inside Cam.begin / layer)."""
import math

import numpy as np
import skia

from engine import (clamp, lerp, ease, eout, smooth, win, col, mix, text, P, poly, pine, ridge, fog, Cam,
                    draw_person, Look, Pose, walk_pose, OPPENHEIMER_1944, GROVES, SOLDIER, SCIENTIST)

# ------------------------------------------------------------------ extra looks
OPP_CHILD = Look(height=1.38, build=0.75, suit=(70, 64, 58), suit_dark=(54, 50, 46), hat=None, hair=(40, 34, 30))
OPP_TEEN = Look(height=1.66, build=0.74, suit=(76, 70, 62), suit_dark=(60, 56, 50), hat=None, hair=(40, 34, 30))
OPP_YOUNG = Look(height=1.80, build=0.78, suit=(62, 60, 66), suit_dark=(48, 46, 52), hat=None, hair=(36, 30, 28))
OPP_30S = Look(height=1.81, build=0.8, suit=(96, 92, 84), suit_dark=(74, 70, 64), shirt=(120, 150, 186), hat=None, hair=(40, 34, 30))
OPP_RANCH = Look(height=1.81, build=0.8, suit=(66, 90, 128), suit_dark=(52, 72, 104), shirt=(66, 90, 128),
                 hat=(150, 120, 84), hat_band=(90, 70, 50), hair=(40, 34, 30))
OPP_TRINITY = Look(height=1.82, build=0.72, suit=(150, 138, 110), suit_dark=(120, 110, 88), shirt=(200, 196, 180))
OPP_50S = Look(height=1.81, build=0.78, suit=(48, 50, 56), suit_dark=(38, 40, 44), hat=None, hair=(150, 150, 150))
OPP_60S = Look(height=1.79, build=0.7, suit=(96, 98, 102), suit_dark=(76, 78, 82), hat=None, hair=(200, 200, 198),
               skin=(200, 176, 160))
GROVES_45 = GROVES
FERMI = Look(height=1.68, build=1.0, suit=(110, 110, 104), suit_dark=(88, 88, 84), hat=None, hair=(52, 44, 38))
BORN = Look(height=1.76, build=1.0, suit=(40, 40, 46), suit_dark=(32, 32, 36), hat=None, hair=(60, 50, 42))
LAWRENCE = Look(height=1.86, build=1.0, suit=(120, 112, 100), suit_dark=(96, 90, 80), hat=None, hair=(200, 176, 120))
HAHN = Look(height=1.72, build=1.05, suit=(226, 224, 216), suit_dark=(196, 194, 186), hat=None, hair=(170, 170, 166),
            moustache=True, coat_long=True)
STRASSMANN = Look(height=1.76, build=0.95, suit=(226, 224, 216), suit_dark=(196, 194, 186), hat=None, hair=(50, 42, 36),
                  coat_long=True)
BETHE = Look(height=1.80, build=1.25, suit=(110, 96, 80), suit_dark=(90, 78, 64), hat=None, hair=(110, 84, 60))
KISTI = Look(height=1.74, build=1.15, suit=(150, 138, 110), suit_dark=(120, 110, 88), hat=None, hair=(120, 110, 100))
TIBBETS = Look(height=1.78, build=1.0, suit=(120, 120, 96), suit_dark=(98, 98, 78), hat=None, hair=(44, 38, 34))
CREW = Look(height=1.76, build=1.05, suit=(122, 118, 92), suit_dark=(100, 96, 74), hat=None, hair=(70, 56, 44))
PARSONS = Look(height=1.76, build=0.95, suit=(160, 146, 110), suit_dark=(130, 118, 90), hat=None, hair=(120, 100, 80))
TRUMAN = Look(height=1.75, build=1.05, suit=(110, 112, 116), suit_dark=(88, 90, 94), hat=None, hair=(170, 170, 168))
OFFICIAL = Look(height=1.78, build=1.1, suit=(52, 54, 60), suit_dark=(40, 42, 46), hat=(44, 44, 48), hat_band=(24, 24, 26))
WOMAN = Look(height=1.64, build=0.9, suit=(120, 84, 80), suit_dark=(96, 66, 64), shirt=(220, 214, 200), hat=None,
             hair=(90, 62, 44), skirt=True, hair_long=True)
WOMAN2 = Look(height=1.62, build=0.9, suit=(70, 90, 110), suit_dark=(56, 72, 88), shirt=(220, 214, 200), hat=None,
              hair=(50, 40, 34), skirt=True, hair_long=True)
STUDENT = Look(height=1.76, build=1.0, suit=(90, 76, 62), suit_dark=(72, 60, 50), hat=None, hair=(80, 62, 46))
STUDENT2 = Look(height=1.74, build=1.0, suit=(60, 64, 74), suit_dark=(48, 52, 60), hat=None, hair=(40, 34, 30))
JP_MAN = Look(height=1.66, build=0.9, suit=(210, 206, 196), suit_dark=(180, 176, 168), shirt=(230, 228, 220), hat=None,
              hair=(30, 28, 28))
JP_STUDENT = Look(height=1.45, build=0.8, suit=(40, 44, 56), suit_dark=(32, 36, 46), hat=None, hair=(26, 24, 24))
JP_WOMAN = Look(height=1.55, build=0.85, suit=(110, 106, 96), suit_dark=(88, 84, 76), shirt=(200, 196, 186), hat=None,
                hair=(26, 24, 24), skirt=True, hair_long=True)


def stand(**kw):
    p = Pose(hip_l=-3, hip_r=4, knee_l=4, knee_r=3, sh_l=-4, sh_r=6, el_l=14, el_r=16)
    for a, b in kw.items():
        setattr(p, a, b)
    return p


def sit(**kw):
    p = Pose(hip_l=88, hip_r=92, knee_l=88, knee_r=92, sh_l=12, sh_r=30, el_l=40, el_r=60, bob=0.45, lean=6)
    for a, b in kw.items():
        setattr(p, a, b)
    return p


def idle(p, t, seed=0.0, amt=1.0):
    """Subtle life: breathing, small weight shifts and head motion."""
    p.lean += math.sin(t * 1.3 + seed) * 0.8 * amt
    p.head += math.sin(t * 0.7 + seed * 2) * 2.0 * amt
    p.sh_r += math.sin(t * 1.1 + seed) * 2 * amt
    p.sh_l += math.sin(t * 0.9 + seed * 3) * 1.5 * amt
    return p


def gesture(p, t, seed=0.0, amt=1.0):
    p.sh_r = 35 + 20 * amt * math.sin(t * 2.1 + seed)
    p.el_r = 70 + 20 * amt * math.sin(t * 3.3 + seed)
    p.head += 3 * math.sin(t * 1.7 + seed)
    return p


# ------------------------------------------------------------------ sky and ground (screen space)
def sky(c, W, H, top, bottom, horizon=0.62):
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, 0), (0, H * horizon)], [col(top), col(bottom)])))


def ground(c, W, H, cam, near, far):
    hz = cam.to_screen(0, 0, 3000)[1]
    c.drawRect(skia.Rect(0, hz, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, hz), (0, H)], [col(far), col(near)])))
    return hz


def stars(c, W, H, t, n=200, seed=5, top=0.6, a=0.7):
    rng = np.random.default_rng(abs(int(seed)))
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H * top)
        r = rng.uniform(0.5, 1.5) * H / 1080
        tw = 0.6 + 0.4 * math.sin(t * rng.uniform(0.5, 2) + rng.uniform(0, 6))
        c.drawCircle(x, y, r, P(c=col((230, 232, 240), a * tw * rng.uniform(0.3, 1))))


# ------------------------------------------------------------------ interiors
def wall(c, x0, x1, top, colr, light=None, light_r=3.0, light_c=(255, 210, 160), light_a=0.3, floor=None):
    c.drawRect(skia.Rect(x0, top, x1, 0.02), P(c=col(colr)))
    if light:
        c.drawRect(skia.Rect(x0, top, x1, 0.02), skia.Paint(Shader=skia.GradientShader.MakeRadial(
            light, light_r, [col(light_c, light_a), col(light_c, 0)])))
    c.drawRect(skia.Rect(x0, -0.12, x1, 0.02), P(c=col(mix(colr, (0, 0, 0), 0.35))))  # skirting


def floor_plane(c, x0, x1, colr):
    c.drawRect(skia.Rect(x0, 0, x1, 3), P(c=col(colr)))


def window(c, x0, y0, x1, y1, t, night=False, view=None, frame=(40, 34, 30), sky_c=None):
    c.drawRect(skia.Rect(x0 - 0.06, y0 - 0.06, x1 + 0.06, y1 + 0.06), P(c=col(frame)))
    top, bot = sky_c or (((14, 22, 40), (40, 52, 74)) if night else ((150, 176, 200), (210, 220, 224)))
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, y0), (0, y1)], [col(top), col(bot)])))
    if view:
        c.save(); c.clipRect(skia.Rect(x0, y0, x1, y1)); view(c, x0, y0, x1, y1); c.restore()
    c.drawLine((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, P(c=col(frame), stroke=0.05))
    c.drawLine(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2, P(c=col(frame), stroke=0.04))


def blackboard(c, x0, y0, x1, y1, lines, size=0.13, reveal=None, chalk=(222, 224, 214), frame=(92, 70, 48), board=(30, 40, 36), start=(0.3, 0.32), gap=1.7):
    c.drawRect(skia.Rect(x0 - 0.06, y0 - 0.06, x1 + 0.06, y1 + 0.06), P(c=col(frame)))
    c.drawRect(skia.Rect(x0, y0, x1, y1), P(c=col(board)))
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(x0, y0), (x1, y1)], [col((255, 255, 255), 0.03), col((255, 255, 255), 0.07), col((255, 255, 255), 0.02)])))
    c.drawRect(skia.Rect(x0 - 0.08, y1, x1 + 0.08, y1 + 0.06), P(c=col(mix(frame, (255, 255, 255), 0.1))))
    total = sum(len(s) for s in lines)
    shown = total if reveal is None else int(total * clamp(reveal))
    yy = y0 + start[1]
    for s in lines:
        n = min(len(s), shown)
        shown -= n
        if n > 0:
            c.save(); c.translate(x0 + start[0], yy); c.scale(size / 13.5, size / 13.5)
            text(c, s[:n], 0, 0, 13.5, "reg", chalk, 0.85)
            c.restore()
        yy += size * gap


def bookshelf(c, x0, x1, y0, y1, seed=1, wood=(70, 50, 36)):
    rng = np.random.default_rng(abs(int(seed)))
    c.drawRect(skia.Rect(x0, y0, x1, y1), P(c=col(wood)))
    shelves = 5
    h = (y1 - y0) / shelves
    for i in range(shelves):
        yb = y0 + (i + 1) * h - 0.03
        x = x0 + 0.04
        while x < x1 - 0.06:
            w = rng.uniform(0.03, 0.07)
            bh = h * rng.uniform(0.6, 0.85)
            colr = [(110, 40, 36), (40, 60, 80), (60, 80, 50), (120, 96, 60), (70, 50, 70), (150, 130, 100)][rng.integers(0, 6)]
            c.drawRect(skia.Rect(x, yb - bh, x + w, yb), P(c=col(mix(colr, (0, 0, 0), rng.uniform(0, 0.3)))))
            x += w + 0.005
        c.drawRect(skia.Rect(x0, yb, x1, yb + 0.03), P(c=col(mix(wood, (0, 0, 0), 0.3))))


def desk_fg(c, x0, x1, top=-0.82, wood=(54, 38, 28), items=True, blur=0.015, lamp=False):
    c.drawRect(skia.Rect(x0, top, x1, 0.6), P(c=col(wood), blur=blur))
    c.drawRect(skia.Rect(x0, top - 0.04, x1, top + 0.02), P(c=col(mix(wood, (255, 220, 180), 0.15)), blur=blur))
    if items:
        for px, w, rot in ((x0 + 0.6, 0.42, -6), (x0 + 1.3, 0.38, 4), (x0 + 1.8, 0.4, -2)):
            c.save(); c.translate(px, top - 0.04); c.rotate(rot)
            c.drawRect(skia.Rect(0, -0.012, w, 0.0), P(c=col((214, 208, 192)), blur=blur))
            c.restore()
        c.drawRect(skia.Rect(x1 - 1.0, top - 0.16, x1 - 0.7, top - 0.04), P(c=col((90, 40, 36)), blur=blur))
        c.drawRect(skia.Rect(x1 - 0.98, top - 0.26, x1 - 0.72, top - 0.16), P(c=col((40, 52, 70)), blur=blur))
    if lamp:
        lx = x0 + 0.35
        c.drawLine(lx, top - 0.04, lx, top - 0.5, P(c=col((50, 60, 50)), stroke=0.025, blur=blur))
        c.drawPath(poly([(lx - 0.18, top - 0.48), (lx + 0.18, top - 0.48), (lx + 0.1, top - 0.6), (lx - 0.1, top - 0.6)]),
                   P(c=col((40, 80, 60)), blur=blur))
        c.drawCircle(lx, top - 0.46, 0.06, P(c=col((255, 230, 180)), blur=0.05))


def hanging_lamp(c, x, y, shade=(40, 52, 44), glow=(255, 226, 170)):
    c.drawLine(x, y - 4, x, y - 0.18, P(c=col((20, 18, 16)), stroke=0.012))
    c.drawPath(poly([(x - 0.18, y), (x + 0.18, y), (x + 0.08, y - 0.2), (x - 0.08, y - 0.2)]), P(c=col(shade)))
    c.drawCircle(x, y + 0.02, 0.05, P(c=col(glow), blur=0.03))


def chair(c, x, colr=(60, 44, 34), facing=1):
    c.drawRect(skia.Rect(x - 0.22, -0.5, x + 0.22, -0.45), P(c=col(colr)))
    for lx in (x - 0.2, x + 0.18):
        c.drawLine(lx, -0.47, lx, 0, P(c=col(colr), stroke=0.035))
    bx = x - 0.2 * facing
    c.drawLine(bx, -0.47, bx - 0.04 * facing, -1.0, P(c=col(colr), stroke=0.04))


def table(c, x0, x1, top=-0.76, colr=(70, 50, 36), cloth=None):
    c.drawRect(skia.Rect(x0, top, x1, top + 0.06), P(c=col(cloth or colr)))
    for lx in (x0 + 0.08, x1 - 0.12):
        c.drawLine(lx, top, lx, 0, P(c=col(colr), stroke=0.05))


# ------------------------------------------------------------------ exteriors
def building(c, x, w, h, colr, rows=2, roof="gable", win_c=None, door=True, brick=False, cupola=False, seed=0, lit=0.0):
    dark = win_c or mix(colr, (16, 18, 20), 0.6)
    c.drawRect(skia.Rect(x, -h, x + w, 0), P(c=col(colr)))
    if brick:
        rng = np.random.default_rng(abs(int(seed)))
        for yy in np.arange(-h, 0, 0.3):
            c.drawLine(x, yy, x + w, yy, P(c=col(mix(colr, (0, 0, 0), 0.15)), stroke=0.02))
    if roof == "gable":
        c.drawPath(poly([(x - 0.4, -h), (x + w / 2, -h - 0.22 * min(w, 8)), (x + w + 0.4, -h)]), P(c=col(mix(colr, (30, 30, 30), 0.55))))
    elif roof == "flat":
        c.drawRect(skia.Rect(x - 0.2, -h - 0.3, x + w + 0.2, -h), P(c=col(mix(colr, (255, 255, 255), 0.15))))
    if cupola:
        cx = x + w / 2
        c.drawRect(skia.Rect(cx - 0.9, -h - 2.4, cx + 0.9, -h - 0.6), P(c=col((230, 228, 220))))
        c.drawPath(poly([(cx - 1.1, -h - 2.4), (cx, -h - 3.6), (cx + 1.1, -h - 2.4)]), P(c=col((210, 206, 196))))
        c.drawLine(cx, -h - 3.6, cx, -h - 4.6, P(c=col((200, 196, 186)), stroke=0.08))
    rng = np.random.default_rng(abs(int(seed)) + 7)
    rh = h / rows
    for r in range(rows):
        y0 = -h + r * rh + rh * 0.22
        for wx in np.arange(x + 0.7, x + w - 0.8, 1.6):
            wc = mix(dark, (255, 214, 150), lit * (rng.uniform() < 0.55))
            c.drawRect(skia.Rect(wx, y0, wx + 0.85, y0 + rh * 0.5), P(c=col(wc)))
    if door:
        c.drawRect(skia.Rect(x + w * 0.46, -2.2, x + w * 0.46 + 1.1, 0), P(c=col(mix(dark, colr, 0.3))))


def deciduous(c, x, h, colr, t=0.0, leaves=0):
    trunk = mix(colr, (40, 30, 24), 0.6)
    c.drawLine(x, 0, x, -h * 0.55, P(c=col(trunk), stroke=h * 0.05))
    for i, (dx, dy, r) in enumerate(((0, -0.72, 0.3), (-0.18, -0.6, 0.22), (0.2, -0.62, 0.24), (0, -0.88, 0.22))):
        sway = math.sin(t * 0.8 + i) * h * 0.005
        c.drawCircle(x + dx * h + sway, dy * h, r * h, P(c=col(mix(colr, (0, 0, 0), i * 0.05))))


def lamp_post(c, x, h=3.6, colr=(40, 40, 40), on=0.0):
    c.drawLine(x, 0, x, -h, P(c=col(colr), stroke=0.08))
    c.drawPath(poly([(x - 0.15, -h), (x + 0.15, -h), (x + 0.1, -h - 0.35), (x - 0.1, -h - 0.35)]), P(c=col(colr)))
    if on > 0:
        c.drawCircle(x, -h - 0.15, 0.5, P(c=col((255, 214, 150), 0.35 * on), blur=0.3))
        c.drawCircle(x, -h - 0.15, 0.09, P(c=col((255, 230, 180), on)))


def car_1940(c, x, colr=(40, 48, 40), wheel_t=0.0, facing=1, lights=0.0):
    c.save(); c.translate(x, 0); c.scale(facing, 1)
    body = poly([(-2.4, -0.45), (-2.35, -0.95), (-1.0, -1.05), (-0.5, -1.55), (0.9, -1.55), (1.5, -1.0),
                 (2.35, -0.9), (2.45, -0.5), (2.3, -0.32), (-2.3, -0.32)])
    c.drawPath(body, P(c=col(colr)))
    c.drawPath(poly([(-0.35, -1.45), (0.4, -1.45), (0.4, -1.08), (-0.75, -1.08)]), P(c=col((150, 170, 186), 0.6)))
    c.drawPath(poly([(0.5, -1.45), (0.85, -1.45), (1.3, -1.08), (0.5, -1.08)]), P(c=col((150, 170, 186), 0.6)))
    for wx in (-1.5, 1.55):
        c.drawCircle(wx, -0.34, 0.36, P(c=col((20, 20, 20))))
        c.drawCircle(wx, -0.34, 0.16, P(c=col((150, 150, 146))))
        a = wheel_t * 3
        c.drawLine(wx, -0.34, wx + math.cos(a) * 0.15, -0.34 + math.sin(a) * 0.15, P(c=col((60, 60, 60)), stroke=0.03))
    if lights:
        c.drawCircle(2.35, -0.72, 0.09, P(c=col((255, 236, 190), lights)))
    c.restore()


def horse(c, x, phase, colr=(110, 76, 50), walking=1.0, facing=1, head_bob=True):
    """Side-profile horse, height ~1.6 m at the withers; phase drives a four-beat walk."""
    c.save(); c.translate(x, 0); c.scale(facing, 1)
    dark = mix(colr, (0, 0, 0), 0.3)
    legs = [(0.62, 0.0), (0.62, math.pi), (-0.62, math.pi / 2), (-0.62, 3 * math.pi / 2)]
    body_y = -1.22 + 0.02 * math.sin(phase * 2) * walking
    for i, (lx, off) in enumerate(legs):
        ph = phase + off
        a1 = math.radians(18 * math.sin(ph) * walking)
        bend = math.radians(max(0, 40 * math.sin(ph + 1.4)) * walking)
        c0 = col(dark if i % 2 else colr)
        top = (lx, body_y + 0.1)
        knee = (top[0] + math.sin(a1) * 0.55, top[1] + math.cos(a1) * 0.55)
        a2 = a1 - bend if lx < 0 else a1 + bend * 0.5
        hoof = (knee[0] + math.sin(a2) * 0.6, knee[1] + math.cos(a2) * 0.6)
        c.drawLine(*top, *knee, P(c=c0, stroke=0.13, cap=1))
        c.drawLine(*knee, *hoof, P(c=c0, stroke=0.08, cap=1))
        c.drawRect(skia.Rect(hoof[0] - 0.06, hoof[1] - 0.05, hoof[0] + 0.08, hoof[1] + 0.02), P(c=col((30, 26, 24))))
    c.drawOval(skia.Rect(-0.95, body_y - 0.35, 0.95, body_y + 0.3), P(c=col(colr)))
    nb = 0.04 * math.sin(phase * 2) * walking if head_bob else 0
    c.drawPath(poly([(0.6, body_y - 0.2), (1.05, body_y - 0.9 + nb), (1.25, body_y - 0.95 + nb), (1.05, body_y - 0.1)]), P(c=col(colr)))
    c.drawPath(poly([(1.02, body_y - 0.98 + nb), (1.6, body_y - 0.62 + nb), (1.58, body_y - 0.5 + nb), (1.12, body_y - 0.62 + nb)]), P(c=col(colr)))
    c.drawPath(poly([(1.06, body_y - 1.05 + nb), (1.12, body_y - 1.2 + nb), (1.16, body_y - 1.0 + nb)]), P(c=col(dark)))
    c.drawPath(poly([(0.62, body_y - 0.28), (1.02, body_y - 0.96 + nb), (0.96, body_y - 0.98 + nb), (0.5, body_y - 0.3)]), P(c=col(dark)))
    sw = math.sin(phase) * 0.06
    c.drawPath(poly([(-0.92, body_y - 0.15), (-1.2 + sw, body_y + 0.5), (-1.1 + sw, body_y + 0.55), (-0.85, body_y)]), P(c=col(dark)))
    c.drawCircle(1.3, body_y - 0.82 + nb, 0.025, P(c=col((20, 20, 20))))
    c.restore()
    return body_y


def b29(c, x, y, s=1.0, t=0.0, name="", number="", tail="", doors=0.0, bank=0.0, facing=1, metal=(186, 190, 192), shade=0.0):
    """Side-profile Boeing B-29 (span-side view), length ~30 m. x, y = centre of fuselage."""
    c.save(); c.translate(x, y); c.rotate(-bank); c.scale(s * facing, s)
    m1 = mix(metal, (0, 0, 0), shade)
    m2 = mix(m1, (0, 0, 0), 0.25)
    hi = mix(m1, (255, 255, 255), 0.35)
    # fuselage
    fus = skia.Path()
    fus.moveTo(15.0, 0.1); fus.cubicTo(15.4, -1.2, 14.0, -1.55, 12.5, -1.5)
    fus.lineTo(-11.0, -1.4); fus.lineTo(-14.6, -0.5); fus.lineTo(-14.8, 0.2); fus.lineTo(-11.5, 0.9)
    fus.lineTo(12.0, 1.45); fus.cubicTo(14.0, 1.45, 15.0, 1.0, 15.0, 0.1); fus.close()
    c.drawPath(fus, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, -1.5), (0, 1.5)], [col(hi), col(m1), col(m2)])))
    # glazed nose
    nose = skia.Path(); nose.moveTo(12.6, -1.45); nose.cubicTo(14.2, -1.45, 15.4, -0.8, 15.05, 0.3)
    nose.lineTo(12.6, 0.3); nose.close()
    c.drawPath(nose, P(c=col((70, 86, 100), 0.85)))
    for gx in (13.2, 13.8, 14.4):
        c.drawLine(gx, -1.4, gx + 0.3, 0.3, P(c=col(m2), stroke=0.05))
    c.drawLine(12.6, -0.55, 15.2, -0.55, P(c=col(m2), stroke=0.05))
    # anti-glare panel
    c.drawPath(poly([(11.0, -1.48), (12.6, -1.46), (12.6, -1.1), (11.2, -1.2)]), P(c=col((30, 30, 32))))
    # vertical tail
    c.drawPath(poly([(-9.8, -1.3), (-12.6, -6.4), (-13.8, -6.6), (-14.6, -6.1), (-14.6, -0.6)]), P(c=col(m1)))
    c.drawLine(-9.8, -1.3, -12.6, -6.4, P(c=col(hi), stroke=0.06))
    # horizontal stabiliser
    c.drawPath(poly([(-11.5, -0.2), (-14.6, -0.5), (-14.8, -0.15), (-11.8, 0.1)]), P(c=col(m2)))
    # wing (seen edge-on, slightly from below) and nacelles
    c.drawPath(poly([(3.5, 0.1), (-2.5, 0.0), (-3.0, 0.45), (3.8, 0.5)]), P(c=col(m2)))
    for nx, ny in ((5.4, 0.9), (2.4, 0.75)):
        c.drawPath(poly([(nx + 1.2, ny - 0.45), (nx - 3.2, ny - 0.4), (nx - 3.6, ny), (nx - 3.0, ny + 0.35), (nx + 1.2, ny + 0.45)]),
                   skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, ny - 0.5), (0, ny + 0.5)], [col(hi), col(m2)])))
        c.drawOval(skia.Rect(nx + 1.15, ny - 2.0, nx + 1.45, ny + 2.0), P(c=col((40, 40, 40), 0.22)))
        c.drawCircle(nx + 1.35, ny, 0.22, P(c=col((50, 50, 50))))
        a = t * 40 + nx
        c.drawLine(nx + 1.3, ny, nx + 1.3, ny + math.sin(a) * 1.9, P(c=col((30, 30, 30), 0.35), stroke=0.1))
    # tail gun position
    c.drawCircle(-14.7, -0.15, 0.25, P(c=col((70, 86, 100), 0.9)))
    # panel lines and windows
    for px in np.arange(-10, 12, 2.2):
        c.drawLine(px, -1.42, px, 1.4, P(c=col(m2, 0.4), stroke=0.025))
    for wx in (-4.5, -6.2):
        c.drawCircle(wx, -0.6, 0.18, P(c=col((60, 76, 90))))
    # bomb bay doors
    if doors > 0:
        for bx in (4.0, -1.6):
            c.drawPath(poly([(bx, 1.32), (bx - 2.6, 1.28), (bx - 2.7, 1.28 + 1.3 * doors), (bx - 0.1, 1.32 + 1.3 * doors)]), P(c=col(m2)))
    # markings (exact text controlled here)
    if number:
        c.save(); c.translate(8.2, 0.25); c.scale(0.045, 0.045)
        text(c, number, 0, 0, 22, "semi", (20, 20, 22), 0.95)
        c.restore()
    if name:
        c.save(); c.translate(10.0, -0.72); c.scale(0.016, 0.016)
        text(c, name, 0, 0, 22, "semi", (24, 24, 26), 0.9)
        c.restore()
    if tail:
        c.drawCircle(-12.9, -4.2, 0.95, P(c=col((20, 20, 22)), stroke=0.22))
        c.save(); c.translate(-13.35, -3.75); c.scale(0.055, 0.055)
        text(c, tail, 0, 0, 22, "semi", (20, 20, 22), 0.95)
        c.restore()
    c.restore()


def cloud_layer(c, x0, x1, y, seed, colr, a=0.8, scale=1.0, drift=0.0):
    rng = np.random.default_rng(abs(int(seed)))
    x = x0
    while x < x1:
        r = rng.uniform(2, 6) * scale
        for j in range(4):
            c.drawCircle(x + drift + rng.uniform(-r, r), y + rng.uniform(-r * 0.3, r * 0.2), r * rng.uniform(0.6, 1.0),
                         P(c=col(mix(colr, (255, 255, 255), rng.uniform(0, 0.15)), a), blur=r * 0.25))
        x += r * 1.4


def mushroom(c, x, ground_y, t, scale=1.0, glow=(255, 150, 70), smoke=(120, 96, 84), seed=3, mono=False):
    """2D billowing column and cap; t in seconds since detonation."""
    rng = np.random.default_rng(abs(int(seed)))
    rise = 1 - math.exp(-t / 3.5)
    top = ground_y - (6 + 26 * rise) * scale
    heat = math.exp(-t / 2.2)
    stem_w = (1.2 + 1.6 * rise) * scale
    for i in range(40):
        u = i / 40
        yy = lerp(ground_y, top, u)
        w = stem_w * (1 + 0.3 * math.sin(i * 1.7 + t))
        cc = mix(smoke, glow, heat * (1 - u * 0.5)) if not mono else mix((110, 110, 110), (240, 240, 236), heat * (1 - u))
        c.drawCircle(x + math.sin(i * 2.1 + t * 0.6) * 0.4 * scale, yy, w, P(c=col(cc, 0.85), blur=0.6 * scale))
    cap_r = (3 + 7 * rise) * scale
    for j in range(60):
        ang = rng.uniform(0, 6.283)
        rr = cap_r * math.sqrt(rng.uniform(0, 1))
        px = x + math.cos(ang) * rr * 1.5
        py = top + math.sin(ang) * rr * 0.6
        rad = cap_r * rng.uniform(0.25, 0.45)
        k2 = clamp(1 - rr / cap_r)
        cc = mix(smoke, glow, heat * (0.4 + 0.6 * k2)) if not mono else mix((120, 120, 120), (245, 245, 240), heat * k2)
        c.drawCircle(px + math.sin(t * 0.5 + j) * 0.3 * scale, py, rad, P(c=col(cc, 0.9), blur=rad * 0.3))
    if heat > 0.05 and not mono:
        c.drawCircle(x, top, cap_r * 1.8, P(c=col(glow, 0.25 * heat), blur=cap_r))
    # base surge
    surge = (4 + 20 * rise) * scale
    c.drawOval(skia.Rect(x - surge, ground_y - 1.5 * scale * rise, x + surge, ground_y + 0.6 * scale),
               P(c=col(mix(smoke, (180, 160, 140), 0.4), 0.6 * rise), blur=1.2 * scale))


def crowd_row(c, x0, x1, looks, seated=True, t=0.0, seed=0, facing=1, shade=0.0, spacing=0.75, z=5.0, fog_c=None):
    rng = np.random.default_rng(abs(int(seed)))
    x = x0
    i = 0
    while x < x1:
        L = looks[i % len(looks)]
        p = sit() if seated else stand()
        idle(p, t, seed + i * 1.3, 0.8)
        if seated and rng.uniform() < 0.4:
            p.sh_r, p.el_r = 50, 100  # writing notes
        draw_person(c, L, p, x=x, facing=facing, shade=shade, fog_c=fog_c, z=z)
        x += spacing * rng.uniform(0.9, 1.15)
        i += 1
