"""
STEP 1 — Physics Basics
========================
Core concepts: position, velocity, acceleration, gravity, Euler integration.

Run:  python 01_basics.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ── Constants ────────────────────────────────────────────────────────────────
GRAVITY = -9.81   # m/s²  (negative = downward)
DT      = 0.016   # seconds per frame (~60 fps)

# ── The Object ───────────────────────────────────────────────────────────────
class Ball:
    def __init__(self, x, y, vx, vy):
        self.pos = np.array([x, y], dtype=float)   # position (m)
        self.vel = np.array([vx, vy], dtype=float)  # velocity (m/s)

    def update(self):
        # EULER INTEGRATION — heart of every physics sim
        # acceleration from gravity
        acc = np.array([0.0, GRAVITY])

        # velocity changes due to acceleration
        self.vel += acc * DT

        # position changes due to velocity
        self.pos += self.vel * DT

        # Bounce off floor at y=0
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] *= -0.7   # 30% energy lost on bounce

# ── Setup ────────────────────────────────────────────────────────────────────
ball = Ball(x=0, y=10, vx=5, vy=8)   # start at (0,10), thrown diagonally

fig, ax = plt.subplots(figsize=(10, 6), facecolor="#0d0d1a")
ax.set_facecolor("#0d0d1a")
ax.set_xlim(-1, 20)
ax.set_ylim(-0.5, 15)
ax.set_title("Step 1: Gravity + Euler Integration", color="white", fontsize=13)
ax.set_xlabel("X (m)", color="gray")
ax.set_ylabel("Y (m)", color="gray")
ax.tick_params(colors="gray")
ax.spines['bottom'].set_color('#333'); ax.spines['left'].set_color('#333')
ax.spines['top'].set_visible(False);  ax.spines['right'].set_visible(False)
ax.axhline(0, color="#22d3ee", lw=2, label="Ground")

dot,   = ax.plot([], [], 'o', color="#ff69b4", markersize=14, zorder=5)
trail, = ax.plot([], [], '-', color="#ff69b4", alpha=0.3, lw=1.5)
info   = ax.text(0.02, 0.95, "", transform=ax.transAxes,
                 color="white", fontsize=10, va="top")

trail_x, trail_y = [], []

def animate(frame):
    ball.update()
    trail_x.append(ball.pos[0])
    trail_y.append(ball.pos[1])

    dot.set_data([ball.pos[0]], [ball.pos[1]])
    trail.set_data(trail_x, trail_y)
    info.set_text(f"pos=({ball.pos[0]:.1f}, {ball.pos[1]:.1f})  "
                  f"vel=({ball.vel[0]:.1f}, {ball.vel[1]:.1f})")
    return dot, trail, info

ax.legend(facecolor="#1a1a2e", labelcolor="white")
ani = animation.FuncAnimation(fig, animate, frames=300,
                               interval=16, blit=True)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS LEARNED:
#   1. pos += vel * dt        ← Euler position integration
#   2. vel += acc * dt        ← Euler velocity integration
#   3. acc = force / mass     ← Newton's 2nd law  (F = ma)
#   4. Gravity is just a downward force every frame
#   5. Bounce = flip velocity direction (with energy loss)
# ══════════════════════════════════════════════════════════════════════════════
