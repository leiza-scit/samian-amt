#!/usr/bin/env python3
"""prepare_roman.py - the Roman layers for the maps, thinned to the window of the Gaulish kiln sites.

Inputs
  <roman-empire>  a checkout of https://github.com/klokantech/roman-empire (folder data/: provinces, provinces_label,
                  places_medium; from the Digital Atlas of the Roman Empire, DARE)
  <itinere>       itinere_roads.geojson of Itiner-e (de Soto et al. 2025, https://doi.org/10.5281/zenodo.17122148, CC BY 4.0);
                  the file is in EPSG:3395 (ellipsoidal Mercator) and is converted to longitude / latitude here
Output: data/roman-gaul.json  (province borders and labels, main and secondary roads, major places)
Run once (needs numpy):  python visuals/prepare_roman.py <roman-empire> <itinere_roads.geojson>

Province borders: an edge shared by two provinces is a border; an edge with one province only is kept if it lies inland (the
limes), and dropped if it runs along the coast, where Natural Earth already draws the coastline.
"""
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from matplotlib.path import Path as MPath
from skimage import measure

HERE = Path(__file__).resolve().parent
WINDOW = (-6.0, 40.5, 13.0, 54.0)
R_EARTH, E = 6378137.0, 0.0818191908426


def inside(p):
    return WINDOW[0] <= p[0] <= WINDOW[2] and WINDOW[1] <= p[1] <= WINDOW[3]


def simp(pts, tol):
    a = measure.approximate_polygon(np.array(pts), tol)
    return [[round(float(x), 3), round(float(y), 3)] for x, y in a]


def unmercator(x, y):
    lon = np.degrees(x / R_EARTH)
    t = np.exp(-y / R_EARTH)
    phi = np.pi / 2 - 2 * np.arctan(t)
    for _ in range(6):
        s = E * np.sin(phi)
        phi = np.pi / 2 - 2 * np.arctan(t * ((1 - s) / (1 + s)) ** (E / 2))
    return lon, np.degrees(phi)


def runs_inside(line):
    run = []
    for p in line:
        if inside(p):
            run.append((p[0], p[1]))
        else:
            if len(run) >= 2:
                yield run
            run = []
    if len(run) >= 2:
        yield run


def provinces(roman):
    land = [MPath(np.array(r)) for r in json.loads((HERE / "data/basemap-gaul.json").read_text(encoding="utf-8"))["rings"]]

    def on_land(pts):
        ok = np.zeros(len(pts), bool)
        for p in land:
            ok |= p.contains_points(pts)
        return ok

    edges = defaultdict(set)
    for f in json.loads((roman / "data/provinces.geojson").read_text(encoding="utf-8"))["features"]:
        name = f["properties"]["name"]
        g = f["geometry"]
        for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            for ring in poly:
                ring = [tuple(q[:2]) for q in ring]
                for a, b in zip(ring, ring[1:]):
                    if inside(a) and inside(b):
                        edges[tuple(sorted((tuple(round(v, 4) for v in a), tuple(round(v, 4) for v in b))))].add(name)
    keep = [e for e, ns in edges.items() if len(ns) > 1]
    single = [e for e, ns in edges.items() if len(ns) == 1]
    if single:
        mids = np.array([((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in single])
        ok = np.ones(len(single), bool)
        for dx, dy in ((.04, 0), (-.04, 0), (0, .04), (0, -.04), (.03, .03), (-.03, -.03), (.03, -.03), (-.03, .03)):
            ok &= on_land(mids + [dx, dy])
        keep += [e for e, k in zip(single, ok) if k]
    adj = defaultdict(list)
    for a, b in keep:
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
    labels = []
    for f in json.loads((roman / "data/provinces_label.geojson").read_text(encoding="utf-8"))["features"]:
        n = f["properties"]["name"]
        x, y = f["geometry"]["coordinates"][:2]
        if inside((x, y)) and not re.fullmatch(r"[IVX]+", n):
            labels.append({"n": n, "x": round(x, 3), "y": round(y, 3)})
    return [simp(p, 0.008) for p in paths if len(p) >= 2], labels


def places(roman):
    out = []
    for f in json.loads((roman / "data/places_medium.geojson").read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        x, y = f["geometry"]["coordinates"][:2]
        if inside((x, y)) and p["major"] >= 2 and p["type"] == "13" and p["latin"]:   # type 13: cities and towns
            out.append({"n": p["latin"].lstrip("*"), "m": p["modern"], "x": round(x, 3), "y": round(y, 3), "r": int(p["major"])})
    return sorted(out, key=lambda c: (-c["r"], c["n"]))


def roads(path):
    out = []
    for f in json.loads(Path(path).read_text(encoding="utf-8"))["features"]:
        g, pr = f["geometry"], f["properties"]
        if not g:
            continue
        lines = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        for line in lines:
            a = np.array(line, float)
            lon, lat = unmercator(a[:, 0], a[:, 1])
            if not ((lon >= WINDOW[0]) & (lon <= WINDOW[2]) & (lat >= WINDOW[1]) & (lat <= WINDOW[3])).any():
                continue
            for run in runs_inside(list(zip(lon, lat))):
                s = simp(run, 0.008)
                if len(s) >= 2:
                    out.append({"k": 0 if pr["Type"] == "Main Road" else 1, "h": 1 if pr["Segment_s"] == "Hypothetical" else 0, "p": s})
    return out


def main(roman, itinere):
    roman = Path(roman)
    pv, pl = provinces(roman)
    data = {"window": WINDOW, "provinces": pv, "province_labels": pl, "places": places(roman), "roads": roads(itinere)}
    out = HERE / "data/roman-gaul.json"
    out.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8", newline="\n")
    print({k: len(v) for k, v in data.items() if isinstance(v, list)}, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
