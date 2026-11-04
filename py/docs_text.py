"""Prose of the documentation pages. Tables and derivations are generated in step_docs.py.

British English. Keep sentences short: the pages are read by archaeologists who
review the model, not by reasoner developers.
"""

REPO = "https://github.com/leiza-scit/samian-amt"      # planned home of the repository
BLOB = REPO + "/blob/main/"

STATUS = """> **Status: working draft.** The namespace is a placeholder. The weights follow the
> rule of the source paper (see Weights). The logic operator (product) and the role names are proposals,
> except `hasType` / `isTypeOf`, which were agreed with Allard Mees. Three real chains from the Samian Research data
> are modelled (see Chains)."""

INDEX_INTRO = """A deliberately small [AMT](http://academic-meta-tool.xyz/) domain model for one chain:

    [Potform] -- [InformationCarrier] -- [ProductionCentre] -- [Actor]

The model asserts three kinds of links (a carrier has a type, a carrier is attributed to a centre,
an actor works at a centre). A role-chain reasoner derives the links that follow from them: which
potforms are associated with which centres, which carriers with which actors, which potforms with
which actors. Each derived link can be read from both ends."""

IDEA = """| Rule | Reads as |
|---|---|
| `[Potform]>>[ProductionCentre]` | a carrier of this type is attributed to that centre |
| `[InformationCarrier]>>[Actor]` | the carrier is attributed to a centre at which the actor worked |
| `[Potform]>>[Actor]` | a carrier of this type is attributed to a centre at which the actor worked |"""

WHY_INVERSES = """AMT composes edges head to tail: the target of one edge must be the source of the next. The
chain runs Potform, InformationCarrier, ProductionCentre, Actor. Of the three links that the source
data asserts, only one points along that chain:

| Asserted role | Points | Along the chain? |
|---|---|---|
| `hasType` | InformationCarrier to Potform | no, against it |
| `hasProductionCentre` | InformationCarrier to ProductionCentre | yes |
| `worksAt` | Actor to ProductionCentre | no, against it |

Without inverses nothing composes: the first rule starts at a Potform, but no asserted edge leaves a
Potform. `hasType` therefore gets its inverse `isTypeOf` (agreed with Allard Mees), and `worksAt` gets
`hasWorker`. Every rule uses at least one inverse. The derived roles get inverses too, so that an
association can be asked from either end: "which centres go with this potform?" and "which potforms
go with this centre?"."""

CAVEATS = """1. **An association, not an attribution.** `carrierToActor` says that the actor worked at the
   centre to which the carrier is attributed. It does not say that the actor made the carrier. Both
   have time intervals in the source model; the chain does not compare them.
2. **Several paths keep the best one.** When more than one path leads to the same pair, AMT keeps the
   maximum weight. A potform with many carriers at one centre gets the weight of the best single
   carrier, not a weight that grows with the number of carriers.
3. **The third rule is written over the base roles.** `potformToActor` is `isTypeOf o hasProductionCentre
   o hasWorker`, not `potformToCentre o hasWorker`. For the associative operators (Goedel, Product,
   Einstein, Hamacher) both give the same degree; for the n-ary geometric mean they do not."""

WEIGHTS_ANSWER = """**Yes, for inverse roles the weight is the same in both directions.** If a carrier is of a potform
with degree 0.9, then the potform is the type of that carrier with degree 0.9. This is how AMT defines
an inverse, and it is also what the statement means."""

WEIGHTS_WHY = """1. **It is the rule of the AMT ontology.** The `amt:InverseRule` states: *"Add an edge (b -inverse-> a)
   with weight w."* The inverse edge copies the weight of its antecedent.
2. **It is the same statement.** An AMT edge is a statement about a pair with a degree of truth, read as
   a fuzzy relation. The inverse of a fuzzy relation is its transpose with the same membership degrees.
   `Carrier hasType Potform (0.9)` and `Potform isTypeOf Carrier (0.9)` are one statement read from two
   ends. If the two degrees differed, they would not be inverses but two different statements.
3. **The derived roles behave the same way.** All six fuzzy-logic operators of AMT (Goedel, Product,
   Lukasiewicz, Einstein, Geometric mean, Hamacher) are symmetric in their arguments. A chain read
   backwards uses the same weights, so `potformToCentre` and `centreToPotform` carry the same degree,
   and so do the other two pairs."""

WEIGHTS_BREAK = """The symmetry holds because the weight is a degree of truth. Other quantities look like weights
and are **not** all symmetric. Apart from the first row they should not be stored in `amt:weight`:

| Quantity | Example | Same in both directions? | Where it belongs |
|---|---|---|---|
| Degree of truth or certainty of the statement | the attribution of a carrier to a centre holds with 0.5 (recorded as uncertain) | yes | `amt:weight` |
| Conditional share | 40 % of the carriers of a potform are attributed to a centre, but only 10 % of that centre's carriers are of this potform | no | a separate measure on the pair |
| Normalised alternatives | a carrier has two possible centres, weights 0.5 and 0.5 so that they sum to 1 | no: the sum is taken per source node, so the inverse edges would sum differently | normalise when reading, or keep as a separate measure |
| Number of supporting carriers | twelve carriers support the association of a potform with a centre | yes, but it is a count, not a degree | a separate measure |"""

WEIGHTS_RULES = """1. **Assert one direction only.** Assert the roles in the direction of the source data (`hasType`,
   `hasProductionCentre`, `worksAt`) and let the inverse axioms create the other direction. If both
   directions are asserted with different weights, the data contradicts itself.
2. **Take the weight from the rule.** `py/weights.py` computes it from the source string. AND keeps the
   full weight for every entity (1.0, or 0.5 with a question mark); OR shares it (one over the number of
   alternatives, one more with a question mark). Nothing is normalised afterwards.
3. **Put shares and counts elsewhere.** If the question "how many carriers" or "what fraction" matters,
   compute it as its own measure on the pair, in the direction in which it is asked.
4. **Check the symmetry.** A consistency check (a SPARQL query on the reasoned graph) can report every
   pair of inverse edges whose weights differ. It should return nothing."""

WEIGHTS_OPEN = """The rule halves the weight at a question mark (decided with Allard Mees, 2026-11-04): "A or B?" gives
one quarter to each, "A and B?" one half to each, because under AND both hold and the question mark is
the only doubt. Before that day the rule counted the question mark as one more possibility (one third
each for "A or B?"). The weight stays symmetric under inversion either way."""

# Allard Mees's answers to Memo 0.5.0 (2026-11-04), keyed by question number. Shown on REVIEW.md.
REVIEW_ANSWERS = {
    1: "Association: the actor worked at the centre. Role names stay without any hint of authorship.",
    2: "No. Time intervals are ignored for now (too coarse); the order of centres is only a rough chronology.",
    3: "One degree of truth per statement.",
    4: "Yes: a repertoire of forms attested at the centre.",
    5: "No. The number of carriers does not matter; AMT keeps the best single path.",
    6: "Understandable as they are; no renaming.",
    7: "ActorEntity and Actor may be merged (one concept `Actor`).",
    8: "Both. Stamp found at a production site: `hasProductionCentre` is direct (the list of production sites decides). "
       "Otherwise derived through a new role \"same stamp\" (carrier, identical stamp on another sherd, centre of that sherd). "
       "Weaker derivations: a name found on a sherd that is not geometrically identical (homonym risk), and similarity of "
       "distributions (rarely documented). Distribution-based derivations are weaker than direct ones.",
    9: "Product logic.",
    10: "The question mark refers to the whole preceding chain and weakens it once more, without saying whether because of A or B. "
        "A trailing question mark always weakens the statement. Memo 0.7.0 (confirmed by Florian Thiery in Memo 0.8.0): it halves the weight "
        "of every entity; the rule of the paper (one more possibility) was \"the wrong approach\". Frequency shares ignore the question mark.",
    11: "Open pattern question confirmed in part: inherited patterns only in the derived case. A question mark must not follow "
        "a potform with OR; three such faulty entries exist and will be cleaned in the database (212025, 213077, 210355).",
    12: "A combined form such as 18/31 is one type, as in archaeological practice; it is not \"dish or bowl\".",
    13: "Assignments such as \"South Gaul?\" are not usable for this model.",
    14: "Yes: the order and spelling of the source string must be kept (done through fw:TextEvidence).",
}

REVIEW_INTRO = """These are the points where the archaeological reading decides the model. Each question says what
is proposed and what would change if the answer is no."""

REVIEW_QUESTIONS = [
    ("Is \"associated with\" the right reading of the three `>>` roles?",
     "`carrierToActor` says only that the actor worked at the centre to which the carrier is attributed.",
     "If it should read as an attribution, the chain needs more evidence than a shared centre (for example "
     "the actor's period). If it stays an association, the role names should avoid any implication of authorship."),
    ("Should time enter the chain?",
     "Carrier and actor both have time intervals in the source model. At present the chain ignores them.",
     "An overlap of the two intervals can become one more link in the chain, with its own degree."),
    ("What does the weight mean: a possibility degree or a probability?",
     "A degree of truth per statement, computed by the rule of the source paper (see the Weights page).",
     "If alternatives must sum to 1, the weights become directional and shares move into a separate measure."),
    ("Is `actorToPotform` a useful reading?",
     "It is the forms attested at the centre where the actor worked: a candidate repertoire, not the actor's own.",
     "If it misleads, drop the role and its inverse axiom; the other two associations are unaffected."),
    ("Does one potform with many carriers at a centre need more than the best path?",
     "No: AMT keeps the best single path.",
     "If the number of carriers should count, it becomes a separate measure next to the weight."),
    ("Are the role names acceptable?",
     "`hasType` / `isTypeOf` are agreed. `hasProductionCentre`, `worksAt`, `hasWorker` and the six derived "
     "names are proposals.",
     "Renaming touches only the ontology; the documentation is generated from it."),
    ("Is it right to collapse ActorEntity and Actor into one concept?",
     "Yes for this model: the chain only needs the person who works at a centre.",
     "If the stamp name (ActorEntity) must stay distinct from the person (Actor), one more concept and "
     "one more link enter the chain."),
    ("Is the carrier-centre link asserted (M1) or derived from the actor (M2)?",
     "M1: asserted, as in the data export. In the data the centre string belongs to the potter: every one of "
     "the 1,375 potters in the centre exports has exactly one, and the carriers compared (1,072 potters) share "
     "identical edges. The source paper says the carrier-centre relation follows from the potter-centre relation.",
     "M2 asserts only the carrier-potter link (crisp) and derives the carrier-centre link. That removes the "
     "double counting of the same doubt (see question 9) and needs a certain stamp attribution, which the "
     "2,777 carriers with an uncertain potter name do not have."),
    ("Which logic operator: product or Goedel?",
     "Product, as in the role-chain axioms of the source paper. Under M1 a statement that is inherited from "
     "the actor enters the chain twice: for Ve- i the carrier-actor degree is 0.25 under product and 0.5 under Goedel.",
     "Goedel (minimum) avoids the double count but ignores how many doubtful steps a chain has. M2 avoids it "
     "under both operators."),
    ("Is a question mark one more possibility?",
     "Superseded on 2026-11-04: the question mark halves the weight (\"A or B?\" gives 0.25 each). The former proposal "
     "(as in the paper) gave one third to A and B and left one third to \"neither\".",
     "The former rule is available in the history of this file; the FW type and the pattern do not change."),
    ("Which patterns occur on which relation?",
     "As listed on the Weights page. For the carrier-centre relation only the question mark is listed, but "
     "the exports also carry AND and OR there (inherited from the actor).",
     "If the carrier-centre relation is derived (M2) the inherited patterns disappear from it."),
    ("Are combined forms such as 18/31 one type?",
     "Yes (source paper, figure 6): a slash joins two numbers into one type, an OR separates alternatives. "
     "Generic forms such as \"dish or bowl?\" are modelled like any other alternative.",
     "If a generic form should be a class of its own, the possibilities would be counted differently."),
    ("What about centre strings that name more entities than the model has nodes?",
     "The weight is computed from the whole string; an entity without a centre node gets no edge. This happens "
     "in 9,033 of 45,685 centre strings of the exports (regions, groups, centres missing in the mapping); every "
     "one of the 95,819 existing centre edges carries the weight the rule gives.",
     "Creating nodes for regions and groups would close the gap and needs a decision on their class."),
    ("Does the hextuple have to keep the order and spelling of the source string?",
     "No. The round trip from the hextuples back to the string is lossless except for the order of the "
     "entities and the spelling; weight, FW type and the number of edges decide the pattern.",
     "If the order matters, the original string becomes a seventh element or a property of the statement."),
]



ROUNDTRIP_INTRO = """The AFE coin data and the AMT meet in the same question: how is a vague or uncertain statement written down?
AFE answers with containers (a value and a confidence), AMT with a hextuple (a weight and an FW type). Karsten Tolle's
round trip goes **AFE → AMT → AFE** (see [AFE → AMT → AFE](afe-roundtrip.html)). This page shows the other direction, **AMT → AFE → AMT**: the three chains of this
repository are written as the AFE container pattern with two SPARQL queries, read back with a third, and compared with
what they started as."""

ROUNDTRIP_HONEST = """> **What the AFE side is.** The AFE coin data know coins, mints and denominations, not potforms or production centres.
> The AFE side of this round trip is therefore a *rebuilt pattern*: the container classes and properties of the AFE
> (`fw:VagueResourceValue`, `fw:UncertainResourceValue`, `fw:FuzzinessWobblinessResourceValue`, `skos:Collection`,
> `skos:member`, `rdf:value`, `fw:hasConfidence`) with the `sam:` roles as predicates. It is not AFE data."""

ROUNDTRIP_RULES = """The form follows from `fw:hasType` and the weight alone. The source string is not needed (AFE has none).

| FW type and weight | Pattern | AFE form |
|---|---|---|
| `fw:Certainty` | certain | the value directly on the subject |
| `fw:Uncertainty` | `A?` | one `fw:UncertainResourceValue` with `rdf:value` and `fw:hasConfidence` |
| `fw:Vagueness`, weight 1 | `A and B` | **one container per entity** (`fw:VagueResourceValue`, one member, confidence 1) |
| `fw:Vagueness`, weight below 1 | `A or B` | **one container** with a member per entity, each with its share |
| `fw:FuzzinessWobbliness`, weight 0.5 | `A and B?` | one container per entity (`fw:FuzzinessWobblinessResourceValue`, confidence 0.5) |
| `fw:FuzzinessWobbliness`, weight below 0.5 | `A or B?` | one container with a member per entity |

For a known number of edges, weight and type separate the four patterns (`py/weights.py`, self-test), so reading
AND and OR back from them is exact for statements made by the rule."""

ROUNDTRIP_LOSSES = """The AFE pattern has no place for the source string, the method of the weight, the observed frequency shares or the
attribution of model M2. They are **documented, not carried**: the round trip does not smuggle them through, and the test
says exactly what differs. `fw:hasMethod` comes back as `fw:AFEAssignment`, because that is what the weight now is: a value
that was assigned on the AFE side."""

ROUNDTRIP_OPEN = """These points are for Karsten Tolle and Allard Mees; the repository works either way.

1. Is it legal in AFE to have **two containers on the same predicate** of one subject (the AND pattern)? If not, AND needs a
   different form, for example one container with a member per entity and a marker.
2. Does an FW container have to sum its confidences to 0.5, or is a confidence per member of 0.5 (AND with `?`) fine?
3. Should AND be visible in AFE other than through weight and type?"""


ROUNDTRIP_CONSTRUCT = """A `SELECT` query returns a table. A `CONSTRUCT` query returns a **graph**: it has a *template* (the triples to write) and
a `WHERE` pattern (what to look for). For every way the pattern matches, the variables are filled into the template and
the triples are added to the result. A triple whose variables are not all bound is skipped. That is the whole mechanism,
and it is why one query can write several shapes at once: a variable that stays unbound in one branch simply drops that
part of the template."""

ROUNDTRIP_TRICKS = """Four details of the two queries are worth knowing:

* **`UNION` branches.** The first query has one branch for the nodes and one for the statements; the second has one branch
  for each AFE form (collection, one value, direct value) and one for the nodes. Each branch binds only the variables its form
  needs.
* **The unbound-variable trick.** `BIND(IF(?kind = "direct", ?o, ?unbound) AS ?direct)` binds `?direct` only when the statement is
  certain. `?unbound` is never bound, so the `IF` yields an error and `BIND` leaves `?direct` unbound in all other cases; the
  template line `?s ?p ?direct` then writes nothing for them.
* **Generated IRIs.** SPARQL cannot hand one blank node to several result rows, but an OR container needs to be *one* node
  with several members. The first query therefore builds an IRI from subject, predicate (and object for AND), so that all rows
  of one OR reach the same container; the step turns these IRIs into blank nodes afterwards. In the second query
  `BIND(BNODE() AS ?edge)` gives every row its own statement node, which is what a reified statement needs.
* **A lookup table.** `VALUES (?cType ?fwType) { ... }` maps the AFE container class to the FW type, so the type is
  data, not code."""


AFE_RT_INTRO = """> **State of the package, version 3 (2026-11-03).** This page shows the round trip as Karsten Tolle's package describes it,
> run on his coin data. His answers to the open questions at the end are still pending; the page is updated when they arrive.

The other page, [AMT → AFE → AMT](roundtrip.html), starts with the AMT data of this repository and rebuilds an AFE pattern.
This page starts with **real AFE data**: coins of the AFE with the container pattern for Authority (the issuing power).
Two SPARQL queries turn the containers into AMT hextuples and back. The question is the same: does a vague or uncertain
statement come back as it went?"""

AFE_RT_CASES = """An AFE value has one of four forms. Each form has exactly one way into AMT:

| Case | AFE form | AMT |
|---|---|---|
| 1 | a container with members: `fw:VagueResourceValue` or `fw:FuzzinessWobblinessResourceValue`, also a `skos:Collection` | one hextuple per member; weight = `fw:hasConfidence` of the member; `fw:hasType` from the container class |
| 2 | one uncertain value: `fw:UncertainResourceValue` with `rdf:value` and `fw:hasConfidence` | one hextuple, `fw:Uncertainty` |
| 3 | a certain value directly on the coin | one hextuple, weight 1.0, `fw:Certainty` |
| 4 | `nm:uncertain_value`: unknown (Authority only) | the coin becomes a node without an edge |

Every hextuple gets `fw:hasMethod fw:AFEAssignment`: in the AFE a person or the system enters the confidence; it is not a
calculation rule. (`fw:EqualShareRule` belongs to the Samian source strings.) The way back reads the type from the edge and
writes the container; a coin without an edge gets `nm:uncertain_value` again."""

AFE_RT_RESULT = """Five coins of the AFE come back equal: four exactly the same, one (16048) on the **top class**. The AFE writes
`fw:UncertainValue` where the way back writes `fw:UncertainResourceValue`; the values are IRIs, so the resource class is the
fitting one, and the AFE side agreed that `…Value` and `…ResourceValue` are the same on the top level. The same holds for the
constructed coin 80001.

If the AMT engine 0.7.0 or newer is installed, the five coins also go through the engine (reasoning) before the way back, and
the result is the same."""

AFE_RT_EDGES = """Four constructed coins (`data/afe/afe-edge-cases.ttl`, numbers 90001 to 90004) test the border of the pattern. They
are part of the test: the step fails if one of them behaves differently from what is written here.

| Coin | Case (memo) | AFE input | Result | Why |
|---|---|---|---|---|
| 90001 | A | uncertainty written as a collection with one member | different | AMT has one edge for it, so the way back writes a plain container: the AFE form is not recoverable |
| 90002 | B | `fw:VagueValue` (without "Resource") | same on the top class | the way back writes `fw:VagueResourceValue` |
| 90003 | C | vague with one member at confidence 1.0 | same | the type is on the edge; only `fw:Certainty` at 1.0 becomes a direct value |
| 90004 | D | two containers of the same kind on one property | different | they become one container with both members |

Coins 80001 to 80003 test `nmo:hasDenomination` and `nmo:hasMint` in the same patterns. **Their property names are assumed**
from Nomisma and the three coins are constructed; the AFE data seen so far have only `nmo:hasAuthority`."""

AFE_RT_LOST = """* **Case A and case D.** The AFE form of an uncertainty as a one-member collection, and the split into several containers on
  one property, are not carried by the hextuples (see the table above).
* **Top class.** `…Value` becomes `…ResourceValue` (agreed as equal).
* **Container identity.** Containers are blank nodes; they come back as new blank nodes, the structure is the same.
* **Number spelling.** `0.25` and `0.250000` are the same `xsd:decimal`; the engine writes six places.
* **Source texts.** There are none in the AFE data, so nothing is lost here (unlike the Samian strings)."""

AFE_RT_QUESTIONS = """For Karsten Tolle (memo of 2026-11-03, section 8):

1. Are `nmo:hasDenomination` and `nmo:hasMint` the property names in the AFE, with `nm:` concepts as values?
2. How are coins without `nmo:hasAuthority` marked as unknown, and is it only Authority that has `nm:uncertain_value`?
3. Is the confidence property `fw:hasConfidence` (as in the data) or `fw:hasConfidenceLevel`?
4. Which class does a certain value get when it has to sit in a container?
5. Is there a rule for the weights of a container (sum, equal share), or are they free?
6. How should other properties with only the "uncertain" flag be read?

From the other round trip, still open: may one subject have **two containers on the same predicate** (several `nmo:hasAuthority`
edges, each with its own container)? Karsten's earlier answer says: today at most one container per property, in future
several."""
