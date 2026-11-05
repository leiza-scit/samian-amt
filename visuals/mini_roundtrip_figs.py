"""Figures of the mini round trip: the same four kinds of statement on the Samian side and on the coin side.

mini-01-cases  four rows: carrier -> potforms (Samian) and coin -> authorities (AFE), with weights and "back: same"
mini-02-form   the same four cases as AFE container and as AMT statement with its five parts

The data come from py/step_mini_roundtrip.py, never from this file. The coins are schematic and invented
(an abstract head, no real coin, no photograph); the numbers are the coins of data/afe/afe-mini-coins.ttl.
"""
from __future__ import annotations

import build as B
from build import INST, MUTED, REAL, TERM, Fig, tw
import step_mini_roundtrip as MR

NAMES = {"Certainty": "certainty", "Uncertainty": "uncertainty", "Vagueness": "vagueness", "FuzzinessWobbliness": "fuzzy / wobbly"}
ROW = 196
STAMPS = ["OF NOVI", "ARVTVS F", "VALENI M", "CASTI OF"]   # invented names, no real potter


def new(name, title, h):
    f = Fig(name, title, 1750, h)
    f.text(60, 60, title, 34, True, anchor="start")
    return f


def coin_art(f, cx, cy, r, seed):
    """A schematic coin: double rim, an abstract head, a dotted legend ring. Drawn, invented, no real coin."""
    heads = ["M-14,26 C-30,10 -26,-18 -8,-30 C6,-40 24,-30 26,-12 C28,0 20,6 22,14 C24,22 12,28 4,26 Z",
             "M-18,28 C-34,6 -22,-24 -2,-32 C16,-38 30,-22 26,-4 L32,6 L22,10 C24,20 10,30 -2,28 Z",
             "M-12,28 C-30,12 -28,-14 -10,-28 C4,-38 22,-34 28,-18 C32,-6 24,-2 26,8 C26,20 12,30 -12,28 Z",
             "M-16,26 C-32,8 -24,-20 -6,-30 C10,-38 28,-26 26,-8 C24,4 30,12 18,20 C10,28 -4,30 -16,26 Z"][seed % 4]
    f.raw(f'<g transform="translate({cx},{cy})">'
          f'<circle r="{r}" fill="#e9d9a6" stroke="#000000" stroke-width="2"/>'
          f'<circle r="{r - 8}" fill="none" stroke="#8a7430" stroke-width="2"/>'
          f'<circle r="{r - 15}" fill="none" stroke="#8a7430" stroke-width="2" stroke-dasharray="2 5"/>'
          f'<g transform="scale({r / 60:.3f})"><path d="{heads}" fill="#c9b36b" stroke="#6b5a1f" stroke-width="2.4" stroke-linejoin="round"/>'
          f'<path d="M-24,36 C-10,44 12,44 28,34" fill="none" stroke="#6b5a1f" stroke-width="2.4"/></g></g>')


def sherd_art(f, cx, cy, seed, k=1.0):
    """A schematic rim-free body sherd with a potter's stamp (abstract bars, no real stamp). Drawn, invented."""
    shapes = ["M-70,-22 L-30,-46 L18,-40 L62,-18 L70,20 L28,44 L-24,40 L-62,22 Z",
              "M-66,-10 L-38,-44 L12,-46 L64,-26 L72,10 L40,40 L-16,46 L-60,28 Z",
              "M-72,-18 L-24,-48 L30,-38 L68,-14 L64,26 L14,46 L-38,42 L-68,20 Z",
              "M-64,-26 L-14,-46 L40,-42 L72,-8 L58,30 L8,46 L-44,38 L-72,8 Z"][seed % 4]
    f.raw(f'<g transform="translate({cx},{cy}) scale({k})">'
          f'<path d="{shapes}" fill="#c2552d" stroke="#000000" stroke-width="2" stroke-linejoin="round"/>'
          f'<path d="{shapes}" fill="none" stroke="#7a2f14" stroke-width="2" stroke-dasharray="3 6" transform="scale(.86)"/>'
          f'<rect x="-52" y="-15" width="104" height="30" rx="2" fill="#a8431f" stroke="#5e220c" stroke-width="2"/>'
          f'<text x="0" y="1" text-anchor="middle" dominant-baseline="central" font-family="Fira Sans" font-weight="500" font-size="19" letter-spacing="1" fill="#4a1a08">{STAMPS[seed % 4]}</text></g>')


def arrows(f, x0, y0, x1, ys, chips, cx):
    for y, t in zip(ys, chips):
        f.path(f"M{x0},{y0} C{x0 + 45},{y0} {x1 - 55},{y} {x1 - 6},{y}", sw=2.2)
        f.chip(cx, (y0 + y) / 2 if len(ys) > 1 else y, t, 18)


def cases(r):
    f = new("mini-01-cases", "Mini round trip: four kinds of statement, two sides", 190 + ROW * 4 + 80)
    f.text(60, 112, "Case", 22, True, MUTED, "start")
    f.text(300, 112, "Samian: carrier → potform  (AMT)", 22, True, MUTED, "start")
    f.text(940, 112, "AFE: coin → issuing authority  (nmo:hasAuthority)", 22, True, MUTED, "start")
    y = 140
    for p, c in zip(r["potform"]["cases"], r["coins"]["cases"]):
        f.rect(50, y, 1650, ROW - 12, "#ffffff", "#d8d6ce", 6)
        mid = y + (ROW - 12) / 2
        f.text(66, mid - 14, f"{p['n']}  {p['name']}", 21, True, "#000000", "start", 230)
        f.text(66, mid + 18, f"{p['note']}", 16, False, MUTED, "start", 230)
        # Samian side
        sherd_art(f, 400, mid - 4, p["n"] - 1)
        f.text(400, mid + 78, f"carrier {p['carrier']}  (drawn sherd)", 15, False, MUTED)
        n = len(p["edges"])
        gap = 50
        ys = [mid + (i - (n - 1) / 2) * gap for i, _ in enumerate(p["edges"])]
        for e, yy in zip(p["edges"], ys):
            f.path(f"M478,{mid} C545,{mid} 575,{yy} 635,{yy}", sw=2.2)
            f.chip(585, yy, f"{e['weight']}", 17)
            f.box(640, yy - 21, 150, 42, e["object"], None, TERM, 20)
        f.text(820, mid, "back: same" if p["same"] else "back: different", 17, True, "#166534", "start")
        # AFE side
        coin_art(f, 985, mid, 62, p["n"] - 1)
        f.text(985, mid + 82, f"coin {c['coin']}  (drawn)", 15, False, MUTED)
        n = len(c["edges"])
        ys = [mid + (i - (n - 1) / 2) * gap for i, _ in enumerate(c["edges"])]
        for e, yy in zip(c["edges"], ys):
            f.path(f"M1050,{mid} C1110,{mid} 1140,{yy} 1190,{yy}", sw=2.2)
            f.chip(1135, yy, f"{e['weight']}", 17)
            f.box(1195, yy - 21, 230, 42, e["object"], None, INST, 20)
        f.text(1450, mid - 12, "back: same" if c["verdict"] == "same" else "back: " + c["verdict"], 17, True, "#166534", "start")
        f.text(1450, mid + 14, NAMES[p["edges"][0]["type"]], 16, False, MUTED, "start")
        y += ROW
    f.legend(y + 24, [(TERM, "potform"), (INST, "authority"), (B.PROP, "weight = fw:hasDegreeOfConnection = amt:weight")])
    f.text(60, y + 62, "Coins and sherds with potter's stamps are schematic and invented (the names are made up).", 16, False, MUTED, "start")
    f.save()


def form_lines(c):
    cls_ = c["form"]
    p = "nmo:hasAuthority"
    if cls_["kind"] == "direct":
        return [f"{p}  nm:{cls_['members'][0][0]}"]
    head = f"{p}  [ fw:{cls_['class']}" + (" + skos:Collection" if cls_["kind"] == "collection" else "") + " ]"
    return [head] + [f"    nm:{v}   {w}" for v, w in cls_["members"]]


def amt_lines(c):
    if not c["edges"]:
        return ["(no statement)"]
    return [f"afe:{c['coin']}  nmo:hasAuthority  nm:{e['object']}   {e['weight']}   fw:{e['type']}" for e in c["edges"]]


def form(r):
    h = 200 + sum(max(len(form_lines(c)), len(amt_lines(c))) * 28 + 70 for c in r["coins"]["cases"])
    f = new("mini-02-form", "The same four cases as AFE container and as AMT statement", h)
    f.text(60, 112, "AFE container (Turtle, short)", 22, True, MUTED, "start")
    f.text(770, 112, "AMT statements: subject, property, object, weight, type", 22, True, MUTED, "start")
    y = 140
    for p, c in zip(r["potform"]["cases"], r["coins"]["cases"]):
        a, m = form_lines(c), amt_lines(c)
        hh = max(len(a), len(m)) * 28 + 24
        f.text(60, y + 14, f"{p['n']}  {p['name']}  ·  coin {c['coin']}", 20, True, B.DARK, "start")
        f.rect(50, y + 36, 700, hh, "#ffffff", "#d8d6ce", 6)
        f.rect(770, y + 36, 930, hh, "#fffbea", "#d8d6ce", 6)
        for i, t in enumerate(a):
            f.text(66, y + 36 + 28 + 28 * i, t, 17, False, "#000000", "start", 670)
        for i, t in enumerate(m):
            f.text(786, y + 36 + 28 + 28 * i, t, 17, False, "#000000", "start", 900)
        f.path(f"M752,{y + 36 + hh / 2} L768,{y + 36 + hh / 2}", sw=2.2)
        y += hh + 70
    f.text(60, y, "Five parts only: no fw:hasMethod and no evidence. The way back needs nothing else to rebuild the container.", 16, False, MUTED, "start")
    f.save()


# ---------------------------------------------------------------- one figure per case and side
PW, PGAP, PX = 500, 80, 60
LINK = {"samian": "amt-to-afe.rq / afe-to-amt.rq", "coin": "afe-to-amt.rq / amt-to-afe.rq"}


def lines_afe(subj, prop, form):
    if form["kind"] == "direct":
        pre = "sam:" if prop == "sam:hasType" else "nm:"
        return [f"{subj}  {prop}  {pre}{form['members'][0][0]}"]
    pre = "sam:" if prop == "sam:hasType" else "nm:"
    cls = f"    a fw:{form['class']}" + (", skos:Collection" if form["kind"] == "collection" else "") + " ;"
    return [f"{subj}  {prop}  [", cls] + [f"    {'skos:member' if form['kind'] == 'collection' else 'rdf:value'}  {pre}{v}   {w}" for v, w in form["members"]]


def lines_amt(subj, prop, edges):
    pre = "sam:" if prop == "sam:hasType" else "nm:"
    nm = (lambda o: "pf_" + MR.slug(o)) if prop == "sam:hasType" else (lambda o: o)
    return [f"{subj}  {prop}"] + [f"    {pre}{nm(e['object'])}   {e['weight']}   fw:{e['type']}" for e in edges]


def draw_obj(f, side, cx, cy, n):
    if side == "samian":
        sherd_art(f, cx, cy, n - 1, 0.9)
    else:
        coin_art(f, cx, cy, 52, n - 1)


def panel(f, x, side, kind, title, n, edges, form, subj, prop, sy, verdict=None, cell_lines=0):
    """One panel: the drawn object, arrows with chips above the line, the targets; below it the text of the form."""
    pre = "sam:" if side == "samian" else "nm:"
    f.text(x + PW / 2, sy - 52, title, 24, True)
    mid = sy + 70
    ne = len(edges)
    gap = 54
    ys = [mid + (i - (ne - 1) / 2) * gap for i in range(ne)]
    ox = x + 72
    reach = 66 if side == "samian" else 54
    draw_obj(f, side, ox, mid, n)
    tx, tw_ = (x + 300, 190) if kind == "amt" else (x + 325, 175)
    if kind == "amt":
        for e, yy in zip(edges, ys):
            f.path(f"M{ox + reach},{mid} C{ox + reach + 60},{mid} {tx - 80},{yy} {tx - 6},{yy}", sw=2.2)
            f.chip(tx - 52, yy, f"{e['weight']}", 17)
            f.box(tx, yy - 21, tw_, 42, e["object"], None, TERM if side == "samian" else INST, 20)
        f.text(x + PW / 2, ys[-1] + 44, "fw:" + edges[0]["type"], 17, True, MUTED)
        lines = lines_amt(subj, prop, edges)
    else:
        if form["kind"] == "direct":
            f.path(f"M{ox + reach},{mid} L{tx - 6},{mid}", sw=2.2)
            f.chip(tx - 90, mid, "direct", 17)
            f.box(tx, mid - 21, tw_, 42, form["members"][0][0], None, TERM if side == "samian" else INST, 20)
        else:
            cxn = x + 156
            f.path(f"M{ox + reach},{mid} L{cxn - 4},{mid}", sw=2.2)
            f.box(cxn, mid - 17, 46, 34, "[ ]", None, ("#ffffff", "#000000", "#000000"), 18, dash=True)
            for (v, w), yy in zip(form["members"], ys):
                f.path(f"M{cxn + 46},{mid} C{cxn + 70},{mid} {tx - 80},{yy} {tx - 6},{yy}", sw=2.2)
                f.chip(tx - 52, yy, f"{w}", 17)
                f.box(tx, yy - 21, tw_, 42, v, None, TERM if side == "samian" else INST, 19)
        f.text(x + PW / 2, ys[-1] + 44, ("fw:" + form["class"]) if form["class"] else "direct value = fw:Certainty", 17, True, MUTED)
        lines = lines_afe(subj, prop, form)
    top = sy + 215
    h = 26 * max(len(lines), cell_lines) + 20
    f.rect(x, top, PW, h, "#ffffff" if kind == "afe" else "#fffbea", "#d8d6ce", 6)
    for i, t in enumerate(lines):
        f.text(x + 14, top + 24 + 26 * i, fit(t, 15, PW - 24), 15, False, "#000000", "start")
    if verdict:
        f.rect(x + PW - 150, sy - 36, 150, 30, REAL[0], "#000000", 4)
        f.text(x + PW - 75, sy - 21, verdict, 17, True, REAL[2])
    return top + h


def fit(t, size, maxw):
    while tw(t, size) > maxw and len(t) > 4:
        t = t[:-2].rstrip() + "…"
    return t


def case_fig(side, p, c, r_idx):
    """Left to right: the first form, the second form, the first form again (rebuilt)."""
    case = p if side == "samian" else c
    n = p["n"]
    name = f"mini-case-{n}-{'sherd' if side == 'samian' else 'coin'}"
    subj_s = "ic:" + p["carrier"] if side == "samian" else "afe:" + c["coin"]
    prop = "sam:hasType" if side == "samian" else "nmo:hasAuthority"
    edges = case["edges"]
    form = case["form"]
    order = ("amt", "afe", "amt") if side == "samian" else ("afe", "amt", "afe")
    titles = {"amt": "AMT (hextuples)", "afe": "AFE (container pattern)"}
    cl = max(len(lines_amt(subj_s, prop, edges)), len(lines_afe(subj_s, prop, form)))
    h = 190 + 215 + 26 * cl + 20 + 90
    what = "Samian: carrier → potform" if side == "samian" else "AFE: coin → authority"
    f = new(name, f"Case {n}, {p['name']}: {what}", h)
    sy = 190
    ends = []
    for i, kind in enumerate(order):
        x = PX + i * (PW + PGAP)
        t = titles[kind] + (" again" if i == 2 else "")
        ends.append(panel(f, x, side, kind, t, n, edges, form, subj_s, prop, sy, None, cl))
    for i in range(2):
        x0 = PX + i * (PW + PGAP) + PW + 6
        f.path(f"M{x0},{sy + 70} L{x0 + PGAP - 12},{sy + 70}", sw=2.6)
        f.text(x0 + (PGAP - 12) / 2, sy + 46, "query", 15, False, MUTED)
    f.text(60, max(ends) + 36, ("Invented sherd with an invented potter's stamp; weights by the rule of py/weights.py. " if side == "samian"
           else "Invented coin; weights as entered in data/afe/afe-mini-coins.ttl. ") + "Queries: " + LINK[side] + ".", 15, False, MUTED, "start")
    f.save()


def main():
    r = MR.run()
    cases(r)
    form(r)
    for i, (p, c) in enumerate(zip(r["potform"]["cases"], r["coins"]["cases"])):
        case_fig("samian", p, c, i)
        case_fig("coin", p, c, i)
    print("10 mini round-trip figures ->", B.IMG)
    return r


if __name__ == "__main__":
    main()
