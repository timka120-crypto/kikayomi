"""Production bible: character sheets, style suffixes, colour grades, map coordinates.

Every generation prompt in the storyboard is assembled from the shot-specific prompt
plus the scene style block plus the global suffix for the shot type, so that
characters, grading and quality rules stay identical across all 147 shots.
"""

TITLE = "OPPENHEIMER: THE MAN WHO CREATED THE POWER TO DESTROY THE WORLD"

# ---------------------------------------------------------------------------
# Character reference sheets. Inserted verbatim into prompts via {KEY}.
# Build a reference image set for each from public-domain photographs
# (Los Alamos National Laboratory, US National Archives, DOE) before generating.
# ---------------------------------------------------------------------------
CHARACTERS = {
    "OPP_CHILD": "the boy J. Robert Oppenheimer (age 10-12): slight and thin, pale complexion, large pale blue eyes, dark hair neatly parted, wearing a 1910s boy's wool suit with knickerbockers, starched collar and dark tie",
    "OPP_TEEN": "the teenage J. Robert Oppenheimer (age 14-16): thin and narrow-shouldered, pale, intense pale blue eyes, dark wavy hair combed back, wearing a 1910s wool school jacket, white shirt and tie",
    "OPP20": "young J. Robert Oppenheimer (age 18-23): tall, very slender, narrow angular face, high cheekbones, intense pale blue eyes, thick dark curly hair brushed up and back, clean-shaven",
    "OPP30": "J. Robert Oppenheimer (age 30-35): tall and gaunt, angular face, deep-set pale blue eyes, dark wavy hair worn full and slightly long on top, clean-shaven, a cigarette usually between his fingers",
    "OPP40": "J. Robert Oppenheimer (age 39-41): tall, extremely thin, gaunt angular face with hollow cheeks, pale blue eyes, short dark hair greying at the temples, clean-shaven, wearing his signature light-grey felt porkpie hat and a loose-fitting single-breasted suit",
    "OPP45": "J. Robert Oppenheimer (age 41, July 1945): tall and emaciated (about 115 lb), visibly exhausted, gaunt face with hollow cheeks and dark circles under pale blue eyes, short dark greying hair, light-grey felt porkpie hat, loose khaki work trousers and light shirt",
    "OPP50": "J. Robert Oppenheimer (age 41-50): thin, close-cropped hair turning grey, lined gaunt face, pale blue eyes, clean-shaven, dark single-breasted suit, narrow tie, a briar pipe",
    "OPP60": "J. Robert Oppenheimer (age 55-62): frail and very thin, short white-grey hair, deeply lined face, pale blue eyes, grey suit and knit tie",
    "GROVES42": "Brigadier General Leslie R. Groves (age 46): tall and heavyset with a broad torso, short wavy brown hair, small trimmed moustache, US Army officer's khaki service uniform with one brigadier general's star on each shoulder",
    "GROVES45": "Major General Leslie R. Groves (age 48): tall and heavyset, short wavy brown hair, small trimmed moustache, US Army khaki uniform with two-star major general insignia",
    "FERMI": "Enrico Fermi (age 41): short, compact build, receding dark hair, strong nose, calm focused expression, grey work coat over a shirt and tie",
    "BORN": "Max Born (age 44): receding dark hair, composed professorial bearing, dark three-piece suit",
    "LAWRENCE": "Ernest O. Lawrence (age 36-38): tall, fair hair, rimless glasses, three-piece suit",
    "SNYDER": "Hartland Snyder (age 26): stocky graduate student, dark hair, rolled shirtsleeves",
    "HAHN": "Otto Hahn (age 59): receding grey hair, neat moustache, white laboratory coat over a suit",
    "STRASSMANN": "Fritz Strassmann (age 36): dark hair combed back, white laboratory coat",
    "SERBER": "Robert Serber (age 33): slight build, dark hair, round-framed glasses, shirt and tie",
    "BETHE": "Hans Bethe (age 37): broad-shouldered, wavy brown hair, round face, open-collar shirt and wool sweater",
    "KISTI": "George Kistiakowsky (age 44): stocky, balding, open-collar khaki work shirt",
    "TIBBETS": "Colonel Paul W. Tibbets Jr. (age 30): lean, dark hair, square jaw, USAAF summer flight coveralls, parachute harness, leather headset",
    "LEWIS": "Captain Robert A. Lewis (co-pilot, age 27): stocky, dark hair, USAAF flight coveralls",
    "FEREBEE": "Major Thomas Ferebee (bombardier, age 26): dark hair, thin moustache, USAAF flight coveralls",
    "PARSONS": "Captain William S. Parsons, US Navy (weaponeer, age 43): balding, slim, khaki shirt",
    "SWEENEY": "Major Charles W. Sweeney (age 25): stocky, dark hair, USAAF flight coveralls",
    "TRUMAN": "President Harry S. Truman (age 61): grey hair neatly parted, round wire-rimmed glasses, double-breasted grey suit, dark tie",
    "GRAY": "Gordon Gray (age 45, board chairman): balding, dark suit, reading glasses",
}

# ---------------------------------------------------------------------------
# Global suffixes, appended by shot type.
# ---------------------------------------------------------------------------
SUFFIX = {
    "REC": (
        "Visual style: premium historical documentary reconstruction, photorealistic, "
        "shot on 35mm film with subtle fine grain, natural motion blur, physically "
        "plausible professionally operated camera movement, realistic anatomy and hands, "
        "natural blinking and micro-expressions, no lip movement, period-accurate details only. "
        "No on-screen text, no signage legible text (all text is added in post), "
        "no cartoon style, no exaggerated effects, no lens flares, 16:9, 4K."
    ),
    "ARCH": (
        "Image-to-video treatment of a real archival source: use the referenced "
        "public-domain archival image as the only source frame; separate it into depth "
        "layers and animate with restrained 2.5D parallax and a slow camera move; "
        "do not alter faces, do not add or remove people or objects, do not colourise "
        "unless stated, preserve original grain, scratches and tonality. Tag on screen "
        "as ARCHIVAL with source credit. 16:9, 4K."
    ),
    "GFX": (
        "Visual style: professional broadcast documentary motion graphics, Adobe After "
        "Effects look, layered 2.5D composition, geographically accurate cartography, "
        "restrained sans-serif typography with generous tracking, smooth eased camera "
        "moves, subtle paper texture and film grain, precise thin-line markers, legible "
        "labels, no cartoon icons, no glitch effects. Final text and map data are built "
        "in After Effects from verified sources; use AI only for background plates. 16:9, 4K."
    ),
}
SUFFIX["MIX"] = SUFFIX["GFX"] + " Then: " + SUFFIX["REC"]

TYPE_LABEL = {
    "REC": "Reconstruction (AI-generated)",
    "ARCH": "Archival (real source, animated)",
    "GFX": "Motion graphics",
    "MIX": "Graphics-to-reconstruction transition",
}

# ---------------------------------------------------------------------------
# Verified marker coordinates (WGS84). Re-check every marker against
# the listed source before final render.
# ---------------------------------------------------------------------------
COORDS = [
    ("New York City (Riverside Drive, Upper West Side)", "40.79 N", "73.98 W", "1904 birth / childhood"),
    ("Cambridge, England (Cavendish Laboratory)", "52.20 N", "0.12 E", "1925-26"),
    ("Göttingen, Germany", "51.53 N", "9.94 E", "1926-27 doctorate"),
    ("Berkeley, California", "37.87 N", "122.26 W", "1929-1942"),
    ("Pasadena, California (Caltech)", "34.14 N", "118.13 W", "1929-1942"),
    ("Berlin-Dahlem (Kaiser Wilhelm Institute for Chemistry)", "52.46 N", "13.29 E", "Dec 1938 fission"),
    ("Pearl Harbor, Hawaii", "21.35 N", "157.95 W", "7 Dec 1941, 7:48 AM local"),
    ("Chicago (Stagg Field, University of Chicago)", "41.79 N", "87.60 W", "2 Dec 1942, CP-1"),
    ("Oak Ridge, Tennessee (Clinton Engineer Works)", "36.01 N", "84.27 W", "uranium enrichment"),
    ("Hanford, Washington (B Reactor)", "46.63 N", "119.65 W", "plutonium production"),
    ("Los Alamos, New Mexico (Project Y)", "35.88 N", "106.30 W", "weapon design, from 1943"),
    ("Washington, D.C.", "38.90 N", "77.04 W", "project headquarters"),
    ("Trinity Site, Jornada del Muerto, New Mexico", "33.677 N", "106.475 W", "16 Jul 1945, 5:29:45 AM local"),
    ("Tinian, North Field (Northern Mariana Islands)", "15.07 N", "145.63 E", "509th Composite Group"),
    ("Iwo Jima", "24.78 N", "141.32 E", "6 Aug rendezvous point"),
    ("Hiroshima hypocentre (near Shima Hospital / Aioi Bridge)", "34.395 N", "132.454 E", "6 Aug 1945, 8:15 AM local"),
    ("Kokura (primary target, 9 Aug)", "33.88 N", "130.88 E", "obscured by haze and smoke"),
    ("Yakushima (9 Aug rendezvous point)", "30.35 N", "130.53 E", "rendezvous"),
    ("Nagasaki hypocentre (Matsuyama-machi, Urakami valley)", "32.774 N", "129.864 E", "9 Aug 1945, 11:02 AM local"),
    ("Tokyo Bay (USS Missouri anchorage)", "35.35 N", "139.75 E", "2 Sep 1945 surrender"),
    ("Semipalatinsk Test Site, Kazakh SSR (RDS-1)", "50.44 N", "77.82 E", "29 Aug 1949 - verify"),
    ("Monte Bello Islands, Australia (UK 'Hurricane')", "20.40 S", "115.55 E", "3 Oct 1952"),
    ("Enewetak Atoll, Elugelab (Ivy Mike)", "11.67 N", "162.19 E", "1 Nov 1952"),
    ("Reggane, Algeria (French 'Gerboise Bleue')", "26.31 N", "0.06 W", "13 Feb 1960 - verify"),
    ("Lop Nur, Xinjiang (China 'Project 596')", "40.82 N", "89.80 E", "16 Oct 1964 - verify"),
    ("Princeton, New Jersey (Institute for Advanced Study)", "40.33 N", "74.67 W", "1947-1967"),
]

MAP_SPEC = [
    ("World / global maps", "Robinson or Equal Earth projection; Natural Earth 1:50m coastlines; 1942 borders from the CShapes 2.0 historical borders dataset."),
    ("Europe 1938-1942", "Lambert Azimuthal Equal-Area centred 52N 15E; borders per date from CShapes 2.0 cross-checked against a published historical atlas; occupation fills keyed to exact dates."),
    ("United States", "Albers Equal-Area Conic (USGS standard parallels); state lines from Natural Earth; facility markers at coordinates listed below."),
    ("New Mexico", "UTM zone 13N; SRTM 30m hillshade; Rio Grande and Jornada del Muerto from USGS hydrography; Los Alamos and Trinity markers with a metric and imperial scale bar."),
    ("Japan / Western Pacific", "Lambert Conformal Conic centred 35N 135E; Natural Earth 1:10m coastline for Japan; Hiroshima and Nagasaki city plans traced from the 1945 US Army Map Service city plans."),
    ("Routes", "Draw only the documented legs: Tinian - Iwo Jima - Hiroshima (6 Aug) and Tinian - Yakushima - Kokura - Nagasaki (9 Aug). Label as 'schematic route' and do not imply exact tracks."),
]

TYPOGRAPHY = [
    ("Location card", "Line 1 place name in caps, 600 weight, tracking +80; line 2 date; line 3 local time. Lower-left third, 6% safe margin, white on 40% black plate."),
    ("Date counter", "Tabular-figure monospace numerals rolling on a 12-frame ease; never faster than 1 digit per 2 frames."),
    ("Lower third", "Name in caps / role in sentence case, thin rule above, enters with 10-frame horizontal wipe."),
    ("Source tags", "Top-right corner, small caps: ARCHIVAL - [archive] or RECONSTRUCTION. Always visible on every shot that is not pure graphics."),
]
