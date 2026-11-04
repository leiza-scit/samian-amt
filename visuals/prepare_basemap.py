#!/usr/bin/env python3
"""prepare_basemap.py - thin Natural Earth layers (public domain) to the window of the Gaulish kiln sites.

Input: a folder with these Natural Earth GeoJSON files (https://github.com/nvkelso/natural-earth-vector, folder geojson/)
    ne_50m_land, ne_10m_rivers_lake_centerlines, ne_10m_rivers_europe, ne_10m_admin_0_boundary_lines_land,
    ne_10m_admin_1_states_provinces, ne_10m_populated_places_simple
Output: data/basemap-gaul.json with land rings, rivers, region borders, country borders, region labels, cities.
Run once (needs numpy and scikit-image):  python visuals/prepare_basemap.py <folder>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from skimage import measure

WINDOW = (-6.0, 40.5, 13.0, 54.0)   # lon0, lat0, lon1, lat1
LABEL_COUNTRIES = {"FRA", "DEU", "BEL"}
RIVER_NAMES = {"Rhne": "Rhône", "Sane": "Saône", "Mosel": "Moselle", "Maas": "Meuse", "Rhein": "Rhine", "Rhin": "Rhine"}


def inside(p):
    return WINDOW[0] <= p[0] <= WINDOW[2] and WINDOW[1] <= p[1] <= WINDOW[3]


def load(folder, name):
    return json.loads((Path(folder) / f"{name}.geojson").read_text(encoding="utf-8"))["features"]


def simp(pts, tol):
    a = measure.approximate_polygon(np.array(pts), tol)
    return [[round(float(x), 3), round(float(y), 3)] for x, y in a]


def lines_of(geom):
    if not geom or not geom["coordinates"]:
        return []
    return [geom["coordinates"]] if geom["type"] == "LineString" else list(geom["coordinates"])


def runs_inside(line):
    """The stretches of a line that lie inside the window (points outside end a stretch)."""
    run = []
    for p in line:
        if inside(p):
            run.append(tuple(p[:2]))
        else:
            if len(run) >= 2:
                yield run
            run = []
    if len(run) >= 2:
        yield run


def clip_ring(ring, box):
    x0, y0, x1, y1 = box

    def cut(pts, ins, cross):
        out = []
        for i, b in enumerate(pts):
            a = pts[i - 1]
            if ins(b):
                if not ins(a):
                    out.append(cross(a, b))
                out.append(b)
            elif ins(a):
                out.append(cross(a, b))
        return out
    ax = lambda x: (lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])))
    ay = lambda y: (lambda a, b: (a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y))
    for ins, cr in ((lambda p: p[0] >= x0, ax(x0)), (lambda p: p[0] <= x1, ax(x1)),
                    (lambda p: p[1] >= y0, ay(y0)), (lambda p: p[1] <= y1, ay(y1))):
        if not ring:
            break
        ring = cut(ring, ins, cr)
    return ring


def land(folder):
    rings = []
    for f in load(folder, "ne_50m_land"):
        g = f["geometry"]
        for p in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            c = clip_ring([tuple(q) for q in p[0]], WINDOW)
            if len(c) >= 3:
                s = simp(c, 0.004)
                if len(s) >= 3:
                    rings.append(s)
    return rings


def rivers(folder):
    out, seen = [], set()
    for file, maxrank in (("ne_10m_rivers_lake_centerlines", 9), ("ne_10m_rivers_europe", 11)):
        for f in load(folder, file):
            pr = f["properties"]
            if (pr.get("scalerank") or 99) > maxrank:
                continue
            name = RIVER_NAMES.get(pr.get("name") or "", pr.get("name") or "")
            for line in lines_of(f["geometry"]):
                for run in runs_inside(line):
                    key = (round(run[0][0], 2), round(run[0][1], 2), round(run[-1][0], 2), round(run[-1][1], 2))
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append({"n": name, "s": int(pr["scalerank"]), "p": simp(run, 0.006)})
    return out


def country_borders(folder):
    out = []
    for f in load(folder, "ne_10m_admin_0_boundary_lines_land"):
        for line in lines_of(f["geometry"]):
            for run in runs_inside(line):
                out.append(simp(run, 0.006))
    return out


def area_centroid(ring):
    a = np.array(ring)
    x, y = a[:, 0], a[:, 1]
    cr = x * np.roll(y, -1) - np.roll(x, -1) * y
    ar = cr.sum() / 2
    if abs(ar) < 1e-12:
        return abs(ar), float(x.mean()), float(y.mean())
    return abs(ar), float(((x + np.roll(x, -1)) * cr).sum() / (6 * ar)), float(((y + np.roll(y, -1)) * cr).sum() / (6 * ar))


def regions(folder):
    """Region borders (edges shared by polygons of two different groups) and one label point per group."""
    edges = defaultdict(set)
    acc = defaultdict(lambda: [0.0, 0.0, 0.0])
    for f in load(folder, "ne_10m_admin_1_states_provinces"):
        pr, g = f["properties"], f["geometry"]
        if pr["adm0_a3"] not in LABEL_COUNTRIES or not g:
            continue
        group = (pr["adm0_a3"], pr.get("region") or pr["name"])
        for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            ring = [tuple(q[:2]) for q in poly[0]]
            if not any(inside(p) for p in ring):
                continue
            ar, cx, cy = area_centroid(ring)
            if inside((cx, cy)):
                s = acc[group]
                s[0] += ar; s[1] += ar * cx; s[2] += ar * cy
            for a, b in zip(ring, ring[1:]):
                if inside(a) and inside(b):
                    edges[tuple(sorted((tuple(round(v, 4) for v in a), tuple(round(v, 4) for v in b))))].add(group)
    border = [e for e, gs in edges.items() if len(gs) > 1]
    adj = defaultdict(list)
    for a, b in border:
        adj[a].append(b); adj[b].append(a)
    used, paths = set(), []
    for start in sorted(adj):
        for nxt in sorted(adj[start]):
            if frozenset((start, nxt)) in used:
                continue
            path = [start, nxt]
            used.add(frozenset((start, nxt)))
            while True:
                cands = [q for q in sorted(adj[path[-1]]) if frozenset((path[-1], q)) not in used]
                if not cands:
                    break
                used.add(frozenset((path[-1], cands[0])))
                path.append(cands[0])
            paths.append(path)
    labels = [{"n": g[1], "x": round(v[1] / v[0], 3), "y": round(v[2] / v[0], 3), "a": round(v[0], 2)}
              for g, v in sorted(acc.items()) if v[0] > 0]
    return [simp(p, 0.008) for p in paths if len(p) >= 2], labels


def cities(folder):
    out = []
    for f in load(folder, "ne_10m_populated_places_simple"):
        x, y = f["geometry"]["coordinates"][:2]
        pr = f["properties"]
        if inside((x, y)) and (pr["pop_max"] or 0) >= 150000:
            out.append({"n": pr["name"], "x": round(x, 3), "y": round(y, 3), "p": int(pr["pop_max"])})
    return sorted(out, key=lambda c: (-c["p"], c["n"]))


def main(folder):
    rb, labels = regions(folder)
    data = {"window": WINDOW, "rings": land(folder), "rivers": rivers(folder), "borders": country_borders(folder),
            "regions": rb, "region_labels": labels, "cities": cities(folder)}
    out = Path(__file__).resolve().parent / "data/basemap-gaul.json"
    out.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8", newline="\n")
    print({k: len(v) for k, v in data.items() if isinstance(v, list)}, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
