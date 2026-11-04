#!/usr/bin/env python3
"""prepare_basemap.py - thin Natural Earth 1:50m land (public domain) to the window of the Gaulish kiln sites.

Input:  a ne_50m_land.geojson (https://www.naturalearthdata.com/), passed as argument.
Output: data/basemap-gaul.json (rings in lon/lat). Run once:  python visuals/prepare_basemap.py ne_50m_land.geojson
"""
import json
import sys
from pathlib import Path
from skimage import measure

WINDOW = (-6.0, 40.5, 13.0, 54.0)   # lon0, lat0, lon1, lat1

def clip(ring, box):
    x0, y0, x1, y1 = box
    def cut(pts, inside, cross):
        out = []
        for i, b in enumerate(pts):
            a = pts[i - 1]
            if inside(b):
                if not inside(a): out.append(cross(a, b))
                out.append(b)
            elif inside(a): out.append(cross(a, b))
        return out
    ax = lambda x: (lambda a, b: (x, a[1] + (b[1]-a[1]) * (x-a[0]) / (b[0]-a[0])))
    ay = lambda y: (lambda a, b: (a[0] + (b[0]-a[0]) * (y-a[1]) / (b[1]-a[1]), y))
    for ins, cr in ((lambda p: p[0] >= x0, ax(x0)), (lambda p: p[0] <= x1, ax(x1)),
                    (lambda p: p[1] >= y0, ay(y0)), (lambda p: p[1] <= y1, ay(y1))):
        if not ring: break
        ring = cut(ring, ins, cr)
    return ring

def main(src):
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    rings = []
    for f in data["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for p in polys:
            c = clip([tuple(q) for q in p[0]], WINDOW)
            if len(c) >= 3:
                s = measure.approximate_polygon(__import__("numpy").array(c), 0.004)
                if len(s) >= 3:
                    rings.append([[round(x, 3), round(y, 3)] for x, y in s])
    out = Path(__file__).resolve().parent / "data/basemap-gaul.json"
    out.write_text(json.dumps({"window": WINDOW, "rings": rings}, separators=(",", ":")), encoding="utf-8", newline="\n")
    print(len(rings), "rings", out.stat().st_size, "bytes")

if __name__ == "__main__":
    main(sys.argv[1])
