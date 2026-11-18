"""A single strip of public commit days above the Panda shuttle's service road."""

from datetime import timedelta
from html import escape

from mechanism import HEIGHT, LEFT, WIDTH, Route, Stop, artwork, calendar_seed, rig
from motion import track
from relay import PHASES, reflector, relay, pennant
from shuttle import beams, blaster_art, shuttle

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


def calendar_days(end, counts, geometry):
    start = end - timedelta(days=364)
    origin = start - timedelta(days=(start.weekday() + 1) % 7)
    cells = []
    for index in range(365):
        day = start + timedelta(days=index)
        week, row = divmod((day - origin).days, 7)
        count = counts.get(day, 0)
        cells.append(
            Stop(
                day,
                LEFT + week * geometry["pitch"] + geometry["size"] / 2,
                row,
                count,
                level(count),
            )
        )
    return cells


def render(username, end, counts):
    model = rig()
    geometry = model["geometry"]
    cells = calendar_days(end, counts, geometry)
    active = [c for c in cells if c.count > 0]
    route = Route(active, model, calendar_seed(username, end, active))
    size = geometry["size"]
    total = sum(c.count for c in cells)
    chapter = (
        "A single Franka Panda plays First Light with an arcade blaster. Every active date goes dark on impact. "
        "After the last tile the lunar antenna opens, sends a signal and raises the victory pennant."
        if active
        else "The arm is parked and the lunar relay is asleep."
    )
    light = "".join(f".l{i}{{fill:{ink}}}" for i, (_, ink, _) in enumerate(BANDS))
    dark = "".join(f".l{i}{{fill:{ink}}}" for i, (_, _, ink) in enumerate(BANDS))
    ids = {cell: f"d{i}" for i, cell in enumerate(cells)}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        f'<title id="title">First Light · Commit calendar for {escape(username)}</title>',
        f'<desc id="desc">{total:,} public commit contributions from {cells[0].day} through {end}. {chapter}</desc>',
        "<metadata>Panda geometry from Franka Robotics via MuJoCo Menagerie, Apache-2.0. First Light artwork and choreography by Antikythera.</metadata>",
        "<style>"
        + light
        + ".road{fill:#e7ecf1;stroke:#cbd4db}.mark{stroke:#b7c4ce}.bus{stroke:#c5d2d8}.signal{stroke:#287a83}.beam{stroke:#258d9e}.spark{stroke:#528694}"
        "@media(prefers-color-scheme:dark){"
        + dark
        + ".road{fill:#202b36;stroke:#384654}.mark{stroke:#526272}.bus{stroke:#344b58}.signal{stroke:#a2e9eb}.beam{stroke:#97e9ed}.spark{stroke:#b7edef}}"
        ".moving{display:none}@media(prefers-reduced-motion:no-preference){.moving{display:inline}.still{display:none}}</style>",
        '<defs><radialGradient id="tire-shadow"><stop stop-color="#091019" stop-opacity=".40"/><stop offset="1" stop-color="#091019" stop-opacity="0"/></radialGradient>',
        f'<rect id="socket" width="{size}" height="{size}" rx="2.5"/>',
        blaster_art(),
        artwork(route.frames),
        *(reflector(i) for i in range(PHASES + 1 if active else 1)),
        '<g id="year">',
    ]
    sockets = []
    for c in cells:
        x = c.x - size / 2
        y = geometry["top"] + c.row * geometry["pitch"]
        parts.append(
            f'<g id="{ids[c]}" data-day="{c.day}" transform="translate({x:g} {y:g})" class="l{c.shade}"><title>{c.day} · {c.count} commits</title><use href="#socket"/></g>'
        )
        sockets.append(f'<use href="#socket" x="{x:g}" y="{y:g}"/>')
    parts.extend(
        (
            "</g></defs>",
            '<path class="road" d="M17 179H962l9 19-9 6H15l-8-6z" stroke-width=".8" stroke-linejoin="round"/>',
            '<path class="mark" d="M20 191h936" fill="none" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="11 13"/>',
            '<path class="bus" d="M19 198.5H912" fill="none" stroke-width="1"/>',
        )
    )
    if active:
        parts.extend(('<g class="l0">', "".join(sockets), "</g>"))
    parts.extend(
        (
            '<g class="still">' if active else "<g>",
            '<use href="#year"/>',
            pennant(route, False),
            relay(route, False),
            shuttle(route, False),
            "</g>",
        )
    )
    if active:
        parts.append('<g class="moving" data-story="first-light">')
        parts.append(
            track(
                route.time,
                "opacity",
                [(0, 1), (route.time - 440, 1), (route.time, 0)],
                mode="linear",
            )
        )
        for shot in route.shots:
            hide = track(route.time, "opacity", [(0, 1), (shot.hit, 0)])
            parts.append(
                f'<g data-target="{shot.tile.day}">{hide}<use href="#{ids[shot.tile]}"/></g>'
            )
        parts.extend(
            (
                pennant(route, True),
                relay(route, True),
                shuttle(route, True),
                beams(route),
                "</g>",
            )
        )
    return "\n".join(parts + ["</svg>"])
