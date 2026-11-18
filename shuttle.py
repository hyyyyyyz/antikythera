"""The Panda carries a fictional arcade blaster. All effects live in the SVG."""

from math import hypot
from mechanism import BARREL
from motion import frames_track, number, track, xy


def blaster_art():
    # The rotating light head is drawn around the grip in screen space.
    return f"""<g id="light-head">
<path d="M-6 -6 -2 -9 9 -9 12 -6 23 -6 27 -3 31 -3V4l-7 3H6L1 10-5 8z" fill="#203140" stroke="#101e29" stroke-width="1.2" stroke-linejoin="round"/>
<path d="m-5-5 4-4 10 .3 3 2.5h10l4 3.1-4 3.1H1l-6-1.6z" fill="#cbd9df"/>
<path d="M-2-4h19l4 2.2-4 2.3H0z" fill="#4e6879"/>
<path d="m1-6.8 6 .2 2 1.2H1z" fill="#ffc66b"/>
<path d="M8 2.2h15l-2.3 2.5H7z" fill="#6994a1"/>
<path d="m10 -2.3 3 0m1.2 0h3" stroke="#aaf7ee" stroke-width="1.3" stroke-linecap="round"/>
<path d="m23-4.3 5-1.1 5 .7 2.4 2.1v6l-2.4 1.7-5 .8-5-.9z" fill="#415766" stroke="#142934" stroke-width=".8"/>
<path d="m26-3.9 4.4-.6 1.2.8v6.5l-1.2.7-4.4-.2z" fill="#7ca4ae"/>
<path d="M{BARREL-2} -2.9 Q{BARREL+1} 0 {BARREL-2} 3" fill="none" stroke="#a6fff2" stroke-width="2" stroke-linecap="round"/>
<circle r="5.4" fill="#758b98" stroke="#253949" stroke-width="1.3"/><circle r="2.65" fill="#304b5a"/><circle cx="-.7" cy="-.8" r=".9" fill="#bfdbdf"/>
</g>"""


def shuttle(route, moving):
    frames = route.frames if moving else route.frames[:1]
    road = route.model["geometry"]["road_y"]

    def base(f):
        return xy((f.x, road))

    def tip(f):
        return xy(route.model["tip"][f.pose])

    def sprite(value):
        return (
            f'<use href="{value(frames[0])}">{frames_track(frames,"href",value)}</use>'
        )

    return "".join(
        (
            f'<g data-part="shuttle" transform="translate({base(frames[0])})">',
            frames_track(
                frames, "transform", base, mode="linear", transform="translate"
            ),
            '<ellipse cx="-9" cy="5" rx="67" ry="11" fill="url(#tire-shadow)"/>',
            sprite(lambda f: f"#c{f.wheel}"),
            '<g data-arm="panda">',
            sprite(lambda f: f"#a{f.pose}"),
            f'<g data-part="grip" transform="translate({tip(frames[0])})">',
            frames_track(frames, "transform", tip, transform="translate"),
            f'<g data-part="blaster" transform="rotate({number(frames[0].angle)})">',
            frames_track(
                frames,
                "transform",
                lambda f: number(f.angle),
                mode="linear",
                transform="rotate",
            ),
            '<use href="#light-head"/></g><use href="#h2"/></g></g></g>',
        )
    )


def beams(route):
    # A single reusable path carries short traveling pulses. Only its endpoints change per shot.
    shape = [(0, "M0 0L0 0")]
    opacity = [(0, 0)]
    dash = [(0, "0 1")]
    offset = [(0, 0)]
    impacts = [(0, "0 0")]
    rings = [(0, 0.25)]
    glints = [(0, 0)]
    afterglow = [(0, 0)]
    flash = [(0, 0)]
    muzzles = [(0, "0 0")]
    for shot in route.shots:
        f, h = shot.fired, shot.hit
        length = hypot(shot.target[0] - shot.muzzle[0], shot.target[1] - shot.muzzle[1])
        width = min(0.35, 58 / length)
        shape.append((f, "M" + xy(shot.muzzle) + "L" + xy(shot.target)))
        opacity.extend(((f, 1), (h + 17, 0)))
        afterglow.extend(((h - 1, 0), (h, 0.27), (h + 32, 0)))
        flash.extend(((f - 1, 0), (f, 0.92), (f + 29, 0.33), (f + 42, 0)))
        muzzles.append((f, xy(shot.muzzle)))
        dash.append((f, number(width) + " 2"))
        offset.extend(((f - 1, 0), (f, number(width)), (h, -1 + width), (h + 16, -1)))
        impacts.append((h, xy(shot.target)))
        glints.extend(((h - 1, 0), (h, 0.95), (h + 60, 0.62), (h + 95, 0)))
        rings.extend(((h - 1, 0.24), (h, 0.24), (h + 95, 1)))
    return "".join(
        (
            '<g data-part="arcade-effects" fill="none" pointer-events="none">',
            '<path d="M0 0L0 0" class="beam" opacity="0" stroke-width=".8">',
            track(route.time, "d", shape),
            track(route.time, "opacity", afterglow, mode="linear"),
            "</path>",
            '<g data-part="muzzle-flash" opacity="0">',
            track(route.time, "opacity", flash, mode="linear"),
            track(route.time, "transform", muzzles, transform="translate"),
            '<circle r="4.8" fill="#72ddd9" opacity=".25"/><circle r="2.4" fill="#d2fff1"/></g>',
            '<path data-part="pulse" d="M0 0L0 0" class="beam" pathLength="1" opacity="0" stroke-width="2.0" stroke-linecap="round">',
            track(route.time, "d", shape),
            track(route.time, "opacity", opacity),
            track(route.time, "stroke-dasharray", dash),
            track(route.time, "stroke-dashoffset", offset, mode="linear"),
            "</path>",
            '<g data-part="impact" opacity="0">',
            track(route.time, "opacity", glints, mode="linear"),
            track(route.time, "transform", impacts, transform="translate"),
            "<g>",
            track(route.time, "transform", rings, mode="linear", transform="scale"),
            '<path d="M0-8 8 0 0 8-8 0z" class="spark" stroke-width="1.1"/>',
            '<path d="M-8-4l-2-1m18 9 2 1m-8-14 1-2m-5 19-1 2" class="spark" stroke-width="1.25" stroke-linecap="round"/></g></g></g>',
        )
    )
