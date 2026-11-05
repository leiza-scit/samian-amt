"""Step "mini-roundtrip": the same four kinds of statement on two sides, round trip AMT <-> AFE pattern on both.

Samian side  InformationCarrier -> Potform   (cases PF.1, PF.2, PF.3 of the visuals, plus one certain case)
AFE side     coin -> authority               (nmo:hasAuthority; four coins of the AFE data, data/afe/afe-mini-coins.ttl)

The four cases are: 1 certain, 2 uncertain, 3 vague, 4 vague and uncertain. A statement needs only five parts here:
subject, property, object, weight (fw:hasDegreeOfConnection or amt:weight) and type (fw:hasType). No method, no evidence.

Reads   data/afe/afe-mini-coins.ttl            the four coins (AFE container pattern)
        data/afe/amt-parallel-statements.ttl   two parallel statements on one coin property (needs the AMT engine 0.7.0)
        queries/amt-to-afe.rq, queries/afe-to-amt.rq              Samian side
        queries/coins/afe-to-amt.rq, queries/coins/amt-to-afe.rq  AFE side
Writes  dist/mini-potform-amt.ttl, mini-potform-afe.ttl, mini-potform-back.ttl
        dist/mini-coins-amt.ttl, mini-coins-back.ttl, dist/mini-roundtrip-report.md

Both sides must come back the same. If the AMT engine 0.7.0 or newer is installed, the coins also go through the engine
before the way back, and the parallel statements are run through the engine and the way back.

Standalone: python py/step_mini_roundtrip.py
"""
from __future__ import annotations

import re
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rdflib import BNode, Graph, Literal, RDF, RDFS  # noqa: E402

import step_afe_roundtrip as AR  # noqa: E402
import step_roundtrip as RT  # noqa: E402
import weights as W  # noqa: E402
from samian_amt_utils import DIST, ROOT, local  # noqa: E402

REL = "informationcarrier--potform"
COINS_FILE = ROOT / "data" / "afe" / "afe-mini-coins.ttl"
PARALLEL_FILE = ROOT / "data" / "afe" / "amt-parallel-statements.ttl"
SAM, FW, AMT = RT.SAM, RT.FW, RT.AMT

# (number, name, carrier id, carrier label, source string, coin, note)
CASES = [
    (1, "certain", "mini_1", "Carrier mini 1", "31", "15668", "constructed, same rule"),
    (2, "uncertain", "103585", "Carrier 103585", "18/31?", "16048", "PF.2, Onnio-"),
    (3, "vague", "156521", "Carrier 156521", "15/17 or 18 or 18/31", "15661", "PF.1, Secundus v"),
    (4, "vague and uncertain", "210355", "Carrier 210355", "15/17 or 18 (R?)", "12324", "PF.3, Secundus ii"),
]
EXPECTED_TYPES = {1: {"Certainty"}, 2: {"Uncertainty"}, 3: {"Vagueness"}, 4: {"FuzzinessWobbliness"}}


def slug(x: str) -> str:
    return re.sub(r"[^0-9A-Za-z]+", "_", x).strip("_")


def potform_amt() -> Graph:
    """The four carriers and their potforms as hextuples (five parts), from the weight rule of py/weights.py."""
    g = RT.bind(Graph())
    for k in (SAM.InformationCarrier, SAM.Potform):
        g.add((k, RDF.type, AMT.Concept))
    g.add((SAM.InformationCarrier, RDFS.label, Literal("Information carrier")))
    g.add((SAM.Potform, RDFS.label, Literal("Potform")))
    for _, _, cid, label, text, _, _ in CASES:
        c = SAM["ic_" + cid]
        g.add((c, AMT.instanceOf, SAM.InformationCarrier))
        g.add((c, RDFS.label, Literal(label)))
        for e in W.edges_for(text, REL):
            pf = SAM["pf_" + slug(e["entity"])]
            g.add((pf, AMT.instanceOf, SAM.Potform))
            g.add((pf, RDFS.label, Literal("Potform " + e["entity"])))
            s = BNode()
            for p, o in ((RDF.subject, c), (RDF.predicate, SAM.hasType), (RDF.object, pf),
                         (FW.hasDegreeOfConnection, Literal(Decimal(str(e["weight"])))), (FW.hasType, FW[e["type"]])):
                g.add((s, p, o))
    return g


def potform_edges(g: Graph, carrier) -> list[dict]:
    out = []
    for s in g.subjects(RDF.subject, carrier):
        o = g.value(s, RDF.object)
        out.append({"object": g.value(o, RDFS.label).toPython().replace("Potform ", ""),
                    "weight": Decimal(str(g.value(s, FW.hasDegreeOfConnection))).normalize(),
                    "type": local(g.value(s, FW.hasType))})
    return sorted(out, key=lambda e: e["object"])


def afe_form(afe: Graph, subject, prop) -> dict:
    """The AFE form of one value: direct, or a container with class and members (value label, confidence)."""
    v = afe.value(subject, prop)
    if not isinstance(v, BNode):
        return {"kind": "direct", "class": None, "members": [(local(v), None)]}
    cls = [local(c) for c in afe.objects(v, RDF.type) if c != AR.SKOS.Collection][0]
    members = list(afe.objects(v, AR.SKOS.member))
    if members:
        ms = [(local(afe.value(m, RDF.value)), Decimal(str(afe.value(m, AR.FW.hasConfidence))).normalize()) for m in members]
        return {"kind": "collection", "class": cls, "members": sorted(ms, key=lambda m: m[0])}
    return {"kind": "single", "class": cls,
            "members": [(local(afe.value(v, RDF.value)), Decimal(str(afe.value(v, AR.FW.hasConfidence))).normalize())]}


def run_potform() -> dict:
    DIST.mkdir(exist_ok=True)
    amt = potform_amt()
    RT.canonical(amt).serialize(DIST / "mini-potform-amt.ttl", format="turtle")
    afe = RT.canonical(RT.deskolemise(RT.construct(RT.Q_TO_AFE, amt)))
    afe.serialize(DIST / "mini-potform-afe.ttl", format="turtle")
    afe = Graph().parse(DIST / "mini-potform-afe.ttl", format="turtle")
    back = RT.canonical(RT.construct(RT.Q_TO_AMT, afe))
    back.serialize(DIST / "mini-potform-back.ttl", format="turtle")
    counts = RT.compare(amt, back)          # raises if a statement or node changed
    cases = []
    for n, name, cid, label, text, coin, note in CASES:
        c = SAM["ic_" + cid]
        edges = potform_edges(amt, c)
        got = {e["type"] for e in edges}
        if got != EXPECTED_TYPES[n]:
            raise AssertionError(f"mini case {n}: types {got} instead of {EXPECTED_TYPES[n]}")
        cases.append({"n": n, "name": name, "carrier": cid, "label": label, "text": text, "note": note,
                      "edges": edges, "form": afe_form(afe, c, SAM.hasType), "same": potform_edges(back, c) == edges})
    if not all(c["same"] for c in cases):
        raise AssertionError("mini round trip (Potform): a case did not come back the same")
    return {"cases": cases, "statements": counts["statements"], "nodes": counts["nodes"], "graphs": (amt, afe, back)}


def run_coins() -> dict:
    afe = Graph().parse(COINS_FILE)
    amt = AR.construct(AR.Q_FORTH, afe)
    amt_path = DIST / "mini-coins-amt.ttl"
    AR.canonical(amt).serialize(amt_path, format="turtle")
    middle, engine = amt, False
    if AR.engine_ready():
        middle, engine = AR.through_engine(amt_path, "mini-coins"), True
    back = AR.canonical(AR.blank(AR.construct(AR.Q_BACK, middle), False))
    back.serialize(DIST / "mini-coins-back.ttl", format="turtle")
    back = Graph().parse(DIST / "mini-coins-back.ttl", format="turtle")
    out = []
    for n, name, _, _, _, coin, note in CASES:
        uri = next(c for c in AR.coins(afe) if AR.short(c) == coin)
        v = AR.verdict(afe, back, uri)
        edges = AR.edges(amt, uri)
        got = {e["type"] for e in edges}
        if v != "same" or got != EXPECTED_TYPES[n]:
            raise AssertionError(f"mini coin {coin}: {v}, types {got} instead of {EXPECTED_TYPES[n]}")
        out.append({"n": n, "coin": coin, "edges": edges, "form": afe_form(afe, uri, AR.NMO.hasAuthority), "verdict": v})
    return {"cases": out, "engine": engine, "graphs": (afe, middle, back)}


def run_parallel() -> dict | None:
    """Two parallel statements on one coin property through the engine, and what the way back makes of them."""
    if not AR.engine_ready():
        return None
    middle = AR.through_engine(PARALLEL_FILE, "mini-parallel")
    weights = sorted(Decimal(str(w)).normalize() for w in middle.objects(None, AMT.weight))
    agents = sorted(local(a) for a in middle.objects(None, FW.derivedFrom))
    if weights != [Decimal("0.3"), Decimal("0.8")] or agents != ["M65", "M66"]:
        raise AssertionError(f"parallel statements: the engine gave weights {weights} and sources {agents}")
    back = AR.blank(AR.construct(AR.Q_BACK, middle), False)
    containers = {o for _, _, o in back.triples((None, AR.NMO.hasAuthority, None))}
    return {"weights": weights, "agents": agents, "containers_back": len(containers)}


def run() -> dict:
    res = {"potform": run_potform(), "coins": run_coins(), "parallel": run_parallel()}
    par = res["parallel"]
    if par is not None and par["containers_back"] != 1:
        raise AssertionError("parallel statements: the way back now keeps them apart; update the page and the PRIMER")
    return res


def case_graph(g: Graph, subject) -> Graph:
    """The part of a graph that belongs to one subject: its triples, nested blank nodes, and statements about it."""
    out = Graph()
    for pre, ns in g.namespaces():
        out.bind(pre, ns)
    seen: set = set()

    def take(node):
        if node in seen:
            return
        seen.add(node)
        for p, o in g.predicate_objects(node):
            out.add((node, p, o))
            if isinstance(o, BNode):
                take(o)
            elif p in (RDF.subject, RDF.object, AMT.instanceOf):
                for p2 in (RDF.type, RDFS.label):
                    for o2 in g.objects(o, p2):
                        out.add((o, p2, o2))
    take(subject)
    for st in g.subjects(RDF.subject, subject):
        take(st)
    for _, _, o in list(out.triples((None, AMT.instanceOf, None))):
        for p2 in (RDF.type, RDFS.label):
            for o2 in g.objects(o, p2):
                out.add((o, p2, o2))
    return out


FORMS = {"sherd": ("1-amt", "2-afe", "3-amt-again"), "coin": ("1-afe", "2-amt", "3-afe-again")}


def write_cases(r: dict, folder: Path) -> list[str]:
    """One Turtle file per case, side and form (24 files): what the figures show, written canonically."""
    folder.mkdir(parents=True, exist_ok=True)
    pa, pf, pb = r["potform"]["graphs"]
    ca, cm, cb = r["coins"]["graphs"]
    names = []
    for p, c in zip(r["potform"]["cases"], r["coins"]["cases"]):
        subj = SAM["ic_" + p["carrier"]]
        coin = next(x for x in AR.coins(ca) if AR.short(x) == c["coin"])
        for side, graphs, node in (("sherd", (pa, pf, pb), subj), ("coin", (ca, cm, cb), coin)):
            for form, g in zip(FORMS[side], graphs):
                sub = case_graph(g, node)
                canon = RT.canonical(sub) if side == "sherd" else AR.canonical(AR.blank(sub, False))
                name = f"case-{p['n']}-{side}-{form}.ttl"
                canon.serialize(folder / name, format="turtle")
                names.append(name)
    return names


def report(r: dict) -> str:
    lines = ["# Mini round trip", "", "| Case | Potform side | AFE side |", "|---|---|---|"]
    for p, c in zip(r["potform"]["cases"], r["coins"]["cases"]):
        lines.append(f"| {p['n']} {p['name']} | {'same' if p['same'] else 'different'} | {c['verdict']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    r = run()
    (DIST / "mini-roundtrip-report.md").write_text(report(r), encoding="utf-8", newline="\n")
    p, c = r["potform"], r["coins"]
    print(f"mini round trip: four kinds of statement on both sides come back the same ({p['statements']} hextuples of "
          f"{len(p['cases'])} carriers, {len(c['cases'])} coins){' through the AMT engine' if c['engine'] else ' without the AMT engine'}")
    par = r["parallel"]
    if par:
        print("mini round trip: two parallel statements on one coin property stay apart in the engine "
              f"(weights {', '.join(str(w) for w in par['weights'])}, sources {', '.join(par['agents'])}); the way back merges them into "
              f"{par['containers_back']} container (known limit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
