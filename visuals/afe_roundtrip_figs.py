"""Figures of the round trip AFE -> AMT -> AFE in the house style of the case figures (SVG, Fira Sans, resvg PNG).

afe-roundtrip-01-flow   the four cases of AFE values (coins 15661, 16048, 15668, 11471): AFE, AMT, AFE again
afe-roundtrip-02-cases  every coin of the test data and what the way back makes of it (same, top class, different)

The data come from py/step_afe_roundtrip.py (package AFE-AMT-AFE, version 3, 2026-11-03), never from this file.
"""
from __future__ import annotations

from rdflib import BNode, RDF

import build as B
from build import CLS, INST, MUTED, PROP, REAL, Fig, tw
import step_afe_roundtrip as AR
from samian_amt_utils import local

FLOW = [("15661", "Case 1: container with members"), ("16048", "Case 2: one uncertain value"),
        ("15668", "Case 3: certain value"), ("11471", "Case 4: unknown")]
NOTE = {"16048": "fw:UncertainValue comes back as fw:UncertainResourceValue (the values are IRIs)",
        "80001": "the mint is a fw:UncertainValue: same change",
        "90001": "uncertainty as a collection of one member comes back as a plain container: one AMT edge for both",
        "90002": "class without \"Resource\" comes back with it",
        "90003": "kept: the type is on the edge, only fw:Certainty at 1.0 becomes a direct value",
        "90004": "two containers of the same kind become one container with both members"}
VERDICT = {"same": (REAL, "same"), "top class": (PROP, "top class"), "different": (CLS, "different")}


def new(name, title, w=1750, h=1000):
    f = Fig(name, title, w, h)
    f.text(60, 60, title, 34, True, anchor="start")
    return f


def afe_lines(g, coin):
    """The AFE structure of one coin as short lines of text."""
    lines = []
    for prop in AR.PROPS:
        for v in sorted(g.objects(coin, prop), key=str):
            p = "nmo:" + local(prop)
            if not isinstance(v, BNode):
                lines.append(f"{p}  nm:{local(v)}")
                continue
            cls = [local(c) for c in g.objects(v, RDF.type) if c != AR.SKOS.Collection]
            members = sorted(g.objects(v, AR.SKOS.member), key=str)
            head = f"{p}  [ fw:{cls[0] if cls else '?'}" + (" + Collection" if members else "") + " ]"
            lines.append(head)
            if members:
                for m in sorted(members, key=lambda m: str(g.value(m, RDF.value))):
                    lines.append(f"   nm:{local(g.value(m, RDF.value))}   {g.value(m, AR.FW.hasConfidence).toPython()}")
            else:
                lines.append(f"   nm:{local(g.value(v, RDF.value))}   {g.value(v, AR.FW.hasConfidence).toPython()}")
    return lines or ["(no property)"]


def amt_lines(g, coin):
    es = AR.edges(g, coin)
    if not es:
        return ["node without an edge"]
    return [f"{e['property']}  nm:{e['object']}   {e['weight']}   fw:{e['type']}" for e in es] + [f"fw:hasMethod fw:{es[0]['method']}"]


def cell(f, x, y, w, h, lines, fill="#ffffff", size=17):
    f.rect(x, y, w, h, fill, "#d8d6ce", 6)
    for i, t in enumerate(lines):
        f.text(x + 16, y + 30 + 28 * i, t, size, i == 0 and False, "#000000", "start", w - 24)


def flow(r):
    f = new("afe-roundtrip-01-flow", "Round trip AFE → AMT → AFE: the four forms of an AFE value", h=860)
    all_ = r["files"]["all-cases"]
    cols = ((60, 540, "AFE (data of the AFE)"), (680, 480, "AMT (hextuples)"), (1210, 480, "AFE again"))
    for x, w, t in cols:
        f.text(x + w / 2, 112, t, 24, True)
    y = 150
    for coin, title in FLOW:
        uri = next(c for c in AR.coins(all_["afe"]) if AR.short(c) == coin)
        f.text(60, y + 4, f"{title}  ·  coin {coin}", 20, True, B.DARK, "start")
        a, m, b = afe_lines(all_["afe"], uri), amt_lines(all_["amt"], uri), afe_lines(all_["back"], uri)
        h = 28 * max(len(a), len(m), len(b)) + 24
        cell(f, cols[0][0], y + 24, cols[0][1], h, a)
        cell(f, cols[1][0], y + 24, cols[1][1], h, m, "#fffbea")
        cell(f, cols[2][0], y + 24, cols[2][1], h, b)
        for x0, x1 in ((cols[0][0] + cols[0][1], cols[1][0]), (cols[1][0] + cols[1][1], cols[2][0])):
            f.path(f"M{x0 + 6},{y + 24 + h / 2} L{x1 - 6},{y + 24 + h / 2}", sw=2.4)
        y += h + 62
    f.text(60, 835, "Coins 15661, 16048, 15668 and 11471 of the AFE coin data (kept as sent). fw:hasConfidence and amt:weight are the same number here; the way back writes fw:UncertainResourceValue.", 16, False, MUTED, "start")
    f.save()


def summary(g, coin):
    """One line for one coin: property and value, or container class with its members."""
    parts = []
    for prop in AR.PROPS:
        for v in sorted(g.objects(coin, prop), key=str):
            p = local(prop).replace("has", "")
            if not isinstance(v, BNode):
                parts.append(f"{p} {local(v)}")
                continue
            cls = [local(c) for c in g.objects(v, RDF.type) if c != AR.SKOS.Collection][0].replace("ResourceValue", "").replace("Value", "")
            members = sorted(g.objects(v, AR.SKOS.member), key=lambda m: str(g.value(m, RDF.value))) or [v]
            parts.append(f"{p} {cls}: " + ", ".join(f"{local(g.value(m, RDF.value))} {g.value(m, AR.FW.hasConfidence).toPython()}" for m in members))
    return "  ·  ".join(parts) or "(no property)"


def fit(t, size, maxw):
    while tw(t, size) > maxw and len(t) > 4:
        t = t[:-2].rstrip() + "…"
    return t


def cases(r):
    rows = []
    for name, label in (("all-cases", "AFE"), ("denomination-mint", "constructed"), ("edge-cases", "edge case")):
        fi = r["files"][name]
        for coin in AR.coins(fi["afe"]):
            rows.append((label, fi, coin))
    f = new("afe-roundtrip-02-cases", "What the way back makes of each coin", h=200 + 116 * len(rows))
    for x, t in ((60, "Coin"), (210, "AFE input"), (790, "After the round trip"), (1370, "Result")):
        f.text(x, 112, t, 21, True, MUTED, "start")
    y = 140
    for label, fi, coin in rows:
        s = AR.short(coin)
        f.rect(50, y, 1650, 104, "#ffffff", "#d8d6ce", 6)
        f.text(60, y + 28, s, 22, True, "#000000", "start")
        f.text(60, y + 62, label, 15, False, MUTED, "start")
        for x, g in ((210, fi["afe"]), (790, fi["back"])):
            for i, ln in enumerate(B.wrap(summary(g, coin), 16, 540)[:3]):
                f.text(x, y + 28 + 22 * i, ln, 16, False, "#000000", "start")
        st, text = VERDICT[fi["verdicts"][s]]
        f.rect(1370, y + 12, 130, 34, st[0], "#000000", 4)
        f.text(1435, y + 29, text, 18, True, st[2])
        if s in NOTE:
            f.text(210, y + 90, NOTE[s], 15, False, MUTED, "start", 1300)
        y += 116
    f.legend(y + 20, [(REAL, "same"), (PROP, "same on the top class (…Value = …ResourceValue)"), (CLS, "different: not loss-free")])
    f.save()


def main():
    r = AR.run()
    flow(r)
    cases(r)
    print("2 AFE round-trip figures ->", B.IMG)
    return r


if __name__ == "__main__":
    main()
