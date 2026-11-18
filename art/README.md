# Calendar artwork

The daily Action reads native SVG paths and a small table of wrist positions. The Panda, gripper and stationary pedestal share an orthographic camera. At render time the wrist illustration sits between the rear gripper assembly and the front finger. The calendar, artwork, light pulses and gold pennant all play inside one standalone SVG.

## Rebuild the pose library

1. Download the `franka_emika_panda` directory from the pinned MuJoCo Menagerie revision. Keep `panda.xml` and its `assets/` directory together. [Panda source](https://github.com/google-deepmind/mujoco_menagerie/tree/370c43965323c0944b433b202aac5058b5f907a9/franka_emika_panda)
2. Use a Python 3.12 environment with an offscreen OpenGL context supported by MuJoCo. Install the dependencies with `python -m pip install -r art/requirements.txt`.
3. From the project root, run `python art/bake.py /path/to/franka_emika_panda`. Then run the tests and generate a calendar.

`studio.py` defines the studio lighting and the camera projection. `plinth.py` provides the cast base and its metal collar. The bake produces eleven articulated poses and a split gripper in `assets/panda/geometry.json.gz`. The matching positions in `assets/panda/poses.json` register the wrist artwork to the fingers. [Panda model attribution](../third_party/panda/README.md)

## Custom wrist artwork

Pass an SVG path in the Action’s `artwork` input or with `assembly.py --artwork path/to/art.svg`. Orient the illustration to face left. Use direct-child `path` elements with solid six-digit hex fills. A path may include a two-coordinate `translate` transform. Include a `title` and `metadata` for the artist and license. Both travel with the finished calendar.

| Root attribute | Value |
| --- | --- |
| `viewBox` | Coordinate system of the illustration |
| `data-grip` | Point in the illustration that sits between the fingers, written as `x y` |
| `data-pulse` | Point where the illustrated light pulse appears, written as `x y` |
| `data-span` | Width of the illustration in the arm’s drawing units |

The studio light is a small editable example. Jason’s gallery uses a vectorized capture of a community-published 3D model and carries its own art credits. [Studio light](../assets/studio.svg) · [Gallery artwork and provenance](../gallery/artwork/README.md)
