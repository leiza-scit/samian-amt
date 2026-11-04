"""Step "roundtrip": AMT -> AFE -> AMT on the three chains and on every pattern of the weight rule.

Reads   dist/chains.ttl                   the hextuples of model M1 (step chains)
        data/weight-cases.csv             one source string per pattern of the weight rule
        queries/amt-to-afe.rq             hextuples -> the container pattern of the AFE coin data
        queries/afe-to-amt.rq             the container pattern -> hextuples
Writes  dist/chains-afe.ttl               the chains as AFE pattern (blank-node containers)
        dist/chains-back.ttl              the chains as hextuples again (fw:hasMethod fw:AFEAssignment, no evidence)
        dist/chains-back-with-model.ttl   ontology M1 + chains-back.ttl (input for the AMT engine and the runner)
        dist/roundtrip-report.md          what was compared and what differs
        dist/patterns-afe.ttl, dist/patterns-back.ttl   the same for the pattern cases

Two tests.
  (a) Statements. Subject, predicate, object, weight and FW type of every hextuple must come back unchanged; the nodes
      (concept and label) too. Not compared, because AFE does not carry them: the method (fw:EqualShareRule comes back as
      fw:AFEAssignment), the source string (fw:TextEvidence), the frequency shares and sam:attributedTo (model M2).
  (b) Reasoning. The three runs (M1 product, M1 Goedel, M2 product) on the returned statements must give the same 340
      edges as on the originals (weight, type, and method of every derived edge). If the AMT engine is installed it
      repeats the runs on the returned graph and must agree with the reference reasoner there as well.

The AFE side is modelled after the AFE coin data (containers for vague and uncertain values), with sam: properties.
It is not real AFE data; AFE knows no potforms or production centres.

Standalone: python py/step_roundtrip.py
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rdflib.compare import to_canonical_graph  # noqa: E402
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef  # noqa: E402

import step_chains as C  # noqa: E402
import weights as W  # noqa: E402
from reference_reasoner import reason  # noqa: E402
from samian_amt_utils import DIST, ONTOLOGY, ROOT, load_graph, local, read_model  # noqa: E402

Q_TO_AFE = ROOT / "queries" / "amt-to-afe.rq"
Q_TO_AMT = ROOT / "queries" / "afe-to-amt.rq"

FW = Namespace(C.FW_NS)
AMT = Namespace("http://academic-meta-tool.xyz/vocab#")
SAM = Namespace("http://example.org/samian-amt/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
CONTAINER, MEMBER = "urn:amt-afe:container:", "urn:amt-afe:member:"
PREFIXES = {"amt": str(AMT), "fw": str(FW), "sam": str(SAM), "skos": str(SKOS),
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"}

# what the AFE side calls the containers: kept in one place for the documentation and the figures
AFE_CLASS = {"Vagueness": "VagueResourceValue", "Uncertainty": "UncertainResourceValue",
             "FuzzinessWobbliness": "FuzzinessWobblinessResourceValue"}
PREDICATE_OF = {"informationcarrier--potform": ("InformationCarrier", "hasType", "Potform"),
                "informationcarrier--productioncentre": ("InformationCarrier", "hasProductionCentre", "ProductionCentre"),
                "actor--productioncentre": ("Actor", "worksAt", "ProductionCentre")}


def bind(g: Graph) -> Graph:
    for k, v in PREFIXES.items():
        g.bind(k, v)
    return g


def construct(query: Path, graph: Graph) -> Graph:
    out = bind(Graph())
    out += graph.query(query.read_text(encoding="utf-8")).graph
    return out


def deskolemise(g: Graph) -> Graph:
    """The generated container and member IRIs become blank nodes, as in AFE data."""
    mapping: dict = {}

    def fresh(x):
        if isinstance(x, URIRef) and str(x).startswith((CONTAINER, MEMBER)):
            return mapping.setdefault(x, BNode())
        return x

    out = bind(Graph())
    for s, p, o in g:
        out.add((fresh(s), p, fresh(o)))
    return out


def canonical(g: Graph) -> Graph:
    """Blank nodes get names derived from their content, so that the written Turtle is the same on every run."""
    out = bind(Graph())
    for t in to_canonical_graph(g):
        out.add(t)
    return out


def statements(g: Graph) -> dict:
    """{(subject, predicate, object): (weight, type, method)} of every reified statement, by local name."""
    out = {}
    for s in g.subjects(RDF.subject, None):
        w = g.value(s, FW.hasDegreeOfConnection) or g.value(s, AMT.weight)
        t, m = g.value(s, FW.hasType), g.value(s, FW.hasMethod)
        key = (local(g.value(s, RDF.subject)), local(g.value(s, RDF.predicate)), local(g.value(s, RDF.object)))
        if key in out:
            raise AssertionError(f"statement twice: {key}")
        out[key] = (Decimal(str(w)).normalize(), local(t) if t else None, local(m) if m else None)
    return out


def nodes(g: Graph) -> dict:
    """{node: (concept, label)} of the AMT side (amt:instanceOf) or of the AFE side (rdf:type)."""
    out = {}
    for n, c in g.subject_objects(AMT.instanceOf):
        out[local(n)] = (local(c), str(g.value(n, URIRef(PREFIXES["rdfs"] + "label"))))
    if not out:
        concepts = {SAM.Potform, SAM.InformationCarrier, SAM.ProductionCentre, SAM.Actor}
        for n, c in g.subject_objects(RDF.type):
            if c in concepts:
                out[local(n)] = (local(c), str(g.value(n, URIRef(PREFIXES["rdfs"] + "label"))))
    return out


def container_shapes(afe: Graph) -> Counter:
    """How many values of each AFE form the AFE graph holds: direct, one value, collection (by class)."""
    shapes: Counter = Counter()
    for s, p, o in afe:
        if p not in (SAM.hasType, SAM.hasProductionCentre, SAM.worksAt):
            continue
        if isinstance(o, BNode):
            cls = local(next(c for c in afe.objects(o, RDF.type) if c != SKOS.Collection))
            shapes[cls + (" (collection)" if (o, SKOS.member, None) in afe else " (one value)")] += 1
        else:
            shapes["direct value (certain)"] += 1
    return shapes


def turn(amt: Graph, name: str) -> tuple[Graph, Graph]:
    """AMT -> AFE (written to dist/<name>-afe.ttl and read back) -> AMT."""
    afe = canonical(deskolemise(construct(Q_TO_AFE, amt)))
    path = DIST / f"{name}-afe.ttl"
    afe.serialize(path, format="turtle")
    back = canonical(construct(Q_TO_AMT, Graph().parse(path, format="turtle")))      # through the file, as a person would
    back.serialize(DIST / f"{name}-back.ttl", format="turtle")
    return Graph().parse(path, format="turtle"), back


def compare(before: Graph, after: Graph) -> dict:
    """Test (a). Returns the counts for the report; raises if a statement or a node changed."""
    b, a = statements(before), statements(after)
    problems = [f"only before: {k}" for k in sorted(set(b) - set(a))] + [f"only after: {k}" for k in sorted(set(a) - set(b))]
    for key in sorted(set(a) & set(b)):
        if b[key][:2] != a[key][:2]:
            problems.append(f"{key}: weight and type {b[key][:2]} became {a[key][:2]}")
    nb, na = nodes(before), nodes(after)
    problems += [f"node {k}: {nb.get(k)} became {na.get(k)}" for k in sorted(set(nb) | set(na)) if nb.get(k) != na.get(k)]
    if problems:
        raise AssertionError("round trip AMT -> AFE -> AMT changed something:\n  " + "\n  ".join(problems[:20]))
    return {"statements": len(b), "nodes": len(nb), "methods": Counter((v[2], a[k][2]) for k, v in b.items())}


def patterns_graph() -> tuple[Graph, list[dict]]:
    """One carrier or actor per case of data/weight-cases.csv, so that every pattern of the rule is covered."""
    nodes_, edges, rows = {}, [], []
    with W.CASES.open(encoding="utf-8", newline="") as fh:
        for i, case in enumerate(csv.DictReader(fh), 1):
            concept, role, target = PREDICATE_OF[case["context"]]
            subject = f"case_{i:02d}"
            nodes_[subject] = (concept, f"Case {i:02d}: {case['text']}")
            for e in W.edges_for(case["text"], case["context"]):
                key = ("pf_" if target == "Potform" else "pc_") + C.slug(e["entity"])
                nodes_[key] = (target, (target + " " if target == "Potform" else "") + e["entity"])
                edges.append({"role": role, "from": subject, "to": key, "context": case["context"],
                              "evidence": C.evidence_id(case["context"], case["text"]), **e})
            rows.append({**case, "subject": subject})
    text = "\n".join([C.HEADER, C.nodes_ttl(nodes_), "", C.evidence_ttl(edges), ""] + [C.statement_ttl(e) for e in edges])
    return Graph().parse(data=text, format="turtle"), rows


def back_edges(back: Graph) -> list[dict]:
    """The returned statements as edge dicts for the reference reasoner and the engine inputs."""
    return [{"role": p, "from": s, "to": o, "weight": float(w), "type": t, "method": m, "evidence": None, "context": ""}
            for (s, p, o), (w, t, m) in sorted(statements(back).items())]


def reasoning_equal(res: dict, back: Graph) -> tuple[dict, int]:
    """Test (b): the three runs on the returned statements against the runs on the originals."""
    edges = back_edges(back)
    res2_edges = [(e["role"], e["from"], e["to"], e["weight"], e["type"]) for e in edges]
    m1, m2 = read_model(load_graph(ONTOLOGY)), read_model(load_graph(C.VARIANT))
    m2_edges = [t for t in res2_edges if t[0] != "hasProductionCentre"] + [t for t in res["m2_edges"] if t[0] == "createdBy"]
    runs = {"M1 product": reason(m1, res2_edges), "M1 goedel": reason(C.with_logic(m1, "GoedelLogic"), res2_edges),
            "M2 product": reason(m2, m2_edges)}
    problems = []
    for name, state in runs.items():
        ref = res["runs"][name]
        for key in sorted(set(ref) ^ set(state)):
            problems.append(f"{name}: {key} only in {'original' if key in ref else 'returned'}")
        for key in sorted(set(ref) & set(state)):
            r, s = ref[key], state[key]
            same = abs(r["weight"] - s["weight"]) < 1e-9 and r["type"] == s["type"]
            if r["inferred"]:                                     # the method of an asserted edge is not compared
                same = same and r["method"] == s["method"]
            if not same:
                problems.append(f"{name}: {key} {(r['weight'], r['type'], r['method'])} became {(s['weight'], s['type'], s['method'])}")
    if problems:
        raise AssertionError("reasoning on the returned statements differs:\n  " + "\n  ".join(problems[:20]))
    return {**res, "edges": edges, "runs": runs, "m2_edges": m2_edges}, sum(len(s) for s in runs.values())


def run() -> dict:
    """Everything the step, the figures and the documentation need."""
    DIST.mkdir(exist_ok=True)
    res = C.run()
    C.write_ttl(res["edges"], res["nodes"], res["rows"])                  # dist/chains.ttl, as the step chains writes it
    original = Graph().parse(DIST / "chains.ttl", format="turtle")
    afe, back = turn(original, "chains")
    chains = compare(original, back)
    res2, n_edges = reasoning_equal(res, back)
    (DIST / "chains-back-with-model.ttl").write_text(C.engine_inputs(res2)["M1 product"], encoding="utf-8", newline="\n")
    cases, rows = patterns_graph()
    cases.serialize(DIST / "patterns.ttl", format="turtle")
    afe_p, back_p = turn(cases, "patterns")
    patterns = compare(cases, back_p)
    seen = {r["pattern"] for r in rows}
    if seen != {"certain", "q", "and", "or", "q+and", "q+or"}:
        raise AssertionError(f"the cases do not cover all six patterns: {sorted(seen)}")
    return {"res": res, "res2": res2, "original": original, "afe": afe, "back": back, "chains": chains, "reasoned_edges": n_edges,
            "afe_shapes": container_shapes(afe), "patterns": patterns, "pattern_rows": rows, "pattern_afe": afe_p,
            "pattern_shapes": container_shapes(afe_p), "lost": lost_counts(original)}


def lost_counts(original: Graph) -> dict:
    """What the AFE pattern does not carry, counted on the original graph."""
    return {"evidence": len(list(original.subjects(RDF.type, FW.TextEvidence))),
            "frequency": len(list(original.subjects(SAM.frequencyShare, None))),
            "attributed": len(list(original.subject_objects(SAM.attributedTo))),
            "methods": len({local(m) for m in original.objects(None, FW.hasMethod)})}


def report(r: dict) -> str:
    c, p = r["chains"], r["patterns"]
    lines = ["# Round trip AMT -> AFE -> AMT", "",
             f"Chains: {c['statements']} hextuples and {c['nodes']} nodes come back with the same subject, predicate, object, weight and FW type.",
             f"Reasoning: the three runs on the returned statements give the same {r['reasoned_edges']} edges (weight, type, method of derived edges).",
             f"Patterns: {p['statements']} hextuples of {len(r['pattern_rows'])} cases, all six patterns of the weight rule, come back the same.", "",
             "## AFE forms written (chains)", "", "| Form | Count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(r["afe_shapes"].items())]
    lines += ["", "## Not carried by the AFE pattern", "",
              f"- fw:hasMethod: {', '.join(f'{a} -> {b}' for (a, b), n in sorted(c['methods'].items(), key=str))} (all {c['statements']} statements)",
              f"- fw:TextEvidence (source strings): {r['lost']['evidence']}",
              f"- frequency shares: {r['lost']['frequency']} statements", f"- sam:attributedTo (model M2 only): {r['lost']['attributed']}"]
    return "\n".join(lines) + "\n"


def main() -> int:
    r = run()
    (DIST / "roundtrip-report.md").write_text(report(r), encoding="utf-8", newline="\n")
    c, p = r["chains"], r["patterns"]
    print(f"round trip AMT -> AFE -> AMT: {c['statements']} hextuples and {c['nodes']} nodes of the chains come back the same "
          f"(subject, predicate, object, weight, type); method becomes fw:AFEAssignment, evidence and frequency shares are not carried")
    print(f"round trip: the three reasoning runs on the returned statements give the same {r['reasoned_edges']} edges")
    print(f"round trip: {p['statements']} hextuples of {len(r['pattern_rows'])} pattern cases (all six patterns) come back the same")
    return C.engine_check({**r["res2"], "nodes": r["res"]["nodes"]}, prefix="back-")


if __name__ == "__main__":
    raise SystemExit(main())
