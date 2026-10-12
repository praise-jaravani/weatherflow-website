# WeatherFLOW — honours project website

Project website for **WeatherFLOW: Weather Prediction using Spatio-Temporal
Graph Neural Networks**, an honours project in the Department of Computer
Science, University of Cape Town, 2026.

Génevieve Chikwanha · Zoleka Fuyana · Praise Jaravani
Supervisor: A/Prof Deshendran Moodley

## The site

Static HTML, one hand-written stylesheet and one small dependency-free script.
No framework, no build step at view time and **no external requests** — every
asset, including both typefaces, is served by relative path, so the site renders
identically from a web server or opened straight off disk.

The script is progressive enhancement only (scroll reveals, reading progress,
counting stats). With scripting disabled the site is fully readable and every
link works; all motion is suppressed under `prefers-reduced-motion`.

| | |
|---|---|
| Pages | 7 |
| Internal links | 287, all resolving |
| External links | 3 (departmental project archive, 2 live GitHub repos) |
| HTML validation | 0 errors, 0 warnings — W3C Nu checker |
| CSS validation | valid — W3C CSS validator |
| Renders from `file://` | verified in headless Chrome |
| Blank-region check | 7/7 pages pass |

## Layout

    index.html              group entry page
    background.html         problem, STGNNs, the South African research lineage
    results.html            all workstreams against the shared baselines
    continuous-time.html    Praise Jaravani
    diffusion.html          Génevieve Chikwanha
    lightweight.html        Zoleka Fuyana
    resources.html          documents, source code, data statement, citation
    assets/
      css/                  main.css — the only stylesheet
      js/                   main.js — progressive enhancement only
      fonts/                Source Serif 4, Inter (OFL 1.1), Latin subsets
      img/figures/          figures extracted from the final-paper PDFs
      docs/                 proposal, poster, final papers
      code/                 WeatherFLOW source archive
    tools/                  build and check scripts (not part of the site)

## Working on it

Page content lives in `tools/pages/<slug>.html` as body fragments; the shared
shell — head, header, nav, footer — lives in `tools/build.py`, so navigation
stays identical across every page.

    python3 tools/build.py          # regenerate the 7 pages
    python3 tools/check_links.py    # every relative link and anchor
    python3 tools/check_render.py   # renders each page, fails on blank regions
    python3 tools/validate.py       # W3C HTML + CSS validators (needs network)
    python3 tools/make_network_svg.py # regenerate the hero constellation
    python3 tools/make_submission.py  # build the submission ZIP

Always rebuild after editing a fragment — the root `.html` files are generated.
