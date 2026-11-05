# Changelog

All notable changes are recorded here. Each entry says **what** changed and **why**; the German *Warum* lines are the short rationale for the team.

## [0.20.0] - Mini round trip (Samian and coins), 16048 as UncertainResourceValue, parallel statements tested

### Added
- **Mini round trip** (step `mini-roundtrip`, `py/step_mini_roundtrip.py`): the smallest round trip with one relation on each side and four kinds of statement (certain, uncertain, vague, vague and uncertain), five parts per statement (subject, property, object, weight, type; no method, no evidence). Samian side: information carrier -> potform (PF.1, PF.2, PF.3 of the visuals plus one certain case, built with the weight rule of `py/weights.py`); coin side: coin -> `nmo:hasAuthority` (coins 15668, 16048, 15661, 12324). Both sides must come back the same; the coins also go through the AMT engine 0.7.0. *Warum:* Karsten wollte bremsen: eine Relation, vier Fälle, fünf Teile; so sieht man, ob Roundtrip auf beiden Seiten mit denselben Mitteln funktioniert.
- `data/afe/afe-mini-coins.ttl` (the four coins, AFE container pattern) and `data/afe/amt-parallel-statements.ttl` (one coin, two parallel statements on `nmo:hasAuthority`, weights 0.3 and 0.8, agents M65 and M66 via `fw:derivedFrom`).
- Test of parallel statements in the engine: both edges and both agents survive, `prov:wasAttributedTo` on the statement is dropped; the way back (`queries/coins/amt-to-afe.rq`) merges the two into one container. The step checks that this limit is still there and fails when it is gone, so that page and PRIMER get updated. *Warum:* Karsten plant parallele Aussagen mit `prov:wasAttributedTo`; die Engine kann das, die Rückrichtung braucht später einen Gruppierungsschlüssel (`fw:derivedFrom`).
- Documentation page **Mini round trip** (docs/mini-roundtrip.md), first in the category Roundtrip, with two figures (`mini-01-cases`, `mini-02-form`; invented schematic sherds with a potter's stamp and invented coins, real images wait for Allard and Karsten) and the commands to run it step by step (Windows cmd).
- Written to `dist/`: `mini-potform-{amt,afe,back}.ttl`, `mini-coins-{amt,back}.ttl`, `mini-roundtrip-report.md`; Turtle is canonical.

### Changed
- Coin 16048 and the constructed coin 80001 now use `fw:UncertainResourceValue` (before: the top class `fw:UncertainValue`). *Warum:* Karstens Antwort vom 2026-11-05; damit kommen alle fünf Münzen der AFE gleich zurück, nur die Randfälle 90001 und 90004 bleiben verlustbehaftet.
- Page **AFE round trip**: result, "what is lost" and the open points updated with Karsten's answers of 2026-11-05 (`nm:uncertain_value` means not determinable because of a condition, a missing value is not unknown, `fw:sourceString` does not fit the AFE).

## [0.19.0] - Round trip AFE -> AMT -> AFE (package version 3), engine 0.7.0

### Added
- **Round trip AFE -> AMT -> AFE** (step `afe-roundtrip`, `py/step_afe_roundtrip.py`) on the coin data of the AFE, state of Karsten Tolle's package version 3 (2026-11-03; his answers are still open). Four forms of an AFE value (container with members, one uncertain value, certain value, unknown) become hextuples with `fw:hasMethod fw:AFEAssignment` and come back; each coin is compared with the original as a graph (numbers by value, `...Value` = `...ResourceValue` on the top class). *Warum:* Der Stand von Karstens Paket läuft damit schon im Repository und wird iterativ angepasst, sobald seine Antworten da sind.
- `data/afe/`: `afe-all-cases.ttl` (five coins as sent), `afe-edge-cases.ttl` (constructed 90001 to 90004, cases A to D of the memo, expected outcome is part of the test), `afe-denomination-mint-test.ttl` (constructed 80001 to 80003; `nmo:hasDenomination` and `nmo:hasMint` are assumed names).
- `queries/coins/afe-to-amt.rq` and `queries/coins/amt-to-afe.rq` (content as in the package, comments in English).
- If the AMT engine 0.7.0 or newer is installed, the first file also goes through the engine (reasoning) before the way back; the result must be the same.
- Documentation page **AFE round trip** (docs/afe-roundtrip.md) in the category Roundtrip, with two figures (`afe-roundtrip-01-flow`, `afe-roundtrip-02-cases`), results, edge cases, what is lost, the open questions to Karsten and both queries in full.
- Written to `dist/`: `afe-<name>-as-amt.ttl`, `afe-<name>-back.ttl`, `afe-roundtrip-report.md`, `afe-engine-all-cases/`; Turtle is canonical, two runs give identical files.

### Changed
- `requirements.txt`: the AMT engine is now an active requirement at the release `v0.7.0` (before: a commented line naming a commit). *Warum:* Seit dem Release 0.7.0 kennt die Engine `fw:Certainty`; auf Windows mit Python 3.10 sind Roundtrip-Engine-Prüfung und SHACL für M1 und M2 damit bestätigt.

## [0.18.0] - Round trip AMT -> AFE -> AMT, SHACL of M1 solved

### Added
- **Round trip AMT -> AFE -> AMT** (step `roundtrip`, `py/step_roundtrip.py`): the hextuples of the three chains are written as the container pattern of the AFE coin data (`queries/amt-to-afe.rq`) and read back (`queries/afe-to-amt.rq`), mirroring Karsten Tolle's AFE -> AMT -> AFE. The AFE form follows from `fw:hasType` and the weight alone (certain: direct value; `?`: one `fw:UncertainResourceValue`; OR: one `skos:Collection` with a member per entity; AND: one container per entity). The AFE side is a rebuilt pattern with `sam:` predicates, not AFE data. *Warum:* Der Roundtrip zeigt, dass AMT-Hextupel und AFE-Container dieselbe Information tragen, ohne dass der Quell-String mitgeführt werden muss.
- Two tests, both part of `python main.py`: (a) subject, predicate, object, weight, FW type and nodes of 20 hextuples of the chains and 36 hextuples of the 18 cases of `data/weight-cases.csv` (all six patterns) come back unchanged; (b) the three reasoning runs on the returned statements give the same 340 edges; the AMT engine, if installed, agrees on the returned graph and the SHACL shapes conform.
- Written to `dist/`: `chains-afe.ttl`, `chains-back.ttl`, `chains-back-with-model.ttl`, `patterns-afe.ttl`, `patterns-back.ttl`, `roundtrip-report.md`; Turtle is canonical (blank nodes named by content), so two runs give identical files.
- Documentation page **Round trip** (docs/roundtrip.md) with three figures (`roundtrip-01-flow`, `-02-patterns`, `-03-balance`), the rules, an explanation of SPARQL `CONSTRUCT` with a worked example for carrier 211974, the generated AFE Turtle, the lost information and both queries in full.
- Helper concept `sam:Entity` (see Changed).
- Navigation: new category **Roundtrip** (between Documentation and Visuals), for this page now and for Karsten's use case and AFE -> AMT -> AFE later.

### Changed
- **SHACL of M1:** `sam:reaches` and `sam:reachedBy` now have `rdfs:domain` and `rdfs:range` `sam:Entity`, a helper concept that is only domain and range of the two generic roles (no individual is an instance). The engine shapes (exactly one domain and one range per role) now report no violation for M1 and M2 (before: 4). *Warum:* Ohne Domain und Range brach der Runner bei M1 ab; das Oberconcept löst es im Modell, die Engine bleibt unverändert.
- `py/step_chains.py`: `engine_check` takes a file-name prefix, so the check of the returned graph does not overwrite the engine inputs of the chains.
- Not carried by the AFE pattern, documented and counted: source strings (`fw:TextEvidence`), `fw:hasMethod` (comes back as `fw:AFEAssignment`), frequency shares, `sam:attributedTo`.

## [0.17.1] - Explorer: quieter picture

### Added
- **Labels on selection** (new default of the label button): the lines carry no text until a node or a line is clicked; then the lines of the selection show role and weight. The other modes (names and weights, weights, off) stay. *Warum:* In Kette A lagen die Beschriftungen der gestrichelten Bögen übereinander und verdeckten die Knoten.
- Legend switch **show the inferred lines only** (link parameter `only=inferred`; switches reasoning on if it is off).
- **Dragged nodes are kept in the link** (`pos=x,y;x,y;...`, one pair per node); a link opens the picture as it was arranged. PNG and SVG export what is shown. After a drag, selecting or relabelling no longer throws the nodes back (vis.js lays a hierarchical graph out again on every data change).
- `docs/explorer/assets/img/mainzed.png`: the logo of mainzed.

### Changed
- The legend names only the concept (Potform, InformationCarrier, ProductionCentre, Actor) and is narrower; the plain-language gloss ("vessel form", "kiln site", ...) stays in the details panel (before: "Potform (vessel form (type))" with a double bracket, now "Potform – vessel form").

### Removed
- The note that `mainzed.png` is missing (see 0.17.0).

## [0.17.0] - Explorer: header, legend, details, Cypher, readable reasoning

### Added
- **Cypher dialog** (icon `</>` in the bar): the graph as shown, for Neo4j 5 (one `MERGE` statement per node and per relationship, constraints on `id`; relationship properties `weight`, `role`, `fwType`, `method`, `inferred`, `source`). Copy or download as `.cypher`.
- **Details panel** (icon in the bar, opens by itself on a click): weight, status (asserted or inferred, with the axiom), FW type, method and the source string of a clicked line; IRI and edge count of a clicked node. The neighbourhood of the selection stays in colour, the rest fades.
- **Legend** (bottom right, foldable; folded by itself on a small window): what the node colours mean (Potform, InformationCarrier, ProductionCentre, Actor = potter) and the lines; a switch for the generic role `reaches`.
- **About panel** (icon in the bar) with the logos of LEIZA, mainzed and NFDI4Objects and the funding note; **full screen** button; **PNG**, **SVG** and **link** (`?ttl=...&reasoning=on&labels=...`) buttons; label mode (names and weights, weights, none).
- `amt.js` reads the source string of a statement (`fw:derivedFrom` to `fw:sourceString`).

### Changed
- Header: the AMT penguin at the top left, the title is fixed: "Samian Research - AMT Explorer" (before: the chain title). Turtle, Cypher, PNG, SVG, link are icons.
- **Layout**: the nodes sit in columns in the direction of the chain (Potform, InformationCarrier, ProductionCentre, Actor); inferred lines that skip a column are dashed arcs above or below; line width follows the weight (1 to 3 px). *Warum:* Mit Reasoning war der Graph ein Knäuel; jetzt liegen behauptete Kanten in der Mitte und abgeleitete außen.
- The generic role `reaches` is hidden by default (legend switch). *Warum:* Sie wiederholt `potformToCentre`, `potformToActor` und `carrierToActor` und verdoppelt die Linien.
- Edge labels carry the role name without a prefix (the CURIE `sam:hasType` is in the details panel and in the Turtle file).
- The Turtle download uses the prefix `sam:` instead of `ex:`.

### Removed
- The status "consistent" in the header; only a warning appears if the reasoner finds a violation. *Warum:* Es sagte nur, dass die Domain- und Range-Prüfung nichts fand, und lenkte vom Bild ab.

### Note
- `docs/explorer/assets/img/mainzed.png` is not in the repository (the logo could not be fetched); until it is added the page shows the word "mainzed".

## [0.16.0] - Renamed to samian-amt

### Changed
- The repository is `leiza-scit/samian-amt` (before: `CHNT2026-amt`, working name "Mini-AMT"). Links, texts, README, PRIMER and the figures say `samian-amt`; "CHNT data" is "Samian Research data". *Warum:* Der Name sollte zum Projekt passen, nicht zur Konferenz.
- Namespace `http://example.org/samian-amt/` with the prefix `sam:` (before `mini:`), still a placeholder for a persistent IRI. The Turtle files, the hextuples (`sam:frequencyShare` and the other `sam:` terms) and the Explorer data follow.
- Files renamed: `ontology/mini-amt.ttl` is now `ontology/samian-amt.ttl`, `py/mini_amt_utils.py` is now `py/samian_amt_utils.py`; `dist/mini-amt-with-toy.ttl` is now `dist/samian-amt-with-toy.ttl` (generated, not tracked). The entries below 0.16.0 keep the old names; they describe the state at that time.

## [0.15.0] - AMT Explorer with the three chains

### Added
- `docs/explorer/`: the Explorer of [amt-engine](https://github.com/alpaca-fair-framework/amt-engine) (client-side JavaScript: N3, vis.js, the JavaScript reasoner), adapted for the Mini-AMT: new header (Mini-AMT, LEIZA and NFDI4Objects, credit to the AMT engine), only Chain A, B and C to choose from, no example list and no file upload, local paths. Libraries are copied to `docs/explorer/vendor/` (nothing from a CDN); licences stay with them.
- Step `explorer` (`py/step_explorer.py`): writes `docs/explorer/data/chain-A.ttl`, `chain-B.ttl`, `chain-C.ttl` (model M1 plus the hextuples of one chain, including the frequency shares as extra information) and `examples.json`.
- Menu group "Explorer" (Chain A, B, C) on all pages; Explorer row on the start page.

### Changed
- **The Explorer shows reasoning in one direction only** (Flo, 2026-11-04): edges of the inverse roles are hidden in the picture; the downloaded Turtle keeps them. *Warum:* Mit beiden Richtungen war der Graph unlesbar.

### Checked
- Headless Chromium: the three chains load, reasoning on and off works, no failed request; the weights of all 128 edges derived in the browser equal those of `py/reference_reasoner.py`.

## [0.14.0] - Question mark halves the weight; frequency shares as additional information

### Changed
- **Weight rule** (`py/weights.py`): `weight = (1 / n_possibilities) * (1/2 if "?" else 1)`, decided with Allard Mees on 2026-11-04 (Memos 0.7.0 and 0.8.0). It replaces the rule of the source paper, which counted the question mark as one more possibility. Only OR with a question mark changes: `A or B?` is 0.25 (was 0.33), `A or B or C?` 0.17 (was 0.25). `A?`, `A and B?` (0.5), `A and B` and `A or B` keep their weights. The method stays `fw:EqualShareRule`. *Warum:* Allard: Die alte Regel war „der falsche Ansatz“; das Fragezeichen schwächt alle Alternativen gleichmäßig ab.
- Test cases (`data/weight-cases.csv`), the *Weights* and *Review* pages, the chain pages, the figures PF.3 and PF.4 and the README follow the new rule. The round trip rebuilds the pattern from weight, type and number of edges as before (checked for 2 to 50 edges).
- PF.4: the degree stays the equal share (`fw:hasDegreeOfConnection 0.50`); the frequency share is shown as `mini:frequencyShare`, no longer as the degree. *Warum:* Die Häufigkeitsanteile sind ein Hinweis für den Archäologen, kein Wahrheitsgrad.

### Added
- `py/frequency.py` and `data/form-counts.csv` (extract of Allard Mees's `data-1793809985134.csv`, forms with at least ten vessels): level-A shares of the alternatives of an OR (`31 or 31R` = 0.8025 / 0.1975). Written beside the hextuples in `dist/chains.ttl` (`mini:frequencyShare`, `-Count`, `-Total`, `-Level`, `-Method`) for the potform statements with OR (chain C and the self-test); not a weight, not part of the chain, unchanged by a question mark. Round trip and self-test check the shares.
- PRIMER A4: weight rule, frequency shares; S4a delivered; S4b put on hold.

### Fixed
- `visuals/build.py`: the check of the listed patterns also ran over the cases the chain pages register and stopped with `A.4: pattern not expected for informationcarrier--productioncentre`; only the nine fixed cases are checked now. *Warum:* Der Lauf `python main.py` brach in der Stufe visuals ab, die Stufe docs lief nicht mehr.

## [0.13.2] - Fix: case figures were no longer rebuilt; PC.1 with Saciro iv

### Fixed
- Since 0.12.1 `visuals/build.py` stopped with `A.4: pattern not expected for informationcarrier--productioncentre`, and the case figures (PF, PC, IC-PC) and the pages Overview, Potform and Maps were not rebuilt. Cause: the chain pages add their cases (A.1, A.4, ...) to `CASES`, and `check_cases()` checked those too. It now checks only the cases of `data/cases.csv`. *Warum:* Die Fallgrafiken wurden seit S21 nicht mehr neu erzeugt; die Prüfung galt versehentlich auch für die Kettenfälle.

### Changed
- **PC.1** (One OR between centres) shows Saciro iv, `Pfaffenhofen or Westerndorf`, carrier 202335 (before: Sem- i, `Aspiran or Saint-Saturnin`). The caption no longer carries the counts of the old query.
- All case figures are rebuilt; the kiln sites of `kilnsites-extra.csv` appear among the "other kiln sites".

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
