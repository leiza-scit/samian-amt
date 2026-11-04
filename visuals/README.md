# Case figures: Potform and ProductionCentre

Eight figures for the vagueness / uncertainty patterns of the Mini-AMT, each with a real example from the Samian
Research database. Everything under `site/` is generated.

    pip install -r requirements.txt
    python main.py --only visuals

| Figure | Relation | Pattern | FW type | Example |
|---|---|---|---|---|
| PF.1 | informationcarrier--potform | `A or B or C` | Vagueness | Secundus v, `15/17 or 18 or 18/31` |
| PF.2 | informationcarrier--potform | `A?` | Uncertainty | Onnio-, `18/31?` |
| PF.3 | informationcarrier--potform | `A or B?` | FuzzinessWobbliness | Secundus ii, `15/17 or 18 (R?)` |
| PC.1 | actor--productioncentre | `A or B` | Vagueness | Sem- i, `Aspiran or Saint-Saturnin` |
| PC.2 | actor--productioncentre | `A and B` | Vagueness | Regulus i, `Lezoux and Toulon-sur-Allier` |
| PC.3 | actor--productioncentre | `A and B and C?` | FuzzinessWobbliness | Paternus v |
| PC.4 | actor--productioncentre | `A?` | Uncertainty | Gongius, `Lezoux?` |
| IC-PC.1 | informationcarrier--productioncentre | `A?` | Uncertainty | Maia-, `Lezoux?` |

Weights come from `py/weights.py`. Colours follow the semantic scheme (instance grey, real object green, term purple,
OWL white, property metadata amber). SVGs name Fira Sans without embedding it; use the PNG or install the font.

`trace_forms.py` and `prepare_basemap.py` are one-off scripts (they need scikit-image); their results are committed.
The profile drawings are the supplied JPGs, redrawn; their source and licence are still to be stated here.
Coastline: Natural Earth, public domain. Fonts: Fira Sans, SIL OFL 1.1, see `fonts/`. Figures: CC BY 4.0. Code: MIT.
