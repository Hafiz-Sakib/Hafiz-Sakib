"""
make_ascii_svg.py — convert source-prepped.png into a self-typing
monochrome ASCII-art SVG.

    python scripts/make_ascii_svg.py   # writes avi-ascii.svg

Design choices (kept deliberately simple):
  - Monochrome fill only. Per-character rainbow coloring makes ASCII
    portraits look noisy/static; one light-gray fill reads as clean.
  - High contrast source (see prep_photo.py) so the busy background
    washes out to the space glyph and only the subject prints.
  - Each row wipes in left-to-right via an SVG clipPath animation,
    staggered top-to-bottom, then freezes (no looping).
"""
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FONT_SIZE = 12
FILL = "#8b949e"  # muted light-gray, GitHub-dark-friendly

OUT = "avi-ascii.svg"


def image_to_rows(path: str) -> list[str]:
    img = Image.open(path).convert("L").resize((COLS, ROWS))
    px = img.load()
    rows = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            brightness = px[x, y] / 255.0
            idx = int((1 - brightness) * (len(RAMP) - 1))
            line.append(RAMP[idx])
        rows.append("".join(line).rstrip() or " ")
    return rows


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H + 20
    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}">',
        f'<rect width="100%" height="100%" fill="transparent"/>',
    ]
    for i, row in enumerate(rows):
        y = 10 + i * CHAR_H
        row_w = len(row) * CHAR_W
        delay = i * 0.045
        dur = 0.5
        clip_id = f"clip{i}"
        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{y - CHAR_H}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{row_w:.0f}" '
            f'begin="{delay:.3f}s" dur="{dur}s" fill="freeze" calcMode="linear"/>'
            f'</rect></clipPath>'
        )
        parts.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y}" fill="{FILL}" xml:space="preserve">{escape(row)}</text>'
            f'</g>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    rows = image_to_rows("source-prepped.png")
    svg = build_svg(rows)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT}")
