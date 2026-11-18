"""Layout and artwork for the desktop and compact assembly instruments."""

from datetime import timedelta
from html import escape

from mechanism import DROP, DURATION, METAL, reference, render_arm

# Lower bounds, colors and labels share one scale across the board and both legends.
BANDS = (
    (0,  "#293438", "0"),
    (1,  "#526b95", "1"),
    (2,  "#707db8", "2"),
    (3,  "#957fc0", "3"),
    (4,  "#b282ba", "4–5"),
    (6,  "#d28ba7", "6–9"),
    (10, "#e99a88", "10–19"),
    (20, "#f5b074", "20–39"),
    (40, "#f8d078", "40–79"),
    (80, "#ffecae", "80+"),
)
INK = "#f1eddd"
MUTED = "#b0b9ad"
MONO = "'IBM Plex Mono','SFMono-Regular',Consolas,monospace"
SANS = "'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"


def level(count):
    return sum(count >= minimum for minimum, _, _ in BANDS[1:])


def text(x, y, content, size=12, color=MUTED, *, font=SANS, end=False, weight=400, spacing=0):
    anchor = "end" if end else "start"
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{spacing}" text-anchor="{anchor}">{escape(str(content))}</text>')


def chip_symbols():
    parts = ['<g id="socket"><rect x=".4" y=".4" width="9.2" height="9.2" rx="1.8" fill="#182324" stroke="#3b4542" stroke-width=".7"/>'
             '<circle cx="5" cy="5" r=".95" fill="#3b4642"/></g>']
    for i, (_, color, _) in enumerate(BANDS[1:], 1):
        parts.append(f'<g id="chip-{i}"><path d="M.5 3V1L2 .5h6l1.5 1v7l-1 1H2l-1.5-1z" fill="{color}"/>'
                     '<path d="M1.6 5V2.4l1.1-.8h4.8" fill="none" stroke="#fff3d4" opacity=".44" stroke-width=".7"/>'
                     '<path d="M2.3 8.6h5.4l1-1" fill="none" stroke="#162020" opacity=".35" stroke-width=".8"/>'
                     '<rect x="2.5" y="2.5" width="1.1" height="1.1" fill="#ffefcc" opacity=".75"/></g>')
    return "".join(parts)


def insignia(x, y, scale):
    # A toothed brass wheel and an eccentric index hand reference the namesake.
    ticks = "".join(f'<path d="M0-18v3" transform="rotate({angle})"/>' for angle in range(0,360,15))
    return (f'<g transform="translate({x} {y}) scale({scale})">'
            '<circle r="22.5" fill="#24302e" stroke="#aa966e"/><circle r="19" fill="#263330" stroke="#756f56" stroke-width=".7"/>'
            f'<g stroke="#cfb580" stroke-width="1">{ticks}</g>'
            '<circle r="12" fill="none" stroke="#c2a476" stroke-width="1.2"/>'
            '<path d="M-12 7 8-12 2 2Z" fill="#eed093"/><path d="m8-12-6 14-14 5Z" fill="#af8c51"/>'
            '<circle r="3" fill="#f0d3a3" stroke="#635d44"/></g>')


def feeder(x, y, scale):
    return (f'<g transform="translate({x} {y}) scale({scale})">'
            '<path d="m-12-8 32 0 8 6v28h-40z" fill="#252f2e" stroke="#687064"/>'
            '<path d="m-8-5 25 0 7 5H-8z" fill="#7e7e66"/>'
            '<rect x="-8" y="1" width="31" height="21" rx="1" fill="#172322"/>'
            '<path d="M-5 8h23m-23 4h23m-23 4h23" stroke="#a38b62" stroke-width="1.7"/>'
            '<rect x="-5" y="-5" width="10" height="10" rx="1" fill="#f7cd8b" stroke="#a98958"/></g>')


def render(username, end, counts, compact=False):
    start = end - timedelta(days=364)
    origin = start - timedelta(days=(start.weekday()+1) % 7)
    days = [start+timedelta(days=i) for i in range(365)]
    total = sum(counts.get(d, 0) for d in days)
    latest = next((d for d in reversed(days) if counts.get(d, 0)), None)
    width, height = (440, 498) if compact else (1000, 332)
    margin = 17 if compact else 26
    left, pitch = (48, 13) if compact else (69, 13.6)
    scale = .69 if compact else 1
    park = (343, 408, 298, 353) if compact else (899, 242, 838, 158)
    supply = (269, 380) if compact else (843, 204)
    summary = f"{total:,} public commit contributions from {start} through {end}."
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">Antikythera assembly log for {escape(username)}</title>',
        f'<desc id="desc">{summary} Each socket is one day. A brass and ceramic robot places the latest chip.</desc>',
        '<style>.cycle{display:none}@media(prefers-reduced-motion:no-preference){.cycle{display:inline}.parked{display:none}}</style>',
        '<defs>'+METAL+chip_symbols()+
        '<linearGradient id="case" x2=".9" y2="1"><stop stop-color="#202a29"/><stop offset=".57" stop-color="#172323"/><stop offset="1" stop-color="#172020"/></linearGradient>'
        '<linearGradient id="deck" x2="0" y2="1"><stop stop-color="#182321"/><stop offset="1" stop-color="#202b28"/></linearGradient>'
        '<pattern id="milling" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 .5h4" stroke="#eef0cc" opacity=".023"/></pattern>'
        '<pattern id="holes" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".65" fill="#879284" opacity=".3"/></pattern></defs>',
        f'<rect x=".6" y=".6" width="{width-1.2}" height="{height-1.2}" rx="14" fill="url(#case)" stroke="#657063"/>',
        f'<rect x="2" y="2" width="{width-4}" height="{height-4}" rx="13" fill="url(#milling)"/>',
    ]
    for x in (9, width-9):
        for y in (9, height-9):
            parts.append(f'<g transform="translate({x} {y})"><circle r="2.1" fill="#19201f" stroke="#60665b" stroke-width=".6"/><path d="m-1 .7 2-1.4" stroke="#899080" stroke-width=".65"/></g>')
    parts += [insignia(39 if compact else 55, 43 if compact else 49, .79 if compact else 1.03),
              text(64 if compact else 91, 51 if compact else 62, "Antikythera", 35 if compact else 47, INK,
                   font="'Baskervville',Georgia,'Times New Roman',serif", spacing=-1.9),
              text(width-margin-5, 47 if compact else 55, f"{total:,}", 31 if compact else 39, "#f3d499",
                   end=True, weight=600, spacing=-1.5),
              text(width-margin-5, 64 if compact else 74, "PUBLIC COMMITS", 9 if compact else 10.5,
                   font=MONO, end=True, spacing=1.2),
              text(margin+4 if compact else 92, 79 if compact else 82, f"@{username}  ·  {start:%b %d, %Y} – {end:%b %d, %Y}",
                   11 if compact else 12, "#bcc1b2"),
              f'<rect x="{margin}" y="{94 if compact else 100}" width="{width-2*margin}" height="{326 if compact else 163}" rx="7" fill="url(#deck)" stroke="#566052"/>']
    # The work envelope is etched into the service bay, separate from the data.
    cx,cy = park[:2]
    bay_x, bay_y = (202, 341) if compact else (807, 107)
    bay_width, bay_height = (205, 70) if compact else (158, 141)
    parts.append(f'<svg x="{bay_x}" y="{bay_y}" width="{bay_width}" height="{bay_height}" viewBox="0 0 {bay_width} {bay_height}">'
                 f'<rect width="100%" height="100%" fill="url(#holes)"/>')
    for rad in (36,63,89,116):
        parts.append(f'<circle cx="{cx-bay_x}" cy="{cy-bay_y}" r="{rad}" fill="none" stroke="#617163" stroke-width=".7" stroke-dasharray="3 4" opacity=".62"/>')
    parts.append('</svg>')
    labeled = set()
    target = None
    for d in days:
        week, row = divmod((d-origin).days, 7)
        band, column = divmod(week, 27) if compact else (0, week)
        top = (126,249)[band] if compact else 135
        x, y = left+pitch*column, top+pitch*row
        begins_band = d == start or (compact and column == 0 and row == 0)
        # Give a nearby month boundary priority over a short partial month.
        next_month = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        mark_partial = begins_band and (next_month-d).days >= 17
        month_key = (band, d.year, d.month)
        if (d.day == 1 or mark_partial) and month_key not in labeled:
            parts.append(text(x,top-10,d.strftime("%b"),10.3 if compact else 11.5, "#c1c4b4", font=MONO))
            labeled.add(month_key)
        count = counts.get(d,0)
        parts.append(f'<g transform="translate({x:.1f} {y:.1f})"><title>{d} · {count} commits</title>')
        if d == latest:
            target = (x+5, y+5, top)
            chip = reference(f"chip-{level(count)}")
            parts += [reference("socket"), f'<g class="parked">{chip}</g><g class="cycle">'
                      f'<animate attributeName="opacity" values="0;1;1" keyTimes="0;{DROP};1" calcMode="discrete" dur="{DURATION}" fill="freeze"/>{chip}</g>']
        else:
            parts.append(reference(f"chip-{level(count)}" if count else "socket"))
        parts.append('</g>')
    for top in ((126,249) if compact else (135,)):
        for row, dayname in ((1,"M"),(3,"W"),(5,"F")):
            parts.append(text(left-10,top+row*pitch+9,dayname,10.5,font=MONO,end=True))
    rail_x1,rail_x2 = margin+12,width-margin-13
    for y in ([228, 351, 408] if compact else [242]):
        parts.append(f'<path d="M{rail_x1} {y}H{rail_x2}" stroke="#101a18" stroke-width="6"/>'
                     f'<path d="M{rail_x1} {y-2}H{rail_x2}" stroke="#778073" stroke-width="1"/>'
                     f'<path d="M{rail_x1} {y+1}H{rail_x2}" stroke="#3c4742" stroke-width="1.5" stroke-dasharray="2 4"/>')
    parts.append(feeder(*supply,scale))
    if not compact:
        parts.append(text(961,123,"FEEDER",10,"#a4ad9d",font=MONO,end=True,spacing=1.2))
    idle = render_arm([(0,park)], scale, BANDS[-1][1], False)
    if target:
        x,y,top = target
        by = top+102 if compact else park[1]
        bx = min(x+19, 352) if compact else x+19
        hover = (bx,by,x,y-17*scale)
        place = (bx,by,x,y-10*scale)
        feed = (*park[:2],supply[0],supply[1]-10*scale)
        lift = (*park[:2],supply[0],supply[1]-25*scale)
        poses = [(0,park),(.16,feed),(.23,feed),(.31,lift),(.50,hover),(.55,hover),
                 (.65,place),(.71,place),(.79,hover),(1,park)]
        moving = render_arm(poses,scale,BANDS[level(counts[latest])][1],True)
        parts += [f'<g class="parked">{idle}</g>',f'<g class="cycle">{moving}</g>']
    else:
        parts.append(idle)
    if latest:
        qty = counts[latest]
        newest = f"{latest:%b %d}  ·  {qty} commit{'s' if qty != 1 else ''}"
    else:
        newest = "No public commits"
    if compact:
        parts += [text(32,376,"LATEST CHIP",10,font=MONO,spacing=1.2),
                  text(32,398,newest,16,INK,weight=550),
                  text(23,445,"Commits",13,INK,weight=550), text(23,462,"per day",12)]
    else:
        parts += [text(29,288,"LATEST CHIP",10,font=MONO,spacing=1.3),
                  text(29,311,newest,17,INK,weight=550),
                  text(971,288,"COMMITS PER DAY",10,font=MONO,end=True,spacing=1.3)]
    for i,(_, _, caption) in enumerate(BANDS):
        if compact:
            row, column = divmod(i, 5)
            x, y = 89+column*68, 435+row*26
        else:
            x, y = 314+i*67, 301
        parts += [f'<g transform="translate({x} {y})">{reference("socket" if i == 0 else f"chip-{i}")}</g>',
                  text(x+14,y+9,caption,10.8 if compact else 11.5,INK,font=MONO)]
    return "\n".join(parts+['</svg>'])
