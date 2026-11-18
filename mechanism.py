"""A repeating sequence of poses and light pulses on a two-dimensional calendar."""

from dataclasses import dataclass
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from math import atan2, cos, degrees, radians, sin
from random import Random
from datetime import date

from artwork import ASSETS

WIDTH, HEIGHT = 1010, 163
LEFT, TOP, PITCH, CELL = 14, 28, 15, 11.5
STATION_X, STATION_Y, SCALE = 917, 153, 0.9
REST_POSE = 4


@lru_cache(maxsize=1)
def rig():
    with (ASSETS / "panda" / "poses.json").open() as source:
        return json.load(source)["tip"]


@lru_cache(maxsize=1)
def pose_library():
    with gzip.open(
        ASSETS / "panda" / "geometry.json.gz", "rt", encoding="utf-8"
    ) as source:
        return json.load(source)


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
    pose: int
    angle: float


@dataclass(frozen=True)
class Shot:
    tile: Stop
    muzzle: tuple
    target: tuple
    fired: int
    hit: int


def calendar_seed(username, end, active):
    records = ",".join(str(d.day) for d in active)
    return sha256(f"{username.lower()}/{end}/{records}".encode()).digest()


def screen_grip(tip):
    return STATION_X + tip[0] * SCALE, STATION_Y + tip[1] * SCALE


def screen_flash(grip, offset, angle):
    a = radians(angle)
    dx, dy = offset
    return (
        grip[0] + SCALE * (dx * cos(a) - dy * sin(a)),
        grip[1] + SCALE * (dx * sin(a) + dy * cos(a)),
    )


class Mission:
    def __init__(self, active, tips, plate, seed):
        self.tips = tips
        self.frames = [Frame(0, REST_POSE, -2)]
        self.shots = []
        self.hoist = 0
        if not active:
            return
        order = list(active)
        Random(seed).shuffle(order)
        offset = plate.pulse_offset
        self.move(550, REST_POSE, -2)
        for tile in order:
            target = (tile.x, TOP + tile.row * PITCH + CELL / 2)
            pose = round(tile.row * (len(tips) - 1) / 6)
            grip = screen_grip(tips[pose])
            # The plate faces left in its native image coordinates.
            angle = round(
                degrees(
                    atan2(grip[1] + SCALE * offset[1] - target[1], grip[0] - target[0])
                ),
                3,
            )
            prev = self.frames[-1]
            beat = max(
                58 if len(active) > 36 else 200,
                7 * abs(pose - prev.pose),
                round(1.8 * abs(angle - prev.angle)),
            )
            self.move(beat, pose, angle)
            start = self.time
            self.shots.append(
                Shot(tile, screen_flash(grip, offset, angle), target, start, start + 50)
            )
            self.move(75, pose, angle)
        self.hoist = self.shots[-1].hit + 140
        self.move(390, REST_POSE, -2)
        self.move(self.hoist + 3100 - self.time, REST_POSE, -2)

    @property
    def time(self):
        return self.frames[-1].ms

    def move(self, duration, pose, angle):
        start = self.frames[-1]
        same = (start.pose, start.angle) == (pose, angle)
        steps = 1 if same else max(2, round(duration / 25))
        for i in range(1, steps + 1):
            t = i / steps
            u = t * t * (3 - 2 * t)
            self.frames.append(
                Frame(
                    start.ms + i * duration // steps,
                    round(start.pose + (pose - start.pose) * u),
                    round(start.angle + (angle - start.angle) * u, 3),
                )
            )


def artwork(frames):
    library = pose_library()
    keys = {"h0", "finger0", "plinth0"} | {f"a{f.pose}" for f in frames}
    return "\n".join(library[k] for k in sorted(keys))
