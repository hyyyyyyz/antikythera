"""Side view of a collaborative arm with offset joints and a parallel gripper."""

import math

DURATION = "4.8s"
PICK, DROP = ".23", ".65"
LINK = 65
PARK = (934, 146, 869, 75)
SUPPLY = (855, 115)

# Each casting is drawn in its own joint frame, with its rotation axis at (0, 0).
ART = """
<linearGradient id="shell" x1="0" y1="0" x2=".22" y2="1">
  <stop stop-color="#fff"/><stop offset=".45" stop-color="#e8ecec"/><stop offset="1" stop-color="#9daab0"/>
</linearGradient>
<linearGradient id="rubber" x2=".15" y2="1">
  <stop stop-color="#58616a"/><stop offset=".48" stop-color="#30373f"/><stop offset="1" stop-color="#151b21"/>
</linearGradient>
<g id="upper-shell">
  <path d="M-5-9C0-15 10-14 17-11L41-5Q47-3 52-6L59-9Q64-11 68-5L69 2Q68 8 62 9L51 10Q41 11 32 7L8 5Q-4 7-6 2Z" fill="url(#shell)" stroke="#828f96" stroke-width="1.15"/>
  <path d="M8-10Q12-10 16-8L39-3" fill="none" stroke="#fff" stroke-width="2.1" stroke-linecap="round"/>
  <path d="M18-10 23-9 19 6 15 5Z" fill="#39424a"/><path d="m23-9 2 .5-4 15h-2z" fill="#858f91"/>
  <path d="M34 5Q47 10 57 6" fill="none" stroke="#8a989d" stroke-width="1.4"/>
</g>
<g id="forearm-shell">
  <path d="M-4-6Q1-11 9-10L18-9Q25-9 29-5L37 0Q41 3 46 3L58 0 65-4Q69-5 71-1V5Q64 13 57 14L43 14Q35 14 28 9L17 3 6 4Q-4 6-6 1Z" fill="url(#shell)" stroke="#828f96" stroke-width="1.15"/>
  <path d="M7-7Q19-8 25-4L36 3" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round"/>
  <path d="m42 2 5 .3-1 12-5-.4Z" fill="#35404a"/><path d="m48 2 1.5-.4-1 12.3H47Z" fill="#879397"/>
</g>
<g id="turntable">
  <path d="M-21-4Q-20-8-13-9H12Q20-8 22-4L24 0Q17 5 0 5T-24 0Z" fill="url(#rubber)" stroke="#78838a" stroke-width=".9"/>
  <ellipse cy="-4.5" rx="19.2" ry="4.1" fill="#bcc5c7"/>
  <path d="M-15-7V-15Q-16-24-23-30L-29-36Q-30-42-24-45Q-18-48-13-44L0-34Q10-26 12-17L14-8Q7-4-3-4Z" fill="url(#shell)" stroke="#829197" stroke-width="1.2"/>
  <path d="M-15-12Q-2-8 12-13v5Q-1-4-15-8Z" fill="#323e46"/>
</g>
<g id="rotary">
  <ellipse rx="8" ry="9" fill="#253038" stroke="#97a1a3" stroke-width="1.1"/>
  <ellipse cx="-1.2" cy="-.8" rx="5.6" ry="6.7" fill="#465159"/>
  <path d="M-5-4.8Q-1-8.4 3-4.2" fill="none" stroke="#8b999e" stroke-width="1.1"/>
</g>
"""


def use(name):
    return f'<use href="#{name}" xlink:href="#{name}"/>'


def solve(pose):
    bx, by, tx, ty = pose
    sx, sy = bx-22, by-38
    fx, fy = tx+14, ty-14
    dx, dy = fx-sx, fy-sy
    distance = math.hypot(dx, dy)
    if not 0 < distance <= 2*LINK:
        raise ValueError("Unreachable wrist position")
    h = math.sqrt(LINK**2-(distance/2)**2)
    ex, ey = (sx+fx)/2-dy/distance*h, (sy+fy)/2+dx/distance*h
    return {"base": (bx,by), "shoulder": (sx,sy), "elbow": (ex,ey),
            "flange": (fx,fy), "wrist": (tx,ty),
            "upper": (math.degrees(math.atan2(ey-sy,ex-sx)),),
            "lower": (math.degrees(math.atan2(fy-ey,fx-ex)),)}


def trajectory(target):
    if target is None:
        return [(0,PARK)]
    x,y=target
    # The base slides only far enough for the arm to reach the requested socket.
    base_x=min(PARK[0],x+89)
    lift=(base_x,146,x,y-22)
    place=(base_x,146,x,y-11)
    feed=(*PARK[:2],SUPPLY[0],SUPPLY[1]-11)
    up=(*PARK[:2],SUPPLY[0],SUPPLY[1]-25)
    return [(0,PARK),(.16,feed),(.23,feed),(.31,up),(.50,lift),(.55,lift),
            (.65,place),(.71,place),(.79,lift),(1,PARK)]


def arm(target=None, chip_class="l1"):
    poses=trajectory(target)
    frames=[(0,solve(PARK))]
    for (begin,origin),(end,dest) in zip(poses,poses[1:]):
        steps=6 if origin!=dest else 1
        for i in range(1,steps+1):
            t=i/steps
            blend=t*t*(3-2*t)
            frame=solve([a+(b-a)*blend for a,b in zip(origin,dest)])
            for key in ("upper","lower"):
                previous=frames[-1][1][key][0]
                frame[key]=(previous+(frame[key][0]-previous+180)%360-180,)
            frames.append((begin+(end-begin)*t,frame))

    def transform(key,kind,body):
        def coords(frame):
            return " ".join(f"{v:.2f}" for v in frame[key])
        motion=""
        if target is not None:
            times=";".join(f"{t:.4f}" for t,_ in frames)
            values=";".join(coords(frame) for _,frame in frames)
            motion=(f'<animateTransform attributeName="transform" type="{kind}" dur="{DURATION}" '
                    f'keyTimes="{times}" values="{values}" fill="freeze"/>')
        return f'<g data-joint="{key}" transform="{kind}({coords(frames[0][1])})">{motion}{body}</g>'

    def jaw(side):
        motion=""
        if target is not None:
            close=-side*2
            motion=(f'<animateTransform attributeName="transform" type="translate" dur="{DURATION}" '
                    f'keyTimes="0;.16;{PICK};.6;{DROP};.71;1" values="0 0;0 0;{close} 0;{close} 0;{close} 0;0 0;0 0" fill="freeze"/>')
        return f'<g>{motion}<path d="M{side*8} 1v10l{-side*2} 2" fill="none" stroke="#66737a" stroke-width="2.5" stroke-linejoin="round"/></g>'

    held=""
    if target is not None:
        held=(f'<rect x="-5" y="6" width="10" height="10" rx="2" class="{chip_class}" opacity="0">'
              f'<animate attributeName="opacity" dur="{DURATION}" values="0;1;0;0" keyTimes="0;{PICK};{DROP};1" calcMode="discrete" fill="freeze"/></rect>')
    wrist_shell=('<path d="M15-18Q19-16 17-11l-6 9Q8 2 3 2h-9l-1-5q4-2 5-5l3-8q2-4 7-3Z" fill="url(#shell)" stroke="#89959b" stroke-width="1.2"/>'
                 '<path d="m7-17 6-1 3 1-1.6 4-7 1z" fill="#38434a"/>'
                 '<rect x="-9" y="-3" width="18" height="6" rx="2" fill="url(#rubber)" stroke="#6e7a80" stroke-width=".7"/>')
    return "".join((transform("base","translate",use("turntable")),
                    transform("shoulder","translate",transform("upper","rotate",use("upper-shell"))),
                    transform("elbow","translate",transform("lower","rotate",use("forearm-shell"))),
                    transform("shoulder","translate",use("rotary")),
                    transform("elbow","translate",use("rotary")),
                    transform("flange","translate",'<ellipse rx="5.7" ry="6.8" fill="url(#rubber)" stroke="#aab4b6"/>'),
                    transform("wrist","translate",held+jaw(-1)+jaw(1)+wrist_shell)))
