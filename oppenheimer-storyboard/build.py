"""Assemble the storyboard: timecodes, full prompts, validation, and JSON/Markdown/CSV outputs."""
import csv, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bible import TITLE, CHARACTERS, SUFFIX, TYPE_LABEL, COORDS, MAP_SPEC, TYPOGRAPHY
from shots_1 import SCENES_1
from shots_2 import SCENES_2, ENOLA

OUT = Path(__file__).parent
TARGET = 900
SUBS = dict(CHARACTERS, ENOLA=ENOLA)


def tc(s):
    return f"{s // 60:02d}:{s % 60:02d}"


def build():
    scenes, shots, t, n = [], [], 0, 0
    for si, sc in enumerate(SCENES_1 + SCENES_2, 1):
        s_start = t
        ids = []
        for sh in sc["shots"]:
            n += 1
            body = sh["p"].format_map(SUBS)
            prompt = f"{body} {sc['style']} {SUFFIX[sh['type']]}"
            assert "{" not in prompt, f"unresolved placeholder in shot {n}"
            assert 3 <= sh["d"] <= 8, f"shot {n} duration {sh['d']}"
            rec = dict(n=n, scene=si, start=tc(t), end=tc(t + sh["d"]), dur=sh["d"],
                       type=sh["type"], type_label=TYPE_LABEL[sh["type"]],
                       see=sh["see"], act=sh["act"], cam=sh["cam"], light=sh["light"],
                       gfx=sh["gfx"], tr=sh["tr"], prompt=prompt)
            t += sh["d"]
            shots.append(rec)
            ids.append(n)
        scenes.append(dict(n=si, title=sc["title"], period=sc["period"], grade=sc["grade"],
                           sound=sc["sound"], start=tc(s_start), end=tc(t),
                           dur=t - s_start, first=ids[0], last=ids[-1]))
    assert t == TARGET, f"total runtime {t}s != {TARGET}s"
    used = sorted({k for k in SUBS for s in SCENES_1 + SCENES_2 for x in s["shots"] if "{" + k + "}" in x["p"]})
    return dict(title=TITLE, runtime=tc(t), shot_count=n, scenes=scenes, shots=shots,
                characters=[dict(key=k, sheet=CHARACTERS[k]) for k in CHARACTERS if k in used],
                aircraft=ENOLA, coords=[dict(place=a, lat=b, lon=c, note=d) for a, b, c, d in COORDS],
                map_spec=[dict(name=a, spec=b) for a, b in MAP_SPEC],
                typography=[dict(name=a, spec=b) for a, b in TYPOGRAPHY],
                suffix=SUFFIX)


def write_md(d):
    L = [f"# {d['title']}", "",
         f"Production storyboard - runtime {d['runtime']} - {d['shot_count']} shots - 16:9, 3840x2160", "",
         "Visual production script only: no narration or dialogue. Every shot is tagged ARCHIVAL, RECONSTRUCTION or GRAPHICS.", "",
         "## Scene overview", "", "| # | Scene | Period | Time | Shots |", "|---|---|---|---|---|"]
    for s in d["scenes"]:
        L.append(f"| {s['n']} | {s['title']} | {s['period']} | {s['start']}-{s['end']} | {s['first']}-{s['last']} |")
    for s in d["scenes"]:
        L += ["", f"## Scene {s['n']}: {s['title']} ({s['period']})", "",
              f"**Time:** {s['start']}-{s['end']} ({s['dur']} s)  ", f"**Colour grade:** {s['grade']}  ",
              f"**Sound design:** {s['sound']}"]
        for sh in d["shots"]:
            if sh["scene"] != s["n"]:
                continue
            L += ["", f"### Shot {sh['n']:03d} - {sh['start']}-{sh['end']} ({sh['dur']} s) - {sh['type_label']}", "",
                  f"- **What the viewer sees:** {sh['see']}",
                  f"- **Action and environment:** {sh['act']}",
                  f"- **Camera:** {sh['cam']}",
                  f"- **Lighting and atmosphere:** {sh['light']}",
                  f"- **Motion graphics / on-screen text:** {sh['gfx']}",
                  f"- **Transition in:** {sh['tr']}",
                  "", "**AI video generation prompt:**", "", f"> {sh['prompt']}"]
    L += ["", "## Character reference sheets", ""] + [f"- **{c['key']}:** {c['sheet']}" for c in d["characters"]]
    L += ["", f"- **ENOLA_GAY (aircraft):** {d['aircraft']}", "", "## Map production spec", ""]
    L += [f"- **{m['name']}:** {m['spec']}" for m in d["map_spec"]]
    L += ["", "## Marker coordinates (verify before final render)", "", "| Place | Lat | Lon | Note |", "|---|---|---|---|"]
    L += [f"| {c['place']} | {c['lat']} | {c['lon']} | {c['note']} |" for c in d["coords"]]
    L += ["", "## Typography", ""] + [f"- **{x['name']}:** {x['spec']}" for x in d["typography"]]
    (OUT / "STORYBOARD.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def write_csv(d):
    cols = ["n", "scene", "start", "end", "dur", "type", "see", "act", "cam", "light", "gfx", "tr", "prompt"]
    with open(OUT / "storyboard.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(d["shots"])


if __name__ == "__main__":
    d = build()
    (OUT / "storyboard.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    write_md(d)
    write_csv(d)
    for s in d["scenes"]:
        print(f"{s['n']:>2} {s['start']}-{s['end']} {s['dur']:>4}s shots {s['first']}-{s['last']}  {s['title']}")
    from collections import Counter
    print("total", d["runtime"], "shots", d["shot_count"], Counter(x["type"] for x in d["shots"]))
    gaps = [x["n"] for x in d["shots"] if x["dur"] > 7]
    print("shots over 7 s:", gaps)
