"""A single strip of public commit days above the Panda shuttle's service road."""

from datetime import timedelta
from html import escape

from mechanism import (
    HEIGHT,
    LEFT,
    WIDTH,
    Route,
    Stop,
    animate,
    artwork,
    rig,
    route_stops,
    trolley,
)

# Lower bound, light-mode ink, dark-mode ink.
BANDS = (
    (0, "#edf0f3", "#212b36"),
    (1, "#c6d6e5", "#30455e"),
    (2, "#afc8dc", "#3e5774"),
    (3, "#96b6cf", "#4c6988"),
    (4, "#7ca3c2", "#5a7d9e"),
    (6, "#638faf", "#7192ae"),
    (10, "#4e799c", "#88a8bf"),
    (20, "#3c678a", "#9ebdd0"),
    (40, "#2b5576", "#b8d3e0"),
    (80, "#1a425f", "#d5e9ef"),
)


def level(count):
    return sum(count >= minimum for minimum, _, _ in BANDS[1:])


def render(username, end, counts):
    model = rig()
    geometry = model["geometry"]
    start = end - timedelta(days=364)
    origin = start - timedelta(days=(start.weekday() + 1) % 7)
    size = geometry["size"]
    cells = []
    for n in range(365):
        day = start + timedelta(days=n)
        week, row = divmod((day - origin).days, 7)
        count = counts.get(day, 0)
        cells.append(
            Stop(
                day,
                LEFT + week * geometry["pitch"] + size / 2,
                row,
                count,
                level(count),
            )
        )
    route = Route(route_stops([c for c in cells if c.count]), model)
    active_stops = set(route.stops)
    total = sum(c.count for c in cells)
    description = (
        "A wheeled Franka Panda shuttle collects date tiles and returns them to their original days."
        if active_stops
        else "The Franka Panda shuttle is parked below the empty calendar."
    )
    light = "".join(f".l{i}{{fill:{ink}}}" for i, (_, ink, _) in enumerate(BANDS))
    dark = "".join(f".l{i}{{fill:{ink}}}" for i, (_, _, ink) in enumerate(BANDS))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        f'<title id="title">Commit calendar for {escape(username)}</title>',
        f'<desc id="desc">{total:,} public commit contributions from {start} through {end}. {description}</desc>',
        "<metadata>Panda robot geometry from Franka Robotics via MuJoCo Menagerie, Apache-2.0. Studio renders, shuttle design and animation by Antikythera.</metadata>",
        "<style>" + light + ".road{fill:#e7ecf1;stroke:#cbd4db}.mark{stroke:#b7c4ce}"
        "@media(prefers-color-scheme:dark){"
        + dark
        + ".road{fill:#202b36;stroke:#384654}.mark{stroke:#526272}}"
        ".moving{display:none}@media(prefers-reduced-motion:no-preference){.moving{display:inline}.still{display:none}}</style>",
        '<defs><radialGradient id="tire-shadow"><stop stop-color="#091019" stop-opacity=".42"/><stop offset="1" stop-color="#091019" stop-opacity="0"/></radialGradient>',
        '<g id="block"><path d="M-5-4l2-2h8v9l-2 2h-8z"/><path d="M-5-4l2-2h8L3-4z" fill="white" opacity=".36"/><path d="M3-4l2-2v9L3 5z" fill="#091729" opacity=".28"/></g>',
        artwork(route.frames),
        "</defs>",
        '<path class="road" d="M17 179H962l9 19-9 6H15l-8-6z" stroke-width=".8" stroke-linejoin="round"/>',
        '<path class="mark" d="M20 191.5h936" fill="none" stroke-width="1.35" stroke-linecap="round" stroke-dasharray="11 13"/>',
    ]
    for c in cells:
        x = c.x - size / 2
        y = geometry["top"] + c.row * geometry["pitch"]
        parts.append(
            f'<g data-day="{c.day}" transform="translate({x:g} {y:g})"><title>{c.day} · {c.count} commits</title>'
        )
        rect = f'<rect width="{size}" height="{size}" rx="2.5" class="l{c.shade}"/>'
        if c in active_stops:
            show = animate(
                route.frames, "opacity", lambda f: int(f.held != c and c not in f.cargo)
            )
            parts += [
                f'<rect width="{size}" height="{size}" rx="2.5" class="l0"/>',
                f'<g class="still">{rect}</g><g class="moving">{show}{rect}</g>',
            ]
        else:
            parts.append(rect)
        parts.append("</g>")
    if route.stops:
        parts += [
            f'<g class="still">{trolley(route,False)}</g>',
            f'<g class="moving">{trolley(route,True)}</g>',
        ]
    else:
        parts.append(trolley(route, False))
    return "\n".join(parts + ["</svg>"])
