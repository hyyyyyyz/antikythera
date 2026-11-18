"""Plan the shuttle's reversible collection route and animate its baked 3D poses."""

from dataclasses import dataclass, replace
from datetime import date
from functools import lru_cache
import gzip
import json
from pathlib import Path
from typing import Optional

ASSETS = Path(__file__).resolve().parent / "assets" / "rover"
WIDTH = 978
HEIGHT = 216
LEFT = 14


@lru_cache(maxsize=1)
def rig():
    return json.loads((ASSETS / "poses.json").read_text())


@lru_cache(maxsize=1)
def pose_library():
    with gzip.open(ASSETS / "geometry.json.gz", "rt", encoding="utf-8") as source:
        return json.load(source)


def artwork(frames):
    # A quiet or empty year does not need the full motion library.
    used = (
        {f"a{f.pose}" for f in frames}
        | {f"c{f.wheel}" for f in frames}
        | {f"h{f.jaw}" for f in frames}
    )
    library = pose_library()
    return "\n".join(library[key] for key in sorted(used))


@dataclass(frozen=True)
class Stop:
    day: date
    x: float
    row: int
    count: int
    shade: int


@dataclass(frozen=True)
class Frame:
    ms: int
    x: float
    wheel: int = 0
    pose: int = 0
    jaw: int = 0
    held: Optional[Stop] = None
    cargo: tuple[Stop, ...] = ()


def route_stops(active, limit=6):
    """Sample occupied days across the year, starting with the latest one."""
    if len(active) <= limit:
        return list(reversed(active))
    selected = []
    for i in range(limit):
        section = active[i * len(active) // limit : (i + 1) * len(active) // limit]
        selected.append(
            active[-1]
            if i == limit - 1
            else max(section, key=lambda s: (s.count, s.day))
        )
    return list(reversed(selected))


class Route:
    def __init__(self, stops, model):
        self.model = model
        self.stops = stops
        self.frames = [Frame(0, self.station(stops[0]) if stops else WIDTH - 80)]
        self.distance = 0.0
        if not stops:
            return
        capacity = len(model["slots"])
        self.advance(180)
        for start in range(0, len(stops), capacity):
            batch = stops[start : start + capacity]
            for slot, item in enumerate(batch):
                self.drive(self.station(item))
                self.collect(item, slot)
            # Take the loaded shuttle a little beyond the last stop before
            # returning its cargo. This also gives a one-day calendar a real trip.
            x = self.frames[-1].x
            self.drive(x + (60 if x < WIDTH / 2 else -60))
            self.advance(180)
            for slot in reversed(range(len(batch))):
                item = batch[slot]
                self.drive(self.station(item))
                self.restore(item, slot)
        self.drive(self.frames[0].x)
        self.advance(220)

    def station(self, stop):
        return stop.x - self.model["geometry"]["pick_x"]

    def advance(self, duration, **changes):
        self.frames.append(
            replace(self.frames[-1], ms=self.frames[-1].ms + duration, **changes)
        )

    def handoff(self, **changes):
        self.frames[-1] = replace(self.frames[-1], **changes)

    def drive(self, end):
        start = self.frames[-1].x
        distance = end - start
        if abs(distance) < 0.01:
            return
        duration = round(350 + abs(distance) * 5.5)
        steps = max(2, round(duration / 38))
        for i in range(1, steps + 1):
            t = i / steps
            travel = distance * t * t * (3 - 2 * t)
            # The wheels turn with road distance, including when backing up.
            phase = round(-(self.distance + travel) * self.model["wheel_frames"] / 98)
            dt = i * duration // steps - (i - 1) * duration // steps
            self.advance(
                dt, x=round(start + travel, 3), wheel=phase % self.model["wheel_frames"]
            )
        self.distance += distance

    def reach(self, path, duration, returning=False):
        frames = list(reversed(path)) if returning else path
        steps = len(frames) - 1
        for i, pose in enumerate(frames[1:], 1):
            self.advance(i * duration // steps - (i - 1) * duration // steps, pose=pose)

    def close(self):
        self.advance(80, jaw=1)
        self.advance(80, jaw=2)

    def open(self):
        self.advance(80, jaw=1)
        self.advance(80, jaw=0)

    def collect(self, item, slot):
        cell_path, tray_path = self.model["cells"][item.row], self.model["slots"][slot]
        self.reach(cell_path, 940)
        self.close()
        self.handoff(held=item)
        self.advance(100)
        self.reach(cell_path, 760, returning=True)
        self.reach(tray_path, 420)
        self.handoff(held=None, cargo=self.frames[-1].cargo + (item,))
        self.open()
        self.reach(tray_path, 350, returning=True)

    def restore(self, item, slot):
        cell_path, tray_path = self.model["cells"][item.row], self.model["slots"][slot]
        self.reach(tray_path, 380)
        self.close()
        self.handoff(held=item, cargo=self.frames[-1].cargo[:-1])
        self.reach(tray_path, 390, returning=True)
        self.reach(cell_path, 850)
        self.handoff(held=None)
        self.open()
        self.advance(80)
        self.reach(cell_path, 780, returning=True)


def animate(frames, attribute, value, mode="discrete"):
    """Encode changes only. Linear tracks also need the ends of their holds."""
    values = [value(f) for f in frames]
    keys = [0]
    for i in range(1, len(frames) - 1):
        if values[i] != values[i - 1] or (
            mode == "linear" and values[i] != values[i + 1]
        ):
            keys.append(i)
    if len(keys) == 1 and values[-1] == values[0]:
        return ""
    keys.append(len(frames) - 1)
    duration = frames[-1].ms
    times = ";".join(
        f"{frames[i].ms/duration:.6f}".rstrip("0").rstrip(".") for i in keys
    )
    vals = ";".join(str(values[i]) for i in keys)
    tag = "animateTransform" if attribute == "transform" else "animate"
    kind = ' type="translate"' if tag == "animateTransform" else ""
    return (
        f'<{tag} attributeName="{attribute}"{kind} dur="{duration}ms" repeatCount="indefinite" '
        f'calcMode="{mode}" keyTimes="{times}" values="{vals}"/>'
    )


def xy(point):
    return " ".join(
        f"{coordinate:.3f}".rstrip("0").rstrip(".") or "0" for coordinate in point
    )


def sprite(prefix, field, frames):
    def ref(frame):
        return f"#{prefix}{getattr(frame, field)}"

    return f'<use href="{ref(frames[0])}">{animate(frames,"href",ref)}</use>'


def trolley(route, moving):
    model = route.model
    frames = route.frames if moving else route.frames[:1]
    road = model["geometry"]["road_y"]

    def base(frame):
        return xy((frame.x, road))

    def tool(frame):
        return xy(model["tip"][frame.pose])

    layout = [
        f'<g transform="translate({base(frames[0])})" data-part="shuttle">',
        animate(frames, "transform", base, "linear"),
        '<ellipse cx="-9" cy="5" rx="67" ry="11" fill="url(#tire-shadow)"/>',
        sprite("c", "wheel", frames),
    ]
    if moving:
        for i, item in enumerate(route.stops):
            slot = i % len(model["slots"])
            where = model["tip"][model["slots"][slot][-1]]
            show = animate(
                frames,
                "opacity",
                lambda f: int(len(f.cargo) > slot and f.cargo[slot] == item),
            )
            layout.append(
                f'<g class="l{item.shade}" transform="translate({xy(where)})" opacity="0">{show}<use href="#block"/></g>'
            )
    layout.append(sprite("a", "pose", frames))
    layout += [
        f'<g data-part="pinch" transform="translate({tool(frames[0])})">',
        animate(frames, "transform", tool),
    ]
    if moving:
        for item in route.stops:
            show = animate(frames, "opacity", lambda f: int(f.held == item))
            layout.append(
                f'<g class="l{item.shade}" opacity="0">{show}<use href="#block"/></g>'
            )
    layout.extend((sprite("h", "jaw", frames), "</g></g>"))
    return "".join(layout)
