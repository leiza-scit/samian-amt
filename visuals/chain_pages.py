"""Chain sub pages: one page per chain of the Samian Research data (A, B, C).

Every chain holds vague, uncertain or fuzzy-wobbly statements. A page shows them in the order the
reasoning uses them: first the asserted statements (the potform of each carrier, the centres of the
potter, each as a figure in the style of the case figures), then what the AMT reasoning derives from them
(the chain figure and the table of degrees under the models M1 and M2).

The strings come from data/chains-source.csv, the weights and types from py/weights.py, the derived degrees
from py/step_chains.py. A centre without coordinates in visuals/data gets a figure without map (see
visuals/sql/kilnsites-chains.sql); a potform without profile drawing shows a placeholder.
"""
from __future__ import annotations

import csv
from html import escape

import build as B
from step_chains import comparison, run as run_chains

SRC = B.ROOT / "data" / "chains-source.csv"
TYPE = {"Certainty": "certainty", "Uncertainty": "uncertainty", "Vagueness": "vagueness",
        "FuzzinessWobbliness": "fuzzy / wobbly"}


def register(code, relation, string, row):
    B.CASES[code] = {"case": code, "relation": relation, "query_rows": "", "string_rows": "",
                     "carrier_id": row["carrier_id"], "pottername": row["potter"], "source_string": string}


def form_key(label):
    k = label.replace("/", "_")
    return k if k in B.FORMS else None


def table_inner(head, rows):
    th = "".join(f"<th>{escape(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


def table(head, rows):
    return f"<section>{table_inner(head, rows)}</section>"


def step(n, text):
    num = f'<span class="n">{n}</span>' if n != "" else ""
    return f'<h2 class="step">{num}{escape(text)}</h2>'


READING = {
    "q": "One value, marked with ? in the source: the recorder is not sure (uncertainty).",
    "or": "Several values joined by OR: exactly one of them holds, which one is open; the weight is shared equally (vagueness).",
    "and": "Several values joined by AND, no ?: all of them hold, each with the full weight (vagueness in the FW typing).",
    "q+and": "AND with ?: all listed values are meant, but the statement is marked as doubtful (fuzziness-wobbliness).",
    "q+or": "OR with ?: one of several values, and doubtful on top (fuzziness-wobbliness).",
}
CLASS_NOTE = {
    "InformationCarrier": "the recorded object; its id is the carrier id of Samian Research",
    "Actor": "the potter, by the name in the data",
    "Potform": "the vessel form named in the record of the carrier",
    "ProductionCentre": "a kiln site",
}
CLASS_ORDER = ["InformationCarrier", "Actor", "Potform", "ProductionCentre"]
PLURAL = {"InformationCarrier": "carriers", "Actor": "actor", "Potform": "potforms", "ProductionCentre": "production centres"}


def fmt(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def main():
    res = run_chains()
    comp = comparison(res)
    nodes, edges = res["nodes"], res["edges"]
    rows = list(csv.DictReader(open(SRC, encoding="utf-8", newline="")))
    cards_index = []
    for L in sorted({r["chain"] for r in rows}):
        mine = sorted((r for r in rows if r["chain"] == L), key=lambda r: r["carrier_id"])
        potter = mine[0]["potter"]
        cards, n = [], 0
        cards.append(step(1, "Statements about the potform (InformationCarrier, hasType)"))
        for r in mine:
            n += 1
            code = f"{L}.{n}"
            register(code, "informationcarrier--potform", r["potform_text"], r)
            _, st, ed = B.statements(code)
            forms = [(e["entity"], form_key(e["entity"])) for e in ed]
            name = f"chain-{L}-{n}-potform"
            B.potform_fig(name, code, f"Potform of carrier {r['carrier_id']}",
                          f"Chain {L}, {potter}: carrier {r['carrier_id']}; source string as in the Samian Research data (data/chains-source.csv).", forms)
            note = r["note"][0].upper() + r["note"][1:]
            cards.append(B.card(code, f"Potform of carrier {r['carrier_id']}: {r['potform_text']}",
                                f"{TYPE[ed[0]['type']]}; weight {ed[0]['weight']:.2f} per statement. Note from the source table: {note}.", name))
        n += 1
        code = f"{L}.{n}"
        register(code, "actor--productioncentre", mine[0]["centre_text"], mine[0])
        _, st, ed = B.statements(code)
        sites = [B.SITE_ALIAS.get(e["entity"], e["entity"]) for e in ed]
        have_map = all(s in B.KILNS for s in sites)
        cards.append(step(2, "Statements about the production centre (Actor, worksAt)"))
        sub = f"Chain {L}, {potter}: centres of the potter; the carrier inherits them (model M1)."
        credit = f"{TYPE[ed[0]['type']]}; weight {ed[0]['weight']:.2f} per statement."
        name = f"chain-{L}-{n}-centres"
        B.centre_fig(name, code, f"Centres of {potter}", sub, "actor")
        cards.append(B.card(code, f"Centres of {potter}: {mine[0]['centre_text']}", credit + (" Modern map." if have_map else " No map yet: coordinates missing."), name))
        if have_map:
            B.centre_fig(name + "-roman", code, f"Centres of {potter}", sub, "actor", "roman")
            cards.append(B.card(code, f"Centres of {potter}: {mine[0]['centre_text']} (Roman map)", credit + " Roman map.", name + "-roman"))

        cards.append(step(3, "Statements about the production centre of each carrier (InformationCarrier, hasProductionCentre)"))
        for r in mine:
            n += 1
            code = f"{L}.{n}"
            register(code, "informationcarrier--productioncentre", r["centre_text"], r)
            _, st, ed = B.statements(code)
            name = f"chain-{L}-{n}-carrier-centres"
            sub = f"Chain {L}: carrier {r['carrier_id']} with the centres of its potter (model M1, asserted on the carrier)."
            B.centre_fig(name, code, f"Centres of carrier {r['carrier_id']}", sub, "carrier")
            credit = f"{TYPE[ed[0]['type']]}; weight {ed[0]['weight']:.2f} per statement."
            cards.append(B.card(code, f"Centres of carrier {r['carrier_id']}: {r['centre_text']}", credit + (" Modern map." if have_map else " No map yet: coordinates missing."), name))
            if have_map:
                B.centre_fig(name + "-roman", code, f"Centres of carrier {r['carrier_id']}", sub, "carrier", "roman")
                cards.append(B.card(code, f"Centres of carrier {r['carrier_id']}: {r['centre_text']} (Roman map)", credit + " Roman map.", name + "-roman"))

        ics = ["ic_" + r["carrier_id"] for r in mine]
        pfs = {e["to"] for e in edges if e["role"] == "hasType" and e["from"] in ics}
        pcs = {e["to"] for e in edges if e["role"] == "hasProductionCentre" and e["from"] in ics}
        ae = next(e["from"] for e in edges if e["role"] == "worksAt" and e["to"] in pcs and nodes[e["from"]][1] == potter)
        mine_nodes = set(ics) | pfs | pcs | {ae}
        cards.append(step(4, "What the reasoning derives"))
        dr = [(c["relation"], nodes[c["from"]][1], nodes[c["to"]][1], fmt(c["m1_product"]), fmt(c["m1_goedel"]), fmt(c["m2_product"]))
              for c in comp if c["from"] in mine_nodes and c["to"] in mine_nodes]
        cards.append(table(["Derived role", "From", "To", "M1 product", "M1 Goedel", "M2 product"], dr))
        types = sorted({TYPE[e["type"]] for e in edges if e["from"] in mine_nodes and e["to"] in mine_nodes})

        # top of the page: the chain figure, the entities, the statements
        top = [step("", "The chain"),
               B.card("Chain", f"Asserted statements and derived degrees ({potter})",
                      "Product logic. M1: carrier-centre statements asserted; M2: derived from the actor.", f"model-05{L.lower()}-chain-{L}")]
        counts = {c: sorted(k for k, v in nodes.items() if k in mine_nodes and v[0] == c) for c in CLASS_ORDER}
        total = sum(len(v) for v in counts.values())
        listing = ", ".join(f"{len(counts[c])} {PLURAL[c] if len(counts[c]) != 1 else {'InformationCarrier': 'carrier', 'Actor': 'actor', 'Potform': 'potform', 'ProductionCentre': 'production centre'}[c]}" for c in CLASS_ORDER)
        top.append(f'<section class="text"><h3>Entities</h3><p>This chain has {total} entities: {listing}. '
                   f'The potter is {escape(potter)}; the carriers say which form the vessel has, and the potter says where the work was done.</p>')
        top.append(table_inner(["Class", "Entity", "Meaning"],
                               [(c, nodes[k][1], CLASS_NOTE[c]) for c in CLASS_ORDER for k in counts[c]]) + "</section>")
        srows, seen = [], set()
        for e in edges:
            if e["from"] in mine_nodes and e["to"] in mine_nodes and e["role"] in ("hasType", "hasProductionCentre", "worksAt"):
                st = B.wt.parse(e["source"])
                srows.append((e["role"], nodes[e["from"]][1], nodes[e["to"]][1], e["source"], TYPE[e["type"]],
                              f"1/{st.n_possibilities}" + (" × 1/2" if st.n_questionmark else "") + f" = {fmt(e['weight'])}"))
                seen.add(e["pattern"])
        read = "".join(f"<li><b>{escape(k)}</b>: {escape(READING[k])}</li>" for k in READING if k in seen)
        top.append(f'<section class="text"><h3>Vague, uncertain and fuzzy-wobbly statements</h3>'
                   f'<p>The statements come from the strings of the source data. Each string becomes one statement per entity, '
                   f'with a degree of connection (weight) and a type from the FW ontology. In this chain:</p><ul>{read}</ul>'
                   + table_inner(["Role", "From", "To", "Source string", "FW type", "Weight = 1/possibilities (× 1/2 for ?)"], srows) + "</section>")
        cards = top + cards
        types = sorted({TYPE[e["type"]] for e in edges if e["from"] in mine_nodes and e["to"] in mine_nodes})
        B.page(f"chain-{L}.html", f"Chain {L}: {potter}",
               f"{len(mine)} carrier{'s' if len(mine) > 1 else ''} of the potter; statement types in this chain: {', '.join(types)}. "
               "The statements come first, the reasoning after them.", cards)
        cards_index.append((f"Chain {L}", f"{potter}", ", ".join(types).capitalize() + ".", f"model-05{L.lower()}-chain-{L}", f"chain-{L}.html"))
    B.CHAIN_CARDS = cards_index
    print(len(cards_index), "chain pages ->", B.SITE)
