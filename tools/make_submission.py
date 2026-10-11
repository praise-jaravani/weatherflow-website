#!/usr/bin/env python3
"""Build the submission ZIP for projects.cs.uct.ac.za/honsproj/.

The brief requires index.html in the ROOT of the archive, relative links only,
and a filename of <project abbreviation>_<surnames>.zip. Development files are
excluded; everything the site needs to render is included.
"""
import os, sys, zipfile, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "weatherflow_chikwanha_fuyana_jaravani.zip"
SKIP_DIRS = {"tools", "_private", ".git", "dist", "__pycache__", ".github"}
SKIP_FILES = {".gitignore", ".nojekyll", "README.md", ".DS_Store"}

def main():
    # never package a stale build
    if subprocess.call([sys.executable, os.path.join(ROOT, "tools", "build.py")],
                       stdout=subprocess.DEVNULL) != 0:
        print("build failed"); return 1
    if subprocess.call([sys.executable, os.path.join(ROOT, "tools", "check_links.py")],
                       stdout=subprocess.DEVNULL) != 0:
        print("link check failed — not packaging"); return 1
    if subprocess.call([sys.executable, os.path.join(ROOT, "tools", "check_render.py")],
                       stdout=subprocess.DEVNULL) != 0:
        print("render check failed — pages have blank regions, not packaging"); return 1

    out_dir = os.path.join(ROOT, "dist")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, NAME)
    n = total = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and
                       os.path.join(base, d) != out_dir]
            for f in sorted(files):
                if f in SKIP_FILES:
                    continue
                p = os.path.join(base, f)
                rel = os.path.relpath(p, ROOT)
                z.write(p, rel)
                n += 1
                total += os.path.getsize(p)

    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    assert "index.html" in names, "index.html is not at the archive root"
    print(f"  {out}")
    print(f"  {n} files, {total/1024/1024:.1f} MB uncompressed, "
          f"{os.path.getsize(out)/1024/1024:.1f} MB zipped")
    print(f"  index.html at archive root: yes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
