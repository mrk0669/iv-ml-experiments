PHYSICS ENGINE LEARNING PATH
=============================

Run these files in order — each one teaches the next concept.

  01_basics.py     — Gravity, velocity, position, Euler integration
                     (ball bouncing under gravity)

  02_rotation.py   — Rotation matrices, angular velocity, torque
                     (box that spins in 2D)

  03_drone_2d.py   — 2D drone physics: 2 motors, tilt, thrust direction
  [INTERACTIVE]      Use W/A/S/D keys to fly it
                     Same physics as Drone 1 project!

  04_drone_3d.py   — Full 3D quadcopter: 4 motors, Euler angles, 3D rendering
  [INTERACTIVE]      Use WASD + arrows to fly it
                     This is exactly how drone_3d_gif.py was built.

INSTALL:
  pip install numpy matplotlib

WHAT YOU LEARN:
  1. pos += vel * dt         (Euler integration)
  2. vel += force/mass * dt  (Newton's 2nd law)
  3. Rotation matrix R(θ)    (2D rotation)
  4. R(roll, pitch, yaw)     (3D rotation = Euler angles)
  5. 4 motors → mix of throttle/roll/pitch/yaw

NEXT STEPS AFTER THIS:
  - Add a PID controller to auto-hover (no keyboard needed)
  - Add reinforcement learning (Drone 1 and 2 projects!)
  - Use PyBullet or Isaac Gym for real 3D physics with collision
