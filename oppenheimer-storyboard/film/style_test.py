"""25-second style test: 3D globe -> Los Alamos street (2.5D walk) -> night blackboard.

python3 style_test.py [--width 1920] [--stills 2,6,11,15,19,23]
"""
import argparse, math, subprocess, sys
from pathlib import Path

import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).parent))
from engine import *  # noqa

OUT = Path(__file__).resolve().parent.parent / "renders"
FPS = 30
DUR = 25.0
GOLD = (201, 164, 99)
LOS_ALAMOS = (-106.30, 35.88)


# ====================================================================== shot A: 3D globe
class ShotGlobe:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.globe = Globe(res=8192)
        rng = np.random.default_rng(11)
        self.stars = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.4, 1.4) * H / 1080, rng.uniform(0.15, 0.6))
                      for _ in range(260)]

    def draw(self, c, t):
        W, H = self.W, self.H
        k = H / 1080
        c.clear(col((8, 12, 18)))
        bg = skia.Paint(Shader=skia.GradientShader.MakeRadial((W * 0.6, H * 0.5), W * 0.8,
                                                             [col((20, 30, 42)), col((6, 9, 14))]))
        c.drawRect(skia.Rect(0, 0, W, H), bg)
        drift = t * 4 * k
        for x, y, r, a in self.stars:
            c.drawCircle((x - drift) % W, y, r, P(c=col((220, 225, 235), a)))
        z = ease(t / 6.0)
        R = math.exp(lerp(math.log(330 * k), math.log(1050 * k), z))
        lon0 = lerp(-25, -104.5, ease(t / 5.6))
        lat0 = lerp(12, 33.2, ease(t / 5.8))
        cx, cy = W * lerp(0.56, 0.57, z), H * lerp(0.52, 0.56, z)
        # atmosphere glow behind the sphere
        glow = skia.Paint(Shader=skia.GradientShader.MakeRadial((cx, cy), R * 1.12,
                          [col((80, 130, 180), 0.0), col((80, 130, 180), 0.0), col((90, 140, 190), 0.28), col((90, 140, 190), 0)],
                          [0.0, 0.86, 0.9, 1.0]))
        c.drawCircle(cx, cy, R * 1.12, glow)
        img = self.globe.render(W, H, cx, cy, R, lon0, lat0)
        c.drawImage(skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType), 0, 0)
        # marker
        mx, my, vis = Globe.project(*LOS_ALAMOS, cx, cy, R, lon0, lat0)
        a = clamp((t - 4.6) / 0.6) * vis
        if a > 0:
            c.drawCircle(mx, my, 5 * k, P(c=col(GOLD, a)))
            c.drawCircle(mx, my, 13 * k, P(c=col(GOLD, a), stroke=1.5 * k))
            pr = clamp((t - 5.0) / 1.5)
            if 0 < pr < 1:
                c.drawCircle(mx, my, (14 + 60 * eout(pr)) * k, P(c=col(GOLD, 0.8 * (1 - pr)), stroke=1.3 * k))
            c.drawLine(mx + 14 * k, my, mx + 70 * k, my, P(c=col(GOLD, a), stroke=1.2 * k))
            text(c, "LOS ALAMOS", mx + 78 * k, my + 5 * k, 15 * k, "semi", GOLD, a, track=0.2)
        caption(c, W, H, [("LOS ALAMOS, NEW MEXICO", 34, "semi", (236, 232, 222)),
                          ("PROJECT Y · LABORATORY OPENS SPRING 1943", 16, "mono", (190, 194, 196))],
                clamp((t - 5.4) / 1.0))
        tag(c, W, H, "3D GRAPHICS · NATURAL EARTH DATA")


# ====================================================================== shot B: Los Alamos street, walking (2.5D)
class ShotStreet:
    SKY_T, SKY_B = (128, 140, 150), (184, 188, 188)
    FOG = (172, 178, 182)

    def __init__(self, W, H):
        self.W, self.H = W, H
        rng = np.random.default_rng(5)
        self.mtn = ridge(rng, -900, 900, -30, 55, 160, 0.6)       # Jemez Mountains at z=420
        self.mesa = ridge(rng, -400, 400, -12, 6, 90, 0.2)         # nearer mesa at z=160
        self.pines_far = [(x + rng.uniform(-2, 2), rng.uniform(9, 15)) for x in np.arange(-160, 160, 3.2)]
        self.pines_mid = [(x + rng.uniform(-1, 1), rng.uniform(7, 11)) for x in np.arange(-60, 60, 4.5)]
        self.smoke = rng.uniform(0, 1, (40, 3))

    def opp_x(self, t):
        return -5.6 + 1.32 * t

    def draw(self, c, t):
        W, H = self.W, self.H
        k = H / 1080
        ox = self.opp_x(t)
        cam = Cam(x=ox + 1.15, y=-1.25 - 0.06 * math.sin(t * 0.4), z=0.4, W=W, H=H)
        # sky
        sky = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 0), (0, H * 0.62)], [col(self.SKY_T), col(self.SKY_B)]))
        c.drawRect(skia.Rect(0, 0, W, H), sky)
        hz = cam.to_screen(0, 0, 2000)[1]
        # ground plane (gradient from horizon to foreground)
        gr = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, hz), (0, H)], [col((150, 148, 140)), col((96, 86, 72))]))
        c.drawRect(skia.Rect(0, hz, W, H), gr)

        def layer(z, fn):
            cam.begin(c, z); fn(); c.restore()

        layer(420, lambda: c.drawPath(poly(self.mtn), P(c=col(fog((104, 114, 124), 420, self.FOG, amount=0.55)))))
        layer(160, lambda: c.drawPath(poly(self.mesa), P(c=col(fog((96, 104, 100), 160, self.FOG, amount=0.5)))))
        layer(60, lambda: [pine(c, x, h, fog((58, 70, 58), 60, self.FOG, amount=0.55)) for x, h in self.pines_far])
        layer(26, lambda: [pine(c, x, h, fog((48, 60, 48), 26, self.FOG, amount=0.4)) for x, h in self.pines_mid])

        # water tower at z=18
        def tower():
            tc = fog((86, 84, 76), 18, self.FOG, amount=0.35)
            for lx in (-1.4, 1.4):
                c.drawLine(9 + lx, 0, 9 + lx * 0.6, -9, P(c=col(tc), stroke=0.18))
            c.drawLine(7.8, -4, 10.2, -4, P(c=col(tc), stroke=0.12))
            c.drawRect(skia.Rect(7.6, -12.5, 10.4, -9), P(c=col(tc)))
            c.drawPath(poly([(7.4, -12.5), (9, -13.8), (10.6, -12.5)]), P(c=col(tc)))
        layer(18, tower)

        # soldier walking left at z=11
        def soldier():
            sx = 6.0 - 1.1 * t
            draw_person(c, SOLDIER, walk_pose(t * 5.2), x=sx, facing=-1, fog_c=self.FOG, z=11)
        layer(11, soldier)

        # lab buildings at z=8 (Technical Area, drab green wooden two-storey)
        def buildings():
            base = fog((84, 98, 78), 17, self.FOG, amount=0.3)
            dark = mix(base, (20, 24, 22), 0.55)
            roof = mix(base, (40, 40, 40), 0.5)
            for bx in (-30, -13, 4, 21):
                w = 13
                c.drawRect(skia.Rect(bx, -6.2, bx + w, 0), P(c=col(base)))
                c.drawPath(poly([(bx - 0.4, -6.2), (bx + w / 2, -7.6), (bx + w + 0.4, -6.2)]), P(c=col(roof)))
                for row in (-5.2, -2.6):
                    for wx in np.arange(bx + 0.8, bx + w - 0.8, 1.6):
                        c.drawRect(skia.Rect(wx, row, wx + 0.9, row + 1.3), P(c=col(dark)))
                        c.drawLine(wx + 0.45, row, wx + 0.45, row + 1.3, P(c=col(base), stroke=0.06))
                c.drawRect(skia.Rect(bx + w * 0.45, -2.2, bx + w * 0.45 + 1.1, 0), P(c=col(mix(dark, base, 0.3))))
                # chimney + smoke
                chx = bx + w * 0.75
                c.drawRect(skia.Rect(chx, -8.4, chx + 0.5, -6.8), P(c=col(roof)))
                for i, (a, b, ph) in enumerate(self.smoke[:12]):
                    life = (t * 0.25 + ph) % 1.0
                    sx = chx + 0.25 + life * 3.0 + math.sin(life * 6 + i) * 0.3
                    sy = -8.6 - life * 4.0
                    c.drawCircle(sx, sy, 0.3 + life * 1.1, P(c=col((205, 208, 210), 0.22 * (1 - life)), blur=0.25))
        layer(17, buildings)

        # boardwalk + main characters at z=5
        def main():
            plank = (110, 92, 72)
            c.drawRect(skia.Rect(cam.x - 30, -0.08, cam.x + 30, 0.04), P(c=col(plank)))
            for px in np.arange(math.floor(cam.x - 30), cam.x + 30, 0.35):
                c.drawLine(px, -0.08, px, 0.04, P(c=col((80, 66, 52)), stroke=0.015))
            # scientist slightly behind (z ~5.4 drawn in same plane, darker), gesturing while walking
            sx = ox - 0.85
            pose = walk_pose(t * 5.6 + 0.6, 0.95)
            pose.sh_r = 40 + 15 * math.sin(t * 2.2); pose.el_r = 60 + 15 * math.sin(t * 3.1)
            draw_person(c, SCIENTIST, pose, x=sx, facing=1, shade=0.12)
            # Oppenheimer with clipboard
            pose = walk_pose(t * 5.5, 1.0)
            pose.sh_l = -5 + 4 * math.sin(t * 5.5); pose.el_l = 85; pose.hand_r = ""
            # turns head to listen around t=4-6
            pose.head = 2 - 6 * win(t, 3.6, 6.4, 0.6)
            draw_person(c, OPPENHEIMER_1944, pose, x=ox, facing=1, rim=0.3)
            # clipboard tucked under the back arm
            c.drawRect(skia.Rect(ox + 0.02, -1.24, ox + 0.06, -0.9), P(c=col((120, 96, 66))))
        layer(5, main)

        # ground detail: ruts, puddles and old snow at several depths (reads as a receding ground plane)
        def ground(z, items):
            def fn():
                for x0, w, colr, a in items:
                    c.drawOval(skia.Rect(x0, -0.03, x0 + w, 0.03), P(c=col(colr, a)))
            layer(z, fn)
        ground(3.2, [(x, 1.6, (70, 62, 52), 0.6) for x in np.arange(-12, 14, 5.3)])
        ground(4.1, [(x, 0.9, (150, 160, 168), 0.5) for x in np.arange(-10, 14, 6.1)])
        ground(7.0, [(x, 2.2, (226, 228, 228), 0.55) for x in np.arange(-14, 18, 7.7)])
        ground(11.0, [(x, 3.0, (220, 224, 226), 0.5) for x in np.arange(-20, 24, 9.4)])

        # foreground fence posts + wire at z=1.8, blurred
        def fence():
            fc = (40, 36, 32)
            for px in np.arange(math.floor((cam.x - 8) / 4.8) * 4.8, cam.x + 8, 4.8):
                c.drawRect(skia.Rect(px, -1.35, px + 0.09, 0.5), P(c=col(fc), blur=0.02))
        layer(1.8, fence)

        caption(c, W, H, [("LOS ALAMOS, NEW MEXICO", 34, "semi", (240, 236, 226)),
                          ("TECHNICAL AREA · 1944", 16, "mono", (220, 222, 222))], win(t, 0.8, 8.6, 0.8))
        tag(c, W, H, "2D RECONSTRUCTION")


# ====================================================================== shot C: night office, blackboard
class ShotBoard:
    WRITTEN = ["n + U-235  →  Ba-141 + Kr-92 + 3n", "E ≈ 200 MeV per fission", "implosion: ρ ↑  →  critical mass ↓"]
    NEW = "k > 1"

    def __init__(self, W, H):
        self.W, self.H = W, H
        rng = np.random.default_rng(2)
        self.stars = [(rng.uniform(-2.55, -1.65), rng.uniform(-2.35, -1.75), rng.uniform(0.004, 0.009)) for _ in range(30)]
        self.smoke = rng.uniform(0, 1, (26, 3))

    def opp(self, t):
        step = smooth((t - 4.4) / 1.0) * -0.22
        return 0.05 + step

    def draw(self, c, t):
        W, H = self.W, self.H
        cam = Cam(x=lerp(0.9, 1.15, ease(t / 8)), y=-1.55, z=lerp(-0.9, 0.5, ease(t / 8)), W=W, H=H)
        c.clear(col((22, 20, 19)))

        def layer(z, fn):
            cam.begin(c, z); fn(); c.restore()

        def wall():
            c.drawRect(skia.Rect(-8, -4, 8, 0.2), P(c=col((50, 44, 40))))
            # warm light pool from the lamp
            pool = skia.Paint(Shader=skia.GradientShader.MakeRadial((1.3, -1.9), 3.2,
                              [col((255, 200, 140), 0.32), col((255, 200, 140), 0.0)]))
            c.drawRect(skia.Rect(-8, -4, 8, 0.2), pool)
            # window with night mesa
            c.drawRect(skia.Rect(-2.62, -2.42, -1.58, -1.18), P(c=col((30, 26, 24))))
            sky = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, -2.38), (0, -1.22)], [col((14, 22, 40)), col((40, 52, 74))]))
            c.drawRect(skia.Rect(-2.56, -2.36, -1.64, -1.24), sky)
            for sx, sy, r in self.stars:
                c.drawCircle(sx, sy, r, P(c=col((230, 232, 240), 0.5 + 0.3 * math.sin(t * 2 + sx * 40))))
            c.drawPath(poly([(-2.56, -1.24), (-2.56, -1.52), (-2.3, -1.56), (-2.1, -1.5), (-1.9, -1.55), (-1.64, -1.49), (-1.64, -1.24)]),
                       P(c=col((12, 14, 18))))
            c.drawLine(-2.1, -2.36, -2.1, -1.24, P(c=col((30, 26, 24)), stroke=0.04))
            # blackboard
            c.drawRect(skia.Rect(0.32, -2.42, 4.3, -0.92), P(c=col((92, 70, 48))))
            c.drawRect(skia.Rect(0.38, -2.36, 4.24, -0.98), P(c=col((30, 40, 36))))
            smear = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0.4, -2.3), (4.2, -1.0)],
                               [col((255, 255, 255), 0.03), col((255, 255, 255), 0.07), col((255, 255, 255), 0.02)]))
            c.drawRect(skia.Rect(0.38, -2.36, 4.24, -0.98), smear)
            c.drawRect(skia.Rect(0.3, -0.98, 4.32, -0.92), P(c=col((110, 86, 60))))
            # existing equations
            font_c = (222, 224, 214)
            for i, s in enumerate(self.WRITTEN):
                c.save(); c.translate(1.3, -2.12 + i * 0.27); c.scale(0.01, 0.01)
                text(c, s, 0, 0, 13.5, "reg", font_c, 0.82)
                c.restore()
            # the new line, revealed as he writes (t 0.6-4.2)
            n = int(len(self.NEW) * clamp((t - 0.6) / 3.4) + 0.001)
            if n:
                c.save(); c.translate(0.62, -1.3); c.scale(0.011, 0.011)
                text(c, self.NEW[:n], 0, 0, 17, "med", font_c, 0.92)
                c.restore()
        layer(5.3, wall)

        def lamp():
            c.drawLine(1.3, -6, 1.3, -2.95, P(c=col((20, 18, 16)), stroke=0.012))
            c.drawPath(poly([(1.12, -2.78), (1.48, -2.78), (1.38, -2.98), (1.22, -2.98)]), P(c=col((40, 52, 44))))
            c.drawCircle(1.3, -2.76, 0.05, P(c=col((255, 226, 170)), blur=0.03))
        layer(4.0, lamp)

        def person():
            x = self.opp(t)
            writing = 1 - smooth((t - 4.2) / 0.7)
            pose = Pose(lean=4 - 6 * (1 - writing), head=-6 * writing - 10 * win(t, 4.8, 8.5, 0.8))
            pose.hip_l, pose.hip_r, pose.knee_l, pose.knee_r = -6, 8, 6, 4
            # front arm: raised to the board while writing, small hand motion
            wob = math.sin(t * 9) * 3 * writing
            pose.sh_r = lerp(10, 112 + wob, writing)
            pose.el_r = lerp(14, 22 + math.sin(t * 7) * 4 * writing, writing)
            pose.hand_r = "chalk" if writing > 0.2 else ""
            # back arm: cigarette, raised to the mouth after writing
            lift = win(t, 5.6, 7.4, 0.5)
            pose.sh_l = lerp(-4, 70, lift)
            pose.el_l = lerp(30, 128, lift)
            draw_person(c, OPPENHEIMER_1944, pose, x=x, facing=1, rim=0.65, light=(255, 210, 160))
            # smoke after the drag
            for i, (a, b, ph) in enumerate(self.smoke):
                life = (t - 6.8 - ph * 1.2) / 2.2
                if 0 < life < 1:
                    sx = x + 0.2 + life * 0.5 + math.sin(life * 5 + i) * 0.06
                    sy = -1.74 - life * 0.9
                    c.drawCircle(sx, sy, 0.03 + life * 0.14, P(c=col((210, 210, 214), 0.16 * (1 - life)), blur=0.04))
        layer(4.85, person)

        def desk():
            c.drawRect(skia.Rect(-3, -0.82, 3.2, 0.5), P(c=col((54, 38, 28)), blur=0.015))
            c.drawRect(skia.Rect(-3, -0.86, 3.2, -0.8), P(c=col((84, 60, 42)), blur=0.015))
            for px, w, rot in ((-0.6, 0.42, -6), (0.1, 0.38, 4), (0.55, 0.4, -2)):
                c.save(); c.translate(px, -0.86); c.rotate(rot)
                c.drawRect(skia.Rect(0, -0.012, w, 0.0), P(c=col((210, 204, 188)), blur=0.01))
                c.restore()
            c.drawRect(skia.Rect(1.4, -0.98, 1.7, -0.86), P(c=col((90, 40, 36)), blur=0.015))   # books
            c.drawRect(skia.Rect(1.42, -1.08, 1.68, -0.98), P(c=col((40, 52, 70)), blur=0.015))
            c.drawPath(poly([(-1.3, -0.86), (-1.05, -0.86), (-1.08, -0.9), (-1.27, -0.9)]), P(c=col((120, 120, 118)), blur=0.01))
        layer(2.1, desk)

        caption(c, W, H, [("DIRECTOR'S OFFICE, LOS ALAMOS", 30, "semi", (240, 232, 218)),
                          ("NIGHT · 1945", 16, "mono", (210, 200, 186))], win(t, 1.0, 7.6, 0.8))
        tag(c, W, H, "2D RECONSTRUCTION")


# ====================================================================== assemble
SHOTS = [(0.0, 8.0, ShotGlobe), (8.0, 17.0, ShotStreet), (17.0, 25.0, ShotBoard)]
XF = 0.6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--stills", default="")
    a = ap.parse_args()
    W = a.width; H = W * 9 // 16
    shots = [(t0, t1, cls(W, H)) for t0, t1, cls in SHOTS]
    grain = Grain(W, H)
    surf = skia.Surface(W, H)
    c = surf.getCanvas()

    def frame(t):
        active = [(t0, t1, s) for t0, t1, s in shots if t0 - XF <= t < t1 + XF]
        first = True
        for t0, t1, s in active:
            local = t - t0
            if first:
                s.draw(c, max(0.0, local)); first = False
            else:
                alpha = clamp((t - (t0 - XF)) / (2 * XF))
                c.saveLayerAlpha(None, int(255 * alpha))
                s.draw(c, max(0.0, local))
                c.restore()
        vignette(c, W, H, 120)
        grain.apply(c, t, 0.07)
        if t < 0.8:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * (1 - t / 0.8)))))
        if t > DUR - 0.8:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * (t - DUR + 0.8) / 0.8))))

    OUT.mkdir(exist_ok=True)
    if a.stills:
        for s in a.stills.split(","):
            frame(float(s))
            p = OUT / f"test_{float(s):05.1f}.png"
            surf.makeImageSnapshot().save(str(p), skia.kPNG)
            print(p)
        return
    vid = OUT / "_style_test_video.mp4"
    w = Writer(vid, W, H, FPS)
    for i in range(int(DUR * FPS)):
        frame(i / FPS)
        w.frame(surf)
    w.close()
    wav = OUT / "_style_test.wav"
    score(wav, DUR, root=55.0)
    final = OUT / "style_test_2d3d.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-i", str(wav), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    vid.unlink(); wav.unlink()
    print(final)


if __name__ == "__main__":
    main()
