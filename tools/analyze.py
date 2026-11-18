#!/usr/bin/env python3
"""Frame-by-frame analysis of every video in shorts/ at a fixed 30 fps.

Every single frame (decoded by ffmpeg with fps=30) is measured, nothing sampled:
  light/contrast : mean luma, RMS contrast, p1/p5/p50/p95/p99, shadow & highlight
                   clipping, center-vs-edge vignette, saturation, warm/cool balance
  shadows        : share of pixels in deep shadow, shadow colour tint
  camera         : global motion between consecutive frames (dx, dy, zoom, roll)
                   from tracked features + RANSAC; residual = in-frame animation
  effects        : held/duplicate frames, flashes, blur (whip/motion blur), shake
  edits          : hard cuts, dissolves/fades, flash cuts

Outputs per video in analysis/<name>/:
  frames.csv   one row per frame
  shots.json   shot list with transitions, duration, camera move, light stats
  cuts.jpg     every cut shown as frames [-2,-1 | 0,+1,+2] for visual review
  shots.jpg    first / middle / last frame of every shot
and analysis/summary.md across all videos.
"""
import csv, json, subprocess, sys, pathlib
import numpy as np
import cv2

FPS = 30
W, H = 270, 480          # analysis resolution (9:16); full frames kept for sheets
ROOT = pathlib.Path(__file__).resolve().parent.parent


def frames(path):
    cmd = ["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf",
           f"fps={FPS},scale={W}:{H}:flags=area", "-f", "rawvideo",
           "-pix_fmt", "bgr24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


def global_motion(prev_g, g):
    pts = cv2.goodFeaturesToTrack(prev_g, 300, 0.01, 6)
    if pts is None or len(pts) < 12:
        return 0.0, 0.0, 1.0, 0.0, np.nan, 0
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev_g, g, pts, None, winSize=(21, 21), maxLevel=3)
    ok = st.ravel() == 1
    a, b = pts[ok].reshape(-1, 2), nxt[ok].reshape(-1, 2)
    if len(a) < 12:
        return 0.0, 0.0, 1.0, 0.0, np.nan, 0
    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if M is None:
        return 0.0, 0.0, 1.0, 0.0, np.nan, 0
    s = float(np.hypot(M[0, 0], M[1, 0]))
    rot = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    # residual motion of outliers = things moving against the camera (characters, FX)
    pred = a @ M[:, :2].T + M[:, 2]
    resid = np.linalg.norm(b - pred, axis=1)
    out = ~inl.ravel().astype(bool)
    res = float(np.median(resid[out])) if out.sum() >= 5 else 0.0
    c = np.array([W / 2, H / 2])
    tc = M[:, :2] @ c + M[:, 2] - c      # displacement of the frame centre
    return float(tc[0]), float(tc[1]), s, rot, res, int(inl.sum())


def frame_stats(bgr):
    ycc = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    y = ycc[..., 0].astype(np.float32)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    p = np.percentile(y, [1, 5, 50, 95, 99])
    ch, cw = H // 4, W // 4
    center = y[ch:-ch, cw:-cw].mean()
    edge_mask = np.ones_like(y, bool); edge_mask[H // 8:-H // 8, W // 8:-W // 8] = False
    edge = y[edge_mask].mean()
    sh = y < 40
    b, g, r = [bgr[..., i].astype(np.float32) for i in range(3)]
    shadow_tint = float((b[sh] - r[sh]).mean()) if sh.sum() > 50 else 0.0
    gray = ycc[..., 0]
    return dict(
        luma=float(y.mean()), contrast=float(y.std()),
        p1=p[0], p5=p[1], p50=p[2], p95=p[3], p99=p[4],
        crush=float((y <= 8).mean()), clip=float((y >= 247).mean()),
        shadow_frac=float(sh.mean()), shadow_tint_b_minus_r=shadow_tint,
        vignette=float(center - edge), sat=float(hsv[..., 1].mean()),
        warmth_r_minus_b=float((r - b).mean()),
        sharp=float(cv2.Laplacian(gray, cv2.CV_32F).var()),
    ), gray


def hist(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv], [0, 1, 2], None, [16, 8, 8], [0, 180, 0, 256, 0, 256])
    return cv2.normalize(h, h).flatten()


def classify_move(sh):
    dx, dy = np.sum(sh["dx"]), np.sum(sh["dy"])
    zoom = np.prod(sh["zoom"])
    rot = np.sum(sh["rot"])
    jitter = float(np.std(np.diff(sh["dx"])) + np.std(np.diff(sh["dy"]))) if len(sh["dx"]) > 3 else 0
    tags = []
    if zoom > 1.04: tags.append(f"push-in x{zoom:.2f}")
    if zoom < 0.96: tags.append(f"pull-out x{zoom:.2f}")
    # image content moves opposite to camera: content right (+dx) = camera pans left
    if abs(dx) > W * 0.08: tags.append(("pan-left" if dx > 0 else "pan-right") + f" {abs(dx)/W:.0%}W")
    if abs(dy) > H * 0.06: tags.append(("tilt-up" if dy > 0 else "tilt-down") + f" {abs(dy)/H:.0%}H")
    if abs(rot) > 2: tags.append(f"roll {rot:+.1f}deg")
    if jitter > 1.2: tags.append(f"shake({jitter:.1f})")
    return ", ".join(tags) or "static/locked"


def analyze(video):
    name = video.stem
    out = ROOT / "analysis" / name
    out.mkdir(parents=True, exist_ok=True)
    rows, thumbs = [], []
    prev = prev_g = prev_h = None
    for i, f in enumerate(frames(video)):
        st, g = frame_stats(f)
        h = hist(f)
        if prev is None:
            mv = (0.0, 0.0, 1.0, 0.0, 0.0, 0); hd = 0.0; mad = 0.0
        else:
            mv = global_motion(prev_g, g)
            hd = 1 - float(cv2.compareHist(prev_h, h, cv2.HISTCMP_CORREL))
            mad = float(cv2.absdiff(prev, f).mean())
        st.update(frame=i, t=i / FPS, dx=mv[0], dy=mv[1], zoom=mv[2], rot=mv[3],
                  anim_resid=mv[4], inliers=mv[5], hist_diff=hd, mad=mad)
        rows.append(st)
        thumbs.append(cv2.resize(f, (135, 240), interpolation=cv2.INTER_AREA))
        prev, prev_g, prev_h = f, g, h
    if not rows:
        print("no frames:", video); return None

    n = len(rows)
    hd = np.array([r["hist_diff"] for r in rows]); mad = np.array([r["mad"] for r in rows])
    luma = np.array([r["luma"] for r in rows]); inl = np.array([r["inliers"] for r in rows])
    sharp = np.array([r["sharp"] for r in rows])
    med_mad = np.median(mad[mad > 0]) if (mad > 0).any() else 1

    # --- edit detection -------------------------------------------------
    events = []
    for i in range(1, n):
        lo, hi = max(1, i - 15), min(n, i + 16)
        local = np.median(hd[lo:hi])
        local_mad = np.median(mad[lo:hi])
        local_inl = np.median(inl[lo:hi])
        hist_spike = hd[i] > 0.35 and hd[i] > 4 * max(local, 0.02)
        mad_spike = mad[i] > 18 and mad[i] > 3.5 * max(local_mad, 2)
        lost = inl[i] < 0.5 * max(local_inl, 1)
        hard = (hist_spike and (lost or mad_spike)) or (mad_spike and lost)
        flash = (luma[i] - luma[i - 1] > 40) and i + 3 < n and abs(luma[min(n - 1, i + 3)] - luma[i - 1]) < 25
        recent_flash = any(k == "flash" and i - j <= 6 for j, k in events)
        if flash:
            events.append((i, "flash"))
        elif hard and not recent_flash:
            events.append((i, "cut"))
    # gradual transitions: sustained moderate hist change with low tracking
    run = 0
    for i in range(1, n):
        if 0.06 < hd[i] < 0.35 and inl[i] < 40:
            run += 1
        else:
            if run >= 6 and not any(abs(e[0] - i) < run + 3 for e in events):
                events.append((i - run, f"dissolve/fade ({run} fr)"))
            run = 0
    events.sort()
    for r in rows: r["event"] = ""
    for i, k in events: rows[i]["event"] = k
    # held frames (animation on 2s/3s or freeze) : near-zero change
    for i, r in enumerate(rows):
        r["held"] = int(i > 0 and r["mad"] < 0.15 * med_mad)

    with open(out / "frames.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    # --- shots ----------------------------------------------------------
    bounds = [0] + [i for i, k in events if k in ("cut",) or k.startswith("dissolve")] + [n]
    bounds = sorted(set(bounds))
    shots = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b - a < 2: continue
        seg = rows[a + 1:b] if b - a > 2 else rows[a:b]
        flash_idx = {r["frame"] for r in rows[a:b] if r["event"] == "flash"}
        good = [r for r in seg if r["inliers"] >= 20 and not any(0 <= r["frame"] - f <= 4 for f in flash_idx)]
        seg = good or seg
        arr = {k: np.array([r[k] for r in seg], float) for k in ("dx", "dy", "zoom", "rot")}
        res = np.array([r["anim_resid"] for r in seg], float)
        shots.append(dict(
            start_frame=a, end_frame=b - 1, start_t=round(a / FPS, 3), dur_s=round((b - a) / FPS, 3),
            transition_in=rows[a]["event"] or ("start" if a == 0 else ""),
            camera=classify_move(arr),
            luma=round(float(np.mean([r["luma"] for r in rows[a:b]])), 1),
            contrast=round(float(np.mean([r["contrast"] for r in rows[a:b]])), 1),
            p5_p95=[round(float(np.mean([r["p5"] for r in rows[a:b]])), 1),
                    round(float(np.mean([r["p95"] for r in rows[a:b]])), 1)],
            shadow_frac=round(float(np.mean([r["shadow_frac"] for r in rows[a:b]])), 3),
            vignette=round(float(np.mean([r["vignette"] for r in rows[a:b]])), 1),
            sat=round(float(np.mean([r["sat"] for r in rows[a:b]])), 1),
            warmth=round(float(np.mean([r["warmth_r_minus_b"] for r in rows[a:b]])), 1),
            luma_drift=round(float(rows[b - 1]["luma"] - rows[a]["luma"]), 1),
            held_frac=round(float(np.mean([r["held"] for r in rows[a:b]])), 2),
            flashes=sum(1 for r in rows[a:b] if r["event"] == "flash"),
            blur_frames=int(np.sum(sharp[a:b] < 0.35 * np.median(sharp))),
            anim_resid_px=round(float(np.nanmedian(res)) if np.isfinite(res).any() else 0, 2),
        ))
    json.dump(dict(video=name, frames=n, fps=FPS, duration_s=round(n / FPS, 2),
                   events=[dict(frame=i, t=round(i / FPS, 3), kind=k) for i, k in events],
                   shots=shots), open(out / "shots.json", "w"), indent=1)

    # --- review sheets --------------------------------------------------
    def label(img, txt):
        img = img.copy(); cv2.putText(img, txt, (4, 16), 0, 0.45, (0, 0, 0), 3); cv2.putText(img, txt, (4, 16), 0, 0.45, (0, 255, 255), 1); return img
    blank = np.zeros_like(thumbs[0])
    lines = []
    for i, k in events:
        row = [label(thumbs[j], f"{j} {k[:5]}" if j == i else str(j)) if 0 <= j < n else blank for j in range(i - 2, i + 3)]
        lines.append(np.hstack(row))
    if lines:
        cols = 2
        while len(lines) % cols: lines.append(np.zeros_like(lines[0]))
        sheet = np.vstack([np.hstack(lines[r:r + cols]) for r in range(0, len(lines), cols)])
        cv2.imwrite(str(out / "cuts.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 80])
    tiles = []
    for s_i, s in enumerate(shots):
        a, b = s["start_frame"], s["end_frame"]
        tiles.append(np.hstack([label(thumbs[a], f"S{s_i} {a}"), thumbs[(a + b) // 2], label(thumbs[b], str(b))]))
    cols = 3
    while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
    sheet = np.vstack([np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)])
    cv2.imwrite(str(out / "shots.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 80])
    print(f"{name}: {n} frames, {len(shots)} shots, {len(events)} events")
    return json.load(open(out / "shots.json"))


def summary(results):
    L = ["# Shorts analysis (all frames @30 fps)\n",
         "| # | video | dur s | frames | shots | avg shot s | cuts | dissolves | flashes | luma | contrast | moving-cam shots |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    allshots = []
    for k, r in enumerate(results, 1):
        sh = r["shots"]; allshots += sh
        ev = [e["kind"] for e in r["events"]]
        mv = sum(1 for s in sh if s["camera"] != "static/locked")
        L.append(f"| {k} | {r['video'][:40]} | {r['duration_s']} | {r['frames']} | {len(sh)} | "
                 f"{np.mean([s['dur_s'] for s in sh]):.2f} | {ev.count('cut')} | "
                 f"{sum(e.startswith('dissolve') for e in ev)} | {ev.count('flash')} | "
                 f"{np.mean([s['luma'] for s in sh]):.0f} | {np.mean([s['contrast'] for s in sh]):.0f} | {mv}/{len(sh)} |")
    from collections import Counter
    c = Counter()
    for s in allshots:
        for t in s["camera"].split(", "): c[t.split(" ")[0]] += 1
    L += ["\n## Camera moves across all shots\n"] + [f"- {k}: {v}" for k, v in c.most_common()]
    d = np.array([s["dur_s"] for s in allshots])
    L += [f"\n## Shot length\n- shots: {len(d)}, median {np.median(d):.2f}s, p10 {np.percentile(d,10):.2f}s, p90 {np.percentile(d,90):.2f}s"]
    (ROOT / "analysis" / "summary.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    vids = sorted(p for p in (ROOT / "shorts").glob("*") if p.suffix.lower() in (".mp4", ".webm", ".mkv"))
    if len(sys.argv) > 1:
        vids = [pathlib.Path(a) for a in sys.argv[1:]]
    res = [r for r in (analyze(v) for v in vids) if r]
    if res: summary(res)
