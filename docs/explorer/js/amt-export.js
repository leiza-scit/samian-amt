// ============================================================
// AMT - Academic Meta Tool
// amt-export.js - Export functions: TTL download + Cypher
// Depends on: amt-render.js (_AMT state), amt.js (StrID)
// ============================================================

// ------------------------------------------------------------
// Helper: strip a full IRI down to its local name
// e.g. "http://example.org/samian-amt/ae_vitalis_viii" -> "ae_vitalis_viii"
// ------------------------------------------------------------
var localName = function(iri) {
    var ex = _AMT.prefix;
    if (iri && iri.startsWith(ex)) return iri.slice(ex.length);
    // fallback: take everything after last # or /
    return iri ? iri.replace(/^.*[#\/]/, "") : iri;
};

// ------------------------------------------------------------
// Helper: safe Cypher identifier (Neo4J relationship types and
// node labels must be alphanumeric + underscore)
// ------------------------------------------------------------
var cypherSafe = function(str) {
    return str.replace(/[^a-zA-Z0-9_]/g, "_");
};

// ------------------------------------------------------------
// Helper: trigger a browser file download
// ------------------------------------------------------------
var downloadFile = function(filename, content, mimeType) {
    var blob = new Blob([content], { type: mimeType });
    var url  = URL.createObjectURL(blob);
    var a    = document.createElement("a");
    a.href     = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// ------------------------------------------------------------
// getReasonedGraph: returns graph with reasoning applied if
// reasoning is currently ON, otherwise the original graph.
// Always includes ALL edges (original + inferred).
// ------------------------------------------------------------
var getReasonedGraph = function() {
    // Get original graph (no reasoning) for baseline nodes/edges
    var base     = _AMT.amt.getGraph(false, false);
    // Get reasoned graph for full edge set
    var reasoned = _AMT.amt.getGraph(true, false);
    return {
        nodes: reasoned.nodes,
        edges: reasoned.edges,
        baseEdgeCount: base.edges.length
    };
};

// ------------------------------------------------------------
// ttlLiteral: format a string as a Turtle string literal,
// escaping internal quotes and newlines
// ------------------------------------------------------------
var ttlLiteral = function(str) {
    return '"' + String(str).replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n") + '"';
};

// ------------------------------------------------------------
// ttlDecimal: format a weight as an xsd:decimal literal (the datatype
// amt-shapes.ttl asks for)
// ------------------------------------------------------------
var ttlDecimal = function(w) {
    var v = (typeof w === "number") ? w : parseFloat(w) || 0;
    if (v > 1.0) v = 1.0;
    // always emit with enough precision, never Infinity
    return ttlLiteral(v.toFixed(6)) + "^^xsd:decimal";
};

// ------------------------------------------------------------
// ttlHextuple: the lines for fw:hasType and fw:hasMethod of an edge, each
// ending in " ;" (empty if the edge has neither; the default type is not
// written unless the edge carries it)
// ------------------------------------------------------------
var ttlHextuple = function(e, width) {
    var out = [];
    var pad = function(name) { while (name.length < width) name += " "; return name; };
    if (e.type)   out.push("    " + pad("fw:hasType")   + "<" + e.type   + "> ;");
    if (e.method) out.push("    " + pad("fw:hasMethod") + "<" + e.method + "> ;");
    return out;
};

// ------------------------------------------------------------
// exportTTL: full standalone Turtle serialisation
//
// Sections:
//   1. Prefixes
//   2. AMT meta-ontology (vocabulary classes & properties)
//   3. Domain model (Concepts, Roles, Axioms) – read from LocalStore
//   4. Instance data (original assertions)
//   5. Inferred assertions (reasoning results, tagged amt:inferred)
// ------------------------------------------------------------
var exportTTL = function() {
    var ex  = _AMT.prefix;
    var AMT = "http://academic-meta-tool.xyz/vocab#";
    var RDF  = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
    var RDFS = "http://www.w3.org/2000/01/rdf-schema#";
    var XSD  = "http://www.w3.org/2001/XMLSchema#";

    var rg   = getReasonedGraph();
    var nodes = rg.nodes;
    var edges = rg.edges;
    var baseEdgeCount = rg.baseEdgeCount;

    var lines = [];
    var sep   = function() { lines.push(""); };

    // ── 1. Prefixes ────────────────────────────────────────────
    lines.push("@prefix amt:  <" + AMT  + "> .");
    lines.push("@prefix rdf:  <" + RDF  + "> .");
    lines.push("@prefix rdfs: <" + RDFS + "> .");
    lines.push("@prefix xsd:  <" + XSD  + "> .");
    if (edges.some(function(e) { return e.type || e.method; })) {
        lines.push("@prefix fw:   <http://w3id.org/fw_ontology/> .");
    }
    lines.push("@prefix sam:  <"  + ex   + "> .");
    sep();

    // ── 2. AMT meta-ontology ───────────────────────────────────
    lines.push("# ── AMT Meta-Ontology ────────────────────────────────────");
    sep();

    lines.push("amt:Concept");
    lines.push("    rdfs:subClassOf rdfs:Class .");
    sep();

    lines.push("amt:Role");
    lines.push("    rdfs:subClassOf rdf:Property .");
    sep();

    lines.push("amt:Axiom");
    lines.push("    rdfs:subClassOf rdfs:Class .");
    sep();

    lines.push("amt:InferenceAxiom");
    lines.push("    rdfs:subClassOf amt:Axiom .");
    sep();

    lines.push("amt:IntegrityAxiom");
    lines.push("    rdfs:subClassOf amt:Axiom .");
    sep();

    lines.push("amt:RoleChainAxiom");
    lines.push("    rdfs:subClassOf amt:InferenceAxiom .");
    sep();

    lines.push("amt:InverseAxiom");
    lines.push("    rdfs:subClassOf amt:InferenceAxiom .");
    sep();

    lines.push("amt:DisjointAxiom");
    lines.push("    rdfs:subClassOf amt:IntegrityAxiom .");
    sep();

    lines.push("amt:SelfDisjointAxiom");
    lines.push("    rdfs:subClassOf amt:IntegrityAxiom .");
    sep();

    lines.push("amt:Logic");
    lines.push("    rdfs:subClassOf rdfs:Class .");
    sep();

    lines.push("amt:SubsumptionAxiom");
    lines.push("    rdfs:subClassOf amt:InferenceAxiom .");
    sep();

    ["GoedelLogic", "ProductLogic", "LukasiewiczLogic", "EinsteinProduct", "GeometricMean", "HamacherProduct"].forEach(function(l) {
        lines.push("amt:" + l);
        lines.push("    rdf:type amt:Logic .");
        sep();
    });

    // ── 3. Domain model from LocalStore ────────────────────────
    lines.push("# ── Domain Model ─────────────────────────────────────────");

    // Helper: read from LocalStore using known predicate IRIs
    var P_TYPE        = RDF  + "type";
    var P_LABEL       = RDFS + "label";
    var P_SUBCLASSOF  = RDFS + "subClassOf";
    var P_DOMAIN      = RDFS + "domain";
    var P_RANGE       = RDFS + "range";
    var C_CONCEPT     = AMT  + "Concept";
    var C_ROLE        = AMT  + "Role";
    var P_PLACEHOLDER = AMT  + "placeholder";
    var P_INSTANCEOF  = AMT  + "instanceOf";
    var P_ANT1        = AMT  + "antecedent1";
    var P_ANT2        = AMT  + "antecedent2";
    var P_ANT         = AMT  + "antecedent";
    var P_CONS        = AMT  + "consequent";
    var P_LOGIC       = AMT  + "logic";
    var P_INV         = AMT  + "inverse";
    var P_ROLE1       = AMT  + "role1";
    var P_ROLE2       = AMT  + "role2";

    // Helper: shorten an IRI to prefixed form for output
    var pfx = function(iri) {
        if (!iri) return iri;
        if (iri.startsWith(ex))  return "sam:" + iri.slice(ex.length);
        if (iri.startsWith(AMT)) return "amt:" + iri.slice(AMT.length);
        if (iri.startsWith(RDF)) return "rdf:" + iri.slice(RDF.length);
        if (iri.startsWith(RDFS))return "rdfs:"+ iri.slice(RDFS.length);
        if (iri.startsWith(XSD)) return "xsd:" + iri.slice(XSD.length);
        return "<" + iri + ">";
    };

    // 3a. Concepts
    sep();
    lines.push("# Concepts");
    var conceptIRIs = LocalStore.subjectsOf(P_TYPE, C_CONCEPT);
    conceptIRIs.forEach(function(c) {
        var label       = LocalStore.objectOf(c, P_LABEL);
        var placeholder = LocalStore.objectOf(c, P_PLACEHOLDER);
        lines.push(pfx(c));
        lines.push("    rdf:type          amt:Concept ;");
        if (label)       lines.push("    rdfs:label        " + ttlLiteral(label) + " ;");
        if (placeholder) lines.push("    amt:placeholder   " + ttlLiteral(placeholder) + " ;");
        // remove trailing semicolon from last predicate
        lines[lines.length - 1] = lines[lines.length - 1].replace(/ ;$/, " .");
        sep();
    });

    // 3b. Roles
    lines.push("# Roles");
    var roleIRIs = LocalStore.subjectsOf(P_TYPE, C_ROLE);
    roleIRIs.forEach(function(r) {
        var label  = LocalStore.objectOf(r, P_LABEL);
        var domain = LocalStore.objectOf(r, P_DOMAIN);
        var range  = LocalStore.objectOf(r, P_RANGE);
        lines.push(pfx(r));
        lines.push("    rdf:type      amt:Role ;");
        if (label)  lines.push("    rdfs:label    " + ttlLiteral(label) + " ;");
        if (domain) lines.push("    rdfs:domain   " + pfx(domain) + " ;");
        if (range)  lines.push("    rdfs:range    " + pfx(range)  + " ;");
        lines[lines.length - 1] = lines[lines.length - 1].replace(/ ;$/, " .");
        sep();
    });

    // 3c. Axioms, as the reasoner reads them (role chains as RDF lists)
    lines.push("# Axioms");
    var KEYS = ["antecedent", "inverse", "consequent", "logic", "logicParameter",
                "subRole", "superRole", "role1", "role2", "role"];
    _AMT.amt.getAxioms().forEach(function(a) {
        var props = [];
        props.push("    rdf:type          amt:" + a.type);
        if (a.type === "RoleChainAxiom" && a.antecedents && a.antecedents.length) {
            props.push("    amt:antecedents   ( " + a.antecedents.map(pfx).join(" ") + " )");
        }
        KEYS.forEach(function(k) {
            if (a[k] === undefined) return;
            if (k === "logicParameter") props.push("    amt:logicParameter " + ttlLiteral(a[k]) + "^^xsd:decimal");
            else props.push("    amt:" + k + " ".repeat(Math.max(1, 17 - k.length)) + pfx(a[k]));
        });
        lines.push(pfx(a.iri));
        lines.push(props.join(" ;\r\n") + " .");
        sep();
    });

    // ── 4. Instance data ───────────────────────────────────────
    lines.push("# ── Instances ────────────────────────────────────────────");
    sep();
    nodes.forEach(function(n) {
        lines.push(pfx(n.id));
        lines.push("    amt:instanceOf  " + pfx(n.concept) + " ;");
        lines.push("    rdfs:label      " + ttlLiteral(n.label) + " .");
        sep();
    });

    // ── 5. Assertions (original) ───────────────────────────────
    lines.push("# ── Original Assertions ──────────────────────────────────");
    sep();
    for (var j = 0; j < Math.min(baseEdgeCount, edges.length); j++) {
        var e = edges[j];
        var bnode = "_:a" + (j + 1);
        lines.push(bnode);
        lines.push("    rdf:subject   " + pfx(e.from) + " ;");
        lines.push("    rdf:predicate " + pfx(e.role) + " ;");
        lines.push("    rdf:object    " + pfx(e.to)   + " ;");
        lines.push("    amt:weight    " + ttlDecimal(e.width) + (e.type || e.method ? " ;" : " ."));
        var hx = ttlHextuple(e, 14);
        hx.forEach(function(l, n) { lines.push(n === hx.length - 1 ? l.replace(/ ;$/, " .") : l); });
        sep();
    }

    // ── 6. Inferred assertions ─────────────────────────────────
    if (edges.length > baseEdgeCount) {
        lines.push("# ── Inferred Assertions (Reasoning) ─────────────────────");
        sep();
        for (var k = baseEdgeCount; k < edges.length; k++) {
            var ei = edges[k];
            var bi = "_:i" + (k - baseEdgeCount + 1);
            lines.push(bi);
            lines.push("    rdf:subject    " + pfx(ei.from) + " ;");
            lines.push("    rdf:predicate  " + pfx(ei.role) + " ;");
            lines.push("    rdf:object     " + pfx(ei.to)   + " ;");
            lines.push("    amt:weight     " + ttlDecimal(ei.width) + " ;");
            ttlHextuple(ei, 15).forEach(function(l) { lines.push(l); });
            if (ei.provenance && ei.provenance.length) {
                lines.push('    amt:inferred   "true"^^xsd:boolean ;');
                lines.push("    amt:provenance " + ei.provenance.map(pfx).join(", ") + " .");
            } else {
                lines.push('    amt:inferred   "true"^^xsd:boolean .');
            }
            sep();
        }
    }

    var content = lines.join("\r\n").replace(/Infinity/g, "1.000000");
    downloadFile("amt-graph-standalone.ttl", content, "text/turtle");
    console.log("Standalone TTL export: " + nodes.length + " nodes, " +
                edges.length + " edges (" + (edges.length - baseEdgeCount) + " inferred)");
};

// ------------------------------------------------------------
// buildCypher: the graph as it is shown in the Explorer, as Cypher for Neo4j 5.
//
// Shown = one direction only (inverse roles stay out), the generic role only if its switch is on, and with
// reasoning on the inferred edges too. One statement per node and per relationship, each ended by ";", so the
// script can be pasted into Neo4j Browser or run with cypher-shell and run again without duplicates (MERGE).
//   node label           the concept (Potform, InformationCarrier, ProductionCentre, Actor)
//   node properties      id (local name), iri, name
//   relationship type    the role in UPPER_SNAKE_CASE (hasProductionCentre -> HAS_PRODUCTION_CENTRE)
//   relationship props   weight, role, fwType, method (if any), inferred, source (the source string, if any)
// ------------------------------------------------------------
var cypherString = function(s) { return JSON.stringify(String(s)); };
var cypherRel = function(role) { return cypherSafe(localName(role).replace(/([a-z0-9])([A-Z])/g, "$1_$2")).toUpperCase(); };

var buildCypher = function() {
    var nodes = _AMT.thisNodes, edges = _AMT.thisEdges;
    var byId = {};
    nodes.forEach(function(n) { byId[n.id] = n; });
    var nInf = edges.filter(function(e) { return e.inferred; }).length;
    var out = [];
    out.push("// samian-amt: " + _AMT.file.replace(/\.ttl$/, "") + (_AMT.reasoning ? ", reasoning on" : ", reasoning off"));
    out.push("// Cypher for Neo4j 5, the graph as shown in the Explorer: " + nodes.length + " nodes, " + edges.length +
             " relationships (" + (edges.length - nInf) + " asserted, " + nInf + " inferred).");
    out.push("// sam: = " + _AMT.prefix);
    out.push("");
    var labels = {};
    nodes.forEach(function(n) { labels[cypherSafe(localName(n.concept))] = true; });
    Object.keys(labels).sort().forEach(function(l) {
        out.push("CREATE CONSTRAINT " + l.toLowerCase() + "_id IF NOT EXISTS FOR (n:" + l + ") REQUIRE n.id IS UNIQUE;");
    });
    out.push("");
    nodes.forEach(function(n) {
        out.push("MERGE (n:" + cypherSafe(localName(n.concept)) + " {id: " + cypherString(localName(n.id)) + "}) SET n.iri = " +
                 cypherString(n.id) + ", n.name = " + cypherString(n.label) + ";");
    });
    out.push("");
    edges.forEach(function(e) {
        var a = byId[e.from], b = byId[e.to];
        if (!a || !b) return;
        var props = ["r.weight = " + (Math.round(e.weight * 1000000) / 1000000),
                     "r.role = " + cypherString("sam:" + localName(e.role)),
                     "r.fwType = " + cypherString(localName(e.type || "http://w3id.org/fw_ontology/Vagueness")),
                     "r.inferred = " + (e.inferred ? "true" : "false")];
        if (e.method) props.push("r.method = " + cypherString(localName(e.method)));
        if (e.source) props.push("r.source = " + cypherString(e.source));
        out.push("MATCH (a:" + cypherSafe(localName(a.concept)) + " {id: " + cypherString(localName(a.id)) + "}), (b:" +
                 cypherSafe(localName(b.concept)) + " {id: " + cypherString(localName(b.id)) + "}) MERGE (a)-[r:" +
                 cypherRel(e.role) + "]->(b) SET " + props.join(", ") + ";");
    });
    out.push("");
    out.push("// Look at it: MATCH (a)-[r]->(b) RETURN a, r, b;");
    return out.join("\n").replace(/Infinity/g, "1.0") + "\n";
};
