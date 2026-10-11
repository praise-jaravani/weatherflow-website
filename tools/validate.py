#!/usr/bin/env python3
"""Validate every page against the W3C Nu HTML Checker, and the stylesheet
against the W3C CSS validator. Network access required."""
import os, sys, json, time, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "WeatherFLOW-site-check/1.0 (honours project build check)"}

def nu(path):
    data = open(path, "rb").read()
    req = urllib.request.Request(
        "https://validator.w3.org/nu/?out=json", data=data,
        headers={**UA, "Content-Type": "text/html; charset=utf-8"})
    return json.load(urllib.request.urlopen(req, timeout=60)).get("messages", [])

def css(path):
    data = open(path, "rb").read()
    body = urllib.parse.urlencode({
        "text": data.decode("utf-8"), "profile": "css3svg",
        "output": "json", "warning": "0"}).encode()
    req = urllib.request.Request("https://jigsaw.w3.org/css-validator/validator",
                                 data=body, headers=UA)
    r = json.load(urllib.request.urlopen(req, timeout=90))["cssvalidation"]
    return r.get("errors", []), r.get("result", {})

fail = 0
print("  HTML — W3C Nu checker")
for p in sorted(f for f in os.listdir(ROOT) if f.endswith(".html")):
    try:
        msgs = nu(os.path.join(ROOT, p))
    except Exception as e:
        print(f"    {p:<24} could not reach validator: {e}"); continue
    errs = [m for m in msgs if m.get("type") == "error"]
    warns = [m for m in msgs if m.get("subType") == "warning"]
    flag = "FAIL" if errs else "pass"
    print(f"    {p:<24} {flag}   {len(errs)} error(s), {len(warns)} warning(s)")
    for m in errs + warns:
        print(f"        [{m.get('subType') or m.get('type')}] line {m.get('lastLine','?')}: {m.get('message','')[:150]}")
    fail += len(errs)
    time.sleep(1.5)

print("\n  CSS — W3C CSS validator")
try:
    errs, res = css(os.path.join(ROOT, "assets/css/main.css"))
    print(f"    main.css                 {'FAIL' if errs else 'pass'}   {len(errs)} error(s)")
    for e in errs:
        print(f"        line {e.get('line')}: {e.get('message','').strip()[:150]}")
    fail += len(errs)
except Exception as e:
    print(f"    could not reach CSS validator: {e}")

sys.exit(1 if fail else 0)
