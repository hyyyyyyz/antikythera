"""SVG geometry for the articulated pick-and-place arm."""

import math

DURATION = "4.8s"
PICK, DROP = ".23", ".65"

METAL = """
<linearGradient id="alloy" x2=".28" y2="1" gradientUnits="objectBoundingBox">
  <stop stop-color="#ffe0a0"/><stop offset=".27" stop-color="#efb76b"/>
  <stop offset=".63" stop-color="#c78842"/><stop offset="1" stop-color="#875132"/>
</linearGradient>
<linearGradient id="ceramic" x2=".2" y2="1">
  <stop stop-color="#fff7d9"/><stop offset=".42" stop-color="#dfd8bd"/>
  <stop offset="1" stop-color="#a19d87"/>
</linearGradient>
<linearGradient id="steel" x2=".3" y2="1">
  <stop stop-color="#a8b3a9"/><stop offset=".38" stop-color="#576765"/>
  <stop offset="1" stop-color="#303b3e"/>
</linearGradient>
<radialGradient id="hub" cx=".33" cy=".27" r=".9">
  <stop stop-color="#a7aea0"/><stop offset=".6" stop-color="#67746b"/><stop offset="1" stop-color="#434d49"/>
</radialGradient>
<g id="bearing"><circle r="12" fill="#1a2222" stroke="#c4ab85" stroke-width=".9"/>
  <circle r="9.6" fill="url(#hub)" stroke="#48524a"/><circle r="6.7" fill="#39413f" stroke="#a6a692" stroke-width=".8"/>
  <path d="M-3.5-1.8 0-3.8l3.5 2v3.6l-3.5 2-3.5-2z" fill="#b6b6a2"/>
  <circle cx="-7" cy="-5" r=".9" fill="#e5d5a9"/><circle cx="7" cy="5" r=".9" fill="#202a27"/></g>
<g id="upper-casting">
  <path d="M-9 4Q-12-10 1-12L54-15Q61-16 68-11L82-7 84 5 62 10 14 12Q2 16-9 4Z" fill="url(#alloy)" stroke="#372f24" stroke-width="2"/>
  <path d="M5-8 54-11 66-8" fill="none" stroke="#ffe8ae" stroke-width="2.2" stroke-linecap="round"/>
  <path d="m18 2 37-5 8 2-9 5-35 4z" fill="#76522e"/><path d="m21 2 32-4" stroke="#ac8055"/>
  <path d="m2 15 16 2 43-7 12 0" fill="none" stroke="#172223" stroke-width="4"/><path d="m2 14 16 2 43-7" fill="none" stroke="#58645c" stroke-width="1.2"/>
  <circle cx="11" cy="-5" r="1.6" fill="#584a38"/><circle cx="64" cy="3" r="1.4" fill="#6f5134"/>
</g>
<g id="forearm-casting">
  <path d="M-6-7 11-11 63-6 84-3 84 5 60 7 13 10-7 7z" fill="url(#ceramic)" stroke="#31372e" stroke-width="1.8"/>
  <path d="M10-7 57-4" stroke="#fff5d8" stroke-width="2"/>
  <path d="m17 1 42 1-7 3-35-1z" fill="#8e917e"/><path d="m65-4 5 .5v7l-5 .2z" fill="#6b756a"/>
  <circle cx="11" cy="3" r="1.4" fill="#687064"/>
</g>
"""


def reference(name):
    return f'<use href="#{name}" xlink:href="#{name}"/>'


def render_arm(poses, scale, chip_color, animate):
    # Frames contain carriage x/y and wrist x/y. Solve the two-link arm for
    # intermediate frames as well, so its castings stay joined in transit.
    length = 84 * scale

    def solve(pose):
        bx, by, tx, ty = pose
        dx, dy = tx - bx, ty - by
        dist = math.hypot(dx, dy)
        if not 0 < dist <= 2 * length:
            raise ValueError("Unreachable wrist position")
        h = math.sqrt(length**2 - (dist/2)**2)
        ex, ey = (bx+tx)/2 - dy/dist*h, (by+ty)/2 + dx/dist*h
        return {"base": (bx, by), "elbow": (ex, ey), "wrist": (tx, ty),
                "upper": (math.degrees(math.atan2(ey-by, ex-bx)),),
                "lower": (math.degrees(math.atan2(ty-ey, tx-ex)),)}

    frames = [(0, solve(poses[0][1]))]
    if animate:
        for (begin, origin), (end, target) in zip(poses, poses[1:]):
            steps = 6 if origin != target else 1
            for i in range(1, steps+1):
                t = i/steps
                blend = t*t*(3-2*t)
                position = [a+(b-a)*blend for a,b in zip(origin,target)]
                frame = solve(position)
                # Avoid rotating the long way round across atan2's 180° seam.
                for key in ("upper", "lower"):
                    previous = frames[-1][1][key][0]
                    angle = previous + (frame[key][0]-previous+180) % 360 - 180
                    frame[key] = (angle,)
                frames.append((begin+(end-begin)*t, frame))

    def number(values):
        return " ".join(f"{v:.2f}" for v in values)

    def transform(key, kind, body):
        initial = number(frames[0][1][key])
        motion = ""
        if animate:
            times = ";".join(f"{t:.4f}" for t,_ in frames)
            values = ";".join(number(frame[key]) for _,frame in frames)
            motion = (f'<animateTransform attributeName="transform" type="{kind}" dur="{DURATION}" '
                      f'keyTimes="{times}" values="{values}" fill="freeze"/>')
        return f'<g data-joint="{key}" transform="{kind}({initial})">{motion}{body}</g>'

    def scaled(body):
        return f'<g transform="scale({scale})">{body}</g>'

    def link(origin, rotation, name):
        return transform(origin, "translate", transform(rotation, "rotate", scaled(reference(name))))

    def jaw(side):
        motion = ""
        if animate:
            motion = (f'<animateTransform attributeName="transform" type="translate" dur="{DURATION}" '
                      f'keyTimes="0;.15;{PICK};.60;{DROP};.71;1" '
                      f'values="0 0;0 0;{-side*2} 0;{-side*2} 0;{-side*2} 0;0 0;0 0" fill="freeze"/>')
        return f'<g>{motion}<path d="M{side*7} 3v7l{-side*1.6} 2" fill="none" stroke="#e0e5d2" stroke-linejoin="round" stroke-width="2.4"/></g>'

    carried = ""
    if animate:
        carried = (f'<rect x="-4" y="6" width="8" height="8" rx="1.2" fill="{chip_color}" opacity="0">'
                   f'<animate attributeName="opacity" dur="{DURATION}" values="0;1;0;0" keyTimes="0;{PICK};{DROP};1" calcMode="discrete" fill="freeze"/></rect>')
    base = ('<path d="M-24 4-20-3h40l5 7v5h-49z" fill="url(#steel)" stroke="#171e1c" stroke-width="2"/>'
            '<rect x="-17" y="-10" width="33" height="13" rx="4" fill="url(#ceramic)" stroke="#454a40"/>'
            '<path d="M-19 6h36" stroke="#c2c6ad" stroke-width="1.5"/>')
    wrist = ('<rect x="-8" y="-6" width="16" height="10" rx="2.5" fill="url(#steel)" stroke="#29332f"/>'
             '<circle cy="-2" r="3.2" fill="#d8c9a5"/><circle cy="-2" r="1.4" fill="#4d574c"/>')
    return "".join((transform("base","translate",scaled(base)), link("base","upper","upper-casting"),
                    link("elbow","lower","forearm-casting"),
                    transform("base","translate",scaled(reference("bearing"))),
                    transform("elbow","translate",scaled(reference("bearing"))),
                    transform("wrist","translate",scaled(carried + jaw(-1) + jaw(1) + wrist))))
