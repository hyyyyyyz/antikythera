"""Bake the 3D geometry once. The GitHub Action only reads the resulting atlases."""

import argparse
import gzip
import json
from math import pi, sin
from pathlib import Path

import numpy as np
from outlines import symbols

from studio import (
    DENSITY,
    LAYER,
    ORIGIN,
    PICK_X,
    PITCH,
    RACK,
    READY,
    ROAD_Y,
    SQUARE,
    TOP,
    Studio,
    project,
    row_target,
)

WHEEL_FRAMES = 16
CAPACITY = 3


def bake(source, output):
    studio = Studio(source)
    output.mkdir(parents=True, exist_ok=True)
    try:
        rest = studio.pose(READY, studio.rest)
        studio.set_joints(rest)
        arms = [studio.image(2)]
        tips = [project(READY).round(3).tolist()]

        def path_to(goal, frames, arch):
            indexes = [0]
            seed = rest
            for i in range(1, frames + 1):
                u = i / frames
                # Ease into each contact and approach from just above the payload.
                t = u * u * (3 - 2 * u)
                point = (1 - t) * READY + t * goal + arch * sin(pi * t)
                seed = studio.pose(point, seed)
                studio.set_joints(seed)
                indexes.append(len(arms))
                arms.append(studio.image(2))
                tip = project(studio.data.site_xpos[studio.site])
                if np.linalg.norm(tip - project(point)) > 0.18:
                    raise ValueError("tool center misses its baked trajectory")
                tips.append(tip.round(3).tolist())
            return indexes

        cells = [
            path_to(row_target(i), 18, np.array([-0.012, 0.035, 0.04]))
            for i in range(7)
        ]
        slots = [
            path_to(RACK + [0, 0, i * LAYER], 10, np.array([0.014, 0.025, 0.025]))
            for i in range(CAPACITY)
        ]
        carts = []
        for i in range(WHEEL_FRAMES):
            studio.set_joints(rest, wheel=2 * pi * i / WHEEL_FRAMES)
            carts.append(studio.image(1))
        hands = []
        for width in (0.04, 0.034, 0.027):
            studio.set_joints(rest, jaw=width)
            hands.append(studio.image(4))
        artwork = symbols(arms, ORIGIN, DENSITY, "a")
        artwork.update(symbols(carts, ORIGIN, DENSITY, "c"))
        artwork.update(symbols(hands, ORIGIN + project(READY), DENSITY, "h"))
        encoded = json.dumps(artwork, separators=(",", ":")).encode()
        (output / "geometry.json.gz").write_bytes(gzip.compress(encoded, mtime=0))
        metadata = {
            "wheel_frames": len(carts),
            "tip": tips,
            "cells": cells,
            "slots": slots,
            "geometry": {
                "road_y": ROAD_Y,
                "top": TOP,
                "pitch": PITCH,
                "size": SQUARE,
                "pick_x": PICK_X,
            },
        }
        (output / "poses.json").write_text(
            json.dumps(metadata, separators=(",", ":")) + "\n"
        )
        print(
            f"Baked {len(arms)} Panda poses, {len(hands)} gripper states and {len(carts)} wheel phases."
        )
    finally:
        studio.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "model", type=Path, help="Path to the pinned franka_emika_panda directory"
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "assets" / "rover",
    )
    args = parser.parse_args()
    bake(args.model, args.output)
