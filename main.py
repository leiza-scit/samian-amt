"""mini-amt - the single entry point.

    python main.py                 all steps, in order
    python main.py --list          print the steps and exit
    python main.py --only reason   one step
    python main.py --dry-run       print the plan, run nothing

Every step is also runnable on its own (python py/step_reason.py).
"""
from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "py"))

STEPS = [
    ("weights",  "weights",       "the weight rule of the source paper: self-test of data/weight-cases.csv -> dist/"),
    ("reason",   "step_reason",   "reasoning on the toy chain -> dist/ (cross-checks the AMT engine if installed)"),
    ("chains",   "step_chains",   "three real chains as hextuples, reasoning of the models M1 and M2 -> dist/"),
    ("visuals", "step_visuals",  "case figures and model figures in the visuals style -> docs/visuals/ (SVG + PNG + 2 HTML pages)"),
    ("docs",     "step_docs",     "GitHub Pages documentation -> docs/ (generated from ontology, reasoning, figures); also the stylesheet and layout"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print the steps and exit")
    ap.add_argument("--only", choices=[s[0] for s in STEPS], help="run one step")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    args = ap.parse_args()

    plan = [s for s in STEPS if args.only in (None, s[0])]
    if args.list or args.dry_run:
        for name, module, text in plan:
            print(f"{name:10s} {module}.py  {text}")
        return 0

    timings = []
    for name, module, _ in plan:
        print(f"== {name}")
        t0 = time.perf_counter()
        rc = importlib.import_module(module).main()      # lazy: --list needs neither rdflib nor resvg
        timings.append((name, time.perf_counter() - t0))
        if rc:
            print(f"step {name} failed (exit {rc})")
            return rc
    total = sum(t for _, t in timings)
    for name, t in timings:
        print(f"{name:10s} {t:6.2f} s  {100 * t / total:3.0f} %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
