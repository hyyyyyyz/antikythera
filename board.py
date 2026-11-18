"""One continuous, responsive strip of 53 weeks and a collaborative arm."""

from datetime import timedelta
from html import escape

from mechanism import ART, DROP, DURATION, PICK, SUPPLY, arm

# Each threshold has a light-mode and a dark-mode ink.
BANDS = (
    (0,  "#edf0f3", "#212b36"),
    (1,  "#c6d6e5", "#30455e"),
    (2,  "#afc8dc", "#3e5774"),
    (3,  "#96b6cf", "#4c6988"),
    (4,  "#7ca3c2", "#5a7d9e"),
    (6,  "#638faf", "#7192ae"),
    (10, "#4e799c", "#88a8bf"),
    (20, "#3c678a", "#9ebdd0"),
    (40, "#2b5576", "#b8d3e0"),
    (80, "#1a425f", "#d5e9ef"),
)


def level(count):
    return sum(count >= minimum for minimum, _, _ in BANDS[1:])


def render(username, end, counts):
    start = end-timedelta(days=364)
    origin = start-timedelta(days=(start.weekday()+1)%7)
    days = [start+timedelta(days=i) for i in range(365)]
    total = sum(counts.get(d,0) for d in days)
    latest = next((d for d in reversed(days) if counts.get(d,0)),None)
    light = "".join(f".l{i}{{fill:{c}}}" for i,(_,c,_) in enumerate(BANDS))
    dark = "".join(f".l{i}{{fill:{c}}}" for i,(_,_,c) in enumerate(BANDS))
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="978" height="164" viewBox="0 0 978 164" role="img" aria-labelledby="title desc">',
        f'<title id="title">Commit calendar for {escape(username)}</title>',
        f'<desc id="desc">{total:,} public commit contributions from {start} through {end}. Each square is one day. The arm places the most recent active day.</desc>',
        '<style>'+light+'@media(prefers-color-scheme:dark){'+dark+'}.cycle{display:none}'
        '@media(prefers-reduced-motion:no-preference){.cycle{display:inline}.parked{display:none}}</style>',
        '<defs>'+ART+'</defs>',
    ]
    target=None
    for day in days:
        week,row=divmod((day-origin).days,7)
        x,y=12+15*week,34+15*row
        n=counts.get(day,0)
        rect=f'<rect width="11.5" height="11.5" rx="2.6" class="l{level(n)}"/>'
        parts.append(f'<g transform="translate({x} {y})"><title>{day} · {n} commits</title>')
        if day==latest:
            target=(x+5.75,y+5.75)
            parts.extend(['<rect width="11.5" height="11.5" rx="2.6" class="l0"/>',
                          f'<g class="parked">{rect}</g><g class="cycle">'
                          f'<animate attributeName="opacity" dur="{DURATION}" values="0;1;1" keyTimes="0;{DROP};1" calcMode="discrete" fill="freeze"/>{rect}</g>'])
        else:
            parts.append(rect)
        parts.append('</g>')
    idle=arm()
    if target:
        color=f"l{level(counts[latest])}"
        loose=(f'<rect x="{SUPPLY[0]-5}" y="{SUPPLY[1]-5}" width="10" height="10" rx="2" class="{color}" opacity="0">'
               f'<animate attributeName="opacity" values="1;0;0" keyTimes="0;{PICK};1" calcMode="discrete" dur="{DURATION}" fill="freeze"/></rect>')
        parts += [f'<g class="parked">{idle}</g>', f'<g class="cycle">{loose}{arm(target,color)}</g>']
    else:
        parts.append(idle)
    return "\n".join(parts+["</svg>"])
