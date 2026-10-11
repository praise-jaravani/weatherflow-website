"""Extract figure regions from the final-paper PDFs as PNGs.

For each 'Figure N:' caption we take the union of vector-drawing and raster
bboxes that sit above it in the same column band, then render that region.
"""
import fitz, re, os, sys, json

DPI = 240
PAD = 6

def clusters(page):
    boxes = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.width > 3 and r.height > 3:
            boxes.append(fitz.Rect(r))
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") == 1:
            boxes.append(fitz.Rect(b["bbox"]))
    return boxes

def captions(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        txt = " ".join(s["text"] for l in b["lines"] for s in l["spans"])
        m = re.match(r'\s*Figure\s+(\d+)\s*[:.]', txt)
        if m:
            out.append((int(m.group(1)), fitz.Rect(b["bbox"]), txt.strip()))
    return out

def extract(pdf, outdir, tag):
    doc = fitz.open(pdf)
    os.makedirs(outdir, exist_ok=True)
    manifest = []
    for pno, page in enumerate(doc):
        caps = captions(page)
        if not caps:
            continue
        boxes = clusters(page)
        for num, crect, ctext in caps:
            # drawings above the caption, horizontally overlapping it
            # a caption wider than 60% of the page belongs to a full-width
            # figure; otherwise restrict to the caption's own column band
            pw = page.rect.width
            full = crect.width > 0.6 * pw
            lo, hi = (0, pw) if full else (crect.x0 - 18, crect.x1 + 18)
            cand = []
            for b in boxes:
                if not (b.y1 <= crect.y0 + 2 and b.y1 > crect.y0 - 430):
                    continue
                cx = 0.5 * (b.x0 + b.x1)
                if lo <= cx <= hi:
                    cand.append(b)
            if not cand:
                continue
            reg = cand[0]
            for b in cand[1:]:
                reg |= b
            # never reach above the previous caption in the same column
            ceil = crect.y0 - 430
            for _n, _r, _t in caps:
                if _r is crect:
                    continue
                _cx = 0.5 * (_r.x0 + _r.x1)
                if _r.y1 <= crect.y0 - 4 and (full or lo <= _cx <= hi):
                    ceil = max(ceil, _r.y1 + 3)
            reg.y0 = max(reg.y0, ceil)
            cand = [b for b in cand if b.y1 > reg.y0]
            if not cand:
                continue
            reg = cand[0]
            for b in cand[1:]:
                reg |= b
            reg.y0 = max(reg.y0, ceil)
            reg = fitz.Rect(reg.x0-PAD, reg.y0-PAD, reg.x1+PAD, reg.y1+PAD) & page.rect
            if reg.width < 60 or reg.height < 45:
                continue
            name = f"{tag}-fig{num}.png"
            pix = page.get_pixmap(clip=reg, dpi=DPI, alpha=False)
            pix.save(os.path.join(outdir, name))
            manifest.append(dict(file=name, fig=num, page=pno+1,
                                 w=pix.width, h=pix.height,
                                 caption=re.sub(r'\s+',' ',ctext)[:300]))
    return manifest

if __name__ == "__main__":
    allm = {}
    for pdf, tag in [("assets/docs/final-paper-jaravani.pdf","jaravani"),
                     ("assets/docs/final-paper-chikwanha.pdf","chikwanha")]:
        allm[tag] = extract(pdf, "assets/img/figures", tag)
        print(f"\n### {tag}")
        for m in allm[tag]:
            print(f"  fig{m['fig']:<2} p{m['page']:<3} {m['w']}x{m['h']:<5} {m['caption'][:95]}")
    json.dump(allm, open("tools/figures.json","w"), indent=2)
