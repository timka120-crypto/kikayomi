"""Scenes 5-8 (shots 34-91): fission and war, Manhattan Project, Los Alamos, Trinity."""
import math

import numpy as np
import skia

from engine import *  # noqa
from env import *  # noqa
from kit import *  # noqa
from kit import _topo_rings
from reg import shot, Stage, track
from shots_a import mv, ping, globe_scene, smoke_puffs, _G
import style_test

WAR, COLD, DES = PAL["war"], PAL["cold"], PAL["desert"]
RED = WAR["accent"]
EUROPE = "+proj=laea +lat_0=52 +lon_0=15 +datum=WGS84"


def tag2d(c, W, H, pal):
    small_tag(c, W, H, "2D RECONSTRUCTION", pal)


def card(c, W, H, t, d, pal, a_, b_=None, t0=0.6):
    lines = [(a_, 28, "semi", "fg")] + ([(b_, 16, "mono", "fg")] if b_ else [])
    location_card(c, W, H, lines, win(t, t0, d - 0.2, 0.6), pal)


# =========================================================== SCENE 5
@shot(34)
def s34(c, t, d, W, H):
    m = mv("europe", EUROPE, (-12, 34, 42, 66))
    z = ease((t - 3.2) / 2.6)
    center = (lerp(13, 13.4, z), lerp(50.5, 52.5, z))
    width = lerp(3600, 1200, z)
    a_aus = clamp((t - 1.0) / 0.6)
    mat, mpx = draw_map(c, W, H, m, center, width, WAR, grat=5,
                        fills=[(("hist", "Germany"), RED, 1.0, False), ("040", WAR["land"], 1 - a_aus, False), ("040", RED, a_aus, True)],
                        markers=[(14.0, 50.65, "SUDETENLAND — OCT 1938", ping(t, 2.0) * (1 - z), "dot", (12, -10)),
                                 (13.29, 52.46, "BERLIN", ping(t, 3.6), "key", (14, -12))],
                        labels=[(14.2, 47.5, "AUSTRIA — MAR 1938", 13, a_aus * (1 - z)), (10.0, 51.0, "GERMAN REICH", 15, 1 - z)])
    map_title(c, W, H, WAR, "EUROPE 1938", "BOUNDARIES: HISTORICAL BASEMAPS 1938 · NATURAL EARTH", clamp(t / 0.8) * (1 - z))
    date_counter(c, W, H, WAR, "MARCH 1938" if t < 1.8 else ("OCTOBER 1938" if t < 3.4 else "DECEMBER 1938"), clamp(t / 0.6))
    legend(c, W, H, [(RED, "German Reich", "fill"), (mix(RED, (255, 255, 255), 0.25), "Annexed 1938", "hatch")], WAR, clamp((t - 0.5) / 0.6) * (1 - z), y=H * 0.78)
    location_card(c, W, H, [("BERLIN, GERMANY", 30, "semi", "fg"), ("DECEMBER 1938", 20, "med", "fg")], clamp((t - 4.4) / 0.8), WAR)
    small_tag(c, W, H, "GRAPHICS", WAR)


@shot(35)
def s35(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, 0.2, 0.8), y=-1.4, z=track(t, d, -0.8, 0.6))
    c.clear(col((30, 32, 32)))
    with st.at(5):
        wall(c, -6, 6, -4.5, (90, 92, 88), light=(-2.6, -2.8), light_r=3, light_c=(200, 210, 220), light_a=0.25)
        window(c, -3.6, -3.4, -2.0, -1.2, t, sky_c=((130, 140, 150), (180, 186, 190)))
        bookshelf(c, 2.6, 4.4, -3.4, -1.0, seed=8, wood=(60, 56, 50))
        for i in range(5):
            c.drawRect(skia.Rect(2.5 + i * 0.35, -0.9, 2.75 + i * 0.35, -0.6), P(c=col((140, 160, 150), 0.6)))
    with st.at(3.8):
        table(c, -1.2, 2.2, top=-0.9, colr=(70, 60, 50))
        for i in range(6):
            c.drawRect(skia.Rect(0.2 + i * 0.17, -1.1, 0.36 + i * 0.17, -0.9), P(c=col((70, 72, 76))))
        c.drawRect(skia.Rect(1.3, -1.3, 1.8, -0.9), P(c=col((50, 46, 40))))
        c.drawCircle(1.55, -1.12, 0.12, P(c=col((230, 224, 210))))
        a = -2.6 + 0.6 * abs(math.sin(t * 6)) + 0.4 * math.sin(t * 17)
        c.drawLine(1.55, -1.12, 1.55 + math.cos(a) * 0.1, -1.12 + math.sin(a) * 0.1, P(c=col((150, 30, 30)), stroke=0.012))
        p = stand(lean=16, head=14, sh_r=60, el_r=60)
        draw_person(c, STRASSMANN, idle(p, t, 2, 0.6), x=1.0, facing=1)
        look = smooth((t - 3.0) / 0.5) * (1 - smooth((t - 4.0) / 0.5))
        p2 = stand(lean=8, head=lerp(18, 0, look), sh_r=55, el_r=70, sh_l=40, el_l=80)
        draw_person(c, HAHN, idle(p2, t, 4, 0.4), x=-0.4, facing=1)
        c.drawRect(skia.Rect(0.0, -0.94, 0.4, -0.9), P(c=col((224, 216, 196))))
    card(c, W, H, t, d, WAR, "KAISER WILHELM INSTITUTE FOR CHEMISTRY", "BERLIN-DAHLEM · OTTO HAHN AND FRITZ STRASSMANN · DEC 1938")
    tag2d(c, W, H, WAR)


@shot(36)
def s36(c, t, d, W, H):
    k = K(H)
    c.clear(col((18, 22, 26)))
    cx, cy = W * 0.6, H * 0.5
    nucleus(c, cx, cy, 120 * k, 92, 143, t, k, tremble=1.0, a=eout(t / 0.8))
    nx = lerp(W * 0.05, cx - 150 * k, clamp(t / d))
    particle(c, nx, cy, 16 * k, (150, 156, 166))
    c.drawLine(nx - 200 * k, cy, nx - 30 * k, cy, P(c=col((150, 156, 166), 0.3), stroke=1.5 * k))
    a = eout((t - 1.0) / 0.8)
    label_line(c, cx + 80 * k, cy - 90 * k, cx + 220 * k, cy - 220 * k, "URANIUM-235 · 92 PROTONS, 143 NEUTRONS", k, WAR, a)
    label_line(c, nx, cy + 20 * k, nx + 40 * k, cy + 120 * k, "NEUTRON", k, WAR, a)
    small_tag(c, W, H, "GRAPHICS", WAR)


@shot(37)
def s37(c, t, d, W, H):
    k = K(H)
    c.clear(col((18, 22, 26)))
    cx, cy = W * 0.5, H * 0.5
    split = 2.2
    if t < split:
        st = 1 + 0.5 * smooth(t / split)
        c.save(); c.translate(cx, cy); c.scale(st, 1 / st ** 0.5); c.translate(-cx, -cy)
        nucleus(c, cx, cy, 120 * k, 92, 144, t, k, tremble=2.0)
        c.restore()
    else:
        u = eout((t - split) / 2.5)
        nucleus(c, cx - (90 + 260 * u) * k, cy - 20 * u * k, 90 * k, 56, 85, t, k, seed=8)
        nucleus(c, cx + (80 + 240 * u) * k, cy + 20 * u * k, 78 * k, 36, 56, t, k, seed=9)
        for i, ang in enumerate((-1.2, 0.4, 2.2)):
            r = (60 + 520 * u) * k
            particle(c, cx + math.cos(ang) * r, cy + math.sin(ang) * r, 14 * k, (150, 156, 166))
        energy_ring(c, cx, cy, (40 + 700 * u) * k, 1 - u, k)
        a = clamp((t - split - 1.2) / 0.6)
        text(c, "BARIUM-141", cx - 350 * k, cy - 140 * k, 18 * k, "semi", WAR["fg"], a, align="center", track=0.12)
        text(c, "KRYPTON-92", cx + 330 * k, cy + 140 * k, 18 * k, "semi", WAR["fg"], a, align="center", track=0.12)
        text(c, "3 NEUTRONS · ENERGY ≈ 200 MeV PER FISSION", W / 2, H * 0.88, 20 * k, "med", WAR["fg"], a, align="center", track=0.14)
    text(c, "NUCLEAR FISSION", 64 * k, 90 * k, 28 * k, "semi", WAR["fg"], eout(t / 0.8), track=0.2)
    small_tag(c, W, H, "GRAPHICS", WAR)


@shot(38)
def s38(c, t, d, W, H):
    if "nature" not in _G:
        _G["nature"] = journal_page(1300, 1800, "NATURE", "VOL. 143 · FEBRUARY 11, 1939",
                                    ["Disintegration of Uranium by Neutrons:", "a New Type of Nuclear Reaction"],
                                    "LISE MEITNER · O. R. FRISCH", "", cols=2)
    document_shot(c, t, d, W, H, _G["nature"], WAR, focus=(0.5, 0.12), highlight=(0.08, 0.2), tag="RECREATION · NATURE 143, 239 (1939)")
    location_card(c, W, H, [("11 FEBRUARY 1939", 26, "semi", "fg"), ("Meitner and Frisch explain the process and call it fission", 18, "reg", "accent")],
                  clamp((t - 2.2) / 0.7), WAR)


@shot(39)
def s39(c, t, d, W, H):
    m = mv("atl", "+proj=lcc +lat_1=40 +lat_2=55 +lat_0=48 +lon_0=-30 +datum=WGS84", (-80, 25, 25, 65))
    u = ease((t - 2.6) / 3.6)
    center = (lerp(14, -72.4, u), lerp(50, 41.0, u))
    width = math.exp(lerp(math.log(2600), math.log(1400), u)) * (1 + 1.6 * math.sin(math.pi * u))
    a_cz = clamp((t - 0.6) / 0.6)
    draw_map(c, W, H, m, center, width, WAR, grat=10,
             fills=[(("hist", "Germany"), RED, 1.0, False), ("040", RED, 1.0, True), ("203", RED, a_cz, True)],
             markers=[(-72.43, 41.0, "PECONIC, LONG ISLAND", ping(t, 5.4), "key", (14, -12))],
             labels=[(15.3, 49.6, "BOHEMIA AND MORAVIA — MAR 1939", 13, a_cz * (1 - u)), (-40, 45, "ATLANTIC OCEAN", 16, 1.0)])
    date_counter(c, W, H, WAR, "MARCH 1939" if t < 2.6 else "2 AUGUST 1939", clamp(t / 0.6))
    location_card(c, W, H, [("PECONIC, LONG ISLAND, NEW YORK", 28, "semi", "fg"), ("2 AUGUST 1939", 20, "med", "fg")], clamp((t - 5.6) / 0.8), WAR)
    small_tag(c, W, H, "GRAPHICS", WAR)


@shot(40)
def s40(c, t, d, W, H):
    if "einstein" not in _G:
        _G["einstein"] = typed_letter(1300, 1800,
            ["Albert Einstein", "Old Grove Rd.", "Nassau Point", "Peconic, Long Island", "", "August 2nd, 1939",
             "", "F.D. Roosevelt,", "President of the United States,", "White House", "Washington, D.C."],
            ["Sir:", "Some recent work by E.Fermi and L. Szilard, which has been communicated to me in manuscript, "
             "leads me to expect that the element uranium may be turned into a new and important source of energy "
             "in the immediate future."],
            sign=["Yours very truly,", "A. Einstein", "(Albert Einstein)"])
    document_shot(c, t, d, W, H, _G["einstein"], WAR, focus=(0.5, lerp(0.35, 0.6, t / d)), tone=(40, 34, 30),
                  tag="RECREATION · ORIGINAL: FDR PRESIDENTIAL LIBRARY")
    location_card(c, W, H, [("EINSTEIN–SZILÁRD LETTER", 26, "semi", "fg"), ("Delivered to Roosevelt on 11 October 1939", 18, "reg", "accent")],
                  clamp((t - 2.6) / 0.7), WAR)


@shot(41)
def s41(c, t, d, W, H):
    m = mv("europe", EUROPE, (-12, 34, 42, 66))
    a_pl = clamp((t - 0.8) / 0.8)
    draw_map(c, W, H, m, (track(t, d, 15, 19), 51.5), track(t, d, 2600, 1900), WAR, grat=5,
             fills=[(("hist", "Germany"), RED, 1.0, False), ("040", RED, 1.0, True), ("203", RED, 1.0, True),
                    (("hist", "Poland"), mix(RED, (120, 110, 150), 0.4), a_pl, True), (("hist", "USSR"), WAR["neutral"], 0.8, False)],
             labels=[(19.5, 52.0, "POLAND", 16, a_pl), (32, 55, "USSR", 16, 0.8)])
    legend(c, W, H, [(RED, "German Reich and annexed lands", "fill"), (mix(RED, (120, 110, 150), 0.4), "Poland — invaded 1 Sep (Germany) and 17 Sep 1939 (USSR)", "hatch")],
           WAR, clamp((t - 1.0) / 0.6), y=H * 0.16)
    location_card(c, W, H, [("1 SEPTEMBER 1939", 30, "semi", "fg"), ("GERMANY INVADES POLAND", 20, "med", "fg"),
                            ("Beginning of World War II", 18, "reg", "accent")], clamp((t - 1.6) / 0.8), WAR)
    small_tag(c, W, H, "GRAPHICS", WAR)


@shot(42)
def s42(c, t, d, W, H):
    m = mv("europe", EUROPE, (-12, 34, 42, 66))
    seq = [("208", 0.4, "DENMARK — APR 1940", (10.0, 56.0)), ("578", 0.9, "NORWAY — APR 1940", (10.5, 61.5)),
           ("528", 1.9, "NETHERLANDS — MAY 1940", (5.6, 52.3)), ("056", 2.2, "BELGIUM — MAY 1940", (4.6, 50.6)),
           ("442", 2.4, "", (6.1, 49.8)), ("250", 3.4, "FRANCE — JUNE 1940", (2.4, 46.8))]
    fills = [(("hist", "Germany"), RED, 1.0, False), ("040", RED, 1.0, True), ("203", RED, 1.0, True), (("hist", "Poland"), RED, 0.8, True)]
    labels = []
    for key, t0, lab, pos in seq:
        a = clamp((t - t0) / 0.6)
        fills.append((key, RED, a * (0.6 if key == "250" else 1.0), True))
        if lab:
            labels.append((pos[0], pos[1], lab, 12, a))
    draw_map(c, W, H, m, (track(t, d, 10, 6), track(t, d, 53, 51)), track(t, d, 2400, 3000), WAR, grat=5, fills=fills, labels=labels)
    date_counter(c, W, H, WAR, "APRIL 1940" if t < 1.8 else ("MAY 1940" if t < 3.2 else "JUNE 1940"), clamp(t / 0.6))
    text(c, "France: north and west occupied, south under the Vichy regime", 64 * K(H), H - 64 * K(H), 15 * K(H), "reg", WAR["muted"], clamp((t - 3.8) / 0.6))
    small_tag(c, W, H, "GRAPHICS", WAR)


@shot(43)
def s43(c, t, d, W, H):
    m = mv("world", "+proj=robin +datum=WGS84", (-180, -60, 180, 85))
    allied = WAR["allied"]
    axis = [("hist", "Germany"), ("hist", "Italy"), ("hist", "Empire of Japan")]
    allies = [("hist", "United States"), ("hist", "United Kingdom"), ("hist", "USSR"), "156"]
    fills = [(k_, RED, clamp((t - 0.6 - i * 0.3) / 0.6), False) for i, k_ in enumerate(axis)]
    fills += [(k_, allied, clamp((t - 1.8 - i * 0.3) / 0.6), False) for i, k_ in enumerate(allies)]
    draw_map(c, W, H, m, (track(t, d, 20, 60), 25), track(t, d, 34000, 30000), WAR, grat=30, fills=fills)
    map_title(c, W, H, WAR, "WORLD WAR II", "PRINCIPAL AXIS AND ALLIED POWERS · 1938 BOUNDARIES", clamp(t / 0.8))
    legend(c, W, H, [(RED, "Principal Axis powers: Germany, Italy, Japan", "fill"),
                     (allied, "Principal Allies: USA, UK, USSR, China", "fill")], WAR, clamp((t - 2.6) / 0.6), y=H * 0.82)
    small_tag(c, W, H, "GRAPHICS", WAR)


@shot(44)
def s44(c, t, d, W, H):
    if "nyt41" not in _G:
        _G["nyt41"] = newspaper(1300, 1800, "The New York Times", "NEW YORK, MONDAY, DECEMBER 8, 1941",
                                [("JAPAN WARS ON U.S. AND BRITAIN;", 58), ("MAKES SUDDEN ATTACK ON HAWAII;", 50),
                                 ("HEAVY FIGHTING AT SEA REPORTED", 50)], photo=True, seed=41)
    document_shot(c, t, d, W, H, _G["nyt41"], WAR, focus=(0.5, 0.15), tone=(34, 30, 28), tag="RECREATION · FRONT PAGE, 8 DECEMBER 1941")


@shot(45)
def s45(c, t, d, W, H):
    m = mv("pacific_hi", "+proj=lcc +lat_1=15 +lat_2=30 +lat_0=21 +lon_0=-158 +datum=WGS84", (-170, 10, -145, 30), "land-10m.json")
    z = ease((t - 0.4) / 3.8)
    draw_map(c, W, H, m, (lerp(-157, -157.95, z), lerp(21, 21.4, z)), math.exp(lerp(math.log(1600), math.log(110), z)), WAR, grat=2,
             markers=[(-157.95, 21.35, "PEARL HARBOR", ping(t, 3.4), "key", (14, -12))],
             labels=[(-155.5, 19.6, "HAWAII", 13, 1 - z), (-157.0, 21.9, "OAHU", 13, z)])
    location_card(c, W, H, [("PEARL HARBOR, HAWAII", 30, "semi", "fg"), ("7 DECEMBER 1941", 20, "med", "fg"),
                            ("7:48 AM LOCAL TIME · The United States enters the war", 18, "reg", "accent")], clamp((t - 3.6) / 0.8), WAR)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", WAR)


# =========================================================== SCENE 6
@shot(46)
def s46(c, t, d, W, H):
    st = Stage(c, W, H, x=0.0, y=-1.45, z=track(t, d, 1.0, 2.2), f=1100)
    c.clear(col((26, 30, 34)))
    with st.at(4.2):
        wall(c, -4, 4, -4, (70, 76, 80), light=(0, -1.8), light_r=2.5, light_c=(230, 236, 240), light_a=0.25)
        c.drawLine(1.2, 0, 1.2, -3.0, P(c=col((150, 130, 80)), stroke=0.04))
        c.drawPath(poly([(1.2, -3.0), (2.4, -2.9), (2.3, -2.0), (1.2, -2.1)]), P(c=col((120, 40, 40))))
        c.drawRect(skia.Rect(1.2, -3.0, 1.7, -2.6), P(c=col((40, 50, 90))))
    with st.at(3.6):
        draw_person(c, GROVES, idle(stand(sh_r=-2, sh_l=-2, el_r=10, el_l=10), t, 1, 0.5), x=0.0, facing=1, rim=0.4)
    location_card(c, W, H, [("LESLIE R. GROVES", 30, "semi", "fg"), ("Head of the Manhattan Project from 17 September 1942", 18, "reg", "accent")],
                  clamp((t - 0.6) / 0.8), COLD)
    tag2d(c, W, H, COLD)


@shot(47)
def s47(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, 0.2, 0.7), y=-1.3, z=track(t, d, -1.0, 0.3))
    c.clear(col((30, 32, 30)))
    with st.at(5):
        wall(c, -6, 6, -4.4, (96, 100, 92), light=(-1, -2.4), light_r=3.5, light_c=(220, 226, 230), light_a=0.2)
        window(c, -4.0, -3.4, -2.6, -1.2, t, sky_c=((150, 156, 160), (190, 192, 192)))
        c.drawRect(skia.Rect(-1.6, -3.3, 1.8, -1.4), P(c=col((200, 196, 176))))
        for i in range(30):
            rng = np.random.default_rng(i)
            c.drawCircle(rng.uniform(-1.5, 1.7), rng.uniform(-3.2, -1.5), 0.03, P(c=col((150, 40, 40))))
        for x in (2.6, 3.2):
            c.drawRect(skia.Rect(x, -1.4, x + 0.55, 0), P(c=col((80, 86, 82))))
    with st.at(3.6):
        table(c, -0.6, 1.8, top=-0.76, colr=(70, 50, 36))
        for j in range(4):
            c.drawRect(skia.Rect(0.9, -0.8 - j * 0.03, 1.5, -0.77 - j * 0.03), P(c=col((190, 170, 120))))
        phone = t > 3.6
        p = sit(head=12 if not phone else 0, sh_r=60 if not phone else 120, el_r=80 if not phone else 150, lean=10)
        p.sh_r += math.sin(t * 8) * 3 * (not phone)
        draw_person(c, GROVES, idle(p, t, 3, 0.4), x=0.2, facing=1)
        c.drawRect(skia.Rect(1.2, -0.84, 1.36, -0.77), P(c=col((20, 20, 20))))
        draw_person(c, SOLDIER if False else Look(height=1.8, build=1.0, suit=(118, 104, 74), suit_dark=(96, 84, 60), hat=None, hair=(60, 50, 40)),
                    idle(stand(sh_r=40, el_r=90), t, 6, 0.5), x=2.6, facing=-1)
    card(c, W, H, t, d, COLD, "WASHINGTON, D.C.", "WAR DEPARTMENT · SEPTEMBER 1942")
    tag2d(c, W, H, COLD)


@shot(48)
def s48(c, t, d, W, H):
    sway = math.sin(t * 2.1) * 0.012
    st = Stage(c, W, H, x=0.0 + sway, y=-1.25, z=track(t, d, -0.2, 0.6), f=1100)
    c.clear(col((20, 18, 18)))
    with st.at(3.2):
        c.drawRect(skia.Rect(-3, -3, 3, 0.2), P(c=col((70, 50, 40))))
        c.drawRect(skia.Rect(-0.7, -2.0, 0.7, -1.1), P(c=col((10, 12, 18))))
        for i in range(4):
            x = 0.7 - ((t * 0.9 + i * 0.4) % 1.6)
            c.drawCircle(x, -1.35 - i * 0.05, 0.015, P(c=col((255, 220, 160), 0.8)))
            c.drawLine(x - 0.1 * (i % 2), -1.1, x - 0.1 * (i % 2), -2.0, P(c=col((30, 30, 34), 0.6), stroke=0.02))
        c.drawCircle(0, -2.5, 0.25, P(c=col((255, 220, 160), 0.15), blur=0.3))
    with st.at(2.6):
        table(c, -0.35, 0.35, top=-0.72, colr=(90, 66, 46))
        c.drawRect(skia.Rect(-0.15, -0.74, 0.15, -0.72), P(c=col((220, 214, 196))))
        for side, L, x in ((1, OPP_TRINITY if False else OPPENHEIMER_1944, -0.75), (-1, GROVES, 0.75)):
            c.drawRect(skia.Rect(x - 0.35, -1.3, x + 0.35, -0.45), P(c=col((60, 40, 36))))
            p = sit(lean=10)
            if side == 1:
                gesture(p, t, 0.0, 0.8); p.hand_r = "cig"
            else:
                p.sh_r, p.el_r = 40, 120; p.sh_l, p.el_l = 40, 120
                p.head = 4 * math.sin(t * 1.5) + (8 if t > 4.5 else 0)
            draw_person(c, L, idle(p, t, side, 0.4), x=x, facing=side)
    card(c, W, H, t, d, COLD, "OCTOBER 1942", "RECONSTRUCTION OF THEIR DOCUMENTED MEETING ABOARD A PASSENGER TRAIN")
    tag2d(c, W, H, COLD)


@shot(49)
def s49(c, t, d, W, H):
    callout(c, t, d, W, H, COLD, ["Groves selects Oppenheimer to direct a new weapons laboratory: Project Y."], title="OCTOBER 1942")
    small_tag(c, W, H, "GRAPHICS", COLD)


@shot(50)
def s50(c, t, d, W, H):
    m = mv("usa", "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +datum=WGS84", (-126, 24, -66, 50))
    sites = [(-77.04, 38.9, "WASHINGTON, D.C. — HEADQUARTERS", 0.6, (14, -12)), (-87.6, 41.79, "CHICAGO — METALLURGICAL LAB", 1.4, (14, -12)),
             (-122.26, 37.87, "BERKELEY — RADIATION LAB", 2.2, (14, 18)), (-84.27, 36.01, "OAK RIDGE — URANIUM ENRICHMENT", 3.0, (14, 20)),
             (-119.65, 46.63, "HANFORD — PLUTONIUM PRODUCTION", 3.8, (14, -12)), (-106.3, 35.88, "LOS ALAMOS — WEAPON DESIGN", 4.6, (14, 18))]
    routes = [([(-77.04, 38.9), (lo, la)], clamp((t - t0 - 0.2) / 0.8), COLD["muted"]) for lo, la, _, t0, _ in sites[1:]]
    mat, mpx = draw_map(c, W, H, m, (-96, 38.5), track(t, d, 5600, 5000), COLD, grat=10, routes=routes,
                        markers=[(lo, la, name, ping(t, t0), "key" if "LOS" in name else "dot", off) for lo, la, name, t0, off in sites])
    map_title(c, W, H, COLD, "THE MANHATTAN PROJECT, 1942–1945", "PRINCIPAL SITES", clamp(t / 0.8))
    scale_bar(c, W, H, mpx, COLD)
    small_tag(c, W, H, "GRAPHICS · NATURAL EARTH", COLD)


def snow(c, t, x0, x1, top, n=120, seed=3, a=0.8):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1) + math.sin(t + i) * 0.3
        y = (rng.uniform(top, 0) + t * rng.uniform(0.5, 1.2)) % (-top) + top
        c.drawCircle(x, y, rng.uniform(0.02, 0.05), P(c=col((240, 242, 246), a)))


@shot(51)
def s51(c, t, d, W, H):
    st = Stage(c, W, H, x=0.5, y=track(t, d, -9, -1.6), z=-2)
    sky(c, W, H, (196, 200, 206), (226, 228, 230))
    ground(c, W, H, st.cam, (220, 222, 226), (236, 236, 238))
    with st.at(24):
        c.drawRect(skia.Rect(-20, -12, 20, 0), P(c=col((170, 164, 150))))
        for x in np.arange(-20, 20.1, 1.4):
            c.drawRect(skia.Rect(x, -13, x + 0.8, -12), P(c=col((170, 164, 150))))
        for x in (-16, 12):
            c.drawRect(skia.Rect(x, -18, x + 4, 0), P(c=col((160, 154, 140))))
            for xx in np.arange(x, x + 4.1, 1.0):
                c.drawRect(skia.Rect(xx, -18.8, xx + 0.6, -18), P(c=col((160, 154, 140))))
        for x in np.arange(-10, 10, 3):
            c.drawPath(poly([(x, -3), (x, -7), (x + 0.9, -8), (x + 1.8, -7), (x + 1.8, -3)]), P(c=col((90, 86, 80))))
        c.drawPath(poly([(-1.2, 0), (-1.2, -4), (0, -5.2), (1.2, -4), (1.2, 0)]), P(c=col((50, 46, 44))))
        snow(c, t, -20, 20, -18, n=60, seed=5)
    with st.at(7):
        for i in range(3):
            draw_person(c, OFFICIAL, walk_pose(t * 4.6 + i, 0.8), x=-4 + t * 0.9 + i * 0.9, facing=1)
    with st.at(3):
        snow(c, t, -4, 4, -4, n=80, seed=9)
    card(c, W, H, t, d, COLD, "STAGG FIELD, UNIVERSITY OF CHICAGO", "2 DECEMBER 1942")
    tag2d(c, W, H, COLD)


def graphite_pile(c, x, w=6.0, h=6.0):
    for row in range(int(h / 0.12)):
        y = -row * 0.12
        frac = 1 - abs((row * 0.12) / h * 2 - 1) ** 2
        half = w / 2 * (0.5 + 0.5 * math.sqrt(max(0, frac)))
        c.drawRect(skia.Rect(x - half, y - 0.12, x + half, y), P(c=col((22 + (row % 2) * 6, 22 + (row % 2) * 6, 24))))
        for bx in np.arange(x - half, x + half, 0.4):
            c.drawLine(bx + (row % 2) * 0.2, y - 0.12, bx + (row % 2) * 0.2, y, P(c=col((50, 50, 52)), stroke=0.01))
    c.drawRect(skia.Rect(x - w / 2 - 0.3, -h - 0.1, x - w / 2 - 0.2, 0), P(c=col((120, 96, 70))))
    c.drawRect(skia.Rect(x + w / 2 + 0.2, -h - 0.1, x + w / 2 + 0.3, 0), P(c=col((120, 96, 70))))


@shot(52)
def s52(c, t, d, W, H):
    st = Stage(c, W, H, x=0.5, y=track(t, d, -1.4, -5.6), z=-3)
    c.clear(col((14, 14, 16)))
    with st.at(9):
        wall(c, -10, 10, -9, (60, 58, 54), light=(0, -6), light_r=6, light_c=(255, 240, 210), light_a=0.2)
        c.drawRect(skia.Rect(-9, -6.6, 9, -6.3), P(c=col((50, 44, 38))))
        crowd_row(c, -4, 3, [OFFICIAL, STUDENT2, STUDENT], seated=False, t=t, seed=2, spacing=0.9, z=9)
    with st.at(7):
        c.save(); c.translate(0, -6.3); c.restore()
    with st.at(6.5):
        graphite_pile(c, 0.0, 7.0, 6.2)
        pull = smooth(t / d) * 1.2
        c.drawRect(skia.Rect(3.5 + pull, -2.6, 6.0 + pull, -2.5), P(c=col((170, 170, 176))))
        p = stand(lean=-12, sh_r=80, el_r=10, sh_l=80, el_l=10)
        draw_person(c, Look(height=1.76, build=1.05, suit=(80, 80, 82), suit_dark=(64, 64, 66), hat=None, hair=(50, 44, 40)),
                    p, x=5.4 + pull, facing=-1)
    rng = np.random.default_rng(1)
    with st.at(4):
        for i in range(60):
            c.drawCircle(rng.uniform(-6, 6) + math.sin(t * 0.3 + i) * 0.2, rng.uniform(-6, 0), 0.01, P(c=col((200, 200, 200), 0.3)))
    card(c, W, H, t, d, COLD, "CHICAGO PILE-1", "GRAPHITE, URANIUM AND URANIUM OXIDE · SQUASH COURT UNDER STAGG FIELD")
    tag2d(c, W, H, COLD)


@shot(53)
def s53(c, t, d, W, H):
    st = Stage(c, W, H, x=0.8, y=-1.5, z=track(t, d, -0.4, 0.7))
    c.clear(col((20, 20, 22)))
    with st.at(4.6):
        wall(c, -6, 6, -4.5, (66, 62, 56), light=(0.6, -2.2), light_r=3, light_a=0.25)
        crowd_row(c, -2.6, -0.4, [OFFICIAL, STUDENT2], seated=False, t=t, seed=4, spacing=0.9, shade=0.2)
    with st.at(3.4):
        table(c, 0.4, 2.4, top=-0.95, colr=(70, 54, 40))
        c.drawRect(skia.Rect(1.3, -1.35, 2.2, -0.95), P(c=col((60, 62, 66))))
        c.drawRect(skia.Rect(1.36, -1.3, 2.14, -1.02), P(c=col((230, 226, 214))))
        pts = [(1.38 + i * 0.012, -1.06 - 0.2 * (math.exp(i / 60 * clamp(t / d) * 3) - 1) / 19) for i in range(int(64 * clamp(t / d)) + 2)]
        if len(pts) > 1:
            c.drawPath(poly(pts, close=False), P(c=col((40, 40, 140)), stroke=0.008))
        p = stand(lean=10, head=lerp(14, 4, 0.5 + 0.5 * math.sin(t * 0.9)), sh_r=70, el_r=70, sh_l=60, el_l=80)
        draw_person(c, FERMI, p, x=0.4, facing=1, rim=0.5)
        c.drawRect(skia.Rect(0.62, -1.28, 0.95, -1.24), P(c=col((220, 216, 200))))
        if t > d - 1.4:
            c.drawCircle(0.45, -1.62, 0.0, P())
    location_card(c, W, H, [("ENRICO FERMI", 28, "semi", "fg"), ("PHYSICIST, METALLURGICAL LABORATORY", 16, "mono", "fg")], win(t, 0.6, d - 0.2, 0.6), COLD)
    tag2d(c, W, H, COLD)


@shot(54)
def s54(c, t, d, W, H):
    k = K(H)
    c.clear(col((16, 21, 28)))
    gens = 6
    x0 = W * 0.08
    dx = W * 0.14
    shown = min(gens, int(t / 0.7) + 1)
    rods = smooth((t - 4.6) / 0.8)
    nodes = [[(x0, H * 0.5)]]
    for g in range(1, gens):
        prev = nodes[-1]
        nxt = []
        for i, (px, py) in enumerate(prev):
            spread = H * 0.32 / (2 ** (g - 1))
            for s in (-1, 1):
                nxt.append((x0 + g * dx, py + s * spread * 0.5))
        nodes.append(nxt)
    for g in range(1, shown):
        a = clamp((t - g * 0.7) / 0.5) * (1 - rods * clamp((g - 2) / 3))
        for i, (x, y) in enumerate(nodes[g]):
            px, py = nodes[g - 1][i // 2]
            c.drawLine(px, py, x, y, P(c=col((150, 156, 166), a * 0.6), stroke=1.2 * k))
    for g in range(shown):
        a = clamp((t - g * 0.7) / 0.5) * (1 - rods * clamp((g - 2) / 3))
        for x, y in nodes[g]:
            c.drawCircle(x, y, 8 * k, P(c=col((214, 150, 86), a)))
            c.drawCircle(x, y, 14 * k, P(c=col((255, 220, 170), a * 0.25), blur=6 * k))
        text(c, f"GEN {g + 1}", nodes[g][0][0], H * 0.9, 13 * k, "mono", COLD["muted"], a, align="center")
    if rods > 0:
        for i in range(3):
            x = x0 + (2.5 + i) * dx
            c.drawRect(skia.Rect(x - 8 * k, 0, x + 8 * k, H * rods * 0.9), P(c=col((120, 126, 132), 0.9)))
        text(c, "CONTROL RODS ABSORB NEUTRONS", W * 0.62, H * 0.12, 18 * k, "semi", COLD["fg"], rods, track=0.14)
    text(c, "CHAIN REACTION", 64 * k, 90 * k, 28 * k, "semi", COLD["fg"], eout(t / 0.8), track=0.2)
    text(c, "k > 1 : each fission triggers more than one more", 64 * k, 124 * k, 16 * k, "reg", COLD["muted"], eout((t - 0.5) / 0.8))
    small_tag(c, W, H, "GRAPHICS", COLD)


@shot(55)
def s55(c, t, d, W, H):
    k = K(H)
    c.clear(col((10, 10, 12)))
    c.save(); c.translate(W * 0.5, H * 0.95); c.scale(110 * k, 110 * k)
    graphite_pile(c, 0.0, 12, 9)
    c.restore()
    c.drawRect(skia.Rect(0, 0, W, H), P(c=col((0, 0, 0), 0.45)))
    sec = int(lerp(20, 25, clamp(t / 3)))
    text(c, f"3:{sec:02d} PM", W * 0.5, H * 0.38, 64 * k, "monom", COLD["accent"], eout(t / 0.6), align="center")
    location_card(c, W, H, [("CHICAGO PILE-1", 34, "semi", "fg"), ("2 DECEMBER 1942 · 3:25 PM LOCAL TIME", 20, "med", "fg"),
                            ("First self-sustaining nuclear chain reaction", 18, "reg", "accent")], clamp((t - 0.8) / 0.8), COLD)
    small_tag(c, W, H, "GRAPHICS", COLD)


@shot(56)
def s56(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -40, 40), y=-30, z=-60, f=1200)
    sky(c, W, H, (170, 180, 180), (200, 200, 190), horizon=0.3)
    ground(c, W, H, st.cam, (110, 96, 70), (130, 130, 100))
    with st.at(500):
        c.drawPath(poly(ridge(np.random.default_rng(6), -1500, 1500, -30, 40, 120, 0.5)), P(c=col((100, 120, 96))))
    with st.at(160):
        c.drawRect(skia.Rect(-400, -18, 400, 0), P(c=col((150, 150, 144))))
        for x in np.arange(-400, 400, 6):
            c.drawLine(x, -18, x, 0, P(c=col((120, 120, 116)), stroke=0.6))
        for i, x in enumerate((-120, -20, 90)):
            c.drawLine(x, 0, x, -60, P(c=col((60, 60, 60)), stroke=1.2))
            arm = math.sin(t * 0.3 + i) * 10
            c.drawLine(x, -60, x + 40, -60 + arm * 0.2, P(c=col((60, 60, 60)), stroke=1.0))
            c.drawLine(x + 30, -60, x + 30, -30, P(c=col((60, 60, 60)), stroke=0.3))
    with st.at(60):
        for i in range(12):
            car_1940(c, -120 + ((t * 8 + i * 25) % 260), (80, 84, 60), wheel_t=t)
        for i in range(30):
            draw_person(c, SOLDIER if i % 3 == 0 else CREW, walk_pose(t * 5 + i, 0.8), x=-100 + i * 7 + t * 1.2, facing=1)
    card(c, W, H, t, d, COLD, "K-25 PLANT, OAK RIDGE, TENNESSEE", "1944 · URANIUM-235 ENRICHMENT")
    tag2d(c, W, H, COLD)


@shot(57)
def s57(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.5, 1.5), y=-1.2, z=-0.5)
    c.clear(col((40, 42, 44)))
    with st.at(4.5):
        wall(c, -10, 10, -4, (110, 116, 112), light=(0, -3), light_r=6, light_c=(230, 236, 240), light_a=0.2)
        for x in np.arange(-8, 8, 1.6):
            c.drawRect(skia.Rect(x, -2.0, x + 1.3, -0.6), P(c=col((70, 80, 84))))
            for j in range(3):
                cx_ = x + 0.3 + j * 0.35
                c.drawCircle(cx_, -1.6, 0.12, P(c=col((230, 226, 210))))
                a = -2.0 + 0.5 * math.sin(t * 1.3 + x + j)
                c.drawLine(cx_, -1.6, cx_ + math.cos(a) * 0.1, -1.6 + math.sin(a) * 0.1, P(c=col((30, 30, 30)), stroke=0.015))
            for j in range(4):
                c.drawCircle(x + 0.2 + j * 0.3, -1.05, 0.04, P(c=col((220, 80, 60) if (j + int(t * 2)) % 4 == 0 else (60, 160, 90))))
    with st.at(3.6):
        for i, x in enumerate(np.arange(-7.4, 8, 1.6)):
            c.drawLine(x + 0.6, -0.55, x + 0.6, 0, P(c=col((50, 50, 50)), stroke=0.04))
            p = sit(sh_r=80, el_r=40, head=-8, lean=8, bob=0.4)
            idle(p, t, i, 0.6)
            p.sh_r += 6 * math.sin(t * 1.7 + i)
            draw_person(c, [WOMAN, WOMAN2][i % 2], p, x=x, facing=1)
    card(c, W, H, t, d, COLD, "Y-12 PLANT, OAK RIDGE", "CALUTRON OPERATORS · ELECTROMAGNETIC URANIUM SEPARATION, 1944")
    tag2d(c, W, H, COLD)


@shot(58)
def s58(c, t, d, W, H):
    inside = smooth((t - d * 0.5) / 0.8)
    if inside < 1:
        st = Stage(c, W, H, x=0, y=-3, z=track(t, d, -20, -8))
        sky(c, W, H, (170, 186, 200), (220, 214, 196))
        ground(c, W, H, st.cam, (150, 134, 100), (176, 162, 130))
        with st.at(300):
            c.drawPath(poly(ridge(np.random.default_rng(2), -800, 800, -10, 14, 90, 0.3)), P(c=col((170, 150, 120))))
        with st.at(80):
            c.drawRect(skia.Rect(-300, -0.8, 300, 0.4), P(c=col((110, 140, 156))))
        with st.at(30):
            c.drawRect(skia.Rect(-8, -14, 8, 0), P(c=col((176, 172, 160))))
            c.drawRect(skia.Rect(4, -22, 6, -14), P(c=col((150, 146, 136))))
            c.drawRect(skia.Rect(-12, -6, -8, 0), P(c=col((160, 156, 146))))
        with st.at(6):
            rng = np.random.default_rng(3)
            for x in np.arange(-10, 10, 1.2):
                c.drawCircle(x + rng.uniform(-0.3, 0.3) + math.sin(t + x) * 0.03, -0.25, 0.3, P(c=col((120, 120, 90))))
    if inside > 0:
        c.saveLayerAlpha(None, int(255 * inside))
        st = Stage(c, W, H, x=0, y=track(t, d, -1, -6), z=-2)
        c.clear(col((40, 44, 48)))
        with st.at(8):
            c.drawRect(skia.Rect(-8, -12, 8, 0), P(c=col((110, 112, 110))))
            for x in np.arange(-7.6, 7.6, 0.5):
                for y in np.arange(-11.6, -0.4, 0.5):
                    c.drawCircle(x, y, 0.1, P(c=col((70, 72, 72))))
            ly = -5 + 3 * math.sin(t * 0.3)
            c.drawRect(skia.Rect(-2, ly, 2, ly + 0.2), P(c=col((180, 150, 60))))
            draw_person(c, CREW, idle(stand(sh_r=110, el_r=20), t, 1, 0.8), x=0.0, facing=1)
        c.restore()
    card(c, W, H, t, d, COLD, "B REACTOR, HANFORD, WASHINGTON", "1944 · PLUTONIUM PRODUCTION")
    tag2d(c, W, H, COLD)


@shot(59)
def s59(c, t, d, W, H):
    k = K(H)
    bg_fill(c, W, H, COLD)
    blue, amber = (110, 160, 200), (214, 150, 86)
    y1, y2 = H * 0.36, H * 0.64
    xs = (W * 0.12, W * 0.45, W * 0.8)
    for y, colr, a_, b_, c_ in ((y1, blue, "OAK RIDGE", "URANIUM-235", "GUN-TYPE DESIGN"), (y2, amber, "HANFORD", "PLUTONIUM-239", "IMPLOSION DESIGN")):
        prog = clamp((t - 0.4) / 2.0)
        c.drawLine(xs[0], y, lerp(xs[0], xs[1], prog), y, P(c=col(colr), stroke=3 * k))
        for i, (x, lab) in enumerate(zip(xs[:2], (a_, c_))):
            a = clamp((t - 0.3 - i * 1.6) / 0.5)
            c.drawCircle(x, y, 12 * k, P(c=col(colr, a)))
            text(c, lab, x, y - 30 * k, 22 * k, "semi", COLD["fg"], a, align="center", track=0.12)
        text(c, b_, (xs[0] + xs[1]) / 2, y + 40 * k, 18 * k, "mono", colr, clamp((t - 1.0) / 0.6), align="center")
        p2 = clamp((t - 2.6) / 1.4)
        c.drawLine(xs[1], y, lerp(xs[1], xs[2], p2), lerp(y, H * 0.5, p2), P(c=col(colr), stroke=3 * k))
    a = clamp((t - 3.8) / 0.6)
    c.drawCircle(xs[2], H * 0.5, 18 * k, P(c=col(COLD["accent"], a)))
    text(c, "LOS ALAMOS", xs[2], H * 0.5 - 36 * k, 24 * k, "semi", COLD["fg"], a, align="center", track=0.12)
    text(c, "WEAPON DESIGN AND ASSEMBLY", xs[2], H * 0.5 + 46 * k, 15 * k, "mono", COLD["muted"], a, align="center")
    small_tag(c, W, H, "GRAPHICS", COLD)


# =========================================================== SCENE 7
@shot(60)
def s60(c, t, d, W, H):
    z = ease(t / 6.0)
    R = math.exp(lerp(math.log(330 * K(H)), math.log(1050 * K(H)), z))
    globe_scene(c, W, H, t, COLD, lerp(-25, -104.5, ease(t / 5.6)), lerp(12, 33.2, ease(t / 5.8)), R,
                cx=W * lerp(0.56, 0.57, z), cy=H * lerp(0.52, 0.56, z), points=[(-106.3, 35.88, "LOS ALAMOS", clamp((t - 4.6) / 0.6))])
    location_card(c, W, H, [("LOS ALAMOS, NEW MEXICO", 32, "semi", "fg"), ("PROJECT Y · LABORATORY OPERATIONS BEGIN SPRING 1943", 16, "mono", "fg")],
                  clamp((t - 5.2) / 0.9), COLD)
    small_tag(c, W, H, "3D GRAPHICS · NATURAL EARTH", COLD)


def log_building(c, x, w, h, colr=(120, 84, 56)):
    c.drawRect(skia.Rect(x, -h, x + w, 0), P(c=col(colr)))
    for yy in np.arange(-h, 0, 0.3):
        c.drawLine(x, yy, x + w, yy, P(c=col(mix(colr, (0, 0, 0), 0.3)), stroke=0.06))
    c.drawPath(poly([(x - 0.6, -h), (x + w / 2, -h - w * 0.18), (x + w + 0.6, -h)]), P(c=col((70, 60, 50))))
    for wx in np.arange(x + 1, x + w - 1, 2.2):
        c.drawRect(skia.Rect(wx, -h * 0.75, wx + 1.0, -h * 0.45), P(c=col((40, 34, 30))))
        c.drawRect(skia.Rect(wx, -h * 0.35, wx + 1.0, -h * 0.08), P(c=col((40, 34, 30))))
    c.drawRect(skia.Rect(x - 0.2, -h * 0.42, x + w + 0.2, -h * 0.38), P(c=col((80, 60, 44))))


def mesa_bg(c, st, t, snow_on=False, fog_c=(172, 178, 182)):
    with st.at(420):
        c.drawPath(poly(ridge(np.random.default_rng(5), -900, 900, -30, 55, 160, 0.6)), P(c=col(fog((104, 114, 124), 420, fog_c, amount=0.55))))
    with st.at(60):
        rng = np.random.default_rng(7)
        for x in np.arange(-160, 160, 3.2):
            pine(c, x + rng.uniform(-2, 2), rng.uniform(9, 15), fog((58, 70, 58), 60, fog_c, amount=0.55))


@shot(61)
def s61(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -2, 1.5), y=-1.4, z=0.0)
    sky(c, W, H, (150, 170, 190), (214, 220, 224))
    ground(c, W, H, st.cam, (210, 212, 214), (190, 194, 196))
    mesa_bg(c, st, t)
    with st.at(22):
        log_building(c, -16, 14, 6)
        log_building(c, 6, 10, 5)
    with st.at(12):
        for i in range(4):
            xx = -6 + ((t * 2.6 * (1 if i % 2 else -1) + i * 3) % 12)
            p = walk_pose(t * 8 + i, 1.2)
            draw_person(c, Look(height=1.4, build=0.8, suit=(120, 60, 40) if i % 2 else (60, 70, 100), suit_dark=(90, 50, 34), hat=None, hair=(70, 50, 30)),
                        p, x=xx, facing=1 if i % 2 else -1)
    with st.at(6):
        cx = lerp(-12, -1.5, eout(t / 2.8))
        car_1940(c, cx, (52, 64, 48), wheel_t=cx)
        out = smooth((t - 3.0) / 0.8)
        if out > 0:
            c.saveLayerAlpha(None, int(255 * out))
            p1 = stand(sh_r=lerp(0, 95, smooth((t - 4.4) / 0.6)), el_r=10, head=-4)
            draw_person(c, OPPENHEIMER_1944, p1, x=cx + 2.8, facing=1)
            draw_person(c, GROVES, idle(stand(), t, 2, 0.6), x=cx + 1.6, facing=1)
            c.restore()
    card(c, W, H, t, d, COLD, "LOS ALAMOS RANCH SCHOOL", "16 NOVEMBER 1942")
    tag2d(c, W, H, COLD)


@shot(62)
def s62(c, t, d, W, H):
    st = Stage(c, W, H, x=0.5, y=track(t, d, -1.2, -5), z=track(t, d, -1, -6))
    sky(c, W, H, (130, 160, 196), (220, 220, 214))
    ground(c, W, H, st.cam, (130, 110, 90), (190, 186, 180))
    mesa_bg(c, st, t)
    with st.at(24):
        log_building(c, -10, 20, 8, (126, 88, 58))
        for x in (14, 20):
            c.drawRect(skia.Rect(x, -5, x + 4.5, 0), P(c=col((200, 190, 160))))
            for xx in np.arange(x, x + 4.6, 0.6):
                c.drawLine(xx, -5, xx, 0, P(c=col((140, 120, 90)), stroke=0.08))
    with st.at(10):
        car_1940(c, -10 + t * 2.2, (70, 76, 50), wheel_t=t)
        for i in range(4):
            p = stand(sh_r=100 + 30 * math.sin(t * 4 + i), el_r=20)
            draw_person(c, CREW, p, x=4 + i * 1.6, facing=1 if i % 2 else -1)
        c.drawRect(skia.Rect(3.6, -0.4, 9.5, -0.2), P(c=col((170, 140, 100))))
    card(c, W, H, t, d, COLD, "FULLER LODGE, LOS ALAMOS", "EARLY 1943")
    tag2d(c, W, H, COLD)


def tech_area(c, st, t, lit=0.0):
    with st.at(17):
        base = (84, 98, 78)
        for bx in (-30, -13, 4, 21):
            building(c, bx, 13, 6.2, base, rows=2, seed=abs(bx), lit=lit)
            c.drawRect(skia.Rect(bx + 9.7, -8.4, bx + 10.2, -6.8), P(c=col((50, 56, 46))))
    with st.at(18):
        tc = (86, 84, 76)
        for lx in (-1.4, 1.4):
            c.drawLine(9 + lx, 0, 9 + lx * 0.6, -9, P(c=col(tc), stroke=0.18))
        c.drawRect(skia.Rect(7.6, -12.5, 10.4, -9), P(c=col(tc)))


@shot(63)
def s63(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -10, 10), y=-14, z=-30, f=1300)
    sky(c, W, H, (128, 140, 150), (184, 188, 188))
    ground(c, W, H, st.cam, (96, 86, 72), (150, 148, 140))
    mesa_bg(c, st, t)
    tech_area(c, st, t)
    with st.at(10):
        for i in range(10):
            draw_person(c, [SCIENTIST, SOLDIER, OFFICIAL][i % 3], walk_pose(t * 5 + i, 0.9), x=-20 + i * 4 + t * (1 if i % 2 else -1),
                        facing=1 if i % 2 else -1)
        car_1940(c, -16 + t * 4, (60, 70, 50), wheel_t=t * 2)
    card(c, W, H, t, d, COLD, "TECHNICAL AREA, LOS ALAMOS", "1944")
    tag2d(c, W, H, COLD)


@shot(64)
def s64(c, t, d, W, H):
    st = Stage(c, W, H, x=0.8, y=-1.4, z=track(t, d, -0.5, 0.6))
    sky(c, W, H, (150, 166, 180), (210, 212, 210))
    ground(c, W, H, st.cam, (110, 100, 88), (170, 166, 156))
    mesa_bg(c, st, t)
    with st.at(9):
        for x in np.arange(-20, 20, 2.5):
            c.drawLine(x, 0, x, -2.4, P(c=col((80, 80, 80)), stroke=0.06))
        for y in (-2.4, -1.6, -0.8):
            c.drawLine(-20, y, 20, y, P(c=col((90, 90, 90)), stroke=0.02))
    with st.at(5):
        c.drawRect(skia.Rect(2.2, -2.4, 3.6, 0), P(c=col((120, 110, 90))))
        c.drawRect(skia.Rect(2.4, -1.9, 3.4, -1.2), P(c=col((60, 70, 80))))
        up = smooth((t - 3.0) / 0.8)
        c.save(); c.translate(2.0, -1.0); c.rotate(-80 * up)
        c.drawRect(skia.Rect(-5, -0.06, 0, 0.06), P(c=col((230, 230, 226))))
        for i in range(5):
            c.drawRect(skia.Rect(-5 + i, -0.06, -4.5 + i, 0.06), P(c=col((190, 40, 36))))
        c.restore()
        cx = lerp(-5.5, -4.2, eout(t / 1.5)) + lerp(0, 9, smooth((t - 3.8) / 1.4))
        car_1940(c, cx, (40, 40, 44), wheel_t=cx)
        p = stand(sh_r=lerp(80, 20, smooth((t - 2.4) / 0.5)), el_r=40, head=4)
        draw_person(c, SOLDIER, idle(p, t, 1, 0.5), x=0.8, facing=-1)
    card(c, W, H, t, d, COLD, "MAIN GATE, LOS ALAMOS", "PASSES CHECKED BY MILITARY POLICE")
    tag2d(c, W, H, COLD)


@shot(65)
def s65(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.5, 0.6), y=-1.4, z=track(t, d, -1.6, -0.4))
    c.clear(col((40, 36, 32)))
    with st.at(6.5):
        wall(c, -8, 8, -4, (130, 116, 96), light=(0, -2.6), light_r=5, light_a=0.22)
        blackboard(c, -2.6, -3.0, 3.4, -1.1, ["σ_f ≈ 1.5 barn", "ν ≈ 2.5 neutrons", "critical mass ∝ 1/ρ²"], size=0.2, gap=1.8)
        c.drawCircle(2.4, -2.1, 0.45, P(c=col((222, 224, 214), 0.85), stroke=0.015))
        draw_person(c, Look(height=1.72, build=0.9, suit=(80, 84, 90), suit_dark=(64, 68, 72), hat=None, hair=(40, 34, 30)),
                    stand(sh_r=lerp(30, 115, 0.5 + 0.5 * math.sin(t * 0.8)), el_r=20, head=-2), x=-1.6, facing=1)
    with st.at(4.0):
        crowd_row(c, -5, 5, [STUDENT, SCIENTIST, WOMAN2, STUDENT2], t=t, seed=11, spacing=0.85, shade=0.15)
    with st.at(3.2):
        p = sit(lean=0, sh_r=10, el_r=60, hand_r="cig", head=-2)
        draw_person(c, OPPENHEIMER_1944, idle(p, t, 2, 0.4), x=0.6, facing=1, rim=0.3)
        smoke_puffs(c, t, 0.95, -1.4, n=10, seed=6, a=0.12)
    location_card(c, W, H, [("ROBERT SERBER'S LECTURES", 28, "semi", "fg"), ("LOS ALAMOS · APRIL 1943", 16, "mono", "fg")], win(t, 0.6, d - 0.2, 0.6), COLD)
    tag2d(c, W, H, COLD)


@shot(66)
def s66(c, t, d, W, H):
    if "primer" not in _G:
        _G["primer"] = report_cover(1300, 1800, [("LA - 1", 44)], [("THE", 48), ("LOS ALAMOS", 72), ("PRIMER", 72)],
                                    [("Notes on lectures by R. Serber", 28), ("Los Alamos · April 1943", 28)], stamp="DECLASSIFIED")
    document_shot(c, t, d, W, H, _G["primer"], COLD, focus=(0.5, 0.45), tag="RECREATION · LOS ALAMOS REPORT LA-1")


@shot(67)
def s67(c, t, d, W, H):
    key = ("street", W)
    if key not in _G:
        _G[key] = style_test.ShotStreet(W, H)
    _G[key].draw(c, t + 1.5)


@shot(68)
def s68(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.0, 1.2), y=-1.3, z=track(t, d, -1.2, -0.2))
    c.clear(col((36, 38, 40)))
    with st.at(6):
        wall(c, -8, 8, -4, (120, 124, 120), light=(0, -3), light_r=6, light_c=(230, 236, 240), light_a=0.2)
        window(c, -6.8, -3.0, -5.4, -1.2, t)
        p = sit(head=10, sh_r=60, el_r=80, lean=12)
        table(c, 3.2, 5.2, top=-0.76, colr=(80, 60, 44))
        draw_person(c, BETHE, idle(p, t, 3, 0.5), x=3.0, facing=1)
        for j in range(6):
            c.drawRect(skia.Rect(3.6 + j * 0.2, -0.79, 3.78 + j * 0.2, -0.76), P(c=col((230, 226, 214))))
    with st.at(4.0):
        for i, x in enumerate(np.arange(-6, 3, 1.5)):
            table(c, x + 0.2, x + 1.3, top=-0.76, colr=(90, 70, 50))
            c.drawRect(skia.Rect(x + 0.5, -1.0, x + 1.1, -0.76), P(c=col((60, 64, 70))))
            car = 0.08 * math.sin(t * 6 + i)
            c.drawRect(skia.Rect(x + 0.45 + car, -1.06, x + 1.15 + car, -1.0), P(c=col((90, 94, 100))))
            p = sit(sh_r=80 + 8 * math.sin(t * 7 + i), el_r=60, head=8)
            draw_person(c, [WOMAN, WOMAN2][i % 2], p, x=x, facing=1)
    location_card(c, W, H, [("THEORETICAL DIVISION", 28, "semi", "fg"), ("HANS BETHE, DIVISION HEAD · HUMAN 'COMPUTERS'", 16, "mono", "fg")], win(t, 0.6, d - 0.2, 0.6), COLD)
    tag2d(c, W, H, COLD)


@shot(69)
def s69(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -0.6, 0.6), y=-1.0, z=0.6, f=900)
    c.clear(col((30, 32, 34)))
    with st.at(2.4):
        c.drawRect(skia.Rect(-3, -1.8, 3, 0.2), P(c=col((120, 124, 126))))
        c.drawRect(skia.Rect(-2.6, -1.5, -0.6, -0.5), P(c=col((40, 42, 44))))
        for i in range(10):
            ph = (t * 3 + i * 0.1) % 1
            x = lerp(-2.4, -0.8, ph)
            c.drawRect(skia.Rect(x, -1.2, x + 0.4, -0.95), P(c=col((220, 200, 160), 0.9)))
            for j in range(6):
                c.drawRect(skia.Rect(x + 0.04 + j * 0.06, -1.17 + (i * j % 3) * 0.06, x + 0.07 + j * 0.06, -1.14 + (i * j % 3) * 0.06), P(c=col((40, 40, 40))))
        c.drawRect(skia.Rect(0.4, -1.6, 2.6, -0.4), P(c=col((50, 54, 58))))
        for x in np.arange(0.5, 2.5, 0.12):
            for y in np.arange(-1.5, -0.5, 0.12):
                c.drawCircle(x, y, 0.025, P(c=col((20, 20, 20))))
        for i in range(6):
            x0, y0 = 0.6 + i * 0.3, -1.4
            x1, y1 = 0.8 + i * 0.25, -0.6
            c.drawPath(poly([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 0.25), (x1, y1)], close=False),
                       P(c=col([(200, 60, 50), (60, 120, 200), (230, 200, 60)][i % 3]), stroke=0.025))
    card(c, W, H, t, d, COLD, "IBM PUNCHED-CARD MACHINES", "USED FOR IMPLOSION CALCULATIONS FROM 1944")
    tag2d(c, W, H, COLD)


@shot(70)
def s70(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -3, 3), y=-1.4, z=0.0)
    sky(c, W, H, (170, 178, 190), (220, 224, 226))
    ground(c, W, H, st.cam, (220, 222, 224), (200, 204, 208))
    mesa_bg(c, st, t)
    with st.at(16):
        for bx in (-24, -8, 8):
            building(c, bx, 12, 6, (150, 140, 120), rows=2, roof="gable", seed=abs(bx) + 3, lit=0.3)
        for i, x in enumerate(np.arange(-20, 20, 4)):
            c.drawLine(x, -2.2, x + 3.6, -2.2, P(c=col((60, 60, 60)), stroke=0.02))
            for j in range(3):
                sw = math.sin(t * 2 + i + j) * 0.05
                c.drawRect(skia.Rect(x + 0.5 + j * 1.0 + sw, -2.2, x + 1.1 + j * 1.0 + sw, -1.5), P(c=col([(230, 230, 220), (180, 200, 220), (220, 190, 180)][j])))
    with st.at(7):
        for i in range(3):
            xx = -3 + i * 1.5 + math.sin(t * 2 + i) * 0.4
            p = walk_pose(t * 8 + i, 0.6)
            if (t + i) % 2 < 0.5:
                p.sh_r, p.el_r = 150, 30
            draw_person(c, Look(height=1.2, build=0.8, suit=[(150, 50, 40), (50, 80, 130), (60, 110, 60)][i], suit_dark=(60, 40, 40), hat=None, hair=(60, 40, 30)),
                        p, x=xx, facing=1 if i % 2 else -1)
        draw_person(c, WOMAN, walk_pose(t * 4.4, 0.8), x=2 + t * 0.7, facing=1)
        car_1940(c, 18 - t * 3, (80, 90, 60), wheel_t=-t * 3, facing=-1)
    card(c, W, H, t, d, COLD, "LOS ALAMOS — A SECRET TOWN", "1944")
    tag2d(c, W, H, COLD)


@shot(71)
def s71(c, t, d, W, H):
    st = Stage(c, W, H, x=0.0, y=-1.6, z=track(t, d, -2.0, -0.8))
    sky(c, W, H, (130, 160, 196), (220, 214, 196))
    ground(c, W, H, st.cam, (150, 120, 90), (180, 160, 130))
    with st.at(80):
        c.drawPath(poly([(-200, 0), (-200, -30), (-30, -26), (-24, -12), (24, -12), (30, -28), (200, -32), (200, 0)]), P(c=col((176, 140, 110))))
    with st.at(60):
        bt = t - 1.4
        if bt > 0:
            for i in range(40):
                rng = np.random.default_rng(i)
                r = (2 + 10 * (1 - math.exp(-bt / 0.8))) * rng.uniform(0.5, 1.2)
                ang = rng.uniform(math.pi, 2 * math.pi)
                c.drawCircle(math.cos(ang) * r * 1.3, -2 + math.sin(ang) * r - bt * 1.5, r * 0.5,
                             P(c=col((140, 124, 108), 0.7 * math.exp(-bt / 4)), blur=r * 0.2))
            if bt < 0.3:
                c.drawCircle(0, -2, 6, P(c=col((255, 220, 160), 1 - bt / 0.3), blur=2))
    with st.at(6):
        c.drawPath(poly([(-4, 0), (-3.6, -1.1), (2.4, -1.1), (2.8, 0)]), P(c=col((100, 80, 56))))
        for i, (L, x) in enumerate(((KISTI, -1.6), (SCIENTIST, -0.4), (CREW, 0.8))):
            rise = smooth((t - 2.6 - i * 0.2) / 0.6)
            p = Pose(lean=lerp(40, 4, rise), hip_l=lerp(70, 0, rise), hip_r=lerp(70, 6, rise), knee_l=lerp(110, 4, rise), knee_r=lerp(110, 4, rise),
                     sh_r=lerp(120, 10, rise), el_r=lerp(40, 20, rise), bob=lerp(0.45, 0, rise), head=-10)
            draw_person(c, L, p, x=x, facing=1)
    location_card(c, W, H, [("GEORGE KISTIAKOWSKY", 28, "semi", "fg"), ("EXPLOSIVES DIVISION · IMPLOSION LENS TESTS, 1944–45", 16, "mono", "fg")], win(t, 0.6, d - 0.2, 0.6), COLD)
    tag2d(c, W, H, COLD)


@shot(72)
def s72(c, t, d, W, H):
    k = K(H)
    c.clear(col((14, 22, 32)))
    for x in range(0, W, int(40 * k)):
        c.drawLine(x, 0, x, H, P(c=col((255, 255, 255), 0.03), stroke=1))
    for y in range(0, H, int(40 * k)):
        c.drawLine(0, y, W, y, P(c=col((255, 255, 255), 0.03), stroke=1))
    a = eout(t / 1.0)
    cx, cy = W / 2, H / 2
    lp = P(c=col((220, 230, 240), a), stroke=2 * k)
    c.drawRoundRect(skia.Rect(cx - 520 * k, cy - 90 * k, cx + 560 * k, cy + 90 * k), 90 * k, 90 * k, lp)
    c.drawLine(cx - 420 * k, cy - 22 * k, cx + 260 * k, cy - 22 * k, lp)
    c.drawLine(cx - 420 * k, cy + 22 * k, cx + 260 * k, cy + 22 * k, lp)
    slide = smooth((t - 2.0) / 2.2)
    px = lerp(cx - 380 * k, cx + 150 * k, slide)
    c.drawRect(skia.Rect(px, cy - 18 * k, px + 110 * k, cy + 18 * k), P(c=col((214, 150, 86), a)))
    c.drawRect(skia.Rect(cx + 260 * k, cy - 60 * k, cx + 400 * k, cy + 60 * k), P(c=col((214, 150, 86), a * 0.8)))
    if slide > 0.98:
        c.drawRect(skia.Rect(cx + 240 * k, cy - 70 * k, cx + 420 * k, cy + 70 * k), P(c=col((255, 200, 140), 0.3), blur=20 * k))
    aa = clamp((t - 1.0) / 0.6)
    label_line(c, cx - 300 * k, cy, cx - 380 * k, cy - 200 * k, "URANIUM-235 PROJECTILE", k, COLD, aa, align="right")
    label_line(c, cx + 330 * k, cy - 60 * k, cx + 420 * k, cy - 200 * k, "URANIUM-235 TARGET", k, COLD, aa)
    label_line(c, cx, cy + 22 * k, cx + 60 * k, cy + 200 * k, "GUN BARREL", k, COLD, aa)
    text(c, "GUN-TYPE DESIGN · 'LITTLE BOY'", 64 * k, 90 * k, 28 * k, "semi", COLD["fg"], a, track=0.18)
    text(c, "simplified, after published declassified diagrams", 64 * k, 122 * k, 15 * k, "reg", COLD["muted"], a)
    small_tag(c, W, H, "GRAPHICS", COLD)


@shot(73)
def s73(c, t, d, W, H):
    k = K(H)
    c.clear(col((14, 22, 32)))
    cx, cy = W / 2, H / 2
    a = eout(t / 1.0)
    R = 300 * k
    comp = smooth((t - 2.2) / 2.4)
    for i in range(16):
        ang = i / 16 * 6.283 + t * 0.1
        c.drawLine(cx + math.cos(ang) * R, cy + math.sin(ang) * R, cx + math.cos(ang) * R * 0.55, cy + math.sin(ang) * R * 0.55,
                   P(c=col((220, 230, 240), a * 0.5), stroke=1.2 * k))
    c.drawCircle(cx, cy, R, P(c=col((220, 230, 240), a), stroke=2 * k))
    c.drawCircle(cx, cy, R * 0.55, P(c=col((220, 230, 240), a), stroke=1.4 * k))
    shock = lerp(R * 0.98, R * 0.2, comp)
    if 0 < comp < 1:
        c.drawCircle(cx, cy, shock, P(c=col((255, 200, 140), 0.8), stroke=3 * k))
        for i in range(12):
            ang = i / 12 * 6.283
            c.drawLine(cx + math.cos(ang) * (shock + 40 * k), cy + math.sin(ang) * (shock + 40 * k),
                       cx + math.cos(ang) * (shock + 8 * k), cy + math.sin(ang) * (shock + 8 * k), P(c=col((255, 200, 140), 0.8), stroke=2 * k))
    core = lerp(80, 52, comp) * k
    c.drawCircle(cx, cy, core, P(c=col((214, 150, 86), a)))
    if comp > 0.95:
        c.drawCircle(cx, cy, core * 2, P(c=col((255, 220, 170), 0.35), blur=20 * k))
    aa = clamp((t - 1.0) / 0.6)
    label_line(c, cx + R * 0.8, cy - R * 0.6, cx + R * 1.3, cy - R * 0.9, "HIGH-EXPLOSIVE LENSES", k, COLD, aa)
    label_line(c, cx + core, cy, cx + R * 1.3, cy + R * 0.6, "PLUTONIUM-239 CORE", k, COLD, aa)
    text(c, "IMPLOSION DESIGN · 'FAT MAN', 'THE GADGET'", 64 * k, 90 * k, 28 * k, "semi", COLD["fg"], a, track=0.18)
    text(c, "converging shock wave compresses the core to supercritical density · simplified", 64 * k, 122 * k, 15 * k, "reg", COLD["muted"], a)
    small_tag(c, W, H, "GRAPHICS", COLD)


@shot(74)
def s74(c, t, d, W, H):
    timeline(c, t, d, W, H, COLD, [(1943, "1943 — Los Alamos opens"),
                                   (1944.5, "July 1944 — reactor plutonium cannot be used in a gun design; the laboratory reorganises around implosion")],
             focus=(1940, 1948))
    small_tag(c, W, H, "GRAPHICS", COLD)


@shot(75)
def s75(c, t, d, W, H):
    key = ("board", W)
    if key not in _G:
        _G[key] = style_test.ShotBoard(W, H)
    _G[key].draw(c, t + 0.8)


# =========================================================== SCENE 8
def nm_map(c, W, H, t, d, center, width, markers, routes=(), pal=DES):
    m = mv("nm", "+proj=utm +zone=13 +datum=WGS84", (-112, 30, -100, 40))
    if "nm_states" not in _G:
        rings = _topo_rings("states-10m.json")
        _G["nm_states"] = {k_: m._path(v) for k_, v in rings.items() if k_ in ("35", "04", "08", "48", "40", "49", "20")}
    mat, mpx = draw_map(c, W, H, m, center, width, pal, grat=1, routes=(), markers=(), land_a=1.0)
    for k_, path in _G["nm_states"].items():
        pth = skia.Path(path); pth.transform(mat)
        if k_ == "35":
            c.drawPath(pth, P(c=col(mix(pal["land"], (255, 255, 255), 0.2))))
        c.drawPath(pth, P(c=col(pal["coast"], 1.0 if k_ == "35" else 0.55), stroke=(2.4 if k_ == "35" else 1.2) * K(H)))
    for lon, lat, nm in ((-106.0, 36.6, "NEW MEXICO"), (-111.0, 34.6, "ARIZONA"), (-102.0, 32.6, "TEXAS"), (-105.5, 38.0, "COLORADO")):
        q = m.S(mat, lon, lat)
        text(c, nm, q.x(), q.y(), 15 * K(H), "reg", pal["muted"], 0.8, track=0.3, align="center")
    for pts, prog, colr in routes:
        if prog > 0:
            p0, p1 = m.S(mat, *pts[0]), m.S(mat, *pts[-1])
            ex, ey = lerp(p0.x(), p1.x(), prog), lerp(p0.y(), p1.y(), prog)
            rp = P(c=col(colr), stroke=2.4 * K(H)); rp.setPathEffect(skia.DashPathEffect.Make([12 * K(H), 8 * K(H)], 0))
            c.drawLine(p0.x(), p0.y(), ex, ey, rp)
    for lon, lat, name, a, style, off in markers:
        p = m.S(mat, lon, lat)
        if a > 0:
            colr = pal["accent"] if style == "key" else pal["fg"]
            c.drawCircle(p.x(), p.y(), (6 if style == "key" else 4) * K(H), P(c=col(colr, a)))
            text(c, name, p.x() + off[0] * K(H), p.y() + off[1] * K(H), 14 * K(H), "semi", colr, a, track=0.14,
                 align="right" if off[0] < 0 else "left")
    scale_bar(c, W, H, mpx, pal)
    return mat


@shot(76)
def s76(c, t, d, W, H):
    u = ease(t / d)
    mk = [(-105.94, 35.69, "SANTA FE", 1.0, "dot", (12, -8)), (-106.65, 35.08, "ALBUQUERQUE", 1.0, "dot", (12, 16)),
          (-106.89, 34.06, "SOCORRO", 1.0, "dot", (-12, -8)), (-106.3, 35.88, "LOS ALAMOS", 1.0, "key", (12, -10)),
          (-106.475, 33.677, "TRINITY SITE", ping(t, 4.4), "key", (14, 18))]
    nm_map(c, W, H, t, d, (lerp(-106.1, -106.3, u), lerp(34.5, 34.6, u)), lerp(1400, 1050, u), mk,
           routes=[([(-106.3, 35.88), (-106.475, 33.677)], clamp((t - 1.8) / 2.6), DES["accent"])])
    map_title(c, W, H, DES, "NEW MEXICO", "JORNADA DEL MUERTO · ALAMOGORDO BOMBING RANGE", clamp(t / 0.8))
    location_card(c, W, H, [("TRINITY TEST SITE, NEW MEXICO, USA", 28, "semi", "fg"), ("SOUTH OF LOS ALAMOS ON THE JORNADA DEL MUERTO", 16, "mono", "fg")],
                  clamp((t - 5.0) / 0.8), DES)
    small_tag(c, W, H, "GRAPHICS · US ATLAS / NATURAL EARTH", DES)


def desert_bg(c, st, t, sky_top=(120, 150, 190), sky_bot=(230, 210, 180), ground_c=((150, 120, 90), (196, 172, 140)), mtn=(140, 120, 120)):
    sky(c, st.W, st.H, sky_top, sky_bot)
    ground(c, st.W, st.H, st.cam, *ground_c)
    with st.at(500):
        c.drawPath(poly(ridge(np.random.default_rng(12), -1600, 1600, -26, 40, 140, 0.55)), P(c=col(mtn)))


def tower(c, x, h=30, colr=(60, 56, 54)):
    for lx in (-2.5, 2.5):
        c.drawLine(x + lx, 0, x + lx * 0.4, -h, P(c=col(colr), stroke=0.25))
    for y in np.arange(-h, 0, 3):
        f = 1 - (-y) / h * 0.6
        c.drawLine(x - 2.5 * f, y, x + 2.5 * f, y, P(c=col(colr), stroke=0.12))
        c.drawLine(x - 2.5 * f, y, x + 2.5 * (f + 0.06), y - 3, P(c=col(colr), stroke=0.08))
    c.drawRect(skia.Rect(x - 1.8, -h - 2.4, x + 1.8, -h), P(c=col(mix(colr, (200, 190, 170), 0.3))))


@shot(77)
def s77(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -20, -2), y=-4, z=track(t, d, -60, -30))
    desert_bg(c, st, t)
    with st.at(60):
        tower(c, 0)
        for i in range(4):
            p = stand(sh_r=100 + 25 * math.sin(t * 4 + i), el_r=20)
            draw_person(c, CREW, p, x=-1.5 + i * 0.6, facing=1)
    with st.at(30):
        cx = -30 + t * 5
        car_1940(c, cx, (90, 90, 70), wheel_t=t * 3)
        for i in range(14):
            life = (t * 0.8 + i / 14) % 1
            c.drawCircle(cx - 3 - life * 8, -0.6 - life * 1.5, 0.6 + life * 2, P(c=col((200, 176, 140), 0.3 * (1 - life)), blur=0.6))
    with st.at(8):
        rng = np.random.default_rng(4)
        for x in np.arange(-40, 40, 2.4):
            c.drawCircle(x + rng.uniform(-0.6, 0.6) + st.cam.x * 0.0, -0.3, rng.uniform(0.3, 0.6), P(c=col((110, 110, 70))))
    card(c, W, H, t, d, DES, "TRINITY SITE", "JULY 1945 · 100-FOOT STEEL TOWER")
    tag2d(c, W, H, DES)


@shot(78)
def s78(c, t, d, W, H):
    st = Stage(c, W, H, x=0.6, y=-1.3, z=track(t, d, -1.0, 0.2))
    c.clear(col((60, 54, 48)))
    with st.at(4.6):
        wall(c, -6, 6, -4, (196, 186, 166), light=(-2.6, -2.2), light_r=3, light_c=(255, 240, 220), light_a=0.25)
        window(c, -3.4, -2.8, -2.0, -1.2, t, frame=(150, 140, 120), sky_c=((200, 210, 216), (230, 228, 220)))
        c.drawRect(skia.Rect(-3.4, -2.8, -2.0, -1.2), P(c=col((240, 240, 236), 0.5)))
    with st.at(3.6):
        table(c, -0.4, 2.0, top=-0.84, colr=(90, 70, 50), cloth=(230, 228, 220))
        c.drawRect(skia.Rect(1.4, -1.06, 1.7, -0.84), P(c=col((90, 90, 90))))
        for i, (L, x, f) in enumerate(((SCIENTIST, -0.6, 1), (CREW, 2.4, -1), (Look(height=1.78, build=1.0, suit=(220, 216, 206), suit_dark=(190, 186, 176), hat=None, hair=(60, 50, 40)), 0.9, 1))):
            p = stand(lean=18, head=16, sh_r=70 + 6 * math.sin(t * 1.3 + i), el_r=70)
            draw_person(c, L, p, x=x, facing=f)
    card(c, W, H, t, d, DES, "McDONALD RANCH HOUSE", "12–13 JULY 1945 · PLUTONIUM CORE ASSEMBLY")
    tag2d(c, W, H, DES)


def gadget(c, x, y, r=0.8):
    c.drawCircle(x, y, r, P(c=col((96, 98, 100))))
    for i in range(14):
        ang = i / 14 * 6.283
        c.drawLine(x + math.cos(ang) * r * 0.7, y + math.sin(ang) * r * 0.7, x + math.cos(ang) * r * 1.15, y + math.sin(ang) * r * 1.15,
                   P(c=col((40, 40, 40)), stroke=0.04))
    c.drawCircle(x - r * 0.3, y - r * 0.3, r * 0.3, P(c=col((255, 255, 255), 0.12)))


@shot(79)
def s79(c, t, d, W, H):
    st = Stage(c, W, H, x=0, y=track(t, d, -4, -24), z=-30)
    desert_bg(c, st, t, sky_top=(110, 150, 200), sky_bot=(236, 214, 180))
    with st.at(20):
        tower(c, 0)
        gy = lerp(-3, -24, smooth(t / d))
        c.drawLine(0, -32, 0, gy - 0.8, P(c=col((30, 30, 30)), stroke=0.05))
        gadget(c, math.sin(t * 1.4) * 0.15, gy)
        for i in range(3):
            draw_person(c, CREW, idle(stand(sh_r=150, el_r=10, head=-30), t, i, 0.5), x=-4 + i * 1.2, facing=1)
    card(c, W, H, t, d, DES, "14 JULY 1945", "'THE GADGET' — PLUTONIUM IMPLOSION DEVICE — HOISTED UP THE TOWER")
    tag2d(c, W, H, DES)


@shot(80)
def s80(c, t, d, W, H):
    st = Stage(c, W, H, x=0.3, y=-1.2, z=track(t, d, -0.4, 0.5))
    sky(c, W, H, (90, 130, 190), (220, 200, 170))
    with st.at(3.4):
        c.drawRect(skia.Rect(-3, -3.2, 3, 0.4), P(c=col((150, 146, 136))))
        c.drawRect(skia.Rect(-2.8, -3.0, 2.8, 0.2), P(c=col((90, 88, 84))))
        gadget(c, 0.6, -0.9, 0.85)
        draw_person(c, Look(height=1.8, build=0.95, suit=(170, 160, 136), suit_dark=(140, 132, 112), hat=None, hair=(60, 50, 40)),
                    idle(stand(sh_r=30, el_r=60), t, 1, 0.5), x=-1.0, facing=1)
    card(c, W, H, t, d, DES, "TOP OF THE TRINITY TOWER", "THE ASSEMBLED DEVICE · JULY 1945")
    tag2d(c, W, H, DES)


@shot(81)
def s81(c, t, d, W, H):
    st = Stage(c, W, H, x=0.8, y=-1.4, z=track(t, d, -0.6, 0.4))
    flash = max(0.0, math.sin(t * 2.3) ** 30) * 0.8 if 1.0 < t < d - 0.5 else 0.0
    sky(c, W, H, mix((14, 16, 26), (150, 150, 180), flash), mix((30, 30, 40), (120, 110, 130), flash))
    ground(c, W, H, st.cam, (30, 28, 30), (44, 40, 44))
    with st.at(300):
        tower(c, 40, colr=mix((10, 10, 14), (40, 40, 50), flash))
        if flash > 0.3:
            c.drawPath(poly([(20, -200), (26, -120), (22, -118), (30, -40)], close=False), P(c=col((230, 230, 255), flash), stroke=1.2))
    with st.at(7):
        c.drawPath(poly([(-6, 0), (-5, -2.2), (1, -2.4), (2, 0)]), P(c=col((50, 46, 42))))
        c.drawRect(skia.Rect(-1.2, -1.9, -0.2, 0), P(c=col((255, 214, 150))))
        c.drawCircle(-0.7, -1.0, 1.2, P(c=col((255, 214, 150), 0.18), blur=0.5))
        p = stand(sh_r=lerp(10, 110, win(t, 2.0, 3.6, 0.3)), el_r=lerp(10, 120, win(t, 2.0, 3.6, 0.3)), head=-14)
        draw_person(c, OPP_TRINITY, p, x=1.6, facing=1, rim=0.3)
        draw_person(c, GROVES, idle(stand(head=-16), t, 2, 0.4), x=3.0, facing=-1)
    rng = np.random.default_rng(3)
    for i in range(160):
        x = rng.uniform(0, W)
        y = (rng.uniform(0, H) + t * 1400 * K(H)) % H
        c.drawLine(x, y, x - 8 * K(H), y + 40 * K(H), P(c=col((200, 210, 230), 0.25), stroke=1.2 * K(H)))
    card(c, W, H, t, d, DES, "S-10000 CONTROL BUNKER", "NIGHT, 15–16 JULY 1945 · STORMS DELAY THE TEST FROM 4:00 AM")
    tag2d(c, W, H, DES)


@shot(82)
def s82(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -1.5, 1.5), y=-1.3, z=0.0)
    c.clear(col((20, 20, 22)))
    with st.at(5):
        wall(c, -8, 8, -3.2, (80, 80, 78), light=(0, -2), light_r=5, light_c=(255, 220, 170), light_a=0.15)
        c.drawRect(skia.Rect(4.5, -1.4, 5.3, -0.8), P(c=col((230, 226, 214))))
        text(c, "", 0, 0, 1)
    with st.at(3.6):
        for x in np.arange(-6, 6, 1.4):
            c.drawRect(skia.Rect(x, -1.3, x + 1.2, -0.7), P(c=col((60, 64, 60))))
            for j in range(3):
                c.drawCircle(x + 0.25 + j * 0.35, -1.0, 0.08, P(c=col((220, 214, 190))))
                c.drawCircle(x + 0.25 + j * 0.35, -0.8, 0.025, P(c=col((255, 120, 60) if (j + int(t)) % 3 == 0 else (90, 200, 120))))
        for i, x in enumerate((-4.4, -1.6, 1.2, 3.8)):
            p = sit(sh_r=70 + 5 * math.sin(t * 2 + i), el_r=50, head=6, lean=10)
            draw_person(c, [CREW, SCIENTIST, CREW, KISTI][i], p, x=x - 0.6, facing=1)
    card(c, W, H, t, d, DES, "INSIDE S-10000", "5:20 AM, 16 JULY 1945")
    tag2d(c, W, H, DES)


@shot(83)
def s83(c, t, d, W, H):
    k = K(H)
    c.clear(col((10, 12, 26)))
    c.drawRect(skia.Rect(0, H * 0.7, W, H), P(c=col((20, 18, 26))))
    c.save(); c.translate(W * 0.7, H * 0.7); c.scale(6 * k, 6 * k); tower(c, 0, colr=(30, 30, 40)); c.restore()
    s = min(45, 30 + int(t / d * 15.999))
    text(c, f"5:29:{s:02d}", W / 2, H * 0.42, 120 * k, "monom", (240, 232, 216), eout(t / 0.4), align="center")
    text(c, "AM", W / 2 + 330 * k, H * 0.42, 34 * k, "mono", DES["muted"], eout(t / 0.4))
    location_card(c, W, H, [("TRINITY TEST SITE, NEW MEXICO, USA", 30, "semi", "fg"), ("16 JULY 1945", 22, "med", "fg"),
                            ("5:29:45 AM LOCAL TIME", 22, "med", "accent")], clamp((t - 1.0) / 0.8), DES)
    small_tag(c, W, H, "GRAPHICS", DES)


@shot(84)
def s84(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -2, 2), y=-0.7, z=0.6)
    sky(c, W, H, (10, 14, 34), (40, 46, 74))
    stars(c, W, H, t, n=160)
    ground(c, W, H, st.cam, (40, 36, 40), (60, 56, 64))
    with st.at(12):
        for x in (-8, 6):
            c.drawPath(poly([(x - 1.6, 0), (x, -1.8), (x + 1.6, 0)]), P(c=col((70, 70, 80))))
    with st.at(4):
        c.drawRect(skia.Rect(-10, -0.15, 10, 0.1), P(c=col((30, 28, 32))))
        for i, x in enumerate(np.arange(-6, 6, 2.0)):
            c.save(); c.translate(x, -0.12); c.rotate(-90)
            draw_person(c, [CREW, SCIENTIST, OFFICIAL][i % 3], stand(sh_r=170, el_r=10, sh_l=170, el_l=10), x=0, facing=1)
            c.restore()
            c.drawRect(skia.Rect(x + 1.85, -0.18, x + 2.0, -0.08), P(c=col((20, 40, 30))))
    card(c, W, H, t, d, DES, "BASE CAMP, ABOUT 10 MILES FROM THE TOWER", "OBSERVERS LIE FACE-DOWN, FEET TOWARD THE BLAST")
    tag2d(c, W, H, DES)


@shot(85)
def s85(c, t, d, W, H):
    st = Stage(c, W, H, x=0.2, y=-1.6, z=track(t, d, 1.8, 2.4), f=1100)
    c.clear(col((14, 14, 16)))
    with st.at(4.0):
        wall(c, -3, 3, -3, (50, 50, 50), light=(0.4, -1.6), light_r=1.5, light_c=(255, 200, 150), light_a=0.2)
        c.drawRect(skia.Rect(0.55, -3, 0.75, 0), P(c=col((90, 70, 50))))
        p = stand(sh_r=lerp(70, 74, 0.5 + 0.5 * math.sin(t * 3)), el_r=70, head=-2 + math.sin(t * 0.8))
        draw_person(c, OPP_TRINITY, p, x=0.0, facing=1, rim=0.5, light=(255, 200, 150))
    small_tag(c, W, H, "2D RECONSTRUCTION", DES)


def trinity_view(c, W, H, t_since, cam_z=-60, mono=False, observers=False, t=0.0):
    st = Stage(c, W, H, x=0, y=-3, z=cam_z)
    glow = math.exp(-max(0, t_since) / 3)
    sky(c, W, H, mix((20, 24, 48), (255, 200, 150), 0.6 * glow), mix((60, 50, 70), (255, 170, 100), 0.8 * glow))
    ground(c, W, H, st.cam, mix((30, 26, 30), (120, 80, 60), glow), mix((50, 40, 44), (200, 130, 80), glow))
    with st.at(900):
        c.drawPath(poly(ridge(np.random.default_rng(12), -2600, 2600, -40, 60, 140, 0.55)), P(c=col(mix((30, 26, 40), (220, 120, 70), glow))))
    with st.at(480):
        mushroom(c, 0, 0, max(0.05, t_since), scale=8, mono=mono)
    return st


@shot(86)
def s86(c, t, d, W, H):
    if have_photo("trinity_fireball_0.jpg"):
        photo_shot(c, t, d, W, H, "trinity_fireball_0.jpg", DES, "BERLYN BRIXNER / LOS ALAMOS NATIONAL LABORATORY · 0.016 s",
                   start=(0.5, 0.55, 1.0), end=(0.5, 0.5, 1.15))
        location_card(c, W, H, [("TRINITY TEST SITE, NEW MEXICO, USA", 28, "semi", "fg"), ("16 JULY 1945 · 5:29:45 AM LOCAL TIME", 20, "med", "accent")],
                      clamp((t - 0.6) / 0.8), DES)
        return
    trinity_view(c, W, H, t * 0.35, cam_z=-120)
    location_card(c, W, H, [("TRINITY TEST SITE, NEW MEXICO, USA", 28, "semi", "fg"), ("16 JULY 1945 · 5:29:45 AM LOCAL TIME", 20, "med", "accent")],
                  clamp((t - 0.6) / 0.8), DES)
    small_tag(c, W, H, "2D RECONSTRUCTION", DES)


@shot(87)
def s87(c, t, d, W, H):
    if have_photo("trinity_fireball_1.jpg"):
        photo_shot(c, t, d, W, H, "trinity_fireball_1.jpg", DES, "LOS ALAMOS NATIONAL LABORATORY / NNSA · 0.053 s",
                   start=(0.5, 0.5, 1.0), end=(0.5, 0.42, 1.12))
        return
    trinity_view(c, W, H, 2.5 + t * 0.9, cam_z=-160)
    small_tag(c, W, H, "2D RECONSTRUCTION", DES)


@shot(88)
def s88(c, t, d, W, H):
    st = trinity_view(c, W, H, 8 + t * 1.2, cam_z=-260)
    with st.at(8):
        c.drawRect(skia.Rect(-30, -1.6, -29.8, 0), P(c=col((20, 16, 14))))
        rng = np.random.default_rng(5)
        for x in np.arange(-60, 60, 3.0):
            c.drawCircle(x + rng.uniform(-1, 1), -0.4, rng.uniform(0.4, 0.8), P(c=col((24, 20, 18))))
    card(c, W, H, t, d, DES, "VIEW FROM ABOUT 10,000 YARDS", "5:30 AM, 16 JULY 1945")
    tag2d(c, W, H, DES)


@shot(89)
def s89(c, t, d, W, H):
    st = Stage(c, W, H, x=0.5, y=-1.1, z=track(t, d, 0.4, -1.2))
    glow = 0.35 * math.exp(-t / 3)
    sky(c, W, H, mix((40, 44, 70), (255, 190, 140), glow), mix((140, 110, 110), (255, 170, 110), glow))
    ground(c, W, H, st.cam, (60, 50, 50), (110, 90, 84))
    with st.at(500):
        mushroom(c, -60, 0, 16 + t, scale=7)
    with st.at(10):
        for x in (-7, 5):
            c.drawPath(poly([(x - 1.6, 0), (x, -1.8), (x + 1.6, 0)]), P(c=col((70, 70, 80))))
    with st.at(4):
        for i, x in enumerate(np.arange(-4, 4.5, 1.4)):
            rise = smooth((t - 0.3 - i * 0.2) / 1.0)
            p = Pose(lean=lerp(60, 0, rise), hip_l=lerp(80, 0, rise), hip_r=lerp(80, 4, rise), knee_l=lerp(100, 4, rise), knee_r=lerp(100, 2, rise),
                     sh_r=lerp(100, 20, rise), el_r=lerp(40, 30, rise), bob=lerp(0.5, 0, rise), head=-12)
            if i == 2 and t > 3:
                p.sh_r, p.el_r = 160, 40
            draw_person(c, [CREW, SCIENTIST, OFFICIAL][i % 3], p, x=x, facing=-1, rim=0.6, light=(255, 190, 140))
    gust = clamp((t - 3.2) / 0.4) * clamp((d - t) / 1.0)
    if gust > 0:
        rng = np.random.default_rng(8)
        for i in range(60):
            x = (rng.uniform(0, W) + (t - 3.2) * 1500 * K(H)) % W
            c.drawLine(x, rng.uniform(H * 0.4, H), x + 60 * K(H), rng.uniform(H * 0.4, H), P(c=col((200, 170, 140), 0.25 * gust), stroke=2 * K(H)))
    tag2d(c, W, H, DES)


@shot(90)
def s90(c, t, d, W, H):
    k = K(H)
    bg_fill(c, W, H, DES)
    u = eout((t - 0.4) / 1.6)
    x0, y = W * 0.16, H * 0.5
    c.drawRect(skia.Rect(x0, y - 22 * k, x0 + W * 0.6 * u, y + 22 * k), P(c=col(DES["accent"])))
    for i in range(6):
        xx = x0 + W * 0.6 * i / 5
        c.drawLine(xx, y + 34 * k, xx, y + 44 * k, P(c=col(DES["fg"], 0.6), stroke=1.2 * k))
        text(c, f"{i * 5}", xx, y + 70 * k, 15 * k, "mono", DES["muted"], 0.8, align="center")
    text(c, "kilotons of TNT", x0 + W * 0.6, y + 100 * k, 15 * k, "mono", DES["muted"], 0.8, align="right")
    text(c, "ESTIMATED YIELD: ABOUT 20 KILOTONS OF TNT", x0, y - 60 * k, 30 * k, "semi", DES["fg"], eout(t / 0.8), track=0.12)
    text(c, "later estimates up to about 25 kt · source: Los Alamos National Laboratory", x0, y - 30 * k - 4 * k, 15 * k, "reg", DES["muted"], eout((t - 0.4) / 0.8))
    text(c, "16 JULY 1945 — TRINITY", x0, H * 0.8, 20 * k, "monom", DES["accent"], eout((t - 1.6) / 0.8), track=0.1)
    small_tag(c, W, H, "GRAPHICS", DES)


@shot(91)
def s91(c, t, d, W, H):
    st = Stage(c, W, H, x=track(t, d, -0.5, 0.8), y=-1.3, z=track(t, d, -1.0, 0.0))
    desert_bg(c, st, t, sky_top=(110, 150, 196), sky_bot=(230, 216, 190), ground_c=((150, 130, 100), (186, 170, 140)))
    with st.at(6):
        for x in (-1.5, 1.4):
            c.drawPath(poly([(x - 0.3, 0), (x - 0.2, -0.9), (x + 0.4, -1.3), (x + 0.1, -0.7), (x + 0.3, 0)]), P(c=col((80, 70, 60))))
        c.drawOval(skia.Rect(-12, -0.15, 12, 0.15), P(c=col((110, 150, 110), 0.4)))
        draw_person(c, OPP_TRINITY, idle(stand(sh_r=-6, sh_l=-6), t, 1, 0.5), x=-0.3, facing=1)
        draw_person(c, GROVES, idle(stand(), t, 2, 0.5), x=0.6, facing=-1)
    with st.at(10):
        crowd_row(c, -6, -2, [OFFICIAL, CREW], seated=False, t=t, seed=3, spacing=0.9, shade=0.15)
        crowd_row(c, 3, 6.5, [OFFICIAL, SOLDIER], seated=False, t=t, seed=5, spacing=0.9, shade=0.15, facing=-1)
    card(c, W, H, t, d, DES, "GROUND ZERO, TRINITY", "SEPTEMBER 1945 · OPPENHEIMER AND GROVES AT THE REMAINS OF THE TOWER")
    tag2d(c, W, H, DES)
