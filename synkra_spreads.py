"""Draws SYNKRA spread diagrams, empty and filled, reusing the glyph grammar."""
import math, os
import cairosvg
from synkra_glyphs import glyph_elements, GROUP, MATRIX

CONCEPT = {
    "T": ["Seed", "Fracture", "Chrysalis", "Emergence", "Ash"],
    "R": ["Threshold", "Abyss", "Mirror", "Knot", "Resonance"],
    "M": ["Root", "Leap", "Current", "Path", "Return"],
    "K": ["Veil", "Labyrinth", "Trace", "Key", "Witness"],
    "I": ["Void", "Fragment", "Fulcrum", "Overflow", "Weave"],
}
F = 'font-family="Helvetica, Arial, sans-serif"'
S = 104  # slot size
PNG_SCALE = 3  # PNG resolution multiplier over the SVG's pixel size


def slot(x, y, order, line1, line2, code=None):
    """Slot centered at x,y. Empty when code is None."""
    out = []
    x0, y0 = x - S / 2, y - S / 2
    if code is None:
        out.append(f'<rect x="{x0}" y="{y0}" width="{S}" height="{S}" rx="10" fill="#fff" '
                   f'stroke="#888" stroke-width="1.6" stroke-dasharray="6 5"/>')
        out.append(f'<text x="{x}" y="{y + 9}" {F} font-size="28" fill="#999" text-anchor="middle">{order}</text>')
    else:
        out.append(f'<rect x="{x0}" y="{y0}" width="{S}" height="{S}" rx="10" fill="#fff" stroke="#bbb" stroke-width="1.2"/>')
        k, p = code[0], int(code[1])
        body = "".join(glyph_elements(k, p))
        sc = 0.92
        out.append(f'<g transform="translate({x - 50 * sc},{y - 50 * sc}) scale({sc})" {GROUP}>{body}</g>')
        out.append(f'<circle cx="{x0 + 14}" cy="{y0 + 14}" r="9" fill="#f2f2f2" stroke="#bbb" stroke-width="1"/>')
        out.append(f'<text x="{x0 + 14}" y="{y0 + 18}" {F} font-size="11" fill="#555" text-anchor="middle">{order}</text>')
    out.append(f'<text x="{x}" y="{y + S / 2 + 20}" {F} font-size="13" font-weight="700" text-anchor="middle">{line1}</text>')
    out.append(f'<text x="{x}" y="{y + S / 2 + 36}" {F} font-size="11" fill="#555" text-anchor="middle">{line2}</text>')
    return out


def svg(name, w, h, slots, title=None):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
             f'<rect width="{w}" height="{h}" fill="#fff"/>']
    if title:
        parts.append(f'<text x="{w / 2}" y="26" {F} font-size="14" font-weight="700" letter-spacing="2" text-anchor="middle">{title}</text>')
    for s in slots:
        parts += slot(*s)
    parts.append("</svg>")
    os.makedirs("spreads", exist_ok=True)
    data = "\n".join(parts)
    open(f"spreads/{name}.svg", "w").write(data)
    cairosvg.svg2png(bytestring=data.encode(), write_to=f"spreads/{name}.png", scale=PNG_SCALE)


def g(code):
    k, p = code[0], int(code[1])
    return f"{MATRIX[k][p - 1]}, the {CONCEPT[k][p - 1]}"


def row(xs_n, gap, w):
    start = w / 2 - gap * (xs_n - 1) / 2
    return [start + gap * i for i in range(xs_n)]


# ---------- empty spreads ----------
TITLE_Y = 0
svg("single_empty", 320, 210, [(160, 100, 1, "The glyph", "one focused theme")], "SINGLE GLYPH")

xs = row(3, 180, 600)
svg("time_triad_empty", 600, 210, [
    (xs[0], 100, 1, "Past", "what led here"),
    (xs[1], 100, 2, "Present", "what is active now"),
    (xs[2], 100, 3, "Tendency", "where things are heading"),
], "TIME TRIAD")
svg("knot_triad_empty", 600, 210, [
    (xs[0], 100, 1, "Situation", "what is going on"),
    (xs[1], 100, 2, "Obstacle", "what is in the way"),
    (xs[2], 100, 3, "Resource", "what can help"),
], "KNOT TRIAD")

QX, QY, DX, DY = 330, 290, 200, 190
Q = {"c": (QX, QY), "a": (QX, QY - DY), "b": (QX, QY + DY), "l": (QX - DX, QY), "r": (QX + DX, QY)}
svg("quincunx_empty", 660, 580, [
    (*Q["c"], 1, "Center", "the heart of the matter"),
    (*Q["a"], 2, "Above", "what you know"),
    (*Q["b"], 3, "Below", "what remains in shadow"),
    (*Q["l"], 4, "Left", "what holds you back"),
    (*Q["r"], 5, "Right", "what draws you forward"),
], "QUINCUNX")

svg("two_paths_empty", 440, 380, [
    (130, 100, 1, "Path A", "the first option"),
    (310, 100, 2, "Path B", "the second option"),
    (220, 280, 3, "Shared ground", "what both have in common"),
], "TWO PATHS")

xs5 = row(5, 150, 780)
dims = [("T", "Transformation"), ("R", "Relation"), ("M", "Movement"), ("K", "Knowledge"), ("I", "Integration")]
svg("five_rooms_empty", 780, 210, [(xs5[i], 100, i + 1, d, f"row {k}, roll the phase") for i, (k, d) in enumerate(dims)],
    "FIVE ROOMS")

phases = ["Latency", "Crisis", "Process", "Manifestation", "Completion"]
senses = ["the first seed", "what breaks open", "the hidden work", "what comes out", "how it closes"]
cx, cy, R = 330, 300, 190
cyc = []
for i in range(5):
    a = -math.pi / 2 + 2 * math.pi * i / 5
    cyc.append((cx + R * math.cos(a), cy + R * math.sin(a) - 15, i + 1, phases[i], senses[i]))
svg("cycle_empty", 660, 580, cyc, "THE CYCLE")

# ---------- filled spreads (Chapter 11) ----------
svg("giulia_single", 320, 210, [(160, 100, 1, g("T3"), "T3 · the glyph", "T3")], "GIULIA · SINGLE GLYPH")
svg("marco_knot", 600, 210, [
    (xs[0], 100, 1, g("R4"), "R4 · Situation", "R4"),
    (xs[1], 100, 2, g("M1"), "M1 · Obstacle", "M1"),
    (xs[2], 100, 3, g("K2"), "K2 · Resource", "K2"),
], "MARCO · KNOT TRIAD")
svg("sara_quincunx", 660, 580, [
    (*Q["c"], 1, g("R3"), "R3 · Center", "R3"),
    (*Q["a"], 2, g("T4"), "T4 · Above", "T4"),
    (*Q["b"], 3, g("K1"), "K1 · Below", "K1"),
    (*Q["l"], 4, g("I2"), "I2 · Left", "I2"),
    (*Q["r"], 5, g("M5"), "M5 · Right", "M5"),
], "SARA · QUINCUNX")
svg("elena_single", 320, 210, [(160, 100, 1, g("I3"), "I3 · the glyph", "I3")], "ELENA · SINGLE GLYPH")
print(sorted(os.listdir("spreads")))
