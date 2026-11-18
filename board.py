"""A single horizontal strip of 365 commit days beside a stationary robot arm."""

from datetime import timedelta
from html import escape

from artwork import studio_plate
from mechanism import (
    CELL,
    HEIGHT,
    LEFT,
    PITCH,
    TOP,
    WIDTH,
    Mission,
    Stop,
    artwork,
    calendar_seed,
    rig,
)
from motion import track
from station import arm, beams, pennant, platform

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


def calendar_days(end, counts):
    start = end - timedelta(days=364)
    origin = start - timedelta(days=(start.weekday() + 1) % 7)
    cells = []
    for index in range(365):
        day = start + timedelta(days=index)
        week, row = divmod((day - origin).days, 7)
        count = counts.get(day, 0)
        cells.append(
            Stop(day, LEFT + week * PITCH + CELL / 2, row, count, level(count))
        )
    return cells


def render(username, end, counts, plate=None):
    plate = plate or studio_plate()
    cells = calendar_days(end, counts)
    active = [c for c in cells if c.count]
    mission = Mission(active, rig(), plate, calendar_seed(username, end, active))
    total = sum(c.count for c in cells)
    chapter = (
        f"A Franka Panda holds {plate.title} on a fixed pedestal. Each lit date fades on impact. "
        "A gold pennant rises beside the base after the last date goes dark."
        if active
        else "The arm rests on its pedestal beside an empty year."
    )
    light = "".join(f".l{i}{{fill:{ink}}}" for i, (_, ink, _) in enumerate(BANDS))
    dark = "".join(f".l{i}{{fill:{ink}}}" for i, (_, _, ink) in enumerate(BANDS))
    ids = {cell: f"d{i}" for i, cell in enumerate(cells)}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        f'<title id="title">First Light · Commit calendar for {escape(username)}</title>',
        f'<desc id="desc">{total:,} public commit contributions from {cells[0].day} through {end}. {escape(chapter)}</desc>',
        "<metadata>Franka Panda geometry via MuJoCo Menagerie, Apache-2.0. "
        f"First Light illustration and choreography by Antikythera. {escape(plate.credit)}</metadata>",
        "<style>" + light + ".beam{stroke:#bd504a}.spark{stroke:#ae5349}"
        "@media(prefers-color-scheme:dark){"
        + dark
        + ".beam{stroke:#ff9c8b}.spark{stroke:#ffbcab}}"
        ".moving{display:none}@media(prefers-reduced-motion:no-preference){.moving{display:inline}.still{display:none}}</style>",
        '<defs><radialGradient id="foot-shadow"><stop stop-color="#101c27" stop-opacity=".37"/><stop offset="1" stop-color="#101c27" stop-opacity="0"/></radialGradient>',
        f'<rect id="socket" width="{CELL}" height="{CELL}" rx="2.5"/>',
        plate.symbol(),
        artwork(mission.frames),
        '<g id="year">',
    ]
    sockets = []
    for c in cells:
        x, y = c.x - CELL / 2, TOP + c.row * PITCH
        parts.append(
            f'<g id="{ids[c]}" data-day="{c.day}" transform="translate({x:g} {y:g})" class="l{c.shade}"><title>{c.day} · {c.count} commits</title><use href="#socket"/></g>'
        )
        sockets.append(f'<use href="#socket" x="{x:g}" y="{y:g}"/>')
    parts.extend(("</g></defs>", platform()))
    if active:
        parts.extend(('<g class="l0">', "".join(sockets), "</g>"))
    parts.extend(
        (
            '<g class="still">' if active else "<g>",
            '<use href="#year"/>',
            arm(mission, False),
            "</g>",
        )
    )
    if active:
        parts.append('<g class="moving" data-story="first-light">')
        for shot in mission.shots:
            hide = track(mission.time, "opacity", [(0, 1), (shot.hit, 0)])
            parts.append(
                f'<g data-target="{shot.tile.day}">{hide}<use href="#{ids[shot.tile]}"/></g>'
            )
        parts.extend((arm(mission, True), beams(mission), pennant(mission), "</g>"))
    return "\n".join(parts + ["</svg>"])
