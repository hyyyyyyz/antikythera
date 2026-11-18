"""Faceted display plinth for the orthographic Panda illustration."""

from math import cos, pi, sin
from xml.etree.ElementTree import SubElement

MOUNT = (-0.12, 0, 0.29)


def values(items):
    return " ".join(f"{value:.7g}" for value in items)


def add_plinth(root):
    assets, world = root.find("asset"), root.find("worldbody")
    for name, rgba in (
        ("graphite", (0.16, 0.20, 0.23, 1)),
        ("slate", (0.31, 0.38, 0.42, 1)),
        ("machined", (0.61, 0.67, 0.69, 1)),
        ("brass", (0.76, 0.60, 0.37, 1)),
    ):
        SubElement(
            assets,
            "material",
            name=name,
            rgba=values(rgba),
            specular=".36",
            shininess=".38",
        )

    def layer(name, material, rings, sides=12):
        # Loft horizontal polygons. Broad faces catch the same studio light as the arm.
        vertices = []
        faces = []
        for z, radius in rings:
            for i in range(sides):
                angle = 2 * pi * (i + 0.5) / sides
                vertices.extend((radius * cos(angle), radius * sin(angle), z))
        for row in range(len(rings) - 1):
            for i in range(sides):
                a = row * sides + i
                b = row * sides + (i + 1) % sides
                faces.extend((a, b, b + sides, a, b + sides, a + sides))
        top = (len(rings) - 1) * sides
        for i in range(1, sides - 1):
            faces.extend((0, i + 1, i, top, top + i, top + i + 1))
        SubElement(
            assets,
            "mesh",
            name=name,
            vertex=values(vertices),
            face=" ".join(map(str, faces)),
        )
        SubElement(
            world,
            "geom",
            type="mesh",
            mesh=name,
            material=material,
            pos=values((*MOUNT[:2], 0)),
            group="1",
            contype="0",
            conaffinity="0",
        )

    layer(
        "plinth_foot",
        "graphite",
        [(0.060, 0.235), (0.066, 0.263), (0.085, 0.263), (0.093, 0.250)],
    )
    layer(
        "plinth_casting",
        "slate",
        [(0.088, 0.247), (0.103, 0.249), (0.190, 0.205), (0.207, 0.192)],
    )
    layer("plinth_inlay", "brass", [(0.207, 0.191), (0.214, 0.187)])
    layer("plinth_cap", "graphite", [(0.213, 0.187), (0.225, 0.186), (0.239, 0.163)])
    layer(
        "plinth_collar",
        "machined",
        [(0.237, 0.146), (0.249, 0.148), (0.284, 0.126), (0.29, 0.126)],
        32,
    )
