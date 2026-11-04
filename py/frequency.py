"""Frequency shares of the alternatives of an OR statement: additional information, not a weight.

Decided with Allard Mees and Florian Thiery on 2026-11-04:

* The share of an alternative is its number of vessels in the database divided by the number of vessels
  of all alternatives of the string ("31 or 31R": 9,070 / 11,302 = 0.8025 and 2,232 / 11,302 = 0.1975).
* It is a hint for the archaeologist to check an existing uncertainty against the overall distribution of
  the database. It has no influence on the uncertainty statement: it is not written to
  fw:hasDegreeOfConnection (that stays the rule of weights.py), it does not enter the chain, and a
  question mark in the string does not change the shares.
* Method (label agreed on 2026-11-04): "Probability based on frequency share" /
  "Wahrscheinlichkeit basierend auf dem Häufigkeitsanteil". Local name FrequencyShare in the namespace
  sam: until the FW ontology has an entry for it.
* Level "A" (the whole database) is implemented. Level "C" (the potter's own repertoire, smoothed with
  (n_potter + k * share_A) / (N_potter + k), k = 5, with the count n and a status attested /
  never_attested / no_data) and a level for the stamp are planned; see PRIMER.md, step S4a.

The counts come from data/form-counts.csv (columns "potform","n"). The file in the repository is an
extract of Allard Mees's export data-1793809985134.csv (forms with at least ten vessels); the complete
export has the same two columns and can replace it without a change of code.

Standalone: python py/frequency.py   (self-test with the 31 / 31R case)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from samian_amt_utils import ROOT  # noqa: E402

COUNTS = ROOT / "data" / "form-counts.csv"
METHOD = "FrequencyShare"
LEVEL = "A"
LABEL_EN = "Probability based on frequency share"
LABEL_DE = "Wahrscheinlichkeit basierend auf dem Häufigkeitsanteil"


def load_counts(path: Path = COUNTS) -> dict[str, int]:
    """Form -> number of vessels (certain forms only: no OR, no question mark)."""
    with path.open(encoding="utf-8", newline="") as fh:
        return {r["potform"].strip(): int(r["n"]) for r in csv.DictReader(fh)}


def shares(entities: tuple[str, ...] | list[str], counts: dict[str, int] | None = None) -> list[dict] | None:
    """Level A shares of the alternatives, four decimals; None if a form has no count or the total is zero."""
    counts = load_counts() if counts is None else counts
    if len(entities) < 2 or any(e not in counts for e in entities):
        return None
    total = sum(counts[e] for e in entities)
    if total == 0:
        return None
    return [{"entity": e, "count": counts[e], "total": total, "share": round(counts[e] / total, 4), "level": LEVEL}
            for e in entities]


def selftest() -> None:
    got = shares(("31", "31R"))
    assert got is not None and [(g["count"], g["total"], g["share"]) for g in got] == \
        [(9070, 11302, 0.8025), (2232, 11302, 0.1975)], got
    assert shares(("31", "no such form")) is None and shares(("31",)) is None
    three = shares(("24", "27", "33"))
    assert three is not None and abs(sum(g["share"] for g in three) - 1) < 0.001, three


def main() -> int:
    selftest()
    print("frequency shares: 31 or 31R gives 0.8025 / 0.1975 (level A)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
