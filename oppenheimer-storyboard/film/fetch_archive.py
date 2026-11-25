"""Slowly search Wikimedia Commons for public-domain/CC archival photos and download previews.
Respects rate limits: one request every ~8 s, exponential backoff on HTTP 429."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(__file__).parent / "archive"
UA = "HistoryDocBuilder/1.0 (non-commercial documentary research)"
QUERIES = {
 "groves_portrait": "Leslie Groves portrait", "trinity_fireball": "Trinity test fireball 1945",
 "trinity_color": "Trinity shot color Aeby", "trinity_gadget": "Trinity gadget Bradbury tower",
 "trinity_groundzero": "Oppenheimer Groves Trinity ground zero", "littleboy": "Little Boy bomb Tinian",
 "fatman": "Fat Man bomb Tinian trailer", "tibbets": "Tibbets waving Enola Gay cockpit",
 "enola_gay": "Enola Gay B-29 1945 Tinian", "hiroshima_ruins": "Hiroshima after atomic bombing 1945 ruins",
 "hiroshima_dome": "Hiroshima Prefectural Industrial Promotion Hall 1945", "urakami": "Urakami Cathedral 1945 ruins",
 "missouri": "Surrender of Japan USS Missouri 1945", "ivy_mike": "Ivy Mike mushroom cloud",
 "einstein_letter": "Einstein Szilard letter Roosevelt 1939", "calutron": "Calutron operators Y-12",
 "cp1": "Chicago Pile-1 1942", "pearl_harbor": "USS Arizona burning Pearl Harbor 1941",
 "hahn_apparatus": "Hahn Strassmann apparatus nuclear fission Deutsches Museum", "los_alamos_1940s": "Los Alamos 1940s Manhattan Project buildings",
 "primer": "Los Alamos Primer LA-1", "fermi_award": "Fermi Award Oppenheimer Johnson 1963",
 "e_award": "Army-Navy E award Los Alamos 1945 Oppenheimer", "lawrence_cyclotron": "Lawrence cyclotron Berkeley 1930s",
 "max_born": "Max Born physicist", "trinity_obelisk": "Trinity site obelisk", "lanterns": "Hiroshima lantern floating ceremony dome",
 "nyt_1945": "newspaper front page August 1945 atomic bomb", "rds1": "RDS-1 Soviet atomic bomb 1949",
 "oppenheimer_1950s": "Oppenheimer 1950s", "hanford_b": "Hanford B Reactor 1944", "k25": "K-25 Oak Ridge 1945",
 "fuller_lodge": "Fuller Lodge Los Alamos", "oppenheimer_young": "J. Robert Oppenheimer young 1920s",
}


def get(url, tries=8):
    delay = 10
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(delay); delay = min(delay * 2, 120); continue
            if e.code == 404:
                return None
            time.sleep(delay)
        except Exception:
            time.sleep(delay)
    return None


def main():
    OUT.mkdir(exist_ok=True)
    idx_p = OUT / "candidates.json"
    idx = json.loads(idx_p.read_text()) if idx_p.exists() else {}
    for key, q in QUERIES.items():
        if key in idx:
            continue
        api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6"
               f"&gsrlimit=8&gsrsearch={urllib.parse.quote(q)}&prop=imageinfo&iiprop=url|extmetadata|size&iiurlwidth=1920")
        raw = get(api)
        time.sleep(8)
        if not raw:
            print("fail", key, flush=True); continue
        pages = json.loads(raw).get("query", {}).get("pages", {})
        cands = []
        for p in sorted(pages.values(), key=lambda p: p.get("index", 99)):
            ii = (p.get("imageinfo") or [{}])[0]
            md = ii.get("extmetadata", {})
            lic = md.get("LicenseShortName", {}).get("value", "")
            if not any(s in lic.lower() for s in ("public domain", "pd", "cc0", "cc by")):
                continue
            if ii.get("width", 0) < 700 or not p["title"].lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
                continue
            cands.append(dict(title=p["title"], thumb=ii.get("thumburl"), url=ii.get("url"), license=lic,
                              artist=md.get("Artist", {}).get("value", "")[:200], w=ii.get("width"), h=ii.get("height")))
        idx[key] = cands[:3]
        for i, cnd in enumerate(idx[key]):
            dst = OUT / f"{key}_{i}.jpg"
            if not dst.exists() and cnd["thumb"]:
                data = get(cnd["thumb"])
                if data:
                    dst.write_bytes(data)
                time.sleep(6)
        idx_p.write_text(json.dumps(idx, indent=1))
        print("ok", key, len(idx[key]), flush=True)


if __name__ == "__main__":
    main()
