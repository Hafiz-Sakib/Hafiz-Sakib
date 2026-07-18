"""
make_info_card.py — neofetch-style info panel, fades in line by line.

    python scripts/make_info_card.py            # animated
    STATIC=1 python scripts/make_info_card.py    # frozen frame (Quick Look preview)

Edit ROWS below to change what shows on your profile.
"""
import os

OUT = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

TITLE = "hafiz@github"
ROWS = [
    ("OS", "Zorin OS 18 (Hyprland)"),
    ("Now", "Building Proof Sheet — Figure to PDF (React/Vite PWA)"),
    ("Prev", "AlgoViz — 64+ algorithms, React/TS, TanStack Router"),
    ("Stack", "React · TypeScript · Node · PyTorch · Firebase"),
    ("CP", "Codeforces & LeetCode @hafiz_sakib"),
    ("Highlights", "AlgoViz · NOVA MathPlot · SubCalcPro · Sababa Tours"),
]

WIDTH = 490
LINE_H = 30
PAD_TOP = 56
KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
TITLE_COLOR = "#58a6ff"

HEIGHT = PAD_TOP + LINE_H * (len(ROWS) + 1) + 20


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="14">',
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # fake titlebar dots
        '<circle cx="20" cy="20" r="5" fill="#ff5f56"/>',
        '<circle cx="38" cy="20" r="5" fill="#ffbd2e"/>',
        '<circle cx="56" cy="20" r="5" fill="#27c93f"/>',
        f'<text x="20" y="{PAD_TOP - 20}" fill="{TITLE_COLOR}" font-size="16" '
        f'font-weight="bold">{escape(TITLE)}</text>',
        f'<line x1="20" y1="{PAD_TOP - 10}" x2="{WIDTH - 20}" y2="{PAD_TOP - 10}" '
        f'stroke="{BORDER}"/>',
    ]

    for i, (key, val) in enumerate(ROWS):
        y = PAD_TOP + i * LINE_H
        line = f'{key}: {escape(val)}'
        text_el = (
            f'<text x="20" y="{y}" xml:space="preserve">'
            f'<tspan fill="{KEY_COLOR}" font-weight="bold">{escape(key)}: </tspan>'
            f'<tspan fill="{VAL_COLOR}">{escape(val)}</tspan>'
            f'</text>'
        )
        if STATIC:
            parts.append(text_el)
        else:
            delay = 0.25 + i * 0.12
            parts.append(
                f'<g opacity="0" transform="translate(-8,0)">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8,0" to="0,0" begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
                f'{text_el}</g>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT}")
