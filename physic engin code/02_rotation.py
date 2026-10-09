"""
STEP 2 — Rotation & Rigid Body
================================
Concepts: angle, angular velocity, torque, rotation matrices.
A box that spins in 2D.

Run:  python 02_rotation.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon

DT = 0.016

# ── Rigid Body ───────────────────────────────────────────────────────────────
class RigidBody:
    def __init__(self):
        self.pos    = np.array([0.0, 0.0])   # centre position
        self.vel    = np.array([0.0, 0.0])   # linear velocity
        self.angle  = 0.0                    # rotation angle (radians)
        self.omega  = 0.5                    # angular velocity (rad/s)
        self.mass   = 1.0
        self.inertia= 1.0                    # moment of inertia

    def apply_force(self, force):
        """F = ma  →  a = F/m"""
        acc = force / self.mass
        self.vel   += acc    * DT
        self.pos   += self.vel * DT

    def apply_torque(self, torque):
        """τ = I·α  →  α = τ/I"""
        alpha      = torque / self.inertia
        self.omega += alpha * DT
        self.angle += self.omega * DT

    def get_corners(self, w=1.0, h=0.4):
        """Get world-space corners of a box with this body's rotation."""
        # 2D rotation matrix
        # [ cos θ  -sin θ ]
        # [ sin θ   cos θ ]
        c, s = np.cos(self.angle), np.sin(self.angle)
        R = np.array([[c, -s],
                      [s,  c]])

        # Local corners (centred at origin)
        local = np.array([[-w/2, -h/2],
                           [ w/2, -h/2],
                           [ w/2,  h/2],
                           [-w/2,  h/2]])

        # Rotate and translate to world space
        world = (R @ local.T).T + self.pos
        return world

# ── Setup ────────────────────────────────────────────────────────────────────
body = RigidBody()

fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor="#0d0d1a")
ax1, ax2 = axes
for ax in axes:
    ax.set_facecolor("#0d0d1a")
    ax.tick_params(colors="gray")
    for sp in ax.spines.values(): sp.set_color('#333')

ax1.set_xlim(-2, 2); ax1.set_ylim(-2, 2)
ax1.set_aspect("equal")
ax1.set_title("Rotating Box (2D)", color="white", fontsize=12)
ax1.axhline(0, color='#333', lw=0.5)
ax1.axvline(0, color='#333', lw=0.5)

box_patch = Polygon(body.get_corners(), closed=True,
                    facecolor="#8b5cf6", edgecolor="#a78bfa", lw=2)
ax1.add_patch(box_patch)

# Draw a red dot on one corner to show rotation visually
red_dot, = ax1.plot([], [], 'o', color="#ff6b6b", markersize=8, zorder=5)

# Forward vector arrow
arrow_x = ax1.annotate("", xy=(0,0), xytext=(0,0),
    arrowprops=dict(arrowstyle="-|>", color="#22d3ee", lw=2))

angle_history = []
ax2.set_xlim(0, 300); ax2.set_ylim(-10, 10)
ax2.set_title("Angle over time (radians)", color="white", fontsize=12)
ax2.set_xlabel("Frame", color="gray")
ax2.set_ylabel("Angle (rad)", color="gray")
angle_line, = ax2.plot([], [], color="#22d3ee", lw=1.5)

info = ax1.text(0.02, 0.95, "", transform=ax1.transAxes,
                color="white", fontsize=9, va="top")

torque_dir = 1.0
frame_count = [0]

def animate(frame):
    frame_count[0] += 1

    # Reverse torque every 80 frames to show direction change
    t = torque_dir * np.sin(frame_count[0] * 0.05) * 2.0
    body.apply_torque(t)
    body.apply_force(np.array([0.0, -9.81]) * body.mass * DT)

    # Bounce on floor
    if body.pos[1] < -1.5:
        body.pos[1] = -1.5
        body.vel[1] = abs(body.vel[1]) * 0.5

    corners = body.get_corners()
    box_patch.set_xy(corners)
    red_dot.set_data([corners[0, 0]], [corners[0, 1]])

    # Forward vector (local Y axis rotated)
    c, s = np.cos(body.angle), np.sin(body.angle)
    fwd = body.pos + np.array([-s, c]) * 0.8
    arrow_x.xy = fwd; arrow_x.xytext = body.pos

    angle_history.append(body.angle)
    angle_line.set_data(range(len(angle_history)), angle_history)
    if len(angle_history) > 300:
        ax2.set_xlim(len(angle_history)-300, len(angle_history))

    info.set_text(f"angle = {body.angle:.2f} rad  ({np.degrees(body.angle):.1f}°)\n"
                  f"omega = {body.omega:.2f} rad/s\n"
                  f"torque = {t:.2f} N·m")
    return box_patch, red_dot, angle_line, info

ani = animation.FuncAnimation(fig, animate, frames=600, interval=16, blit=False)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS LEARNED:
#   1. Rotation matrix R(θ) — rotates any 2D point around origin
#   2. angular velocity ω  — how fast angle changes (rad/s)
#   3. torque τ            — rotational force (like F but for spin)
#   4. moment of inertia I — resistance to spinning (like mass for rotation)
#   5. τ = I·α  (same as F = m·a but for rotation)
# ══════════════════════════════════════════════════════════════════════════════
