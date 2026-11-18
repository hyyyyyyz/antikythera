"""Procedural geometry for the original four-wheel shuttle and its cargo tray."""

from math import cos, pi, sin
from xml.etree.ElementTree import SubElement


def values(items):
    return " ".join(f"{v:.7g}" for v in items)


def material(asset, name, color, specular=0.28, shininess=0.34):
    SubElement(
        asset,
        "material",
        name=name,
        rgba=values((*color, 1)),
        specular=str(specular),
        shininess=str(shininess),
    )


def hull(asset, name, length, width, radius, levels):
    """Loft a rounded rectangular section to give cast bodywork bevelled edges."""
    perimeter = []
    for i, (cx, cy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        for j in range(6):
            angle = (i + j / 5) * pi / 2
            perimeter.append(
                (
                    cx * (length / 2 - radius) + radius * cos(angle),
                    cy * (width / 2 - radius) + radius * sin(angle),
                )
            )
    ring = len(perimeter)
    verts = [(x * scale, y * scale, z) for z, scale in levels for x, y in perimeter]
    faces = []
    for layer in range(len(levels) - 1):
        for i in range(ring):
            a = layer * ring + i
            b = layer * ring + (i + 1) % ring
            faces.extend(((a, b, b + ring), (a, b + ring, a + ring)))
    top = (len(levels) - 1) * ring
    for i in range(1, ring - 1):
        faces.extend(((0, i + 1, i), (top, top + i, top + i + 1)))
    SubElement(
        asset,
        "mesh",
        name=name,
        vertex=values(v for p in verts for v in p),
        face=values(v for f in faces for v in f),
    )


def add_shuttle(root):
    asset, world = root.find("asset"), root.find("worldbody")
    material(asset, "enamel", (0.94, 0.64, 0.13))
    material(asset, "trim", (0.10, 0.14, 0.17))
    material(asset, "tire", (0.105, 0.116, 0.13), 0.12, 0.12)
    material(asset, "silver", (0.57, 0.63, 0.66), 0.5)
    material(asset, "glass", (0.085, 0.135, 0.17), 0.63)
    material(asset, "lamp", (0.94, 0.91, 0.68))
    hull(
        asset,
        "bus_body",
        0.77,
        0.405,
        0.052,
        [(-0.063, 0.96), (-0.045, 1), (0.044, 1), (0.066, 0.92)],
    )
    hull(
        asset,
        "bus_bumper",
        0.79,
        0.421,
        0.052,
        [(-0.015, 0.95), (-0.008, 1), (0.008, 1), (0.015, 0.98)],
    )
    hull(
        asset,
        "bus_deck",
        0.68,
        0.352,
        0.038,
        [(-0.011, 0.97), (-0.006, 1), (0.006, 1), (0.011, 0.97)],
    )

    def geom(parent, kind, pos, mat, size=None, **attrs):
        if size:
            attrs["size"] = values(size)
        return SubElement(
            parent,
            "geom",
            type=kind,
            pos=values(pos),
            material=mat,
            group="1",
            contype="0",
            conaffinity="0",
            **attrs,
        )

    geom(world, "mesh", (0.065, 0, 0.188), "enamel", mesh="bus_body")
    geom(world, "mesh", (0.065, 0, 0.121), "trim", mesh="bus_bumper")
    geom(world, "mesh", (0.065, 0, 0.259), "trim", mesh="bus_deck")
    geom(world, "cylinder", (-0.12, 0, 0.277), "silver", (0.098, 0.01))
    # Dark inset side panels and a slim yellow sill echo a small shuttle bus.
    for sign in (-1, 1):
        for x in (-0.12, 0.042, 0.204):
            geom(world, "box", (x, sign * 0.200, 0.203), "glass", (0.069, 0.003, 0.022))
        geom(world, "box", (0.044, sign * 0.203, 0.166), "trim", (0.217, 0.003, 0.004))
        for x in (-0.26, 0.37):
            geom(
                world, "sphere", (x, sign * 0.173, 0.238), "lamp", (0.014, 0.011, 0.008)
            )
    # Low-sided tray in front of the bolted robot pedestal.
    geom(world, "box", (0.275, 0, 0.276), "silver", (0.103, 0.106, 0.006))
    for sign in (-1, 1):
        geom(world, "box", (0.275, sign * 0.102, 0.291), "trim", (0.107, 0.007, 0.013))
    geom(world, "box", (0.38, 0, 0.289), "trim", (0.007, 0.107, 0.011))

    for x in (-0.195, 0.335):
        for sign in (-1, 1):
            wheel = SubElement(
                world,
                "body",
                name=f"wheel_{x}_{sign}",
                mocap="true",
                pos=values((x, sign * 0.202, 0.096)),
            )
            axis = {"quat": ".7071068 .7071068 0 0"}
            geom(wheel, "cylinder", (0, 0, 0), "tire", (0.097, 0.033), **axis)
            geom(
                wheel, "cylinder", (0, sign * 0.032, 0), "trim", (0.072, 0.006), **axis
            )
            geom(
                wheel,
                "cylinder",
                (0, sign * 0.040, 0),
                "silver",
                (0.049, 0.003),
                **axis,
            )
            geom(
                wheel, "cylinder", (0, sign * 0.044, 0), "trim", (0.024, 0.003), **axis
            )
            for i in range(5):
                a = 2 * pi * i / 5
                geom(
                    wheel,
                    "sphere",
                    (0.035 * cos(a), sign * 0.045, 0.035 * sin(a)),
                    "trim",
                    (0.006, 0.003, 0.006),
                )
            # A small sidewall mark makes wheel rotation readable at profile size.
            geom(
                wheel,
                "box",
                (0.073, sign * 0.034, 0),
                "silver",
                (0.008, 0.0018, 0.0038),
            )
