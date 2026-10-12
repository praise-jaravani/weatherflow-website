#!/usr/bin/env python3
"""Build the WeatherFLOW honours project website.

Every page shares one shell (head / header / nav / footer) so that navigation
and links stay identical across the site. Content fragments live in
tools/pages/<slug>.html and are inserted verbatim.

Output is plain static HTML with relative links only — no build artefacts are
required at view time and the site works when opened straight off disk.

    python3 tools/build.py
"""
from __future__ import annotations
import os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "tools", "pages")

# ---------------------------------------------------------------- site data
SITE = "WeatherFLOW"
TAGLINE = "Weather prediction using spatio-temporal graph neural networks"
YEAR = "2026"

NAV = [
    ("index.html",           "Overview"),
    ("background.html",      "Background"),
    ("results.html",         "Results"),
    ("continuous-time.html", "Continuous-time"),
    ("diffusion.html",       "Diffusion"),
    ("lightweight.html",     "Lightweight"),
    ("resources.html",       "Resources"),
]

PAGES = {
    "index.html": dict(
        title=f"{SITE} — {TAGLINE}",
        desc="Honours project comparing continuous-time, diffusion-based and "
             "lightweight spatio-temporal graph neural networks for weather "
             "forecasting on South African weather-station data.",
    ),
    "background.html": dict(
        title=f"Background — {SITE}",
        desc="The forecasting problem, how spatio-temporal graph neural networks "
             "model it, and the three-study South African research lineage this "
             "project extends.",
    ),
    "results.html": dict(
        title=f"Results — {SITE}",
        desc="Forecasting accuracy of six new STGNN architectures against two shared "
             "baselines on 32 South African weather stations, to 48 hours ahead.",
    ),
    "continuous-time.html": dict(
        title=f"Continuous-time STGNNs — {SITE}",
        desc="Praise Jaravani — neural-ODE graph models (MTGODE, STGODE) for normal "
             "and extreme weather prediction on South African station data.",
    ),
    "diffusion.html": dict(
        title=f"Diffusion-based STGNNs — {SITE}",
        desc="Génevieve Chikwanha — probabilistic diffusion models (DiffSTG, USTD) "
             "for weather forecasting on South African station data.",
    ),
    "lightweight.html": dict(
        title=f"Lightweight STGNNs — {SITE}",
        desc="Zoleka Fuyana — parameter-efficient spatio-temporal graph models "
             "(STLGRU, LiteSTGNN) for weather forecasting on South African station data.",
    ),
    "resources.html": dict(
        title=f"Resources — {SITE}",
        desc="Every document, figure and source-code archive produced by the "
             "WeatherFLOW honours project.",
    ),
}

MARK = (
    '<svg class="mark" viewBox="0 0 24 24" width="19" height="19" aria-hidden="true" '
    'focusable="false" fill="none" stroke="currentColor" stroke-width="1.7" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="5" cy="7" r="1.9"/><circle cx="18" cy="5.5" r="1.9"/>'
    '<circle cx="12" cy="13" r="1.9"/><circle cx="19" cy="17.5" r="1.9"/>'
    '<circle cx="5.5" cy="18" r="1.9"/>'
    '<path d="M6.6 8.2 10.6 11.8M16.2 6.4 13.2 11.3M13.5 14.2 17.2 16.4'
    'M10.4 14.2 6.8 16.6M6.9 7.3h9.3"/></svg>'
)

HEAD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Génevieve Chikwanha, Zoleka Fuyana, Praise Jaravani">
<link rel="stylesheet" href="assets/css/main.css">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<script>(function(d,w){{var r=d.documentElement;r.classList.add("js");w.wfUnarm=function(){{r.classList.remove("js");}};setTimeout(function(){{if(!w.wfReady)w.wfUnarm();}},2000);}})(document,window);</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="index.html">{mark}<span>{site}</span> <span class="sub">UCT&nbsp;Honours&nbsp;{year}</span></a>
<nav class="site-nav" aria-label="Main">
<ul>
{navitems}
</ul>
</nav>
<div class="progress" aria-hidden="true"></div>
</div>
</header>
<main id="main">
"""

FOOT = """</main>
<footer class="site-footer">
<div class="wrap">
<div class="cols">
<div>
<h2>Project</h2>
<ul>
<li><a href="index.html">Overview</a></li>
<li><a href="background.html">Background</a></li>
<li><a href="results.html">Results</a></li>
<li><a href="resources.html">Resources</a></li>
</ul>
</div>
<div>
<h2>Workstreams</h2>
<ul>
<li><a href="continuous-time.html">Continuous-time &mdash; Jaravani</a></li>
<li><a href="diffusion.html">Diffusion-based &mdash; Chikwanha</a></li>
<li><a href="lightweight.html">Lightweight &mdash; Fuyana</a></li>
</ul>
</div>
<div>
<h2>Key documents</h2>
<ul>
<li><a href="assets/docs/weatherflow-poster.pdf">Project poster (PDF)</a></li>
<li><a href="assets/docs/final-paper-jaravani.pdf">Final paper &mdash; Jaravani (PDF)</a></li>
<li><a href="assets/docs/final-paper-chikwanha.pdf">Final paper &mdash; Chikwanha (PDF)</a></li>
</ul>
</div>
<div>
<h2>Department</h2>
<ul>
<li>Department of Computer Science</li>
<li>University of Cape Town</li>
<li>Supervisor: A/Prof Deshendran Moodley</li>
</ul>
</div>
</div>
<div class="colophon">
<p>WeatherFLOW &mdash; CSC4002W honours project, Department of Computer Science,
University of Cape Town, {year}.</p>
<p>Station observations supplied by the South African Weather Service and used
under their data policy. Computation on the UCT ICTS High-Performance Computing
cluster. This work is based on research supported in part by the National
Research Foundation of South Africa (ref. PMDS251030376307).</p>
</div>
</div>
</footer>
<script src="assets/js/main.js" defer></script>
</body>
</html>
"""


def nav_html(current: str) -> str:
    out = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "\n".join(out)


def build() -> int:
    written = []
    for slug, meta in PAGES.items():
        frag_path = os.path.join(PAGES_DIR, slug)
        if not os.path.exists(frag_path):
            print(f"  !! missing fragment: tools/pages/{slug}", file=sys.stderr)
            return 1
        body = open(frag_path, encoding="utf-8").read().strip()
        html = (
            HEAD.format(title=meta["title"], desc=meta["desc"], mark=MARK,
                        site=SITE, year=YEAR, navitems=nav_html(slug))
            + body + "\n"
            + FOOT.format(year=YEAR)
        )
        out = os.path.join(ROOT, slug)
        open(out, "w", encoding="utf-8").write(html)
        written.append((slug, len(html)))
    for slug, n in written:
        print(f"  {slug:<24} {n/1024:6.1f} KB")
    print(f"  {len(written)} pages built")
    return 0


if __name__ == "__main__":
    sys.exit(build())
