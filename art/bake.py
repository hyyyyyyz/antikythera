"""Bake the 3D geometry once. The GitHub Action only reads the resulting atlases."""

import argparse
import gzip
import json
from math import pi, sin
from pathlib import Path

import numpy as np
from outlines import symbols

from studio import DENSITY, LOW, ORIGIN, READY, Studio, project


def bake(source, output):
    studio = Studio(source)
    output.mkdir(parents=True, exist_ok=True)
    try:
        seed = studio.rest
        arms = []
        tips = []
        # A single studio gesture supplies eleven illustrated wrist heights.
        for i in range(11):
            u = i / 10
            t = u * u * (3 - 2 * u)
            point = (
                (1 - t) * READY
                + t * LOW
                + np.array([0.014, 0.025, 0.025]) * sin(pi * t)
            )
            seed = studio.pose(point, seed)
            studio.set_joints(seed)
            tip = project(studio.data.site_xpos[studio.site])
            if np.linalg.norm(tip - project(point)) > 0.18:
                raise ValueError("Wrist projection misses its illustration anchor")
            tips.append(tip.round(3).tolist())
            arms.append(studio.image(2))
            if i == 0:
                hand = studio.image(4)
                finger = studio.image(5)
                plinth = studio.image(1)
        artwork = symbols(arms, ORIGIN, DENSITY, "a")
        artwork.update(symbols([hand], ORIGIN + tips[0], DENSITY, "h"))
        artwork.update(symbols([finger], ORIGIN + tips[0], DENSITY, "finger"))
        artwork.update(symbols([plinth], ORIGIN, DENSITY, "plinth"))
        encoded = json.dumps(artwork, separators=(",", ":")).encode()
        (output / "geometry.json.gz").write_bytes(gzip.compress(encoded, mtime=0))
        (output / "poses.json").write_text(
            json.dumps({"tip": tips}, separators=(",", ":")) + "\n"
        )
        print(
            f"Baked {len(arms)} arm poses, a closed gripper and one stationary plinth."
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
        default=Path(__file__).resolve().parents[1] / "assets" / "panda",
    )
    args = parser.parse_args()
    bake(args.model, args.output)
