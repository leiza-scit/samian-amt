#!/usr/bin/env python3
"""trace_forms.py - redraw the profile drawings in data/forms-src/ as vector paths.

Marching squares on a 8x bicubic enlargement of each JPG gives sub-pixel outlines.
Three layers per drawing: the black section (level 140), the thin lines (level 215)
and, for the R variants, the grey rim sherd above the profile (own component).
Output: data/forms.json (coordinates in source pixels, two decimals). Deterministic.
Run only when the source drawings change:  python visuals/trace_forms.py
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from skimage import measure
from skimage.transform import resize

HERE = Path(__file__).resolve().parent
S = 8

def contours(arr, level, tol):
    out = []
    for c in measure.find_contours(arr, level):
        c = measure.approximate_polygon(c, tol)
        if len(c) >= 4:
            out.append([(round(x / S, 2), round(y / S, 2)) for y, x in c])
    return out

def d(polys):
    return " ".join("M" + " L".join(f"{x} {y}" for x, y in p) + "Z" for p in polys)

def main():
    res = {}
    for f in sorted((HERE/"data/forms-src").glob("*.jpg")):
        im = np.asarray(Image.open(f).convert("L"), float) / 255
        h, w = im.shape
        big = resize(np.pad(im, 2, constant_values=1), ((h+4)*S, (w+4)*S), order=3, mode="edge")
        big = np.clip(big, 0, 1)
        black = contours(big, 140/255, 0.9)
        thin = contours(big, 215/255, 0.9)
        # rim sherd: the component of "not white" that sits above the profile (R variants)
        lab = measure.label(resize(np.pad(im, 2, constant_values=1), (h+4, w+4), order=0) < 0.93, connectivity=2)
        sherd = None
        if lab.max() > 1:
            props = sorted(measure.regionprops(lab), key=lambda p: p.centroid[0])
            top = props[0]
            if top.area < 0.35 * sum(p.area for p in props) and top.bbox[2] < (h+4) * 0.45:
                y0, x0, y1, x1 = top.bbox
                sherd = [round(v - 2, 1) for v in (x0, y0, x1, y1)]
        key = f.stem
        def inbox(poly, b):
            cx = sum(x for x, _ in poly) / len(poly) - 2; cy = sum(y for _, y in poly) / len(poly) - 2
            return b[0] - 1 <= cx <= b[2] + 1 and b[1] - 1 <= cy <= b[3] + 1
        sherd_poly = []
        if sherd:
            sherd_poly = [p for p in contours(big, 0.93, 0.9) if inbox(p, sherd)]
            black = [p for p in black if not inbox(p, sherd)]
            thin = [p for p in thin if not inbox(p, sherd)]
        res[key] = {"w": w, "h": h, "black": d([[(x-2, y-2) for x, y in p] for p in black]),
                    "thin": d([[(round(x-2, 2), round(y-2, 2)) for x, y in p] for p in thin]), "sherd": d([[(round(x-2, 2), round(y-2, 2)) for x, y in p] for p in sherd_poly]) if sherd else ""}
        print(key, w, h, len(black), len(thin), sherd)
    (HERE/"data/forms.json").write_text(json.dumps(res, sort_keys=True), encoding="utf-8", newline="\n")

if __name__ == "__main__":
    main()
