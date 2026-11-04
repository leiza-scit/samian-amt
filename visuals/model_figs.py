"""Model figures in the house style of the case figures (SVG, Fira Sans, resvg PNG).

The same five figures as docs/diagrams (01 simple, 02 full semantics, 03 toy reasoning, 04 both
directions, 05 three chains), redrawn with the visuals kit and published on docs/visuals/model.html.
Names, domains, ranges, axioms and weights are read from the ontology and the reasoner, as in
py/step_diagrams.py; only the positions are fixed here.
"""
from __future__ import annotations

from html import escape

import build as B
from build import CLS, INST, LINE, MUTED, PROP, Fig, tw
from mini_amt_utils import ONTOLOGY, TOY, load_graph, read_edges, read_model  # noqa: E402
from reference_reasoner import reason  # noqa: E402
from step_chains import comparison, run as run_chains  # noqa: E402

RED = "#dc2626"
CHAIN = ["Potform", "InformationCarrier", "ProductionCentre", "Actor"]
MARKER_RED = (f'<defs><marker id="r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
              f'orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="{RED}" stroke-width="1.8" '
              f'stroke-linecap="round" stroke-linejoin="round"/></marker></defs>')


def new(name, title, w=1750, h=1000):
    f = Fig(name, title, w, h)
    f.raw(MARKER_RED)
    f.text(60, 60, title, 34, True, anchor="start")
    return f


def line(f, p, q, red=False, dash=False):
    f.path(f"M{p[0]:.1f},{p[1]:.1f} L{q[0]:.1f},{q[1]:.1f}", dash, "r" if red else "a",
           RED if red else LINE, 2.4 if red else 1.6)


def qpoint(p, c, q, t):
    return tuple((1 - t) ** 2 * a + 2 * t * (1 - t) * b + t * t * d for a, b, d in zip(p, c, q))


def arc(f, p, q, rise, label, t=0.5, dash=False, size=17):
    """Quadratic arc from p to q bulging by `rise` (negative: up); red, with a white label box."""
    c = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 2 * rise)
    f.path(f"M{p[0]:.1f},{p[1]:.1f} Q{c[0]:.1f},{c[1]:.1f} {q[0]:.1f},{q[1]:.1f}", dash, "r", RED, 2.6)
    x, y = qpoint(p, c, q, t)
    tag(f, x, y, label, size)


def tag(f, x, y, lines, size=17):
    lines = lines.split("\n") if isinstance(lines, str) else lines
    w = max(tw(t, size, i == 0) for i, t in enumerate(lines)) + 22
    h = len(lines) * size * 1.3 + 10
    f.rect(x - w / 2, y - h / 2, w, h, "#ffffff", RED, 5, 1.4)
    for i, t in enumerate(lines):
        f.text(x, y - h / 2 + 5 + size * 1.3 * (i + .5), t, size, i == 0, RED if i == 0 else "#7f1d1d")


def key(f, y, items, x=60):
    """Legend: (kind, text) with kind 'solid', 'dashed', 'red', 'reddashed' or a fill colour tuple."""
    for kind, text in items:
        if isinstance(kind, tuple):
            f.rect(x, y - 11, 34, 22, kind[0], "#000000", 4)
            w = 44
        else:
            red = kind.startswith("red")
            line(f, (x, y), (x + 56, y), red, kind.endswith("dashed"))
            w = 66
        f.text(x + w, y, text, 19, color=MUTED, anchor="start")
        x += w + tw(text, 19) + 40


# ------------------------------------------------ 01 / 03 / 04: the chain

def chain_fig(model, name, title, legend, instances=None, weights=None, inverse_arcs=False, note=None):
    h = 1000 if inverse_arcs else 800
    f = new(name, title, 1750, h)
    BW, BH, yc = 230, 130, 470
    cx = {c: 70 + i * 460 + BW / 2 for i, c in enumerate(CHAIN)}
    top, bottom = yc - BH / 2, yc + BH / 2
    for c in CHAIN:
        if instances:
            lab, sub = instances[c]
            f.box(cx[c] - BW / 2, top, BW, BH, lab, sub, INST, rx=BH / 2)
        else:
            f.box(cx[c] - BW / 2, top, BW, BH, c, None, CLS, ts=23, rx=16)

    def wl(role, concept):
        return f"{role}  {weights[(role, concept)]:.2f}" if weights else role

    derived = {cons for _, _, cons, _ in model["chains"]}
    for _, ante, inv in model["inverses"]:
        if ante in derived or ante == "reaches":
            continue
        d, r = model["roles"][ante]["domain"], model["roles"][ante]["range"]
        right = CHAIN.index(d) < CHAIN.index(r)
        sx = lambda c, facing: cx[c] + (BW / 2 + 6 if facing else -BW / 2 - 6)
        a, b = sx(d, right), sx(r, not right)
        line(f, (a, yc - 35), (b, yc - 35))
        f.chip((a + b) / 2, yc - 35, wl(ante, d), 18)
        line(f, (b, yc + 35), (a, yc + 35), dash=True)
        f.chip((a + b) / 2, yc + 35, wl(inv, r), 18, med=False)

    inverse_of = {ante: inv for _, ante, inv in model["inverses"]}
    for _, ante, cons, _ in model["chains"]:
        d, r = model["roles"][cons]["domain"], model["roles"][cons]["range"]
        i, j = CHAIN.index(d), CHAIN.index(r)
        outer = j - i >= 3
        so, eo = (-40, 40) if outer else (40, -40)
        rise = 260 if outer else 150
        arc(f, (cx[d] + so, top - 6), (cx[r] + eo, top - 6), -rise,
            [">> " + wl(cons, d), " o ".join(ante)])
        if inverse_arcs:
            inv = inverse_of[cons]
            arc(f, (cx[r] + eo, bottom + 6), (cx[d] + so, bottom + 6), rise,
                ["<< " + inv, "inverse of " + cons], dash=True)
    key(f, h - 70, legend)
    if note:
        f.text(60, h - 30, note, 17, color=MUTED, anchor="start")
    f.save()


# ------------------------------------------------ 02: full semantics

def semantics_fig(model):
    W2, H2 = 2200, 1180
    f = new("model-02-full-semantics", "Mini-AMT: full semantics (AMT vocabulary)", W2, H2)
    roles = model["roles"]
    inv_roles = {inv for _, _, inv in model["inverses"]}
    chain_roles = {r for _, ante, _, _ in model["chains"] for r in ante}
    longest = max(model["chains"], key=lambda c: len(c[1]))
    row_y = dict(zip(longest[1], (330, 600, 870)))
    others = [c for c in model["chains"] if c is not longest]
    top = next(c for c in others if c[1][0] == longest[1][0])
    bottom = next(c for c in others if c is not top)
    der_row = {longest[2]: 600, top[2]: 330, bottom[2]: 870}
    col = {"back": 215, "fwd": 655, "rca": 1095, "der": 1535, "sup": 1975}
    heads = {"back": "roles against the chain|(direction of the source data)",
             "fwd": "roles along the chain|Potform > Carrier > Centre > Actor",
             "rca": "RoleChainAxiom|(ordered antecedents)",
             "der": "derived roles (>>)|and their inverses (<<)", "sup": "generic super-role|"}
    for k, t in heads.items():
        a, b = t.split("|")
        f.text(col[k], 150, a, 22, True, "#334155")
        f.text(col[k], 180, b, 19, False, "#334155")

    pills = {}

    def pill(role, x, y, dashed=False, derived=False, h=100):
        r = roles[role]
        sub = f"{r['domain']} -> {r['range']}" if r["domain"] else "no domain / range"
        f.rect(x - 145, y - h / 2, 290, h, PROP[0], RED if derived else "#000000", h / 2, 3 if derived else 1.6, dashed)
        f.text(x, y - 14, role, 22, True, maxw=250)
        f.text(x, y + 20, sub, 15, maxw=278)
        pills[role] = {"cx": x, "cy": y, "l": (x - 145, y), "r": (x + 145, y), "t": (x, y - h / 2), "b": (x, y + h / 2)}

    def link(p, q, label=None, t=0.5, size=15, med=False, dash=False):
        line(f, p, q, dash=dash)
        if label:
            f.text(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, label, size, med, halo=True)

    base = [(a, b, c) for a, b, c in model["inverses"] if b in row_y or c in row_y]
    for _, ante, inv in base:
        fwd, back = (ante, inv) if ante in chain_roles else (inv, ante)
        y = row_y[fwd]
        pill(back, col["back"], y, back in inv_roles)
        pill(fwd, col["fwd"], y, fwd in inv_roles)
        if ante == back:
            link((pills[ante]["r"][0] + 6, y), (pills[inv]["l"][0] - 6, y), "InverseAxiom")
        else:
            link((pills[ante]["l"][0] - 6, y), (pills[inv]["r"][0] + 6, y), "InverseAxiom")

    for _, ante, cons, logic in model["chains"]:
        y = der_row[cons]
        f.rect(col["rca"] - 175, y - 60, 350, 120, "#ffffff", "#000000", 16, 1.6)
        f.text(col["rca"], y - 28, "RoleChainAxiom", 20, True)
        f.text(col["rca"], y + 4, " o ".join(ante), 15, maxw=330)
        f.text(col["rca"], y + 34, f"logic: {logic} (proposal)", 15, color=MUTED)
        for i, role in enumerate(ante):
            dy = (i - (len(ante) - 1) / 2) * 34
            link((pills[role]["r"][0] + 6, pills[role]["cy"]), (col["rca"] - 181, y + dy), str(i + 1), 0.22, 22, True)
        pill(cons, col["der"], y, derived=True)
        link((col["rca"] + 181, y), (pills[cons]["l"][0] - 6, y), "consequent")

    pill("reaches", col["sup"], 600, derived=True)
    for _, sub, sup in model["subs"]:
        spread = (pills[sub]["cy"] - 600) / 4 * 0.5
        link((pills[sub]["r"][0] + 6, pills[sub]["cy"]), (pills[sup]["l"][0] - 6, pills[sup]["cy"] + spread),
             "SubsumptionAxiom", 0.45)

    for _, ante, inv in model["inverses"]:
        if ante in pills and ante not in row_y and inv not in pills:
            pill(inv, pills[ante]["cx"], pills[ante]["cy"] + 140, True, True, 90)
            link((pills[ante]["cx"], pills[ante]["b"][1] + 4), (pills[inv]["cx"], pills[inv]["t"][1] - 4), None, dash=True)
            f.text(pills[ante]["cx"] + 12, pills[ante]["b"][1] + 25, "InverseAxiom", 14, anchor="start")

    y = H2 - 95
    x = 60
    for text, dashed, red, fill in [("asserted role", False, False, PROP[0]), ("inverse role (InverseAxiom)", True, False, PROP[0]),
                                    ("derived role (red = reasoning)", False, True, PROP[0]), ("axiom", False, False, "#ffffff")]:
        f.rect(x, y - 16, 56, 32, fill, RED if red else "#000000", 16, 3 if red else 1.6, dashed)
        f.text(x + 70, y, text, 19, color=MUTED, anchor="start")
        x += 70 + tw(text, 19) + 50
    f.text(60, H2 - 45, "Roles show domain -> range. The logic operator of the role chains is a proposal (product, as in the source paper).",
           17, color=MUTED, anchor="start")
    f.save()


# ------------------------------------------------ 05: three chains

TYPE_TAG = {"Certainty": "C", "Uncertainty": "U", "Vagueness": "V", "FuzzinessWobbliness": "FW", None: ""}
COLX = {"pf": 230, "ic": 680, "pc": 1130, "ae": 1560}
PITCH = 130


def fmt(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def chains_fig(res):
    comp = comparison(res)
    edges, nodes, rows = res["edges"], res["nodes"], res["rows"]
    panels = {}
    for r in rows:
        panels.setdefault(r["chain"], []).append(r)
    layout = []
    for chain, rs in sorted(panels.items()):
        ics = sorted("ic_" + r["carrier_id"] for r in rs)
        ae = "ae_" + next(e["from"] for e in edges if e["role"] == "worksAt" and e["from"].startswith("ae_")
                          and nodes[e["from"]][1] == rs[0]["potter"])[3:]
        pfs = list(dict.fromkeys(e["to"] for ic in ics for e in edges if e["role"] == "hasType" and e["from"] == ic))
        pcs = list(dict.fromkeys(e["to"] for e in edges if e["role"] == "hasProductionCentre" and e["from"] in ics))
        n = max(len(pfs), len(ics), len(pcs))
        layout.append((chain, rs, ics, ae, pfs, pcs, n, (n - 1) * PITCH + 390))
    H = sum(p[-1] for p in layout) + 270
    f = new("model-05-chains", "Three chains from the CHNT data: hextuples and derived degrees", 1750, H)
    y0 = 100
    for chain, rs, ics, ae, pfs, pcs, n, h in layout:
        mid = y0 + 215 + (n - 1) * PITCH / 2
        pos = {}
        for colname, items in (("pf", pfs), ("ic", ics), ("pc", pcs), ("ae", [ae])):
            for i, k in enumerate(items):
                pos[k] = (COLX[colname], mid - ((len(items) - 1) / 2 - i) * PITCH)
        f.text(60, y0 + 18, f"Chain {chain}: {rs[0]['potter']}", 25, True, anchor="start")
        BW, BH = 290, 76
        for k, (x, y) in pos.items():
            f.box(x - BW / 2, y - BH / 2, BW, BH, nodes[k][1], None, INST, ts=21, rx=BH / 2)

        def side(k, s):
            x, y = pos[k]
            return (x + (BW / 2 + 6) * s, y)

        def tg(e):
            return f"{e['weight']:g} {TYPE_TAG[e['type']]}".strip()

        for e in edges:
            if e["from"] not in pos or e["to"] not in pos:
                continue
            role = e["role"]
            if role == "hasType":
                p, q, t = side(e["from"], -1), side(e["to"], 1), 0.5
            elif role == "hasProductionCentre":
                p, q, t = side(e["from"], 1), side(e["to"], -1), 0.32
            elif role == "worksAt":
                p, q, t = side(e["from"], -1), side(e["to"], 1), 0.5
            else:
                continue
            line(f, p, q)
            f.chip(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, tg(e), 17)
        c1 = next(c for c in comp if c["relation"] == "potformToActor" and c["from"] == pfs[0] and c["to"] == ae)
        c2 = next(c for c in comp if c["relation"] == "potformToCentre" and c["from"] == pfs[-1] and c["to"] == pcs[-1])
        a, b = pos[pfs[0]], pos[ae]
        arc(f, (a[0], a[1] - BH / 2 - 6), (b[0], b[1] - BH / 2 - 6), -100,
            f"Potform>>Actor   M1 {fmt(c1['m1_product'])}  |  M2 {fmt(c1['m2_product'])}", 0.5)
        a, b = pos[pfs[-1]], pos[pcs[-1]]
        arc(f, (a[0], a[1] + BH / 2 + 6), (b[0], b[1] + BH / 2 + 6), 100,
            f"Potform>>Centre   {fmt(c2['m1_product'])}", 0.5, dash=True)
        y0 += h
    key(f, H - 95, [("solid", "asserted, weight + type"), ("red", "derived (product logic)"),
                    ("reddashed", "derived Potform>>Centre")])
    f.text(60, H - 50, "Type: C certainty, U uncertainty (?), V vagueness (AND / OR), FW fuzziness-wobbliness (? with AND / OR). "
           "M1: carrier-centre asserted; M2: derived from the actor.", 16, color=MUTED, anchor="start")
    f.save()


# ------------------------------------------------ main

FIGS = [
    ("model-01-simple", "Simple view", "Classes, asserted properties with their inverses, and the three derived properties (red).", "01_simple_model"),
    ("model-02-full-semantics", "Full semantics", "Roles with domain and range, InverseAxiom, RoleChainAxiom with ordered antecedents, SubsumptionAxiom.", "02_full_semantics"),
    ("model-03-toy-reasoning", "Toy reasoning", "The same picture on the abstract toy chain, with toy weights and product logic.", "03_toy_reasoning"),
    ("model-04-both-directions", "Both directions", "Every derived property (>>) with its inverse (<<) below.", "04_reasoning_both"),
    ("model-05-chains", "Three chains", "Three real chains from the CHNT data: hextuples with weight and FW type, derived degrees for M1 and M2.", "05_chains"),
]


def main():
    g = load_graph(ONTOLOGY, TOY)
    model = read_model(g)
    for n in CHAIN:
        model["concepts"][n]

    chain_fig(model, "model-01-simple", "Mini-AMT: classes, properties, reasoning",
              [("solid", "asserted property"), ("dashed", "inverse (InverseAxiom)"), ("red", "derived by role chain (>>)"), (CLS, "class (Concept)")])
    semantics_fig(model)
    state = reason(model, read_edges(g))
    names = ("Potform", "Carrier", "Centre", "Actor")
    instances = {c: (f"{n} 1", c) for c, n in zip(CHAIN, names)}
    holder = {c: f"{n}_1" for c, n in zip(CHAIN, names)}
    weights = {(role, next(c for c, n in holder.items() if n == a)): e["weight"] for (role, a, b), e in state.items()}
    chain_fig(model, "model-03-toy-reasoning", "Toy chain: what the reasoning derives (toy weights, product logic)",
              [("solid", "asserted, with weight"), ("dashed", "inverse, same weight"), ("red", "derived, weight by logic"), (INST, "individual")],
              instances=instances, weights=weights)
    chain_fig(model, "model-04-both-directions", "Derived properties in both directions: >> and <<",
              [("solid", "asserted property"), ("dashed", "inverse of an asserted property"), ("red", "derived, forward (>>)"), ("reddashed", "derived, inverse (<<)")],
              inverse_arcs=True)
    chains_fig(run_chains())

    rows = [f'<figure id="{n}"><img src="img/{n}.png" alt="{escape(t)}" width="875"><figcaption><b>{escape(t)}.</b> {escape(c)} '
            f'<a href="img/{n}.svg">SVG</a> · <a href="../diagrams/{d}.svg">docs version (matplotlib)</a></figcaption></figure>'
            for n, t, c, d in FIGS]
    B.page("model.html", "Model figures",
           "The Mini-AMT model in the style of the case figures. The figures in the documentation pages (<a href=\"../model.html\">Model</a>, "
           "<a href=\"../reasoning.html\">Reasoning</a>, <a href=\"../chains.html\">Chains</a>) are the matplotlib versions and are developed there; "
           "this page shows the same content for presentations and papers.", rows)
    print(len(FIGS), "model figures ->", B.IMG)
