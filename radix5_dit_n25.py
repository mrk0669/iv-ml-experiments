import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

N        = 25
WIRE_SP  = 0.85
GRP_CLR  = ['#58a6ff', '#f0883e', '#3fb950', '#bc8cff', '#ff7b72']

fig, ax = plt.subplots(figsize=(20, 24))
ax.set_xlim(-1, 16.5)
ax.set_ylim(-2.0, 24.0)
ax.axis('off')
ax.set_facecolor('#0d1117')
fig.patch.set_facecolor('#0d1117')

def wy(w):          return (N - 1 - w) * WIRE_SP
def drev5(n):       return (n % 5) * 5 + (n // 5)

# ── column x-positions ────────────────────────────────────────────────────────
XIN_LBL  = 0.05
XIN_NODE = 1.30
# Stage-1: 5 spines slightly offset to distinguish them
XS1_BASE = 3.60          # centre x for the spine cluster
SPINE_SEP = 0.22         # horizontal gap between spines
XTW      = 6.40          # twiddle box centre
XS2_L    = 8.20
XS2_R    = 11.40
XOUT_N   = 12.50
XOUT_LBL = 13.00

# ── background wires ─────────────────────────────────────────────────────────
for w in range(N):
    ax.plot([XIN_NODE, XOUT_N], [wy(w), wy(w)],
            color='#21262d', lw=0.65, zorder=1)

# ── input labels & nodes ─────────────────────────────────────────────────────
for w in range(N):
    c = GRP_CLR[w % 5]
    y = wy(w)
    ax.text(XIN_LBL, y, f'x[{drev5(w):2d}]', ha='right', va='center',
            fontsize=8, color=c, family='monospace', fontweight='bold')
    ax.add_patch(plt.Circle((XIN_NODE, y), 0.08, color=c, zorder=5))

# ── Stage 1: vertical spine + horizontal stubs ────────────────────────────────
for j in range(5):
    wires  = [j + 5*k for k in range(5)]   # stride-5 group
    c      = GRP_CLR[j]
    ys     = [wy(w) for w in wires]
    y_top  = max(ys)
    y_bot  = min(ys)
    xs     = XS1_BASE + (j - 2) * SPINE_SEP   # offset per BF group

    # vertical spine
    ax.plot([xs, xs], [y_bot, y_top],
            color=c, lw=2.5, alpha=0.70, zorder=4,
            solid_capstyle='round')

    for y in ys:
        # input stub: wire → spine
        ax.plot([XIN_NODE + 0.08, xs], [y, y],
                color=c, lw=1.1, alpha=0.85, zorder=3)
        # output stub: spine → twiddle
        ax.plot([xs, XTW - 0.38], [y, y],
                color=c, lw=1.1, alpha=0.85, zorder=3)
        # dot at spine junction
        ax.add_patch(plt.Circle((xs, y), 0.07, color=c, zorder=6))

    # BF label above its spine
    ax.text(xs, y_top + 0.32, f'BF{j}',
            ha='center', va='bottom', fontsize=7.5,
            color=c, fontweight='bold', zorder=7)

# ── twiddle factors  W_25^{j·k} ──────────────────────────────────────────────
for w in range(N):
    j   = w % 5
    k   = w // 5
    exp = (j * k) % 25
    c   = GRP_CLR[j]
    y   = wy(w)

    lbl   = r'$1$' if exp == 0 else f'$W_{{25}}^{{{exp}}}$'
    alpha = 0.28  if exp == 0 else 1.0

    ax.add_patch(mpatches.FancyBboxPatch(
        (XTW - 0.37, y - 0.22), 0.74, 0.44,
        boxstyle='round,pad=0.03',
        linewidth=0.9, edgecolor=c,
        facecolor='#161b22', zorder=5, alpha=alpha))
    ax.text(XTW, y, lbl, ha='center', va='center',
            fontsize=6.8, color=c, zorder=6, alpha=alpha)

    # stub → Stage 2
    ax.plot([XTW + 0.37, XS2_L], [y, y],
            color=c, lw=1.0, zorder=2)

# ── Stage 2: compact butterfly boxes (5 consecutive wires) ───────────────────
for k in range(5):
    wires = [5*k + j for j in range(5)]
    y_top = wy(wires[0])  + 0.33
    y_bot = wy(wires[-1]) - 0.33
    y_mid = (y_top + y_bot) / 2
    bw    = XS2_R - XS2_L

    ax.add_patch(mpatches.FancyBboxPatch(
        (XS2_L, y_bot), bw, y_top - y_bot,
        boxstyle='round,pad=0.1',
        linewidth=1.6, edgecolor='#c9d1d9',
        facecolor='#161b22', zorder=3))

    # light butterfly-crossing pattern inside box
    cx = (XS2_L + XS2_R) / 2
    for i, w1 in enumerate(wires):
        for i2, w2 in enumerate(wires):
            if i != i2:
                ax.plot([XS2_L + 0.3, cx],
                        [wy(w1), (wy(w1)+wy(w2))/2],
                        color='#444c56', lw=0.45, alpha=0.45, zorder=4)

    ax.text(cx, y_mid, f'$R_5$ BF{k}\nconsecutive',
            ha='center', va='center', fontsize=9,
            color='#c9d1d9', fontweight='bold', zorder=7,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#0d1117', alpha=0.92))

    for w in wires:
        ax.plot([XS2_R, XOUT_N - 0.08], [wy(w), wy(w)],
                color='#8b949e', lw=1.1, zorder=2)

# ── output nodes & labels ─────────────────────────────────────────────────────
for w in range(N):
    y = wy(w)
    ax.add_patch(plt.Circle((XOUT_N, y), 0.08, color='#c9d1d9', zorder=5))
    ax.text(XOUT_LBL, y, f'X[{w:2d}]', ha='left', va='center',
            fontsize=8, color='#e6edf3', family='monospace', fontweight='bold')

# ── column headers ────────────────────────────────────────────────────────────
yH = wy(0) + 1.00
ax.text(XS1_BASE, yH,       'STAGE 1',     ha='center', fontsize=13, color='#58a6ff', fontweight='bold')
ax.text(XS1_BASE, yH - 0.52,'5 × R5  (stride 5)', ha='center', fontsize=8.5, color='#8b949e')
ax.text(XTW,      yH,       'TWIDDLE',     ha='center', fontsize=11, color='#f0883e', fontweight='bold')
ax.text(XTW,      yH - 0.52, r'$W_{25}^{j \cdot k}$', ha='center', fontsize=9,  color='#f0883e')
ax.text((XS2_L+XS2_R)/2, yH,'STAGE 2',    ha='center', fontsize=13, color='#c9d1d9', fontweight='bold')
ax.text((XS2_L+XS2_R)/2, yH-0.52,'5 × R5  (stride 1)', ha='center', fontsize=8.5, color='#8b949e')

# ── title ─────────────────────────────────────────────────────────────────────
ax.text(7.2, wy(0) + 2.05,
        'Radix-5 DIT FFT Butterfly Structure  —  N = 25  (= 5²,  2 stages)',
        ha='center', fontsize=16, color='#58a6ff', fontweight='bold')
ax.text(7.2, wy(0) + 1.52,
        r'$X[k]=\mathrm{DFT}_{25}\{x[n]\}$   ·   $W_{25}=e^{-j2\pi/25}$   ·   inputs in base-5 digit-reversed order',
        ha='center', fontsize=10, color='#c9d1d9')

# ── legend ────────────────────────────────────────────────────────────────────
patches = [
    mpatches.Patch(color=GRP_CLR[j],
                   label=f'Stage-1 BF{j}: wires {j}, {j+5}, {j+10}, {j+15}, {j+20}')
    for j in range(5)
]
patches.append(mpatches.Patch(color='#c9d1d9', label='Stage-2 BFs: 5 consecutive wires each'))
ax.legend(handles=patches, loc='lower left', fontsize=8.5,
          framealpha=0.5, facecolor='#161b22',
          edgecolor='#30363d', labelcolor='#e6edf3')

plt.tight_layout(pad=0.5)
out = r'C:\Users\KESHAV\Desktop\iv project\radix5_dit_n25.png'
plt.savefig(out, dpi=160, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f'Saved: {out}')
plt.close()
