"""Read flat, path-only illustrations for the wrist, with anchors in image pixels."""

from dataclasses import dataclass
from functools import lru_cache
from html import escape
from math import isfinite
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from motion import number, xy

ASSETS = Path(__file__).resolve().parent / "assets"
SVG = "{http://www.w3.org/2000/svg}"


@dataclass(frozen=True)
class Plate:
    title: str
    credit: str
    scale: float
    grip: tuple
    flash: tuple
    paths: str

    @property
    def pulse_offset(self):
        return tuple((p - g) * self.scale for p, g in zip(self.flash, self.grip))

    def symbol(self):
        offset = xy((-self.grip[0], -self.grip[1]))
        return (
            f'<g id="prop-art"><title>{escape(self.title)}</title>'
            f'<g transform="scale({number(self.scale)}) translate({offset})">{self.paths}</g></g>'
        )


@lru_cache(maxsize=8)
def read_plate(path):
    try:
        root = ET.fromstring(Path(path).read_bytes())
    except ET.ParseError as error:
        raise ValueError(f"Invalid SVG in {path}: {error}") from error
    if root.tag != SVG + "svg":
        raise ValueError(f"Expected an SVG illustration in {path}")

    def vector(name, length):
        values = tuple(map(float, root.get(name, "").split()))
        if len(values) != length or not all(isfinite(v) for v in values):
            raise ValueError(f"Invalid {name} in {path}")
        return values

    _, _, width, height = vector("viewBox", 4)
    (span,) = vector("data-span", 1)
    if min(width, height, span) <= 0:
        raise ValueError("Artwork must have positive dimensions")
    paths = []
    for node in root.findall(SVG + "path"):
        fill = node.get("fill", "")
        if not re.fullmatch(r"#[a-fA-F0-9]{6}", fill):
            raise ValueError("Artwork paths need six-digit hex colors")
        placement = ""
        if "transform" in node.attrib:
            move = node.attrib["transform"]
            if not re.fullmatch(r"translate\(\s*-?[0-9.]+[ ,]+-?[0-9.]+\s*\)", move):
                raise ValueError("Artwork paths support translation only")
            placement = f' transform="{move}"'
        paths.append(
            f'<path fill="{fill}"{placement} d="{escape(node.attrib["d"], quote=True)}"/>'
        )
    if not paths:
        raise ValueError("Artwork needs at least one filled SVG path")
    return Plate(
        root.findtext(SVG + "title", "Studio light"),
        root.findtext(SVG + "metadata", ""),
        span / width,
        vector("data-grip", 2),
        vector("data-pulse", 2),
        "".join(paths),
    )


def studio_plate():
    return read_plate(ASSETS / "studio.svg")
