"""A folding parabolic antenna for the final transmission of First Light."""

from math import cos, pi, sin, sqrt
from motion import number, track

PHASES = 14


def unit(v):
    length = sqrt(sum(x * x for x in v))
    return tuple(x / length for x in v)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def points(vertices):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y, _ in vertices)


def reflector(phase):
    """Project each hinged panel into the camera and paint the far surfaces first."""
    u = phase / PHASES
    opening = u * u * (3 - 2 * u)
    axis = unit((0.09 + 0.54 * opening, -0.94 + 0.38 * opening, 0.33 + 0.24 * opening))
    right = unit((-axis[1], axis[0], 0))
    up = cross(axis, right)

    def vertex(theta, fraction):
        radius = 32 * fraction * (0.115 + 0.885 * opening)
        height = 32 * (0.92 * (1 - opening) * fraction + 0.30 * opening * fraction**1.8)
        return tuple(
            axis[j] * height + radius * (cos(theta) * right[j] + sin(theta) * up[j])
            for j in range(3)
        )

    faces = []
    light = unit((-0.39, -0.67, 0.74))
    petals = 12
    for i in range(petals):
        a, b = (i + 0.025) * 2 * pi / petals, (i + 0.975) * 2 * pi / petals
        for r1, r2 in ((0.07, 0.52), (0.52, 1)):
            quad = [vertex(a, r1), vertex(a, r2), vertex(b, r2), vertex(b, r1)]
            p, q, r = quad[:3]
            normal = unit(
                cross([y - x for x, y in zip(p, q)], [y - x for x, y in zip(p, r)])
            )
            diffuse = sum(x * y for x, y in zip(normal, light))
            tone = round(142 + 60 * diffuse + 7 * (i % 2) + 4 * r2)
            rgb = tuple(max(0, min(255, tone + v)) for v in (-15, 0, 10))
            color = "#%02x%02x%02x" % rgb
            faces.append(
                (
                    sum(v[2] for v in quad) / 4,
                    f'<polygon points="{points(quad)}" fill="{color}" stroke="#586b78" stroke-width=".38" stroke-linejoin="round"/>',
                )
            )
    surfaces = "".join(p[1] for p in sorted(faces))
    horn = tuple(n * (31 + 2 * opening) for n in axis)
    struts = [vertex((i + 0.5) * 2 * pi / petals, 0.91) for i in (1, 5, 9)]
    ribs = "".join(
        f'<path d="M{p[0]:.2f} {p[1]:.2f} L{horn[0]:.2f} {horn[1]:.2f}" fill="none" stroke="#aab9c0" stroke-width=".9"/>'
        for p in struts
    )
    return f'<g id="dish{phase}">{surfaces}{ribs}<circle cx="{horn[0]:.2f}" cy="{horn[1]:.2f}" r="2.1" fill="#d9e8ea" stroke="#506372" stroke-width=".75"/></g>'


def relay(route, moving):
    duration = route.time if moving else 0
    parts = [
        '<g data-part="relay" transform="translate(910 146)">',
        '<ellipse cx="-1" cy="43" rx="36" ry="6.5" fill="url(#tire-shadow)"/>',
        '<path d="m-32 35 9-7h43l10 6-5 7h-51z" fill="#45525e" stroke="#293a47" stroke-width=".9"/>',
        '<path d="m-32 35 8-6h44l9 5-13 3h-42z" fill="#9cabb4"/>',
        '<path d="m-24 29 3-11 13-4 23 2 7 12-9 6-28-1z" fill="#71828e"/>',
        '<path d="m-21 18 13-4 23 2-7 5-23 1z" fill="#cfdbdf"/><path d="m8 21 7-5 7 12-9 6z" fill="#465964"/>',
        '<path d="m-10 17 2-17h9l5 15-4 4h-7z" fill="#aebdc4" stroke="#526573" stroke-width="1.2"/>',
        '<path d="m-4 14 1-12 2-1 3 13z" fill="#4f626f"/>',
        '<circle r="6" fill="#a7b6be" stroke="#526471" stroke-width="1.1"/><circle r="2.9" fill="#3d5362"/>',
    ]
    dish_track = ""
    if moving:
        keys = [(0, "#dish0")]
        for i in range(1, PHASES + 1):
            keys.append(
                (
                    route.deployment + (route.signal - route.deployment) * i // PHASES,
                    f"#dish{i}",
                )
            )
        dish_track = track(duration, "href", keys)
    parts.append(f'<use data-part="dish" href="#dish0">{dish_track}</use>')
    parts.append(
        '<rect x="-19" y="24" width="25" height="5.1" rx="1.5" fill="#263740"/>'
    )
    for i in range(5):
        x = number(-17 + i * 4.6)
        parts.append(
            f'<rect x="{x}" y="25.1" width="3.3" height="2.8" rx=".55" fill="#526571"/>'
        )
        if moving:
            hit = route.shots[((i + 1) * len(route.shots) - 1) // 5].hit
            glow = track(duration, "opacity", [(0, 0), (hit, 1)])
            parts.append(
                f'<rect x="{x}" y="25.1" width="3.3" height="2.8" rx=".55" fill="#a5e9dc" opacity="0">{glow}</rect>'
            )
    if moving:
        parts.append(
            '<g data-part="transmission" transform="translate(20 -21) rotate(-43)">'
        )
        for i in range(3):
            begin = route.signal + 420 * i
            opacity = track(
                duration,
                "opacity",
                [
                    (0, 0),
                    (begin, 0),
                    (begin + 140, 0.95),
                    (begin + 760, 0.72),
                    (begin + 1210, 0),
                ],
                mode="linear",
            )
            drift = track(
                duration,
                "transform",
                [(0, "0 0"), (begin, "0 0"), (begin + 1210, "27 0")],
                mode="linear",
                transform="translate",
            )
            expand = track(
                duration,
                "transform",
                [(0, ".28"), (begin, ".28"), (begin + 1210, "1.17")],
                mode="linear",
                transform="scale",
            )
            parts.append(
                f'<g opacity="0">{opacity}{drift}<g>{expand}<path class="signal" d="M2 -19 Q16 0 2 19" fill="none" stroke-width="2.8" stroke-linecap="round"/></g></g>'
            )
        parts.append("</g>")
    return "".join(parts) + "</g>"


def pennant(route, moving):
    # A small checkered hoist carries the win state without a dashboard or lettering.
    parts = [
        '<g data-part="flagpole" transform="translate(858 0)">',
        '<ellipse cx="1" cy="187" rx="10" ry="2.7" fill="url(#tire-shadow)"/>',
        '<path d="m-6 183 3-3h7l4 3-2 2H-5z" fill="#627784"/>',
        '<g transform="translate(0 181)"><g transform="scale(1 .28)">',
    ]
    if moving:
        parts.append(
            track(
                route.time,
                "transform",
                [(0, "1 .28"), (route.hoist, "1 .28"), (route.hoist + 690, "1 1")],
                mode="linear",
                transform="scale",
            )
        )
    parts.extend(
        (
            '<path d="M0 0V-90" stroke="#718693" stroke-width="2.6" stroke-linecap="round"/>',
            '<path d="M.7 0V-89" stroke="#b5c5cb" stroke-width=".8"/>',
            '<circle cy="-91" r="2.1" fill="#c9d8d9" stroke="#647783" stroke-width=".7"/></g></g>',
        )
    )
    if moving:
        start = route.hoist
        finish = start + 970
        d = route.time
        opacity = track(
            d, "opacity", [(0, 0), (start, 0), (start + 100, 1)], mode="linear"
        )
        lift = track(
            d,
            "transform",
            [
                (0, "0 164"),
                (start, "0 164"),
                (start + 270, "0 155"),
                (start + 750, "0 100"),
                (finish, "0 92"),
            ],
            mode="linear",
            transform="translate",
        )
        unfurl = track(
            d,
            "transform",
            [
                (0, ".08 .5"),
                (start, ".08 .5"),
                (start + 200, ".34 .72"),
                (start + 680, "1 1"),
                (finish + 220, ".91 .94"),
                (finish + 660, "1 1"),
                (finish + 1100, ".94 .96"),
                (finish + 1600, "1 1"),
            ],
            mode="linear",
            transform="scale",
        )
        parts.extend(
            (
                '<g data-part="victory-flag" transform="translate(0 164)" opacity="0">',
                opacity,
                lift,
                "<g>",
                unfurl,
                '<path d="M1 1c9-5 17 2 25 0l14-2-8 8 7 5c-9 4-18-1-24 .5-6 1-9 2-14 1z" fill="#f0ae43" stroke="#9f6e2a" stroke-width=".8" stroke-linejoin="round"/>',
                '<path d="M1 1c9-5 17 2 25 0l14-2-3 3c-12 3-18 1-25 .2C7 1.7 4 2 1 3z" fill="#ffdb87"/>',
                '<g fill="#3b4650"><path d="M3 1h3v3H3zm3 3h3v3H6zm-3 3h3v3H3zm3 3h3v3H6z"/><path d="m21 3 1.6 3.2 3.6.5-2.6 2.4.6 3.3-3.2-1.6-3.1 1.4.6-3.2-2.4-2.4 3.4-.4z"/></g>',
                "</g></g>",
            )
        )
    return "".join(parts) + "</g>"
