"""Round-trip figures in the house style of the case figures (SVG, Fira Sans, resvg PNG).

roundtrip-01-flow      Chain C (carrier 211974, Ve- i) as hextuples, as AFE pattern, and as hextuples again
roundtrip-02-patterns  the six patterns of the weight rule and the AFE form each one takes
roundtrip-03-balance   what comes back unchanged, what changes, what the AFE pattern does not carry

Weights, types, counts and the labels come from py/step_roundtrip.py and py/weights.py, never from this file;
only positions and wording of the captions are fixed here.
"""
from __future__ import annotations

import build as B
from build import CLS, INST, LINE, MUTED, PROP, REAL, Fig, tw
import step_roundtrip as RT
import weights as W

CARRIER = "ic_211974"
SHORT = {"VagueResourceValue": "fw:VagueResourceValue", "UncertainResourceValue": "fw:UncertainResourceValue",
         "FuzzinessWobblinessResourceValue": "fw:FuzzinessWobblinessResourceValue"}


def new(name, title, w=1750, h=1000):
    f = Fig(name, title, w, h)
    f.text(60, 60, title, 34, True, anchor="start")
    return f


def fmt(w):
    return f"{w:g}" if w == int(w) else f"{w:.2f}".rstrip("0")


def carrier_statements(r):
    """The statements of Chain C's carrier: [(predicate, target label, weight, type, method)], sorted."""
    nodes = r["res"]["nodes"]
    out = []
    for e in r["res"]["edges"]:
        if e["from"] == CARRIER:
            out.append((e["role"], nodes[e["to"]][1].replace("Potform ", ""), e["weight"], e["type"], e["method"]))
    return sorted(out, key=lambda x: (x[0] != "hasType", x[1]))


def column(f, x, w, title, sub):
    f.rect(x, 110, w, 840, "#faf9f5", "#d8d6ce", 8)
    f.text(x + w / 2, 142, title, 26, True)
    f.text(x + w / 2, 174, sub, 19, False, MUTED)


def flow(r):
    f = new("roundtrip-01-flow", "Round trip AMT → AFE → AMT: Chain C (carrier 211974, Ve- i)")
    stm = carrier_statements(r)
    pot = [s for s in stm if s[0] == "hasType"]
    cen = [s for s in stm if s[0] == "hasProductionCentre"]
    cx = (60, 640, 1230)
    cw = 470
    column(f, cx[0], cw, "AMT", "hextuples, as in dist/chains.ttl")
    column(f, cx[1], 520, "AFE pattern", "containers, as in the AFE coin data")
    column(f, cx[2], cw, "AMT again", "hextuples, read back from the AFE pattern")

    # left and right: the statements as rows
    def rows(x, method):
        y = 210
        f.box(x + 20, y, 200, 56, "Carrier 211974", st=INST)
        y += 90
        for role, label, w, t, m in stm:
            f.box(x + 20, y, 250, 64, label, f"sam:{role}", st=INST, ts=21, ss=17)
            f.path(f"M{x + 270},{y + 32} L{x + 290},{y + 32}", m=None)
            f.chip(x + 300, y + 32, f"{fmt(w)}", 19, "start", True)
            f.text(x + 300, y + 62, f"fw:{t}", 15, False, MUTED, "start")
            y += 98
        f.text(x + 20, y + 14, f"fw:hasMethod fw:{method}", 19, False, MUTED, "start")
        if method != W.FW_METHOD:
            f.text(x + 20, y + 44, "(was fw:EqualShareRule; the AFE pattern has no place for it)", 16, False, MUTED, "start")
        else:
            f.text(x + 20, y + 44, "fw:derivedFrom → fw:TextEvidence (the source strings)", 16, False, MUTED, "start")
    rows(cx[0], W.FW_METHOD)
    rows(cx[2], "AFEAssignment")

    # middle: the AFE pattern
    x0 = cx[1] + 20
    f.box(x0, 210, 120, 56, "Carrier 211974", st=INST, ts=15)
    # potform: one collection, n members
    f.box(x0 + 160, 210, 340, 56, "fw:VagueResourceValue", "+ skos:Collection", st=CLS, ts=17, ss=15)
    f.path(f"M{x0 + 120},238 L{x0 + 160},238")
    for i, (_, label, w, t, m) in enumerate(pot):
        bx = x0 + 160 + 70 * i
        f.box(bx, 300, 64, 70, label, f"{fmt(w)}", st=INST, ts=17, ss=15)
        f.path(f"M{x0 + 330},266 L{bx + 32},300", m="a")
    f.text(x0 + 160, 394, "rdf:value, fw:hasConfidence", 15, False, MUTED, "start")
    # centres: one container per entity
    y = 450
    for _, label, w, t, m in cen:
        f.box(x0 + 160, y, 340, 56, SHORT[RT.AFE_CLASS[t]], "+ skos:Collection", st=CLS, ts=16, ss=15)
        f.path(f"M{x0 + 60},266 Q{x0 + 60},{y + 28} {x0 + 160},{y + 28}", m="a")
        f.box(x0 + 160, y + 80, 150, 64, label, f"{fmt(w)}", st=INST, ts=16, ss=15)
        f.path(f"M{x0 + 235},{y + 56} L{x0 + 235},{y + 80}")
        y += 190
    f.chip(x0 + 8, 425, "sam:hasProductionCentre", 15, "start")
    f.chip(x0 + 8, 330, "sam:hasType", 15, "start")
    f.text(x0, y + 4, "AND: one container per entity,", 16, False, MUTED, "start")
    f.text(x0, y + 26, "OR: one container, one member per entity", 16, False, MUTED, "start")

    # arrows between the columns, with the queries
    for a, b, q in ((cx[0] + cw, cx[1], "queries/amt-to-afe.rq"), (cx[1] + 520, cx[2], "queries/afe-to-amt.rq")):
        f.path(f"M{a + 6},560 L{b - 6},560", sw=3)
        f.text((a + b) / 2, 520, "SPARQL", 15, False, MUTED)
        f.text((a + b) / 2, 540, "CONSTRUCT", 15, False, MUTED)
    f.legend(978, [(INST, "individual"), (CLS, "AFE container class")])
    f.save()


PATTERN_EXAMPLES = [("certain", "Rheinzabern"), ("q", "Rheinzabern?"), ("or", "Pfaffenhofen or Westerndorf"),
                    ("and", "Kräherwald and Rheinzabern"), ("q+or", "A or B or C?"), ("q+and", "Kräherwald and Rheinzabern?")]


def afe_form(pattern, n, w):
    """(box title, sub line) for the AFE form of a pattern, from the same rule the query reads."""
    cls = RT.AFE_CLASS
    t = W.FW_TYPE[pattern]
    if pattern == "certain":
        return "value directly", "?s ?p ?o  (no container)"
    if pattern == "q":
        return "fw:UncertainResourceValue", "rdf:value ?o ; fw:hasConfidence " + fmt(w)
    kind = "one collection, " + str(n) + " members" if pattern.endswith("or") else str(n) + " containers, one member each"
    return "fw:" + cls[t], kind + " ; fw:hasConfidence " + fmt(w)


def patterns(r):
    f = new("roundtrip-02-patterns", "The six patterns of the weight rule and the AFE form each takes")
    head = ((60, 330, "Pattern and source string"), (410, 400, "AMT: per entity"), (830, 860, "AFE pattern"))
    for x, w, t in head:
        f.text(x, 112, t, 21, True, MUTED, "start")
    y = 150
    for pattern, text in PATTERN_EXAMPLES:
        st = W.parse(text)
        e = W.edges_for(text, "actor--productioncentre")[0]
        n = len(st.entities)
        f.rect(50, y - 8, 1650, 126, "#ffffff", "#d8d6ce", 8)
        f.box(60, y, 330, 110, text, f"pattern  {pattern}", st=INST, ts=22, ss=18)
        f.text(410, y + 22, f"{n} × fw:hasDegreeOfConnection  {fmt(e['weight'])}", 21, False, "#000000", "start")
        f.chip(410, y + 62, f"fw:{e['type']}", 19, "start")
        if n > 1:
            f.text(410, y + 98, "AND: weight " + ("1" if pattern == "and" else "0.5") if pattern.endswith("and")
                   else "OR: weight = share", 17, False, MUTED, "start")
        title, sub = afe_form(pattern, n, e["weight"])
        f.box(830, y, 380, 110, title, None, st=CLS if pattern != "certain" else INST, ts=19, rx=6)
        f.text(1230, y + 34, sub, 17, False, "#000000", "start")
        f.text(1230, y + 78, back_rule(pattern), 17, False, MUTED, "start")
        y += 138
    f.text(60, 985, "Back: the form and the weight decide the pattern; the source string is not needed (weights.py, self-test: no two patterns share weight and type).", 17, False, MUTED, "start")
    f.save()


def back_rule(pattern):
    return {"certain": "back: Certainty, weight 1.0",
            "q": "back: Uncertainty, weight = hasConfidence",
            "or": "back: Vagueness, weight < 1",
            "and": "back: Vagueness, weight = 1",
            "q+or": "back: FuzzinessWobbliness, weight < 0.5",
            "q+and": "back: FuzzinessWobbliness, weight = 0.5"}[pattern]


def balance(r):
    f = new("roundtrip-03-balance", "What the round trip keeps, changes and drops")
    c, p, lost = r["chains"], r["patterns"], r["lost"]
    cols = (
        ("Comes back unchanged", REAL, [
            ("Subject, predicate, object", f"{c['statements']} hextuples of the chains, {p['statements']} of the pattern cases"),
            ("Degree of connection", "fw:hasDegreeOfConnection, two decimals"),
            ("FW type", "Certainty, Uncertainty, Vagueness, FuzzinessWobbliness"),
            ("Nodes", f"{c['nodes']} nodes: concept and label"),
            ("Reasoning result", f"{r['reasoned_edges']} edges in the three runs: weight, type, method of derived edges")]),
        ("Changes", PROP, [
            ("fw:hasMethod", f"fw:EqualShareRule becomes fw:AFEAssignment on all {c['statements']} statements"),
            ("Statement nodes", "new blank nodes; the statements stay the same"),
            ("AND and OR", "no longer a string: read from the form and from weight and type")]),
        ("Not carried by the AFE pattern", CLS, [
            ("Source strings", f"{lost['evidence']} fw:TextEvidence nodes (fw:sourceString, fw:derivedFrom)"),
            ("Frequency shares", f"{lost['frequency']} statements with sam:frequencyShare and its sources"),
            ("sam:attributedTo", f"{lost['attributed']} links, used only by model M2"),
            ("Order and spelling", "of the entities in a string (already lost in step weights)")]))
    x = 60
    for title, st, items in cols:
        f.rect(x, 110, 510, 830, "#faf9f5", "#d8d6ce", 8)
        f.box(x + 20, 130, 470, 60, title, st=st, ts=24)
        y = 220
        for head, body in items:
            f.rect(x + 20, y, 470, 120, "#ffffff", "#d8d6ce", 6)
            f.text(x + 36, y + 28, head, 21, True, "#000000", "start", 460)
            lines = B.wrap(body, 18, 438)
            for i, ln in enumerate(lines[:3]):
                f.text(x + 36, y + 62 + 24 * i, ln, 18, False, MUTED, "start")
            y += 136
        x += 560
    f.save()


def main():
    r = RT.run()
    flow(r)
    patterns(r)
    balance(r)
    print("3 round-trip figures ->", B.IMG)
    return r


if __name__ == "__main__":
    main()
