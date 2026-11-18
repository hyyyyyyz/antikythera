"""Choreograph a single-arm arcade mission in the calendar's SVG coordinates."""

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from math import atan2, degrees, hypot
from pathlib import Path
from random import Random

ASSETS = Path(__file__).resolve().parent / "assets" / "rover"
WIDTH, HEIGHT, LEFT, DOCK = 978, 216, 14, 777
BARREL = 36  # Distance in illustration pixels from the grip to the luminous ring.


@lru_cache(maxsize=1)
def rig():
    return json.loads((ASSETS / "poses.json").read_text())


@lru_cache(maxsize=1)
def pose_library():
    with gzip.open(ASSETS / "geometry.json.gz", "rt", encoding="utf-8") as source:
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
    x: float
    wheel: int
    pose: int
    angle: float


@dataclass(frozen=True)
class Shot:
    tile: Stop
    muzzle: tuple[float, float]
    target: tuple[float, float]
    fired: int
    hit: int


def ease(t):
    return t * t * (3 - 2 * t)


def calendar_seed(username, end, active):
    records = ",".join(str(d.day) for d in active)
    return sha256(f"{username.lower()}/{end}/{records}".encode()).digest()


class Route:
    def __init__(self, active, model, seed):
        self.model = model
        self.stance = model["slots"][0]
        self.frames = [Frame(0, DOCK, 0, self.stance[9], -133)]
        self.shots = []
        self.deployment = self.signal = self.hoist = 0
        if not active:
            return
        rng = Random(seed)
        remaining = list(active)
        count = len(remaining)
        burst_x = 0
        burst_left = 0
        geom = model["geometry"]
        centers_y = [
            geom["top"] + row * geom["pitch"] + geom["size"] / 2 for row in range(7)
        ]
        poses = [self.stance[2 + round(row * 8 / 6)] for row in range(7)]

        def eligible(cart):
            result = []
            for tile in remaining:
                px, py = model["tip"][poses[tile.row]]
                gap = hypot(
                    tile.x - cart - px, centers_y[tile.row] - geom["road_y"] - py
                )
                if gap >= BARREL + 16:
                    result.append(tile)
            return result

        self.move(270, DOCK, self.stance[9], -133)
        for index in range(count):
            # The whole year gets one out-and-back sweep while the light head follows each burst.
            t = index / max(1, count - 1)
            x = 109 + (DOCK - 109) * ease(abs(1 - 2 * t))
            choices = eligible(x)
            if not choices:
                # A sparse year's last tile can sit directly over the prop. Roll clear first.
                tile = remaining[0]
                x = max(
                    109, min(847, tile.x + 143 if tile.x < WIDTH / 2 else tile.x - 111)
                )
                choices = eligible(x)
            start_burst = burst_left == 0
            if start_burst:
                burst_left = rng.randint(3, 7)
            else:
                nearby = [tile for tile in choices if abs(tile.x - burst_x) <= 60]
                if nearby:
                    choices = nearby
            tile = rng.choice(choices)
            remaining.remove(tile)
            burst_x = tile.x if start_burst else burst_x
            burst_left -= 1
            x = round(x, 3)
            target = (tile.x, centers_y[tile.row])
            pose = poses[tile.row]
            tip = model["tip"][pose]
            y = geom["road_y"] + tip[1]
            dx, dy = target[0] - x - tip[0], target[1] - y
            distance = hypot(dx, dy)
            angle = round(degrees(atan2(dy, dx)), 4)
            last = self.frames[-1]
            # Long pans get a readable beat. In a busy year adjacent shots are short.
            slew = max(
                48 if count > 36 else 155,
                round(abs(last.angle - angle) * 0.62),
                round(abs(x - last.x) * 2.15),
                12 * abs(self.stance.index(last.pose) - self.stance.index(pose)),
            )
            if start_burst:
                slew += 58
            self.move(slew, x, pose, angle)
            muzzle = (x + tip[0] + dx * BARREL / distance, y + dy * BARREL / distance)
            fire = self.time
            self.shots.append(Shot(tile, muzzle, target, fire, fire + 43))
            self.move(61, x, pose, angle)
        self.move(
            max(390, round(abs(self.frames[-1].x - DOCK) * 3)),
            DOCK,
            self.stance[9],
            -128,
        )
        self.deployment = self.time + 170
        self.signal = self.deployment + 1050
        self.hoist = self.signal + 740
        self.move(self.hoist + 3450 - self.time, DOCK, self.stance[9], -128)

    @property
    def time(self):
        return self.frames[-1].ms

    def move(self, duration, x, pose, angle):
        start = self.frames[-1]
        if (start.x, start.pose, start.angle) == (x, pose, angle):
            self.frames.append(Frame(start.ms + duration, x, start.wheel, pose, angle))
            return
        steps = max(2, round(duration / 33))
        first, last = self.stance.index(start.pose), self.stance.index(pose)
        for i in range(1, steps + 1):
            u = ease(i / steps)
            cart = round(start.x + (x - start.x) * u, 3)
            wrist = self.stance[round(first + (last - first) * u)]
            direction = round(start.angle + (angle - start.angle) * u, 4)
            wheel = (
                round((DOCK - cart) * self.model["wheel_frames"] / 98)
                % self.model["wheel_frames"]
            )
            self.frames.append(
                Frame(start.ms + i * duration // steps, cart, wheel, wrist, direction)
            )


def artwork(frames):
    used = {f"a{f.pose}" for f in frames} | {f"c{f.wheel}" for f in frames} | {"h2"}
    library = pose_library()
    return "\n".join(library[key] for key in sorted(used))
