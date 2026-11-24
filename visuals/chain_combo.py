"""Chain C, potform and centres side by side: one figure with the panels A and B.

Panel A is the statement of the carrier about the potform (C.1), panel B the statement of the potter about
its centres on the Roman map (C.2). Both are taken from the figures that visuals/chain_pages.py has just
written (the vessel drawings of C.1, the map of C.2), laid out again closer together and without titles,
formulas and notes. Every string, weight, type and method comes from the data (py/weights.py via
build.statements), not from the page. The two panels carry their own legend; the connectors "or" and "and"
sit on a line between the boxes; the kiln numbers are centred on their ink, not on the advance box.

Written: docs/visuals/img/chain-<L>-potform-centres.svg and .png (needs visuals/fonts/FiraSans-Bold.ttf).
Only built for chain C: the map window and the three form cards are laid out for this chain.
"""
from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET

import resvg_py
from PIL import ImageFont

import build as B

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
BOLD = B.HERE / "fonts/FiraSans-Bold.ttf"

W, H = 2515, 800
XD = 1825                       # left edge of the right-hand column (diagram of panel B)
MAP_X0, MAP_X1, MAP_Y0 = 380, 965, 200      # window of the map of C.2 in its own coordinates (chain C: kilns near 530, 490)
MAP_AT = 1220                   # where the window starts in the figure (flush with the divider)
BOX_H, GAP = 186, 34            # form cards of panel A and the space for the connector between them
BX, SP = 640, 520               # left edge of the form cards; x of the vertical line of the branches

_BOLD_FONT = ImageFont.truetype(str(BOLD), 200, layout_engine=ImageFont.Layout.BASIC)


def q(tag):
    return f"{{{NS}}}{tag}"


def f1(v):
    return f"{v:.1f}"


class Canvas:
    """Small writer for the elements this figure needs; texts are centred with dy (same in every renderer)."""

    def __init__(self, parent):
        self.p = parent

    def sub(self, tag, **a):
        return ET.SubElement(self.p, q(tag), {k.replace("_", "-"): str(v) for k, v in a.items()})

    def text(self, x, y, s, size, fill="#000000", med=False, anchor="middle"):
        a = {"x": f1(x), "y": f1(y), "text-anchor": anchor, "font-family": "Fira Sans", "font-size": size, "dy": "0.35em", "fill": fill}
        if med:
            a["font-weight"] = 500
        t = self.sub("text", **a)
        t.text = s
        return t

    def box(self, x, y, w, h, fill, rx=0, dash=False, stroke="#000000", sw=1):
        a = dict(x=f1(x), y=f1(y), width=f1(w), height=f1(h), rx=rx, fill=fill, stroke=stroke, stroke_width=sw)
        if dash:
            a["stroke_dasharray"] = "7 6"
        return self.sub("rect", **a)

    def path(self, d, dash=False, arrow=False):
        a = dict(d=d, fill="none", stroke=B.LINE, stroke_width=1.6)
        if dash:
            a["stroke_dasharray"] = "7 6"
        if arrow:
            a["marker_end"] = "url(#a)"
        self.sub("path", **a)

    def chip(self, cx, cy, label, size, med=True, w=None):
        w = w or B.tw(label, size, med) + 18
        self.box(cx - w / 2, cy - 16, w, 32, B.PROP[0], 5)
        self.text(cx, cy, label, size, med=med)

    def pill(self, cx, y, label, y0, y1):
        w = B.tw(label, 16, True) + 18
        self.path(f"M{f1(cx)} {f1(y0)} V{f1(y1)}")
        self.box(cx - w / 2, y, w, 22, "#ffffff", 11, stroke=B.LINE)
        self.text(cx, y + 11, label, 16, "#1f1f1d", True)

    def numeral(self, cx, cy, ch, size, fill):
        """Bold digit whose ink, not its advance box, is centred on (cx, cy)."""
        x0, y0, x1, y1 = _BOLD_FONT.getbbox(ch, anchor="ls")
        k = size / 200
        x = cx + (_BOLD_FONT.getlength(ch) / 2 - (x0 + x1) / 2) * k
        y = cy - (y0 + y1) / 2 * k
        t = self.sub("text", x=f"{x:.2f}", y=f"{y:.2f}", text_anchor="middle", font_family="Fira Sans",
                     font_size=size, font_weight=700, fill=fill)
        t.text = ch

    def badge(self, x, y, letter, ring=False):
        r = self.box(x, y, 72, 72, "#000000", 8)
        if ring:
            r.set("stroke", "#ffffff")
            r.set("stroke-width", "3")
        t = self.sub("text", x=f1(x + 36), y=f1(y + 37), text_anchor="middle", font_family="Fira Sans", font_size=46,
                     dy="0.35em", font_weight=500, fill="#ffffff")
        t.text = letter

    def hextuple_chips(self, x, y, e, vertical):
        for t in (f"fw:hasDegreeOfConnection  {e['weight']:.2f}", f"fw:hasType  fw:{e['type']}", f"fw:hasMethod  fw:{e['method']}"):
            w = B.tw(t, 20) + 18
            self.box(x, y - 16, w, 32, B.PROP[0], 5)
            self.text(x + w / 2, y, t, 20)
            if vertical:
                y += 40
            else:
                x += w + 14

    def legend(self, items, x, y, vertical):
        for fill, label in items:
            self.box(x, y - 11, 22, 22, fill, 3)
            self.text(x + 34, y, label, 19, B.MUTED, anchor="start")
            if vertical:
                y += 32
            else:
                x += 34 + B.tw(label, 19) + 36


def drawings(root):
    """The vessel profile groups of the potform figure, top to bottom, each with the top of the card it belongs to."""
    cards = sorted((r for r in root.iter(q("rect")) if r.get("width") == "890"), key=lambda r: float(r.get("y")))
    gs = [g for g in root if g.tag == q("g") and "scale" in g.get("transform", "")]
    assert len(cards) == len(gs) > 0, f"potform figure: {len(cards)} cards, {len(gs)} drawings"
    out = []
    for card, g in zip(cards, gs):
        m = re.match(r"translate\(([\d.]+) ([\d.]+)\) scale\(([\d.]+)\)", g.get("transform"))
        cx = float(card.get("x")) + 230 + (float(card.get("width")) - 230) / 2          # centre of the white part of the card
        out.append((g, float(m[1]) - cx, float(m[2]) - float(card.get("y")), m[3]))
    return out


def build(code, name, potter, carrier_id, pot_src, pot_edges, pot_svg, centre_src, centre_edges, centre_svg):
    """Compose the figure; pot_svg / centre_svg are the paths of the C.1 and C.2 (Roman map) figures."""
    pot, cen = ET.parse(pot_svg).getroot(), ET.parse(centre_svg).getroot()
    root = ET.Element(q("svg"), {"width": str(W), "height": str(H), "viewBox": f"0 0 {W} {H}", "role": "img"})
    ET.SubElement(root, q("title")).text = f"Chain {code}: potform of carrier {carrier_id} (A), centres of {potter} (B)"
    ET.SubElement(root, q("rect"), {"width": str(W), "height": str(H), "fill": "#ffffff"})
    defs = ET.SubElement(root, q("defs"))
    defs.append(copy.deepcopy(next(cen.iter(q("marker")))))                            # arrow marker id="a"
    ET.SubElement(ET.SubElement(defs, q("clipPath"), {"id": "cropmap"}), q("rect"),
                  {"x": str(MAP_X0), "y": str(MAP_Y0), "width": str(MAP_X1 - MAP_X0), "height": str(H)})

    # ------------------------------------------------------------ A: potform
    A = Canvas(ET.SubElement(root, q("g"), {"id": "panel-A"}))
    A.badge(20, 16, "A")
    n = len(pot_edges)
    assert 2 <= n <= 3, "the form cards are laid out for two or three forms"
    top0 = 50 + (3 * BOX_H + 2 * GAP - (n * BOX_H + (n - 1) * GAP)) / 2
    tops = [top0 + i * (BOX_H + GAP) for i in range(n)]
    mids = [t + BOX_H / 2 for t in tops]
    cy = (mids[0] + mids[-1]) / 2
    ep = pot_edges[0]
    A.box(20, cy - 60, 340, 120, B.INST[0], 30)
    A.text(190, cy - 16, potter, 28, med=True)
    A.text(190, cy + 19, f"InformationCarrier  ·  id {carrier_id}", 20)
    A.path(f"M190 {f1(cy + 60)} V{f1(cy + 160)}", dash=True, arrow=True)
    A.chip(190, cy + 110, "fw:derivedFrom", 19, med=False)
    A.box(20, cy + 160, 340, 130, "#ffffff", dash=True)
    A.text(190, cy + 190, "fw:TextEvidence", 23, "#1f1f1d", True)
    A.text(190, cy + 226, f"“{pot_src}”", 22, "#1f1f1d")
    A.text(190, cy + 260, "fw:sourceString", 17, B.MUTED)
    A.path(f"M360 {f1(cy)} H{SP}")
    A.path(f"M{SP} {f1(mids[0])} V{f1(mids[-1])}")
    for (g, dx, dy, sc), e, t, y in zip(drawings(pot), pot_edges, tops, mids):
        A.path(f"M{SP} {f1(y)} H{BX}", arrow=True)
        A.box(BX, t, 560, BOX_H, "#ffffff")
        A.box(BX, t, 230, BOX_H, B.TERM[0])
        A.text(BX + 115, y - 25, e["entity"], 40, "#ffffff", True)
        A.text(BX + 115, y + 25, "Potform", 21, "#ffffff")
        g2 = copy.deepcopy(g)
        g2.set("transform", f"translate({BX + 230 + 165 + dx:.1f} {t + dy:.1f}) scale({sc})")
        A.p.append(g2)
        A.chip((SP + BX) / 2, y, f"{e['weight']:.2f}", 22)
    word = "or" if "or" in ep["pattern"] else "and"
    for t in tops[:-1]:
        A.pill(BX + 115, t + BOX_H + 6, word, t + BOX_H, t + BOX_H + GAP)
    A.chip((360 + SP) / 2, cy, "hasType", 21)
    A.hextuple_chips(20, 716, ep, vertical=False)
    A.legend([(B.INST[0], "InformationCarrier"), (B.TERM[0], "Potform"), ("#ffffff", "evidence"), (B.PROP[0], "hextuple elements")], 20, 772, False)

    # ------------------------------------------------------------ B: map
    kids = list(cen)
    start = next(i for i, e in enumerate(kids) if e.get("clip-path"))
    div = next(i for i, e in enumerate(kids) if e.tag == q("line") and e.get("x1") == "1000" and e.get("y1") == "0")
    Bm = ET.SubElement(root, q("g"), {"id": "panel-B-map", "transform": f"translate({MAP_AT - MAP_X0} {-MAP_Y0})"})
    Bc = ET.SubElement(Bm, q("g"), {"clip-path": "url(#cropmap)"})
    legend_g = ET.Element(q("g"), {"transform": f"translate({MAP_X0 + 12 - 20} 0)"})     # map legend, moved into the window
    low_g = ET.Element(q("g"), {"transform": f"translate({MAP_X0 + 12 - 30} 0)"})        # scale bar and source line
    parent = {c: p for p in cen.iter() for c in p}
    digits, rings = [], []
    for g in kids[start:div]:
        for c in g.iter():
            if c.tag == q("circle") and c.get("stroke-dasharray") and c.get("stroke") == B.REAL[0]:
                rings.append((float(c.get("cx")), float(c.get("cy"))))
            if c.tag == q("text") and (c.text or "").strip().isdigit() and c.get("fill") == B.REAL[0]:
                digits.append(c)
    for c in digits:
        parent[c].remove(c)                                                  # the kiln numbers are redrawn below, centred
    assert len(rings) == len(centre_edges), f"{len(rings)} kiln rings for {len(centre_edges)} centres"
    for e in kids[start:div]:
        t = e.tag
        txt = (e.text or "").strip() if t == q("text") else ""
        y = float(e.get("y") or e.get("y1") or e.get("cy") or 0)
        x = float(e.get("x") or e.get("x1") or e.get("cx") or 0)
        if t == q("text") and x == 80 and 750 <= y <= 930:
            legend_g.append(copy.deepcopy(e)); continue
        if t == q("text") and y > 960:                                       # source line: two lines, it is wider than the window
            parts = txt.split("  ·  ")
            for line, yy in (("  ·  ".join(parts[:2]), 966), ("  ·  ".join(parts[2:]), 986)):
                t2 = copy.deepcopy(e); t2.text = line; t2.set("y", str(yy)); low_g.append(t2)
            continue
        if t == q("text") and txt == "100 km":
            low_g.append(copy.deepcopy(e)); continue
        if t == q("rect") and e.get("height") == "8":
            low_g.append(copy.deepcopy(e)); continue
        if t in (q("rect"), q("line"), q("circle")) and y >= 750 and x < 300:
            legend_g.append(copy.deepcopy(e)); continue
        e2 = copy.deepcopy(e)
        for c in e2.iter(q("text")):
            if c.get("dy") is None and "dominant-baseline" in c.attrib:      # same vertical centring as the rest of the figure
                del c.attrib["dominant-baseline"]
                c.set("dy", "0.35em")
        Bc.append(e2)
    Cm = Canvas(Bc)
    labels = {}
    for c in digits:                                                         # which digit belonged to which ring: the nearest one
        k = min(range(len(rings)), key=lambda i: (rings[i][0] - float(c.get("x"))) ** 2 + (rings[i][1] - float(c.get("y"))) ** 2)
        labels[k] = c.text.strip()
    for k, (cx, cy_) in enumerate(rings):
        Cm.numeral(cx, cy_, labels[k], 26, B.REAL[0])
    Bc.append(legend_g)
    Bc.append(low_g)
    Cb = Canvas(root)
    Cb.badge(MAP_AT + 32, 12, "B", ring=True)

    # ------------------------------------------------------------ B: diagram of the centres
    D = Canvas(ET.SubElement(root, q("g"), {"id": "panel-B-diagram", "transform": f"translate({XD - 1040} -150)"}))
    ec = centre_edges[0]
    D.box(1040, 200, 290, 104, B.INST[0], 30)
    D.text(1185, 237, potter, 26, med=True)
    D.text(1185, 269, f"Actor  ·  potter  (e.g. carrier {carrier_id})", 17)
    D.box(1470, 200, 240, 114, "#ffffff", dash=True)
    D.text(1590, 224, "fw:TextEvidence", 20, "#1f1f1d", True)
    quote = B.wrap(f"“{centre_src}”", 18, 215)
    assert len(quote) == 2, f"evidence text wraps to {len(quote)} lines"
    for line, yy in zip(quote, (256, 280)):
        D.text(1590, yy, line, 18, "#1f1f1d")
    D.path("M1330 252 H1470", dash=True, arrow=True)
    D.chip(1400, 252, "derivedFrom", 15, med=False)
    ys = [423 + 120 * i for i in range(len(centre_edges))]
    D.path(f"M1185 304 V{ys[-1]}")
    D.chip(1185, 363, "worksAt", 21)
    for i, (e, y) in enumerate(zip(centre_edges, ys), 1):
        site = B.SITE_ALIAS.get(e["entity"], e["entity"])
        qid = B.KILNS[site]["wikidataid"]
        D.path(f"M1185 {y} H1330", arrow=True)
        D.chip(1257.5, y, f"{e['weight']:.2f}", 22)
        D.box(1330, y - 43, 380, 86, B.REAL[0])
        D.sub("circle", cx=1366, cy=y, r=16, fill="#ffffff", stroke="#000000", stroke_width=1)
        D.numeral(1366, y, str(i), 24, B.REAL[0])
        D.text(1400, y - 15, e["entity"], 23, "#ffffff", True, "start")
        D.text(1400, y + 15, qid, 17, "#ffffff", anchor="start")
    word = "or" if "or" in ec["pattern"] else "and"
    for y in ys[:-1]:
        D.pill(1520, y + 49, word, y + 43, y + 77)
    Cb.hextuple_chips(XD, 500, ec, vertical=True)
    Cb.legend([(B.INST[0], "Actor"), (B.REAL[0], "ProductionCentre"), ("#ffffff", "evidence"), (B.PROP[0], "hextuple elements")], XD, 668, True)
    for x in (MAP_AT, MAP_AT + (MAP_X1 - MAP_X0)):
        Cb.sub("line", x1=x, y1=0, x2=x, y2=H, stroke="#000000", stroke_width=1)

    ET.indent(root, space=" ")
    svg = B.IMG / f"{name}.svg"
    svg.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8", newline="\n")
    (B.IMG / f"{name}.png").write_bytes(bytes(resvg_py.svg_to_bytes(
        svg_path=str(svg), background="#ffffff", skip_system_fonts=True, font_files=[str(B.R), str(B.M), str(BOLD)], zoom=2.0)))
    return name
