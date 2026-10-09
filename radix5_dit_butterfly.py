import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(-0.5, 13)
ax.set_ylim(-0.5, 9.5)
ax.axis('off')
ax.set_facecolor('#0d1117')
fig.patch.set_facecolor('#0d1117')

# ── colours ──────────────────────────────────────────────────────────────────
C_NODE   = '#58a6ff'
C_LINE   = '#8b949e'
C_TWID   = '#f0883e'
C_LABEL  = '#e6edf3'
C_TITLE  = '#58a6ff'
C_SUMBOX = '#238636'

NODE_R = 0.22

# ── node positions ────────────────────────────────────────────────────────────
# y positions (top → bottom): 4 inputs spread evenly from 8 to 0
y_pos = [8, 6, 4, 2, 0]

# columns: x[n] inputs | twiddle multiply | sum node | X[k] outputs
COL_IN    = 1.0
COL_TW    = 4.5    # twiddle-factor multiplier column
COL_SUM   = 8.0    # summation node column
COL_OUT   = 11.0

# W_5 twiddle labels
def tw_label(n, k):
    exp = (n * k) % 5
    if exp == 0:
        return r'$W_5^0\!=\!1$'
    return rf'$W_5^{{{exp}}}$'

# ── draw a filled circle node ─────────────────────────────────────────────────
def draw_node(cx, cy, color=C_NODE, r=NODE_R, zorder=5):
    circ = plt.Circle((cx, cy), r, color=color, zorder=zorder)
    ax.add_patch(circ)

# ── draw arrow ───────────────────────────────────────────────────────────────
def draw_arrow(x1, y1, x2, y2, color=C_LINE, lw=1.2, style='->', zorder=3):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle='arc3,rad=0'))

# ── draw line (no arrowhead) ─────────────────────────────────────────────────
def draw_line(x1, y1, x2, y2, color=C_LINE, lw=1.2, ls='-', zorder=3):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, ls=ls, zorder=zorder)

# ── twiddle-factor multiplier box ─────────────────────────────────────────────
def draw_twiddle_box(cx, cy, label, color=C_TWID):
    rect = mpatches.FancyBboxPatch((cx - 0.45, cy - 0.28), 0.9, 0.56,
                                    boxstyle='round,pad=0.05',
                                    linewidth=1.2, edgecolor=color,
                                    facecolor='#161b22', zorder=5)
    ax.add_patch(rect)
    ax.text(cx, cy, label, ha='center', va='center',
            fontsize=7.5, color=color, zorder=6)

# ── summation circle ─────────────────────────────────────────────────────────
def draw_sum_node(cx, cy):
    circ = plt.Circle((cx, cy), NODE_R + 0.06, color=C_SUMBOX,
                       zorder=5, linewidth=0)
    ax.add_patch(circ)
    ax.text(cx, cy, r'$\Sigma$', ha='center', va='center',
            fontsize=11, color='white', fontweight='bold', zorder=6)

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD THE DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

# ── Input labels & nodes ──────────────────────────────────────────────────────
for n in range(5):
    y = y_pos[n]
    ax.text(0.0, y, rf'$x[{n}]$', ha='right', va='center',
            fontsize=12, color=C_LABEL, fontweight='bold')
    draw_node(COL_IN, y, C_NODE)

# ── Fan out lines from each input node ───────────────────────────────────────
# Each input x[n] fans out to ALL 5 twiddle-box rows (one per output k)
# Twiddle boxes are arranged vertically at x=COL_TW, same y as outputs

for n in range(5):    # input index
    for k in range(5):   # output index
        y_src = y_pos[n]
        y_dst = y_pos[k]  # twiddle box row matches output row

        # horizontal segment from input node to a small junction
        x_junc = COL_IN + 0.5
        # draw line from input to junction then down/up to twiddle
        # Use a bent path: go right to x_junc, then diagonally to twiddle box
        draw_line(COL_IN + NODE_R, y_src,
                  x_junc, y_src, color=C_LINE, lw=0.9)
        draw_line(x_junc, y_src,
                  COL_TW - 0.46, y_dst, color=C_LINE, lw=0.9, zorder=2)

# ── Twiddle boxes  (one per (n,k) pair → stacked per output k) ───────────────
# We place 5 twiddle boxes horizontally for each output row k
# x spacing within a row: spread 5 boxes around COL_TW
TW_SPACING = 0.72
tw_xs = [COL_TW - 2*TW_SPACING + i*TW_SPACING for i in range(5)]

for k in range(5):   # output row
    y = y_pos[k]
    for n in range(5):   # which input
        cx = tw_xs[n]
        label = tw_label(n, k)
        draw_twiddle_box(cx, y, label)
        # line from twiddle box to sum node
        draw_line(cx + 0.46, y, COL_SUM - NODE_R - 0.08, y,
                  color=C_TWID, lw=1.0)

# ── Sum nodes ─────────────────────────────────────────────────────────────────
for k in range(5):
    draw_sum_node(COL_SUM, y_pos[k])

# ── Output lines & labels ─────────────────────────────────────────────────────
for k in range(5):
    y = y_pos[k]
    draw_arrow(COL_SUM + NODE_R + 0.08, y, COL_OUT - 0.1, y,
               color=C_NODE, lw=1.4)
    ax.text(COL_OUT, y, rf'$X[{k}]$', ha='left', va='center',
            fontsize=12, color=C_LABEL, fontweight='bold')

# ── Input vertical junction dots ──────────────────────────────────────────────
for n in range(5):
    draw_node(COL_IN + 0.5, y_pos[n], color='#ffffff', r=0.07, zorder=7)

# ── Title & annotations ───────────────────────────────────────────────────────
ax.text(6.25, 9.2, 'Radix-5 DIT Butterfly Structure',
        ha='center', va='center', fontsize=16,
        color=C_TITLE, fontweight='bold')

ax.text(6.25, 8.75,
        r'$X[k] = \sum_{n=0}^{4} x[n]\cdot W_5^{nk}$,   $W_5 = e^{-j2\pi/5}$',
        ha='center', va='center', fontsize=11, color='#c9d1d9')

# Legend
legend_items = [
    mpatches.Patch(color=C_NODE,   label='Input / Output node'),
    mpatches.Patch(color=C_TWID,   label=r'Twiddle factor $W_5^{nk}$'),
    mpatches.Patch(color=C_SUMBOX, label='Summation node  (Σ)'),
]
ax.legend(handles=legend_items, loc='lower left',
          fontsize=9, framealpha=0.3,
          facecolor='#161b22', edgecolor=C_LINE, labelcolor=C_LABEL)

plt.tight_layout()
out_path = r'C:\Users\KESHAV\Desktop\iv project\radix5_dit_butterfly.png'
plt.savefig(out_path, dpi=180, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print(f'Saved: {out_path}')
plt.show()
