# Franka Emika Panda model attribution

The pose artwork in `assets/panda/geometry.json.gz` is adapted from the Franka Emika Panda visual meshes and kinematic model. The model is distributed under Apache-2.0. Its license and the upstream Franka notice are included in this directory. The application code and original pedestal design are covered by the root MIT license.

The source model was converted from Franka's ROS description by MuJoCo Menagerie. Antikythera adds an original fixed pedestal, sets studio lighting and materials, and encodes eleven rendered wrist poses and the gripper as SVG paint layers. The label-free illustration is independent of Franka Robotics.

- [Pinned MuJoCo Menagerie model](https://github.com/google-deepmind/mujoco_menagerie/tree/370c43965323c0944b433b202aac5058b5f907a9/franka_emika_panda)
- [Upstream Franka ROS description](https://github.com/frankarobotics/franka_ros/tree/develop/franka_description)
