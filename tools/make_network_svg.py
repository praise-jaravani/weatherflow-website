#!/usr/bin/env python3
"""Generate the hero constellation SVG from the real 32-station network.

Same data and construction as the Showcase title image: true coordinates,
equal aspect, each station joined to its three nearest neighbours. Nodes
pulse gently via CSS embedded in the SVG, which animates even when the file
is referenced from an <img> element.
"""
import csv, math, os

CSVP = "/home/praise/Computer_Science_Resources/Weatherflow/data/saws/stations_32node.csv"
OUT = "assets/img/network.svg"
W, H, PAD = 720, 560, 34

rows = list(csv.DictReader(open(CSVP)))
pts_geo = [(float(r["longitude"]), float(r["latitude"])) for r in rows]
x0 = min(p[0] for p in pts_geo); x1 = max(p[0] for p in pts_geo)
y0 = min(p[1] for p in pts_geo); y1 = max(p[1] for p in pts_geo)
s = min((W - 2 * PAD) / (x1 - x0), (H - 2 * PAD) / (y1 - y0))
ox = PAD + ((W - 2 * PAD) - (x1 - x0) * s) / 2
oy = PAD + ((H - 2 * PAD) - (y1 - y0) * s) / 2
pts = [(round(ox + (lo - x0) * s, 1), round(oy + (y1 - la) * s, 1))
       for lo, la in pts_geo]

edges = set()
for i, p in enumerate(pts):
    for _, j in sorted((math.dist(p, q), j) for j, q in enumerate(pts) if j != i)[:3]:
        edges.add((min(i, j), max(i, j)))
edges = sorted(edges)

lines = "".join(
    f'<line x1="{pts[i][0]}" y1="{pts[i][1]}" x2="{pts[j][0]}" y2="{pts[j][1]}"'
    f' class="e" style="--d:{(i * 7 + j * 3) % 40 / 10:.1f}s"/>'
    for i, j in edges)
dots = "".join(
    f'<circle cx="{x}" cy="{y}" r="5.5" class="n" style="--d:{i % 16 * 0.25:.2f}s"/>'
    for i, (x, y) in enumerate(pts))
halos = "".join(
    f'<circle cx="{x}" cy="{y}" r="13" class="h" style="--d:{i % 16 * 0.25:.2f}s"/>'
    for i, (x, y) in enumerate(pts))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"
 aria-label="Network diagram of 32 South African weather stations, each joined to its three nearest neighbours.">
<title>The 32-station SAWS network as a graph</title>
<style>
  .e {{ stroke:#0d6e8c; stroke-width:1.5; opacity:.40;
        animation:drawIn 1.1s ease-out both; animation-delay:var(--d); }}
  .n {{ fill:#0d6e8c; animation:pop .6s cubic-bezier(.2,.8,.2,1) both,
        pulse 4.5s ease-in-out infinite; animation-delay:var(--d), calc(var(--d) + 1s); }}
  .h {{ fill:#22a5c8; opacity:.20; animation:halo 4.5s ease-in-out infinite;
        animation-delay:var(--d); transform-origin:center; transform-box:fill-box; }}
  @keyframes drawIn {{ from {{ opacity:0 }} to {{ opacity:.40 }} }}
  @keyframes pop    {{ from {{ opacity:0; r:0 }} to {{ opacity:1; r:5.5 }} }}
  @keyframes pulse  {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.55 }} }}
  @keyframes halo   {{ 0%,100% {{ transform:scale(.72); opacity:.16 }}
                       50% {{ transform:scale(1.15); opacity:.30 }} }}
  @media (prefers-reduced-motion: reduce) {{
    .e,.n,.h {{ animation:none }} .e {{ opacity:.40 }} .n {{ opacity:1 }} .h {{ opacity:.20 }}
  }}
</style>
<g>{lines}</g><g>{halos}</g><g>{dots}</g>
</svg>
'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(svg)
print(f"  {OUT}  {len(pts)} nodes, {len(edges)} edges, {os.path.getsize(OUT)/1024:.1f} KB")
