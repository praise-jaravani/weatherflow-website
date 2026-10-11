#!/usr/bin/env python3
"""Verify every relative link, asset and in-page anchor resolves on disk.

External (absolute) links are listed but not followed.
"""
import os, re, sys, html
from urllib.parse import urldefrag, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTR = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.I)
IDRE = re.compile(r'\bid\s*=\s*"([^"]+)"')

pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
ids = {p: set(IDRE.findall(open(os.path.join(ROOT, p), encoding="utf-8").read()))
       for p in pages}

bad, ext, checked = [], set(), 0
for p in pages:
    src = open(os.path.join(ROOT, p), encoding="utf-8").read()
    for raw in ATTR.findall(src):
        url = html.unescape(raw).strip()
        if url.startswith(("http://", "https://")):
            ext.add((p, url)); continue
        if url.startswith(("mailto:", "tel:", "data:")):
            continue
        checked += 1
        target, frag = urldefrag(url)
        target = unquote(target)
        if target == "":                       # same-page anchor
            if frag and frag not in ids[p]:
                bad.append((p, url, "missing anchor on this page"))
            continue
        path = os.path.normpath(os.path.join(ROOT, target))
        if not path.startswith(ROOT):
            bad.append((p, url, "escapes site root")); continue
        if not os.path.exists(path):
            bad.append((p, url, "file not found")); continue
        if frag and target.endswith(".html"):
            if frag not in ids.get(target, set()):
                bad.append((p, url, f"missing anchor #{frag} in {target}"))

print(f"  pages:            {len(pages)}")
print(f"  internal links:   {checked}")
print(f"  external links:   {len(ext)}")
for p, u in sorted(ext):
    print(f"      {p} -> {u}")
if bad:
    print(f"\n  BROKEN ({len(bad)}):")
    for p, u, why in bad:
        print(f"      {p:<22} {u:<46} {why}")
    sys.exit(1)
print("\n  all internal links and anchors resolve")
