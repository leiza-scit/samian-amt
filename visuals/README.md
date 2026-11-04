# Case figures: Potform and ProductionCentre

Fourteen figures for the vagueness / uncertainty patterns of the Mini-AMT, each with a real example from the Samian
Research database, plus the five model figures (`model_figs.py`, same content as `docs/diagrams`, in the same style).
Everything is generated into `docs/visuals/` (pages `index.html` (overview), `potform.html`, `maps-modern.html`, `maps-roman.html`, `chain-A/B/C.html` and `model.html`, images in `img/`; stylesheet and fonts in `docs/assets/`, written by `py/site_kit.py`) and so is published with the
GitHub Pages site (menu entry *Visuals*). The matplotlib figures in `docs/diagrams/` stay the figures of the documentation pages.

    pip install -r requirements.txt
    python main.py --only visuals

| Figure | Relation | Pattern | FW type | Example |
|---|---|---|---|---|
| PF.1 | informationcarrier--potform | `A or B or C` | Vagueness | Secundus v, `15/17 or 18 or 18/31` |
| PF.2 | informationcarrier--potform | `A?` | Uncertainty | Onnio-, `18/31?` |
| PF.3 | informationcarrier--potform | `A or B?` | FuzzinessWobbliness | Secundus ii, `15/17 or 18 (R?)` |
| PF.4 | informationcarrier--potform | `A or B` with observed shares | Vagueness | `31 or 31R`: 80.25 % / 19.75 % (proposal: `fw:RelativeFrequency`) |
| PC.1 | actor--productioncentre | `A or B` | Vagueness | Sem- i, `Aspiran or Saint-Saturnin` |
| PC.2 | actor--productioncentre | `A and B` | Vagueness | Regulus i, `Lezoux and Toulon-sur-Allier` |
| PC.3 | actor--productioncentre | `A and B and C?` | FuzzinessWobbliness | Paternus v |
| PC.4 | actor--productioncentre | `A?` | Uncertainty | Gongius, `Lezoux?` |
| IC-PC.1 | informationcarrier--productioncentre | `A?` | Uncertainty | Maia-, `Lezoux?` |

Weights come from `py/weights.py`. Colours follow the semantic scheme (instance grey, real object green, term purple,
OWL white, property metadata amber). SVGs name Fira Sans without embedding it; use the PNG or install the font.

`trace_forms.py` and `prepare_basemap.py` are one-off scripts (they need scikit-image); their results are committed.
The profile drawings are the supplied JPGs, redrawn; their source and licence are still to be stated here.
Coast, rivers, regions, borders, cities: Natural Earth, public domain (modern, not Roman). Fonts: Fira Sans, SIL OFL 1.1, see `fonts/`. Figures: CC BY 4.0. Code: MIT.

## Roman maps

Each map figure (PC.1 to PC.4, IC-PC.1) exists twice: with modern layers and, as `*-roman`, with Roman ones. The Roman map shows
provinces and major places from the Digital Atlas of the Roman Empire (DARE, taken from `klokantech/roman-empire`), the roads of
Itiner-e (de Soto et al. 2025, *Scientific Data* 12:1731, <https://doi.org/10.1038/s41597-025-06140-z>; dataset
<https://doi.org/10.5281/zenodo.17122148>, CC BY 4.0; main roads solid, secondary roads thin, hypothetical segments dotted) and
Latin names of the larger rivers. `prepare_roman.py` builds `data/roman-gaul.json` from the two sources. The DARE layers carry the
licence of DARE, still to be checked and stated here.

## Chain pages

`chain_pages.py` builds one page per chain of `data/chains-source.csv` (A, B, C): the asserted statements first (potform of each carrier,
centres of the potter, as figures in the case style, centres on a modern and a Roman map), then the derived degrees (chain figure, table of
the hextuples, table of the degrees under M1 and M2). Centres without coordinates in `data/kilnsites-gaul.csv` (Kräherwald, Rheinzabern,
Pfaffenhofen, Westerndorf) get a figure without map until `data/kilnsites-extra.csv` exists (query: `sql/kilnsites-chains.sql`); forms without
profile drawing (24, 27, 31, 32, 33) show a placeholder.
