"""Scenes 9-12 (shots 92-147): Hiroshima, Nagasaki and surrender, Cold War and hearing, legacy."""
import math
import sys
from pathlib import Path

import numpy as np
import skia

from engine import *  # noqa
from env import *  # noqa
from kit import *  # noqa
from reg import shot, Stage, track
from shots_a import mv, ping, globe_scene, smoke_puffs, _G
from shots_b import card, tag2d, snow

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "graphics"))
import hiroshima_map as HM  # noqa

MONO, CW, DARK = PAL["mono"], PAL["coldwar"], PAL["dark"]
JAPAN = "+proj=lcc +lat_1=30 +lat_2=40 +lat_0=35 +lon_0=135 +datum=WGS84"
HIRO = (132.4536, 34.3955)
NAGA = (129.8636, 32.7736)
ENOLA = dict(name="ENOLA GAY", number="82", tail="R")


def hm_frame(c, W, H, t):
    key = ("hm", W)
    if key not in _G:
        _G[key] = (HM.build_path(HM.load_land()), HM.make_grain(W, H))
    land, grain = _G[key]
    HM.draw(c, t, W, H, land, grain)


def sky_air(c, W, H, t, top=(70, 96, 130), bot=(190, 200, 206), clouds_y=0.72, speed=1.0, seed=3):
    sky(c, W, H, top, bot, horizon=0.7)
    k = K(H)
    rng = np.random.default_rng(seed)
    for layer in range(3):
        y = H * (clouds_y + layer * 0.08)
        sp = (120 + layer * 170) * k * speed
        for i in range(18):
            x = (rng.uniform(0, W * 1.4) - t * sp) % (W * 1.4) - W * 0.2
            r = rng.uniform(40, 110) * k * (1 + layer * 0.4)
            c.drawOval(skia.Rect(x - r * 1.8, y - r * 0.35, x + r * 1.8, y + r * 0.35), P(c=col((236, 238, 240), 0.55 + layer * 0.12), blur=r * 0.2))
    # high thin cirrus drifting the other way for parallax
    for i in range(8):
        x = (rng.uniform(0, W * 1.6) - t * 30 * k * speed) % (W * 1.6) - W * 0.3
        y = H * rng.uniform(0.08, 0.4)
        r = rng.uniform(120, 260) * k
        c.drawOval(skia.Rect(x - r * 2.2, y - r * 0.08, x + r * 2.2, y + r * 0.08), P(c=col((240, 244, 248), 0.18), blur=r * 0.15))


def little_boy(c, x, y, s=1.0, colr=(70, 74, 66)):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-1.5, -0.36, 1.2, 0.36), 0.3, 0.3, P(c=col(colr)))
    c.drawRect(skia.Rect(-1.95, -0.4, -1.45, 0.4), P(c=col(mix(colr, (0, 0, 0), 0.2))))
    c.drawCircle(1.15, 0, 0.36, P(c=col(colr)))
    c.restore()


def fat_man(c, x, y, s=1.0, colr=(176, 160, 96)):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect(-1.0, -0.76, 1.1, 0.76), P(c=col(colr)))
    c.drawRect(skia.Rect(-1.75, -0.7, -0.95, 0.7), P(c=col(mix(colr, (0, 0, 0), 0.25))))
    for yy in (-0.35, 0.35):
        c.drawLine(-0.9, yy, 1.0, yy, P(c=col((40, 34, 24), 0.6), stroke=0.04))
    c.restore()


def mono_layer(c, W, H, a=0.35):
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(128, 128, 128, int(255 * a)), BlendMode=skia.BlendMode.kSaturation))


# =========================================================== SCENE 9
@shot(92)
def s92(c, t, d, W, H):
    m = mv("pac", "+proj=lcc +lat_1=12 +lat_2=30 +lat_0=22 +lon_0=140 +datum=WGS84", (120, 5, 160, 40), "land-10m.json")
    z = ease((t - 0.5) / 4.0)
    draw_map(c, W, H, m, (lerp(140, 145.6, z), lerp(22, 15.0, z)), math.exp(lerp(math.log(4200), math.log(260), z)), MONO, grat=5,
             markers=[(144.79, 13.44, "GUAM", ping(t, 1.2), "dot", (12, 4)), (145.75, 15.18, "SAIPAN", ping(t, 1.2), "dot", (12, -8)),
                      (145.63, 14.99, "TINIAN", ping(t, 3.8), "key", (-14, 16)), (141.32, 24.78, "IWO JIMA", ping(t, 0.8) * (1 - z), "dot", (12, -8)),
                      (135.5, 34.7, "JAPAN", (1 - z), "dot", (12, -8))])
    location_card(c, W, H, [("TINIAN, NORTHERN MARIANA ISLANDS", 26, "semi", "fg"), ("NORTH FIELD · 509th COMPOSITE GROUP", 16, "mono", "fg"),
                            ("26 July 1945 — USS Indianapolis delivers Little Boy components", 16, "reg", "accent")], clamp((t - 4.4) / 0.8), MONO)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", MONO)


@shot(93)
def s93(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -0.8, 0.8), y=-0.9, z=track(t, d, -0.6, 0.6))
    c.clear(col((14, 16, 18)))
    with st.at(5):
        c.drawRect(skia.Rect(-8, -0.6, 8, 0.4), P(c=col((90, 88, 84))))
        c.drawRect(skia.Rect(-3, -0.6, 3, 1.8), P(c=col((40, 40, 40))))
        c.drawCircle(0, -4, 3.5, P(c=col((255, 255, 240), 0.12), blur=1.5))
        c.drawRect(skia.Rect(-1.4, 0.0, 1.4, 0.15), P(c=col((60, 60, 58))))
        little_boy(c, 0, -0.35, 1.0)
        for i, x in enumerate((-4.0, -2.6, 2.8, 4.0)):
            draw_person(c, [CREW, SOLDIER, PARSONS, CREW][i], idle(stand(head=12, sh_r=30, el_r=60), t, i, 0.6), x=x, facing=1 if x < 0 else -1, z=5)
    mono_layer(c, W, H, 0.6)
    card(c, W, H, t, d, MONO, "LITTLE BOY · URANIUM-235, GUN-TYPE", "BOMB LOADING PIT, NORTH FIELD, TINIAN · 5 AUGUST 1945")
    tag2d(c, W, H, MONO)


@shot(94)
def s94(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -2, 2), y=track(t, d, -8, -1.8), z=-6)
    c.clear(col((8, 9, 12)))
    stars(c, W, H, t, n=120, top=0.5, a=0.5)
    ground(c, W, H, st.cam, (40, 40, 38), (60, 60, 58))
    with st.at(60):
        for x in (-40, 50):
            b29(c, x, -4, 0.8, t, shade=0.6)
        for x in np.arange(-80, 80, 9):
            c.drawLine(x, 0, x + 1.5, -12, P(c=col((10, 12, 10)), stroke=0.6))
            c.drawCircle(x + 1.5, -12, 3, P(c=col((10, 12, 10))))
    with st.at(22):
        c.drawCircle(-6, -14, 14, P(c=col((255, 250, 230), 0.12), blur=5))
        b29(c, 0, -4.4, 1.0, t * 0.0, **ENOLA)
    with st.at(8):
        for i, x in enumerate(np.arange(-5, 5, 1.1)):
            draw_person(c, [CREW, CREW, TIBBETS, CREW][i % 4], idle(stand(), t, i, 0.6), x=x, facing=1, z=8)
        for i, x in enumerate((-7.5, 6.8)):
            flash = 1.0 if (t * 1.3 + i * 0.5) % 1.6 < 0.08 else 0.0
            draw_person(c, OFFICIAL, stand(sh_r=100, el_r=80), x=x, facing=1 if x < 0 else -1, z=8)
            c.drawCircle(x + (0.5 if x < 0 else -0.5), -1.7, 0.4, P(c=col((255, 255, 255), flash), blur=0.2))
    mono_layer(c, W, H, 0.5)
    card(c, W, H, t, d, MONO, "NORTH FIELD, TINIAN", "6 AUGUST 1945, AFTER MIDNIGHT")
    tag2d(c, W, H, MONO)


@shot(95)
def s95(c, t, d, W, H):
    st = Stage(c, W, H, x=11.6, y=-1.0, z=track(t, d, -8, -6.4))
    c.clear(col((12, 13, 16)))
    c.drawCircle(W * 0.3, H * 0.2, W * 0.4, P(c=col((255, 250, 230), 0.08), blur=80))
    with st.at(4):
        b29(c, 0, 0, 1.0, 0, **ENOLA)
        c.drawRect(skia.Rect(11.0, -1.44, 11.9, -1.0), P(c=col((40, 50, 60))))
        c.drawCircle(11.38, -1.18, 0.13, P(c=col((196, 168, 146))))
        c.drawPath(poly([(11.25, -1.24), (11.3, -1.33), (11.46, -1.33), (11.5, -1.26), (11.36, -1.28)]), P(c=col((44, 38, 34))))
        c.drawCircle(11.44, -1.2, 0.015, P(c=col((30, 30, 30))))
        wv = math.sin(t * 6) * 0.08
        c.drawLine(11.55, -1.04, 11.85 + wv, -1.55, P(c=col((120, 120, 96)), stroke=0.06, cap=1))
        c.drawCircle(11.87 + wv, -1.6, 0.05, P(c=col((196, 168, 146))))
    mono_layer(c, W, H, 0.6)
    location_card(c, W, H, [("COL. PAUL W. TIBBETS JR.", 28, "semi", "fg"), ("PILOT · COMMANDER, 509th COMPOSITE GROUP", 16, "mono", "fg")],
                  win(t, 0.5, d - 0.2, 0.6), MONO)
    tag2d(c, W, H, MONO)


@shot(96)
def s96(c, t, d, W, H):
    x = -40 + 2.0 * t ** 2.1
    lift = max(0.0, (t - 3.4)) ** 1.8 * 0.9
    st = Stage(c, W, H, x=x * 0.55, y=-3 - lift * 0.4, z=-10)
    c.clear(col((6, 7, 10)))
    stars(c, W, H, t, n=100, top=0.5, a=0.4)
    with st.at(40):
        c.drawRect(skia.Rect(-400, -0.2, 400, 4), P(c=col((24, 24, 24))))
        for rx in np.arange(-200, 200, 6):
            c.drawCircle(rx, -0.1, 0.25, P(c=col((255, 230, 180), 0.8)))
        b29(c, x, -4.4 - lift, 0.9, t * 3, bank=-min(6, lift * 2), **ENOLA)
        for nx in (5.4, 2.4):
            c.drawCircle(x + nx * 0.9 - 3.2, -4.4 - lift + 0.8, 1.2, P(c=col((255, 160, 80), 0.35), blur=0.6))
    mono_layer(c, W, H, 0.4)
    card(c, W, H, t, d, MONO, "TAKEOFF", "2:45 AM (TINIAN TIME), 6 AUGUST 1945")
    tag2d(c, W, H, MONO)


@shot(97)
def s97(c, t, d, W, H):
    st = Stage(c, W, H, x=0.4, y=-1.1, z=track(t, d, -0.6, 0.6))
    c.clear(col((6, 6, 8)))
    shake = math.sin(t * 40) * 0.004
    with st.at(4 + shake):
        for x in np.arange(-5, 5, 0.8):
            c.drawLine(x, -3, x, 1, P(c=col((30, 32, 34)), stroke=0.05))
        c.save(); c.clipPath(poly([(-0.9, -2.0), (2.8, -0.2), (2.8, 0.6), (-0.9, -1.2)]))
        c.drawRect(skia.Rect(-5, -4, 5, 2), P(c=col((255, 240, 200), 0.16)))
        little_boy(c, 1.2, -0.9, 1.0, colr=(110, 112, 104))
        c.restore()
        little_boy(c, 1.2, -0.9, 1.0, colr=(26, 28, 26))
        c.save(); c.clipPath(poly([(-0.9, -2.0), (2.8, -0.2), (2.8, 0.6), (-0.9, -1.2)]))
        little_boy(c, 1.2, -0.9, 1.0, colr=(100, 102, 96))
        c.restore()
        p = Pose(lean=40, hip_l=70, hip_r=80, knee_l=110, knee_r=100, sh_r=70 + 6 * math.sin(t * 5), el_r=40, sh_l=50, el_l=60, bob=0.4, head=20)
        draw_person(c, PARSONS, p, x=-0.5, facing=1, z=4)
        p2 = Pose(lean=30, hip_l=60, hip_r=60, knee_l=100, knee_r=100, sh_r=60, el_r=40, bob=0.36, head=14)
        draw_person(c, CREW, p2, x=-1.4, facing=1, z=4, shade=0.4)
        c.drawRect(skia.Rect(-0.95, -1.55, -0.75, -1.45), P(c=col((90, 90, 90))))
    location_card(c, W, H, [("CAPT. WILLIAM S. PARSONS, U.S. NAVY", 26, "semi", "fg"), ("WEAPONEER · COMPLETES ARMING IN FLIGHT", 16, "mono", "fg")],
                  win(t, 0.5, d - 0.2, 0.6), MONO)
    tag2d(c, W, H, MONO)


@shot(98)
def s98(c, t, d, W, H):
    m = mv("pac", "+proj=lcc +lat_1=12 +lat_2=30 +lat_0=22 +lon_0=140 +datum=WGS84", (120, 5, 160, 40), "land-10m.json")
    draw_map(c, W, H, m, (track(t, d, 139.5, 138.5), track(t, d, 24.2, 24.8)), track(t, d, 4800, 4500), MONO, grat=5,
             routes=[([(145.63, 14.99), (141.32, 24.78)], clamp((t - 0.6) / 2.2), MONO["accent"]),
                     ([(141.32, 24.78), (132.45, 34.4)], clamp((t - 3.2) / 2.6), MONO["accent"])],
             markers=[(145.63, 14.99, "TINIAN — TAKEOFF 2:45 AM (TINIAN TIME)", 1.0, "key", (14, 6)),
                      (141.32, 24.78, "IWO JIMA — RENDEZVOUS", ping(t, 2.6), "dot", (14, 6)),
                      (132.45, 34.4, "HIROSHIMA", ping(t, 5.6), "target", (-14, -12))])
    text(c, "schematic route · Tinian time was one hour ahead of Japan", 64 * K(H), H - 64 * K(H), 15 * K(H), "mono", MONO["muted"], clamp((t - 1) / 0.8))
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", MONO)


@shot(99)
def s99(c, t, d, W, H):
    hm_frame(c, W, H, t * 8.0 / d)


@shot(100)
def s100(c, t, d, W, H):
    hm_frame(c, W, H, 8.0 + t * 14.0 / d)


def aerial(c, W, H, t, a=1.0, scale=1.0, center_off=(0, 0)):
    """Stylised aerial plate of the Hiroshima delta region built on the 10m coastline."""
    m = mv("jp10", JAPAN, (128, 30, 136, 37), "land-10m.json")
    mat, mpx = m.view(W, H, (HIRO[0] + center_off[0], HIRO[1] + center_off[1]), 60 / scale)
    c.saveLayerAlpha(None, int(255 * a))
    c.clear(col((86, 104, 112)))
    lp = skia.Path(m.land); lp.transform(mat)
    c.drawPath(lp, P(c=col((110, 116, 96))))
    rng = np.random.default_rng(1)
    c.save(); c.clipPath(lp)
    for i in range(500):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        c.drawCircle(x, y, rng.uniform(4, 30) * K(H), P(c=col(mix((110, 116, 96), (70, 80, 64), rng.uniform()), 0.4), blur=6 * K(H)))
    hp = m.S(mat, *HIRO)
    for i in range(300):
        r = abs(rng.normal(0, 1)) * 60 * K(H) * scale
        ang = rng.uniform(0, 6.28)
        c.drawRect(skia.Rect(hp.x() + math.cos(ang) * r, hp.y() + math.sin(ang) * r, hp.x() + math.cos(ang) * r + 4 * K(H),
                             hp.y() + math.sin(ang) * r + 3 * K(H)), P(c=col((150, 146, 136), 0.6)))
    c.restore()
    c.drawPath(lp, P(c=col((170, 176, 170), 0.5), stroke=1.2 * K(H)))
    for i in range(14):
        x = (rng.uniform(0, W * 1.3) - t * 25 * K(H)) % (W * 1.3) - W * 0.15
        y = rng.uniform(0, H)
        r = rng.uniform(40, 120) * K(H)
        c.drawOval(skia.Rect(x - r * 1.6, y - r * 0.6, x + r * 1.6, y + r * 0.6), P(c=col((240, 242, 244), 0.5), blur=r * 0.35))
    c.drawRect(skia.Rect(0, 0, W, H), P(c=col((200, 210, 220), 0.18)))
    c.restore()
    return hp


@shot(101)
def s101(c, t, d, W, H):
    hm_frame(c, W, H, 22.0)
    a = smooth((t - 0.6) / 2.4)
    if a > 0:
        aerial(c, W, H, t, a, scale=lerp(1.0, 1.25, t / d))
    mono_layer(c, W, H, 0.4 * a)
    if a > 0.5:
        tag2d(c, W, H, MONO)


@shot(102)
def s102(c, t, d, W, H):
    k = K(H)
    sky_air(c, W, H, t, clouds_y=0.76)
    st = Stage(c, W, H, x=track(t, d, -2, 4), y=-1, z=-40)
    with st.at(220):
        b29(c, -60 + t * 0.6, -6, 1.0, t, shade=0.1)
        b29(c, -95 + t * 0.6, 4, 1.0, t, shade=0.15)
    with st.at(10):
        b29(c, 0, math.sin(t * 0.7) * 0.3, 1.0, t, **ENOLA)
    mono_layer(c, W, H, 0.45)
    location_card(c, W, H, [("ENOLA GAY · B-29 SUPERFORTRESS", 26, "semi", "fg"), ("ABOUT 31,000 FT · WITH THE GREAT ARTISTE AND NECESSARY EVIL", 15, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), MONO)
    tag2d(c, W, H, MONO)


@shot(103)
def s103(c, t, d, W, H):
    sky_air(c, W, H, t, clouds_y=0.85, speed=0.6)
    st = Stage(c, W, H, x=track(t, d, 13.5, 9.0), y=-0.5, z=-2.4)
    with st.at(4):
        b29(c, 0, math.sin(t * 0.8) * 0.05, 1.0, t, **ENOLA)
    mono_layer(c, W, H, 0.45)
    tag2d(c, W, H, MONO)


@shot(104)
def s104(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, 0.0, 1.0), y=-1.1, z=track(t, d, -0.6, 0.4))
    c.clear(col((150, 170, 190)))
    with st.at(3.6):
        c.drawRect(skia.Rect(-6, -3, 6, -2.2), P(c=col((40, 42, 44))))
        c.drawRect(skia.Rect(-6, -0.5, 6, 1), P(c=col((40, 42, 44))))
        for x in np.arange(-6, 6, 0.9):
            c.drawLine(x, -2.2, x + 0.3, -0.5, P(c=col((40, 42, 44)), stroke=0.06))
        c.drawRect(skia.Rect(-2.6, -0.95, 0.4, -0.55), P(c=col((30, 30, 32))))
        for i in range(8):
            c.drawCircle(-2.3 + i * 0.36, -0.75, 0.1, P(c=col((220, 214, 196))))
        for i, (L, x) in enumerate(((TIBBETS, -2.0), (CREW, -0.6))):
            p = sit(sh_r=70 + 3 * math.sin(t * 2 + i), el_r=50, head=-2, lean=4, bob=0.4)
            draw_person(c, L, p, x=x, facing=1, z=3.6)
        p = Pose(lean=50, hip_l=60, hip_r=60, knee_l=90, knee_r=90, sh_r=90 + 5 * math.sin(t * 3), el_r=30, bob=0.36, head=30)
        draw_person(c, CREW, p, x=2.4, facing=1, z=3.6)
        c.drawRect(skia.Rect(2.95, -1.0, 3.3, -0.6), P(c=col((40, 40, 40))))
    mono_layer(c, W, H, 0.5)
    location_card(c, W, H, [("IN THE COCKPIT, 8:10 AM", 26, "semi", "fg"), ("TIBBETS AND LEWIS · BOMBARDIER THOMAS FEREBEE AT THE NORDEN BOMBSIGHT", 15, "mono", "fg")],
                  win(t, 0.5, d - 0.2, 0.6), MONO)
    tag2d(c, W, H, MONO)


def dome_building(c, x, colr=(170, 160, 146)):
    c.drawRect(skia.Rect(x - 12, -9, x + 12, 0), P(c=col(colr)))
    for xx in np.arange(x - 11, x + 11, 1.6):
        for yy in (-8, -5.2, -2.6):
            c.drawRect(skia.Rect(xx, yy, xx + 0.8, yy + 1.6), P(c=col(mix(colr, (30, 30, 30), 0.6))))
    c.drawRect(skia.Rect(x - 3, -15, x + 3, -9), P(c=col(mix(colr, (255, 255, 255), 0.08))))
    c.drawOval(skia.Rect(x - 3.2, -20.5, x + 3.2, -13.5), P(c=col((100, 130, 116))))
    c.drawRect(skia.Rect(x - 3.4, -15.2, x + 3.4, -14.6), P(c=col(colr)))


@shot(105)
def s105(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -4, 2), y=-1.6, z=0.0)
    sky(c, W, H, (150, 176, 200), (226, 230, 230))
    ground(c, W, H, st.cam, (120, 116, 110), (160, 158, 150))
    with st.at(70):
        dome_building(c, 6)
    with st.at(40):
        c.drawRect(skia.Rect(-300, -0.6, 300, 1.2), P(c=col((120, 146, 156))))
    with st.at(16):
        for bx in np.arange(-40, 40, 6.5):
            c.drawRect(skia.Rect(bx, -3.4, bx + 6, 0), P(c=col((120, 100, 80))))
            c.drawPath(poly([(bx - 0.4, -3.4), (bx + 3, -4.8), (bx + 6.4, -3.4)]), P(c=col((60, 60, 66))))
    with st.at(9):
        tx = 20 - t * 4
        c.drawRoundRect(skia.Rect(tx - 5, -3.0, tx + 5, -0.4), 0.4, 0.4, P(c=col((70, 100, 80))))
        for wx in np.arange(tx - 4.4, tx + 4.4, 1.2):
            c.drawRect(skia.Rect(wx, -2.6, wx + 0.8, -1.6), P(c=col((200, 210, 210))))
        c.drawLine(-60, -5.4, 60, -5.4, P(c=col((40, 40, 40)), stroke=0.03))
        c.drawLine(tx, -3.0, tx + 1, -5.4, P(c=col((40, 40, 40)), stroke=0.05))
        for wx in (tx - 3.5, tx + 3.5):
            c.drawCircle(wx, -0.3, 0.35, P(c=col((30, 30, 30))))
    with st.at(5):
        for i in range(5):
            xx = -6 + i * 0.7 + t * 1.0
            draw_person(c, JP_STUDENT, walk_pose(t * 6 + i, 0.8), x=xx, facing=1, z=5)
        draw_person(c, JP_MAN, walk_pose(t * 5.2, 0.9), x=4 - t * 1.0, facing=-1, z=5)
        draw_person(c, JP_WOMAN, walk_pose(t * 4.8 + 1, 0.8), x=6 - t * 0.9, facing=-1, z=5)
        bicycle(c, -10 + t * 3.0, t, JP_MAN)
    mono_layer(c, W, H, 0.55)
    card(c, W, H, t, d, MONO, "HIROSHIMA", "8:00 AM, 6 AUGUST 1945")
    tag2d(c, W, H, MONO)


def bicycle(c, x, t, look, facing=1):
    c.save(); c.translate(x, 0); c.scale(facing, 1)
    for wx in (-0.55, 0.55):
        c.drawCircle(wx, -0.34, 0.34, P(c=col((30, 30, 30)), stroke=0.03))
    c.drawPath(poly([(-0.55, -0.34), (-0.1, -0.34), (0.1, -0.8), (0.55, -0.34)], close=False), P(c=col((40, 40, 40)), stroke=0.03))
    c.restore()
    p = Pose(hip_l=70 + 25 * math.sin(t * 5), hip_r=70 - 25 * math.sin(t * 5), knee_l=70, knee_r=70, sh_r=60, el_r=20, sh_l=55, el_l=20, bob=0.05, lean=14)
    draw_person(c, look, p, x=x - 0.1 * facing, facing=facing)


@shot(106)
def s106(c, t, d, W, H):
    k = K(H)
    off = (lerp(-0.05, 0.0, ease(t / (d * 0.8))), lerp(0.04, 0.0, ease(t / (d * 0.8))))
    c.clear(col((0, 0, 0)))
    c.save()
    path = skia.Path(); path.addCircle(W / 2, H / 2, H * 0.42)
    c.clipPath(path, doAntiAlias=True)
    hp = aerial(c, W, H, t, 1.0, scale=2.0, center_off=off)
    c.restore()
    c.drawCircle(W / 2, H / 2, H * 0.42, P(c=col((0, 0, 0)), stroke=12 * k))
    c.drawCircle(W / 2, H / 2, H * 0.44, P(c=col((0, 0, 0), 0.8), blur=30 * k, stroke=40 * k))
    cp = P(c=col((20, 20, 20), 0.85), stroke=1.6 * k)
    c.drawLine(W / 2 - H * 0.4, H / 2, W / 2 + H * 0.4, H / 2, cp)
    c.drawLine(W / 2, H / 2 - H * 0.4, W / 2, H / 2 + H * 0.4, cp)
    mono_layer(c, W, H, 0.5)
    text(c, "AIMING POINT: AIOI BRIDGE", W / 2 + H * 0.46, H * 0.85, 15 * k, "mono", MONO["fg"], clamp((t - 1) / 0.6), track=0.1)
    tag2d(c, W, H, MONO)


@shot(107)
def s107(c, t, d, W, H):
    sky_air(c, W, H, t, top=(60, 86, 120), bot=(170, 186, 196), clouds_y=0.86)
    st = Stage(c, W, H, x=1.0, y=1.2, z=-30)
    doors = smooth(t / 0.8)
    rel = 1.2
    with st.at(10):
        b29(c, t * 0.4, math.sin(t) * 0.2 - 0.3 * smooth((t - rel) / 0.6), 1.0, t, doors=doors, **ENOLA)
        if t > rel:
            u = t - rel
            bx = 1.5 + t * 0.4 - u * 1.2
            by = 1.6 + 4.9 * u * u
            c.save(); c.translate(bx, by); c.rotate(min(70, u * 30) + math.sin(u * 6) * 3 * math.exp(-u))
            little_boy(c, 0, 0, 0.75, colr=(60, 62, 58))
            c.restore()
    mono_layer(c, W, H, 0.45)
    text(c, "8:15 AM", W - 64 * K(H), H - 70 * K(H), 40 * K(H), "monom", MONO["accent"], clamp((t - rel) / 0.4), align="right")
    tag2d(c, W, H, MONO)


@shot(108)
def s108(c, t, d, W, H):
    k = K(H)
    aerial(c, W, H, t, 1.0, scale=1.2)
    mono_layer(c, W, H, 0.7)
    c.drawRect(skia.Rect(0, 0, W, H), P(c=col((0, 0, 0), 0.55)))
    x = W * 0.72
    top, bot = H * 0.14, H * 0.86
    c.drawLine(x, top, x, bot, P(c=col(MONO["fg"], 0.7), stroke=1.6 * k))
    det_y = lerp(bot, top, 600 / 9400)
    for yy, lab in ((top, "31,000 FT · ABOUT 9,400 M — RELEASE"), (det_y, "ABOUT 600 M — DETONATION")):
        c.drawLine(x - 10 * k, yy, x + 10 * k, yy, P(c=col(MONO["fg"]), stroke=1.6 * k))
        text(c, lab, x + 20 * k, yy + 6 * k, 16 * k, "mono", MONO["fg"], 0.9, track=0.06)
    u = clamp((t - 0.4) / (d - 1.2))
    c.drawCircle(x, lerp(top, det_y, u * u), 7 * k, P(c=col(MONO["accent"])))
    text(c, f"{43 * u:4.1f} s", x - 30 * k, lerp(top, det_y, u * u) + 6 * k, 18 * k, "monom", MONO["accent"], 1, align="right")
    location_card(c, W, H, [("8:15 AM LOCAL TIME", 30, "semi", "fg"), ("Fall time about 43 seconds", 18, "reg", "accent"),
                            ("Source: U.S. Strategic Bombing Survey, 1946", 14, "mono", "muted")], clamp((t - 0.4) / 0.8), MONO)
    small_tag(c, W, H, "GRAPHICS", MONO)


@shot(109)
def s109(c, t, d, W, H):
    sky_air(c, W, H, t, clouds_y=0.8)
    st = Stage(c, W, H, x=0, y=0, z=track(t, d, -40, -70))
    bank = lerp(0, 55, smooth(t / 1.6))
    with st.at(10):
        b29(c, -t * 3.0, t * 1.4, lerp(1.0, 0.7, t / d), t, bank=bank, facing=-1 if t > 1.8 else 1, **ENOLA)
    mono_layer(c, W, H, 0.45)
    card(c, W, H, t, d, MONO, "A STEEP DIVING TURN OF ABOUT 155°", "AWAY FROM THE CITY")
    tag2d(c, W, H, MONO)


@shot(110)
def s110(c, t, d, W, H):
    ok = photo_shot(c, t, d, W, H, "Atomic_bombing_of_Japan.jpg", MONO, "U.S. AIR FORCE / NATIONAL ARCHIVES",
                    crop=(0.0, 0.0, 0.5, 1.0), start=(0.5, 0.55, 1.0), end=(0.5, 0.45, 1.1), fit="contain")
    location_card(c, W, H, [("HIROSHIMA", 30, "semi", "fg"), ("6 AUGUST 1945 · 8:15 AM LOCAL TIME", 20, "med", "fg")], clamp((t - 0.8) / 0.8), MONO)


def ruins(c, st, t, kind="dome"):
    with st.at(80):
        rng = np.random.default_rng(4)
        for x in np.arange(-120, 120, 2.0):
            h = rng.uniform(0.2, 2.0)
            c.drawRect(skia.Rect(x, -h, x + rng.uniform(0.8, 2.0), 0), P(c=col((110, 108, 104))))
    if kind == "dome":
        with st.at(40):
            x = 2
            c.drawRect(skia.Rect(x - 10, -6, x - 4, 0), P(c=col((90, 88, 84))))
            c.drawPath(poly([(x - 4, 0), (x - 4, -9), (x - 2.6, -10), (x - 3, -14), (x - 2.2, -15), (x + 2.2, -15), (x + 3, -14), (x + 2.6, -10), (x + 4, -9), (x + 6, -5), (x + 8, -4), (x + 8, 0)]),
                       P(c=col((96, 94, 90))))
            for i in range(9):
                ang = math.pi + i / 8 * math.pi
                c.drawLine(x, -15, x + math.cos(ang) * 3.2, -15 + math.sin(ang) * 4.2, P(c=col((60, 60, 58)), stroke=0.18))
            c.drawOval(skia.Rect(x - 3.2, -19.2, x + 3.2, -10.8), P(c=col((60, 60, 58)), stroke=0.2))
            for xx in np.arange(x - 3.5, x + 7, 1.5):
                c.drawRect(skia.Rect(xx, -8, xx + 0.7, -6.6), P(c=col((40, 40, 40))))
    else:
        with st.at(40):
            x = 0
            c.drawPath(poly([(x - 8, 0), (x - 8, -7), (x - 6.5, -9), (x - 5, -6), (x - 3, -6.5), (x - 2, -4), (x + 1, -4.5), (x + 2, -8), (x + 3.2, -12),
                             (x + 4.4, -8), (x + 6, -7), (x + 7.5, -5), (x + 8, 0)]), P(c=col((110, 96, 88))))
            for xx in (-6.5, -3.5, 3.2):
                c.drawRect(skia.Rect(x + xx - 0.4, -6, x + xx + 0.4, -4.4), P(c=col((40, 36, 34))))
            draw_person(c, Look(height=1.6, build=0.9, suit=(150, 146, 140), suit_dark=(130, 126, 120), hat=None, hair=(150, 146, 140)),
                        stand(), x=x + 5.2, facing=1, z=40)
    with st.at(10):
        rng = np.random.default_rng(9)
        for x in np.arange(-30, 30, 1.0):
            c.drawRect(skia.Rect(x, -rng.uniform(0.1, 0.6), x + rng.uniform(0.4, 1.0), 0), P(c=col((80, 78, 74))))


@shot(111)
def s111(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -8, 2), y=-3, z=-10)
    sky(c, W, H, (150, 152, 154), (196, 196, 194))
    ground(c, W, H, st.cam, (100, 98, 94), (140, 138, 134))
    ruins(c, st, t, "dome")
    mono_layer(c, W, H, 1.0)
    location_card(c, W, H, [("HIROSHIMA — AUTUMN 1945", 28, "semi", "fg"), ("THE PREFECTURAL INDUSTRIAL PROMOTION HALL, TODAY THE ATOMIC BOMB DOME", 14, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), MONO)
    tag2d(c, W, H, MONO)


# =========================================================== SCENE 10
@shot(112)
def s112(c, t, d, W, H):
    m = mv("jp10", JAPAN, (128, 30, 136, 37), "land-10m.json")
    mat, mpx = draw_map(c, W, H, m, (HIRO[0] + 0.03, HIRO[1] - 0.02), track(t, d, 26, 20), MONO, grat=0.1,
                        rings=[(HIRO[0], HIRO[1], r, clamp((t - 0.6 - i * 0.5) / 0.6)) for i, r in enumerate((1, 2, 3))],
                        markers=[(HIRO[0], HIRO[1], "HYPOCENTRE", 1.0, "target", (16, -12))])
    p = m.S(mat, *HIRO)
    r2 = 1700 / mpx
    c.drawCircle(p.x(), p.y(), r2 * clamp((t - 2.0) / 1.2), P(c=col((180, 180, 176), 0.25)))
    for i, r in enumerate((1, 2, 3)):
        text(c, f"{r} km", p.x() + r * 1000 / mpx + 6 * K(H), p.y() - 6 * K(H), 13 * K(H), "mono", MONO["fg"], clamp((t - 0.8 - i * 0.5) / 0.6))
    scale_bar(c, W, H, mpx, MONO)
    location_card(c, W, H, [("HIROSHIMA", 28, "semi", "fg"), ("Estimated deaths by the end of 1945: about 90,000–140,000", 18, "reg", "accent"),
                            ("Sources: U.S. Strategic Bombing Survey (1946); City of Hiroshima estimates", 13, "mono", "muted")],
                  clamp((t - 2.4) / 0.8), MONO)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", MONO)


@shot(113)
def s113(c, t, d, W, H):
    if "nyt45" not in _G:
        _G["nyt45"] = newspaper(1300, 1800, "The New York Times", "NEW YORK, TUESDAY, AUGUST 7, 1945",
                                [("FIRST ATOMIC BOMB DROPPED ON JAPAN;", 50), ("MISSILE IS EQUAL TO 20,000 TONS OF TNT;", 44),
                                 ("TRUMAN WARNS FOE OF A 'RAIN OF RUIN'", 44)], photo=True, seed=45)
    document_shot(c, t, d, W, H, _G["nyt45"], MONO, focus=(0.5, 0.15), tone=(30, 28, 26), tag="RECREATION · FRONT PAGE, 7 AUGUST 1945")
    mono_layer(c, W, H, 0.4)


@shot(114)
def s114(c, t, d, W, H):
    m = mv("pac", "+proj=lcc +lat_1=12 +lat_2=30 +lat_0=22 +lon_0=140 +datum=WGS84", (120, 5, 160, 40), "land-10m.json")
    draw_map(c, W, H, m, (track(t, d, 136, 131.5), track(t, d, 25, 32.5)), track(t, d, 3600, 1300), MONO, grat=5,
             routes=[([(145.63, 14.99), (130.53, 30.35)], clamp((t - 0.4) / 2.2), MONO["accent"]),
                     ([(130.53, 30.35), (130.88, 33.88)], clamp((t - 2.6) / 1.2), MONO["accent"]),
                     ([(130.88, 33.88), (129.86, 32.77)], clamp((t - 4.4) / 1.4), MONO["accent"])],
             markers=[(145.63, 14.99, "TINIAN — TAKEOFF 3:47 AM", 1.0, "dot", (12, 6)), (130.53, 30.35, "YAKUSHIMA — RENDEZVOUS", ping(t, 2.4), "dot", (12, 6)),
                      (130.88, 33.88, "KOKURA — PRIMARY TARGET, OBSCURED", ping(t, 3.8), "dot", (12, -10)),
                      (129.86, 32.77, "NAGASAKI", ping(t, 5.6), "target", (-14, 16))])
    date_counter(c, W, H, MONO, "9 AUGUST 1945", clamp(t / 0.6))
    text(c, "schematic route", 64 * K(H), H - 64 * K(H), 15 * K(H), "mono", MONO["muted"], clamp((t - 1) / 0.8))
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", MONO)


@shot(115)
def s115(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -0.6, 0.6), y=-1.0, z=track(t, d, -0.4, 0.5))
    sky(c, W, H, (150, 166, 180), (210, 212, 210))
    ground(c, W, H, st.cam, (110, 110, 106), (150, 150, 146))
    with st.at(5):
        c.drawRect(skia.Rect(-2.2, -0.6, 2.2, -0.45), P(c=col((50, 50, 50))))
        for wx in (-1.6, 1.6):
            c.drawCircle(wx, -0.25, 0.25, P(c=col((20, 20, 20))))
        fat_man(c, 0, -1.35, 0.95)
        for i, x in enumerate((-3.4, -2.6, 2.8)):
            draw_person(c, [CREW, SOLDIER, CREW][i], idle(stand(head=8), t, i, 0.6), x=x, facing=1 if x < 0 else -1, z=5)
    mono_layer(c, W, H, 0.55)
    card(c, W, H, t, d, MONO, "FAT MAN · PLUTONIUM-239, IMPLOSION", "TINIAN · AUGUST 1945")
    tag2d(c, W, H, MONO)


@shot(116)
def s116(c, t, d, W, H):
    sky_air(c, W, H, t, top=(80, 100, 120), bot=(200, 204, 204), clouds_y=0.68, seed=7)
    st = Stage(c, W, H, x=track(t, d, 0, 3), y=-1, z=-40)
    with st.at(10):
        b29(c, 0, math.sin(t * 0.6) * 0.3, 1.0, t, number="77", bank=lerp(0, 4, smooth((t - 3) / 2)))
    mono_layer(c, W, H, 0.5)
    location_card(c, W, H, [("BOCKSCAR · B-29 SUPERFORTRESS", 26, "semi", "fg"), ("PILOT: MAJ. CHARLES W. SWEENEY · NOSE ART PAINTED ONLY AFTER THE MISSION", 14, "mono", "fg")],
                  win(t, 0.6, d - 0.2, 0.6), MONO)
    tag2d(c, W, H, MONO)


@shot(117)
def s117(c, t, d, W, H):
    m = mv("jp10", JAPAN, (128, 30, 136, 37), "land-10m.json")
    z = ease((t - 0.3) / 4.0)
    draw_map(c, W, H, m, (lerp(130.6, NAGA[0] + 0.08, z), lerp(33.0, NAGA[1], z)), math.exp(lerp(math.log(420), math.log(40), z)), MONO, grat=0.5,
             markers=[(NAGA[0], NAGA[1], "", ping(t, 3.8), "target", (14, -12))],
             labels=[(129.78, 32.68, "NAGASAKI HARBOUR", 12, z), (129.875, 32.82, "URAKAMI VALLEY", 12, z)])
    location_card(c, W, H, [("NAGASAKI, JAPAN", 34, "semi", "fg"), ("9 AUGUST 1945", 22, "med", "fg"), ("11:02 AM LOCAL TIME", 22, "med", "accent"),
                            ("32°46′25″ N · 129°51′49″ E", 13, "mono", "muted")], clamp((t - 4.2) / 0.9), MONO)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", MONO)


@shot(118)
def s118(c, t, d, W, H):
    photo_shot(c, t, d, W, H, "Nagasakibomb.jpg", MONO, "CHARLES LEVY / NATIONAL ARCHIVES",
               start=(0.5, 0.55, 1.0), end=(0.5, 0.42, 1.12), fit="contain")
    location_card(c, W, H, [("NAGASAKI", 30, "semi", "fg"), ("9 AUGUST 1945 · 11:02 AM LOCAL TIME", 20, "med", "fg")], clamp((t - 0.8) / 0.8), MONO)


@shot(119)
def s119(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -3, 3), y=-3, z=-12)
    sky(c, W, H, (150, 152, 154), (196, 196, 194))
    ground(c, W, H, st.cam, (100, 98, 94), (140, 138, 134))
    with st.at(200):
        c.drawPath(poly(ridge(np.random.default_rng(8), -500, 500, -20, 22, 90, 0.4)), P(c=col((120, 122, 118))))
    ruins(c, st, t, "cathedral")
    mono_layer(c, W, H, 1.0)
    card(c, W, H, t, d, MONO, "URAKAMI CATHEDRAL, NAGASAKI", "1945")
    tag2d(c, W, H, MONO)


@shot(120)
def s120(c, t, d, W, H):
    m = mv("jp", JAPAN, (125, 28, 146, 46))
    draw_map(c, W, H, m, (track(t, d, 132, 131.5), track(t, d, 33.8, 33.6)), track(t, d, 900, 1100), MONO, grat=2,
             markers=[(HIRO[0], HIRO[1], "HIROSHIMA", 1.0, "target", (14, -12)), (NAGA[0], NAGA[1], "NAGASAKI", 1.0, "target", (-14, 18))])
    legend(c, W, H, [(MONO["accent"], "HIROSHIMA — 6 AUG 1945 — 8:15 AM — 'LITTLE BOY' (uranium, gun-type)", "dot"),
                     (MONO["accent"], "NAGASAKI — 9 AUG 1945 — 11:02 AM — 'FAT MAN' (plutonium, implosion)", "dot")],
           MONO, clamp((t - 0.8) / 0.8), y=H * 0.82)
    map_title(c, W, H, MONO, "THE TWO ATOMIC BOMBINGS", "AUGUST 1945", clamp(t / 0.8))
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", MONO)


@shot(121)
def s121(c, t, d, W, H):
    k = K(H)
    st = Stage(c, W, H, x=track(t, d, -1, 1), y=-2.0, z=track(t, d, -3, -1.6))
    sky(c, W, H, (150, 160, 170), (200, 200, 196))
    with st.at(60):
        c.drawRect(skia.Rect(-300, -1, 300, 3), P(c=col((110, 120, 126))))
        c.drawPath(poly(ridge(np.random.default_rng(5), -300, 300, -2, 4, 60, 0.3)), P(c=col((130, 136, 136))))
    with st.at(14):
        c.drawRect(skia.Rect(-4, -14, 6, -2), P(c=col((120, 124, 126))))
        c.drawRect(skia.Rect(-2, -22, 2, -14), P(c=col((110, 114, 116))))
        c.drawRect(skia.Rect(-10, -4, -4, -2), P(c=col((100, 104, 106))))
        for i in range(3):
            c.drawLine(-7, -3.2 + i * 0.3, -16, -3.6 + i * 0.3, P(c=col((90, 94, 96)), stroke=0.35))
    with st.at(6):
        c.drawRect(skia.Rect(-20, -0.4, 20, 0.6), P(c=col((140, 136, 126))))
        table(c, -0.8, 0.8, top=-0.76, colr=(70, 60, 50), cloth=(60, 70, 60))
        for i, x in enumerate(np.arange(-7, 7.1, 0.9)):
            if abs(x) < 1.2:
                continue
            L = Look(height=1.78, build=1.0, suit=(214, 206, 180) if i % 3 else (40, 40, 44), suit_dark=(180, 174, 150), hat=(200, 196, 170) if i % 3 else None, hair=(60, 50, 40))
            draw_person(c, L, idle(stand(), t, i, 0.4), x=x, facing=1 if x < 0 else -1, z=6)
        p = sit(lean=20, head=20, sh_r=60, el_r=80)
        draw_person(c, Look(height=1.68, build=1.0, suit=(40, 40, 44), suit_dark=(30, 30, 34), hat=(40, 40, 44), hat_band=(20, 20, 20), hair=(30, 30, 30)),
                    p, x=-0.4, facing=1, z=6)
    mono_layer(c, W, H, 0.6)
    events = [("6 AUG", "HIROSHIMA"), ("9 AUG", "NAGASAKI"), ("15 AUG", "EMPEROR'S RADIO BROADCAST"), ("2 SEP 1945", "FORMAL SURRENDER")]
    c.drawRect(skia.Rect(0, H * 0.86, W, H), P(c=col((0, 0, 0), 0.55)))
    for i, (a_, b_) in enumerate(events):
        a = clamp((t - 0.6 - i * 0.6) / 0.5)
        x = W * (0.1 + i * 0.24)
        c.drawCircle(x, H * 0.9, 5 * k, P(c=col(MONO["accent"], a)))
        text(c, a_, x + 14 * k, H * 0.9 + 5 * k, 16 * k, "monom", MONO["accent"], a)
        text(c, b_, x + 14 * k, H * 0.9 + 30 * k, 13 * k, "med", MONO["fg"], a, track=0.1)
    text(c, "USS MISSOURI, TOKYO BAY · 2 SEPTEMBER 1945", 64 * k, 90 * k, 22 * k, "semi", MONO["fg"], clamp((t - 0.4) / 0.6), track=0.16)
    tag2d(c, W, H, MONO)


# =========================================================== SCENE 11
@shot(122)
def s122(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1, 1), y=-1.6, z=track(t, d, -2, -0.6))
    sky(c, W, H, (130, 160, 196), (220, 220, 214))
    ground(c, W, H, st.cam, (130, 120, 100), (170, 166, 150))
    with st.at(22):
        from shots_b import log_building
        log_building(c, -10, 20, 8, (126, 88, 58))
    with st.at(9):
        c.drawLine(4, 0, 4, -7, P(c=col((150, 130, 80)), stroke=0.08))
        c.drawPath(poly([(4, -7), (6.4, -6.8), (6.3, -5.4), (4, -5.6)]), P(c=col((120, 40, 40))))
        c.drawRect(skia.Rect(4, -7, 5.0, -6.3), P(c=col((40, 50, 90))))
        c.drawRect(skia.Rect(-0.5, -1.1, 0.5, 0), P(c=col((90, 70, 50))))
        draw_person(c, OPP_50S, gesture(stand(), t, 0, 0.5), x=-0.1, facing=-1, z=9)
    with st.at(5):
        crowd_row(c, -6, 6, [SCIENTIST, WOMAN, SOLDIER, OFFICIAL, WOMAN2], seated=False, t=t, seed=4, spacing=0.75, shade=0.3, facing=1)
    card(c, W, H, t, d, CW, "ARMY–NAVY 'E' AWARD, LOS ALAMOS", "16 OCTOBER 1945 · OPPENHEIMER STEPS DOWN AS DIRECTOR")
    tag2d(c, W, H, CW)


@shot(123)
def s123(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, 0.4, 0.9), y=-1.3, z=track(t, d, -1.0, 0.2))
    c.clear(col((40, 40, 44)))
    with st.at(5):
        wall(c, -6, 6, -4.6, (200, 200, 190), light=(0, -2.6), light_r=4, light_c=(240, 244, 250), light_a=0.2)
        for x in (-3.4, 2.4):
            window(c, x, -3.6, x + 1.4, -1.0, t, frame=(220, 216, 206))
            c.drawRect(skia.Rect(x - 0.3, -3.8, x, 0), P(c=col((180, 176, 160), 0.8)))
            c.drawRect(skia.Rect(x + 1.4, -3.8, x + 1.7, 0), P(c=col((180, 176, 160), 0.8)))
        for x, kind in ((-0.6, "us"), (0.2, "pres")):
            c.drawLine(x, 0, x, -2.6, P(c=col((170, 150, 90)), stroke=0.03))
            if kind == "us":
                for i in range(7):
                    c.drawRect(skia.Rect(x, -2.6 + i * 0.11, x + 0.5, -2.545 + i * 0.11), P(c=col((170, 40, 44))))
                    c.drawRect(skia.Rect(x, -2.545 + i * 0.11, x + 0.5, -2.49 + i * 0.11), P(c=col((236, 232, 224))))
                c.drawRect(skia.Rect(x, -2.6, x + 0.22, -2.36), P(c=col((40, 52, 100))))
            else:
                c.drawRect(skia.Rect(x, -2.6, x + 0.5, -1.85), P(c=col((30, 40, 90))))
                c.drawCircle(x + 0.25, -2.22, 0.12, P(c=col((220, 200, 140))))
    with st.at(3.8):
        table(c, -1.4, 0.6, top=-0.78, colr=(80, 52, 34))
        p = sit(lean=-4, head=0, sh_r=40, el_r=90)
        if t > 3.2:
            p.sh_r, p.el_r = 60, 70
        draw_person(c, TRUMAN, idle(p, t, 1, 0.4), x=-1.0, facing=1, z=3.8)
        p2 = stand(head=8 + 4 * math.sin(t * 0.7), sh_r=30 + 10 * math.sin(t * 2.4), el_r=90 + 20 * math.sin(t * 3.1), sh_l=25, el_l=100)
        draw_person(c, OPP_50S, p2, x=1.6, facing=-1, z=3.8)
    card(c, W, H, t, d, CW, "THE OVAL OFFICE", "25 OCTOBER 1945 · OPPENHEIMER MEETS PRESIDENT TRUMAN")
    tag2d(c, W, H, CW)


@shot(124)
def s124(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1, 1), y=lerp(-12, -1.6, eout(t / 3)), z=-1)
    sky(c, W, H, (130, 160, 196), (226, 214, 190))
    ground(c, W, H, st.cam, (90, 110, 70), (140, 150, 110))
    with st.at(36):
        building(c, -16, 32, 13, (150, 72, 54), rows=3, roof="gable", brick=True, cupola=True, seed=8)
    with st.at(14):
        for x in (-14, -6, 8, 15):
            deciduous(c, x, 9, (190, 120, 50), t)
    with st.at(5):
        p = walk_pose(t * 5)
        p.hand_r = "pipe"
        draw_person(c, OPP_50S, p, x=-3 + t * 1.2, facing=1, z=5)
        c.drawRect(skia.Rect(-3 + t * 1.2 - 0.18, -0.75, -3 + t * 1.2 + 0.08, -0.5), P(c=col((90, 60, 40))))
        from shots_a import leaves
        leaves(c, t, -8, 8, -6)
    card(c, W, H, t, d, CW, "INSTITUTE FOR ADVANCED STUDY, PRINCETON", "1947 · DIRECTOR, 1947–1966")
    tag2d(c, W, H, CW)


def arc_on_globe(c, a, b, cx, cy, R, lon0, lat0, prog, colr, k):
    pts = []
    for u in np.linspace(0, prog, 60):
        lon = lerp(a[0], b[0], u); lat = lerp(a[1], b[1], u) + math.sin(math.pi * u) * 18
        x, y, vis = Globe.project(lon, lat, cx, cy, R, lon0, lat0)
        if vis:
            pts.append((x, y))
    if len(pts) > 1:
        c.drawPath(poly(pts, close=False), P(c=col(colr), stroke=2 * k))


@shot(125)
def s125(c, t, d, W, H):
    k = K(H)
    lon0 = lerp(-60, 40, ease(t / d))
    R = H * 0.42
    globe_scene(c, W, H, t, CW, lon0, 45, R, points=[(-106.48, 33.68, "TRINITY 1945", 1.0), (77.82, 50.44, "SEMIPALATINSK 1949", ping(t, 4.2))])
    arc_on_globe(c, (-106.48, 33.68), (77.82, 50.44), W / 2, H / 2, R, lon0, 45, clamp((t - 1.0) / 3.2), CW["accent"], k)
    n = 1 if t < 4.2 else 2
    text(c, f"NUCLEAR-ARMED STATES: {n}", W - 64 * k, 110 * k, 22 * k, "monom", CW["accent"], 1, align="right")
    location_card(c, W, H, [("SEMIPALATINSK TEST SITE, KAZAKH SSR", 26, "semi", "fg"), ("29 AUGUST 1949 · FIRST SOVIET ATOMIC TEST (RDS-1)", 16, "mono", "fg")],
                  clamp((t - 4.6) / 0.8), CW)
    small_tag(c, W, H, "3D GRAPHICS · NATURAL EARTH", CW)


@shot(126)
def s126(c, t, d, W, H):
    if "truman49" not in _G:
        _G["truman49"] = typed_letter(1300, 1800, ["THE WHITE HOUSE", "", "STATEMENT BY THE PRESIDENT", "September 23, 1949"],
            ["I believe the American people to the fullest extent consistent with the national security are entitled to be informed "
             "of all developments in the field of atomic energy. That is my reason for making public the following information.",
             "We have evidence that within recent weeks an atomic explosion occurred in the U.S.S.R."])
    document_shot(c, t, d, W, H, _G["truman49"], CW, focus=(0.5, 0.36), tone=(32, 34, 38), highlight=(0.33, 0.4),
                  tag="RECREATION · ORIGINAL: TRUMAN LIBRARY")


@shot(127)
def s127(c, t, d, W, H):
    k = K(H)
    bg_fill(c, W, H, CW)
    cards = [("OCTOBER 1949", "The AEC General Advisory Committee, chaired by Oppenheimer, advises against a crash programme to build the hydrogen bomb."),
             ("31 JANUARY 1950", "President Truman orders development to proceed.")]
    for i, (a_, b_) in enumerate(cards):
        a = eout((t - 0.3 - i * 1.4) / 0.7)
        x, y = W * 0.1, H * (0.22 + i * 0.26)
        text(c, a_, x, y, 28 * k, "semi", CW["accent"], a, track=0.12)
        for j, ln in enumerate(wrap(b_, "reg", 24 * k, W * 0.8)):
            text(c, ln, x, y + (40 + j * 34) * k, 24 * k, "reg", CW["fg"], a)
    a = clamp((t - 3.0) / 0.8)
    y = H * 0.78
    c.drawRect(skia.Rect(W * 0.1, y, W * 0.1 + 6 * k, y + 20 * k), P(c=col(CW["fg"], a)))
    c.drawRect(skia.Rect(W * 0.1, y + 36 * k, W * 0.1 + W * 0.75 * a, y + 56 * k), P(c=col(CW["accent"], a)))
    text(c, "FISSION BOMB (KILOTONS)", W * 0.1 + 20 * k, y + 16 * k, 14 * k, "mono", CW["muted"], a)
    text(c, "THERMONUCLEAR BOMB (MEGATONS)", W * 0.1, y + 80 * k, 14 * k, "mono", CW["muted"], a)
    small_tag(c, W, H, "GRAPHICS", CW)


@shot(128)
def s128(c, t, d, W, H):
    st = Stage(c, W, H, x=0, y=-3, z=-80)
    glow = 0.5 * math.exp(-t / 3)
    sky(c, W, H, mix((60, 90, 130), (255, 210, 160), glow), mix((170, 190, 200), (255, 180, 120), glow))
    ground(c, W, H, st.cam, (40, 80, 110), (70, 110, 130))
    with st.at(600):
        mushroom(c, 0, 0, 3 + t * 1.4, scale=7, glow=(255, 170, 90), smoke=(150, 130, 120))
    with st.at(60):
        for x in (-40, -20, 30):
            c.drawOval(skia.Rect(x - 6, -0.4, x + 6, 0.4), P(c=col((190, 180, 140))))
            pine(c, x, 3, (40, 70, 50))
    location_card(c, W, H, [("ENEWETAK ATOLL, MARSHALL ISLANDS", 26, "semi", "fg"), ("1 NOVEMBER 1952 · IVY MIKE", 18, "med", "fg"),
                            ("First full-scale thermonuclear test, about 10.4 megatons", 16, "reg", "accent")], win(t, 0.8, d - 0.2, 0.7), CW)
    tag2d(c, W, H, CW)


@shot(129)
def s129(c, t, d, W, H):
    m = mv("world", "+proj=robin +datum=WGS84", (-180, -60, 180, 85))
    tests = [(-106.48, 33.68, "USA 1945", 0.4), (77.82, 50.44, "USSR 1949", 1.4), (115.55, -20.4, "UK 1952", 2.4),
             (162.19, 11.67, "USA 1952 · H-BOMB", 3.2), (0.06, 26.31, "FRANCE 1960", 4.4), (89.8, 40.82, "CHINA 1964", 5.6)]
    draw_map(c, W, H, m, (track(t, d, 30, 40), 20), track(t, d, 36000, 33000), CW, grat=30,
             markers=[(lo, la, name, ping(t, t0), "key", (12, -10)) for lo, la, name, t0 in tests])
    n = sum(1 for lo, la, name, t0 in tests if t >= t0 and "H-BOMB" not in name)
    text(c, f"NUCLEAR-ARMED STATES: {n}", W - 64 * K(H), 110 * K(H), 22 * K(H), "monom", CW["accent"], 1, align="right")
    map_title(c, W, H, CW, "THE NUCLEAR ARMS RACE, 1945–1964", "FIRST TESTS BY EACH NUCLEAR POWER", clamp(t / 0.8))
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", CW)


@shot(130)
def s130(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -2, 2), y=-1.6, z=0)
    sky(c, W, H, (160, 170, 180), (214, 214, 210))
    ground(c, W, H, st.cam, (110, 110, 106), (160, 160, 156))
    with st.at(300):
        c.drawPath(poly([(-2, 0), (-1.4, -50), (0, -54), (1.4, -50), (2, 0)]), P(c=col((210, 206, 196))))
    with st.at(20):
        building(c, -16, 34, 7, (176, 172, 160), rows=2, roof="flat", seed=3)
        for x in (-20, 22):
            deciduous(c, x, 7, (230, 190, 200), t)
    with st.at(6):
        car_1940(c, -2, (20, 20, 22))
        car_1940(c, 6 + t * 2.0 * smooth((t - 2) / 1), (20, 20, 22), wheel_t=t)
        for i in range(2):
            draw_person(c, OFFICIAL, walk_pose(t * 5 + i, 0.9), x=-6 + i * 0.8 + t * 1.1, facing=1, z=6)
    card(c, W, H, t, d, CW, "WASHINGTON, D.C.", "APRIL 1954 · ATOMIC ENERGY COMMISSION, BUILDING T-3")
    tag2d(c, W, H, CW)


def hearing_room(c, st, t):
    with st.at(6):
        wall(c, -8, 8, -4.2, (130, 118, 100), light=(-2, -2.4), light_r=5, light_c=(230, 236, 240), light_a=0.18)
        for x in (-6.4, 4.4):
            window(c, x, -3.4, x + 1.8, -1.0, t, sky_c=((170, 180, 190), (210, 210, 206)))
            for yy in np.arange(-3.4, -1.0, 0.12):
                c.drawLine(x, yy, x + 1.8, yy, P(c=col((200, 196, 186), 0.7), stroke=0.04))


@shot(131)
def s131(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.0, 0.6), y=-1.3, z=track(t, d, -2.0, -0.6))
    c.clear(col((40, 38, 36)))
    hearing_room(c, st, t)
    with st.at(5.2):
        c.drawRoundRect(skia.Rect(2.2, -0.9, 5.0, -0.1), 0.15, 0.15, P(c=col((90, 56, 40))))
        c.drawRect(skia.Rect(2.2, -1.3, 5.0, -0.85), P(c=col((80, 50, 36))))
        p = sit(lean=0, sh_r=20, el_r=100, hand_r="pipe", head=-4, bob=0.5)
        draw_person(c, OPP_50S, idle(p, t, 2, 0.4), x=3.0, facing=-1, z=5.2)
        smoke_puffs(c, t, 2.6, -1.5, n=8, seed=3, a=0.12)
    with st.at(4.0):
        table(c, -4.6, 1.2, top=-0.78, colr=(80, 60, 44))
        for i, x in enumerate((-4.0, -2.8, -1.6)):
            p = sit(head=10, sh_r=60, el_r=80)
            if i == 1:
                p.sh_r, p.el_r, p.head = 70 + 5 * math.sin(t * 2), 60, 6
            draw_person(c, [OFFICIAL, Look(height=1.8, build=1.05, suit=(50, 50, 56), suit_dark=(40, 40, 44), hat=None, hair=(120, 110, 100)), OFFICIAL][i],
                        p, x=x, facing=1, z=4.0)
        for j in range(5):
            c.drawRect(skia.Rect(-3.5 + j * 0.9, -0.82, -3.1 + j * 0.9, -0.78), P(c=col((224, 218, 204))))
    with st.at(2.6):
        c.drawRect(skia.Rect(-0.2, -0.75, 0.4, -0.6), P(c=col((40, 40, 40))))
        p = sit(sh_r=70 + 6 * math.sin(t * 9), el_r=50, head=6)
        draw_person(c, WOMAN2, p, x=-0.5, facing=1, z=2.6)
    card(c, W, H, t, d, CW, "ROOM 2022, ATOMIC ENERGY COMMISSION", "PERSONNEL SECURITY BOARD · 12 APRIL – 6 MAY 1954")
    tag2d(c, W, H, CW)


@shot(132)
def s132(c, t, d, W, H):
    st = Stage(c, W, H, x=0.3, y=-1.25, z=track(t, d, 2.6, 3.2), f=1100)
    c.clear(col((30, 28, 26)))
    with st.at(4.6):
        wall(c, -3, 3, -3, (110, 100, 86), light=(0.6, -1.4), light_r=1.6, light_c=(230, 236, 240), light_a=0.25)
        c.drawRoundRect(skia.Rect(-1.6, -0.9, 1.6, -0.1), 0.15, 0.15, P(c=col((90, 56, 40))))
        c.drawRect(skia.Rect(-1.6, -1.35, 1.6, -0.85), P(c=col((80, 50, 36))))
        drag = win(t, 1.2, 2.6, 0.4)
        p = sit(lean=-2, sh_r=lerp(20, 120, drag), el_r=lerp(100, 150, drag), hand_r="pipe", head=lerp(-4, -10, drag), bob=0.5)
        draw_person(c, OPP_50S, p, x=0.0, facing=1, z=4.6, rim=0.4, light=(230, 236, 240))
        smoke_puffs(c, t + 2, 0.35, -1.6, n=12, seed=5, a=0.18)
        for yy in np.arange(-3, 0, 0.22):
            c.drawRect(skia.Rect(-3, yy, 3, yy + 0.08), P(c=col((0, 0, 0), 0.12)))
    tag2d(c, W, H, CW)


@shot(133)
def s133(c, t, d, W, H):
    if "transcript" not in _G:
        _G["transcript"] = report_cover(1300, 1800, [("UNITED STATES ATOMIC ENERGY COMMISSION", 26)],
                                        [("IN THE MATTER OF", 46), ("J. ROBERT OPPENHEIMER", 56)],
                                        [("TRANSCRIPT OF HEARING BEFORE", 24), ("PERSONNEL SECURITY BOARD", 24),
                                         ("WASHINGTON, D.C., APRIL 12, 1954, THROUGH MAY 6, 1954", 22)])
    document_shot(c, t, d, W, H, _G["transcript"], CW, focus=(0.5, 0.45), tone=(30, 32, 36), tag="RECREATION · U.S. GOVERNMENT PRINTING OFFICE, 1954")


@shot(134)
def s134(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1, 1.5), y=-1.4, z=-0.5)
    sky(c, W, H, (150, 156, 160), (196, 196, 194))
    ground(c, W, H, st.cam, (100, 100, 98), (140, 140, 138))
    with st.at(14):
        building(c, -14, 30, 7, (176, 172, 160), rows=2, roof="flat", seed=3)
    with st.at(7):
        car_1940(c, 4.5, (20, 20, 22))
        ox = lerp(-3, 2.6, smooth(t / (d - 0.6)))
        p = walk_pose(t * 5, 0.9 * (1 - smooth((t - d + 1) / 0.6)))
        p.head = 8
        draw_person(c, Look(height=1.81, build=0.78, suit=(40, 42, 46), suit_dark=(32, 34, 36), hat=(40, 42, 46), hat_band=(20, 20, 22), hair=(150, 150, 150)),
                    p, x=ox, facing=1, z=7)
    with st.at(3.2):
        for i, x in enumerate((-2.0, -0.9, 1.4, 2.4)):
            draw_person(c, OFFICIAL, stand(sh_r=100, el_r=90, head=-4), x=x, facing=1 if x < 0 else -1, z=3.2, shade=0.4)
            fl = 1.0 if (t * 1.1 + i * 0.37) % 1.3 < 0.07 else 0.0
            c.drawRect(skia.Rect(x + (0.15 if x < 0 else -0.45), -1.75, x + (0.45 if x < 0 else -0.15), -1.5), P(c=col((40, 40, 40))))
            c.drawCircle(x + (0.3 if x < 0 else -0.3), -1.85, 0.35, P(c=col((255, 255, 255), fl * 0.9), blur=0.2))
    tag2d(c, W, H, CW)


@shot(135)
def s135(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1, 0), y=track(t, d, -1.6, -4), z=track(t, d, -1, -6))
    sky(c, W, H, (20, 30, 60), (90, 90, 120))
    ground(c, W, H, st.cam, (40, 40, 46), (70, 70, 80))
    with st.at(400):
        c.drawRect(skia.Rect(-14, -30, 14, 0), P(c=col((200, 200, 196))))
        c.drawOval(skia.Rect(-12, -60, 12, -26), P(c=col((210, 210, 206))))
        c.drawRect(skia.Rect(-1.5, -70, 1.5, -58), P(c=col((210, 210, 206))))
        c.drawCircle(0, -45, 40, P(c=col((255, 240, 200), 0.12), blur=15))
    with st.at(12):
        for x in np.arange(-16, 16, 6):
            building(c, x, 5.5, 9, (60, 58, 60), rows=3, roof="flat", seed=abs(int(x)) + 2, lit=0.6)
    with st.at(6):
        for x in (-4, 2.5, 9):
            lamp_post(c, x, on=smooth((t - 0.6 - (x + 4) * 0.05) / 0.4))
        draw_person(c, OPP_50S if False else Look(height=1.81, build=0.78, suit=(30, 30, 34), suit_dark=(24, 24, 28), hat=(30, 30, 34), hat_band=(16, 16, 18), hair=(150, 150, 150)),
                    walk_pose(t * 4.2, 0.7), x=-2 + t * 0.7, facing=1, z=6)
    tag2d(c, W, H, CW)


@shot(136)
def s136(c, t, d, W, H):
    timeline(c, t, d, W, H, CW, [(1954.3, "12 APRIL – 6 MAY 1954 — Security hearing"),
                                 (1954.5, "29 JUNE 1954 — The AEC refuses to reinstate his security clearance")], focus=(1950, 1958))
    small_tag(c, W, H, "GRAPHICS", CW)


# =========================================================== SCENE 12
@shot(137)
def s137(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, 0.2, 0.7), y=-1.2, z=track(t, d, -0.8, 0.5))
    c.clear(col((20, 18, 16)))
    with st.at(4.8):
        wall(c, -6, 6, -4.4, (70, 60, 50), light=(-1.6, -1.8), light_r=3, light_c=(255, 230, 190), light_a=0.25)
        for x in (1.0, 3.0):
            bookshelf(c, x, x + 1.9, -3.8, -0.05, seed=int(x * 7))
        def view(cv, x0, y0, x1, y1):
            for i in range(3):
                deciduous(cv, x0 + 0.3 + i * 0.5, 1.2, (170, 110, 50), t)
        window(c, -3.2, -3.0, -1.6, -1.2, t, view=view, sky_c=((170, 180, 190), (220, 210, 190)))
    with st.at(3.6):
        table(c, -1.4, 0.8, top=-0.76, colr=(70, 50, 36))
        c.drawRect(skia.Rect(-0.6, -0.8, 0.0, -0.77), P(c=col((230, 224, 210))))
        p = sit(head=14, sh_r=60 + 3 * math.sin(t * 3), el_r=80, lean=10)
        if 2.5 < t < 3.6:
            p.head = -6
        draw_person(c, OPP_60S, p, x=-1.2, facing=1, z=3.6, rim=0.4)
    card(c, W, H, t, d, DARK, "PRINCETON", "LATE 1950s")
    tag2d(c, W, H, DARK)


@shot(138)
def s138(c, t, d, W, H):
    st = Stage(c, W, H, x=0.4, y=-1.4, z=track(t, d, -1.0, 0.2))
    c.clear(col((40, 34, 30)))
    with st.at(5.4):
        wall(c, -6, 6, -4.6, (200, 190, 170), light=(0, -2.8), light_r=4, light_c=(255, 240, 210), light_a=0.25)
        for x in (-3.6, 2.6):
            c.drawRect(skia.Rect(x, -3.8, x + 1.2, -0.8), P(c=col((170, 150, 110))))
        c.drawCircle(0.4, -3.6, 0.5, P(c=col((255, 230, 180), 0.3), blur=0.4))
        crowd_row(c, -4.5, -1.6, [OFFICIAL, WOMAN2, OFFICIAL], seated=False, t=t, seed=2, spacing=0.8, shade=0.25, z=5.4)
        crowd_row(c, 2.4, 5.0, [OFFICIAL, WOMAN, OFFICIAL], seated=False, t=t, seed=6, spacing=0.8, shade=0.25, facing=-1, z=5.4)
    with st.at(4.0):
        hand = smooth((t - 1.2) / 0.8)
        lbj = Look(height=1.92, build=1.15, suit=(40, 42, 46), suit_dark=(32, 34, 36), hat=None, hair=(120, 116, 110), nose=1.4)
        draw_person(c, lbj, stand(sh_r=lerp(10, 70, hand), el_r=lerp(10, 20, hand)), x=-0.3, facing=1, z=4.0)
        draw_person(c, OPP_60S, stand(sh_r=lerp(10, 66, hand), el_r=20), x=1.35, facing=-1, z=4.0)
        if hand > 0.5:
            c.drawRect(skia.Rect(0.42, -1.32, 0.62, -1.18), P(c=col((210, 180, 100))))
        draw_person(c, Look(height=1.6, build=0.85, suit=(120, 120, 130), suit_dark=(100, 100, 110), hat=None, hair=(80, 70, 60), skirt=True, hair_long=True),
                    idle(stand(), t, 3, 0.4), x=2.3, facing=-1, z=4.0)
    card(c, W, H, t, d, DARK, "THE WHITE HOUSE", "2 DECEMBER 1963 · PRESIDENT LYNDON B. JOHNSON PRESENTS THE ENRICO FERMI AWARD")
    tag2d(c, W, H, DARK)


@shot(139)
def s139(c, t, d, W, H):
    timeline(c, t, d, W, H, DARK, [(1954.4, "1954 — Security clearance revoked"), (1963.9, "2 DECEMBER 1963 — Enrico Fermi Award, presented by President Johnson")],
             focus=(1952, 1968))
    small_tag(c, W, H, "GRAPHICS", DARK)


@shot(140)
def s140(c, t, d, W, H):
    k = K(H)
    c.clear(col((14, 14, 16)))
    tv = skia.Rect(W * 0.2, H * 0.12, W * 0.8, H * 0.82)
    c.drawRoundRect(skia.Rect(tv.left() - 30 * k, tv.top() - 30 * k, tv.right() + 30 * k, tv.bottom() + 30 * k), 40 * k, 40 * k, P(c=col((50, 44, 38))))
    c.save()
    rr = skia.RRect.MakeRectXY(tv, 60 * k, 60 * k)
    c.clipRRect(rr, True)
    c.clear(col((40, 40, 40)))
    st = Stage(c, W, H, x=0.15, y=-1.05, z=track(t, d, 2.0, 2.4), f=1000)
    with st.at(4):
        wall(c, -3, 3, -3, (70, 70, 70), light=(0, -1.6), light_r=1.6, light_c=(255, 255, 255), light_a=0.2)
        p = sit(head=6 + 4 * math.sin(t * 0.6), sh_r=30, el_r=100, bob=0.5)
        draw_person(c, OPP_60S, p, x=0.0, facing=1, z=4, rim=0.5, light=(255, 255, 255))
    for yy in range(int(tv.top()), int(tv.bottom()), max(2, int(4 * k))):
        c.drawLine(tv.left(), yy, tv.right(), yy, P(c=col((0, 0, 0), 0.18), stroke=1))
    c.drawRect(tv, skia.Paint(Color=skia.Color(128, 128, 128, 255), BlendMode=skia.BlendMode.kSaturation))
    c.drawRect(tv, P(c=col((255, 255, 255), 0.03 + 0.02 * math.sin(t * 30))))
    c.restore()
    location_card(c, W, H, [("1965", 28, "semi", "fg"), ("AFTER A TELEVISED NBC INTERVIEW", 16, "mono", "fg")], win(t, 0.6, d - 0.2, 0.6), DARK)
    tag2d(c, W, H, DARK)


@shot(141)
def s141(c, t, d, W, H):
    ev = [(1904, "1904 Born"), (1927, "1927 Doctorate"), (1939, "1939 WWII begins"), (1942, "1942 Manhattan Project"),
          (1945.6, "1945 Trinity · Hiroshima · Nagasaki · surrender"), (1943, "1943 Los Alamos"), (1949.6, "1949 Soviet test"),
          (1954.3, "1954 Hearing"), (1963.9, "1963 Fermi Award"), (1967.1, "18 FEB 1967 — Dies in Princeton, aged 62")]
    timeline(c, t, d, W, H, PAL["title"], ev, reveal_all=True)
    small_tag(c, W, H, "GRAPHICS", DARK)


@shot(142)
def s142(c, t, d, W, H):
    st = Stage(c, W, H, x=0.0, y=-0.9, z=track(t, d, -2.0, 0.0))
    sky(c, W, H, (20, 30, 60), (220, 140, 100))
    ground(c, W, H, st.cam, (60, 50, 50), (110, 80, 70))
    with st.at(600):
        c.drawPath(poly(ridge(np.random.default_rng(12), -1600, 1600, -26, 40, 140, 0.55)), P(c=col((40, 34, 50))))
    with st.at(6):
        c.drawPath(poly([(-0.9, 0), (-0.6, -3.6), (0, -3.9), (0.6, -3.6), (0.9, 0)]), P(c=col((30, 28, 30))))
        c.drawRect(skia.Rect(-0.35, -2.2, 0.35, -1.7), P(c=col((90, 80, 60))))
        c.drawLine(-12, -1.0, 12, -1.0, P(c=col((30, 30, 30), 0.6), stroke=0.01))
    with st.at(2.5):
        for x in np.arange(-6, 6, 0.6):
            sway = math.sin(t * 2 + x) * 0.05
            c.drawPath(poly([(x, 0), (x + 0.05 + sway, -0.5), (x + 0.1, 0)]), P(c=col((50, 44, 40))))
    card(c, W, H, t, d, DARK, "TRINITY SITE GROUND ZERO MONUMENT", "ERECTED 1965 · TODAY")
    small_tag(c, W, H, "2D ILLUSTRATION · PRESENT DAY", DARK)


@shot(143)
def s143(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -3, 3), y=-1.0, z=-1)
    sky(c, W, H, (8, 10, 20), (30, 34, 50))
    stars(c, W, H, t, n=80, top=0.4, a=0.4)
    with st.at(60):
        x = 0
        c.drawPath(poly([(x - 4, 0), (x - 4, -9), (x - 3, -14), (x + 3, -14), (x + 4, -9), (x + 8, -4), (x + 8, 0)]), P(c=col((60, 62, 66))))
        c.drawOval(skia.Rect(x - 3.2, -19.2, x + 3.2, -10.8), P(c=col((150, 170, 190)), stroke=0.25))
        c.drawCircle(0, -10, 14, P(c=col((150, 170, 200), 0.1), blur=6))
    with st.at(20):
        c.drawRect(skia.Rect(-200, -0.2, 200, 0.4), P(c=col((30, 30, 34))))
    with st.at(6):
        c.drawRect(skia.Rect(-100, 0, 100, 3), P(c=col((14, 18, 28))))
        rng = np.random.default_rng(3)
        for i in range(30):
            x = rng.uniform(-14, 14) + t * 0.25
            y = rng.uniform(0.05, 1.5)
            c.drawRect(skia.Rect(x - 0.12, y - 0.18, x + 0.12, y), P(c=col((255, 200, 140), 0.9)))
            c.drawCircle(x, y - 0.1, 0.4, P(c=col((255, 190, 120), 0.18), blur=0.3))
            c.drawRect(skia.Rect(x - 0.12, y + 0.05, x + 0.12, y + 0.4), P(c=col((255, 200, 140), 0.15), blur=0.06))
    card(c, W, H, t, d, DARK, "HIROSHIMA PEACE MEMORIAL (GENBAKU DOME)", "UNESCO WORLD HERITAGE SITE SINCE 1996 · LANTERNS ON 6 AUGUST")
    small_tag(c, W, H, "2D ILLUSTRATION · PRESENT DAY", DARK)


@shot(144)
def s144(c, t, d, W, H):
    callout(c, t, d, W, H, DARK, ["The U.S. Department of Energy vacates the 1954 decision to revoke his security clearance."], title="16 DECEMBER 2022")
    small_tag(c, W, H, "GRAPHICS", DARK)


@shot(145)
def s145(c, t, d, W, H):
    st = Stage(c, W, H, x=0, y=track(t, d, -2, -10), z=track(t, d, -4, -30))
    sky(c, W, H, (4, 6, 14), (20, 26, 44))
    stars(c, W, H, t, n=400, top=0.75, a=0.9)
    ground(c, W, H, st.cam, (6, 8, 10), (14, 16, 20))
    with st.at(300):
        c.drawPath(poly(ridge(np.random.default_rng(5), -900, 900, -30, 55, 160, 0.6)), P(c=col((14, 16, 22))))
    with st.at(80):
        rng = np.random.default_rng(2)
        c.drawRect(skia.Rect(-300, -6, 300, 0), P(c=col((10, 12, 14))))
        for i in range(120):
            c.drawCircle(rng.uniform(-60, 60), rng.uniform(-6, -1), rng.uniform(0.08, 0.2),
                         P(c=col((255, 214, 150), 0.6 + 0.3 * math.sin(t * rng.uniform(0.5, 2) + i))))
    with st.at(10):
        rng = np.random.default_rng(8)
        for x in np.arange(-30, 30, 2.2):
            pine(c, x + rng.uniform(-0.6, 0.6), rng.uniform(5, 8), (4, 6, 6))
    small_tag(c, W, H, "2D ILLUSTRATION", DARK)


@shot(146)
def s146(c, t, d, W, H):
    title_card(c, t, d, W, H, PAL["title"], "OPPENHEIMER", "THE MAN WHO CREATED THE POWER TO DESTROY THE WORLD")


@shot(147)
def s147(c, t, d, W, H):
    k = K(H)
    pal = PAL["title"]
    bg_fill(c, W, H, pal)
    lines = [("SOURCES AND DATA", 26, "semi"), ("", 10, "reg"),
             ("Archival photographs: U.S. National Archives / U.S. Air Force (Hiroshima and Nagasaki, 1945);", 18, "reg"),
             ("Los Alamos National Laboratory (Oppenheimer identification photograph; Trinity fireball, Berlyn Brixner).", 18, "reg"),
             ("Recreated documents are re-set from the originals and labelled RECREATION.", 18, "reg"),
             ("Maps: Natural Earth, world-atlas, us-atlas, Historical Basemaps (1938 boundaries).", 18, "reg"),
             ("Figures: U.S. Strategic Bombing Survey (1946); City of Hiroshima; Los Alamos National Laboratory.", 18, "reg"),
             ("", 10, "reg"),
             ("2D reconstructions are dramatised illustrations, not historical records.", 18, "med")]
    y = H * 0.3 - t * 6 * k
    for i, (s_, size, fc) in enumerate(lines):
        a = eout((t - 0.3 - i * 0.2) / 0.6)
        text(c, s_, W / 2, y, size * k, fc, pal["fg"] if fc != "reg" else pal["muted"], a, align="center", track=0.06 if fc == "semi" else 0)
        y += (size + 22) * k
