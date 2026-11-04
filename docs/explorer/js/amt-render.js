// ============================================================
// AMT - Academic Meta Tool, Explorer of samian-amt
// amt-render.js - graph rendering, node/edge styling, UI logic
// Depends on: amt.js, amt-export.js, vis.js, jQuery, Materialize
//
// Adapted from the Explorer of amt-engine (MIT licence, see ../LICENSE-amt-engine):
//   * the nodes sit in columns that follow the chain Potform -> InformationCarrier -> ProductionCentre -> Actor
//   * every concept has a fixed colour, explained in the legend
//   * the picture shows one direction only (inverse roles stay in the Turtle file) and hides the generic
//     role "reaches" unless the legend switch is on
//   * click a node or an edge: details panel; the neighbourhood stays in colour, the rest fades
//   * Cypher dialog, PNG and SVG export, a link that remembers chain, reasoning and label mode
// ============================================================

// ------------------------------------------------------------
// Global AMT state
// ------------------------------------------------------------
var _AMT = {};
_AMT.prefix    = "http://example.org/samian-amt/";
_AMT.graph     = {};
_AMT.edit      = false;
_AMT.thisNodes = [];
_AMT.thisEdges = [];
_AMT.inverse   = false;
_AMT.mode      = "potter";
_AMT.reasoning = false;
_AMT.rdf       = "";
_AMT.file      = "chain-A.ttl";
_AMT.info      = "";            // one line about the chain, from data/examples.json
_AMT.labels    = "names";       // names | weights | none
_AMT.generic   = false;         // show the generic role (reaches) as well
_AMT.selected  = null;          // { kind: "node" | "edge", id }

// ------------------------------------------------------------
// Concepts: one fixed colour, one column and one plain explanation each.
// The order is the direction of the chain.
// ------------------------------------------------------------
var AMT_CONCEPTS = [
    { name: "Potform",            bg: "#4a9a82", border: "#184838", font: "#000", gloss: "vessel form (type)" },
    { name: "InformationCarrier", bg: "#e8b878", border: "#8a5a1a", font: "#000", gloss: "stamped vessel or sherd" },
    { name: "ProductionCentre",   bg: "#8fa3c4", border: "#2c3a52", font: "#000", gloss: "kiln site" },
    { name: "Actor",              bg: "#c8833f", border: "#8a5a1a", font: "#000", gloss: "potter" }
];
var AMT_FALLBACK = { bg: "#cfe6dc", border: "#1f6b57", font: "#000", gloss: "" };

var amtLocal = function(iri) {
    return (typeof iri === "string") ? iri.replace(/^.*[#\/]/, "") : iri;
};

var conceptIndex = function(conceptIri) {
    var n = amtLocal(conceptIri);
    for (var i = 0; i < AMT_CONCEPTS.length; i++) if (AMT_CONCEPTS[i].name === n) return i;
    return -1;
};

// Edge colours come from the page's CSS variables (assets/palette.css), with the palette values as fallback.
var amtColour = function(name, fallback) {
    try {
        var v = getComputedStyle(document.documentElement).getPropertyValue("--" + name).trim();
        return v || fallback;
    } catch (e) { return fallback; }
};

// "#rrggbb" -> "rgba(r,g,b,a)": vis.js 4.20 has no opacity option, so fading is done with the colour itself
var rgba = function(hex, a) {
    var m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(hex || "");
    if (!m) return hex;
    return "rgba(" + parseInt(m[1], 16) + "," + parseInt(m[2], 16) + "," + parseInt(m[3], 16) + "," + a + ")";
};

// ------------------------------------------------------------
// styleNodes: colour and column by concept
// ------------------------------------------------------------
var styleNodes = function(nodes) {
    for (var i in nodes) {
        var idx = conceptIndex(nodes[i].concept);
        var col = idx >= 0 ? AMT_CONCEPTS[idx] : AMT_FALLBACK;
        nodes[i].level = idx >= 0 ? idx : 0;
        nodes[i].chosen = false;
        nodes[i].baseColour = col;
        nodes[i].color = {
            background: col.bg,
            border:     col.border,
            highlight:  { background: "#ffffff", border: col.border },
            hover:      { background: col.bg, border: col.border }
        };
        nodes[i].shape = "dot";
        nodes[i].size  = 20;
        nodes[i].borderWidth = 2;
        nodes[i].font  = { size: 15, face: "Fira Sans, Roboto, Arial, sans-serif", color: "#17231f",
                           strokeWidth: 4, strokeColor: amtColour("bg", "#f8f7f1") };
        nodes[i].title = (idx >= 0 ? AMT_CONCEPTS[idx].name : amtLocal(nodes[i].concept)) + ": " + nodes[i].label;
    }
    return nodes;
};

// ------------------------------------------------------------
// shortenURI: turn a full IRI into a CURIE using the prefix map captured from the TTL (set in amt.js after
// N3 parsing). Falls back to the part after # or the last /.
// ------------------------------------------------------------
var shortenURI = function(uri) {
    if (typeof uri !== "string") return uri;
    var prefixes = (_AMT && _AMT.prefixes) ? _AMT.prefixes : {};
    var bestPrefix = null, bestNs = "";
    for (var p in prefixes) {
        var ns = prefixes[p];
        if (ns && uri.indexOf(ns) === 0 && ns.length > bestNs.length) { bestPrefix = p; bestNs = ns; }
    }
    if (bestPrefix !== null) return bestPrefix + ":" + uri.substring(bestNs.length);
    return amtLocal(uri);
};

// ------------------------------------------------------------
// styleEdges: asserted = solid dark, inferred = dashed red; the line gets thicker with the weight
// ------------------------------------------------------------
var edgeLabel = function(e, role, weight) {
    if (_AMT.labels === "none") return "";
    if (_AMT.labels === "weights" || e.inferred) return String(weight);
    return role + " " + weight;
};

var styleEdges = function(edges) {
    var bg = amtColour("bg", "#f8f7f1");
    var groups = {};
    for (var i in edges) {
        var key = [edges[i].from, edges[i].to].sort().join("|");
        (groups[key] = groups[key] || []).push(edges[i]);
    }
    for (var i in edges) {
        var e = edges[i];
        var isReasoned = !!e.inferred || (e.font && e.font.color === "red");
        e.inferred = isReasoned;
        var roleShort  = amtLocal(e.role);
        var weightVal  = Math.round(e.width * 100) / 100;
        var w          = Math.max(0, Math.min(1, e.width));   // e.width is the weight until the line is styled below
        var col        = isReasoned ? amtColour("inferred", "#c62828") : amtColour("asserted", "#2c3a52");

        e.weight = weightVal;
        var zero = (e.width < 0.0000001);
        e.arrowStrikethrough = false;
        e.chosen  = false;
        e.hidden  = zero;
        e.arrows  = { to: { enabled: true, scaleFactor: 0.7 } };
        e.length  = 350;
        e.dashes  = isReasoned ? [7, 5] : false;
        e.baseColour = col;
        var shown = isReasoned ? rgba(col, 0.85) : col;
        e.color   = { color: shown, highlight: shown, hover: shown };
        e.label   = edgeLabel(e, roleShort, weightVal);
        e.title   = (isReasoned ? "inferred" : "asserted") + " | " + shortenURI(e.role) + " | weight " + weightVal +
            " | type: " + (e.type ? amtLocal(e.type) : "Vagueness") +
            (e.method ? " | method: " + amtLocal(e.method) : "");
        e.font = { align: "middle", size: isReasoned ? 11 : 12, color: col, face: "Fira Sans, Roboto, Arial, sans-serif",
                   strokeWidth: 4, strokeColor: bg };

        // Edges between the same two nodes are bent apart, a single edge gets a gentle horizontal S-curve.
        var group = groups[[e.from, e.to].sort().join("|")];
        var k = group.indexOf(e);
        if (group.length === 1) {
            e.smooth = { enabled: true, type: "cubicBezier", forceDirection: "horizontal", roundness: 0.45 };
            e.roundnessUsed = 0.45;
        } else {
            var step = 0.18 + 0.12 * Math.floor(k / 2);
            e.smooth = { enabled: true, type: (k % 2 === 0) ? "curvedCW" : "curvedCCW", roundness: step };
            e.roundnessUsed = step;
        }
        // line width in pixels: thicker = higher weight (1 to 3 px); the weight itself stays in e.weight
        e.width = isReasoned ? 0.8 + 1.6 * w : 1 + 2 * w;
    }
    return edges;
};

// ------------------------------------------------------------
// vis.js network options: columns in the direction of the chain, no physics
// ------------------------------------------------------------
var AMT_VIS_OPTIONS = {
    layout: {
        hierarchical: {
            enabled: true,
            direction: "LR",
            sortMethod: "directed",
            levelSeparation: 330,
            nodeSpacing: 170,
            treeSpacing: 160,
            blockShifting: true,
            edgeMinimization: true,
            parentCentralization: false
        }
    },
    physics: { enabled: false },
    interaction: { hover: true, tooltipDelay: 150, hoverConnectedEdges: false, selectConnectedEdges: false, zoomView: true },
    nodes: { shape: "dot" },
    edges: { selectionWidth: 0 }
};

// ------------------------------------------------------------
// Status: only a warning if the browser reasoner finds a violation of an integrity axiom (domain, range ...).
// ------------------------------------------------------------
var showStatus = function(amt) {
    var err = amt.getError();
    var el  = $("#status");
    if (err) {
        el.text("Could not load the data: " + err).css("color", "#ffb3b3").attr("title", "");
        return;
    }
    var v = amt.getViolations();
    if (v.length === 0) {
        el.text("").attr("title", "");
    } else {
        el.text(v.length + " consistency violation" + (v.length > 1 ? "s" : ""))
          .css("color", "#ffd180").attr("title", v.join("\n"));
    }
};

// ------------------------------------------------------------
// Legend (bottom left): what the colours of the nodes and the lines mean
// ------------------------------------------------------------
var buildLegend = function() {
    var h = "<b>Nodes</b>";
    AMT_CONCEPTS.forEach(function(c) {
        h += '<div class="lg"><i class="dot" style="background:' + c.bg + ';border-color:' + c.border + '"></i>' +
             '<span><b>' + (c.name === "Actor" ? "Actor" : c.name) + '</b> &ndash; ' + c.gloss + '</span></div>';
    });
    h += '<b class="sec">Lines</b>' +
         '<div class="lg"><i class="ln" style="border-top:3px solid var(--asserted)"></i><span>asserted (in the data)</span></div>' +
         '<div class="lg"><i class="ln" style="border-top:3px dashed var(--inferred)"></i><span>inferred by reasoning (one direction)</span></div>' +
         '<div class="lg"><i class="ln thick"></i><span>thicker line = higher weight</span></div>' +
         '<label class="sw"><input type="checkbox" id="sw-generic"' + (_AMT.generic ? " checked" : "") +
         ' onchange="toggleGeneric(this.checked)" /><span>also show the generic role <code>reaches</code></span></label>';
    $("#legend-body").html(h);
};

// ------------------------------------------------------------
// update: (re)load data and render the graph
// ------------------------------------------------------------
var _network = null;

var update = function() {
    var amt = new AMT();
    _AMT.amt = amt;
    $("#status").text("");
    amt.load(function() {
        var graph = amt.getGraph(_AMT.reasoning, false);
        // Every role has an inverse and the reasoner derives both directions. The picture shows one direction
        // only; the inverse roles stay in the downloaded Turtle file. The generic role (the super role of the
        // derived roles) repeats them and is hidden unless the switch in the legend is on.
        var hiddenRoles = {};
        amt.getAxioms().forEach(function(a) {
            if (a.type === "InverseAxiom" && a.inverse) hiddenRoles[a.inverse] = true;
            if (!_AMT.generic && a.type === "SubsumptionAxiom" && a.superRole) hiddenRoles[a.superRole] = true;
        });
        graph.edges = graph.edges.filter(function(e) { return !hiddenRoles[e.role]; });
        graph.nodes = styleNodes(graph.nodes);
        graph.edges = styleEdges(graph.edges);
        graph.edges.forEach(function(e, i) { e.id = "e" + i; });

        _AMT.graph.nodes = new vis.DataSet(graph.nodes);
        _AMT.graph.edges = new vis.DataSet(graph.edges);
        if (_network) _network.destroy();
        _network = new vis.Network(
            document.getElementById("graph"),
            { nodes: _AMT.graph.nodes, edges: _AMT.graph.edges },
            AMT_VIS_OPTIONS
        );
        _AMT.thisNodes = graph.nodes;
        _AMT.thisEdges = graph.edges;
        _AMT.selected = null;

        _network.on("click", function(p) {
            if (p.nodes.length) selectItem("node", p.nodes[0]);
            else if (p.edges.length) selectItem("edge", p.edges[0]);
            else selectItem(null);
        });
        _network.once("afterDrawing", function() {
            arcInferred();
            _network.fit({ animation: false });
            // a little smaller and to the left, so the legend at the bottom right does not cover a node
            _network.moveTo({ scale: _network.getScale() * 0.86, offset: { x: 90, y: -25 }, animation: false });
        });

        buildLegend();
        showStatus(amt);
        showDetail();
        syncUrl();
    });
};

// ------------------------------------------------------------
// Inferred edges that skip a column bow out of the row of the nodes (above or below, away from the middle of the
// picture), so they no longer run over the asserted edges. Done once after the layout has placed the nodes.
// vis.js: for a chord running to the right, curvedCW bows up and curvedCCW down (the other way round to the left).
// ------------------------------------------------------------
var arcInferred = function() {
    var pos = _network.getPositions();
    var ys = Object.keys(pos).map(function(k) { return pos[k].y; });
    var mid = ys.reduce(function(a, b) { return a + b; }, 0) / (ys.length || 1);
    var up = 0, down = 0, upd = [];
    _AMT.thisEdges.forEach(function(e) {
        if (!e.inferred) return;
        var a = nodeById(e.from), b = nodeById(e.to);
        if (!a || !b) return;
        var span = Math.abs(a.level - b.level);
        if (span < 2) return;
        var ya = pos[e.from].y, yb = pos[e.to].y;
        var wantUp = (ya + yb) / 2 < mid || ((ya + yb) / 2 === mid && (up <= down));
        if (wantUp) up++; else down++;
        var rightwards = pos[e.to].x >= pos[e.from].x;
        var type = (wantUp === rightwards) ? "curvedCW" : "curvedCCW";
        var round = 0.05 + 0.07 * span + 0.04 * (wantUp ? up : down);
        e.smooth = { enabled: true, type: type, roundness: round };
        e.roundnessUsed = round;
        upd.push({ id: e.id, smooth: e.smooth });
    });
    if (upd.length) _AMT.graph.edges.update(upd);
};

// ------------------------------------------------------------
// Details panel and focus (the neighbourhood of the selection stays in colour, the rest fades)
// ------------------------------------------------------------
var nodeById = function(id) { return _AMT.thisNodes.filter(function(n) { return n.id === id; })[0]; };
var edgeById = function(id) { return _AMT.thisEdges.filter(function(e) { return e.id === id; })[0]; };

var applyFocus = function() {
    var sel = _AMT.selected;
    var keepNodes = {}, keepEdges = {};
    if (sel && sel.kind === "node") {
        keepNodes[sel.id] = true;
        _AMT.thisEdges.forEach(function(e) {
            if (e.from === sel.id || e.to === sel.id) { keepEdges[e.id] = true; keepNodes[e.from] = true; keepNodes[e.to] = true; }
        });
    } else if (sel && sel.kind === "edge") {
        var e0 = edgeById(sel.id);
        if (e0) { keepEdges[e0.id] = true; keepNodes[e0.from] = true; keepNodes[e0.to] = true; }
    }
    var dim = !!sel;
    _AMT.graph.nodes.update(_AMT.thisNodes.map(function(n) {
        var on = !dim || keepNodes[n.id];
        var c = n.baseColour;
        return { id: n.id,
                 color: { background: on ? c.bg : rgba(c.bg, 0.18), border: on ? c.border : rgba(c.border, 0.25),
                          highlight: { background: "#ffffff", border: c.border }, hover: { background: c.bg, border: c.border } },
                 font: { size: 15, face: "Fira Sans, Roboto, Arial, sans-serif", color: on ? "#17231f" : "rgba(23,35,31,0.3)",
                         strokeWidth: 4, strokeColor: amtColour("bg", "#f8f7f1") } };
    }));
    _AMT.graph.edges.update(_AMT.thisEdges.map(function(e) {
        var on = !dim || keepEdges[e.id];
        var isSel = sel && sel.kind === "edge" && sel.id === e.id;
        var col = on ? (e.inferred ? rgba(e.baseColour, 0.85) : e.baseColour) : rgba(e.baseColour, 0.15);
        return { id: e.id,
                 color: { color: col, highlight: col, hover: col },
                 font: { align: "middle", size: e.inferred ? 11 : 12, color: on ? e.baseColour : rgba(e.baseColour, 0.25),
                         face: "Fira Sans, Roboto, Arial, sans-serif", strokeWidth: 4, strokeColor: amtColour("bg", "#f8f7f1") },
                 shadow: isSel ? { enabled: true, color: "rgba(0,0,0,0.35)", size: 8, x: 0, y: 0 } : { enabled: false } };
    }));
};

var selectItem = function(kind, id) {
    _AMT.selected = kind ? { kind: kind, id: id } : null;
    applyFocus();
    showDetail();
    if (kind) openPanel("detail", true);
};

// The two info panels open from the icons in the bar (details, about); the legend folds itself.
var openPanel = function(name, on) {
    $("#" + name).toggleClass("open", !!on);
    $("#b-" + name).toggleClass("on", !!on);
};
var togglePanel = function(name) { openPanel(name, !$("#" + name).hasClass("open")); };

// Full screen: the browser's own full screen; the legend folds itself on a small window to leave room for the graph.
var toggleFullscreen = function() {
    try {
        if (document.fullscreenElement) document.exitFullscreen();
        else document.documentElement.requestFullscreen();
    } catch (e) { toast("Full screen is not available here (try F11)"); }
};
document.addEventListener("fullscreenchange", function() {
    var on = !!document.fullscreenElement;
    $("#b-full").toggleClass("on", on).find("i").text(on ? "fullscreen_exit" : "fullscreen");
    if (_network) { _network.redraw(); _network.fit({ animation: false }); }
});

var esc = function(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function(c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
};
var row = function(k, v) { return '<tr><th>' + k + '</th><td>' + v + '</td></tr>'; };

var showDetail = function() {
    var sel = _AMT.selected, h = "";
    if (sel && sel.kind === "edge" && edgeById(sel.id)) {
        var e = edgeById(sel.id), a = nodeById(e.from), b = nodeById(e.to);
        var axioms = (e.provenance || []).map(function(p) { return amtLocal(p); }).join(", ");
        h += '<h6>' + esc(shortenURI(e.role)) + '</h6>' +
             '<p class="who">' + esc(a ? a.label : amtLocal(e.from)) + ' &rarr; ' + esc(b ? b.label : amtLocal(e.to)) + '</p><table>' +
             row("weight", "<b>" + e.weight + "</b>") +
             row("status", e.inferred ? "inferred" + (axioms ? " by <code>" + esc(axioms) + "</code>" : "") : "asserted") +
             row("FW type", esc(e.type ? shortenURI(e.type) : "fw:Vagueness (default)")) +
             (e.method ? row("method", esc(shortenURI(e.method))) : "") +
             (e.source ? row("source string", "<code>" + esc(e.source) + "</code>") : "") + '</table>';
    } else if (sel && sel.kind === "node" && nodeById(sel.id)) {
        var n = nodeById(sel.id), idx = conceptIndex(n.concept);
        var out = _AMT.thisEdges.filter(function(e) { return e.from === n.id; }).length;
        var inn = _AMT.thisEdges.filter(function(e) { return e.to === n.id; }).length;
        h += '<h6>' + esc(n.label) + '</h6>' +
             '<p class="who">' + esc(idx >= 0 ? AMT_CONCEPTS[idx].name + " (" + AMT_CONCEPTS[idx].gloss + ")" : amtLocal(n.concept)) + '</p><table>' +
             row("IRI", "<code>" + esc(shortenURI(n.id)) + "</code>") +
             row("edges shown", out + " outgoing, " + inn + " incoming") + '</table>';
    } else {
        h += '<h6>' + esc(_AMT.file.replace(/\.ttl$/, "").replace("chain-", "Chain ")) + '</h6><p class="who">' + esc(_AMT.info) + '</p>' +
             '<p class="hint">Click a node or a line for details; click the background to reset.</p>';
    }
    $("#detail-body").html(h);
};

// ------------------------------------------------------------
// Chains, reasoning, label mode, generic role, link
// ------------------------------------------------------------
var _examples = [];

var loadExampleList = function(done) {
    fetch("data/examples.json")
        .then(function(r) { return r.ok ? r.json() : []; })
        .catch(function() { return []; })
        .then(function(list) { _examples = list; if (done) done(); });
};

var chooseExample = function(file) {
    _AMT.file = file;
    _AMT.info = "";
    _examples.forEach(function(ex) { if (ex.file === file) _AMT.info = ex.title.replace(/^Chain [A-Z] - /, ""); });
    window.AMT_SOURCE = "data/" + file;
    $("#chains .chain").each(function() { $(this).toggleClass("on", $(this).data("file") === file); });
};

var selectChain = function(file) {
    chooseExample(file);
    update();
};

var toggleReasoning = function() {
    _AMT.reasoning = !_AMT.reasoning;
    $("#r-but").toggleClass("on", _AMT.reasoning).text(_AMT.reasoning ? "Reasoning: on" : "Reasoning: off");
    update();
};

var LABEL_MODES = ["names", "weights", "none"];
var LABEL_TEXT  = { names: "Labels: names + weights", weights: "Labels: weights", none: "Labels: off" };
var cycleLabels = function() {
    _AMT.labels = LABEL_MODES[(LABEL_MODES.indexOf(_AMT.labels) + 1) % LABEL_MODES.length];
    $("#l-but").text(LABEL_TEXT[_AMT.labels]);
    _AMT.thisEdges.forEach(function(e) { e.label = edgeLabel(e, amtLocal(e.role), e.weight); });
    _AMT.graph.edges.update(_AMT.thisEdges.map(function(e) { return { id: e.id, label: e.label }; }));
    syncUrl();
};

var toggleGeneric = function(on) {
    _AMT.generic = !!on;
    update();
};

var linkUrl = function() {
    var q = ["ttl=" + encodeURIComponent(_AMT.file)];
    if (_AMT.reasoning) q.push("reasoning=on");
    if (_AMT.labels !== "names") q.push("labels=" + _AMT.labels);
    if (_AMT.generic) q.push("generic=1");
    return window.location.href.replace(/[?#].*$/, "") + "?" + q.join("&");
};

var syncUrl = function() {
    try { window.history.replaceState(null, "", linkUrl()); } catch (e) { /* e.g. file:// in some browsers */ }
};

var toast = function(text) {
    try { Materialize.toast(text, 2500); } catch (e) { /* no toast, nothing else to do */ }
};

var copyLink = function() {
    var url = linkUrl();
    var done = function() { toast("Link copied"); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function() { window.prompt("Link", url); });
    else window.prompt("Link", url);
};

// ------------------------------------------------------------
// Image export (PNG from the canvas, SVG drawn from the node positions)
// ------------------------------------------------------------
var imageName = function(ext) {
    return "samian-amt-" + _AMT.file.replace(/\.ttl$/, "") + (_AMT.reasoning ? "-reasoned" : "") + "." + ext;
};

var exportPNG = function() {
    if (!_network) return;
    var src = _network.canvas.frame.canvas;
    var c = document.createElement("canvas");
    c.width = src.width; c.height = src.height;
    var ctx = c.getContext("2d");
    ctx.fillStyle = amtColour("bg", "#f8f7f1");
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.drawImage(src, 0, 0);
    c.toBlob(function(blob) { downloadFile(imageName("png"), blob, "image/png"); }, "image/png");
};

var exportSVG = function() {
    if (!_network) return;
    var pos = _network.getPositions();
    var ids = Object.keys(pos);
    if (!ids.length) return;
    var R = 20, pad = 90;
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    ids.forEach(function(id) {
        minX = Math.min(minX, pos[id].x); maxX = Math.max(maxX, pos[id].x);
        minY = Math.min(minY, pos[id].y); maxY = Math.max(maxY, pos[id].y);
    });
    minX -= pad; minY -= pad; maxX += pad; maxY += pad;
    var W = Math.round(maxX - minX), H = Math.round(maxY - minY);
    var bg = amtColour("bg", "#f8f7f1");
    var f = function(x) { return Math.round(x * 10) / 10; };
    var X = function(x) { return f(x - minX); }, Y = function(y) { return f(y - minY); };
    var s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H +
            '" font-family="Fira Sans, Roboto, Arial, sans-serif">\n';
    s += '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
         '<path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>\n';
    s += '<rect width="' + W + '" height="' + H + '" fill="' + bg + '"/>\n';
    _AMT.thisEdges.forEach(function(e) {
        var a = pos[e.from], b = pos[e.to];
        if (!a || !b) return;
        var dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 1;
        var ux = dx / d, uy = dy / d;
        var x1 = a.x + ux * R, y1 = a.y + uy * R, x2 = b.x - ux * (R + 4), y2 = b.y - uy * (R + 4);
        var r = e.roundnessUsed || 0.3, path, mx, my;
        if (e.smooth && e.smooth.type === "cubicBezier") {
            var sg = dx >= 0 ? 1 : -1, k = r * Math.abs(x2 - x1);
            path = "M" + X(x1) + "," + Y(y1) + " C" + X(x1 + sg * k) + "," + Y(y1) + " " + X(x2 - sg * k) + "," + Y(y2) + " " + X(x2) + "," + Y(y2);
            mx = (x1 + x2) / 2; my = (y1 + y2) / 2;
        } else {
            var sgn = (e.smooth && e.smooth.type === "curvedCCW") ? -1 : 1;
            var cx = (x1 + x2) / 2 - uy * d * r * sgn, cy = (y1 + y2) / 2 + ux * d * r * sgn;
            path = "M" + X(x1) + "," + Y(y1) + " Q" + X(cx) + "," + Y(cy) + " " + X(x2) + "," + Y(y2);
            mx = 0.25 * x1 + 0.5 * cx + 0.25 * x2; my = 0.25 * y1 + 0.5 * cy + 0.25 * y2;
        }
        var sw = f(e.inferred ? 0.8 + 1.6 * Math.max(0, Math.min(1, e.weight)) : 1 + 2 * Math.max(0, Math.min(1, e.weight)));
        s += '<path d="' + path + '" fill="none" stroke="' + e.baseColour + '" stroke-width="' + sw + '"' +
             (e.inferred ? ' stroke-dasharray="7 5"' : "") + ' marker-end="url(#ah)"/>\n';
        if (e.label) {
            s += '<text x="' + X(mx) + '" y="' + Y(my) + '" text-anchor="middle" dominant-baseline="central" font-size="' + (e.inferred ? 11 : 12) +
                 '" fill="' + e.baseColour + '" stroke="' + bg + '" stroke-width="4" paint-order="stroke">' + esc(e.label) + '</text>\n';
        }
    });
    _AMT.thisNodes.forEach(function(n) {
        var p = pos[n.id]; if (!p) return;
        var c = n.baseColour;
        s += '<circle cx="' + X(p.x) + '" cy="' + Y(p.y) + '" r="' + R + '" fill="' + c.bg + '" stroke="' + c.border + '" stroke-width="2"/>\n';
        s += '<text x="' + X(p.x) + '" y="' + Y(p.y + R + 16) + '" text-anchor="middle" font-size="15" fill="#17231f" stroke="' + bg +
             '" stroke-width="4" paint-order="stroke">' + esc(n.label) + '</text>\n';
    });
    s += '</svg>\n';
    downloadFile(imageName("svg"), s, "image/svg+xml");
};

// ------------------------------------------------------------
// Cypher dialog: the graph as shown (one direction; with reasoning on, the inferred edges as well)
// ------------------------------------------------------------
var openCypher = function() {
    var text = buildCypher();
    $("#cypher").val(text);
    $("#cypher-note").text(_AMT.thisNodes.length + " nodes, " + _AMT.thisEdges.length + " relationships (" +
        _AMT.thisEdges.filter(function(e) { return e.inferred; }).length + " inferred)");
    $("#cypherModal").modal("open");
};
var copyCypher = function() {
    var t = $("#cypher").val();
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function() { toast("Cypher copied"); });
    else { $("#cypher").select(); document.execCommand("copy"); toast("Cypher copied"); }
};
var downloadCypher = function() {
    downloadFile(imageName("cypher"), $("#cypher").val(), "text/plain");
};

// ------------------------------------------------------------
// DOM ready
// ------------------------------------------------------------
$(function() {
    $("#cypherModal").modal();
    if (window.innerHeight < 760 || window.innerWidth < 1100) $("#legend").addClass("shut");   // small screen: legend folded
    var params = new URLSearchParams(window.location.search);
    _AMT.reasoning = params.get("reasoning") === "on";
    _AMT.generic   = params.get("generic") === "1";
    if (LABEL_MODES.indexOf(params.get("labels")) >= 0) _AMT.labels = params.get("labels");
    $("#r-but").toggleClass("on", _AMT.reasoning).text(_AMT.reasoning ? "Reasoning: on" : "Reasoning: off");
    $("#l-but").text(LABEL_TEXT[_AMT.labels]);
    loadExampleList(function() {
        var file = (params.get("ttl") || "chain-A.ttl").replace(/^data\//, "");
        chooseExample(file);
        update();
    });
});
