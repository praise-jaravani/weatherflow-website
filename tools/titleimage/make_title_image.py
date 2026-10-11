#!/usr/bin/env python3
"""Compose the Showcase title image: 1024x768, the house format.

The hero visual is the real 32-station SAWS network, drawn from the project's
own coordinates, with each station joined to its nearest neighbours — the
graph the models actually operate on.
"""
import csv, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SC   = "/tmp/claude-1000/-home-praise-Computer-Science-Resources-CSC-Honours-WeatherFlow-Website/9a3a11d5-25c2-4307-b9b6-c668065f41e8/scratchpad"
FONT = f"{SC}/fonts"
CSVP = "/home/praise/Computer_Science_Resources/Weatherflow/data/saws/stations_32node.csv"

W, H, SS = 1024, 768, 3          # supersample for clean edges
CW, CH = W * SS, H * SS

INK        = (252, 251, 248)
INK_DIM    = (168, 196, 206)
INK_FAINT  = (112, 145, 158)
TEAL       = (95, 198, 224)
TEAL_DEEP  = (13, 92, 116)
BG_TOP     = (9, 44, 57)
BG_BOT     = (8, 20, 27)

def f(name, px):
    return ImageFont.truetype(f"{FONT}/{name}.ttf", px * SS)

def stations():
    out = []
    with open(CSVP) as fh:
        for r in csv.DictReader(fh):
            out.append((float(r["longitude"]), float(r["latitude"]),
                        r["station"], r["province"]))
    return out

def main():
    img = Image.new("RGB", (CW, CH), BG_BOT)
    d = ImageDraw.Draw(img)

    # ---- background: vertical gradient + a soft radial bloom behind the map
    for y in range(CH):
        t = y / CH
        e = t ** 0.85
        d.line([(0, y), (CW, y)],
               fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * e) for i in range(3)))

    bloom = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(bloom).ellipse(
        [int(CW * .50), int(CH * .02), int(CW * 1.12), int(CH * .92)], fill=90)
    bloom = bloom.filter(ImageFilter.GaussianBlur(120 * SS // 3))
    img = Image.composite(Image.new("RGB", (CW, CH), TEAL_DEEP), img, bloom)
    d = ImageDraw.Draw(img)

    # ---- the station network, right-hand side
    st = stations()
    lons = [s[0] for s in st]; lats = [s[1] for s in st]
    x0, x1 = min(lons), max(lons); y0, y1 = min(lats), max(lats)
    PX0, PY0 = int(CW * .505), int(CH * .085)
    PX1, PY1 = int(CW * .965), int(CH * .80)
    sx = (PX1 - PX0) / (x1 - x0); sy = (PY1 - PY0) / (y1 - y0)
    s = min(sx, sy)                                  # equal aspect, no distortion
    ox = PX0 + ((PX1 - PX0) - (x1 - x0) * s) / 2
    oy = PY0 + ((PY1 - PY0) - (y1 - y0) * s) / 2
    def proj(lon, lat):
        return (ox + (lon - x0) * s, oy + (y1 - lat) * s)
    pts = [proj(a, b) for a, b, _, _ in st]

    # edges to the 3 nearest neighbours — the graph the STGNNs see
    edges = set()
    for i, p in enumerate(pts):
        dist = sorted(((math.dist(p, q), j) for j, q in enumerate(pts) if j != i))
        for _, j in dist[:3]:
            edges.add((min(i, j), max(i, j)))

    glow = Image.new("RGB", (CW, CH), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i, j in edges:
        gd.line([pts[i], pts[j]], fill=(26, 108, 134), width=max(1, SS))
    for p in pts:
        r = 7 * SS
        gd.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(90, 190, 215))
    glow = glow.filter(ImageFilter.GaussianBlur(9 * SS // 2))
    img = Image.blend(img, Image.blend(img, glow, 0.0), 0)
    img = Image.fromarray(__import__("numpy").clip(
        __import__("numpy").asarray(img, dtype="int16")
        + __import__("numpy").asarray(glow, dtype="int16"), 0, 255).astype("uint8"))
    d = ImageDraw.Draw(img)

    for i, j in edges:                                # crisp edges over the glow
        d.line([pts[i], pts[j]], fill=(44, 124, 150), width=max(1, SS))
    for p in pts:
        r = 3.6 * SS
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=TEAL)
        r2 = 1.5 * SS
        d.ellipse([p[0] - r2, p[1] - r2, p[0] + r2, p[1] + r2], fill=(226, 248, 255))

    # ---- type, left-hand column
    L = int(CW * .062)
    d.text((L, int(CH * .135)), "UNIVERSITY OF CAPE TOWN  ·  SCHOOL OF IT",
           font=f("inter-600", 13), fill=INK_FAINT)
    d.text((L, int(CH * .180)), "HONOURS PROJECT  ·  2026",
           font=f("inter-600", 13), fill=TEAL)

    d.text((L, int(CH * .240)), "WeatherFLOW", font=f("serif-700", 80), fill=INK)

    rule_y = int(CH * .397)
    d.line([(L, rule_y), (L + int(CW * .085), rule_y)], fill=TEAL, width=3 * SS)

    sub = ["Spatio-temporal graph neural", "networks for 48-hour weather",
           "prediction across 32 South", "African weather stations"]
    yy = int(CH * .437)
    for ln in sub:
        d.text((L, yy), ln, font=f("serif-600", 25), fill=INK_DIM)
        yy += int(34 * SS)

    d.text((L, int(CH * .700)), "Génevieve Chikwanha  ·  Zoleka Fuyana  ·  Praise Jaravani",
           font=f("inter-500", 13), fill=INK_DIM)
    d.text((L, int(CH * .740)), "Supervised by A/Prof Deshendran Moodley",
           font=f("inter-400", 13), fill=INK_FAINT)
    d.text((L, int(CH * .780)), "Data: South African Weather Service",
           font=f("inter-400", 13), fill=INK_FAINT)

    cap = "32 SAWS stations  ·  Eastern Cape, KwaZulu-Natal, Free State, Gauteng"
    bb = d.textbbox((0, 0), cap, font=f("inter-400", 12))
    d.text((PX1 - (bb[2] - bb[0]), int(CH * .845)), cap,
           font=f("inter-400", 12), fill=INK_FAINT)

    out = img.resize((W, H), Image.LANCZOS)
    p = os.path.join(HERE, "weatherflow-title-image.png")
    out.save(p, optimize=True)
    print(f"  {p}  {out.size[0]}x{out.size[1]}  {os.path.getsize(p)/1024:.0f} KB")

if __name__ == "__main__":
    main()
