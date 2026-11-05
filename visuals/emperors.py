"""Schematic profile portraits of Roman emperors in the style of a coin relief (drawn, invented, no real coin).

portrait_svg(who) returns an SVG group in a box of 200 x 240 (profile facing right, head and bust);
who is the nomisma id of the emperor, None gives a worn head without features.
The features are the typical ones, never a copy of one coin: bald and lined (Vespasian), short curls (Titus),
full curly beard (Marcus Aurelius), long wavy curls and beard (Lucius Verus), curls and a short beard
(Commodus), radiate crown with short hair and short beard (Aurelian), radiate crown, stubble and heavy brow
(Philip the Arab).
"""
from __future__ import annotations

import math

GOLD, LIGHT, DARK, LEAF = "#c9b36b", "#dcc98a", "#5e4c16", "#a9b45a"
ST = f'stroke="{DARK}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"'
def st(w):
    return f'stroke="{DARK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def thin(w=2):
    return st(w) + ' fill="none"'


THIN = thin()

_N = [0]


def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
    dx = 3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0])
    dy = 3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    return x, y, math.atan2(dy, dx)


def _curls(clip_d, x0, x1, y0, y1, r, step, jitter=1.0):
    """Curly texture: small open circles on a staggered grid inside the clip shape."""
    _N[0] += 1
    cid = f"cl{_N[0]}"
    cs = []
    row = 0
    y = y0
    while y < y1:
        x = x0 + (step / 2 if row % 2 else 0)
        while x < x1:
            jx = ((int(x * 7 + y * 13) % 5) - 2) * jitter
            jy = ((int(x * 11 + y * 5) % 5) - 2) * jitter
            cs.append(f'<circle cx="{x + jx:.1f}" cy="{y + jy:.1f}" r="{r}" fill="{GOLD}" {st(1.8)}/>')
            x += step
        y += step * 0.82
        row += 1
    return (f'<defs><clipPath id="{cid}"><path d="{clip_d}"/></clipPath></defs>'
            f'<path d="{clip_d}" fill="{GOLD}"/><g clip-path="url(#{cid})">{"".join(cs)}</g>'
            f'<path d="{clip_d}" fill="none" {ST}/>')



BUST = "M22,244 C26,206 56,190 88,188 L132,186 C152,196 170,216 180,244 Z"

# One hand-drawn profile per emperor (facing right, box 200 x 240), drawn by eye from busts and from the aureus of Aurelian
# (a real profile); the proportions differ on purpose: skull, forehead, nose, lips, chin, jaw and neck are not shared.
#   face   silhouette of head and neck      hair, beard: filled areas (curly texture or cropped)
#   eye    centre of the eye                ear: centre of the ear         mouth: right end of the mouth line
#   crown  four points of the wreath curve  extras: lined / round / brow / young
EMPERORS = {
    "vespasian": dict(
        label="Vespasian", dress="drape", crown="laurel", crown_pts=((146, 62), (126, 18), (60, 24), (50, 104)),
        face="M100,32 C130,34 148,52 148,74 L149,86 C147,92 145,96 147,100 C153,108 160,118 162,124 C157,127 152,127 148,128 "
             "C150,131 149,134 147,136 C149,140 148,146 145,150 C146,158 143,164 138,170 C132,178 126,182 120,184 C116,186 114,188 114,192 "
             "L114,228 L70,228 C72,204 60,178 56,150 C46,110 50,66 66,46 C78,36 90,32 100,32 Z",
        hair=None, tuft="M52,104 C46,124 50,144 62,156 C66,140 70,124 78,108 Z", beard=None,
        eye=(134, 86), ear=(76, 112), mouth=(147, 134), extras="lined"),
    "titus": dict(
        label="Titus", dress="drape", crown="laurel", crown_pts=((150, 58), (130, 14), (50, 22), (38, 100)),
        face="M100,30 C132,30 152,48 154,74 L155,84 C153,88 152,92 153,96 C157,100 160,106 161,111 C157,114 153,114 150,115 "
             "C152,118 152,121 150,124 C151,127 151,131 148,133 C152,138 154,146 150,154 C148,164 138,172 126,176 C120,178 116,180 114,186 "
             "L116,228 L48,228 C50,196 44,170 40,140 C32,100 38,60 62,40 C74,32 88,30 100,30 Z",
        hair="M100,26 C66,30 36,58 34,100 C34,122 40,134 48,140 C52,118 62,94 80,82 C100,72 126,68 152,64 L154,72 C152,46 132,28 100,26 Z",
        hair_style=(4.6, 9.5), beard=None, eye=(140, 82), ear=(68, 108), mouth=(150, 123), extras="round"),
    "marcus_aurelius": dict(
        label="Marcus Aurelius", dress="drape", crown="laurel", crown_pts=((146, 60), (122, 16), (48, 22), (36, 108)),
        face="M102,30 C132,32 148,50 150,74 L151,86 C149,92 148,96 150,100 C154,106 158,114 158,120 C154,123 149,124 146,125 "
             "C148,129 148,133 145,135 C149,139 149,144 145,148 C146,156 142,164 136,170 C130,176 124,180 120,184 C118,186 118,188 118,192 "
             "L120,228 L62,228 C64,200 54,176 48,150 C40,116 44,66 62,46 C74,34 88,30 102,30 Z",
        hair="M100,20 C58,20 30,58 32,116 C34,142 48,152 62,150 C64,128 76,108 94,98 C110,90 132,78 144,66 L148,74 C150,42 130,20 100,20 Z",
        hair_style=(6.5, 12), beard="M84,104 C84,132 96,160 122,172 C134,170 142,164 143,158 C142,152 143,150 145,148 C138,146 132,142 130,136 C112,132 96,120 84,104 Z",
        beard_style=(5, 10), moustache=True, eye=(134, 86), ear=(80, 108), mouth=(145, 134), extras=""),
    "lucius_verus": dict(
        label="Lucius Verus", dress="drape", crown="laurel", crown_pts=((144, 60), (124, 4), (38, 8), (26, 112)),
        face="M108,38 C130,40 142,56 144,76 L146,90 C144,96 142,100 144,104 C152,112 162,124 168,130 C162,133 154,133 148,134 "
             "C150,138 150,142 147,144 C150,148 150,154 146,158 C146,168 144,176 138,184 C132,190 126,194 122,198 L124,228 L70,228 "
             "C72,198 64,176 58,148 C50,116 52,72 68,52 C80,40 94,38 108,38 Z",
        hair="M110,2 C40,2 6,56 14,128 C18,160 44,170 60,164 C64,136 74,114 90,104 C108,96 126,82 138,68 L144,76 C150,36 132,4 110,2 Z",
        hair_style=(10, 18), beard="M80,100 C74,148 90,198 120,214 C136,208 148,194 148,174 C148,162 148,160 147,158 C140,156 134,152 132,144 C112,140 94,122 80,100 Z",
        beard_style=(6, 12), moustache=True, eye=(134, 90), ear=(84, 112), mouth=(148, 140), extras="young"),
    "commodus": dict(
        label="Commodus", dress="drape", crown="lion", crown_pts=((146, 62), (126, 18), (60, 24), (50, 104)),
        face="M100,34 C130,34 150,50 152,74 L153,86 C151,92 150,96 152,100 C157,104 160,110 161,115 C156,118 151,118 148,119 "
             "C150,123 150,127 148,129 C151,133 151,138 148,142 C150,150 148,158 142,164 C136,172 128,178 120,182 C116,184 114,186 114,190 "
             "L116,228 L56,228 C58,196 50,172 46,142 C38,106 44,64 64,44 C76,36 88,34 100,34 Z",
        hair="M100,26 C58,28 30,64 34,118 C36,138 46,148 56,150 C58,120 70,96 92,88 C112,80 138,72 150,64 C148,40 128,26 100,26 Z",
        hair_style=(7, 13), beard="M84,104 C84,132 96,164 120,180 C130,178 138,172 142,164 C146,156 148,148 148,142 C140,138 134,134 130,128 C114,126 98,118 84,104 Z",
        beard_style=(5, 10), moustache=True, eye=(138, 84), ear=(72, 110), mouth=(148, 128), extras="young"),
    "aurelian": dict(
        label="Aurelian", dress="cuirass", crown="laurel", crown_pts=((164, 56), (130, 20), (60, 40), (44, 112)),
        face="M97,24 C130,24 158,38 166,52 L168,66 L168,73 C166,78 164,82 166,84 C170,90 174,97 176,102 C172,105 168,106 165,106 "
             "C167,110 166,114 163,117 C165,122 162,128 159,131 C161,136 163,140 161,143 C156,150 148,152 143,152 L138,154 "
             "C140,166 142,176 141,186 L142,228 L57,228 C58,200 57,170 54,140 C44,124 36,100 33,80 C34,50 62,26 97,24 Z",
        hair="M97,24 C62,26 34,50 33,80 C36,100 44,124 54,134 C58,120 70,100 90,92 C110,84 150,74 168,64 L166,52 C158,38 130,24 97,24 Z",
        hair_style=None, beard="M96,96 C98,120 114,146 138,154 C148,152 156,150 161,143 C163,140 160,134 158,129 C146,126 130,116 120,106 C112,100 104,96 96,96 Z",
        beard_style=(3.4, 7), moustache=False, eye=(156, 76), ear=(86, 100), mouth=(163, 118), extras=""),
    "philip_the_arab": dict(
        label="Philip the Arab", dress="drape", crown="radiate", crown_pts=((148, 58), (128, 20), (62, 26), (46, 104)),
        face="M100,34 C132,34 148,44 150,66 L152,84 C150,90 148,94 150,98 C156,106 162,116 163,122 C158,126 152,126 149,127 "
             "C151,131 151,134 149,136 C152,140 152,146 150,150 L152,164 C150,172 142,178 132,180 L120,182 C118,184 118,188 118,192 "
             "L120,228 L52,228 C54,200 48,176 44,150 C36,110 40,66 58,46 C70,36 84,34 100,34 Z",
        hair="M100,32 C70,34 46,52 42,90 C42,110 46,126 54,136 C56,114 66,92 84,80 C106,70 134,66 148,62 C148,44 130,32 100,32 Z",
        hair_style=None, beard="M88,100 C86,130 100,160 124,176 C138,178 148,172 151,164 L150,150 C150,138 148,134 146,130 C130,126 106,118 88,100 Z",
        beard_style="stubble", moustache=False, eye=(138, 84), ear=(76, 110), mouth=(149, 132), extras="brow"),
}
STEPS = None


def _crown_curve(p):
    return f"M{p[0][0]},{p[0][1]} C{p[1][0]},{p[1][1]} {p[2][0]},{p[2][1]} {p[3][0]},{p[3][1]}"


def _laurel(p):
    out = []
    for i in range(13):
        t = i / 12
        x, y, a = _bez(*p, t)
        for side in (-1, 1):
            ang = math.degrees(a) + side * 38
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="14" ry="5.8" transform="rotate({ang:.0f} {x:.1f} {y:.1f})" fill="{LEAF}" {st(1.6)}/>')
    x3, y3 = p[3]
    out.append(f'<path d="M{x3},{y3} C{x3 - 8},{y3 + 12} {x3 - 12},{y3 + 26} {x3 - 10},{y3 + 42} M{x3 + 2},{y3 + 2} C{x3},{y3 + 18} {x3 + 2},{y3 + 34} {x3 + 10},{y3 + 48}" {THIN}/>')
    out.append(f'<path d="{_crown_curve(p)}" {thin(3)}/>')
    return "".join(out)


def _radiate(p):
    cv = _crown_curve(p)
    out = [f'<path d="{cv}" fill="none" stroke="{DARK}" stroke-width="9" stroke-linecap="round"/>',
           f'<path d="{cv}" fill="none" stroke="{LIGHT}" stroke-width="4" stroke-linecap="round"/>']
    for i in range(1, 8):
        x, y, a = _bez(*p, i / 8)
        nx, ny = math.sin(a), -math.cos(a)
        if nx * (x - 90) + ny * (y - 110) < 0:
            nx, ny = -nx, -ny
        out.append(f'<path d="M{x:.1f},{y:.1f} L{x + nx * 28:.1f},{y + ny * 28:.1f}" stroke="{DARK}" stroke-width="7" stroke-linecap="round" fill="none"/>')
        out.append(f'<path d="M{x:.1f},{y:.1f} L{x + nx * 28:.1f},{y + ny * 28:.1f}" stroke="{LIGHT}" stroke-width="3" stroke-linecap="round" fill="none"/>')
    return "".join(out)


def _lion():
    """Commodus as Hercules: the lion skin over the head, the paws knotted on the chest."""
    out = [f'<path d="M146,66 C142,30 104,10 68,24 C34,40 20,96 34,142 C44,150 54,152 60,150 C58,110 80,76 112,70 C124,66 140,68 146,66 Z" fill="#b99a4a" {ST}/>']
    out.append(f'<path d="M146,66 C156,62 164,64 168,70 C164,76 156,78 148,76 Z" fill="#b99a4a" {ST}/><circle cx="160" cy="68" r="2" fill="{DARK}"/>')
    out.append(f'<circle cx="88" cy="20" r="9" fill="#b99a4a" {ST}/><circle cx="118" cy="24" r="9" fill="#b99a4a" {ST}/>')
    for x, y in [(60, 40), (48, 62), (40, 86), (40, 112), (52, 132), (74, 36), (96, 36), (120, 44), (126, 56)]:
        out.append(f'<path d="M{x},{y} l-6,10" {thin(2)}/>')
    out.append(f'<path d="M104,200 C96,190 108,184 118,192 M132,200 C142,190 156,196 148,208" {thin(2.4)}/>')
    out.append(f'<ellipse cx="108" cy="208" rx="9" ry="6" fill="#b99a4a" {ST}/><ellipse cx="138" cy="210" rx="9" ry="6" fill="#b99a4a" {ST}/>')
    return "".join(out)


def portrait_svg(who):
    e = EMPERORS.get(who)
    out = [f'<path d="{BUST}" fill="{GOLD}" {ST}/>']
    if e is None:
        out.append(f'<path d="{EMPERORS["marcus_aurelius"]["face"]}" fill="{GOLD}" {ST} stroke-dasharray="5 6"/>')
        out.append(f'<path d="M70,60 C90,44 120,50 132,70" {THIN} stroke-dasharray="3 8"/>')
        return "".join(out)
    if e["dress"] == "drape":
        out.append(f'<path d="M60,214 C84,206 112,214 130,238 M96,206 C112,220 126,230 134,244 M150,212 C160,224 168,232 172,244" {THIN}/>')
        out.append(f'<circle cx="156" cy="212" r="6" fill="{LIGHT}" {st(1.8)}/>')
    else:
        out.append(f'<path d="M40,226 C70,214 120,214 166,226 M36,238 C70,228 124,228 172,238" {THIN}/>')
        out.append("".join(f'<circle cx="{x}" cy="{y}" r="3" fill="none" {st(1.4)}/>' for x in range(52, 170, 14) for y in (232, 242)))
    out.append(f'<path d="{e["face"]}" fill="{GOLD}" {ST}/>')
    ex, ey = e["eye"]
    mx, my = e["mouth"]
    ax, ay = e["ear"]
    bw = 6 if e["extras"] == "brow" else 3.2
    out.append(f'<g transform="translate({ex - 127},{ey - 87})">'
               f'<path d="M118,86 C124,82 132,83 136,87 C130,92 123,92 118,86 Z" fill="{LIGHT}" {st(1.8)}/><circle cx="127" cy="87" r="2.6" fill="{DARK}"/>'
               f'<path d="M112,78 C120,73 130,74 138,79" fill="none" stroke="{DARK}" stroke-width="{bw}" stroke-linecap="round"/>')
    if e["extras"] == "lined":
        out.append(f'<path d="M96,52 C108,50 120,54 128,62 M92,62 C106,60 118,64 128,72 M122,98 C112,104 104,110 104,120 M128,108 C124,118 126,126 132,132 M114,94 C120,98 128,98 133,94" {thin(1.8)}/>')
    if e["extras"] == "brow":
        out.append(f'<path d="M100,54 C112,52 124,56 132,64 M98,64 C110,62 122,66 130,72 M122,98 C116,108 114,118 118,130 M114,94 C120,98 128,98 133,94" {thin(2)}/>')
    out.append("</g>")
    out.append(f'<g transform="translate({ax - 81},{ay - 114})"><path d="M84,100 C74,100 72,116 80,126 C84,130 90,126 90,120" fill="{GOLD}" {st(2.2)}/>'
               f'<path d="M-9,0" fill="none"/></g>')
    out.append(f'<path d="M{mx},{my} C{mx - 6},{my + 1} {mx - 12},{my} {mx - 18},{my - 3}" {THIN}/>')
    if e["extras"] == "round":
        out.append(f'<path d="M130,112 C140,122 142,134 136,144 M112,172 C122,178 130,176 136,170" {thin(1.6)} opacity=".7"/>')
    if e.get("tuft"):
        out.append(f'<path d="{e["tuft"]}" fill="{GOLD}" {ST}/>')
        out.append(f'<path d="M54,118 l8,-6 M56,130 l8,-6 M60,142 l8,-4" {thin(1.6)}/>')
    if e.get("hair"):
        hs = e.get("hair_style")
        if hs:
            out.append(_curls(e["hair"], 4, 180, 4, 180, hs[0], hs[1], 0.7))
        else:   # cropped hair: a cap with short combed strokes
            out.append(f'<path d="{e["hair"]}" fill="{GOLD}" {ST}/>')
            rows = []
            for k in range(9):
                x = 54 + k * 11
                rows.append(f'M{x},{96 - k * 5} l6,-9')
            out.append(f'<path d="{" ".join(rows)}" {thin(1.5)}/>')
    if e.get("beard"):
        bs = e["beard_style"]
        if bs == "stubble":
            _N[0] += 1
            cid = f"st{_N[0]}"
            dots = "".join(f'<circle cx="{x}" cy="{y}" r="1.5" fill="{DARK}"/>' for x in range(86, 156, 6) for y in range(100, 182, 6) if (x * 3 + y) % 3 != 0)
            out.append(f'<defs><clipPath id="{cid}"><path d="{e["beard"]}"/></clipPath></defs><g clip-path="url(#{cid})">{dots}</g>')
        else:
            out.append(_curls(e["beard"], 70, 180, 90, 215, bs[0], bs[1], 0.7))
        if e.get("moustache"):
            out.append(f'<path d="M{mx},{my - 6} C{mx - 8},{my - 8} {mx - 16},{my - 6} {mx - 22},{my} C{mx - 14},{my + 4} {mx - 6},{my + 4} {mx},{my + 1} Z" fill="{GOLD}" {ST}/>')
    c = e["crown"]
    if c == "lion":
        out.append(_lion())
    elif c == "laurel":
        out.append(_laurel(e["crown_pts"]))
    else:
        out.append(_radiate(e["crown_pts"]))
    return "".join(out)


def place(f, cx, cy, r, who, coin=True):
    """A coin (rim, dotted ring, portrait) or a plain medallion with the portrait of `who` at the position (cx, cy)."""
    _N[0] += 1
    cid = f"pt{_N[0]}"
    inner = r - 15 if coin else r - 3
    k = (inner * 2) / 215
    ring = (f'<circle r="{r - 8}" fill="none" stroke="#8a7430" stroke-width="2"/>'
            f'<circle r="{r - 12}" fill="none" stroke="#8a7430" stroke-width="2" stroke-dasharray="2 5"/>') if coin else ""
    f.raw(f'<defs><clipPath id="{cid}"><circle r="{inner}"/></clipPath></defs>'
          f'<g transform="translate({cx},{cy})"><circle r="{r}" fill="#e9d9a6" stroke="#000000" stroke-width="2"/>{ring}'
          f'<g clip-path="url(#{cid})"><g transform="scale({k:.4f}) translate(-100,-125)">{portrait_svg(who)}</g></g></g>')
