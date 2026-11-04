#!/usr/bin/env python3
"""build.py - figures for the vagueness / uncertainty cases of Potform and ProductionCentre (CHNT2026).

Nine figures in the *-visuals house pattern (1750x1000, Fira Sans, SVG plus PNG) and a caption
page, written to visuals/site/. One figure per case:

    PF.1  informationcarrier--potform           multiple OR        [A or B]    vagueness
    PF.2  informationcarrier--potform           question mark      [A?]        uncertainty
    PF.3  informationcarrier--potform           OR + question mark [A or B?]   fuzzy / wobbly
    PF.4  informationcarrier--potform           OR with observed shares (colour bars of the website)
    PC.1  actor--productioncentre               one OR             [A or B]    vagueness
    PC.2  actor--productioncentre               multiple AND       [A and B]   vagueness
    PC.3  actor--productioncentre               AND + question mark            fuzzy / wobbly
    PC.4  actor--productioncentre               question mark      [A?]        uncertainty
    IC-PC.1 informationcarrier--productioncentre question mark    [A?]        uncertainty

Weights, FW types and methods come from py/weights.py (the rule of the source paper), never from
this file. The example strings and carriers are in data/cases.csv (extract of the CHNT exports);
the kiln sites in data/kilnsites-gaul.csv; the profile drawings in data/forms.json (traced from
data/forms-src/ by trace_forms.py); the coastline in data/basemap-gaul.json.

    python visuals/build.py
"""
import csv
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import ImageFont
import resvg_py

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "py"))
import weights as wt  # noqa: E402

SITE, IMG, DATA = HERE / "site", HERE / "site" / "img", HERE / "data"
R, M = HERE / "fonts/FiraSans-Regular.ttf", HERE / "fonts/FiraSans-Medium.ttf"
W, H = 1750, 1000

# Flo's semantic colour scheme (fill, stroke, text)
INST = ("#e2e8f0", "#000000", "#000000")   # subject / object
REAL = ("#166534", "#000000", "#ffffff")   # real object
CLS = ("#9a3412", "#000000", "#ffffff")    # class
TERM = ("#4c1d95", "#000000", "#ffffff")   # term
OWL = ("#ffffff", "#000000", "#000000")    # OWL node
PROP = ("#fbbf24", "#000000", "#000000")   # property metadata
DARK, MUTED, LINE = "#1f1f1d", "#55544f", "#55544f"
SEA, LAND = "#dbe9f2", "#f3f1e8"

TYPE_LABEL = {"Certainty": "certainty", "Uncertainty": "uncertainty", "Vagueness": "vagueness",
              "FuzzinessWobbliness": "fuzzy / wobbly"}


def tw(s, size, med=False):
    font = ImageFont.truetype(str(M if med else R), 100, layout_engine=ImageFont.Layout.BASIC)
    return round(font.getlength(s) * size / 100, 1)


def wrap(s, size, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if tw(t, size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


class Fig:
    def __init__(s, name, title):
        s.name = name
        s.o = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"><title>{escape(title)}</title>',
               f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
               f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="{LINE}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>']

    def text(s, x, y, t, size=22, med=False, color=DARK, anchor="middle", maxw=None, halo=False):
        if maxw and tw(t, size, med) > maxw:
            raise ValueError(f"{s.name}: too wide ({tw(t, size, med):.0f}>{maxw}): {t}")
        wt_ = ' font-weight="500"' if med else ""
        hl = ' stroke="#ffffff" stroke-width="5" stroke-linejoin="round" paint-order="stroke"' if halo else ""
        s.o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central" font-family="Fira Sans" font-size="{size}"{wt_} fill="{color}"{hl}>{escape(t)}</text>')

    def rect(s, x, y, w, h, fill, stroke="none", rx=0, sw=1, dash=False):
        ds = ' stroke-dasharray="8 6"' if dash else ""
        s.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{ds}/>')

    def box(s, x, y, w, h, title, sub=None, st=INST, ts=23, ss=19, rx=6, dash=False, left=None):
        f, b, c = st
        s.rect(x, y, w, h, f, b, rx, 2.4 if dash else 1, dash)
        cx, anchor = (x + w / 2, "middle") if left is None else (x + left, "start")
        mw = w - 14 if left is None else w - left - 10
        if sub:
            s.text(cx, y + h / 2 - ts * .58, title, ts, True, c, anchor, mw)
            s.text(cx, y + h / 2 + ts * .66, sub, ss, False, c, anchor, mw)
        else:
            s.text(cx, y + h / 2, title, ts, True, c, anchor, mw)

    def path(s, d, dash=False, m="a"):
        ds = ' stroke-dasharray="7 6"' if dash else ""
        mk = f' marker-end="url(#{m})"' if m else ""
        s.o.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.6"{ds}{mk}/>')

    def chip(s, x, y, t, size=19, anchor="middle", med=False):
        w = tw(t, size, med) + 18
        x0 = x - w / 2 if anchor == "middle" else x
        s.rect(x0, y - 16, w, 32, PROP[0], "#000000", 4)
        s.text(x0 + w / 2, y, t, size, med, "#000000")
        return w

    def legend(s, y, items, x=60):
        for st, t in items:
            s.rect(x, y - 11, 22, 22, st[0], "#000000", 3)
            s.text(x + 32, y, t, 19, color=MUTED, anchor="start")
            x += 34 + tw(t, 19) + 34

    def raw(s, x):
        s.o.append(x)

    def save(s):
        IMG.mkdir(parents=True, exist_ok=True)
        p = IMG / f"{s.name}.svg"
        p.write_text("\n".join(s.o + ["</svg>"]) + "\n", encoding="utf-8", newline="\n")
        (IMG / f"{s.name}.png").write_bytes(bytes(resvg_py.svg_to_bytes(
            svg_path=str(p), background="#ffffff", skip_system_fonts=True, font_files=[str(R), str(M)], zoom=2.0)))


# ---------------------------------------------------------------- data

def read_csv(p, delim=","):
    with open(p, encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter=delim))


CASES = {r["case"]: r for r in read_csv(DATA / "cases.csv")}
SHARES = read_csv(DATA / "shares.csv")
KILNS = {r["site"]: r for r in read_csv(DATA / "kilnsites-gaul.csv")}
FORMS = json.loads((DATA / "forms.json").read_text(encoding="utf-8"))
BASE = json.loads((DATA / "basemap-gaul.json").read_text(encoding="utf-8"))
# spelling in the centre strings -> name in the kiln-site table
SITE_ALIAS = {"Saint-Saturnin": "Jonquières, Saint Saturnin", "Vichy": "Vichy, Terre Franche"}


def statements(code):
    """Weight, FW type and method of every statement of a case, from py/weights.py."""
    c = CASES[code]
    return c, wt.parse(c["source_string"]), wt.edges_for(c["source_string"], c["relation"])


def n_fmt(n):
    return f"{int(n):,}"


# ---------------------------------------------------------------- shared furniture

def header(f, code, title, c, st, edges):
    ftype = edges[0]["type"]
    w = tw(code, 28, True) + 30
    f.rect(60, 46, w, 48, PROP[0], "#000000", 5)
    f.text(60 + w / 2, 70, code, 28, True)
    f.text(60 + w + 22, 70, title, 34, True, anchor="start")
    f.text(60, 124, f"{c['relation']}  ·  pattern  [{c['source_string'] if len(c['source_string']) < 34 else pattern_name(edges)}]  ·  {TYPE_LABEL[ftype]}", 22, False, MUTED, "start")


def pattern_name(edges):
    return {"or": "A or B", "and": "A and B", "q": "A?", "q+or": "A or B?", "q+and": "A and B?"}[edges[0]["pattern"]]


def rule_line(f, st, edges, x, y, anchor="start"):
    e = edges[0]
    n_all = st.n_questionmark + st.n_possibilities
    f.text(x, y, f"weight = 1 / (n? + n possibilities) = 1 / ({st.n_questionmark} + {st.n_possibilities}) = {e['weight']:.2f}", 24, False, DARK, anchor)


def hextuple_chips(f, edges, x, y, vertical=False):
    e = edges[0]
    items = [f"fw:hasDegreeOfConnection  {e['weight']:.2f}", f"fw:hasType  fw:{e['type']}", f"fw:hasMethod  fw:{e['method']}"]
    for t in items:
        w = f.chip(x, y, t, 20, "start")
        if vertical:
            y += 42
        else:
            x += w + 14


def note(f, t, x=60, y=968, anchor="start"):
    f.text(x, y, t, 17, False, MUTED, anchor)


# ---------------------------------------------------------------- potform figures

def form_art(f, key, x, y, scale):
    v = FORMS[key]
    f.raw(f'<g transform="translate({x:.1f} {y:.1f}) scale({scale})">'
          f'<path d="{v["thin"]}" fill="{DARK}" fill-rule="evenodd"/>'
          f'<path d="{v["black"]}" fill="#000000" fill-rule="evenodd"/>'
          + (f'<path d="{v["sherd"]}" fill="#b3b3ae" fill-rule="evenodd"/>' if v["sherd"] else "") + "</g>")


def potform_fig(name, code, title, subnote, forms):
    """forms: list of (potform label, drawing key). Weights and types are read from the case."""
    c, st, edges = statements(code)
    f = Fig(name, f"{code} {title}")
    header(f, code, title, c, st, edges)
    ncard = len(forms)
    ghost = st.n_questionmark and st.connective == ""
    slots = ncard + (1 if ghost else 0)
    ch, gap = (200, 26) if slots <= 2 else (186, 22)
    total = slots * ch + (slots - 1) * gap
    top = 190 + (650 - total) / 2
    cx, cw = 800, 890
    maxh = max(FORMS[k]["h"] for _, k in forms)
    scale = min(3.4, (ch - 34) / maxh)
    cy_carrier = 190 + 650 / 2
    # carrier and evidence
    f.box(60, cy_carrier - 60, 380, 120, c["pottername"], f"InformationCarrier  ·  id {c['carrier_id']}", INST, 28, 20, 30)
    ev_y = 700
    f.rect(60, ev_y, 380, 130, OWL[0], OWL[1], 6, 2.4, True)
    f.text(250, ev_y + 30, "fw:TextEvidence", 23, True)
    f.text(250, ev_y + 66, f"“{c['source_string']}”", 22, False, DARK, maxw=360)
    f.text(250, ev_y + 100, "fw:sourceString", 17, False, MUTED)
    f.path(f"M250 {cy_carrier + 60} V {ev_y}", dash=True)
    f.text(262, (cy_carrier + 60 + ev_y) / 2, "fw:derivedFrom", 19, False, MUTED, "start")
    f.text(520, cy_carrier - 30, "hasType", 21, True, DARK, "start")
    assert len(edges) == ncard, f"{code}: {len(edges)} statements but {ncard} drawings"
    for i, ((label, key), e) in enumerate(zip(forms, edges)):
        y = top + i * (ch + gap)
        mid = y + ch / 2
        f.rect(cx, y, cw, ch, "#ffffff", "#000000", 6)
        f.rect(cx, y, 230, ch, TERM[0], "#000000", 6)
        f.text(cx + 115, mid - 22, label, 40, True, TERM[2], maxw=214)
        f.text(cx + 115, mid + 28, "Potform", 21, False, TERM[2])
        form_art(f, key, cx + 250 + (cw - 250 - 150 * scale) / 2 - 10, y + (ch - FORMS[key]["h"] * scale) / 2, scale)
        f.path(f"M440 {cy_carrier} H 620 V {mid} H {cx}")
        f.chip(710, mid, f"{e['weight']:.2f}", 22, "middle", True)
    if ghost:
        y = top + ncard * (ch + gap)
        f.rect(cx, y, cw, ch, "#ffffff", "#000000", 6, 2.4, True)
        f.text(cx + cw / 2, y + ch / 2 - 18, "any other form", 30, True, MUTED)
        f.text(cx + cw / 2, y + ch / 2 + 24, "the “?” counts as one more possibility; it is not an edge", 21, False, MUTED)
    rule_line(f, st, edges, 60, 880)
    hextuple_chips(f, edges, 60, 922)
    f.legend(968, [(INST, "InformationCarrier"), (TERM, "Potform"), (OWL, "evidence"), (PROP, "hextuple elements")], 880 if False else 1010)
    note(f, subnote, 60, 968)
    f.save()
    return f.name


def share_fig(name, code, title, subnote):
    """Equal share (the rule) against the observed share of each form in the database (the colour bars of the website)."""
    c, st, edges = statements(code)
    rows = [r for r in SHARES if r["case"] == code]
    freq = [round(int(r["count"]) / int(r["total"]), 2) for r in rows]
    for r in rows:   # the percentages the website shows must follow from the counts
        if round(100 * int(r["count"]) / int(r["total"]), 2) != float(r["page_percent"]):
            raise SystemExit(f"{code} {r['form']}: counts give {100 * int(r['count']) / int(r['total']):.2f} %, the page says {r['page_percent']} %")
    f = Fig(name, f"{code} {title}")
    f.raw('<defs><linearGradient id="gy" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#15803d"/><stop offset="1" stop-color="#86efac"/></linearGradient>'
          '<linearGradient id="rd" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#f59e0b"/><stop offset="1" stop-color="#ef4444"/></linearGradient></defs>')
    header(f, code, title, c, st, edges)
    ch, gap, cx, cw = 240, 36, 800, 890
    top = 190 + (650 - (2 * ch + gap)) / 2
    cy_c = 190 + 650 / 2
    f.box(60, cy_c - 60, 340, 120, "any carrier", "InformationCarrier  ·  with this string", INST, 28, 19, 30)
    ev_y = 700
    f.rect(60, ev_y, 340, 130, OWL[0], OWL[1], 6, 2.4, True)
    f.text(230, ev_y + 30, "fw:TextEvidence", 23, True)
    f.text(230, ev_y + 66, f"“{c['source_string']}”", 22, False, DARK, maxw=320)
    f.text(230, ev_y + 100, "fw:sourceString", 17, False, MUTED)
    f.path(f"M230 {cy_c + 60} V {ev_y}", dash=True)
    f.text(242, (cy_c + 60 + ev_y) / 2, "fw:derivedFrom", 19, False, MUTED, "start")
    f.text(440, cy_c - 30, "hasType", 21, True, DARK, "start")
    for i, (r, e, fr) in enumerate(zip(rows, edges, freq)):
        y = top + i * (ch + gap)
        mid = y + ch / 2
        f.rect(cx, y, cw, ch, "#ffffff", "#000000", 6)
        f.rect(cx, y, 200, ch, TERM[0], "#000000", 6)
        f.text(cx + 100, mid - 22, r["form"], 44, True, TERM[2], maxw=186)
        f.text(cx + 100, mid + 28, "Potform", 21, False, TERM[2])
        if r["form"] in FORMS:
            form_art(f, r["form"], cx + 215, mid - FORMS[r["form"]]["h"] * 1.0, 2.0)
        else:
            f.rect(cx + 215, mid - 70, 300, 140, "#ffffff", MUTED, 4, 1.6, True)
            f.text(cx + 365, mid, "drawing not supplied", 20, False, MUTED)
        bx, bw = cx + 545, 320
        f.text(bx, mid - 52, f"{100 * int(r['count']) / int(r['total']):.2f} %", 36, True, DARK, "start")
        f.text(bx, mid - 14, f"{n_fmt(r['count'])} of {n_fmt(r['total'])}", 21, False, MUTED, "start")
        f.rect(bx, mid + 12, bw * int(r["count"]) / int(r["total"]), 26, "url(#gy)", "#000000", 0, 1)
        f.rect(bx + bw * int(r["count"]) / int(r["total"]), mid + 12, bw * (1 - int(r["count"]) / int(r["total"])), 26, "url(#rd)", "#000000", 0, 1)
        f.path(f"M400 {cy_c} H 500 V {mid} H {cx}")
        f.chip(650, mid - 20, f"equal share  {e['weight']:.2f}", 19, "middle")
        f.chip(650, mid + 20, f"frequency  {fr:.2f}", 19, "middle", True)
    f.text(60, 872, f"equal share: 1 / (0 + {st.n_possibilities}) = {edges[0]['weight']:.2f} each (fw:EqualShareRule)", 22, False, DARK, "start")
    f.text(60, 906, "frequency: " + "   ·   ".join(f"{n_fmt(r['count'])} / {n_fmt(r['total'])} = {fr:.2f}" for r, fr in zip(rows, freq)), 22, False, DARK, "start")
    x = 60
    for t in (f"fw:hasDegreeOfConnection  {freq[0]:.2f}", f"fw:hasType  fw:{edges[0]['type']}", "fw:hasMethod  fw:RelativeFrequency (proposal)"):
        x += f.chip(x, 944, t, 19, "start") + 12
    note(f, subnote, 60, 978)
    f.save()
    return f.name


# ---------------------------------------------------------------- production-centre figures

def project(lon, lat, win):
    lon0, lat0, span, k = win
    return 1000 / 2 + (lon - lon0) * k * math.cos(math.radians(lat0)), 1000 / 2 - (lat - lat0) * k


RIVER_W = lambda rank: 3.4 if rank <= 4 else 2.7 if rank <= 6 else 2.1 if rank <= 8 else 1.5
RIVER_LABELS = {"Loire", "Seine", "Garonne", "Rhône", "Saône", "Allier", "Moselle", "Rhine", "Meuse", "Marne", "Dordogne", "Main", "Neckar", "Doubs"}
C_RIVER, C_REGION, C_COUNTRY, C_PLACE = "#8fb9d6", "#b4af97", "#857f6a", "#9d977f"


def pl(pts, win):
    return " ".join("%.1f,%.1f" % project(x, y, win) for x, y in pts)


def hit(r, rects):
    return any(r[0] < q[0] + q[2] and q[0] < r[0] + r[2] and r[1] < q[1] + q[3] and q[1] < r[1] + r[3] for q in rects)


def draw_base(f, win, keep_clear):
    """Sea, land, region borders, country borders, rivers, region names, large cities (all Natural Earth, modern)."""
    f.rect(0, 0, 1000, 1000, SEA)
    for ring in BASE["rings"]:
        f.raw(f'<polygon points="{pl(ring, win)}" fill="{LAND}" stroke="#c9c6b9" stroke-width="1"/>')
    for line in BASE["regions"]:
        f.raw(f'<polyline points="{pl(line, win)}" fill="none" stroke="{C_REGION}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    for line in BASE["borders"]:
        f.raw(f'<polyline points="{pl(line, win)}" fill="none" stroke="{C_COUNTRY}" stroke-width="2"/>')
    for r in sorted(BASE["rivers"], key=lambda r: -r["s"]):
        f.raw(f'<polyline points="{pl(r["p"], win)}" fill="none" stroke="{C_RIVER}" stroke-width="{RIVER_W(r["s"])}" stroke-linecap="round" stroke-linejoin="round"/>')
    taken = list(keep_clear) + [(20, 778, 262, 158)]   # markers, their names, the legend
    # river names: on the longest stretch inside the map, at the first spot (middle, then either side) that is free
    longest = {}
    for r in BASE["rivers"]:
        if r["n"] in RIVER_LABELS:
            pts = [project(x, y, win) for x, y in r["p"]]
            pts = [q for q in pts if 40 < q[0] < 960 and 40 < q[1] < 960]
            if len(pts) >= 4 and len(pts) > len(longest.get(r["n"], [])):
                longest[r["n"]] = pts
    for name in sorted(longest):
        pts = longest[name]
        w = tw(name, 16) + 8
        for frac in (0.5, 0.35, 0.65, 0.2, 0.8):
            m = int(len(pts) * frac)
            x, y = pts[m]
            box = (x - w / 2 - 6, y - w / 2 - 6, w + 12, w + 12)
            if hit(box, taken):
                continue
            (x0, y0), (x1, y1) = pts[max(m - 2, 0)], pts[min(m + 2, len(pts) - 1)]
            ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
            ang = ang + 180 if ang > 90 else ang - 180 if ang < -90 else ang
            f.raw(f'<text transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})" dy="-9" text-anchor="middle" dominant-baseline="central" font-family="Fira Sans" font-size="16" fill="#4f84a8" stroke="#ffffff" stroke-width="3.5" stroke-linejoin="round" paint-order="stroke">{escape(name)}</text>')
            taken.append(box)
            break
    for lab in BASE["region_labels"]:
        x, y = project(lab["x"], lab["y"], win)
        t = lab["n"].upper()
        w = tw(t, 15) + 3 * len(t)
        r = (x - w / 2, y - 10, w, 20)
        if 30 < x < 970 and 30 < y < 940 and not hit(r, taken):
            f.raw(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" font-family="Fira Sans" font-size="15" letter-spacing="3" fill="{C_PLACE}">{escape(t)}</text>')
            taken.append(r)
    n = 0
    for c in BASE["cities"]:
        x, y = project(c["x"], c["y"], win)
        size = 20 if c["p"] >= 1000000 else 17
        w = tw(c["n"], size, c["p"] >= 1000000)
        r = (x - 6, y - 14, w + 22, 28)
        if 30 < x < 960 - w and 30 < y < 940 and not hit(r, taken) and n < 14:
            f.raw(f'<rect x="{x - 4.5:.1f}" y="{y - 4.5:.1f}" width="9" height="9" fill="#1f1f1d" stroke="#ffffff" stroke-width="1.2"/>')
            f.text(x + 12, y, c["n"], size, c["p"] >= 1000000, "#3a3a37", "start", halo=True)
            taken.append(r)
            n += 1


def map_legend(f):
    f.raw('<rect x="20" y="778" width="262" height="158" rx="6" fill="#ffffff" fill-opacity="0.88"/>')
    y = 800
    for kind, t in (("river", "river"), ("region", "region border (modern)"), ("country", "country border"), ("city", "city > 150,000"), ("kiln", "other kiln site")):
        if kind == "river":
            f.raw(f'<line x1="32" y1="{y}" x2="68" y2="{y}" stroke="{C_RIVER}" stroke-width="3" stroke-linecap="round"/>')
        elif kind == "region":
            f.raw(f'<line x1="32" y1="{y}" x2="68" y2="{y}" stroke="{C_REGION}" stroke-width="1.6" stroke-dasharray="6 4"/>')
        elif kind == "country":
            f.raw(f'<line x1="32" y1="{y}" x2="68" y2="{y}" stroke="{C_COUNTRY}" stroke-width="2"/>')
        elif kind == "city":
            f.raw(f'<rect x="45.5" y="{y - 4.5}" width="9" height="9" fill="#1f1f1d"/>')
        else:
            f.raw(f'<circle cx="50" cy="{y}" r="6" fill="#ffffff" stroke="{MUTED}" stroke-width="1.2"/>')
        f.text(80, y, t, 17, False, DARK, "start")
        y += 28


def centre_fig(name, code, title, subnote, subject_kind):
    c, st, edges = statements(code)
    uncertain = st.n_questionmark > 0
    f = Fig(name, f"{code} {title}")
    ents = []
    for e in edges:
        site = SITE_ALIAS.get(e["entity"], e["entity"])
        k = KILNS[site]
        ents.append((e["entity"], site, k, e))
    lons = [float(k["coordinate1"]) for _, _, k, _ in ents]
    lats = [float(k["coordinate2"]) for _, _, k, _ in ents]
    clon, clat = (min(lons) + max(lons)) / 2, (min(lats) + max(lats)) / 2
    span = max(6.0, 1.9 * max(max(lats) - min(lats), (max(lons) - min(lons)) * math.cos(math.radians(clat))))
    win = (clon, clat, span, 1000 / span)
    # marker positions first, so that city labels can keep clear of them
    placed, labels = [], []   # a marker that would touch an earlier one is pushed away, with a leader line
    for i, (ent, site, k, e) in enumerate(ents, 1):
        tx, ty = project(float(k["coordinate1"]), float(k["coordinate2"]), win)
        x, y = tx, ty
        for px_, py_, _, _ in placed:
            d = math.hypot(x - px_, y - py_)
            if d < 50:
                ang = math.atan2(y - py_, x - px_) if d > 1 else math.pi / 2
                x, y = px_ + 50 * math.cos(ang), py_ + 50 * math.sin(ang)
        placed.append((x, y, tx, ty))
        right = x < 700
        wl = tw(site, 22, True)
        labels.append((x + 28, y - 14, wl, 28) if right else (x - 28 - wl, y - 14, wl, 28))
    keep_clear = [(x - 24, y - 24, 48, 48) for x, y, _, _ in placed] + labels
    f.raw('<defs><clipPath id="m"><rect x="0" y="0" width="1000" height="1000"/></clipPath></defs>')
    f.raw('<g clip-path="url(#m)">')
    draw_base(f, win, keep_clear)
    chosen = {site for _, site, _, _ in ents}
    for site, k in KILNS.items():
        if site in chosen:
            continue
        x, y = project(float(k["coordinate1"]), float(k["coordinate2"]), win)
        if 8 < x < 992 and 8 < y < 992:
            f.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#ffffff" stroke="{MUTED}" stroke-width="1.2"/>')
    for i, ((ent, site, k, e), (x, y, tx, ty)) in enumerate(zip(ents, placed), 1):
        if math.hypot(x - tx, y - ty) > 1:
            f.raw(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#000000" stroke-width="1.4"/>')
            f.raw(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.5" fill="#000000"/>')
        if uncertain:
            f.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="#ffffff" stroke="{REAL[0]}" stroke-width="3" stroke-dasharray="6 4"/>')
            f.text(x, y, str(i), 20, True, REAL[0])
        else:
            f.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{REAL[0]}" stroke="#000000" stroke-width="1"/>')
            f.text(x, y, str(i), 20, True, "#ffffff")
        right = x < 700
        f.text(x + (28 if right else -28), y, site, 22, True, DARK, "start" if right else "end", halo=True)
    f.raw("</g>")
    # scale bar (km), at the latitude of the window centre
    km100 = 100 / 111.32 * win[3] * math.cos(math.radians(clat))
    f.rect(30, 944, km100, 8, "#ffffff", "#000000", 0, 1.2)
    f.text(30 + km100 + 12, 948, "100 km", 17, False, DARK, "start", halo=True)
    map_legend(f)
    f.text(30, 975, "Coast, rivers, regions, places: Natural Earth (modern)  ·  kiln sites: Samian Research (cat29.tblkilnsites)", 15, False, MUTED, "start", halo=True)
    f.raw('<line x1="1000" y1="0" x2="1000" y2="1000" stroke="#000000" stroke-width="1"/>')
    # right panel
    px = 1040
    w = tw(code, 28, True) + 30
    f.rect(px, 46, w, 48, PROP[0], "#000000", 5)
    f.text(px + w / 2, 70, code, 28, True)
    f.text(px + w + 20, 70, title, 30, True, anchor="start", maxw=1710 - px - w - 20)
    f.text(px, 124, f"[{pattern_name(edges)}]  ·  {TYPE_LABEL[edges[0]['type']]}", 22, False, MUTED, "start")
    f.text(px, 152, c["relation"], 19, False, MUTED, "start")
    kind = "Actor  ·  potter" if subject_kind == "actor" else "InformationCarrier"
    sub = f"{kind}" if subject_kind == "actor" else f"{kind}  ·  id {c['carrier_id']}"
    f.box(px, 200, 290, 104, c["pottername"], sub if subject_kind != "actor" else f"{kind}  (e.g. carrier {c['carrier_id']})", INST, 26, 17, 30)
    lines = wrap(f"“{c['source_string']}”", 18, 256)
    eh = 66 + 24 * len(lines)
    f.rect(1430, 200, 280, max(104, eh), OWL[0], OWL[1], 6, 2.4, True)
    f.text(1570, 224, "fw:TextEvidence", 20, True)
    for j, ln in enumerate(lines):
        f.text(1570, 256 + 24 * j, ln, 18, False, DARK)
    f.path("M1330 252 H 1430", dash=True)
    f.text(1380, 232, "derivedFrom", 15, False, MUTED)
    role = "worksAt" if subject_kind == "actor" else "hasProductionCentre"
    n = len(ents)
    rh, rg = 86, 18
    rtop = 380
    rail = px + 145
    last = rtop + (n - 1) * (rh + rg) + rh / 2
    f.path(f"M{rail} 304 V {last}", m=None)
    f.text(rail + 14, 342, role, 21, True, DARK, "start")
    for i, (ent, site, k, e) in enumerate(ents, 1):
        y = rtop + (i - 1) * (rh + rg)
        mid = y + rh / 2
        f.path(f"M{rail} {mid} H 1330")
        f.chip(rail + 92, mid, f"{e['weight']:.2f}", 22, "middle", True)
        f.rect(1330, y, 380, rh, REAL[0], "#000000", 6)
        f.raw(f'<circle cx="1366" cy="{mid}" r="20" fill="#ffffff" stroke="#000000" stroke-width="1"/>')
        f.text(1366, mid, str(i), 20, True, REAL[0])
        f.text(1400, mid - 15, site, 23, True, "#ffffff", "start", maxw=300)
        sub2 = k["wikidataid"] if k["wikidataid"] not in ("", "NULL") else "no Wikidata item"
        if ent != site:
            sub2 = f"“{ent}”  ·  {sub2}"
        f.text(1400, mid + 15, sub2, 17, False, "#ffffff", "start", maxw=300)
    ytop = max(rtop + n * (rh + rg) + 20, 640)
    if st.connective == "and":
        f.text(px, ytop, ("AND: every centre holds, so each keeps the full weight" if not uncertain else "AND: every centre holds; the ? counts as one more possibility"), 20, False, MUTED, "start")
        ytop += 34
    elif st.connective == "or":
        f.text(px, ytop, "OR: one centre or the other, so the weight is shared", 20, False, MUTED, "start")
        ytop += 34
    rule_line(f, st, edges, px, 800 if ytop < 800 else ytop + 10)
    hextuple_chips(f, edges, px, 846, vertical=True)
    f.legend(975, [(INST, "subject"), (REAL, "kiln site"), (OWL, "evidence"), (PROP, "hextuple")], px) if False else None
    for j, ln in enumerate(wrap(subnote, 16, 690)):
        f.text(px, 962 + 22 * j, ln, 16, False, MUTED, "start")
    f.save()
    return f.name


# ---------------------------------------------------------------- the eight figures

def check_cases():
    """Stop if a case no longer says what the figures draw."""
    for code, c in CASES.items():
        ed = wt.edges_for(c["source_string"], c["relation"])
        if not all(e["listed"] for e in ed):
            raise SystemExit(f"{code}: pattern not expected for {c['relation']}")
    want = {"PF.1": ("or", 0.33, 3), "PF.2": ("q", 0.5, 1), "PF.3": ("q+or", 0.33, 2), "PF.4": ("or", 0.5, 2),
            "PC.1": ("or", 0.5, 2), "PC.2": ("and", 1.0, 2), "PC.3": ("q+and", 0.5, 3),
            "PC.4": ("q", 0.5, 1), "IC-PC.1": ("q", 0.5, 1)}
    for code, (pat, w, n) in want.items():
        c = CASES[code]
        ed = wt.edges_for(c["source_string"], c["relation"])
        got = (ed[0]["pattern"], ed[0]["weight"], len(ed))
        if got != (pat, w, n):
            raise SystemExit(f"{code}: expected {(pat, w, n)}, rule gives {got}")


def main():
    check_cases()
    C = CASES
    figs = []
    figs.append((potform_fig("PF.1-multiple-or", "PF.1", "Several forms with OR",
        f"Samian Research, Gaulish tradition: {C['PF.1']['query_rows']} carriers with two or more ORs in the potform; this string on {C['PF.1']['string_rows']}.",
        [("15/17", "15_17"), ("18", "18"), ("18/31", "18_31")]),
        "PF.1", "Several forms with OR", C["PF.1"]))
    figs.append((potform_fig("PF.2-question-mark", "PF.2", "One form with a question mark",
        f"Samian Research, Gaulish tradition: {n_fmt(C['PF.2']['query_rows'])} carriers with a ? in the potform; this string on {C['PF.2']['string_rows']}.",
        [("18/31", "18_31")]),
        "PF.2", "One form with a question mark", C["PF.2"]))
    figs.append((potform_fig("PF.3-or-question-mark", "PF.3", "OR and a question mark",
        f"Samian Research, Gaulish tradition: {C['PF.3']['query_rows']} carriers with OR and ? in the potform. Drawings show the rim variants (R?).",
        [("15/17", "15_17R"), ("18", "18R")]),
        "PF.3", "OR and a question mark", C["PF.3"]))
    figs.append((share_fig("PF.4-frequency-bars", "PF.4", "Observed frequency instead of equal share",
        "Bars as on the Samian Research website (form “31 or 31R”, Dish); counts taken from a screenshot. The frequency method is a proposal, not yet in the FW ontology."),
        "PF.4", "Observed frequency instead of equal share", C["PF.4"]))
    figs.append((centre_fig("PC.1-one-or", "PC.1", "One OR between centres",
        f"Samian Research, Gaulish tradition: {C['PC.1']['query_rows']} carriers with OR in the centre; this string on {C['PC.1']['string_rows']}.", "actor"),
        "PC.1", "One OR between centres", C["PC.1"]))
    figs.append((centre_fig("PC.2-multiple-and", "PC.2", "Several centres with AND",
        f"Samian Research, Gaulish tradition: {n_fmt(C['PC.2']['query_rows'])} carriers with AND and no ?; this string on {C['PC.2']['string_rows']}.", "actor"),
        "PC.2", "Several centres with AND", C["PC.2"]))
    figs.append((centre_fig("PC.3-and-question-mark", "PC.3", "AND and a question mark",
        f"Samian Research, Gaulish tradition: {n_fmt(C['PC.3']['query_rows'])} carriers with AND and ?; this string on {C['PC.3']['string_rows']}.", "actor"),
        "PC.3", "AND and a question mark", C["PC.3"]))
    figs.append((centre_fig("PC.4-question-mark", "PC.4", "One centre with a question mark",
        f"Samian Research, Gaulish tradition: {n_fmt(C['PC.4']['query_rows'])} carriers with only a ? in the centre; this string on {n_fmt(C['PC.4']['string_rows'])}.", "actor"),
        "PC.4", "One centre with a question mark", C["PC.4"]))
    figs.append((centre_fig("IC-PC.1-question-mark", "IC-PC.1", "Carrier to centre with a question mark",
        f"Same query as PC.4 ({n_fmt(C['IC-PC.1']['query_rows'])} carriers); here the statement is asserted on the carrier (model M1, hasProductionCentre).", "carrier"),
        "IC-PC.1", "Carrier to centre with a question mark", C["IC-PC.1"]))
    write_site(figs)
    print(len(figs), "figures ->", IMG)


def write_site(figs):
    rows = []
    for name, code, title, c in figs:
        ed = wt.edges_for(c["source_string"], c["relation"])
        e = ed[0]
        rows.append(f'<figure id="{code}"><img src="img/{name}.png" alt="{escape(code + " " + title)}" width="875">'
                    f'<figcaption><b>{code}</b> {escape(title)}. {escape(c["relation"])}; string <code>{escape(c["source_string"])}</code> '
                    f'({escape(c["pottername"] + ", id " + c["carrier_id"] if c["carrier_id"] else "any carrier")}); weight {e["weight"]:.2f} per statement, fw:{e["type"]}, fw:{e["method"]}. '
                    f'<a href="img/{name}.svg">SVG</a></figcaption></figure>')
    html = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>CHNT2026 vagueness and uncertainty cases</title>'
            '<style>body{font:16px/1.5 "Fira Sans",sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#1f1f1d}'
            'figure{margin:0 0 2rem}img{max-width:100%;border:1px solid #ddd}figcaption{color:#55544f}</style>'
            "<h1>Vagueness and uncertainty cases</h1>"
            "<p>Potform and ProductionCentre, one figure per case. Examples from the Samian Research database.</p>"
            + "".join(rows) + "</html>\n")
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(html, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
