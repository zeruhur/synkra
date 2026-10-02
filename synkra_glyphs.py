"""Generates the 25 SYNKRA glyphs from the visual grammar: base shape (dimension) + mark (phase)."""
import math, os
import cairosvg

SW = 3
TOP_EXT = 14
PNG_SIZE = 1024  # pixel width/height of the exported PNGs
GAP_R = 9

def circle_pts(c=(50, 52), r=28, n=240):
    return [(c[0] + r * math.sin(2 * math.pi * i / n), c[1] - r * math.cos(2 * math.pi * i / n)) for i in range(n)]

def mandorla_pts(c=(50, 52), R=34, d=17, n=120):
    h = math.sqrt(R * R - d * d)
    pts = []
    a0 = math.atan2(-h, d); a1 = math.atan2(h, d)
    for i in range(n):
        a = a0 + (a1 - a0) * i / n
        pts.append((c[0] - d + R * math.cos(a), c[1] + R * math.sin(a)))
    b0 = math.atan2(h, -d); b1 = math.atan2(-h, -d) + 2 * math.pi
    for i in range(n):
        a = b0 + (b1 - b0) * i / n
        pts.append((c[0] + d + R * math.cos(a), c[1] + R * math.sin(a)))
    return pts

def densify(verts, step=0.5):
    pts = []
    for i in range(len(verts)):
        (x0, y0), (x1, y1) = verts[i], verts[(i + 1) % len(verts)]
        L = math.hypot(x1 - x0, y1 - y0)
        k = max(1, int(L / step))
        for j in range(k):
            pts.append((x0 + (x1 - x0) * j / k, y0 + (y1 - y0) * j / k))
    return pts

TRI = [(50, 22), (80, 74), (20, 74)]
RHOMBUS = [(50, 18), (70, 52), (50, 86), (30, 52)]  # narrow: same proportions as the mandorla
SQUARE = [(50, 26), (76, 26), (76, 78), (24, 78), (24, 26)]

SHAPES = {
    "T": dict(pts=lambda: circle_pts(), c=(50, 52), top=(50, 24), wave=17),
    "R": dict(pts=lambda: mandorla_pts(), c=(50, 52), top=(50, 52 - math.sqrt(34**2 - 17**2)), wave=8),
    "M": dict(pts=lambda: densify(TRI), c=(50, 56.7), top=(50, 22), wave=12),
    "K": dict(pts=lambda: densify(RHOMBUS), c=(50, 52), top=(50, 18), wave=9),
    "I": dict(pts=lambda: densify(SQUARE), c=(50, 52), top=(50, 26), wave=17),
}

def poly(pts, closed=True):
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return d + (" Z" if closed else "")

def base_path(key, scale=1.0):
    s = SHAPES[key]; cx, cy = s["c"]
    return [(cx + (x - cx) * scale, cy + (y - cy) * scale) for x, y in s["pts"]()]

def gap_path(key):
    s = SHAPES[key]; pts = s["pts"](); tx, ty = s["top"]
    r = GAP_R * (0.7 if key == "R" else 1)
    keep = [math.hypot(x - tx, y - ty) > r for x, y in pts]
    n = len(pts)
    start = next(i for i in range(n) if keep[i] and not keep[i - 1])
    seq = [pts[(start + i) % n] for i in range(n) if keep[(start + i) % n]]
    return poly(seq, closed=False)

def glyph_elements(key, phase):
    s = SHAPES[key]; cx, cy = s["c"]; el = []
    el.append(f'<path d="{gap_path(key)}"/>' if phase == 2 else f'<path d="{poly(base_path(key))}"/>')
    if phase == 1:
        el.append(f'<circle cx="{cx}" cy="{cy:.2f}" r="3.6" fill="#000" stroke="none"/>')
    elif phase == 3:
        w, A, n = s["wave"], 4, 60
        pts = [(cx - w + 2 * w * i / n, cy + A * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
        el.append(f'<path d="{poly(pts, closed=False)}"/>')
    elif phase == 4:
        el.append(f'<line x1="{cx}" y1="{cy:.2f}" x2="{cx}" y2="{s["top"][1] - TOP_EXT:.2f}"/>')
    elif phase == 5:
        el.append(f'<path d="{poly(base_path(key, 0.52))}"/>')
    return el

GROUP = f'fill="none" stroke="#000" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"'
MATRIX = {
    "T": ["GERMA", "BREKA", "UMVEL", "EMRAL", "ASKOR"],
    "R": ["LIMYR", "DISTEN", "MIREN", "THEKNA", "SONAL"],
    "M": ["RADHEN", "JEKTA", "FLUEN", "VEKTOR", "CYRKEL"],
    "K": ["HULMEN", "QUERIK", "IKNOR", "KLAVEN", "OKULAR"],
    "I": ["ZERAN", "PARTEN", "NEXAL", "XUNDA", "WEVAN"],
}

os.makedirs("glyphs", exist_ok=True)
for key in MATRIX:
    for p in range(1, 6):
        name = MATRIX[key][p - 1]
        body = "\n  ".join(glyph_elements(key, p))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">\n'
               f'<title>{key}{p} {name}</title>\n<rect width="100" height="100" fill="#fff"/>\n<g {GROUP}>\n  {body}\n</g>\n</svg>\n')
        open(f"glyphs/{key}{p}_{name}.svg", "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=f"glyphs/{key}{p}_{name}.png",
                         output_width=PNG_SIZE, output_height=PNG_SIZE)
print("done")

# --- matrix sheet ---
CONCEPTS = {
    "T": ["Seed", "Fracture", "Chrysalis", "Emergence", "Ash"],
    "R": ["Threshold", "Abyss", "Mirror", "Knot", "Resonance"],
    "M": ["Root", "Leap", "Current", "Path", "Return"],
    "K": ["Veil", "Labyrinth", "Trace", "Key", "Witness"],
    "I": ["Void", "Fragment", "Fulcrum", "Overflow", "Weave"],
}
DIMS = [("T", "Transformation"), ("R", "Relation"), ("M", "Movement"), ("K", "Knowledge"), ("I", "Integration")]
PHASES = ["1 Latency", "2 Crisis", "3 Process", "4 Manifestation", "5 Completion"]
LEFT, TOPH, CW, CH = 150, 60, 140, 175
W, H = LEFT + 5 * CW + 20, TOPH + 5 * CH + 70
F = 'font-family="Helvetica, Arial, sans-serif"'
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     f'<rect width="{W}" height="{H}" fill="#fff"/>',
     f'<text x="20" y="34" {F} font-size="20" font-weight="700" letter-spacing="3">SYNKRA</text>',
     f'<text x="128" y="34" {F} font-size="14" fill="#555">The Twenty-Five Mirrors</text>']
for j, ph in enumerate(PHASES):
    s.append(f'<text x="{LEFT + j * CW + CW / 2}" y="{TOPH + 8}" {F} font-size="12" fill="#555" text-anchor="middle">{ph}</text>')
for i, (key, dim) in enumerate(DIMS):
    y0 = TOPH + 20 + i * CH
    s.append(f'<text x="20" y="{y0 + 60}" {F} font-size="22" font-weight="700">{key}</text>')
    s.append(f'<text x="20" y="{y0 + 80}" {F} font-size="12" fill="#555">{dim}</text>')
    for p in range(1, 6):
        x0 = LEFT + (p - 1) * CW + (CW - 100) / 2
        body = "".join(glyph_elements(key, p))
        s.append(f'<g transform="translate({x0},{y0})" {GROUP}>{body}</g>')
        cxm = LEFT + (p - 1) * CW + CW / 2
        s.append(f'<text x="{cxm}" y="{y0 + 118}" {F} font-size="13" font-weight="700" text-anchor="middle" letter-spacing="1">{MATRIX[key][p-1]}</text>')
        s.append(f'<text x="{cxm}" y="{y0 + 134}" {F} font-size="11" fill="#555" text-anchor="middle">{key}{p} · {CONCEPTS[key][p-1]}</text>')
s.append("</svg>")
open("SYNKRA_glyph_matrix.svg", "w").write("\n".join(s))
