# Changelog

All notable changes are recorded here. Each entry says **what** changed and **why**; the German *Warum* lines are the short rationale for the team.

## [0.13.1] - Decisions from Allard Mees (S4)

### Changed
- `REVIEW.md` shows Allard's answer under each of the 14 questions (`REVIEW_ANSWERS` in `py/docs_text.py`). *Warum:* Die Antworten vom 4. November stehen jetzt direkt bei den Fragen.
- `PRIMER.md`: decisions recorded in A4 (product logic, hybrid direct / "same stamp" model, weaker derivations, question mark, time ignored, best path, Actor merged, frequency method); S4 decided, S4a (frequency weights) and S4b (hybrid model) planned; open points listed for Memo 0.6.0.

## [0.13.0] - Chain pages: kiln coordinates and profile drawings

### Added
- `visuals/data/kilnsites-extra.csv`: coordinates of Kräherwald, Rheinzabern, Pfaffenhofen and Westerndorf (from `cat29.tblkilnsites`). The centre figures of chains A and B now have a modern and a Roman map.
- Profile drawings of the forms 24, 27, 31, 32 and 33 (`visuals/data/forms-src/`, traced into `forms.json`); the potform figures of the three chains show them instead of the placeholder. *Warum:* Die Platzhalter („no map yet“, „no profile drawing yet“) entfallen; die Ketten sind vollständig dargestellt.

### Changed
- Map window of the centre figures: it stays inside the data window (6° west to 13° east), so a centre in Raetia (Pfaffenhofen, Westerndorf) no longer gets an empty strip at the right edge. Maps whose window was inside the data window are unchanged.

## [0.12.1] - Chain pages: the carrier-centre statements get their figures

### Added
- **Chain pages**: a new part *Statements about the production centre of each carrier (InformationCarrier, hasProductionCentre)* with one figure per carrier (modern map, Roman map where all centres have coordinates). These are the statements that model M1 asserts on the carrier; before, only the actor statements (worksAt) and the potform statements were drawn, so the carrier-centre relation was missing on the page. The part with the derived degrees is now step 4. *Warum:* Die Beziehung InformationCarrier zu ProductionCentre fehlte auf den Chain-Seiten; sie ist die M1-Annahme, aus der die Ableitung startet.

## [0.12.0] - Chain pages: chain figure first, entities and statements in text; separated navigation

### Changed
- **Chain pages** start with the chain figure, then a text on the entities of the chain (counts per class and a table of class, entity and meaning), then the vague, uncertain and fuzzy-wobbly statements: a short reading of every pattern that occurs (`?`, OR, AND, AND with `?`) and a table with role, source string, FW type and weight written as `1/(? + possibilities)`. The statement figures and the table of derived degrees follow. *Warum:* Wer die Seite öffnet, soll zuerst die ganze Kette sehen und lesen, welche Entitäten und welche unscharfen Aussagen darin stecken.
- **Navigation**: one framed box with two bands; the *Documentation* band has a dark label and a dark bar, the *Visuals* band an accent-coloured label and bar, a rule between them. *Warum:* Dokumentation und Visuals sollen auf einen Blick getrennt sein.
- Model figures page: intro text without the matplotlib remark.

### Removed
- The dead links "docs version (matplotlib)" on the model figures page (`docs/diagrams/` no longer exists).

## [0.11.0] - One design for documentation and visuals, chain sub pages

### Added
- **Chain sub pages** `docs/visuals/chain-A.html`, `chain-B.html`, `chain-C.html` (`visuals/chain_pages.py`): for each chain of the CHNT data the vague, uncertain and fuzzy-wobbly statements first (potform of each carrier, centres of the potter, centres on a modern and a Roman map), then what the reasoning derives (chain figure, hextuple table, degrees under M1 and M2). The AMT reasoning use case end to end. *Warum:* Die drei Ketten enthalten alle Fälle von Vagheit, Unsicherheit und Fuzzy/Wobbly; sie zeigen den Reasoning-Fall von den Aussagen bis zum abgeleiteten Grad.
- Centres without coordinates in the export (Kräherwald, Rheinzabern, Pfaffenhofen, Westerndorf) get a figure without map; `visuals/sql/kilnsites-chains.sql` extracts them, `visuals/data/kilnsites-extra.csv` is read if present. Forms without profile drawing (24, 27, 31, 32, 33) show a placeholder.
- `py/site_kit.py`: the stylesheet (`docs/assets/site.css`), the navigation and the Jekyll layout, written by `main.py` (steps `visuals` and `docs`).

### Changed
- The **documentation pages** (Overview, Model, Vocabulary, Reasoning, Chains, Weights) have the design of the visuals pages: cream background, white cards, Fira Sans, accent `#9a3412`, one navigation with a *Documentation* and a *Visuals* row.
- The figures in the documentation are the visuals figures (`docs/visuals/img/model-*`), no longer the matplotlib ones.

### Removed
- `docs/diagrams/`, `py/step_diagrams.py`, `py/diagram_kit.py` and the step `diagrams`; matplotlib is no longer a requirement. *Warum:* Es gibt nur noch einen Stil; die Grafiken sind außerdem auf allen Plattformen gleich.

## [0.10.0] - Visuals pages in the layout of the GeoScience-FAIRification-LOD figure page, split by group

### Changed
- The pages of `docs/visuals/` take the layout of the figure page of `GeoScience-FAIRification-LOD`: cream background, one white card with a rim per figure, accent colour `#9a3412` for the figure label, a *Copy* button for the caption, credit line, PNG and SVG downloads. Fira Sans is shipped in `docs/visuals/fonts/` so the page looks the same on every machine.
- The case figures are separated into **Potform** (`potform.html`: PF.1 to PF.4), **Maps, modern** (`maps-modern.html`) and **Maps, Roman** (`maps-roman.html`); `index.html` is an overview with one card per group, `model.html` keeps the model figures. A navigation bar links the pages and the documentation. *Warum:* Die Fallgrafiken waren eine lange Liste; die Gruppen (Formen, moderne Karten, römische Karten) sollen getrennt auffindbar sein.
- `step_visuals` draws the model figures first, because the overview shows one of them.

## [0.9.3] - Review page no longer published

### Changed
- The **Review** page is removed from the GitHub Pages site (menu, overview table, links in Chains and Weights). The questions are now generated into `REVIEW.md` in the repository root, outside `docs/`, as an internal working note. The section "Open for the degree step" of the Weights page moved there as well. The status note and the site description say "working draft" instead of "draft for archaeological review". *Warum:* Die öffentliche Seite soll nur zeigen, was gesichert ist; offene Fragen bleiben im Repository für das Team.

## [0.9.2] - Numbered edges in the documentation figure

### Changed
- `docs/diagrams/02_full_semantics`: the numbers on the edges are circled (white, black rim) and explained in the note: position of the role in the chain, i.e. the order of the antecedents. `diagram_kit.arrow` has a new option `circled`. The figure is regenerated by `python main.py --only diagrams`; the patch contains the code only, because matplotlib versions render the five figures slightly differently. *Warum:* Die Zahlen waren unerklärt.

## [0.9.1] - Single chains, clearer arrows

### Added
- The three chains of figure 05 also as single figures `model-05a-chain-A`, `-05b-chain-B`, `-05c-chain-C` (own SVG and PNG, listed on `docs/visuals/model.html`). *Warum:* Eine Kette allein passt besser auf eine Folie oder in ein Paper.

### Changed
- Property labels in figures 01, 03 and 04 sit above (asserted) and below (inverse) their line instead of on it, so every arrowhead is visible; boxes are narrower for that.
- Figure 02: the numbers on the edges are circled and explained in the note (position of the role in the chain, i.e. the order of the antecedents); axiom labels sit above their lines.

## [0.9.0] - Model figures in the visuals style, visuals published with the docs

### Added
- **Model figures in the visuals style** (`visuals/model_figs.py`): the five figures of `docs/diagrams` (simple view, full semantics, toy reasoning, both directions, three chains) redrawn as SVG with Fira Sans and the semantic colours, read from the ontology and the reasoner as before. Page `docs/visuals/model.html`; each figure links to its matplotlib twin. *Warum:* Dieselben Inhalte sollen auch im Stil der Fallgrafiken vorliegen (Poster, Paper, Folien), neue Grafiken kommen dort leicht dazu.
- Menu entry **Visuals** in the documentation; every model figure page in the docs links to its visuals version.

### Changed
- The case figures and their page are now written to `docs/visuals/` (was `visuals/site/`), so GitHub Pages serves them: `.../visuals/index.html` (cases) and `.../visuals/model.html` (model). `visuals/site/` is removed.
- `docs/diagrams/` (matplotlib) is unchanged and remains the source of the figures in the documentation pages.
- `Fig` accepts a canvas size and a path colour (existing figures are byte-identical).

## [0.8.0] - Roman variant of the maps

### Added
- **Roman maps** `*-roman` for PC.1 to PC.4 and IC-PC.1 (14 figures in total): Roman provinces and names, major places with Latin names (DARE via `klokantech/roman-empire`), the Itiner-e road network (main, secondary, hypothetical), Latin river names (Liger, Sequana, Garumna, Rhodanus, Arar, Elaver, Mosella, Rhenus, Mosa, Matrona, Moenus, Nicer). `visuals/prepare_roman.py` builds `visuals/data/roman-gaul.json` (about 400 kB) from the two sources. *Warum:* Die Töpfereien liegen in römischen Provinzen; die moderne Karte zeigt, wo, die römische, in welchem Straßen- und Provinzgefüge.
- Province borders: shared edges are borders; an edge with one province only is kept when inland (the limes) and dropped along the coast.

### Changed
- Legend and credit line of the maps depend on the variant; the site page lists both variants.

## [0.7.0] - Frequency case PF.4, orientation layers on the maps

### Added
- **PF.4** (`visuals/`, figure `PF.4-frequency-bars`): the colour bars of the Samian Research website (`31 or 31R`, 9,070 and 2,232 of 11,302). It sets the equal share of the rule (0.50 / 0.50, `fw:EqualShareRule`) against the observed share (0.80 / 0.20). The method `fw:RelativeFrequency` is a **proposal**, not in the FW ontology; counts are in `visuals/data/shares.csv` and the build checks that they give the percentages the page shows. *Warum:* Manche OR-Aussagen haben empirische Anteile; das Modell soll zeigen, dass der Grad dann aus einer anderen Methode kommt.
- **Maps**: rivers (named: Loire, Seine, Garonne, Rhône, Saône, Allier, Moselle, Rhine, Meuse, Marne, Dordogne, Main, Neckar, Doubs), modern region borders and names (French régions, German states, Belgian regions), country borders and cities above 150,000 inhabitants, all Natural Earth; a legend; the map window is at least 6 degrees of latitude. *Warum:* Die Lage der Zentren war ohne Orientierung schwer zu erkennen.

### Changed
- `visuals/prepare_basemap.py` reads six Natural Earth files from a folder (see its docstring); `visuals/data/basemap-gaul.json` grew to about 160 kB.
- Note under the map figures wraps; nine figures instead of eight.

## [0.6.0] - Case figures for Potform and ProductionCentre

### Added
- **`visuals/`**: eight figures in the house pattern of the `*-visuals` folders (1750x1000, Fira Sans, SVG and PNG, caption page `visuals/site/index.html`), one per vagueness / uncertainty case: PF.1 (multiple OR), PF.2 (`A?`), PF.3 (`A or B?`), PC.1 (one OR), PC.2 (multiple AND), PC.3 (AND with `?`), PC.4 (`A?`) and IC-PC.1 (carrier to centre, `A?`). Weight, FW type and method of every statement come from `py/weights.py`; `check_cases()` stops the build if the rule no longer gives the pattern drawn. *Warum:* Die Fälle aus den SQL-Abfragen werden an echten Samian-Beispielen gezeigt, ohne dass Gewichte von Hand gesetzt sind.
- **Profile drawings** (Drag. 15/17, 18, 18/31 and the rim variants 15/17R, 18R, 18/31R, 31R) redrawn as vector paths by `visuals/trace_forms.py` from the supplied JPGs (`visuals/data/forms-src/`); result in `visuals/data/forms.json`.
- **Maps** for the centre cases: Natural Earth coastline (`visuals/prepare_basemap.py`, public domain) and the 36 Gaulish kiln sites with Wikidata IDs (`visuals/data/kilnsites-gaul.csv`). A marker with `?` is drawn hollow and dashed.
- `visuals/data/cases.csv`: the example strings and carriers (extract of the CHNT exports, with the number of rows per query).
- Step `visuals` in `main.py`; `resvg-py` and `pillow` in `requirements.txt`.

## [0.5.0] - fw:Certainty for certain statements

The engine and the FW ontology have a fourth type, `fw:Certainty` (engine step S25, FW ontology 2026-11-03): a certain statement is not fuzzy at all and has weight 1.0. The Mini-AMT uses it instead of leaving the type out.

### Changed
- **Certain statements** (one entity, no `?`, no AND, no OR; weight 1.0) get the pattern type `fw:Certainty` in `py/weights.py` (`FW_TYPE["certain"]`). Before, no `fw:hasType` was written and AMT read that as `fw:Vagueness`. *Warum:* Eine sichere Aussage ist weder vage noch unsicher; mit dem eigenen Typ ist sie von „Typ nicht angegeben“ zu unterscheiden und rechnet im Reasoning richtig (Beschluss 2026-11-03, FW-Ontologie und Engine).
- **`createdBy` in model M2** (crisp, weight 1.0) is a certain statement as well and carries `fw:hasType fw:Certainty`, in the reference reasoner and in the engine input. A chain `createdBy` o `worksAt` therefore takes the type of `worksAt` (before: vagueness next to `fw:Uncertainty` gave `fw:FuzzinessWobbliness`).
- **Type of derived edges** in `py/reference_reasoner.py` as in the engine: `fw:Certainty` adds no fuzziness; it is left out as soon as another type is present, a chain of certain edges stays certain.
- `data/weight-cases.csv`: the certain case expects `Certainty`. Pages *Weights* (type table, pattern `certain`, derived statements) and figure 05 (tag `C`) say so; `README.md`; the optional engine line in `requirements.txt` names the engine commit `ce23c5c`.
- The cross-check with the engine is skipped, with a message, if the installed engine does not know `fw:Certainty`.

### Checked
- 340 edges of the three runs agree with AMT.engine (commit `ce23c5c`) in weight, type and method; the 17 weight cases agree; the round trip reads 20 statements back.

## [0.4.0] - FW terms, evidence, check against AMT.engine 0.6.0

The hextuples use the terms the FW ontology fixed on 2026-10-30 (`caa-datadragons/FW_Ontology`, `15ae05f`); the proposals `amt:type`, `amt:method` and `nfdi_fw:ReciprocalPossibilityWeight` are gone. AMT.engine 0.6.0 reads the result.

### Added
- **Source string as evidence**: every statement points with `fw:derivedFrom` to a `fw:TextEvidence` node holding the string (`fw:sourceString`). The statements of one string share the node. *Warum:* Die Zeichenkette bleibt exakt erhalten (Reihenfolge, Schreibweise); die Rekonstruktion aus Gewicht und Typ ist nur noch die Gegenprobe.
- **Round-trip check** in step `chains`: `dist/chains.ttl` is read back; every statement must lead to its string, and weight, type and method must be the ones the rule gives.
- **Check against AMT.engine 0.6.0** in step `chains`: the three runs (M1 product, M1 Goedel, M2 product) are repeated with the engine and compared edge by edge, type and method included (340 edges agree). It needs 0.6.0 or newer and is skipped with a note otherwise. The SHACL shapes of the engine are run as information: M2 conforms, M1 has four violations (`mini:reaches` and `mini:reachedBy` have no `rdfs:domain` and `rdfs:range`; open, see PRIMER).
- **`dist/chains-with-model.ttl`**: ontology M1 and the data in one file for the AMT runner and the Explorer.
- **Type and method of derived edges** in `py/reference_reasoner.py`, written from the rules of AMT.engine 0.6.0: a role chain gives its logic as method and the common type of its antecedents (`fw:FuzzinessWobbliness` if they differ); an inverse or a subsumption takes the type and has no method; a missing type counts as `fw:Vagueness`.
- Two cases from the FW ontology in `data/weight-cases.csv` (`Lezoux or Vichy ?` = 0.33, `South Gaul?` = 0.5); 17 cases.
- `ontology/fw-implemented-by.ttl`: the triple `fw:EqualShareRule fw:implementedBy <py/weights.py>` that the FW ontology still lacks.

### Changed
- `dist/chains.ttl` writes `fw:hasDegreeOfConnection` (the same as `amt:weight`), `fw:hasType` with the individuals `fw:Uncertainty`, `fw:Vagueness`, `fw:FuzzinessWobbliness`, and `fw:hasMethod fw:EqualShareRule`. A certain statement has no type; AMT reads that as `fw:Vagueness`. *Warum:* So nennt die FW-Ontologie die Begriffe; Karstens AFE-Daten und Mini-AMT sprechen jetzt dieselbe Sprache.
- The type of AND and OR strings is `fw:Vagueness` (was `VagueValue`), of `?` strings `fw:Uncertainty` (was `UncertainValue`), of both `fw:FuzzinessWobbliness`. Which pattern gives which type is unchanged.
- Pages *Weights* and *Chains*, figure 05, `README.md`, `requirements.txt` (the optional engine line points to `alpaca-fair-framework/amt-engine`, tag `v0.6.0`).

### Removed
- `ontology/fw-method-draft.ttl`: the FW ontology has `fw:EqualShareRule`.

## [0.3.0] - Weight rule, hextuple, three real chains

### Added
- **`py/weights.py`**: the weight rule of the source paper, `1 / (n_questionmark + n_possibilities)`, with the FW type (`UncertainValue`, `VagueValue`, `FuzzinessWobblinessValue`) per pattern and relation, and a lossless round trip from edges back to the string. 15 cases in `data/weight-cases.csv`. *Warum:* Die Berechnung ist klar und soll ausführbar festgehalten sein, auch für den späteren Roundtrip mit den AFE-Daten.
- **Hextuple**: every weighted statement carries `amt:type` and `amt:method` besides the four elements of the quadruple (proposal). `ontology/fw-method-draft.ttl` is the draft of the method resource for the FW ontology.
- **Step `chains`**: three real chains from the CHNT data (`data/chains-source.csv`) as hextuples in `dist/chains.ttl`, reasoned under M1 with product and Goedel and under the new model M2 (`ontology/variant-b-derived.ttl`, carrier-centre derived from the actor). The exported centre weights are checked against the rule. *Warum:* Das Modell zeigt jetzt an echten Fällen, was es ableitet, und macht die Doppelzählung bei geerbten Aussagen sichtbar.
- **Docs**: page *Chains*, sections *How the weight is computed* and *From quadruple to hextuple* on the Weights page, figure `05_chains`, seven new review questions (8 to 14).

### Changed
- `amt:logic` of the three role chains is `amt:ProductLogic` (was the placeholder `amt:GoedelLogic`), as in the role-chain axioms of the source paper. *Warum:* Das Paper nutzt ProductLogic; Gödel bleibt als Vergleich im Chains-Lauf.
- The weight conventions on the Weights page now follow the rule (AND keeps the full weight, OR shares it, a question mark counts as one more possibility); the earlier recommendation of un-normalised alternatives is replaced.

## [0.2.0] - Reasoning properties described, inverses for the derived roles, documentation

### Added
- **Inverses of the derived roles** in `ontology/mini-amt.ttl`: `centreToPotform`, `actorToCarrier`, `actorToPotform` and `reachedBy`, each with an `amt:InverseAxiom`. *Warum:* Eine Assoziation muss von beiden Enden fragbar sein ("welche Zentren gehören zu dieser Potform?" und umgekehrt).
- **`skos:definition` and `skos:scopeNote` on every role.** The definition says what the role says, the scope note what it does not say. *Warum:* Allard soll die Rollen archäologisch lesen und beurteilen können; die Grenzen (Assoziation statt Urheberschaft, keine Zeit) stehen direkt an der Rolle.
- **`docs/`** for GitHub Pages in the pattern of QSKOS: `index`, `model`, `vocabulary`, `reasoning`, `weights`, `review`. Generated by `py/step_docs.py` from the ontology and the reasoning, prose in `py/docs_text.py`. *Warum:* Tabellen und Ableitungen können nicht vom Modell abweichen.
- **Weights page** answering whether `amt:weight` is the same in both directions (yes for inverses; shares and normalised alternatives are directional). *Warum:* Das ist die Grundlage für den späteren Degree-Schritt.
- **Review page** with the archaeological questions that decide the model.
- **Figure `04_reasoning_both`**: the derived roles in both directions.

### Changed
- Figures are written to `docs/diagrams/` instead of `img/`. Figure 02 shows the derived inverses.
- The `reason` step now derives 15 edges on the toy chain (was 9): the four new inverses add six.

## [0.1.0] - First model

- Ontology in the AMT vocabulary: four concepts, three asserted roles with inverses, three role chains, subsumption under `reaches`.
- Toy chain, reference reasoner with optional cross-check against the AMT engine, three figures drawn by Python.
