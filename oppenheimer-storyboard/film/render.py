"""Render the 15-minute film from storyboard.json + registered shots.

python3 render.py --stills 8:3,26:4          # PNG checks (shot:local_time)
python3 render.py --scenes 1,2,3 --jobs 3    # render scene parts in parallel
python3 render.py --assemble                 # concat parts + score -> renders/oppenheimer_film.mp4
"""
import argparse, json, math, subprocess, sys, wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).parent))
from engine import Grain, vignette, clamp, col, text, Writer  # noqa
from reg import SHOTS
import shots_a  # noqa
for _m in ("shots_b", "shots_c", "shots_d", "shots_e"):
    try:
        __import__(_m)
    except ModuleNotFoundError:
        pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "renders"
PARTS = OUT / "parts"
SB = json.loads((ROOT / "storyboard.json").read_text())
FPS = 24
XF = 0.4


def secs(tc):
    m, s = tc.split(":")
    return int(m) * 60 + int(s)


TL = [dict(n=s["n"], scene=s["scene"], t0=secs(s["start"]), d=s["dur"], type=s["type"], see=s["see"]) for s in SB["shots"]]
DUR = secs(SB["runtime"])


def placeholder(c, t, d, W, H, shot):
    c.clear(col((20, 22, 26)))
    k = H / 1080
    text(c, f"SHOT {shot['n']:03d}", 80 * k, 140 * k, 40 * k, "semi", (230, 226, 216), 1)
    text(c, shot["see"][:110], 80 * k, 200 * k, 20 * k, "reg", (170, 176, 180), 1)


def draw_shot(c, shot, t_local, W, H):
    fn = SHOTS.get(shot["n"])
    if fn is None:
        placeholder(c, t_local, shot["d"], W, H, shot)
    else:
        fn(c, max(0.0, t_local), shot["d"], W, H)


class Film:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.surf = skia.Surface(W, H)
        self.c = self.surf.getCanvas()
        self.grain = Grain(W, H)

    def frame(self, t):
        c, W, H = self.c, self.W, self.H
        i = next(j for j, s in enumerate(TL) if s["t0"] <= t < s["t0"] + s["d"] or j == len(TL) - 1)
        cur = TL[i]
        local = t - cur["t0"]
        draw_shot(c, cur, local, W, H)
        # dissolve into the next shot during the last XF seconds
        if i + 1 < len(TL):
            nxt = TL[i + 1]
            rem = cur["t0"] + cur["d"] - t
            if rem < XF:
                a = 1 - rem / XF
                c.saveLayerAlpha(None, int(255 * a * a * (3 - 2 * a)))
                draw_shot(c, nxt, 0.0, W, H)
                c.restore()
        vignette(c, W, H, 110)
        self.grain.apply(c, t, 0.06)
        if t < 1.0:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * (1 - t)))))
        if t > DUR - 1.5:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * clamp((t - DUR + 1.5) / 1.5)))))
        return self.surf


def scene_range(n):
    ss = [s for s in TL if s["scene"] == n]
    return ss[0]["t0"], ss[-1]["t0"] + ss[-1]["d"]


def render_scene(args):
    n, W = args
    H = W * 9 // 16
    film = Film(W, H)
    t0, t1 = scene_range(n)
    PARTS.mkdir(parents=True, exist_ok=True)
    path = PARTS / f"scene_{n:02d}.mp4"
    w = Writer(path, W, H, FPS)
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    for f in range(f0, f1):
        w.frame(film.frame(f / FPS))
    w.close()
    return str(path)


# ------------------------------------------------------------------ score
SCENE_SOUND = {  # root Hz, wind amount, brightness
    1: (55.0, 0.0, 0.5), 2: (65.4, 0.1, 0.8), 3: (65.4, 0.1, 0.8), 4: (73.4, 0.15, 0.8), 5: (55.0, 0.15, 0.4),
    6: (49.0, 0.1, 0.4), 7: (49.0, 0.35, 0.5), 8: (43.7, 0.5, 0.4), 9: (41.2, 0.2, 0.3), 10: (41.2, 0.15, 0.3),
    11: (46.2, 0.1, 0.35), 12: (55.0, 0.25, 0.4),
}


def build_score(path, sr=44100):
    from scipy.signal import lfilter
    n = int(DUR * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(7)
    root = np.zeros(n); wind = np.zeros(n); bright = np.zeros(n)
    for sc, (r, w, b) in SCENE_SOUND.items():
        a, e = scene_range(sc)
        sl = slice(int(a * sr), int(e * sr))
        root[sl], wind[sl], bright[sl] = r, w, b
    k = int(2.5 * sr)
    ker = np.ones(k) / k
    root = np.convolve(np.pad(root, (k, k), mode="edge"), ker, "same")[k:-k]
    wind = np.convolve(np.pad(wind, (k, k), mode="edge"), ker, "same")[k:-k]
    bright = np.convolve(np.pad(bright, (k, k), mode="edge"), ker, "same")[k:-k]
    phase = np.cumsum(root) / sr * 2 * np.pi
    out = np.zeros((n, 2))
    for mult, amp in ((1, 0.5), (1.5, 0.26), (2, 0.28), (3, 0.1), (4, 0.05)):
        for det, pan in ((-0.004, 0.3), (0.0, 0.5), (0.005, 0.7)):
            ph0 = rng.uniform(0, 6.28)
            sig = np.sin(phase * mult * (1 + det) + ph0)
            lfo = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.03, 0.08) * t + rng.uniform(0, 6.28))
            g = amp * lfo * (bright if mult >= 3 else 1.0)
            out[:, 0] += sig * g * (1 - pan); out[:, 1] += sig * g * pan
    noise = rng.normal(0, 1, (n, 2))
    for ch in range(2):
        y = lfilter([0.005], [1, -0.995], noise[:, ch])
        out[:, ch] += y * 14 * wind * (0.6 + 0.4 * np.sin(2 * np.pi * 0.06 * t + ch))
    # aircraft engines (shots 94-109, 116): low beating drone
    for s in TL:
        if s["n"] in (94, 96, 97, 102, 103, 104, 106, 107, 109, 116):
            a, e = int(s["t0"] * sr), int((s["t0"] + s["d"]) * sr)
            tt = t[a:e]
            eng = sum(np.sin(2 * np.pi * f * tt) for f in (38.0, 38.7, 76.4, 114.2)) * 0.18
            eng *= np.minimum(1, (tt - tt[0]) / 0.5) * np.minimum(1, (tt[-1] - tt) / 0.5)
            out[a:e, 0] += eng; out[a:e, 1] += eng
    # clock ticks during the Trinity countdown (shot 83)
    for s in TL:
        if s["n"] == 83:
            for i in range(s["d"]):
                p = int((s["t0"] + i + 0.05) * sr)
                tick = np.sin(2 * np.pi * 2200 * np.arange(800) / sr) * np.exp(-np.arange(800) / 120)
                out[p:p + 800] += tick[:, None] * 0.3
    # silence windows: Trinity fireball (86) and the two archival clouds (110, 118)
    env = np.ones(n)
    for s in TL:
        if s["n"] in (86, 110, 118):
            a, e = s["t0"], s["t0"] + s["d"]
            env *= 1 - 0.85 * np.clip(np.minimum((t - a + 0.6) / 0.6, (e + 0.6 - t) / 0.6), 0, 1)
    out *= env[:, None]
    fade = np.minimum(1, t / 3) * np.minimum(1, (DUR - t) / 3)
    out *= fade[:, None]
    out /= np.abs(out).max() + 1e-9
    out *= 10 ** (-14 / 20)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


def assemble(scenes):
    lst = PARTS / "list.txt"
    lst.write_text("".join(f"file 'scene_{n:02d}.mp4'\n" for n in scenes))
    vid = PARTS / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vid)], check=True)
    wav = PARTS / "score.wav"
    build_score(wav)
    final = OUT / "oppenheimer_film.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--stills", default="")
    ap.add_argument("--scenes", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--assemble", action="store_true")
    a = ap.parse_args()
    W = a.width; H = W * 9 // 16
    if a.stills:
        film = Film(W, H)
        OUT.mkdir(exist_ok=True)
        for spec in a.stills.split(","):
            n, lt = spec.split(":")
            s = next(x for x in TL if x["n"] == int(n))
            surf = film.frame(s["t0"] + float(lt))
            p = OUT / f"chk_{int(n):03d}_{float(lt):04.1f}.png"
            surf.makeImageSnapshot().save(str(p), skia.kPNG)
            print(p)
    if a.scenes:
        scenes = [int(x) for x in a.scenes.split(",")]
        with Pool(min(a.jobs, len(scenes))) as pool:
            for p in pool.imap_unordered(render_scene, [(n, W) for n in scenes]):
                print("done", p, flush=True)
    if a.assemble:
        print(assemble(list(range(1, 13))))


if __name__ == "__main__":
    main()
