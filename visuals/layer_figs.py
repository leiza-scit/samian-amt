"""Figure of the common modelling layer: the systems, one shared layer in between, the tools written once on top.

layer-01-common-layer   System A, System B and further systems each have a crosswalk to one common modelling layer; in the layer
                        every statement has the same five parts (subject, property, object, weight, type), the weight and the
                        type come from AMT and the FW ontology; reasoning, validation and exploration read the layer, not the
                        systems, so they are written once and serve every system.

The figure is generic on purpose: no example data, no system names. The caption of the page or the paper says which systems
(Samian Research and the AFE) are meant. No header and no footer text in the figure.
"""
from __future__ import annotations

import build as B
from build import INST, MUTED, PROP, REAL, Fig

W, H = 1750, 880
ACCENT = "#9a3412"
X0, STEP, BW = 60, 565, 500      # three columns of 500 with 65 gap


def main():
    f = Fig("layer-01-common-layer", "A common modelling layer between several systems and the tools that are written once", W, H)

    # --- tools, written once (top)
    tools = [("Reasoning", "AMT engine: role chains and weights"),
             ("Validation", "SHACL shapes on the statements"),
             ("Exploration", "AMT Explorer: the inferred edges")]
    for i, (t, s) in enumerate(tools):
        x = X0 + i * STEP
        f.box(x, 50, BW, 110, t, s, REAL, 28, 19)
        f.path(f"M{x + BW / 2},162 L{x + BW / 2},248")
        f.chip(x + BW / 2, 205, "reads", 19)

    # --- the common layer (middle)
    f.rect(60, 250, 1630, 270, "#ffffff", ACCENT, 10, 3)
    f.text(90, 288, "Common modelling layer", 30, True, ACCENT, "start")
    y = 385
    f.box(395, y - 34, 300, 68, "subject", None, INST, 26)
    f.path(f"M695,{y} L1053,{y}")
    f.chip(875, y, "property", 22, "middle", True)
    f.box(1055, y - 34, 300, 68, "object", None, INST, 26)
    # weight and type belong to the statement: hung under the property, joined to the arrow
    f.raw(f'<path d="M875,{y + 17} L875,{y + 42} M815,{y + 42} L935,{y + 42} M815,{y + 42} L815,{y + 54} M935,{y + 42} L935,{y + 54}" fill="none" stroke="{B.LINE}" stroke-width="1.6"/>')
    f.chip(815, y + 70, "weight", 22, "middle", True)
    f.chip(935, y + 70, "type", 22, "middle", True)
    f.text(875, 488, "one shape for every system: five parts, nothing else", 19, False, MUTED)

    # --- source systems (bottom), two crosswalk arrows each
    systems = [("System A", "own data model", "own crosswalk to the layer", False),
               ("System B", "own data model", "own crosswalk to the layer", False),
               ("System n", "any further source", "own crosswalk to the layer", True)]
    ytop, yarrow = 650, 648
    for i, (t, l1, l2, dashed) in enumerate(systems):
        x = X0 + i * STEP
        cx = x + BW / 2
        f.rect(x, ytop, BW, 130, INST[0], INST[1], 6, 2.4 if dashed else 1, dashed)
        f.text(cx, ytop + 32, t, 26, True, INST[2], "middle", BW - 14)
        f.text(cx, ytop + 71, l1, 19, False, INST[2], "middle", BW - 14)
        f.text(cx, ytop + 100, l2, 19, False, MUTED, "middle", BW - 14)
        ds = ' stroke-dasharray="7 6"' if dashed else ""
        for dx, a, b, label in ((-75, yarrow, 522, "to layer"), (75, 522, yarrow, "from layer")):
            f.raw(f'<path d="M{cx + dx},{a} L{cx + dx},{b}" fill="none" stroke="{B.LINE}" stroke-width="1.6"{ds} marker-end="url(#a)"/>')
            f.chip(cx + dx, (a + b) / 2, label, 19)

    f.legend(840, [(REAL, "tool, written once"), (INST, "system, statement part"), (PROP, "property, weight, type")])
    f.save()
    print("1 common-layer figure ->", B.IMG)


if __name__ == "__main__":
    main()
