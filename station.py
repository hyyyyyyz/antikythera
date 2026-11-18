"""The stationary Panda, light effects and final pennant in screen coordinates."""

from math import hypot

from mechanism import SCALE, STATION_X, STATION_Y
from motion import frames_track, number, track, xy


def platform():
    return (
        f'<g data-part="fixed-platform" transform="translate({STATION_X} {STATION_Y}) scale({SCALE})">'
        '<ellipse cx="19" cy="-4" rx="49" ry="7" fill="url(#foot-shadow)"/>'
        '<use href="#plinth0"/></g>'
    )


def arm(mission, moving):
    frames = mission.frames if moving else mission.frames[:1]
    first = frames[0]

    def pose(frame):
        return f"#a{frame.pose}"

    def grip(frame):
        return xy(mission.tips[frame.pose])

    turns = frames_track(
        frames,
        "transform",
        lambda f: number(f.angle),
        mode="linear",
        transform="rotate",
    )
    return "".join(
        (
            f'<g data-arm="panda" transform="translate({STATION_X} {STATION_Y}) scale({SCALE})">',
            f'<use href="{pose(first)}">{frames_track(frames, "href", pose)}</use>',
            f'<g data-part="grip" transform="translate({grip(first)})">',
            frames_track(frames, "transform", grip, transform="translate"),
            '<use href="#h0"/>',
            f'<g data-part="wrist-art" transform="rotate({number(first.angle)})">{turns}<use href="#prop-art"/></g>',
            '<use href="#finger0"/></g></g>',
        )
    )


def pennant(mission):
    start, duration = mission.hoist, mission.time
    lift = [
        (0, 0),
        (start, 0),
        (start + 150, 0.09),
        (start + 540, 0.78),
        (start + 870, 1),
    ]
    pole = track(
        duration,
        "transform",
        [(t, "1 " + number(u)) for t, u in lift],
        mode="linear",
        transform="scale",
    )
    cloth = track(
        duration,
        "transform",
        [(t, "0 " + number(-62 * u)) for t, u in lift],
        mode="linear",
        transform="translate",
    )
    visible = track(
        duration,
        "opacity",
        [(0, 0), (start, 0), (start + 140, 1), (duration - 300, 1), (duration, 0)],
        mode="linear",
    )
    flutter = track(
        duration,
        "transform",
        [
            (0, ".10 .28"),
            (start, ".10 .28"),
            (start + 300, ".48 .82"),
            (start + 780, "1 1"),
            (start + 1090, ".88 .94"),
            (start + 1510, "1 1"),
            (start + 1960, ".93 .96"),
            (start + 2420, "1 1"),
        ],
        mode="linear",
        transform="scale",
    )
    return "".join(
        (
            '<g data-part="victory-flag" transform="translate(966 143)" opacity="0">',
            visible,
            '<g transform="scale(1 0)">',
            pole,
            '<path d="M0 0v-63" stroke="#718591" stroke-width="2.1" stroke-linecap="round"/>',
            '<path d="M.55 -1v-60" stroke="#c6d0cc" stroke-width=".65"/></g>',
            '<g transform="translate(0 0)">',
            cloth,
            '<circle cy="-1" r="1.9" fill="#dab878"/><g transform="scale(.1 .28)">',
            flutter,
            '<path d="M.8 1Q8-2 15 .1T31 0l5-1-6 7 5 5.3q-8 2.9-16.5.7Q9.4 9.7.8 13.7z" fill="#e7af4d" stroke="#9d7236" stroke-width=".8" stroke-linejoin="round"/>',
            '<path d="M1 1Q8-2 15 .1T31 0l5-1-2.5 2.6q-10 3.2-18.5.7Q8.2.6 1 4z" fill="#ffe5a5"/>',
            '<path d="M4 2.7h3v3H4zm3 3h3v3H7zm-3 3h3v3H4z" fill="#51493b"/>',
            "</g></g></g>",
        )
    )


def beams(mission):
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
    for shot in mission.shots:
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
        glints.extend(((h - 1, 0), (h, 0.95), (h + 60, 0.62), (h + 85, 0)))
        rings.extend(((h - 1, 0.24), (h, 0.24), (h + 85, 1)))
    return "".join(
        (
            '<g data-part="light-effects" fill="none" pointer-events="none">',
            '<path d="M0 0L0 0" class="beam" opacity="0" stroke-width=".8">',
            track(mission.time, "d", shape),
            track(mission.time, "opacity", afterglow, mode="linear"),
            "</path>",
            '<g data-part="muzzle-flash" opacity="0">',
            track(mission.time, "opacity", flash, mode="linear"),
            track(mission.time, "transform", muzzles, transform="translate"),
            '<circle r="4.8" fill="#fb8979" opacity=".25"/><circle r="2.4" fill="#fff2da"/></g>',
            '<path data-part="pulse" d="M0 0L0 0" class="beam" pathLength="1" opacity="0" stroke-width="2.0" stroke-linecap="round">',
            track(mission.time, "d", shape),
            track(mission.time, "opacity", opacity),
            track(mission.time, "stroke-dasharray", dash),
            track(mission.time, "stroke-dashoffset", offset, mode="linear"),
            "</path>",
            '<g data-part="impact" opacity="0">',
            track(mission.time, "opacity", glints, mode="linear"),
            track(mission.time, "transform", impacts, transform="translate"),
            "<g>",
            track(mission.time, "transform", rings, mode="linear", transform="scale"),
            '<path d="M0-8 8 0 0 8-8 0z" class="spark" stroke-width="1.1"/>',
            '<path d="M-8-4l-2-1m18 9 2 1m-8-14 1-2m-5 19-1 2" class="spark" stroke-width="1.25" stroke-linecap="round"/></g></g></g>',
        )
    )
