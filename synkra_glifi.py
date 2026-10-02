"""Genera i 25 glifi SYNKRA dalla grammatica visiva: forma base (dimensione) + segno (fase)."""
import math, os, zipfile

SW = 3  # spessore linea nel riquadro 100x100
TOP_EXT = 14  # quanto la linea di fase 4 supera il contorno
GAP_R = 9  # raggio del varco di fase 2

# --- forme base: lista di vertici o campionamento denso, centro, punto piu alto ---

def circle_pts(c=(50, 52), r=28, n=240):
    # parte dal punto piu alto e gira in senso orario
    return [(c[0] + r * math.sin(2 * math.pi * i / n), c[1] - r * math.cos(2 * math.pi * i / n)) for i in range(n)]

def mandorla_pts(c=(50, 52), R=34, d=17, n=120):
    h = math.sqrt(R * R - d * d)
    pts = []
    # arco destro (cerchio centrato a sinistra), dall'alto al basso
    a0 = math.atan2(-h, d)
    a1 = math.atan2(h, d)
    for i in range(n):
        a = a0 + (a1 - a0) * i / n
        pts.append((c[0] - d + R * math.cos(a), c[1] + R * math.sin(a)))
    # arco sinistro (cerchio centrato a destra), dal basso all'alto
    b0 = math.atan2(h, -d)
    b1 = math.atan2(-h, -d) + 2 * math.pi
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
ROMBO = [(50, 22), (78, 52), (50, 82), (22, 52)]
QUAD = [(50, 26), (76, 26), (76, 78), (24, 78), (24, 26)]  # parte dal centro del lato alto

SHAPES = {
    "T": dict(pts=lambda: circle_pts(), c=(50, 52), top=(50, 24), wave=17),
    "R": dict(pts=lambda: mandorla_pts(), c=(50, 52), top=(50, 52 - math.sqrt(34**2 - 17**2)), wave=8),
    "M": dict(pts=lambda: densify(TRI), c=(50, 56.7), top=(50, 22), wave=12),
    "C": dict(pts=lambda: densify(ROMBO), c=(50, 52), top=(50, 22), wave=15),
    "I": dict(pts=lambda: densify(QUAD), c=(50, 52), top=(50, 26), wave=17),
}

def poly(pts, closed=True):
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return d + (" Z" if closed else "")

def base_path(key, scale=1.0):
    s = SHAPES[key]
    cx, cy = s["c"]
    pts = [(cx + (x - cx) * scale, cy + (y - cy) * scale) for x, y in s["pts"]()]
    return pts

def gap_path(key):
    s = SHAPES[key]
    pts = s["pts"]()
    tx, ty = s["top"]
    r = GAP_R * (0.7 if key == "R" else 1)
    keep = [math.hypot(x - tx, y - ty) > r for x, y in pts]
    # ruota la lista in modo che inizi subito dopo il varco
    n = len(pts)
    start = next(i for i in range(n) if keep[i] and not keep[i - 1])
    seq = [pts[(start + i) % n] for i in range(n) if keep[(start + i) % n]]
    return poly(seq, closed=False)

def glyph_elements(key, phase):
    s = SHAPES[key]
    cx, cy = s["c"]
    el = []
    if phase == 2:
        el.append(f'<path d="{gap_path(key)}"/>')
    else:
        el.append(f'<path d="{poly(base_path(key))}"/>')
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
    "C": ["HULMEN", "QUERIK", "IKNOR", "KLAVEN", "OKULAR"],
    "I": ["ZERAN", "PARTEN", "NEXAL", "XUNDA", "WEVAN"],
}
CONCEPTS = {
    "T": ["Seme", "Frattura", "Crisalide", "Emersione", "Cenere"],
    "R": ["Soglia", "Abisso", "Specchio", "Nodo", "Risonanza"],
    "M": ["Radice", "Salto", "Corrente", "Sentiero", "Ritorno"],
    "C": ["Velo", "Labirinto", "Traccia", "Chiave", "Testimone"],
    "I": ["Vuoto", "Frammento", "Fulcro", "Trabocco", "Tessuto"],
}
DIMS = [("T", "Trasformazione"), ("R", "Relazione"), ("M", "Movimento"), ("C", "Conoscenza"), ("I", "Integrazione")]
PHASES = ["1 Latenza", "2 Crisi", "3 Processo", "4 Manifestazione", "5 Compimento"]

out = "synkra_glifi"
os.makedirs(out, exist_ok=True)
files = []
for key, _ in DIMS:
    for p in range(1, 6):
        name = MATRIX[key][p - 1]
        body = "\n  ".join(glyph_elements(key, p))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">\n'
               f'<title>{key}{p} {name}</title>\n<g {GROUP}>\n  {body}\n</g>\n</svg>\n')
        fn = os.path.join(out, f"{key}{p}_{name}.svg")
        open(fn, "w").write(svg)
        files.append(fn)

# --- tavola della matrice ---
LEFT, TOPH, CW, CH = 150, 60, 140, 175
W, H = LEFT + 5 * CW + 20, TOPH + 5 * CH + 70
F = 'font-family="Helvetica, Arial, sans-serif"'
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     f'<rect width="{W}" height="{H}" fill="#fff"/>',
     f'<text x="20" y="34" {F} font-size="20" font-weight="700" letter-spacing="3">SYNKRA</text>',
     f'<text x="128" y="34" {F} font-size="14" fill="#555">I Venticinque Specchi</text>']
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
open("SYNKRA_matrice_glifi.svg", "w").write("\n".join(s))

with zipfile.ZipFile("SYNKRA_glifi_singoli.zip", "w") as z:
    for fn in files:
        z.write(fn, os.path.basename(fn))
print(len(files), "glifi")
