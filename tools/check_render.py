#!/usr/bin/env python3
"""Render every page in a real browser and fail on large blank regions.

This exists because of a specific bug: the scroll-reveal rule hid content
with a selector more specific than the `.in` rule meant to reveal it, so
every page below the hero rendered blank. Validators and the link checker
both passed — only looking at a rendered page catches it.

Pages are rendered with scripting ON and reduced-motion OFF, which is the
state the bug lived in. Needs Chrome; skips cleanly if none is found.

    python3 tools/check_render.py
"""
import os, subprocess, sys, shutil, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_GAP = 700          # px of uniform blank allowed mid-page
# A fixed window height crops anything taller than it rather than scaling
# the capture to fit — found the hard way when 5200px silently truncated
# continuous-time.html (actual height ~14000px) and the check never looked
# at its lower two-thirds. 16000px clears every page with real headroom;
# a page that ever grows past that will need this raised again.
VIEW = (1400, 16000)

CANDIDATES = [
    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
    "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    shutil.which("google-chrome"), shutil.which("chromium"),
    shutil.which("chromium-browser"),
]


def find_browser():
    for c in CANDIDATES:
        if c and os.path.exists(c):
            return c
    return None


def page_url(slug):
    """Chrome on Windows reaches the WSL filesystem over the \\wsl.localhost share."""
    distro = os.environ.get("WSL_DISTRO_NAME")
    if distro and ROOT.startswith("/home"):
        return f"file://wsl.localhost/{distro}{ROOT}/{slug}"
    return "file://" + os.path.join(ROOT, slug)


def main():
    browser = find_browser()
    if not browser:
        print("  no Chrome/Edge found — skipping render check")
        return 0
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        print("  numpy/Pillow unavailable — skipping render check")
        return 0

    outdir = os.environ.get("WF_SHOT_DIR", "/mnt/c/Users/jarav/wfshots")
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError:
        print(f"  cannot write screenshots to {outdir} — skipping")
        return 0

    pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))
    win = f"{VIEW[0]},{VIEW[1]}"
    bad = 0

    for slug in pages:
        shot = os.path.join(outdir, slug.replace(".html", "") + ".render.png")
        win_shot = shot
        if shot.startswith("/mnt/c/"):
            win_shot = "C:\\" + shot[len("/mnt/c/"):].replace("/", "\\")
        subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--virtual-time-budget=9000", f"--window-size={win}",
             f"--screenshot={win_shot}", page_url(slug)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if not os.path.exists(shot):
            print(f"    {slug:<24} render FAILED")
            bad += 1
            continue

        a = np.asarray(Image.open(shot).convert("RGB"))
        rows = a.reshape(a.shape[0], -1).std(axis=1) > 2
        last = max((y for y in range(len(rows)) if rows[y]), default=0)

        gap = run = start = best_at = 0
        for y in range(600, last + 1):           # below the hero, above page end
            if not rows[y]:
                if run == 0:
                    start = y
                run += 1
                if run > gap:
                    gap, best_at = run, start
            else:
                run = 0

        ok = gap <= MAX_GAP
        print(f"    {slug:<24} {'pass' if ok else 'FAIL'}   "
              f"content to {last}px, largest mid-page blank {gap}px"
              + ("" if ok else f" at y={best_at}"))
        if not ok:
            bad += 1

    # The failure that actually reached a user: the inline head script arms
    # the reveal styles, then main.js never arrives, so the body stays hidden.
    # Simulate it by moving the script aside and re-rendering the landing page.
    js = os.path.join(ROOT, "assets", "js", "main.js")
    stash = js + ".checkbak"
    if os.path.exists(js):
        shot = os.path.join(outdir, "nojs.render.png")
        win_shot = ("C:\\" + shot[len("/mnt/c/"):].replace("/", "\\")
                    if shot.startswith("/mnt/c/") else shot)
        os.rename(js, stash)
        try:
            subprocess.run(
                [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                 "--virtual-time-budget=9000", "--window-size=1400,2600",
                 f"--screenshot={win_shot}", page_url("index.html")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        finally:
            os.rename(stash, js)
        if os.path.exists(shot):
            a = np.asarray(Image.open(shot).convert("RGB"))
            rows = a.reshape(a.shape[0], -1).std(axis=1) > 2
            frac = rows.sum() / len(rows)
            ok = frac > 0.40
            print(f"    {'index.html (no main.js)':<24} {'pass' if ok else 'FAIL'}   "
                  f"{frac:.0%} content rows (watchdog must reveal the body)")
            if not ok:
                bad += 1

    print(f"  {len(pages)} pages rendered, {bad} with suspicious blank regions")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
