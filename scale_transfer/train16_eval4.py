#!/usr/bin/env python3
"""
Scale-Transfer Experiment
--------------------------
Train ONLY on 16x16 FrozenLake.
Deploy (zero-shot) on 4x4 FrozenLake.

State encoding: ((n-1-row)/n, (n-1-col)/n)  — goal always at (0,0)
This makes the Q-function grid-size-agnostic.
"""

import random, time
import numpy as np
import torch, torch.nn as nn, torch.optim as optim
import gymnasium as gym
from gymnasium.envs.toy_text.frozen_lake import generate_random_map
from collections import deque
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- Config ------------------------------------------------------------------
SEED          = 42
TRAIN_SIZE    = 16
EVAL_SIZE     = 4
TRAIN_STEPS   = 80_000
BUFFER_MAXLEN = 40_000
BATCH_SIZE    = 128
GAMMA         = 0.95
LR            = 3e-4
TARGET_UPDATE = 200
EPS_START     = 1.0
EPS_END       = 0.10
EPS_DECAY     = 60_000
EVAL_EPISODES = 200
MAX_STEPS_EVAL= 500

random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---- Maps (hole-free, p=1.0) -------------------------------------------------
_MAP_CACHE: dict = {}

def _get_map(size: int):
    if size not in _MAP_CACHE:
        if size == 2:
            _MAP_CACHE[size] = ["SF", "FG"]
        else:
            _MAP_CACHE[size] = generate_random_map(size=size, p=1.0,
                                                    seed=SEED + size)
    return _MAP_CACHE[size]

# ---- Helpers -----------------------------------------------------------------
def encode(obs: int, n: int) -> np.ndarray:
    row, col = obs // n, obs % n
    return np.array([(n-1-row)/n, (n-1-col)/n], dtype=np.float32)

def dist_reward(obs: int, nobs: int, n: int, r: float) -> float:
    old = abs(obs//n-(n-1)) + abs(obs%n-(n-1))
    new = abs(nobs//n-(n-1)) + abs(nobs%n-(n-1))
    mx  = 2.0*(n-1) if n > 1 else 1.0
    return r + 0.1*(old-new)/mx

def make_env(size: int, for_eval: bool = False) -> gym.Env:
    mult = 12 if for_eval else (8 if size >= 64 else 4)
    return gym.make("FrozenLake-v1",
                    desc=_get_map(size),
                    is_slippery=False,
                    max_episode_steps=max(200, mult*size))

# ---- DQN ---------------------------------------------------------------------
class DQN(nn.Module):
    def __init__(self, hidden=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 4),
        )
    def forward(self, x): return self.net(x)

# ---- Training (16x16 only) ---------------------------------------------------
def train():
    buf    = deque(maxlen=BUFFER_MAXLEN)
    env    = make_env(TRAIN_SIZE)
    obs, _ = env.reset(seed=SEED)

    policy = DQN().to(DEVICE)
    target = DQN().to(DEVICE)
    target.load_state_dict(policy.state_dict())
    target.eval()

    opt     = optim.Adam(policy.parameters(), lr=LR, weight_decay=1e-5)
    loss_fn = nn.SmoothL1Loss()
    losses  = []

    def eps_at(s):
        return EPS_START + min(s/EPS_DECAY, 1.0)*(EPS_END-EPS_START)

    print(f"  Training on {TRAIN_SIZE}x{TRAIN_SIZE} for {TRAIN_STEPS:,} steps ...")
    for step in range(1, TRAIN_STEPS+1):
        eps = eps_at(step)
        if random.random() < eps:
            a = env.action_space.sample()
        else:
            s = torch.tensor(encode(obs, TRAIN_SIZE),
                             dtype=torch.float32, device=DEVICE).unsqueeze(0)
            with torch.no_grad():
                a = policy(s).argmax(1).item()

        nobs, r, term, trunc, _ = env.step(a)
        done = term or trunc
        buf.append((encode(obs, TRAIN_SIZE), a,
                    dist_reward(obs, nobs, TRAIN_SIZE, r),
                    encode(nobs, TRAIN_SIZE), float(done)))
        obs = env.reset(seed=random.randint(0,999_999))[0] if done else nobs

        if len(buf) >= BATCH_SIZE:
            batch = random.sample(buf, BATCH_SIZE)
            S  = torch.tensor(np.array([d[0] for d in batch]),
                              dtype=torch.float32, device=DEVICE)
            A  = torch.tensor([d[1] for d in batch],
                              dtype=torch.long, device=DEVICE).unsqueeze(1)
            R  = torch.tensor([d[2] for d in batch],
                              dtype=torch.float32, device=DEVICE)
            NS = torch.tensor(np.array([d[3] for d in batch]),
                              dtype=torch.float32, device=DEVICE)
            D  = torch.tensor([d[4] for d in batch],
                              dtype=torch.float32, device=DEVICE)

            q = policy(S).gather(1, A).squeeze(1)
            with torch.no_grad():
                best_a   = policy(NS).argmax(1, keepdim=True)
                q_target = R + GAMMA*target(NS).gather(1,best_a).squeeze(1)*(1-D)
            loss = loss_fn(q, q_target)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
            opt.step()
            losses.append(loss.item())

        if step % TARGET_UPDATE == 0:
            target.load_state_dict(policy.state_dict())

        if step % 10_000 == 0 or step == 1:
            avg = np.mean(losses[-500:]) if losses else float("nan")
            print(f"  step {step:6d}/{TRAIN_STEPS}  eps={eps:.3f}  loss={avg:.5f}")

    env.close()
    return policy, losses

# ---- Evaluation --------------------------------------------------------------
def evaluate(model: DQN, size: int) -> dict:
    model.eval()
    env = make_env(size, for_eval=True)
    successes, steps_list = 0, []

    for ep in range(EVAL_EPISODES):
        obs, _ = env.reset(seed=2000+ep)
        visited: set = set()
        for step in range(MAX_STEPS_EVAL):
            if obs in visited: break
            visited.add(obs)
            s = torch.tensor(encode(obs, size),
                             dtype=torch.float32, device=DEVICE).unsqueeze(0)
            with torch.no_grad():
                a = model(s).argmax(1).item()
            obs, r, term, trunc, _ = env.step(a)
            if term or trunc:
                if r > 0: successes += 1
                break
        steps_list.append(step+1)

    env.close()
    return {"success_rate": successes/EVAL_EPISODES,
            "mean_steps":   float(np.mean(steps_list))}

# ---- Plotting ----------------------------------------------------------------
def plot(losses, res_train, res_eval):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(
        "Scale-Transfer: Train 16x16  ->  Deploy 4x4\n"
        "State = ((n-1-row)/n, (n-1-col)/n)  |  goal always at (0,0)",
        fontweight="bold"
    )

    # Loss curve
    ax = axes[0]
    if losses:
        w = min(500, len(losses))
        ma = np.convolve(losses, np.ones(w)/w, mode="valid")
        ax.plot(losses, alpha=0.15, color="steelblue", lw=0.5)
        ax.plot(range(w-1, len(losses)), ma, color="steelblue", lw=2)
    ax.set(xlabel="Step", ylabel="SmoothL1 Loss", title="Training Loss (16x16 only)")
    ax.set_yscale("log"); ax.grid(True, alpha=0.3)

    # Success rate bar
    ax = axes[1]
    labels = [f"{TRAIN_SIZE}x{TRAIN_SIZE}\n(trained)", f"{EVAL_SIZE}x{EVAL_SIZE}\n(unseen)"]
    colors = ["#27ae60", "#e74c3c"]
    rates  = [res_train["success_rate"]*100, res_eval["success_rate"]*100]
    bars   = ax.bar(labels, rates, color=colors, edgecolor="black", width=0.4)
    for b, v in zip(bars, rates):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+1.5,
                f"{v:.0f}%", ha="center", fontweight="bold", fontsize=14)
    ax.set(ylabel="Success Rate (%)", title="Zero-Shot Transfer Result", ylim=(0,120))
    ax.axhline(25, ls="--", color="gray", alpha=0.5, label="random baseline")
    ax.legend(fontsize=9); ax.grid(True, axis="y", alpha=0.3)

    # Q-value heatmap on 4x4
    ax = axes[2]
    sym = {0:"<", 1:"v", 2:">", 3:"^"}
    n   = EVAL_SIZE
    qg  = np.zeros((n, n)); ag = np.empty((n, n), dtype=object)
    for row in range(n):
        for col in range(n):
            s = torch.tensor([[(n-1-row)/n, (n-1-col)/n]],
                             dtype=torch.float32, device=DEVICE)
            with torch.no_grad():
                q = res_train["policy"](s)[0].cpu().numpy()
            qg[row,col] = q.max(); ag[row,col] = sym[int(q.argmax())]
    im = ax.imshow(qg, cmap="RdYlGn", interpolation="nearest")
    plt.colorbar(im, ax=ax, label="max Q")
    for row in range(n):
        for col in range(n):
            ax.text(col, row, ag[row,col], ha="center", va="center",
                    fontsize=20, fontweight="bold")
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_title(f"Policy on {EVAL_SIZE}x{EVAL_SIZE}\n(S=top-left, G=bot-right)")

    plt.tight_layout()
    plt.savefig("transfer_16to4.png", dpi=150, bbox_inches="tight")
    print("  Saved: transfer_16to4.png")
    plt.close()

# ---- Main --------------------------------------------------------------------
def main():
    t0  = time.time()
    sep = "-" * 55
    print(sep)
    print(f"  Scale-Transfer Experiment")
    print(f"  Train: {TRAIN_SIZE}x{TRAIN_SIZE}   Eval: {EVAL_SIZE}x{EVAL_SIZE}")
    print(f"  Device: {DEVICE}   Steps: {TRAIN_STEPS:,}")
    print(sep)

    policy, losses = train()
    torch.save(policy.state_dict(), "model_16to4.pth")
    print("  Saved: model_16to4.pth")

    print(f"\n  Evaluating on {TRAIN_SIZE}x{TRAIN_SIZE} (training grid) ...")
    res_train = evaluate(policy, TRAIN_SIZE)
    res_train["policy"] = policy

    print(f"  Evaluating on {EVAL_SIZE}x{EVAL_SIZE}  (UNSEEN smaller grid) ...")
    res_eval  = evaluate(policy, EVAL_SIZE)

    plot(losses, res_train, res_eval)

    print(f"\n{sep}")
    print(f"  RESULTS ({EVAL_EPISODES} episodes each)")
    print(f"  {sep}")
    print(f"  {TRAIN_SIZE}x{TRAIN_SIZE} (trained on)  : "
          f"success={res_train['success_rate']*100:.1f}%  "
          f"steps={res_train['mean_steps']:.1f}  "
          f"optimal={2*(TRAIN_SIZE-1)}")
    print(f"  {EVAL_SIZE}x{EVAL_SIZE}   (zero-shot)   : "
          f"success={res_eval['success_rate']*100:.1f}%  "
          f"steps={res_eval['mean_steps']:.1f}  "
          f"optimal={2*(EVAL_SIZE-1)}")
    print(f"{sep}")
    print(f"  Runtime: {time.time()-t0:.1f}s")
    print(sep)


if __name__ == "__main__":
    main()
