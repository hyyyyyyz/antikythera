"""Encode lit mesh renders as native SVG paint layers usable on GitHub raw."""

import cv2
import numpy as np


def contours(mask):
    lines, _ = cv2.findContours(
        mask.astype("uint8"), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    commands = []
    for line in lines:
        if cv2.contourArea(line) < 3:
            continue
        points = cv2.approxPolyDP(line, 0.85, True)[:, 0]
        if len(points) < 3:
            continue
        first = f"M{points[0,0]} {points[0,1]}l"
        steps = " ".join(f"{x} {y}" for x, y in np.diff(points, axis=0))
        commands.append(first + steps.replace(" -", "-") + "z")
    return "".join(commands)


def paint(image, enamel=False):
    rgba = np.asarray(image)
    rgb = rgba[:, :, :3].astype("float32")
    opaque = rgba[:, :, 3] >= 128
    luminance = rgb @ np.array([0.26, 0.56, 0.18], dtype="float32")
    warm = (rgb[:, :, 0] - rgb[:, :, 2] > 21) & (rgb[:, :, 0] > rgb[:, :, 1])
    families = [opaque & ~warm, opaque & warm] if enamel else [opaque]
    layers = []
    for family in families:
        if not np.any(family):
            continue
        for low in range(0, 256, 12):
            samples = rgb[family & (luminance >= low) & (luminance < low + 12)]
            if not len(samples):
                continue
            path = contours(family & (luminance >= low))
            if path:
                color = "#%02x%02x%02x" % tuple(
                    samples.mean(axis=0).round().astype(int)
                )
                layers.append(f'<path fill="{color}" fill-rule="evenodd" d="{path}"/>')
    return "".join(layers)


def symbols(frames, anchor, density, prefix):
    boxes = [image.getbbox() for image in frames]
    left, top = min(b[0] for b in boxes) - 2, min(b[1] for b in boxes) - 2
    right, bottom = max(b[2] for b in boxes) + 2, max(b[3] for b in boxes) + 2
    if min(left, top) < 0 or right > frames[0].width or bottom > frames[0].height:
        raise ValueError(f"Studio camera clips the {prefix} poses")
    transform = f"translate({left/density-anchor[0]:.3f} {top/density-anchor[1]:.3f}) scale({1/density})"
    result = {}
    for i, image in enumerate(frames):
        layer = paint(image.crop((left, top, right, bottom)), enamel=prefix == "c")
        key = f"{prefix}{i}"
        result[key] = f'<g id="{key}" transform="{transform}">{layer}</g>'
    return result
