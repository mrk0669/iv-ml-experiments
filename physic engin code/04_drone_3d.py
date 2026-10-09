"""
STEP 4 — 3D Quadcopter Simulation
====================================
Full 3D quadcopter with 4 motors, 3D rotation matrices, and matplotlib 3D rendering.
This is EXACTLY how the drone_3d_gif.py in Drone 1 was built.

Run:  python 04_drone_3d.py

Press any arrow key or WASD in the figure window (requires TkAgg).
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation

# ── Physics constants ─────────────────────────────────────────────────────────
DT    = 0.016
MASS  = 1.0
G     = 9.81
ARM   = 0.2    # motor arm length (m)

# Moment of inertia (resistance to rotation around each axis)
Ixx = 0.01   # roll
Iyy = 0.01   # pitch
Izz = 0.02   # yaw  (larger because body is wider than tall)

# ── 3D Rotation utilities ────────────────────────────────────────────────────
def Rx(a):
    """Rotation matrix around X axis (roll)."""
    return np.array([[1,      0,       0    ],
                     [0,  np.cos(a), -np.sin(a)],
                     [0,  np.sin(a),  np.cos(a)]])

def Ry(a):
    """Rotation matrix around Y axis (pitch)."""
    return np.array([[ np.cos(a), 0, np.sin(a)],
                     [     0,     1,     0    ],
                     [-np.sin(a), 0, np.cos(a)]])

def Rz(a):
    """Rotation matrix around Z axis (yaw)."""
    return np.array([[np.cos(a), -np.sin(a), 0],
                     [np.sin(a),  np.cos(a), 0],
                     [    0,          0,     1]])

def euler_to_R(roll, pitch, yaw):
    """Full 3D rotation matrix from Euler angles."""
    return Rz(yaw) @ Ry(pitch) @ Rx(roll)

# ── Quadcopter ───────────────────────────────────────────────────────────────
class Quadcopter:
    def __init__(self):
        # State: position and velocity in world frame
        self.pos   = np.array([0.0, 0.0, 2.0])   # (x, y, z)
        self.vel   = np.array([0.0, 0.0, 0.0])

        # Euler angles (roll, pitch, yaw)
        self.roll  = 0.0
        self.pitch = 0.0
        self.yaw   = 0.0

        # Angular velocities
        self.p = 0.0   # roll rate  (rad/s)
        self.q = 0.0   # pitch rate
        self.r = 0.0   # yaw rate

        # Motor thrusts [FR, FL, RR, RL]  (front-right, front-left, rear-right, rear-left)
        self.motors = np.array([MASS*G/4, MASS*G/4, MASS*G/4, MASS*G/4])

    def set_control(self, throttle, roll_cmd, pitch_cmd, yaw_cmd):
        """
        Convert pilot commands to individual motor thrusts.
        throttle:  +up     roll_cmd: +right   pitch_cmd: +forward   yaw_cmd: +turn left
        Motor layout (X config):
              FL  FR
               \\ /
                X
               / \\
              RL  RR
        """
        T  = MASS * G * throttle          # total thrust
        dr = roll_cmd  * 0.5 * MASS * G  # roll differential
        dp = pitch_cmd * 0.5 * MASS * G  # pitch differential
        dy = yaw_cmd   * 0.1 * MASS * G  # yaw differential

        # +roll  → left motors down, right motors up
        # +pitch → front motors up, rear motors down
        # +yaw   → diagonal pairs spin faster
        self.motors = np.array([
            T/4 + dp/2 - dr/2 + dy/4,   # FL
            T/4 + dp/2 + dr/2 - dy/4,   # FR
            T/4 - dp/2 - dr/2 - dy/4,   # RL
            T/4 - dp/2 + dr/2 + dy/4,   # RR
        ])
        self.motors = np.clip(self.motors, 0.0, MASS * G)

    def update(self):
        FL, FR, RL, RR = self.motors

        # Total thrust (in drone local Z direction)
        total_thrust = FL + FR + RL + RR

        # Torques in body frame
        tau_roll  = ARM * ((FL + RL) - (FR + RR))  # left vs right
        tau_pitch = ARM * ((FL + FR) - (RL + RR))  # front vs rear
        tau_yaw   = 0.05 * ((FL + RR) - (FR + RL)) # CW vs CCW motors

        # Angular acceleration
        p_dot = tau_roll  / Ixx
        q_dot = tau_pitch / Iyy
        r_dot = tau_yaw   / Izz

        # Integrate angular velocity
        self.p += p_dot * DT
        self.q += q_dot * DT
        self.r += r_dot * DT

        # Integrate angles
        self.roll  += self.p * DT
        self.pitch += self.q * DT
        self.yaw   += self.r * DT

        # Clamp angles to avoid gimbal lock in this simple model
        self.roll  = np.clip(self.roll,  -np.pi/3, np.pi/3)
        self.pitch = np.clip(self.pitch, -np.pi/3, np.pi/3)

        # Rotation matrix: body → world
        R = euler_to_R(self.roll, self.pitch, self.yaw)

        # Thrust in body frame → world frame
        thrust_world = R @ np.array([0, 0, total_thrust])

        # Linear acceleration (world frame)
        acc = thrust_world / MASS - np.array([0, 0, G])

        # Integrate linear velocity and position
        self.vel += acc     * DT
        self.pos += self.vel * DT

        # Floor collision
        if self.pos[2] < 0:
            self.pos[2] = 0.0
            self.vel[2] = max(0, self.vel[2])
            self.vel   *= 0.9

    def get_motor_positions(self):
        """World-space positions of 4 motors."""
        R = euler_to_R(self.roll, self.pitch, self.yaw)
        local = np.array([
            [ ARM,  ARM, 0],   # FL
            [ ARM, -ARM, 0],   # FR
            [-ARM,  ARM, 0],   # RL
            [-ARM, -ARM, 0],   # RR
        ])
        return [self.pos + R @ m for m in local]

    def get_body_verts(self):
        """
        Returns list of polygon vertex arrays for 3D rendering:
        - 2 arm beams (as flat boxes)
        - 1 centre hub
        """
        R = euler_to_R(self.roll, self.pitch, self.yaw)
        polys = []

        # Two cross-arms
        for axis in [np.array([1,0,0]), np.array([0,1,0])]:
            pts = []
            for sign in [-1, 1]:
                tip = self.pos + R @ (axis * ARM * sign)
                pts.append(tip)
            # Make a thin flat rectangle
            up  = R @ np.array([0, 0, 0.02])
            side= R @ (np.cross(axis, [0,0,1]) * 0.01)
            q = [pts[0]+side+up, pts[0]-side+up,
                 pts[1]-side+up, pts[1]+side+up]
            polys.append(q)
            q2= [pts[0]+side-up, pts[0]-side-up,
                 pts[1]-side-up, pts[1]+side-up]
            polys.append(q2)

        return polys


# ── Setup ─────────────────────────────────────────────────────────────────────
drone  = Quadcopter()
target = np.array([1.0, 1.0, 3.0])

fig = plt.figure(figsize=(10, 8), facecolor="#0d0d1a")
ax  = fig.add_subplot(111, projection='3d', facecolor="#0d0d1a")
ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_zlim(0, 5)
ax.set_xlabel("X", color="#ff6b6b"); ax.set_ylabel("Y", color="#06d6a0")
ax.set_zlabel("Z", color="#74b9ff")
ax.xaxis.pane.fill = False; ax.yaxis.pane.fill = False; ax.zaxis.pane.fill = False
for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
    pane.set_edgecolor('#1a1a2e')
ax.tick_params(colors="#555")
ax.set_title("Step 4: 3D Quadcopter", color="white", fontsize=13, pad=15)

# Target star
ax.scatter(*target, s=200, c="#ffd166", marker="*", zorder=10)

# Propeller discs
prop_artists = []
for _ in range(4):
    circle_pts = np.array([[np.cos(t)*0.12, np.sin(t)*0.12, 0]
                           for t in np.linspace(0, 2*np.pi, 20)])
    line, = ax.plot([], [], [], '-', color="#8ecae6", alpha=0.5, lw=1.5)
    prop_artists.append(line)

# Motor dots
motor_dots, = ax.plot([], [], [], 'o', color="#ff69b4", markersize=8, zorder=5)

# Body lines (two cross-arms)
arm_lines = [ax.plot([], [], [], '-', color="#a78bfa", lw=3)[0] for _ in range(2)]

# Centre hub
centre_dot, = ax.plot([], [], [], 'o', color="#22d3ee", markersize=12, zorder=6)

# Thrust arrows
thrust_arrows = []
for _ in range(4):
    a = ax.quiver(0,0,0, 0,0,0, color="#22d3ee", alpha=0.7, arrow_length_ratio=0.4)
    thrust_arrows.append(a)

# Trail
trail_x, trail_y, trail_z = [], [], []
trail_line, = ax.plot([], [], [], '-', color="#ff69b4", alpha=0.3, lw=1)

info = ax.text2D(0.02, 0.95, "", transform=ax.transAxes,
                 color="white", fontsize=8, va="top", fontfamily="monospace")

keys = set()
fig.canvas.mpl_connect("key_press_event",   lambda e: keys.add(e.key))
fig.canvas.mpl_connect("key_release_event", lambda e: keys.discard(e.key))

ctrl_text = (
    "Controls:\n"
    "  W/S  — throttle up/down\n"
    "  ←/→  — roll left/right\n"
    "  ↑/↓  — pitch fwd/back\n"
    "  Q/E  — yaw left/right"
)
ax.text2D(0.75, 0.97, ctrl_text, transform=ax.transAxes,
          color="#888", fontsize=7, va="top", fontfamily="monospace")

def animate(frame):
    # Default: hover
    throttle  = 1.0
    roll_cmd  = 0.0
    pitch_cmd = 0.0
    yaw_cmd   = 0.0

    if "w" in keys:        throttle += 0.3
    if "s" in keys:        throttle -= 0.5
    if "left" in keys:     roll_cmd  -= 0.3
    if "right" in keys:    roll_cmd  += 0.3
    if "up" in keys:       pitch_cmd += 0.3
    if "down" in keys:     pitch_cmd -= 0.3
    if "q" in keys:        yaw_cmd   -= 0.3
    if "e" in keys:        yaw_cmd   += 0.3

    drone.set_control(throttle, roll_cmd, pitch_cmd, yaw_cmd)
    drone.update()

    motor_pos = drone.get_motor_positions()

    # Propeller discs
    R = euler_to_R(drone.roll, drone.pitch, drone.yaw)
    for i, (mp, art) in enumerate(zip(motor_pos, prop_artists)):
        angles = np.linspace(0, 2*np.pi, 25)
        r = 0.12
        local = np.array([[r*np.cos(a), r*np.sin(a), 0] for a in angles])
        world = np.array([mp + R @ p for p in local])
        art.set_data(world[:,0], world[:,1])
        art.set_3d_properties(world[:,2])

    # Motor dots
    mxyz = np.array(motor_pos)
    motor_dots.set_data(mxyz[:,0], mxyz[:,1])
    motor_dots.set_3d_properties(mxyz[:,2])

    # Arms
    arm_axes = [np.array([1,0,0]), np.array([0,1,0])]
    for arm_line, axis in zip(arm_lines, arm_axes):
        p1 = drone.pos + R @ ( axis * ARM)
        p2 = drone.pos + R @ (-axis * ARM)
        arm_line.set_data([p1[0],p2[0]], [p1[1],p2[1]])
        arm_line.set_3d_properties([p1[2],p2[2]])

    centre_dot.set_data([drone.pos[0]], [drone.pos[1]])
    centre_dot.set_3d_properties([drone.pos[2]])

    # Trail
    trail_x.append(drone.pos[0]); trail_y.append(drone.pos[1])
    trail_z.append(drone.pos[2])
    if len(trail_x) > 300:
        trail_x.pop(0); trail_y.pop(0); trail_z.pop(0)
    trail_line.set_data(trail_x, trail_y)
    trail_line.set_3d_properties(trail_z)

    dist = np.linalg.norm(drone.pos - target)
    info.set_text(
        f"pos   = ({drone.pos[0]:.2f}, {drone.pos[1]:.2f}, {drone.pos[2]:.2f})\n"
        f"vel   = ({drone.vel[0]:.2f}, {drone.vel[1]:.2f}, {drone.vel[2]:.2f})\n"
        f"roll  = {np.degrees(drone.roll):.1f}°\n"
        f"pitch = {np.degrees(drone.pitch):.1f}°\n"
        f"yaw   = {np.degrees(drone.yaw):.1f}°\n"
        f"dist  = {dist:.2f} m"
    )
    return []

ani = animation.FuncAnimation(fig, animate, frames=6000,
                               interval=16, blit=False)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS LEARNED:
#   1. Euler angles (roll, pitch, yaw) — 3 angles = full orientation in 3D
#   2. Rotation matrix R(roll,pitch,yaw) — converts body frame ↔ world frame
#   3. 4 motors → mix of throttle/roll/pitch/yaw control signals
#   4. Poly3DCollection — draw 3D shapes in matplotlib
#   5. This is EXACTLY the sim in drone_3d_gif.py — you now understand all of it!
# ══════════════════════════════════════════════════════════════════════════════
