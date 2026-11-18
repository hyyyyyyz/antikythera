"""Offline orthographic studio for the Panda; unused by the daily Action."""

from pathlib import Path
from xml.etree import ElementTree as ET

import mujoco
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

from plinth import MOUNT, add_plinth, values

# Display units, before 2x rasterization. The arm and plinth share one projection origin.
SIZE = (236, 236)
ORIGIN = np.array([151.0, 214.0])
DENSITY = 2
PPM = 168.0
LOW = np.array([0.275, 0.018, 0.319])
READY = np.array([0.26, 0.015, 0.60])


def unit(v):
    return np.array(v) / np.linalg.norm(v)


CAM_Z = unit((0.28, 0.94, 0.255))
RIGHT = unit(np.cross([0, 0, 1], CAM_Z))
UP = unit(np.cross(CAM_Z, RIGHT))
# The jaws point forward and slightly down. Their opening is visible in profile.
FORWARD = unit((0.76, -0.26, -0.59))
JAW = -unit(RIGHT - np.dot(RIGHT, FORWARD) * FORWARD)
HAND = np.column_stack((np.cross(JAW, FORWARD), JAW, FORWARD))


def project(point):
    return np.array([RIGHT @ point, -UP @ point]) * PPM


class Studio:
    def __init__(self, folder):
        folder = Path(folder).resolve()
        tree = ET.parse(folder / "panda.xml")
        root = tree.getroot()
        root.find("compiler").set("meshdir", str(folder / "assets"))
        root.find(".//body[@name='link0']").set("pos", values(MOUNT))
        for name in ("hand", "left_finger", "right_finger"):
            for geom in root.find(f".//body[@name='{name}']").findall(
                "geom[@class='visual']"
            ):
                geom.set("group", "5" if name == "left_finger" else "4")
        hand = root.find(".//body[@name='hand']")
        ET.SubElement(
            hand, "site", name="pinch", pos="0 0 .1034", size=".002", rgba="0 0 0 0"
        )
        root.find("./asset/material[@name='black']").set("rgba", ".13 .15 .17 1")
        add_plinth(root)
        world = root.find("worldbody")
        center = RIGHT * ((SIZE[0] / 2 - ORIGIN[0]) / PPM) + UP * (
            (ORIGIN[1] - SIZE[1] / 2) / PPM
        )
        ET.SubElement(
            world,
            "camera",
            name="studio",
            pos=values(center + 4 * CAM_Z),
            xyaxes=values((*RIGHT, *UP)),
            orthographic="true",
            fovy=str(SIZE[1] / PPM),
        )
        for pos, brightness, shadow in [
            ((1.4, 1.9, 3), (0.55, 0.55, 0.54), "true"),
            ((-1.8, 0.5, 1.6), (0.24, 0.25, 0.27), "false"),
            ((-0.7, -1.8, 2.1), (0.28, 0.30, 0.33), "false"),
        ]:
            ET.SubElement(
                world,
                "light",
                pos=values(pos),
                dir=values(-unit(pos)),
                directional="true",
                diffuse=values(brightness),
                specular=".17 .17 .17",
                castshadow=shadow,
            )
        visual = ET.SubElement(root, "visual")
        ET.SubElement(
            visual,
            "global",
            offwidth=str(SIZE[0] * DENSITY),
            offheight=str(SIZE[1] * DENSITY),
        )
        ET.SubElement(visual, "quality", offsamples="4", shadowsize="2048")
        ET.SubElement(
            visual,
            "headlight",
            ambient=".29 .30 .31",
            diffuse=".13 .13 .13",
            specular=".04 .04 .04",
        )
        self.model = mujoco.MjModel.from_xml_string(
            ET.tostring(root, encoding="unicode")
        )
        self.data = mujoco.MjData(self.model)
        mujoco.mj_resetDataKeyframe(self.model, self.data, 0)
        mujoco.mj_forward(self.model, self.data)
        self.site = self.model.site("pinch").id
        self.rest = self.data.qpos[:7].copy()
        self.renderer = mujoco.Renderer(
            self.model, height=SIZE[1] * DENSITY, width=SIZE[0] * DENSITY
        )

    def pose(self, target, seed):
        m, d = self.model, self.data

        def residual(q):
            d.qpos[:7] = q
            mujoco.mj_kinematics(m, d)
            rot = d.site_xmat[self.site].reshape(3, 3)
            error = Rotation.from_matrix(HAND.T @ rot).as_rotvec()
            return np.r_[
                d.site_xpos[self.site] - target, 0.47 * error, 0.0006 * (q - self.rest)
            ]

        q = least_squares(
            residual,
            seed,
            bounds=(m.jnt_range[:7, 0], m.jnt_range[:7, 1]),
            max_nfev=140,
            ftol=1e-11,
            gtol=1e-11,
            xtol=1e-11,
        ).x
        residual(q)
        if (
            np.linalg.norm(d.site_xpos[self.site] - target) > 0.001
            or np.linalg.norm(residual(q)[3:6]) > 0.003
        ):
            raise ValueError(
                f"Unreachable pinch point {target.round(3)} from {seed.round(2)}"
            )
        return q

    def set_joints(self, q):
        self.data.qpos[:7] = q
        self.data.qpos[7:] = 0.027
        mujoco.mj_forward(self.model, self.data)

    def image(self, group):
        opt = mujoco.MjvOption()
        opt.geomgroup[:] = 0
        opt.geomgroup[group] = 1
        opt.sitegroup[:] = 0
        self.renderer.update_scene(self.data, camera="studio", scene_option=opt)
        rgb = self.renderer.render().copy()
        self.renderer.enable_segmentation_rendering()
        ids = self.renderer.render()
        self.renderer.disable_segmentation_rendering()
        alpha = (ids[:, :, 0] >= 0).astype(np.uint8) * 255
        return Image.fromarray(np.dstack((rgb, alpha)))

    def close(self):
        self.renderer.close()
