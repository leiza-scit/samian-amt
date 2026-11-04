# PRIMER — samian-amt

Arbeitsplan für das Repository `leiza-scit/samian-amt`. Wird in jedem Chat hochgeladen, am Ende des Chats
zurückgeschrieben. Dieses Dokument ist deutsch; alles andere im Repository ist britisches Englisch.

---

## Teil A — Immer gültig

### A1 Ausgangslage

| Was | Wo | Rolle |
|---|---|---|
| samian-amt-Ontologie, Reasoning, Docs, Ketten | dieses Repository | Ziel |
| `alpaca-fair-framework/amt-engine`, `alpaca-fair-framework/amt-runner` | GitHub | Engine (0.6.0) und Runner (0.5.0); Quelle für den späteren Viewer; ehemals `n4o-rse` |
| `leiza-scit/CAA2026-amt` | GitHub | Vorbild für Viewer und Docs |
| `caa-datadragons/FW_Ontology` | GitHub | `fw:`-Begriffe: Typ-Individuen, `fw:EqualShareRule`, Evidenz (Stand `15ae05f`) |
| `n4o-rse/oer-001-sparqling-archaeology` (`notebooks_amt`) | GitHub | Vorbild für das Notebook |
| Samian-Exporte (Samian-Daten, `ct_ic_pc`) | lokal, nicht im Repository | Quelle der Zeichenketten und Gewichte |

**Befunde** (geprüft 2026-10-30):

- Der Zentrums-String ist ein Attribut des **Potters**, nicht des Trägers: alle 1.375 Potter der Zentrums-Exporte
  haben genau einen String, und bei den verglichenen 1.072 Potters haben alle Träger identische Kanten. Das Paper sagt
  dasselbe (Ansatz B „folgt aus“ Ansatz A).
- Die frühere Gewichtsformel des Papers `1 / (n_? + n_Möglichkeiten)` (seit 2026-11-04 ersetzt, siehe A4) stimmte für **alle 95.819** vorhandenen Zentrumskanten
  in `ct_ic_pc`. 9.033 von 45.685 Zentrums-Strings haben weniger Zentrumsknoten als Entitäten (Regionen, Gruppen,
  fehlende Zuordnung): Lücke in der Abdeckung, kein Gewichtsfehler.
- Potform-Strings tragen im Export keine Gewichte, nur Text. Die Regel gilt dort nach dem Paper (Abb. 6: 0.33).
- Das Paper rechnet die Rollenketten mit `ProductLogic` (Listings 5 und 6). Listing 6 beginnt mit `(PF)` an einer
  Stelle, an der `(AE)` zu erwarten wäre; vermutlich ein Tippfehler.
- Unter Product zählt Modell M1 eine vom Potter geerbte Unsicherheit doppelt: Ve- i, `carrierToActor` 0.25 (Product)
  gegen 0.5 (Gödel).
- 2.777 Träger haben einen unsicheren Potternamen (OR im Namen): die Träger-Potter-Verknüpfung von M2 ist nicht immer scharf.
- **FW-Ontologie angepasst** (`caa-datadragons/FW_Ontology`, Commit `15ae05f`, 2026-10-30), das ändert die Hextupel-Namen:
  `fw:hasDegreeOfConnection` (äquivalent zu `amt:weight`), `fw:hasType` mit **Individuen** `fw:Uncertainty`, `fw:Vagueness`,
  `fw:FuzzinessWobbliness` (Klasse `fw:FW_Type`), `fw:hasMethod` mit `fw:EqualShareRule` (`fw:formula "1 / (n_question + n_possibilities)"`,
  `fw:implementedBy` steht noch aus), und die Quellzeichenkette als `fw:TextEvidence` (`fw:sourceString`) über `fw:derivedFrom`; ein
  Evidenzknoten kann sich die Alternativen eines OR teilen. `fw:UncertainValue` und `fw:VagueValue` sind Unterklassen von
  `fw:FuzzinessWobblinessValue`. Die Beispiele der FW-Ontologie bestätigen die Zuordnung Muster → Typ (`Lezoux or Vichy ?` = 0,33, FW;
  `South Gaul?` = 0,5, Unsicherheit). Die AMT-Logiken stehen dort als `fw:PropagationMethod` (Vorschlag `data/amt-alignment.ttl`, gehört
  in `amt.ttl` der Engine).
- **Engine 0.6.0 ausgeführt** (2026-10-30, S3a): `python main.py` vergleicht die drei Läufe (M1 Product, M1 Gödel, M2 Product, 340 Kanten) mit dem Referenz-Reasoner in Gewicht, Typ und Methode: gleich. Die Engine liest `fw:hasDegreeOfConnection`, `fw:hasType`, `fw:hasMethod` und `fw:derivedFrom` ohne `amt:weight`.
- **SHACL** (Shapes der Engine, `validate_against_shapes`): M2 entspricht den Shapes; **M1 hat vier Verstöße**, alle bei den Oberrollen `sam:reaches` und `sam:reachedBy`: sie haben weder `rdfs:domain` noch `rdfs:range` (die Shapes verlangen je genau eines). Die Oberrolle fasst `potformToCentre`, `carrierToActor` und `potformToActor` zusammen, die verschiedene Concepts verbinden; ein einzelnes Domain/Range gibt es dafür nicht. Der Runner bricht deshalb bei `dist/chains-with-model.ttl` in der Validierung ab. Offen (S9).

### A2 Zielbild

```
Samian-Strings ──► py/weights.py ──► Hextupel (dist/chains.ttl) ──► Reasoner ──► docs/ (GitHub Pages)
 (data/*.csv)    Gewicht, FW-Typ,     s p o weight type method     M1 / M2        Viewer, Notebook
                 Methode
```

Eigenschaften, die das Ergebnis haben muss:

1. Jedes Gewicht in `dist/` ist aus einer Quellzeichenkette durch `py/weights.py` berechnet; der Selbsttest schlägt bei Abweichung fehl.
2. Aus den Hextupeln lässt sich die Quellzeichenkette bis auf Reihenfolge und Schreibweise zurückbauen (Roundtrip).
3. Docs und Grafiken entstehen nur aus Ontologie, Daten und Reasoning; nichts ist von Hand geschrieben, was daraus folgt.
4. Zwei Läufe von `python main.py` hintereinander ändern keine Datei.

### A3 Querschnittsregeln

- Rohdaten bleiben unverändert und liegen nicht im Repository (nur kleine Auszüge in `data/`).
- Kein `datetime.now()` in Generatoren; Ausgabe ist deterministisch (siehe Abnahme von S3).
- **Zwei Läufe, `git status` bleibt sauber.**
- Netzwerkzugriff nur in einem eigenen Schritt; keiner der heutigen Schritte braucht ihn.
- `main.py` ist der einzige Einstieg; jeder Schritt läuft auch einzeln.
- Kein Chat ändert zwei Schritte gleichzeitig. Lieferung als Patch-ZIP (`patch-zip-delivery`), `PATCH-README.md` nennt den Schritt.
- Befehle für Windows `cmd`, je eine Zeile. Änderungen am Repository nur über Patch-ZIP, nur Quellen.

### A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Name der Rolle Träger → Potform | `hasType`, invers `isTypeOf` (mit Allard Mees geklärt) | vor 2026-10-30 |
| Diagramme | „mermaid-like“, mit Python gezeichnet; Farben nach dem AMT-Schema | 2026-10-30 |
| Ist `amt:weight` in beide Richtungen gleich? | Ja bei Inversen; Anteile und Häufigkeiten gehören nicht in `amt:weight` | 2026-10-30 |
| Wie wird das Gewicht berechnet? | `Gewicht = (1 / n_Möglichkeiten) · (1/2, wenn `?`)`, zwei Nachkommastellen; AND behält volles Gewicht, OR teilt gleich, `?` halbiert das Gewicht jeder Entität (`A or B?` = 0,25; `A or B or C?` = 0,17; `A and B?` = 0,5). Ersetzt die Regel des Papers `1 / (n_? + n_Möglichkeiten)` (`?` als eine Möglichkeit mehr): „der falsche Ansatz“ (Allard); Bestätigung durch Flo im Memo 0.8.0. Methode bleibt `fw:EqualShareRule`, Beschreibung in der FW-Ontologie wird erweitert. Zwei Nachkommastellen bleiben | 2026-11-04 |
| Zuordnung FW-Typ je Muster | `?` → `UncertainValue`; OR oder AND → `VagueValue`; `?` mit OR oder AND → `FuzzinessWobblinessValue` (Flo) | 2026-10-30 |
| Erwartete Muster je Relation | Träger–Potform: OR, `?`, `?`+OR; Actor–Zentrum: OR, AND, `?`+AND, `?`; Träger–Zentrum: `?` (Flo) | 2026-10-30 |
| Hextupel | Quadrupel plus Typ und Methode; Methode wird in `caa-datadragons/FW_Ontology` beschrieben und verlinkt | 2026-10-30 |
| Namen für Gewicht, Typ, Methode, Evidenz | `fw:hasDegreeOfConnection` (≡ `amt:weight`), `fw:hasType` (Individuen `fw:Uncertainty` / `fw:Vagueness` / `fw:FuzzinessWobbliness`), `fw:hasMethod` (`fw:EqualShareRule`), optional `fw:derivedFrom` (`fw:TextEvidence`). Hinfällig: die Vorschläge `amt:type`, `amt:method`, `nfdi_fw:ReciprocalPossibilityWeight` und `nfdi_fw:WeightMethod`; die FW-Ontologie hat es am 2026-10-30 anders festgelegt. samian-amt zieht in S3a nach | 2026-10-30 |
| Methode und Typ abgeleiteter Kanten | wie in AMT.engine 0.6.0: Rollenkette setzt die Logik als `fw:hasMethod` (`amt:ProductLogic` usw.) und als Typ den gemeinsamen Typ der Vorderglieder, bei Unterschied `fw:FuzzinessWobbliness`; Inverse und Subsumtion übernehmen den Typ und haben keine Methode; kein Typ gilt als `fw:Vagueness`; der Referenz-Reasoner bildet das nach und wird gegen die Engine geprüft | 2026-10-30 |
| Typ einer sicheren Aussage (Muster `certain`) | `fw:hasType fw:Certainty` (Gewicht 1.0); `createdBy` in M2 ebenso; `fw:Certainty` wird nie angenommen. Ersetzt: „kein Typ, AMT liest `fw:Vagueness`“ (2026-10-30) | 2026-11-03 |
| Typ abgeleiteter Kanten mit `fw:Certainty` | `fw:Certainty` zählt nicht mit, sobald ein anderer Typ vorkommt; eine Kette sicherer Kanten bleibt sicher (Engine S25) | 2026-11-03 |
| Gewicht im Hextupel | `fw:hasDegreeOfConnection` (die Engine liest es wie `amt:weight`); beide zusammen werden nicht geschrieben | 2026-10-30 |
| Evidenzknoten | ein `fw:TextEvidence`-Knoten je Quellzeichenkette (`sam:ev_<potform\|centre>_<slug>`, `?` als `_q`), von allen Aussagen der Zeichenkette über `fw:derivedFrom` geteilt | 2026-10-30 |
| Logik der Rollenketten | `ProductLogic` wie im Paper (Allard) | 2026-11-04 |
| Modell M1 oder M2 | Beides (Allard): Liegt der Stempel auf einer Scherbe in einem Produktionsort, ist `hasProductionCentre` direkt gesetzt (M1; maßgeblich ist die Liste der Produktionsorte, nicht ein Kennzeichen je Scherbe). Sonst abgeleitet über die neue Rolle „gleicher Stempel“ (Träger → geometrisch identischer Stempel auf anderer Scherbe → Zentrum dieser Scherbe). Umsetzung: S4b | 2026-11-04 |
| Schwächere Ableitungen Träger–Zentrum | (a) Name aus einem Nicht-Produktionsort, gefunden auf einer nicht identischen Scherbe im Produktionsort (Homonymrisiko); (b) Ähnlichkeit der Verbreitung von Töpfer oder Stempel und Zentrum (selten dokumentiert, mehrere Zentren haben ähnliche Verbreitung, zum Beispiel Haute-Yutz, Chémery-Faulquemont, Trier). Beide schwächer als direkt oder „gleicher Stempel“; Weg der Abschwächung (Methode oder Typ) noch zu klären (Memo 0.6.0) | 2026-11-04 |
| Fragezeichen am Ende | bezieht sich auf die ganze Kette davor, schwächt immer ab, ohne zu sagen, ob wegen A oder B (Allard) | 2026-11-04 |
| Zeit in der Kette | ignoriert, bis auf Weiteres (zu ungenau); Quietus-Beispiel bleibt AND ohne Reihenfolge | 2026-11-04 |
| Beste Pfade | nur der beste einzelne Pfad; die Zahl der Träger zählt nicht | 2026-11-04 |
| Actor und ActorEntity | zu einem Concept `Actor` zusammengeführt (schon in `ontology/samian-amt.ttl`) | 2026-11-04 |
| Träger–Töpfer | sicher (Gewicht 1.0, `fw:Certainty`), auch bei unsicherem Namen („Aquitanus?“): maßgeblich ist die geometrisch exakte Stempelgleichheit | 2026-11-04 |
| Kombinierte Formen (`18/31`) | ein Typ, kein „dish or bowl“ (Allard) | 2026-11-04 |
| Zentren-Strings ohne Knoten („South Gaul?“) | für dieses Modell nicht verwertbar; es entstehen keine Knoten für Regionen und Gruppen | 2026-11-04 |
| Quellzeichenkette | bleibt erhalten (`fw:TextEvidence`), Allard bestätigt | 2026-11-04 |
| Muster `?` nach OR bei Potformen | darf nicht vorkommen; drei fehlerhafte Einträge (212025, 213077, 210355) bereinigt Allard in der Datenbank | 2026-11-04 |
| Häufigkeitsanteile („31 or 31R“ = 0,8025 / 0,1975) | Zusatzinformation, **kein Gewicht**: nicht in `fw:hasDegreeOfConnection`, nicht in der Kette, das Fragezeichen ändert sie nicht; nur ein Hinweis für den Archäologen, eine bestehende Unsicherheit an der Gesamtverteilung zu prüfen. Methode „Wahrscheinlichkeit basierend auf dem Häufigkeitsanteil“ (`sam:FrequencyShare`, noch nicht in der FW-Ontologie). Stufe A (ganze Datenbank) umgesetzt in `py/frequency.py` (allgemein) und für die drei Ketten; Stufe C (Töpfer, geglättet, k = 5, Glättung reicht als Rückfall) und Stempel vorgesehen. Belegzahlen aus `data/form-counts.csv` (Auszug aus Allards `data-1793809985134.csv`) | 2026-11-04 |
| Typ-Klassen | hinfällig: der Typ einer Aussage ist ein Individuum von `fw:FW_Type`, keine Klasse (FW-Ontologie, 2026-10-30) | 2026-10-30 |
| Sprache | PRIMER und Memos deutsch, Repository englisch | 2026-10-30 |
| Name des Projekts | `samian-amt` (Repository `leiza-scit/samian-amt`, früher `CHNT2026-amt`, Arbeitsname „Mini-AMT“); überall nur noch `samian-amt`; in Links kein CHNT mehr | 2026-11-04 |
| Prefix und Namespace | Prefix `sam:` statt `mini:`; Namespace `http://example.org/samian-amt/` bleibt ein Platzhalter bis zu einer persistenten IRI; Dateien `ontology/samian-amt.ttl`, `py/samian_amt_utils.py` | 2026-11-04 |
| Titel des Explorers | „Samian Research - AMT Explorer“ (feste Kopfzeile, ohne Kettentitel); oben links das AMT-Logo (Pinguin), LEIZA, mainzed und NFDI4Objects im About-Panel | 2026-11-04 |
| Status „consistent“ im Explorer | entfällt; nur bei Verstößen gegen die Integritätsaxiome erscheint eine Warnung | 2026-11-04 |
| Cypher-Export im Explorer | der gezeigte Graph (eine Richtung; mit Reasoning auch die abgeleiteten Kanten), Neo4j 5, je Knoten und Kante eine Anweisung mit `MERGE`; Eigenschaften `weight`, `role`, `fwType`, `method`, `inferred`, `source` | 2026-11-04 |
| Allgemeine Rolle `reaches` im Explorer | standardmäßig ausgeblendet (wiederholt die abgeleiteten Rollen), Schalter in der Legende; was ausgeblendet ist, steht weder im Bild noch im Cypher-Export | 2026-11-04 |

### A5 Was in welchem Chat hochgeladen wird

Das Repository als Bündel (ohne Erzeugtes), dazu `PRIMER.md`:

```
robocopy . %TEMP%\samian-amt-bundle /E /XD .git .venv dist __pycache__ docs\diagrams
```

```
powershell -Command "Compress-Archive -Path $env:TEMP\samian-amt-bundle\* -DestinationPath samian-amt-bundle.zip -Force"
```

Nicht hochladen: `.git/`, `.venv/`, `dist/`, die Samian-Exporte (nur bei Schritten, die sie brauchen, und dann einzeln).

---

## Teil B — Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S1 | Modell, Ontologie, Referenz-Reasoner, vier Grafiken (0.1.0) | samian-amt | | erledigt 2026-10-30 |
| S2 | Reasoning-Rollen mit Inversen, Docs für GitHub Pages, Gewichtsrichtung (0.2.0) | samian-amt | S1 | erledigt 2026-10-30 |
| S3 | Gewichtsregel, Hextupel, drei echte Ketten, Modell M2 (0.3.0) | samian-amt | S2 | erledigt 2026-10-30 |
| S4 | Entscheidung M1 / M2 und Logik nach der Prüfung durch Allard | samian-amt | S3 | entschieden 2026-11-04 (A4, Review-Seite); Umsetzung in S4a und S4b |
| S4a | Neue Gewichtsregel (`?` halbiert) und Häufigkeitsanteile als Zusatzinformation (Stufe A) (0.14.0) | samian-amt | S4 | Patch geliefert 2026-11-04 |
| S24 | AMT Explorer für die drei Ketten (A, B, C) auf den GitHub Pages, nur eine Reasoning-Richtung (0.15.0) | samian-amt | S4a | Patch geliefert 2026-11-04; Live-Test auf GitHub Pages steht aus |
| S25 | Umbenennung auf `samian-amt` (Repository, Links, Prefix `sam:`, Dateinamen) (0.16.0) | samian-amt | S24 | Patch geliefert 2026-11-04 |
| S26 | Explorer überarbeitet: Kopfzeile, Logos, Legende, Cypher, Details, Layout in Kettenrichtung, PNG/SVG, Link, Vollbild (0.17.0) | samian-amt | S25 | Patch geliefert und eingespielt 2026-11-04 (Live-Seite geprüft) |
| S27 | Explorer ruhiger: Beschriftung bei Auswahl, nur inferierte Linien, Positionen im Link, Legende kurz, mainzed-Logo (0.17.1) | samian-amt | S26 | Patch geliefert 2026-11-04 |
| S4b | Hybridmodell: `hasProductionCentre` direkt, sonst Rolle „gleicher Stempel“ (neu), schwächere Ableitungen (Verbreitung 0,75, Namensgleichheit 0,5) | samian-amt | S4 | zurückgestellt (Allard und Flo, 2026-11-04: Stempel-ID und Fundort spielen für das kleine Modell erst mal keine Rolle) |
| S3a | samian-amt an die FW-Ontologie anpassen (Namen, Typ-Individuen, Methode, Evidenz) | samian-amt | S3 | erledigt 2026-10-30 (0.4.0) |
| S3b | `fw:Certainty` für sichere Aussagen, Typkombination wie die Engine (0.5.0) | samian-amt | S3a | Patch geliefert 2026-11-03, nach Push erledigt |
| S5 | Methode und Typen in der FW-Ontologie | FW_Ontology | S3 | FW-Seite erledigt 2026-10-30; `fw:implementedBy` offen (Triple liegt in `ontology/fw-implemented-by.ttl`) |
| S10 | Hextupel in amt-engine und amt-runner einlesen und durchreichen | amt-engine, amt-runner | S3a | erledigt 2026-10-30 (Engine 0.6.0, Runner 0.5.0; in den Primern dort S19 bis S23) |
| S6 | Alle Potter und Träger als Hextupel (Export → `dist/`) | samian-amt | S4 | offen |
| S7 | Viewer, angepasst aus amt-engine und amt-runner | samian-amt | S6 | offen |
| S8 | Notebook (quarto-live) | samian-amt | S6 | offen |
| S11 | Fallgrafiken PF.1–3, PC.1–4, IC-PC.1 mit Samian-Beispielen (`visuals/`, 0.6.0) | samian-amt | S3b | Patch geliefert 2026-11-04, nach Push erledigt; Rückfragen offen (Teil D) |
| S12 | PF.4 (Häufigkeitsbalken) und Orientierungsebenen der Karten (0.7.0) | samian-amt | S11 | Patch geliefert 2026-11-04 |
| S13 | Römische Variante der Karten (Provinzen, Straßen, Orte; 0.8.0) | samian-amt | S12 | Patch geliefert 2026-11-04 |
| S14 | Modellgrafiken im Visuals-Stil, Visuals über die Docs veröffentlicht (0.9.0) | samian-amt | S13 | Patch geliefert 2026-11-04 |
| S15 | Einzelketten, klarere Pfeile und nummerierte Kanten in den Visuals (0.9.1) | samian-amt | S14 | Patch geliefert 2026-11-04 |
| S16 | Nummerierte Kanten in `docs/diagrams/02_full_semantics` (0.9.2) | samian-amt | S15 | Patch geliefert 2026-11-04 |
| S17 | Review-Seite aus der öffentlichen Version genommen, `REVIEW.md` intern (0.9.3) | samian-amt | S16 | Patch geliefert 2026-11-04 |
| S18 | Visuals-Seiten im Layout von GeoScience-FAIRification-LOD, getrennt nach Potform / Karten modern / Karten römisch (0.10.0) | samian-amt | S17 | Patch geliefert 2026-11-04 |
| S19 | Ein Design für Docs und Visuals, Chain-Unterseiten (A, B, C), matplotlib entfernt (0.11.0) | samian-amt | S18 | erledigt 2026-11-04 |
| S20 | Chain-Seiten: Kettengrafik oben, Entitäten und Aussagen im Text; Menü Docs/Visuals getrennt (0.12.0) | samian-amt | S19 | erledigt 2026-11-04 |
| S21 | Chain-Seiten: Figuren für InformationCarrier–ProductionCentre je Carrier (0.12.1) | samian-amt | S20 | erledigt 2026-11-04 |
| S22 | Koordinaten der vier Zentren und Profilzeichnungen 24, 27, 31, 32, 33 eingebaut (0.13.0) | samian-amt | S21 | erledigt 2026-11-04 |
| S23 | Fehlerbehebung `check_cases` (Fallgrafiken wurden nicht neu gebaut); PC.1 mit Saciro iv (0.13.2) | samian-amt | S22 | Patch geliefert 2026-11-04 |
| S9 | Engine-Abgleich und SHACL-Validierung | samian-amt | S3 | Abgleich erledigt 2026-10-30 (mit S3a); SHACL: M1 hat vier Verstöße (Teil D) |

S5 und der SHACL-Teil von S9 sind unabhängig von S4. S6 bis S8 warten auf die Entscheidung in S4.

---

## Teil C — Die Schritte

## S3 — Gewichtsregel, Hextupel, drei echte Ketten

**Ziel:** Gewicht, FW-Typ und Methode jeder Aussage werden aus der Quellzeichenkette berechnet; drei echte Ketten laufen durch zwei Modelle.

**Uploads:** Paper „How to handle vagueness and uncertainty“; die Samian-Exporte nur für die Prüfung der Kantengewichte.

Inhalt: `py/weights.py`, `data/weight-cases.csv`, `data/chains-source.csv`, `py/step_chains.py`, `ontology/variant-b-derived.ttl`,
`ontology/fw-method-draft.ttl`, Grafik 05, Seite *Chains*, Abschnitte auf der Seite *Weights*, Review-Fragen 8 bis 14.

**Abnahme:** `python main.py` läuft durch; `python py/weights.py` meldet „15 cases agree“; zwei Läufe hintereinander ändern keine Datei in `docs/` und `dist/`;
die exportierten Zentrumsgewichte der vier Träger stimmen mit der Regel überein (sonst bricht `step_chains` ab).

### Erledigt 2026-10-30

- Regel gegen alle Zentrumskanten geprüft: 95.819 von 95.819 stimmen. Die Lücken (9.033 von 45.685 Strings) sind Abdeckung, kein Gewichtsfehler.
- Ketten: A Vitalis viii (AND, `32?`), B Onnio- (OR, `18/31?`), C Ve- i (OR mit drei Formen, AND mit `?`).
- Unter Product zählt M1 die Unsicherheit am Potter doppelt (Ve- i `carrierToActor` 0.25 gegen 0.5 unter Gödel); M2 nicht.
- Der Roundtrip vom Hextupel zur Zeichenkette ist verlustfrei bis auf Reihenfolge und Schreibweise der Entitäten.
- Nicht geprüft: Engine-Abgleich (Engine nicht installiert) und SHACL-Validierung.

## S4 — Entscheidung M1 / M2 und Logik

**Ziel:** Ein Modell, eine Logik, dokumentiert in A4.

**Abnahme:** A4 enthält Beschluss und Datum; die Ontologie entspricht dem Beschluss; Review-Seite aktualisiert.

**Stand:** Allards Antworten auf Memo 0.5.0 (2026-11-04) sind in A4 und in `REVIEW.md` (Abschnitt „Answer“) festgehalten. Die Modelländerungen daraus laufen in S4a und S4b, jeweils in einem eigenen Chat.

## S4a — Gewichtsregel und Häufigkeitsanteile

**Ziel:** Die Gewichtsregel nach Allards Antworten (Memo 0.7.0, bestätigt im Memo 0.8.0) und die Häufigkeitsanteile als Zusatzinformation.

Inhalt (0.14.0):

- `py/weights.py`: `Gewicht = (1 / n_Möglichkeiten) · (1/2, wenn ?)`, Rekonstruktion und Selbsttest angepasst; `data/weight-cases.csv` neu gerechnet (`A or B?` 0,25; neuer Fall `A or B or C?` 0,17).
- `py/frequency.py` und `data/form-counts.csv`: Anteile der Alternativen eines OR in der ganzen Datenbank (Stufe A). Nur Zusatzinformation (`sam:frequencyShare`, `sam:frequencyCount`, `sam:frequencyTotal`, `sam:frequencyLevel`, `sam:frequencyMethod`) in `dist/chains.ttl`; kein Gewicht, nicht in den Engine-Eingaben.
- Grafiken, Seiten (*Weights*, *Review*, Kettenseiten, PF.3 und PF.4) und README an die Regel angepasst.

**Abnahme:** `python main.py` läuft durch; `31 or 31R` ergibt 0,8025 / 0,1975; zwei Läufe ändern keine Datei.

**Offen:** Stufe C (Töpfer-Repertoire, geglättet, mit Belegzahl und Status) und die Stufe „Stempel“; die vollständige Belegzahl-Datei von Allard statt des Auszugs; FW-Ontologie: Beschreibung von `fw:EqualShareRule` und Eintrag für die Häufigkeitsmethode (Patch für `FW_Ontology` liegt bei).

## S24 — AMT Explorer für die drei Ketten

**Ziel:** Auf den Pages des samian-amt läuft der Explorer von `amt-engine` (reines JavaScript im Browser, Reasoner `js/amt-reasoner.js`), aber nur mit den drei Ketten.

Inhalt (0.15.0):

- `docs/explorer/`: Seite, Skripte, Bibliotheken und Palette (statisch, aus `amt-engine` übernommen und angepasst: Pfade, Kopfzeile, Auswahl Chain A / B / C statt Beispielliste, kein Upload). Die Bibliotheken liegen lokal, es wird nichts von einem CDN geladen.
- Schritt `explorer` (`py/step_explorer.py`): schreibt `docs/explorer/data/chain-A.ttl`, `-B`, `-C` (Modell M1 plus die Hextupel der Kette) und `examples.json` aus `data/chains-source.csv`.
- **Reasoning nur in eine Richtung** (Flo, 2026-11-04): Der Explorer blendet die Inversen (`isTypeOf`, `isProductionCentreOf`, `hasWorker`, `centreToPotform`, `actorToCarrier`, `actorToPotform`, `reachedBy`) aus; im Turtle-Download bleiben sie.
- Menü der Seiten: Gruppe „Explorer“ mit Chain A, B, C.

**Abnahme:** Chromium (headless): Graph lädt, Reasoning erzeugt die Kanten; die Gewichte aller 128 Kanten der drei Ketten (mit Inversen) stimmen mit `py/reference_reasoner.py` überein.

**Offen:** Live-Test auf GitHub Pages; Modell M2 oder Gödel-Logik als Auswahl (bewusst nicht eingebaut).

## S25 — Umbenennung auf samian-amt

**Ziel:** Das Repository heißt überall `samian-amt`; kein `CHNT`, kein `Mini-AMT`, kein `mini:` mehr in den Quellen.

Inhalt (0.16.0): Links und Texte (`leiza-scit/samian-amt`), Namespace `http://example.org/samian-amt/` mit Prefix `sam:`, `ontology/samian-amt.ttl`
und `py/samian_amt_utils.py` (umbenannt; die alten Dateien löscht man von Hand), „CHNT data“ wird „Samian Research data“. Der CHANGELOG
vor 0.16.0 bleibt unverändert (er beschreibt den damaligen Stand).

**Abnahme:** `grep` nach `CHNT`, `Mini-AMT`, `mini:` in den Quellen (ohne `CHANGELOG.md` und `PRIMER.md`) findet nichts; `python main.py` läuft zweimal durch, danach
ändert sich nichts mehr; die Turtle-Dateien tragen `sam:`.

## S26 — Explorer überarbeitet

**Ziel:** Der Explorer ist lesbar, auch mit Reasoning, und liefert die Ausgaben, die man für Folien und Neo4j braucht.

Inhalt (0.17.0): Kopfzeile „Samian Research - AMT Explorer“ mit AMT-Logo; Icons statt Text für Turtle, Cypher, PNG, SVG, Link, Vollbild;
Details-Panel und About-Panel (LEIZA, mainzed, NFDI4Objects) als Info-Icons in der Leiste; Legende der Knotenfarben unten rechts, einklappbar
(klein: eingeklappt); Spalten in Kettenrichtung, abgeleitete Kanten als gestrichelte Bögen, dünnere Linien (Dicke = Gewicht), Fokus auf die
Nachbarschaft beim Klick; Kantenbeschriftung wählbar (Namen und Gewichte, Gewichte, keine); allgemeine Rolle `reaches` schaltbar;
Link merkt sich Kette, Reasoning, Beschriftung.

**Abnahme:** Chromium (headless): Titel, keine Konsolenfehler außer dem fehlenden mainzed-Logo, Kanten ohne Reasoning 8 und mit Reasoning 16 (Chain A),
Cypher-Dialog mit 7 Knoten und 16 Beziehungen, PNG und SVG laden, der Link stellt Kette, Reasoning und Beschriftung wieder her.

**Offen:** Cypher-Test in einer echten Neo4j-Instanz (hier nur die Textform geprüft). Das mainzed-Logo kam mit S27.

## S27 — Explorer ruhiger

**Ziel:** Das Bild bleibt auch in Kette A mit Reasoning lesbar (Rückmeldung nach dem Live-Test, 2026-11-04).

Inhalt (0.17.1): Kantenbeschriftung standardmäßig nur bei Auswahl („Labels: on selection“); Schalter „nur inferierte Linien“ in der Legende (`only=inferred`);
verschobene Knoten stehen im Link (`pos=`) und bleiben nach Auswahl und Beschriftungswechsel stehen; Legende nennt nur den Begriff, die Erklärung steht
im Details-Panel; `mainzed.png` im Repository.

**Abnahme:** Chromium (headless): ohne Auswahl keine Beschriftung, mit Auswahl die Linien der Nachbarschaft; „nur inferierte“ zeigt 8 von 16 Linien (Chain A);
Knoten ziehen, auswählen und Beschriftung wechseln lässt die Position stehen; der Link stellt die Positionen wieder her; keine Konsolenfehler,
mainzed-Logo geladen.

**Offen:** Ziehen im echten Browser (hier nur simuliert); Fullscreen mit dem neuen Layout.

## S4b — Hybridmodell Träger–Zentrum (zurückgestellt)

Allard (2026-11-04): Stempel-ID (`in_id`, geometrisch eindeutig) und Fundort je Träger spielen für das kleine Modell erst mal keine Rolle; Flo stimmt zu. Die Daten liegen im Drive (`ct_ic_in.csv`: Träger, Stempel, `dieposition` ignorieren; `ct_ic_pc.csv`: das Gewicht ignorieren, es wird neu abgeleitet; `tblkilnsitesWithCoordinates.csv`: Liste der Produktionsorte). Abgeleitet wird mit den Faktoren Verbreitung 0,75 und Namensgleichheit 0,5 (eigene Methode je Art); mehrere Produktionsorte gleich stark (ein „or“); `Saint-Saturnin` ist die Kurzform von `Jonquières, Saint Saturnin`.

**Ziel:** Fall 1 (Stempel im Produktionsort) bleibt `hasProductionCentre`; Fall 2 wird über die neue Rolle „gleicher Stempel“ abgeleitet; schwächere Ableitungen (Namensgleichheit, Verbreitung) bekommen eigene Methode oder Typ.

**Uploads:** `PRIMER.md`, das Repository als Bündel, die Liste der Produktionsorte, ein Auszug mit Stempelgleichheit (welche Träger teilen einen geometrisch identischen Stempel).

**Abnahme:** Ontologie, Reasoner und Chain-Seiten zeigen beide Fälle; die Rollenkette „gleicher Stempel“ rechnet mit Product; der beste Pfad gewinnt; Dokumentation und `CHANGELOG.md` nennen die Schwächung.

## S3a — samian-amt an die FW-Ontologie anpassen

**Ziel:** Hextupel, Quellen und Dokumentation benutzen die Begriffe der FW-Ontologie statt meiner Vorschläge.

**Uploads:** `PRIMER.md`, das Repository als Bündel, die aktuelle FW-Ontologie (`ontology/nfdi_fw_ontology.owl`).

Inhalt:

- `py/weights.py`: `FW_TYPE` liefert die Individuen `Uncertainty`, `Vagueness`, `FuzzinessWobbliness` (Zuordnung der Muster bleibt); die Methode heißt `EqualShareRule`.
- `py/step_chains.py`: `dist/chains.ttl` schreibt `fw:hasDegreeOfConnection`, `fw:hasType`, `fw:hasMethod` und je Quellzeichenkette einen `fw:TextEvidence`-Knoten (`fw:sourceString`), den sich die Aussagen einer Zeichenkette über `fw:derivedFrom` teilen. Das beantwortet Review-Frage 14 (Reihenfolge und Schreibweise bleiben erhalten).
- Der Roundtrip-Test liest zusätzlich die Zeichenkette aus dem Evidenzknoten; die Rekonstruktion aus Gewicht, Typ und Kantenzahl bleibt als Gegenprobe.
- `ontology/fw-method-draft.ttl` entfällt; `fw:implementedBy` bekommt die IRI von `py/weights.py` (Datei im Repository oder Release).
- Seiten *Weights*, *Chains*, *Review* und die Grafik 05 nennen die neuen Begriffe; `README.md` und `CHANGELOG.md` auch.

**Abnahme:** `python main.py` läuft durch; `dist/chains.ttl` enthält kein `amt:type` und kein `amt:method` mehr; der Selbsttest prüft, dass jede Aussage einer Zeichenkette denselben Evidenzknoten hat und dass Gewicht, Typ und Methode zu den Beispielen der FW-Ontologie (`Lezoux or Vichy ?` = 0,33, `South Gaul?` = 0,5) passen; zwei Läufe ändern keine Datei.

### Erledigt 2026-10-30 (S3a, Version 0.4.0)

- `py/weights.py`: Typ-Individuen `Uncertainty`, `Vagueness`, `FuzzinessWobbliness`; Methode `EqualShareRule`; `IMPLEMENTED_BY`; die Nutzlast jeder Kante nennt die Quellzeichenkette. `data/weight-cases.csv` hat 17 Fälle (neu: die beiden Beispiele der FW-Ontologie).
- `py/step_chains.py`: `dist/chains.ttl` mit `fw:`-Präfix, `fw:hasDegreeOfConnection`, `fw:hasType`, `fw:hasMethod`, `fw:derivedFrom` und je Zeichenkette einem `fw:TextEvidence`-Knoten. Neu: `check_roundtrip` (die Datei wird zurückgelesen: jede Aussage führt zu ihrer Zeichenkette; Gewicht, Typ, Methode stimmen mit der Regel; Gegenprobe aus Gewicht, Typ und Kantenzahl), `dist/chains-with-model.ttl` (Ontologie M1 plus Daten, für Engine und Runner), `engine_check` (drei Läufe mit der Engine, Kante für Kante inklusive Typ und Methode; ab Engine 0.6.0, sonst übersprungen mit Hinweis; dazu die SHACL-Prüfung als Information).
- `py/reference_reasoner.py`: Typ und Methode abgeleiteter Kanten nach der Regel der Engine (Beschlusslage oben), unabhängig geschrieben.
- `ontology/fw-method-draft.ttl` entfällt; `ontology/fw-implemented-by.ttl` hält das eine Triple `fw:EqualShareRule fw:implementedBy <…/py/weights.py>` für die FW-Ontologie.
- Seiten *Weights* und *Chains*, Grafik 05, `README.md`, `CHANGELOG.md`, `requirements.txt` (Engine-Zeile jetzt `alpaca-fair-framework`, ab `v0.6.0`).
- Geprüft (Linux, Python 3.13.18, Engine 0.6.0 aus dem Klon): `python main.py` zweimal, Status stabil; 340 Kanten gleich; der Rückweg liest 20 Aussagen. Mit einer installierten Engine 0.5.0 meldet der Schritt, dass er mindestens 0.6.0 braucht, und überspringt den Abgleich (0.5.0 liest die `fw:`-Begriffe nicht und würde sonst alle Kanten als fehlend melden).
- Nicht geprüft: Windows; ob die Grafiken 01 bis 04 dort unverändert bleiben (matplotlib erzeugt auf anderen Versionen andere Bytes).

## S3b — `fw:Certainty`

**Ziel:** Das samian-amt folgt der Engine (S25) und der FW-Ontologie (2026-11-03): sichere Aussagen tragen `fw:Certainty`.

**Inhalt:** `py/weights.py` (`CERTAINTY`, `FW_TYPE["certain"]`), `py/reference_reasoner.py` (`combine_types` wie die Engine), `py/step_chains.py` (`createdBy` mit `Certainty`, Engine-Prüfung überspringt Engines ohne `fw:Certainty`), `py/step_diagrams.py` (Kennzeichen `C`), `py/step_docs.py`, `data/weight-cases.csv`, README, `requirements.txt` (Engine-Commit `ce23c5c`), CHANGELOG 0.5.0.

**Abnahme:** `python main.py` läuft durch; „17 cases agree“; 340 Kanten stimmen mit der Engine überein; zwei Läufe, `git status` bleibt stabil (nach dem ersten Lauf die neu gezeichneten Grafiken in `docs/diagrams/` mitcommitten).

### Erledigt 2026-11-03 (S3b, Version 0.5.0)

- Geprüft (Linux, Python 3.13, Engine `ce23c5c`): `python main.py`; 17 Fälle, 340 Kanten gleich, Rückweg liest 20 Aussagen, SHACL wie bisher (M1 vier Verstöße, M2 konform).
- Die vier Ketten haben kein reines `certain`-Muster; `Certainty` kommt in den Daten nur über `createdBy` in M2 vor. Die Ketten-Docs ändern sich nicht.
- Nicht geprüft: Windows; die Grafiken wurden hier nicht eingecheckt, matplotlib zeichnet auf anderen Versionen andere Bytes.

## S5 — FW-Ontologie

**Stand 2026-10-30:** Die FW-Seite ist erledigt (Commit `15ae05f`): `fw:hasType`, `fw:hasMethod`, `fw:formula`, `fw:implementedBy`, Evidenzklassen, `fw:EqualShareRule`. Offen ist nur `fw:implementedBy` für die Gewichtsregel; die IRI liefert S3a.

## S6 bis S9

Werden vor dem Start ausgearbeitet (Ziel, Uploads, Abnahme), sobald S4 entschieden ist.

---

## Teil D — Offene Punkte

- **SHACL M1** (mit S4b klären; das Hybridmodell ändert die Rollen): `sam:reaches` und `sam:reachedBy` brauchen je ein `rdfs:domain` und ein `rdfs:range`, sonst entspricht M1 den Shapes der Engine nicht und der Runner bricht ab. Möglichkeiten: ein gemeinsames Oberconcept als Domain und Range (zum Beispiel `sam:Entity`); die Oberrolle und ihre drei Subsumtionen weglassen; oder die Shapes der Engine für Oberrollen lockern (Änderung in `amt-engine`). Das ist eine Modellentscheidung; mit S4 klären.
- `fw:implementedBy`: das Triple liegt bereit; an die FW-Ontologie weitergeben, mit einer Release- oder Zenodo-IRI statt des Branch-Links, sobald es eine gibt.
- Typ abgeleiteter Kanten ist geklärt (A4), aber noch nicht mit Allard besprochen (Frage 9 der Review-Seite): eine abgeleitete Kante, deren Vorderglieder Unsicherheit und Vagheit mischen, bekommt `fw:FuzzinessWobbliness`.
- Regionen und Gruppen ohne Zentrumsknoten (9.033 Strings): eigene Klasse oder weglassen?
- **S11 Rückfragen**: (1) Quelle und Lizenz der sieben Profilzeichnungen; (2) `(R?)` in `15/17 or 18 (R?)`: Randscherbe unsicher? `py/weights.py` liest daraus die Entität `18 (R )`; (3) Pfaffenhofen und Westerndorf (70 Träger) fehlen in `cat29.tblkilnsites`, PC.1 nutzt deshalb `Aspiran or Saint-Saturnin`; (4) ob `Saint-Saturnin` = `Jonquières, Saint Saturnin`; (5) Zentren außerhalb der Tabelle (zum Beispiel Rheinzabern) per Wikidata nachladen?; (6) `18_31R` und `31R` sind noch ohne Figur.
- **S12 Rückfragen**: (1) Häufigkeit als Grad (`fw:hasDegreeOfConnection` 0,80 mit Methode `fw:RelativeFrequency`) oder getrennt halten? A4 sagt „Anteile und Häufigkeiten gehören nicht in `amt:weight`“, die FW-Ontologie lässt den Grad für beliebige Methoden zu; (2) Zählung 9070 / 11302: welche Abfrage (ganze Datenbank, nur Gallien?) und Zeichnung für `31`; (3) Karten: moderne Regionen oder römische Provinzen (dann aus Pleiades, DARE oder Wikidata)?
- **S13 Rückfragen**: (1) Lizenz der DARE-Ebenen (Provinzen, Orte) in `klokantech/roman-empire`: im Repository steht keine; vor Veröffentlichung klären; (2) die Latein-Namen der Flüsse sind mein Vorschlag, bitte gegenlesen; (3) die DARE-Provinzen haben keinen klaren Zeitschnitt (Itiner-e: größte Ausdehnung um 150 n. Chr.), reicht das, oder ein bestimmter Stand (zum Beispiel Ende 2. Jh.)?; (4) Pleiades-URIs der römischen Orte (und der Töpfereien, zum Beispiel Lezoux = Ledosum?) verlinken?
- **S14 Rückfragen**: (1) Die fünf Modellgrafiken gibt es jetzt zweimal (matplotlib in `docs/diagrams`, Visuals-Stil in `docs/visuals`); weiterbauen wir künftig beide parallel, oder soll der Visuals-Stil für neue Grafiken (Allards Antworten, Roundtrip AMT Samian → AFE) die Hauptlinie werden? (2) Die Visuals-Seiten haben ein eigenes, schlichtes Layout; sollen sie das Jekyll-Layout der Docs übernehmen?
- **S17 Rückfragen**: Was auf den öffentlichen Seiten noch als Vorschlag oder Platzhalter steht (Statushinweis der Startseite, Namespace `example.org`, `ProductLogic (proposal)` und die Rollennamen in *Vocabulary*, Toy-Gewichte in *Reasoning*, `fw:RelativeFrequency` auf der Visuals-Seite PF.4): bleibt es als gekennzeichneter Vorschlag stehen, oder soll es bis zur Klärung raus?
- **S19 Rückfragen** (Punkte 1 und 2 mit S22 erledigt): (1) Koordinaten von Kräherwald, Rheinzabern, Pfaffenhofen und Westerndorf (`visuals/sql/kilnsites-chains.sql`, Ergebnis nach `visuals/data/kilnsites-extra.csv`); bis dahin zeigen die Zentren-Figuren der Ketten A und B keine Karte; (2) Profilzeichnungen für die Formen 24, 27, 31, 32 und 33; (3) Allard prüft, ob es für die Fälle ohne Kette bessere archäologische Beispiele gibt.
- **FW-Ontologie (Patch zum 0.14.0):** Beschreibung und Beispiele von `fw:EqualShareRule` an die neue Regel anpassen (`Lezoux or Vichy ?` = 0,25); Eintrag für die Methode „Wahrscheinlichkeit basierend auf dem Häufigkeitsanteil“; die Texte stehen im Patch `FW_Ontology`.
- `fw:implementedBy`-Triple: bleibt (siehe oben).
- LICENSE, `CITATION.cff` und eine `RELEASE`-Konstante fehlen noch; mit dem ersten Zenodo-Release nachziehen.
- Namespace `sam:` ist ein Platzhalter; persistente IRI per w3id klären.
- Eine IRI-Landkarte (A6) entsteht, sobald RDF veröffentlicht wird.
