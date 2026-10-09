"""
STEP 3 — 2D Drone Physics
==========================
A real 2D drone with 2 motors, gravity, and tilt physics.
Same physics as Drone 1 project.

Controls:
  W / Up    — both motors full (rise)
  A / Left  — right motor only (tilt & go left)
  D / Right — left motor only (tilt & go right)
  S / Down  — cut motors (fall)

Run:  python 03_drone_2d.py
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")   # try "Qt5Agg" or "Agg" if TkAgg not installed
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon, Circle
import matplotlib.transforms as mtransforms

# ── Physics constants ─────────────────────────────────────────────────────────
DT          = 1.0 / 60.0
GRAVITY     = -500.0     # px/s²  (world in pixels)
MASS        = 1.0
INERTIA     = 300.0      # resistance to tilting
DRONE_W     = 60.0       # half-width of drone body in px
FORCE_SCALE = 600.0      # max thrust per motor
WORLD       = 600        # canvas size px

# ── Drone ────────────────────────────────────────────────────────────────────
class Drone2D:
    def __init__(self):
        self.pos   = np.array([WORLD/2, WORLD/2], dtype=float)
        self.vel   = np.array([0.0, 0.0])
        self.angle = 0.0     # tilt angle (rad)
        self.omega = 0.0     # angular velocity
        self.lf    = 0.0     # left force  [0, FORCE_SCALE]
        self.rf    = 0.0     # right force

    def set_motors(self, left, right):
        """Set motor forces (0 to 1 normalized)."""
        self.lf = np.clip(left,  0, 1) * FORCE_SCALE
        self.rf = np.clip(right, 0, 1) * FORCE_SCALE

    def update(self):
        # Total thrust (perpendicular to drone body)
        thrust = self.lf + self.rf

        # The drone is tilted by `angle`, so thrust direction is rotated
        # Thrust pushes "up" in drone local space → rotated to world space
        ax = -thrust * np.sin(self.angle) / MASS
        ay =  thrust * np.cos(self.angle) / MASS + GRAVITY

        # Torque: difference in motor forces causes tilt
        torque = DRONE_W * (self.rf - self.lf) / INERTIA

        # Euler integration
        self.vel[0] += ax        * DT
        self.vel[1] += ay        * DT
        self.omega  += torque    * DT
        self.pos    += self.vel  * DT
        self.angle  += self.omega * DT

        # Clamp to world
        self.pos[0] = np.clip(self.pos[0], 20, WORLD-20)
        self.pos[1] = np.clip(self.pos[1], 20, WORLD-20)

    def get_body_corners(self):
        """Rotated rectangle (drone body)."""
        c, s = np.cos(self.angle), np.sin(self.angle)
        hw, hh = DRONE_W, DRONE_W * 0.15
        local = np.array([[-hw,-hh],[hw,-hh],[hw,hh],[-hw,hh]], dtype=float)
        R = np.array([[c, -s],[s, c]])
        return (R @ local.T).T + self.pos

    def motor_pos(self):
        """World positions of left and right motors."""
        c, s = np.cos(self.angle), np.sin(self.angle)
        R = np.array([[c,-s],[s,c]])
        L = self.pos + R @ np.array([-DRONE_W, 0])
        Rm= self.pos + R @ np.array([ DRONE_W, 0])
        return L, Rm

# ── Setup ────────────────────────────────────────────────────────────────────
drone  = Drone2D()
target = np.array([WORLD/2, WORLD * 0.7])
keys   = set()

fig, ax = plt.subplots(figsize=(7, 7), facecolor="#0d0d1a")
ax.set_facecolor("#0d0d1a")
ax.set_xlim(0, WORLD); ax.set_ylim(0, WORLD)
ax.set_aspect("equal"); ax.axis("off")
fig.canvas.mpl_connect("key_press_event",   lambda e: keys.add(e.key))
fig.canvas.mpl_connect("key_release_event", lambda e: keys.discard(e.key))

# Draw target star
ax.plot(*target, '*', color="#ffd166", markersize=20, zorder=2)
ax.plot([target[0]-15, target[0]+15], [target[1], target[1]],
        color="#ffd166", lw=1.5, zorder=2)
ax.plot([target[0], target[0]], [target[1]-15, target[1]+15],
        color="#ffd166", lw=1.5, zorder=2)

body_patch = Polygon(drone.get_body_corners(), closed=True,
                     facecolor="#ff69b4", edgecolor="#fff", lw=1.5, zorder=5)
ax.add_patch(body_patch)

lmotor_patch = Polygon([[0,0],[0,0],[0,0],[0,0]], closed=True,
                        facecolor="#c71585", edgecolor="#333", lw=0.8, zorder=6)
rmotor_patch = Polygon([[0,0],[0,0],[0,0],[0,0]], closed=True,
                        facecolor="#c71585", edgecolor="#333", lw=0.8, zorder=6)
ax.add_patch(lmotor_patch); ax.add_patch(rmotor_patch)

# Thrust arrows
larrow = ax.annotate("", xy=(0,0), xytext=(0,0),
    arrowprops=dict(arrowstyle="-|>", color="#22d3ee", lw=2))
rarrow = ax.annotate("", xy=(0,0), xytext=(0,0),
    arrowprops=dict(arrowstyle="-|>", color="#22d3ee", lw=2))

trail_line, = ax.plot([], [], '-', color="#ff69b4", alpha=0.25, lw=1)
trail_x, trail_y = [], []

info = ax.text(10, WORLD-10, "", color="white", fontsize=9, va="top",
               fontfamily="monospace")
ctrl = ax.text(WORLD/2, 20, "W=up  A=left  D=right  S=cut",
               color="#666", fontsize=8, ha="center")

def motor_box(pos, size=10):
    x, y = pos
    return np.array([[x-size,y-size],[x+size,y-size],
                     [x+size,y+size],[x-size,y+size]], dtype=float)

def animate(frame):
    # Read keyboard
    if "w" in keys or "up" in keys:
        drone.set_motors(0.9, 0.9)
    elif "a" in keys or "left" in keys:
        drone.set_motors(0.1, 0.85)
    elif "d" in keys or "right" in keys:
        drone.set_motors(0.85, 0.1)
    elif "s" in keys or "down" in keys:
        drone.set_motors(0.0, 0.0)
    else:
        drone.set_motors(0.0, 0.0)

    drone.update()

    # Update visuals
    body_patch.set_xy(drone.get_body_corners())
    L, R = drone.motor_pos()
    lmotor_patch.set_xy(motor_box(L, 8))
    rmotor_patch.set_xy(motor_box(R, 8))

    # Thrust arrows
    c, s = np.cos(drone.angle), np.sin(drone.angle)
    thrust_dir = np.array([-s, c])
    larrow.xy    = L + thrust_dir * (drone.lf / FORCE_SCALE * 40)
    larrow.xytext= L
    rarrow.xy    = R + thrust_dir * (drone.rf / FORCE_SCALE * 40)
    rarrow.xytext= R

    trail_x.append(drone.pos[0]); trail_y.append(drone.pos[1])
    if len(trail_x) > 200:
        trail_x.pop(0); trail_y.pop(0)
    trail_line.set_data(trail_x, trail_y)

    dist = np.linalg.norm(drone.pos - target)
    info.set_text(
        f"pos   = ({drone.pos[0]:.0f}, {drone.pos[1]:.0f})\n"
        f"vel   = ({drone.vel[0]:.1f}, {drone.vel[1]:.1f})\n"
        f"angle = {np.degrees(drone.angle):.1f}°\n"
        f"L/R   = {drone.lf:.0f} / {drone.rf:.0f}\n"
        f"dist  = {dist:.0f} px"
    )
    return body_patch, lmotor_patch, rmotor_patch, trail_line, info

ani = animation.FuncAnimation(fig, animate, frames=6000,
                               interval=16, blit=False)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS LEARNED:
#   1. Thrust direction depends on drone angle (rotation matrix!)
#   2. Two motors → differential thrust → torque → tilt
#   3. Tilt → horizontal movement (sin component of thrust)
#   4. Same equations as Drone 1 project — now you understand them!
# ══════════════════════════════════════════════════════════════════════════════
