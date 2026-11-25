"""2.5D documentary animation engine: flat 2D characters and scenery placed in 3D depth,
a shaded 3D globe, film grain, text, and an ffmpeg writer. Pure Python + Skia + NumPy.

World units are metres. Screen y points down; ground is y = 0, "up" is negative y.
A layer at depth z is drawn with scale f / (z - cam.z), so nearer layers move faster
(true parallax) when the camera trucks, cranes or dollies.
"""
import json, math, subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import skia

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "graphics" / "assets"


CLOCK = [0.0]   # global film time, set by the renderer (used for blinking)

# ------------------------------------------------------------------ maths / easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ein(x):
    x = clamp(x)
    return x ** 3


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def win(t, t0, t1, fade=0.5):
    return clamp((t - t0) / fade) * clamp((t1 - t) / fade)


def col(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(255 * clamp(a)))


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ text
_TF = {}


def face(name):
    files = {"reg": "IBMPlexSans_400Regular.ttf", "med": "IBMPlexSans_500Medium.ttf",
             "semi": "IBMPlexSans_600SemiBold.ttf", "mono": "IBMPlexMono_400Regular.ttf",
             "monom": "IBMPlexMono_500Medium.ttf", "news": "OldStandardTT_400Regular.ttf",
             "newsb": "OldStandardTT_700Bold.ttf", "newsi": "OldStandardTT_400Regular_Italic.ttf",
             "type": "SpecialElite_400Regular.ttf", "frak": "UnifrakturMaguntia_400Regular.ttf",
             "serif": "LibreCaslonText_400Regular.ttf", "serifb": "LibreCaslonText_700Bold.ttf"}
    if name not in _TF:
        _TF[name] = skia.Typeface.MakeFromFile(str(ASSETS / files[name]))
    return _TF[name]


def _fonts(s, size, fc):
    font = skia.Font(face(fc), size)
    font.setSubpixel(True)
    font.setEdging(skia.Font.Edging.kAntiAlias)
    font.setHinting(skia.FontHinting.kNone)
    return [font if font.unicharToGlyph(ord(ch)) or ch == " " else _fallback(ch, size, fc) for ch in s]


def measure(s, size, fc="med", track=0.0):
    fonts = _fonts(s, size, fc)
    return sum(f.measureText(ch) for f, ch in zip(fonts, s)) + track * size * max(0, len(s) - 1)


def text(canvas, s, x, y, size, fc="med", color=(230, 226, 216), alpha=1.0, track=0.0, align="left", shadow=0.0, halo=None):
    """Draw text. shadow: soft drop-shadow strength (0-1); halo: (r,g,b) outline colour for text over maps."""
    if not s or alpha <= 0.003:
        return measure(s, size, fc, track) if s else 0
    fonts = _fonts(s, size, fc)
    ws = [f.measureText(ch) for f, ch in zip(fonts, s)]
    total = sum(ws) + track * size * max(0, len(s) - 1)
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    passes = []
    if shadow > 0:
        sp = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(200 * shadow * alpha)))
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(1.0, size * 0.12)))
        passes.append((sp, size * 0.04))
    if halo is not None:
        hp = skia.Paint(AntiAlias=True, Color=col(halo, 0.85 * alpha), Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.5, size * 0.16))
        hp.setStrokeJoin(skia.Paint.kRound_Join)
        passes.append((hp, 0.0))
    passes.append((skia.Paint(AntiAlias=True, Color=col(color, alpha)), 0.0))
    for paint, off in passes:
        xx = x
        for ch, w, f in zip(s, ws, fonts):
            canvas.drawString(ch, xx + off, y + off, f, paint)
            xx += w + track * size
    return total


_FB = {}


def _fallback(ch, size, fc):
    key = ord(ch)
    if key not in _FB:
        mgr = skia.FontMgr.RefDefault()
        tf = None
        for fam in ("DejaVu Sans", "Noto Sans Math", "Noto Sans", "FreeSerif", None):
            tf = mgr.matchFamilyStyleCharacter(fam, skia.FontStyle(), [], key)
            if tf is not None:
                break
        _FB[key] = tf
    tf = _FB[key]
    f = skia.Font(tf if tf is not None else face(fc), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


# ------------------------------------------------------------------ camera
@dataclass
class Cam:
    x: float = 0.0
    y: float = -1.6
    z: float = -6.0
    f: float = 1100.0      # focal length in px (at 1080p)
    W: int = 1920
    H: int = 1080

    def scale(self, z):
        return self.f * (self.H / 1080) / max(0.05, z - self.z)

    def to_screen(self, x, y, z):
        s = self.scale(z)
        return self.W / 2 + (x - self.x) * s, self.H / 2 + (y - self.y) * s

    def begin(self, canvas, z):
        """Enter the coordinate system of a vertical plane at depth z (world units)."""
        s = self.scale(z)
        canvas.save()
        canvas.translate(self.W / 2 - self.x * s, self.H / 2 - self.y * s)
        canvas.scale(s, s)
        return s


def fog(c, z, fog_c, near=4.0, far=120.0, amount=0.75):
    t = clamp((z - near) / (far - near)) ** 0.7 * amount
    return mix(c, fog_c, t)


def P(**kw):
    p = skia.Paint(AntiAlias=True)
    for k, v in kw.items():
        if k == "c":
            p.setColor(v)
        elif k == "stroke":
            p.setStyle(skia.Paint.kStroke_Style)
            p.setStrokeWidth(v)
        elif k == "cap":
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
        elif k == "blur" and v > 0:
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, v))
    return p


def poly(points, close=True):
    path = skia.Path()
    path.moveTo(*points[0])
    for p in points[1:]:
        path.lineTo(*p)
    if close:
        path.close()
    return path


# ------------------------------------------------------------------ characters (flat 2D, rigged)
@dataclass
class Look:
    height: float = 1.82
    build: float = 0.82          # 1 = average; Oppenheimer is very thin
    suit: tuple = (92, 88, 80)
    suit_dark: tuple = (70, 67, 61)
    shirt: tuple = (200, 196, 186)
    skin: tuple = (196, 168, 146)
    hair: tuple = (48, 42, 38)
    hat: tuple = (168, 166, 160)  # None for no hat
    hat_band: tuple = (60, 58, 56)
    shoes: tuple = (34, 30, 28)
    nose: float = 1.0
    moustache: bool = False
    cap_military: bool = False
    skirt: bool = False
    hair_long: bool = False
    coat_long: bool = False


OPPENHEIMER_1944 = Look()
GROVES = Look(height=1.84, build=1.35, suit=(118, 104, 74), suit_dark=(96, 84, 60), shirt=(150, 136, 100),
              hat=None, hair=(84, 66, 50), moustache=True, cap_military=True)
SOLDIER = Look(height=1.76, build=1.05, suit=(104, 98, 70), suit_dark=(84, 79, 56), shirt=(120, 112, 82),
               hat=(210, 210, 204), hat_band=(210, 210, 204), hair=(60, 50, 40))
SCIENTIST = Look(height=1.74, build=1.0, suit=(70, 76, 86), suit_dark=(56, 61, 70), hat=(80, 74, 66),
                 hat_band=(40, 36, 34), hair=(70, 60, 50))


@dataclass
class Pose:
    lean: float = 0.0        # torso lean (deg, + forward)
    head: float = 0.0        # head tilt (deg, + down)
    hip_l: float = 0.0       # thigh angles from vertical (deg, + forward)
    hip_r: float = 0.0
    knee_l: float = 0.0      # knee bend (deg, + bend)
    knee_r: float = 0.0
    sh_l: float = 0.0        # upper arm from vertical (deg, + forward)
    sh_r: float = 0.0
    el_l: float = 10.0       # elbow bend (deg, + bend forward)
    el_r: float = 10.0
    bob: float = 0.0         # vertical body offset (m)
    hand_r: str = ""         # "cig", "chalk", "pipe", "clip"


def walk_pose(phase, speed=1.0):
    s = math.sin(phase)
    c = math.cos(phase)
    a = 24 * speed
    return Pose(lean=4 * speed, head=2,
                hip_l=a * s, hip_r=-a * s,
                knee_l=max(0, 38 * math.sin(phase + 1.9)) * speed + 4,
                knee_r=max(0, 38 * math.sin(phase + 1.9 + math.pi)) * speed + 4,
                sh_l=-20 * s * speed, sh_r=20 * s * speed,
                el_l=18 + 10 * max(0, -s), el_r=18 + 10 * max(0, s),
                bob=-0.025 * abs(c) * speed)


def _limb(canvas, p0, a1, l1, a2, l2, w1, w2, color, foot=None):
    """Two-segment limb hanging down from p0. Angles in degrees from vertical (+ = forward/right)."""
    r1, r2 = math.radians(a1), math.radians(a1 - a2 if foot is None else a1 - a2)
    j = (p0[0] + math.sin(r1) * l1, p0[1] + math.cos(r1) * l1)
    if foot is None:  # arm: elbow bends forward (positive)
        r2 = math.radians(a1 + a2)
    else:             # leg: knee bends backward
        r2 = math.radians(a1 - a2)
    e = (j[0] + math.sin(r2) * l2, j[1] + math.cos(r2) * l2)
    canvas.drawLine(*p0, *j, P(c=col(color), stroke=w1, cap=1))
    canvas.drawLine(*j, *e, P(c=col(color), stroke=w2, cap=1))
    return j, e, r2


def draw_person(canvas, look: Look, pose: Pose, x=0.0, facing=1, shade=0.0, fog_c=None, z=5.0, light=(255, 236, 205), rim=0.0):
    """Draw a flat character standing at ground point (x, 0) in the current plane."""
    L = look
    k = L.height / 1.82
    b = L.build

    def C(c):
        c2 = mix(c, (0, 0, 0), shade)
        return fog(c2, z, fog_c) if fog_c else c2

    canvas.save()
    canvas.translate(x, pose.bob)
    canvas.scale(facing * k, k)

    hip = (0.0, -0.95)
    lean = math.radians(pose.lean)
    sh = (hip[0] + math.sin(lean) * 0.55, hip[1] - math.cos(lean) * 0.55)
    neck = (sh[0] + math.sin(lean) * 0.07, sh[1] - math.cos(lean) * 0.07)
    leg_w, arm_w = 0.105 * (0.85 + 0.15 * b), 0.085 * (0.85 + 0.15 * b)
    tw = 0.17 * b

    def leg(hip_a, knee, color, back):
        p0 = (hip[0] + (-0.02 if back else 0.02), hip[1])
        j, e, r2 = _limb(canvas, p0, hip_a, 0.46, knee, 0.45, leg_w, leg_w * 0.9, color, foot=True)
        # shoe
        fx = e[0] + 0.02
        canvas.drawPath(poly([(e[0] - 0.05, e[1] - 0.03), (fx + 0.13, e[1] - 0.01), (fx + 0.14, e[1] + 0.03),
                              (e[0] - 0.06, e[1] + 0.03)]), P(c=col(C(L.shoes))))

    def arm(sh_a, el, color, back, item=""):
        p0 = (sh[0] + (-0.03 if back else 0.03), sh[1] + 0.04)
        j, e, r2 = _limb(canvas, p0, sh_a, 0.30, el, 0.27, arm_w, arm_w * 0.85, color)
        hand = (e[0] + math.sin(r2) * 0.05, e[1] + math.cos(r2) * 0.05)
        canvas.drawCircle(*hand, 0.042, P(c=col(C(L.skin))))
        if item == "cig":
            tip = (hand[0] + 0.07, hand[1] - 0.01)
            canvas.drawLine(hand[0] + 0.01, hand[1], *tip, P(c=col(C((235, 232, 224))), stroke=0.012, cap=1))
            canvas.drawCircle(*tip, 0.008, P(c=col((230, 120, 60))))
        elif item == "chalk":
            canvas.drawLine(hand[0], hand[1], hand[0] + 0.05, hand[1] - 0.03, P(c=col((240, 238, 230)), stroke=0.016, cap=1))
        elif item == "pipe":
            canvas.drawLine(hand[0], hand[1], hand[0] + 0.07, hand[1] - 0.02, P(c=col(C((60, 40, 30))), stroke=0.018, cap=1))
            canvas.drawCircle(hand[0] + 0.08, hand[1] - 0.04, 0.022, P(c=col(C((70, 46, 34)))))
        elif item == "clip":
            canvas.drawRect(skia.Rect(hand[0] - 0.02, hand[1] - 0.16, hand[0] + 0.03, hand[1] + 0.06), P(c=col(C((150, 120, 80)))))
        return hand

    # back limbs (darker)
    dark = 0.22
    leg(pose.hip_l, pose.knee_l, mix(C(L.suit_dark if not L.skirt else L.skin), (0, 0, 0), dark), True)
    arm(pose.sh_l, pose.el_l, mix(C(L.suit_dark), (0, 0, 0), dark), True)

    # torso: jacket
    tw = 0.17 * b
    jacket = poly([(hip[0] - tw * 0.95, hip[1] + 0.12), (hip[0] + tw * 1.05, hip[1] + 0.12),
                   (sh[0] + tw * 1.0, sh[1] + 0.04), (sh[0] + 0.02, sh[1] - 0.03),
                   (sh[0] - tw * 0.95, sh[1] + 0.05)])
    canvas.drawPath(jacket, P(c=col(C(L.suit))))
    # shirt/tie triangle at the front
    canvas.drawPath(poly([(sh[0] + tw * 0.55, sh[1] + 0.02), (sh[0] + tw * 0.95, sh[1] + 0.02),
                          (sh[0] + tw * 0.75, sh[1] + 0.2)]), P(c=col(C(L.shirt))))
    if rim > 0:
        canvas.drawPath(jacket, P(c=col(light, rim * 0.5), stroke=0.012))

    # front leg & arm
    leg(pose.hip_r, pose.knee_r, C(L.suit if not L.skirt else L.skin), False)
    if L.skirt or L.coat_long:
        sk = C(L.suit)
        seated = pose.hip_r > 60
        if seated:
            canvas.drawPath(poly([(hip[0] - tw, hip[1] - 0.02), (hip[0] + 0.5, hip[1] - 0.04), (hip[0] + 0.52, hip[1] + 0.1),
                                  (hip[0] - tw, hip[1] + 0.12)]), P(c=col(sk)))
        else:
            sw = 0.04 * math.sin(math.radians(pose.hip_r - pose.hip_l))
            canvas.drawPath(poly([(hip[0] - tw, hip[1] + 0.02), (hip[0] + tw, hip[1] + 0.02),
                                  (hip[0] + tw * 1.5 + sw, hip[1] + 0.55), (hip[0] - tw * 1.45 + sw, hip[1] + 0.55)]), P(c=col(sk)))

    # head
    hl = math.radians(pose.head)
    hc = (neck[0] + math.sin(lean) * 0.12 + 0.01, neck[1] - 0.12)
    canvas.drawLine(*neck, hc[0], hc[1] + 0.06, P(c=col(C(L.skin)), stroke=0.07, cap=1))
    canvas.save()
    canvas.translate(*hc)
    canvas.rotate(math.degrees(hl))
    # skull + profile (facing +x)
    nz = L.nose
    head = poly([(-0.085, -0.03), (-0.07, -0.1), (0.0, -0.125), (0.07, -0.1), (0.092, -0.04),
                 (0.095 + 0.03 * nz, 0.0), (0.09, 0.015), (0.093, 0.04), (0.082, 0.06), (0.084, 0.075),
                 (0.06, 0.1), (0.02, 0.11), (-0.04, 0.08), (-0.08, 0.03)])
    canvas.drawPath(head, P(c=col(C(L.skin))))
    canvas.drawCircle(-0.01, 0.0, 0.022, P(c=col(C(mix(L.skin, (0, 0, 0), 0.18)))))  # ear
    if ((CLOCK[0] * 0.23 + abs(x) * 0.37 + L.height) % 1.0) < 0.03:                        # blink
        canvas.drawLine(0.04, -0.025, 0.06, -0.025, P(c=col(C((30, 34, 40))), stroke=0.006))
    else:
        canvas.drawCircle(0.05, -0.025, 0.009, P(c=col(C((30, 34, 40)))))                   # eye
    if L.moustache:
        canvas.drawPath(poly([(0.06, 0.045), (0.095, 0.045), (0.09, 0.058), (0.06, 0.056)]), P(c=col(C(L.hair))))
    # hair
    canvas.drawPath(poly([(-0.088, -0.02), (-0.075, -0.1), (0.0, -0.13), (0.07, -0.105), (0.08, -0.07),
                          (0.02, -0.08), (-0.04, -0.05), (-0.06, 0.0)]), P(c=col(C(L.hair))))
    if L.hair_long:
        canvas.drawPath(poly([(-0.095, -0.06), (-0.07, -0.12), (0.02, -0.135), (0.08, -0.1), (0.09, -0.06),
                              (0.03, -0.08), (-0.02, -0.04), (-0.05, 0.06), (-0.11, 0.07), (-0.12, 0.0)]), P(c=col(C(L.hair))))
    if L.cap_military:
        canvas.drawPath(poly([(-0.09, -0.08), (0.08, -0.1), (0.1, -0.15), (-0.06, -0.17)]), P(c=col(C(L.suit_dark))))
        canvas.drawPath(poly([(0.06, -0.09), (0.16, -0.085), (0.15, -0.075), (0.06, -0.075)]), P(c=col(C((30, 28, 24)))))
    elif L.hat:
        canvas.drawPath(poly([(-0.14, -0.095), (0.15, -0.105), (0.16, -0.085), (-0.13, -0.075)]), P(c=col(C(L.hat))))   # brim
        canvas.drawPath(poly([(-0.085, -0.095), (0.085, -0.1), (0.075, -0.19), (-0.075, -0.185)]), P(c=col(C(L.hat))))  # crown
        canvas.drawPath(poly([(-0.085, -0.095), (0.085, -0.1), (0.083, -0.125), (-0.083, -0.12)]), P(c=col(C(L.hat_band))))
        canvas.drawLine(-0.06, -0.188, 0.06, -0.19, P(c=col(C(mix(L.hat, (0, 0, 0), 0.25))), stroke=0.01))
    canvas.restore()

    arm(pose.sh_r, pose.el_r, C(L.suit), False, pose.hand_r)
    canvas.restore()
    # return approximate world-space front hand for effects (smoke, chalk)
    return hc


# ------------------------------------------------------------------ scenery helpers
def pine(canvas, x, h, color):
    pts = [(x, -h)]
    tiers = 5
    for i in range(tiers):
        y = -h + (i + 1) * h * 0.78 / tiers
        w = 0.12 * h + i * 0.05 * h
        pts.append((x + w, y))
        pts.append((x + w * 0.45, y - 0.02 * h))
    pts += [(x + 0.05 * h, -0.2 * h), (x + 0.04 * h, 0), (x - 0.04 * h, 0), (x - 0.05 * h, -0.2 * h)]
    for i in reversed(range(tiers)):
        y = -h + (i + 1) * h * 0.78 / tiers
        w = 0.12 * h + i * 0.05 * h
        pts.append((x - w * 0.45, y - 0.02 * h))
        pts.append((x - w, y))
    canvas.drawPath(poly(pts), P(c=col(color)))


def ridge(rng, x0, x1, base, amp, n=80, rough=0.5):
    xs = np.linspace(x0, x1, n)
    ys = np.zeros(n)
    for octave in range(5):
        f = 2 ** octave
        ph = rng.uniform(0, 6.28)
        ys += np.sin(xs / (x1 - x0) * 6.28 * f * 1.3 + ph) * amp / f ** (1 - rough * 0.4)
    ys = base - np.abs(ys) - amp * 0.3
    return [(x0, 0)] + list(zip(xs, ys)) + [(x1, 0)]


# ------------------------------------------------------------------ 3D globe (per-pixel orthographic, shaded)
class Globe:
    def __init__(self, res=4096, ocean=(18, 30, 42), land=(78, 88, 86), coast=(150, 166, 170)):
        topo = json.loads((ASSETS / "land-50m.json").read_text())
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
        W, H = res, res // 2
        surf = skia.Surface(W, H)
        c = surf.getCanvas()
        c.clear(col(ocean))
        path = skia.Path()
        path.setFillType(skia.PathFillType.kEvenOdd)
        for g in topo["objects"]["land"]["geometries"]:
            polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
            for pl in polys:
                for ring in pl:
                    pts = []
                    for i in ring:
                        a = arcs[i] if i >= 0 else arcs[~i][::-1]
                        pts.extend(a[1:] if pts else a)
                    q = [((lo + 180) / 360 * W, (90 - la) / 180 * H) for lo, la in pts]
                    path.moveTo(*q[0])
                    for p in q[1:]:
                        path.lineTo(*p)
                    path.close()
        c.drawPath(path, P(c=col(land)))
        c.drawPath(path, P(c=col(coast, 0.8), stroke=max(1.0, res / 4096)))
        # graticule
        gp = P(c=col((255, 255, 255), 0.06), stroke=max(1.0, res / 4096))
        for lo in range(-180, 181, 15):
            x = (lo + 180) / 360 * W
            c.drawLine(x, 0, x, H, gp)
        for la in range(-75, 76, 15):
            y = (90 - la) / 180 * H
            c.drawLine(0, y, W, y, gp)
        self.tex = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3].astype(np.float32)
        self.W, self.H = W, H

    def render(self, Wpx, Hpx, cx, cy, R, lon0, lat0, light=(-0.5, -0.45, 0.74)):
        out = np.zeros((Hpx, Wpx, 4), np.uint8)
        x0, x1 = int(max(0, cx - R)), int(min(Wpx, cx + R + 1))
        y0, y1 = int(max(0, cy - R)), int(min(Hpx, cy + R + 1))
        if x1 <= x0 or y1 <= y0:
            return out
        xs = (np.arange(x0, x1) - cx + 0.5) / R
        ys = -(np.arange(y0, y1) - cy + 0.5) / R
        X, Y = np.meshgrid(xs, ys)
        rr = X * X + Y * Y
        m = rr < 1.0
        Z = np.sqrt(np.clip(1 - rr, 0, 1))
        p0, l0 = math.radians(lat0), math.radians(lon0)
        lat = np.arcsin(np.clip(Y * math.cos(p0) + Z * math.sin(p0), -1, 1))
        lon = l0 + np.arctan2(X, Z * math.cos(p0) - Y * math.sin(p0))
        u = ((np.degrees(lon) + 180) % 360) / 360 * (self.W - 1)
        v = (90 - np.degrees(lat)) / 180 * (self.H - 1)
        # bilinear sample
        u0 = np.floor(u).astype(int); v0 = np.floor(v).astype(int)
        du = (u - u0)[..., None]; dv = (v - v0)[..., None]
        u1 = np.minimum(u0 + 1, self.W - 1); v1 = np.minimum(v0 + 1, self.H - 1)
        T = self.tex
        rgb = (T[v0, u0] * (1 - du) * (1 - dv) + T[v0, u1] * du * (1 - dv) +
               T[v1, u0] * (1 - du) * dv + T[v1, u1] * du * dv)
        Lx, Ly, Lz = light
        n = math.sqrt(Lx * Lx + Ly * Ly + Lz * Lz)
        d = np.clip((X * Lx + Y * -Ly + Z * Lz) / n, 0, 1)
        shade = 0.28 + 0.82 * d ** 0.9
        rgb = rgb * shade[..., None]
        # soft limb darkening + atmosphere tint
        rim = (1 - Z) ** 3
        rgb = rgb * (1 - 0.35 * rim[..., None]) + np.array([90, 130, 170]) * (0.35 * rim[..., None])
        a = np.clip((1 - np.sqrt(rr)) * R * 1.5, 0, 1) * m
        out[y0:y1, x0:x1, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        out[y0:y1, x0:x1, 3] = (a * 255).astype(np.uint8)
        return out

    @staticmethod
    def project(lon, lat, cx, cy, R, lon0, lat0):
        p, l = math.radians(lat), math.radians(lon)
        p0, l0 = math.radians(lat0), math.radians(lon0)
        x = math.cos(p) * math.sin(l - l0)
        y = math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0)
        vis = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l - l0)
        return cx + x * R, cy - y * R, vis > 0


# ------------------------------------------------------------------ finishing
class Grain:
    def __init__(self, W, H, n=8, seed=3):
        rng = np.random.default_rng(seed)
        self.imgs = []
        for _ in range(n):
            g = rng.normal(0, 1, (H // 2, W // 2)).clip(-2.5, 2.5)
            g = ((g + 2.5) / 5 * 255).astype(np.uint8)
            self.imgs.append(skia.Image.fromarray(np.dstack([g, g, g, np.full_like(g, 255)]),
                                                  colorType=skia.kRGBA_8888_ColorType))
        self.W, self.H = W, H

    def apply(self, canvas, t, amount=0.06):
        img = self.imgs[int(t * 24) % len(self.imgs)]
        p = skia.Paint(Alphaf=amount, BlendMode=skia.BlendMode.kOverlay)
        canvas.drawImageRect(img, skia.Rect(0, 0, self.W, self.H), skia.SamplingOptions(skia.FilterMode.kLinear), p)


def vignette(canvas, W, H, strength=130):
    p = skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (W / 2, H / 2), W * 0.72, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, strength)], [0.5, 1.0]))
    canvas.drawRect(skia.Rect(0, 0, W, H), p)


def tag(canvas, W, H, s, t_alpha=0.65):
    k = H / 1080
    text(canvas, s, W - 64 * k, 52 * k, 11 * k, "mono", (200, 200, 196), t_alpha, track=0.14, align="right")


def caption(canvas, W, H, lines, a):
    """Location caption, lower-left: [(text, size, face, colour)]."""
    if a <= 0.01:
        return
    k = H / 1080
    x, y = 64 * k, H - 64 * k - sum(s for _, s, _, _ in lines) * 1.45 * k
    canvas.drawLine(x, y - 12 * k, x + 300 * k * eout(a), y - 12 * k, P(c=col((201, 164, 99), a), stroke=1.4 * k))
    prev = 0
    for i, (s, size, fc, c) in enumerate(lines):
        aa = clamp(a * 1.4 - i * 0.2)
        y += (size * 1.05 + prev * 0.45) * k
        prev = size
        text(canvas, s, x, y + (1 - aa) * 8 * k, size * k, fc, c, aa, track=0.2)


class Writer:
    def __init__(self, path, W, H, fps):
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                                   "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset",
                                   "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)

    def frame(self, surf):
        self.p.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()


# ------------------------------------------------------------------ simple synthesized score
def score(path, dur, sr=48000, root=55.0, seed=1, wind=0.25):
    """Restrained drone: detuned low strings-like pad with slow swells, plus soft wind noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(dur * sr)) / sr
    out = np.zeros((len(t), 2))
    for mult, amp in ((1, 0.5), (1.5, 0.28), (2, 0.3), (3, 0.12)):
        for det, pan in ((-0.6, 0.3), (0.0, 0.5), (0.7, 0.7)):
            f = root * mult + det
            ph = rng.uniform(0, 6.28)
            wav = np.sin(2 * np.pi * f * t + ph) + 0.3 * np.sin(4 * np.pi * f * t + ph) + 0.12 * np.sin(6 * np.pi * f * t)
            lfo = 0.6 + 0.4 * np.sin(2 * np.pi * (0.05 + rng.uniform(0, 0.04)) * t + rng.uniform(0, 6.28))
            out[:, 0] += wav * amp * lfo * (1 - pan)
            out[:, 1] += wav * amp * lfo * pan
    noise = rng.normal(0, 1, (len(t), 2))
    # one-pole low-pass for wind, slowly modulated
    from scipy.signal import lfilter
    a = 0.995
    for ch in range(2):
        y = lfilter([1 - a], [1, -a], noise[:, ch])
        out[:, ch] += y * 18 * wind * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + ch))
    env = np.minimum(1, t / 2.5) * np.minimum(1, (dur - t) / 2.0)
    out *= env[:, None]
    out /= np.abs(out).max() + 1e-9
    out *= 10 ** (-16 / 20)
    import wave
    data = (out * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(data.tobytes())
