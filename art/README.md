# Baking the Panda shuttle

The published Action needs Python's standard library and the GitHub CLI. The optional art pipeline uses MuJoCo to render the actual Panda meshes and the original shuttle under an orthographic studio camera. It bakes the arm, gripper and wheels into separate sets of poses. The pinch locations come directly from the same camera projection.

The runtime embeds the required rendered poses as native SVG paths. A standalone SVG can therefore play as a README image or in its own browser tab, with no external meshes, images, scripts, fonts or rendering service.

## Rebuild the pose library

1. Obtain the `franka_emika_panda` directory from the [pinned MuJoCo Menagerie revision](https://github.com/google-deepmind/mujoco_menagerie/tree/370c43965323c0944b433b202aac5058b5f907a9/franka_emika_panda). Keep `panda.xml` and its `assets/` directory together.
2. Use a Python 3.12 virtual environment and an offscreen OpenGL context supported by MuJoCo. Install the art dependencies with `python -m pip install -r art/requirements.txt`.
3. From the project root, run `python art/bake.py /path/to/franka_emika_panda`, then run the tests and regenerate the calendar.

`studio.py` defines lighting, camera calibration, the pinch site and inverse kinematics. `chassis.py` defines the four-wheel shuttle and its cargo tray. `outlines.py` encodes the lit surfaces into SVG paint layers. `bake.py` writes those layers to `assets/rover/geometry.json.gz` and the projected motion paths to `assets/rover/poses.json`.

The board and rover use the same display units. At a collection stop the chassis translates along the road until the projected pinch site coincides with a real day cell. In the tray, each occupied slot is the projected pinch point of the corresponding deposit pose. [Panda attribution and license](../third_party/panda/README.md)
