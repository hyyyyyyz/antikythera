"""Generate an animated, self-contained SVG assembly calendar."""

import argparse
from datetime import datetime, timedelta, timezone
from html import escape
import math
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from calendar_data import daily_commits

COLORS = ("#302c40", "#74618f", "#ac83a4", "#de997e", "#ffd28e")
PITCH = 14
LEFT, TOP = 64, 101
PARK = (874, 880, 116)
FEED = (874, 855, 151)


def level(count):
    return sum(count >= threshold for threshold in (1, 3, 6, 10))


def label(x, y, content, size=12, color="#c8c3cf", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(content))}</text>'


def arm(pose_sequence, animated=False):
    """Trace a rail carriage, shoulder, elbow and tool through the same keyframes."""
    def geometry(pose):
        base_x, tip_x, tip_y = pose
        base_y = 212
        dx, dy = tip_x - base_x, tip_y - base_y
        distance = math.hypot(dx, dy)
        # Two 75-unit links meet on the right-hand elbow branch.
        height = math.sqrt(max(0, 75**2 - (distance / 2)**2))
        elbow_x = (base_x + tip_x)/2 - dy/distance * height
        elbow_y = (base_y + tip_y)/2 + dx/distance * height
        return {
            "base": f"{base_x:.1f} {base_y}",
            "elbow": f"{elbow_x:.1f} {elbow_y:.1f}",
            "tool": f"{tip_x:.1f} {tip_y:.1f}",
            "upper": f"M{base_x:.1f} {base_y} L{elbow_x:.1f} {elbow_y:.1f}",
            "lower": f"M{elbow_x:.1f} {elbow_y:.1f} L{tip_x:.1f} {tip_y:.1f}",
        }

    times = [time for time, _ in pose_sequence]
    frames = [geometry(pose) for _, pose in pose_sequence]

    def motion(key, transform=False):
        if not animated:
            return ""
        values = ";".join(frame[key] for frame in frames)
        timing = f'dur="4.4s" repeatCount="1" fill="freeze" keyTimes="{";".join(times)}" values="{values}"'
        if transform:
            return f'<animateTransform attributeName="transform" type="translate" {timing}/>'
        return f'<animate attributeName="d" {timing}/>'

    def joint(key, body):
        return f'<g transform="translate({frames[0][key]})">{motion(key, True)}{body}</g>'

    def link(key, color, width):
        return f'<path d="{frames[0][key]}" stroke="{color}" stroke-width="{width}" stroke-linecap="round">{motion(key)}</path>'

    parts = [joint("base", '<rect x="-15" y="-5" width="30" height="10" rx="3" fill="#b8a4b5" stroke="#342d40" stroke-width="2"/>')]
    for key, color, width in (("upper", "#312e41", 10), ("upper", "#a696aa", 6),
                              ("lower", "#392f43", 8), ("lower", "#efa873", 4.5)):
        parts.append(link(key, color, width))
    parts.append(joint("base", '<circle r="6" fill="#6b6077" stroke="#e1c4a2" stroke-width="2"/>'))
    parts.append(joint("elbow", '<circle r="5.5" fill="#50465d" stroke="#f2c194" stroke-width="2"/><circle r="1.6" fill="#f7e6cd"/>'))
    chip = ""
    if animated:
        chip = ('<rect x="-4" y="2" width="8" height="8" rx="1.4" fill="#ffd99f" opacity="0">'
                '<animate attributeName="opacity" dur="4.4s" values="0;1;0;0" keyTimes="0;0.22;0.63;1" calcMode="discrete" fill="freeze"/></rect>')
    parts.append(joint("tool", chip + '<path d="M-5 7V0L-2 -3H2L5 0V7" fill="none" stroke="#ede4d0" stroke-width="2"/><circle r="2.4" fill="#a598a8"/>'))
    return "".join(parts)


def render(username, end, counts):
    start = end - timedelta(days=364)
    origin = start - timedelta(days=(start.weekday() + 1) % 7)
    days = [start + timedelta(days=n) for n in range(365)]
    total = sum(counts.get(day, 0) for day in days)
    last = next((day for day in reversed(days) if counts.get(day, 0)), None)
    last_pos = None
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="274" viewBox="0 0 960 274" role="img" aria-labelledby="title desc">',
        f'<title id="title">Antikythera assembly log for {escape(username)}</title>',
        f'<desc id="desc">{total:,} public commit contributions from {start} through {end}. One socket per day. Brighter chips mark busier days.</desc>',
        '<style>.cycle{display:none}@media(prefers-reduced-motion:no-preference){.cycle{display:inline}.parked{display:none}}</style>',
        '<rect x=".5" y=".5" width="959" height="273" rx="12" fill="#191925" stroke="#4a4053"/>',
        '<g font-family="ui-monospace,SFMono-Regular,Consolas,monospace">',
        '<path d="M24 21h27v26H24z" fill="#514457"/><path d="M30 27h15v14H30z" fill="none" stroke="#f4bb87" stroke-width="2"/>',
        '<path d="M27 18v4m7-4v4m7-4v4m7-4v4M27 46v4m7-4v4m7-4v4m7-4v4" stroke="#be9b85" stroke-width="2"/>',
        label(66, 41, "Antikythera", 25, "#f8e7cb", 'font-weight="700"'),
        label(243, 39, "ASSEMBLY LOG", 11, "#b2a4b7", 'letter-spacing="2"'),
        label(932, 31, f"{total:,} commits", 19, "#ffd69b", 'text-anchor="end" font-weight="700"'),
        label(932, 49, f"{start:%b %d, %Y} – {end:%b %d, %Y}", 11, "#bcb2c6", 'text-anchor="end"'),
        '<path d="M24 62H936" stroke="#484151"/>',
        '<rect x="52" y="91" width="761" height="112" rx="4" fill="#1e1d2c" stroke="#41384c"/>',
    ]
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        svg.append(label(45, TOP + row*PITCH + 9, name, 10, "#c8bed2", 'text-anchor="end"'))
    previous_label = -100
    for day in days:
        week, row = divmod((day - origin).days, 7)
        x, y = LEFT + PITCH*week, TOP + PITCH*row
        if day.day == 1 and x - previous_label > 30:
            svg.append(label(x, 83, day.strftime("%b"), 11))
            previous_label = x
        count = counts.get(day, 0)
        svg.append(f'<g><title>{day.isoformat()} · {count} commits</title><rect x="{x}" y="{y}" width="10" height="10" rx="1.6" fill="{COLORS[0]}"/>')
        if count:
            chip = (f'<rect x="{x}" y="{y}" width="10" height="10" rx="1.6" fill="{COLORS[level(count)]}"/>'
                    f'<path d="M{x+2} {y+3}v-1h4" fill="none" stroke="#fff3d3" opacity=".38"/>')
            if day == last:
                last_pos = (x+5, y+5)
                svg.append(f'<g class="parked">{chip}</g><g class="cycle" opacity="1">'
                           '<animate attributeName="opacity" values="0;1;1" keyTimes="0;0.63;1" calcMode="discrete" dur="4.4s" fill="freeze"/>'
                           + chip + '</g>')
            else:
                svg.append(chip)
        svg.append('</g>')
    svg += [
        '<path d="M822 94v106" stroke="#51465b" stroke-dasharray="2 4"/>',
        label(875, 84, "FEEDER", 10, "#baaabd", 'text-anchor="middle" letter-spacing="2"'),
        '<rect x="842" y="148" width="38" height="35" rx="3" fill="#242230" stroke="#726077"/>',
        '<path d="M848 175h25m-25-6h25m-25-6h25" stroke="#a78173" stroke-width="2"/>',
        '<rect x="850" y="151" width="10" height="10" rx="1" fill="#d9a37f"/>',
        '<path d="M57 212h860" stroke="#484354" stroke-width="5"/><path d="M57 211h860" stroke="#837789" stroke-width="1"/>',
    ]
    resting = arm([("0", PARK)])
    if last_pos:
        x, y = last_pos
        # The carriage moves horizontally so even a months-old target stays within reach.
        base = max(65, min(881, x + 20))
        hover, contact = (base, x, y-15), (base, x, y-5)
        poses = [("0", PARK), ("0.15", FEED), ("0.22", FEED), ("0.30", (874,855,132)),
                 ("0.50", hover), ("0.56", hover), ("0.63", contact), ("0.70", contact),
                 ("0.77", hover), ("1", PARK)]
        svg.extend([f'<g class="parked">{resting}</g>', f'<g class="cycle">{arm(poses, True)}</g>'])
    else:
        svg.append(resting)
    svg += ['<path d="M24 230h912" stroke="#484151"/>', label(26, 255, "@"+username, 13, "#ebddc7"),
            label(932, 254, "commits / day", 11, "#bcb2c6", 'text-anchor="end"')]
    for i, caption in enumerate(("0", "1–2", "3–5", "6–9", "10+")):
        x = 476 + 69*i
        svg += [f'<rect x="{x}" y="244" width="10" height="10" rx="1.5" fill="{COLORS[i]}"/>',
                label(x+15, 254, caption, 11)]
    return "\n".join(svg + ["</g></svg>"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", required=True)
    parser.add_argument("--output", type=Path, default=Path("assembly-log.svg"))
    args = parser.parse_args()
    end = datetime.now(timezone.utc).date()
    counts = daily_commits(args.username, end - timedelta(days=364), end)
    drawing = render(args.username, end, counts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output.parent, delete=False) as temp:
        temp.write(drawing)
    os.replace(temp.name, args.output)
    print(f"Wrote {args.output} with {sum(counts.values()):,} public commit contributions.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError) as error:
        sys.exit(str(error))
