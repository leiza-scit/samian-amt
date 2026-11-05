"""Step "afe-roundtrip": AFE -> AMT -> AFE on the coin data of the AFE (package AFE-AMT-AFE, version 3, 2026-11-03).

Reads   data/afe/afe-all-cases.ttl             the five coins of the AFE, unchanged (the four cases of AFE values)
        data/afe/afe-edge-cases.ttl            four constructed coins that do not come back loss-free (A to D)
        data/afe/afe-denomination-mint-test.ttl  three constructed coins with nmo:hasDenomination and nmo:hasMint
        queries/coins/afe-to-amt.rq            AFE container pattern -> hextuples
        queries/coins/amt-to-afe.rq            hextuples -> AFE container pattern
Writes  dist/afe-<name>-as-amt.ttl             the coins as hextuples
        dist/afe-<name>-back.ttl               the AFE pattern rebuilt from them (blank-node containers)
        dist/afe-roundtrip-report.md           per coin: same, same on the top class, or different

Per coin the original AFE structure (the coin, its three properties and the containers) is compared with the rebuilt
one as a graph; numbers are compared as values (0.25 and 0.250000 are the same xsd:decimal), and the container classes
on the top level (VagueValue = VagueResourceValue, as agreed with the AFE side on 2026-11-03).

The expected outcome of the constructed coins is part of the test: A and D are not loss-free, B comes back equal on the top
class, C comes back unchanged. If the AMT engine 0.7.0 or newer is installed, the coins of the first file also go through
the engine (reasoning) before the way back, and the result must be the same.

This is the state of the package of 2026-11-03; the answers of the AFE side are still open (see PRIMER, S30).

Standalone: python py/step_afe_roundtrip.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef, XSD  # noqa: E402
from rdflib.compare import isomorphic, to_canonical_graph, to_isomorphic  # noqa: E402

from samian_amt_utils import DIST, ROOT, local  # noqa: E402

DATA = ROOT / "data" / "afe"
Q_FORTH = ROOT / "queries" / "coins" / "afe-to-amt.rq"
Q_BACK = ROOT / "queries" / "coins" / "amt-to-afe.rq"
FILES = {"all-cases": DATA / "afe-all-cases.ttl", "edge-cases": DATA / "afe-edge-cases.ttl",
         "denomination-mint": DATA / "afe-denomination-mint-test.ttl"}

NMO = Namespace("http://nomisma.org/ontology#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
FW = Namespace("http://w3id.org/fw_ontology/")
AMT = Namespace("http://academic-meta-tool.xyz/vocab#")
CONT = "urn:amt-afe:container:"
PROPS = (NMO.hasAuthority, NMO.hasDenomination, NMO.hasMint)
PREFIXES = {"amt": str(AMT), "fw": str(FW), "nm": "http://nomisma.org/id/", "nmo": str(NMO),
            "afe": "http://afe.dainst.org/coin?afeid=", "lado": "http://archaeology.link/ontology#", "skos": str(SKOS)}
VALUE_TO_RESOURCE = {FW.VagueValue: FW.VagueResourceValue, FW.UncertainValue: FW.UncertainResourceValue,
                     FW.FuzzinessWobblinessValue: FW.FuzzinessWobblinessResourceValue}

# what the constructed coins of data/afe/afe-edge-cases.ttl must do (memo, section 7)
# Since 2026-11-05 (Karsten Tolle) 16048 is written with fw:UncertainResourceValue in the AFE too (the values are IRIs), so every
# coin of the first and third file comes back the same. The top-class rule stays for coins written the old way (edge case 90002).
TOP_EXPECTED: dict[str, set] = {"all-cases": set(), "denomination-mint": set()}
EDGE_EXPECTED = {"90001": "different", "90002": "top class", "90003": "same", "90004": "different"}
MIN_ENGINE = (0, 7, 0)


def bind(g: Graph) -> Graph:
    for k, v in PREFIXES.items():
        g.bind(k, v)
    return g


def construct(query: Path, graph: Graph) -> Graph:
    out = bind(Graph())
    out += graph.query(query.read_text(encoding="utf-8")).graph
    return out


def canon(o):
    """0.250000 and 0.25 are the same xsd:decimal value; the engine writes six places."""
    if isinstance(o, Literal) and o.datatype == XSD.decimal:
        return Literal(format(Decimal(str(o)).normalize(), "f"), datatype=XSD.decimal)
    return o


def coin_part(g: Graph, coin) -> Graph:
    """One coin with its three properties and the containers below them, nothing else."""
    out = Graph()

    def copy(node):
        for s, p, o in g.triples((node, None, None)):
            out.add((s, p, o))
            if isinstance(o, BNode):
                copy(o)

    out.add((coin, RDF.type, NMO.NumismaticObject))
    for prop in PROPS:
        for value in g.objects(coin, prop):
            out.add((coin, prop, value))
            if isinstance(value, BNode):
                copy(value)
    return out


def blank(g: Graph, top: bool) -> Graph:
    """Generated container IRIs become blank nodes again; numbers by value; with top=True also the top class."""
    mapping: dict = {}

    def fresh(x):
        return mapping.setdefault(x, BNode()) if isinstance(x, URIRef) and str(x).startswith(CONT) else x

    out = Graph()
    for s, p, o in g:
        o = fresh(canon(o))
        if top and p == RDF.type:
            o = VALUE_TO_RESOURCE.get(o, o)
        out.add((fresh(s), p, o))
    return out


def verdict(afe: Graph, back: Graph, coin) -> str:
    a, b = coin_part(afe, coin), coin_part(back, coin)
    if isomorphic(to_isomorphic(blank(a, False)), to_isomorphic(blank(b, False))):
        return "same"
    if isomorphic(to_isomorphic(blank(a, True)), to_isomorphic(blank(b, True))):
        return "top class"
    return "different"


def canonical(g: Graph) -> Graph:
    out = bind(Graph())
    for t in to_canonical_graph(g):
        out.add(t)
    return out


def engine_ready() -> bool:
    try:
        import amt
        from amt.fw import CERTAINTY  # noqa: F401
    except ImportError:
        return False
    version = tuple(int(x) for x in str(getattr(amt, "__version__", "0")).split(".")[:3] if x.isdigit())
    return version >= MIN_ENGINE


def through_engine(path: Path, name: str) -> Graph:
    """The hextuples through the AMT engine (reasoning); the reasoned graph is the middle of the round trip."""
    out = DIST / f"afe-engine-{name}"
    shutil.rmtree(out, ignore_errors=True)
    r = subprocess.run([sys.executable, "-m", "amt.runner", str(path), "-o", str(out), "--no-info", "--strict"],
                       capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(f"the AMT engine failed on {path.name}:\n{r.stdout[-600:]}\n{r.stderr[-600:]}")
    return Graph().parse(next(out.glob("*.reasoned.ttl")))


def coins(g: Graph) -> list:
    return sorted(g.subjects(RDF.type, NMO.NumismaticObject), key=str)


def short(coin) -> str:
    return str(coin).split("=")[-1]


def edges(amt: Graph, coin) -> list[dict]:
    """The hextuples of one coin: property, object, weight, type, method (local names)."""
    out = []
    for node in amt.objects(coin, URIRef("http://archaeology.link/ontology#hasAMT")):
        w = amt.value(node, AMT.weight)
        t, m = amt.value(node, FW.hasType), amt.value(node, FW.hasMethod)
        out.append({"property": local(amt.value(node, RDF.predicate)), "object": local(amt.value(node, RDF.object)),
                    "weight": Decimal(str(w)).normalize(), "type": local(t) if t else None, "method": local(m) if m else None})
    return sorted(out, key=lambda e: (e["property"], e["object"]))


def run_file(name: str, use_engine: bool) -> dict:
    DIST.mkdir(exist_ok=True)
    afe = Graph().parse(FILES[name])
    amt = construct(Q_FORTH, afe)
    amt_path = DIST / f"afe-{name}-as-amt.ttl"
    canonical(amt).serialize(amt_path, format="turtle")
    middle = amt
    engine = False
    if use_engine and name == "all-cases":
        middle, engine = through_engine(amt_path, name), True
    back = canonical(blank(construct(Q_BACK, middle), False))
    back.serialize(DIST / f"afe-{name}-back.ttl", format="turtle")
    back = Graph().parse(DIST / f"afe-{name}-back.ttl", format="turtle")
    return {"name": name, "afe": afe, "amt": amt, "back": back, "engine": engine,
            "verdicts": {short(c): verdict(afe, back, c) for c in coins(afe)}}


def run() -> dict:
    use_engine = engine_ready()
    res = {name: run_file(name, use_engine) for name in FILES}
    got = res["edge-cases"]["verdicts"]
    if got != EDGE_EXPECTED:
        raise AssertionError(f"the constructed coins do not behave as documented: {got} instead of {EDGE_EXPECTED}")
    for name in ("all-cases", "denomination-mint"):
        top = TOP_EXPECTED[name]
        bad = {c: v for c, v in res[name]["verdicts"].items() if v != ("top class" if c in top else "same")}
        if bad:
            raise AssertionError(f"{name}: coins that do not come back as documented: {bad}")
    return {"files": res, "engine": use_engine}


def report(r: dict) -> str:
    lines = ["# Round trip AFE -> AMT -> AFE", "", f"AMT engine in the middle: {'yes' if r['engine'] else 'no (not installed or older than 0.7.0)'}", ""]
    for name, f in r["files"].items():
        lines += [f"## {name}", "", "| Coin | Result |", "|---|---|"] + [f"| {c} | {v} |" for c, v in f["verdicts"].items()] + [""]
    return "\n".join(lines)


def main() -> int:
    r = run()
    (DIST / "afe-roundtrip-report.md").write_text(report(r), encoding="utf-8", newline="\n")
    a, e, d = (r["files"][k]["verdicts"] for k in ("all-cases", "edge-cases", "denomination-mint"))
    same = sum(v == "same" for v in a.values())
    note = "" if same == len(a) else f" ({same} the same, {len(a) - same} on the top class)"
    d_same = sum(v == "same" for v in d.values())
    d_note = "all the same" if d_same == len(d) else f"{d_same} the same, {len(d) - d_same} on the top class"
    print(f"round trip AFE -> AMT -> AFE: {len(a)} coins of the AFE come back equal{note}"
          f"{' through the AMT engine' if r['engine'] else ' without the AMT engine'}; "
          f"{len(d)} constructed coins with denomination and mint too ({d_note})")
    print("round trip AFE: constructed edge cases as documented: " + ", ".join(f"{c} {v}" for c, v in e.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
