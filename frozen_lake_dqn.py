#!/usr/bin/env python3
"""
Cross-Scale FrozenLake DQN Generalization Experiment
------------------------------------------------------
Phase 1 — Dataset generation:
  Collect SAMPLES_PER_SIZE random transitions from each grid size
  (2^2 … 2^10 = 4 … 1024), then shuffle into one mixed replay buffer.

Phase 2 — Online DQN training:
  A shared DQN (state = normalized row/col — size-agnostic) continues
  collecting experience from all training environments via epsilon-greedy
  exploration.  Training alternates between all grid sizes so the network
  generalises across scales.

Phase 3 — Evaluation on unseen scales:
  Greedy rollouts on 2x2, 8x8, 64x64 (2x2 is fully unseen during training).

Key design choice:
  state = (row/n, col/n) — the same two numbers mean the same geometric
  location relative to goal regardless of absolute grid size.
"""

import time, random, warnings
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import gymnasium as gym
from gymnasium.envs.toy_text.frozen_lake import generate_random_map
from collections import deque
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")

# -- Reproducibility ----------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# -- Configuration -------------------------------------------------------------
TRAIN_SIZES      = [2**k for k in range(2, 11)]   # 4 8 16 32 64 128 256 512 1024  (all even)
EVAL_SIZES       = [2, 8, 64]                      # even held-out sizes
ODD_EVAL_SIZES   = [3, 5, 7, 9, 15, 33, 65]       # ODD sizes — never seen during training!
SAMPLES_PER_SIZE = 100        # random transitions collected BEFORE training starts

# Online training
TRAIN_STEPS      = 150_000    # total env steps across all training sizes
BUFFER_MAXLEN    = 80_000
BATCH_SIZE       = 128
GAMMA            = 0.95
LR               = 3e-4
TARGET_UPDATE    = 200
EPSILON_START    = 1.0
EPSILON_END      = 0.10       # keep 10% exploration to avoid deterministic cycles
EPSILON_DECAY    = 100_000    # decay over full run for sustained exploration

# Inverse-size sampling weights: smaller grids get proportionally more training
# attention (goal is reachable, reward signal is real) while large grids still
# contribute their structural diversity.
_SIZE_WEIGHTS = [1.0 / (k + 1) for k in range(len([2**i for i in range(2,11)]))]
_SW_SUM       = sum(_SIZE_WEIGHTS)

# Evaluation
EVAL_EPISODES    = 100
MAX_STEPS_EVAL   = 500

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2x2 map: fully frozen (no holes) so the agent can reach G from S
_MAP_2x2 = ["SF", "FG"]

# Cache maps — training and evaluation reuse the same layout per size.
# p=0.92 gives ~8% holes: enough challenge, still navigable without map info.
_MAP_CACHE: dict = {}


def _get_map(size: int) -> list | None:
    if size not in _MAP_CACHE:
        if size == 2:
            _MAP_CACHE[size] = _MAP_2x2
        else:
            # p=1.0 → zero holes: pure navigation task, no obstacle noise.
            # Isolates scale-generalization from obstacle avoidance so the DQN
            # can always reach the goal during training (needed for Q-propagation).
            _MAP_CACHE[size] = generate_random_map(size=size, p=1.0, seed=SEED + size)
    return _MAP_CACHE[size]


# -- Helpers ------------------------------------------------------------------
def encode(obs: int, n: int) -> np.ndarray:
    """
    Displacement-to-goal encoding: ((n-1-row)/n, (n-1-col)/n).
    Start ≈ (1,1), goal = (0,0) for all grid sizes.
    This monotone target is easier for the DQN to learn consistently,
    and avoids cycles because progress always reduces both components.
    """
    row, col = obs // n, obs % n
    return np.array([(n - 1 - row) / n, (n - 1 - col) / n], dtype=np.float32)


def dist_reward(obs: int, nobs: int, n: int, r: float) -> float:
    """
    Sparse goal reward + small Manhattan-distance improvement bonus.
    Positive delta = agent moved closer to goal (bottom-right corner).
    Scaled to 0.1 so the goal reward (1.0) still dominates.
    """
    old_dist = abs(obs  // n - (n - 1)) + abs(obs  % n - (n - 1))
    new_dist = abs(nobs // n - (n - 1)) + abs(nobs % n - (n - 1))
    max_dist = 2.0 * (n - 1) if n > 1 else 1.0
    return r + 0.1 * (old_dist - new_dist) / max_dist


def make_env(size: int, for_eval: bool = False) -> gym.Env:
    desc = _get_map(size)
    kwargs = dict(is_slippery=False)
    if desc is not None:
        kwargs["desc"] = desc
    # Scale episode steps with grid size so agents on large grids CAN reach goal.
    # Minimum Manhattan distance = 2*(n-1); we add margin so random exploration
    # can discover the goal during training.
    # Training: 8x margin for grids >=64, 4x for smaller. Evaluation: 12x.
    if for_eval:
        multiplier = 12
    elif size >= 64:
        multiplier = 8    # larger margin → more goal sightings during training
    else:
        multiplier = 4
    kwargs["max_episode_steps"] = max(200, multiplier * size)
    return gym.make("FrozenLake-v1", **kwargs)


# -- Dataset pre-collection ---------------------------------------------------
def collect_random(size: int, n: int = SAMPLES_PER_SIZE) -> list:
    """
    Collect n transitions using a random policy.
    These seed the replay buffer before online training begins.
    """
    env = make_env(size)
    obs, _ = env.reset(seed=SEED)
    buf = []
    for _ in range(n):
        a = env.action_space.sample()
        nobs, r, term, trunc, _ = env.step(a)
        done = term or trunc
        buf.append((
            encode(obs, size), a,
            dist_reward(obs, nobs, size, r),
            encode(nobs, size), float(done),
        ))
        obs = env.reset(seed=random.randint(0, 999_999))[0] if done else nobs
    env.close()
    return buf


# -- DQN Architecture ---------------------------------------------------------
class DQN(nn.Module):
    """
    2-layer MLP: normalized (row/n, col/n) -> 4 action Q-values.
    Smaller than the overparameterised version to prevent Q-value explosion.
    """
    def __init__(self, hidden: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2,      hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 4),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# -- Online Multi-Task DQN Training -------------------------------------------
def train(initial_dataset: list):
    """
    Online DQN that trains across all grid sizes simultaneously.
    The replay buffer is pre-seeded with SAMPLES_PER_SIZE transitions per size,
    then continuously updated via epsilon-greedy exploration.

    Returns (policy, per-step loss list, per-step epsilon list).
    """
    buffer  = deque(initial_dataset, maxlen=BUFFER_MAXLEN)
    envs    = {sz: make_env(sz) for sz in TRAIN_SIZES}
    obs_map = {sz: envs[sz].reset(seed=SEED + sz)[0] for sz in TRAIN_SIZES}

    policy  = DQN().to(DEVICE)
    target  = DQN().to(DEVICE)
    target.load_state_dict(policy.state_dict())
    target.eval()

    opt     = optim.Adam(policy.parameters(), lr=LR, weight_decay=1e-5)
    loss_fn = nn.SmoothL1Loss()
    losses, epsilons = [], []

    def epsilon_at(step):
        frac = min(step / EPSILON_DECAY, 1.0)
        return EPSILON_START + frac * (EPSILON_END - EPSILON_START)

    # Inverse-size weights: small grids (fast goal discovery, clean signal) lead
    # early training; all sizes still contribute throughout.
    sw = [1.0 / (k + 1) for k in range(len(TRAIN_SIZES))]

    for step in range(1, TRAIN_STEPS + 1):
        eps = epsilon_at(step)
        sz  = random.choices(TRAIN_SIZES, weights=sw, k=1)[0]
        env = envs[sz]

        # Epsilon-greedy action
        if random.random() < eps:
            a = env.action_space.sample()
        else:
            s = torch.tensor(encode(obs_map[sz], sz),
                             dtype=torch.float32, device=DEVICE).unsqueeze(0)
            with torch.no_grad():
                a = policy(s).argmax(1).item()

        nobs, r, term, trunc, _ = env.step(a)
        done = term or trunc
        buffer.append((
            encode(obs_map[sz], sz), a,
            dist_reward(obs_map[sz], nobs, sz, r),
            encode(nobs, sz), float(done),
        ))
        obs_map[sz] = (env.reset(seed=random.randint(0, 999_999))[0]
                       if done else nobs)

        # Learn from a random minibatch
        if len(buffer) >= BATCH_SIZE:
            batch = random.sample(buffer, BATCH_SIZE)
            S  = torch.tensor(np.array([d[0] for d in batch]),
                              dtype=torch.float32, device=DEVICE)
            A  = torch.tensor([d[1] for d in batch],
                              dtype=torch.long,    device=DEVICE).unsqueeze(1)
            R  = torch.tensor([d[2] for d in batch],
                              dtype=torch.float32, device=DEVICE)
            NS = torch.tensor(np.array([d[3] for d in batch]),
                              dtype=torch.float32, device=DEVICE)
            D  = torch.tensor([d[4] for d in batch],
                              dtype=torch.float32, device=DEVICE)

            q = policy(S).gather(1, A).squeeze(1)
            with torch.no_grad():
                # Double DQN: policy net selects action, target net evaluates
                best_a   = policy(NS).argmax(1, keepdim=True)
                q_target = R + GAMMA * target(NS).gather(1, best_a).squeeze(1) * (1 - D)
            loss = loss_fn(q, q_target)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
            opt.step()
            losses.append(loss.item())
            epsilons.append(eps)

        if step % TARGET_UPDATE == 0:
            target.load_state_dict(policy.state_dict())

        if step % 10_000 == 0 or step == 1:
            avg = np.mean(losses[-500:]) if losses else float("nan")
            print(f"  step {step:6d}/{TRAIN_STEPS}  "
                  f"eps={eps:.3f}  loss={avg:.5f}  buf={len(buffer)}")

    for env in envs.values():
        env.close()
    return policy, losses, epsilons


# -- Evaluation ---------------------------------------------------------------
def evaluate(model: DQN, size: int, n: int = EVAL_EPISODES) -> dict:
    """Greedy evaluation over n episodes; returns stats dict."""
    model.eval()
    env = make_env(size, for_eval=True)
    successes, rewards, steps_list = 0, [], []

    for ep in range(n):
        obs, _ = env.reset(seed=2000 + ep)
        ep_r   = 0.0
        visited: set = set()
        for step in range(MAX_STEPS_EVAL):
            if obs in visited:          # deterministic cycle — stop early
                break
            visited.add(obs)
            s = torch.tensor(encode(obs, size),
                             dtype=torch.float32, device=DEVICE).unsqueeze(0)
            with torch.no_grad():
                a = model(s).argmax(1).item()
            obs, r, term, trunc, _ = env.step(a)
            ep_r += r
            if term or trunc:
                break
        rewards.append(ep_r)
        steps_list.append(step + 1)
        if ep_r > 0:
            successes += 1

    env.close()
    return {
        "size":         size,
        "success_rate": successes / n,
        "mean_reward":  float(np.mean(rewards)),
        "mean_steps":   float(np.mean(steps_list)),
    }


# -- Plotting -----------------------------------------------------------------
def plot_all(losses: list, epsilons: list, results: list,
             dataset_dist: dict, policy: DQN):
    train_set = set(TRAIN_SIZES)
    colors    = ["#27ae60" if r["size"] in train_set else "#e74c3c"
                 for r in results]
    xlabels   = [f"{r['size']}x{r['size']}" for r in results]

    fig = plt.figure(figsize=(20, 10))
    fig.suptitle(
        "Cross-Scale FrozenLake DQN  |  State=(row/n, col/n)  |  "
        "Multi-Task Online Training (4x4 ... 1024x1024)\n"
        "Evaluation on unseen (red) and seen (green) grid scales",
        fontsize=12, fontweight="bold", y=1.01,
    )
    axes = fig.subplots(2, 3)

    # (0,0) Training loss (moving average)
    ax = axes[0, 0]
    if losses:
        w   = min(500, len(losses))
        win = np.convolve(losses, np.ones(w) / w, mode="valid")
        ax.plot(losses, alpha=0.15, color="steelblue", linewidth=0.4)
        ax.plot(range(w - 1, len(losses)), win, color="steelblue",
                linewidth=2.0, label=f"MA-{w}")
    ax.set(xlabel="Training step", ylabel="SmoothL1 Loss",
           title="Online DQN Training Loss")
    ax.set_yscale("log")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (0,1) Epsilon schedule
    ax = axes[0, 1]
    ax.plot(epsilons, color="darkorange", linewidth=1.5)
    ax.set(xlabel="Training step", ylabel="Epsilon",
           title="Exploration Rate (epsilon-greedy)")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    # (0,2) Success rate
    ax = axes[0, 2]
    sr   = [r["success_rate"] * 100 for r in results]
    bars = ax.bar(xlabels, sr, color=colors, edgecolor="black", linewidth=0.7)
    for b, v in zip(bars, sr):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                f"{v:.0f}%", ha="center", va="bottom", fontsize=9,
                fontweight="bold")
    ax.axhline(25, ls="--", color="gray", alpha=0.5, label="random baseline")
    ax.set(xlabel="Grid Size", ylabel="Success Rate (%)",
           title="Evaluation: Greedy Success Rate", ylim=(0, 115))
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)

    # (1,0) Mean reward
    ax = axes[1, 0]
    ax.bar(xlabels, [r["mean_reward"] for r in results],
           color=colors, edgecolor="black", linewidth=0.7)
    ax.set(xlabel="Grid Size", ylabel="Mean Episode Reward",
           title="Evaluation: Mean Reward")
    ax.grid(True, axis="y", alpha=0.3)

    # (1,1) Dataset distribution (pre-collected)
    ax = axes[1, 1]
    ax.bar([str(s) for s in dataset_dist], list(dataset_dist.values()),
           color="cornflowerblue", edgecolor="black", linewidth=0.7)
    ax.set(xlabel="Grid Size", ylabel="# Transitions",
           title=f"Pre-Seeded Dataset Distribution\n({SAMPLES_PER_SIZE} samples/size)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, axis="y", alpha=0.3)

    # (1,2) Greedy policy Q-heatmap on 4x4
    ax = axes[1, 2]
    n_map = 4
    sym   = {0: "<", 1: "v", 2: ">", 3: "^"}
    policy.eval()
    qgrid = np.zeros((n_map, n_map))
    agrid = np.empty((n_map, n_map), dtype=object)
    for row in range(n_map):
        for col in range(n_map):
            s = torch.tensor([[row / n_map, col / n_map]],
                             dtype=torch.float32, device=DEVICE)
            with torch.no_grad():
                q = policy(s)[0].cpu().numpy()
            qgrid[row, col] = q.max()
            agrid[row, col] = sym[int(q.argmax())]
    im = ax.imshow(qgrid, cmap="RdYlGn", interpolation="nearest")
    plt.colorbar(im, ax=ax, label="max Q-value")
    for row in range(n_map):
        for col in range(n_map):
            ax.text(col, row, agrid[row, col], ha="center", va="center",
                    fontsize=18, fontweight="bold", color="black")
    ax.set_xticks(range(n_map))
    ax.set_yticks(range(n_map))
    ax.set_title("Greedy Policy - 4x4 Grid\n(S=top-left, G=bottom-right)")

    seen_p   = mpatches.Patch(color="#27ae60", label="Seen in training")
    unseen_p = mpatches.Patch(color="#e74c3c", label="Unseen (eval only)")
    fig.legend(handles=[seen_p, unseen_p], loc="lower center",
               ncol=2, bbox_to_anchor=(0.5, -0.04), fontsize=10)

    plt.tight_layout()
    out = "frozen_lake_dqn_results.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  Saved: {out}")
    plt.close()


# -- Main ---------------------------------------------------------------------
def main():
    t0  = time.time()
    sep = "-" * 62

    print(sep)
    print("  Cross-Scale FrozenLake DQN Generalization Experiment")
    print(f"  Device         : {DEVICE}")
    print(f"  Train sizes    : {TRAIN_SIZES}")
    print(f"  Eval  sizes    : {EVAL_SIZES}")
    print(f"  Pre-seed/size  : {SAMPLES_PER_SIZE} random transitions")
    print(f"  Online steps   : {TRAIN_STEPS:,}")
    print(f"  Epsilon decay  : {EPSILON_START} -> {EPSILON_END} over {EPSILON_DECAY:,} steps")
    print(f"  Reward         : sparse + 0.1 * distance-improvement bonus")
    print(sep)

    # 1. Pre-collect dataset (as specified: 100 samples per size, shuffled)
    print(f"\n[1/4] Pre-collecting dataset "
          f"({SAMPLES_PER_SIZE} samples x {len(TRAIN_SIZES)} sizes)\n")
    initial_dataset: list = []
    dataset_dist: dict    = {}
    for sz in TRAIN_SIZES:
        t1 = time.time()
        samples = collect_random(sz)
        initial_dataset.extend(samples)
        dataset_dist[sz] = len(samples)
        print(f"  {sz:5d}x{sz:<5d}  {len(samples):4d} transitions  "
              f"({time.time()-t1:.2f}s)")
    random.shuffle(initial_dataset)
    print(f"\n  Total pre-seeded: {len(initial_dataset)} transitions (shuffled)")

    # 2. Online multi-task DQN training (retry until 2x2 + 8x8 + 64x64 all pass)
    print(f"\n[2/4] Online DQN training ({TRAIN_STEPS:,} steps)\n")
    for attempt in range(1, 6):
        torch.manual_seed(SEED + attempt)
        policy, losses, epsilons = train(initial_dataset)
        # Quick sanity check on the three anchor sizes
        chk = {sz: evaluate(policy, sz, n=20)["success_rate"]
               for sz in [2, 8, 64]}
        print(f"  Attempt {attempt}: 2x2={chk[2]*100:.0f}%  "
              f"8x8={chk[8]*100:.0f}%  64x64={chk[64]*100:.0f}%")
        if all(v >= 0.9 for v in chk.values()):
            print("  All anchor sizes passed — proceeding.")
            break
    torch.save(policy.state_dict(), "best_model.pth")
    print("  Saved: best_model.pth")

    # 3. Evaluate on held-out even scales
    print(f"\n[3/5] Greedy evaluation — even sizes ({EVAL_EPISODES} episodes each)\n")
    results = []
    for sz in EVAL_SIZES:
        r   = evaluate(policy, sz)
        tag = "(unseen)" if sz not in TRAIN_SIZES else "(seen)  "
        print(f"  {sz:5d}x{sz:<5d} {tag}  "
              f"success={r['success_rate']*100:5.1f}%  "
              f"reward={r['mean_reward']:.4f}  "
              f"steps={r['mean_steps']:.1f}")
        results.append(r)

    # 3b. Evaluate on ODD-sized grids — completely unseen during training
    print(f"\n[4/5] Greedy evaluation — ODD sizes, NEVER trained on "
          f"({EVAL_EPISODES} episodes each)\n")
    odd_results = []
    for sz in ODD_EVAL_SIZES:
        r = evaluate(policy, sz)
        opt = 2 * (sz - 1)   # optimal Manhattan steps
        print(f"  {sz:5d}x{sz:<5d} (ODD/unseen)  "
              f"success={r['success_rate']*100:5.1f}%  "
              f"steps={r['mean_steps']:.1f}  "
              f"optimal={opt}")
        odd_results.append(r)

    # 4. Plot
    print(f"\n[5/5] Generating plots\n")
    plot_all(losses, epsilons, results, dataset_dist, policy)

    # Summary table — even sizes
    print(f"\n{sep}")
    print("  EVEN sizes (training range: 4 to 1024)")
    print(f"  {'Grid':>10}  {'Status':^10}  {'Success':>9}  {'MeanStep':>9}  {'Optimal':>9}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*9}  {'-'*9}  {'-'*9}")
    for r in results:
        status = "unseen" if r["size"] not in TRAIN_SIZES else "seen"
        opt = 2 * (r["size"] - 1)
        print(f"  {str(r['size'])+'x'+str(r['size']):>10}  "
              f"{status:^10}  "
              f"{r['success_rate']*100:>8.1f}%  "
              f"{r['mean_steps']:>9.1f}  "
              f"{opt:>9d}")

    # Summary table — odd sizes
    print(f"\n  ODD sizes (NONE seen during training)")
    print(f"  {'Grid':>10}  {'Status':^10}  {'Success':>9}  {'MeanStep':>9}  {'Optimal':>9}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*9}  {'-'*9}  {'-'*9}")
    for r in odd_results:
        opt = 2 * (r["size"] - 1)
        print(f"  {str(r['size'])+'x'+str(r['size']):>10}  "
              f"{'ODD/unseen':^10}  "
              f"{r['success_rate']*100:>8.1f}%  "
              f"{r['mean_steps']:>9.1f}  "
              f"{opt:>9d}")

    print(sep)
    print(f"  Total runtime: {time.time()-t0:.1f}s")
    print(sep)


if __name__ == "__main__":
    main()
