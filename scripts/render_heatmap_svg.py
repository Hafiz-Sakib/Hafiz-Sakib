"""
render_heatmap_svg.py — draw data/contributions.json as the classic
53-week x 7-day calendar of rounded boxes, revealed with a diagonal
slide-down (plays once on load, then freezes).

    python scripts/render_heatmap_svg.py   # writes contrib-heatmap.svg
"""
import json
from datetime import datetime

IN = "data/contributions.json"
OUT = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none      lvl1       lvl2       lvl3       lvl4       (extra neon top end unused by GH levels 0-4)

BOX = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
MONTH_LABEL_H = 16


def load() -> dict:
    with open(IN) as f:
        return json.load(f)


def build_svg(payload: dict) -> str:
    days = payload["days"]
    stats = payload.get("stats", {})

    # bucket by (week_index, weekday) — GitHub weeks run Sun-Sat
    by_date = {d["date"]: d["level"] for d in days}
    if not days:
        weeks = 0
    else:
        dates = sorted(datetime.strptime(d["date"], "%Y-%m-%d") for d in days)
        first_sunday_offset = dates[0].weekday() + 1 if dates[0].weekday() != 6 else 0
        weeks = ((len(dates) + first_sunday_offset) // 7) + 1

    width = LEFT_PAD + weeks * (BOX + GAP) + 20
    height = TOP_PAD + MONTH_LABEL_H + 7 * (BOX + GAP) + 60

    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="10">',
        '<rect width="100%" height="100%" fill="transparent"/>',
    ]

    sorted_days = sorted(days, key=lambda d: d["date"])
    last_month = None
    for i, d in enumerate(sorted_days):
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        week = i // 7
        weekday = dt.weekday()  # Mon=0..Sun=6
        weekday = (weekday + 1) % 7  # convert to Sun=0..Sat=6
        x = LEFT_PAD + week * (BOX + GAP)
        y = TOP_PAD + MONTH_LABEL_H + weekday * (BOX + GAP)

        if dt.day <= 7 and dt.strftime("%b") != last_month:
            last_month = dt.strftime("%b")
            parts.append(
                f'<text x="{x}" y="{TOP_PAD + MONTH_LABEL_H - 4}" fill="#8b949e">{last_month}</text>'
            )

        level = min(d["level"], 4)
        color = PALETTE[level]
        delay = (week + weekday) * 0.012
        parts.append(
            f'<rect x="{x}" y="{y - BOX}" width="{BOX}" height="{BOX}" rx="2" '
            f'fill="{color}" opacity="0" transform="translate(0,-6)">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" '
            f'dur="0.35s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0,-6" to="0,0" begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
            f'</rect>'
        )

    # legend
    legend_y = height - 28
    parts.append(f'<text x="{LEFT_PAD}" y="{legend_y}" fill="#8b949e">Less</text>')
    lx = LEFT_PAD + 34
    for lvl, color in enumerate(PALETTE[:5]):
        parts.append(f'<rect x="{lx}" y="{legend_y - 10}" width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>')
        lx += BOX + GAP
    parts.append(f'<text x="{lx + 4}" y="{legend_y}" fill="#8b949e">More</text>')

    total = stats.get("total_active_days", len(days))
    streak = stats.get("current_streak", 0)
    parts.append(
        f'<text x="{LEFT_PAD}" y="{height - 8}" fill="#8b949e">'
        f'{total} contributions in the last year &#8226; current streak {streak} days</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    payload = load()
    svg = build_svg(payload)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT}")
