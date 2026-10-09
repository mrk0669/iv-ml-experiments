import os
import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

FOLDER    = os.path.dirname(os.path.abspath(__file__))
PLOT_PATH = os.path.join(FOLDER, "a2c_reward_plot.png")

env = gym.make("CartPole-v1")

class MyNet(nn.Module):
    def __init__(self):
        super(MyNet, self).__init__()
        self.layer1 = nn.Linear(4, 128)
        self.layer2 = nn.Linear(128, 128)
        self.actor_out  = nn.Linear(128, 2)
        self.critic_out = nn.Linear(128, 1)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        probs = torch.softmax(self.actor_out(x), dim=-1)
        val   = self.critic_out(x)
        return probs, val

model     = MyNet()
optimizer = optim.Adam(model.parameters(), lr=0.001)
gamma     = 0.99
all_scores = []

for ep in range(1, 601):
    state, _ = env.reset()
    done = False
    saved_log_probs = []
    saved_values    = []
    rewards_list    = []

    while not done:
        state_t      = torch.FloatTensor(state)
        probs, value = model(state_t)
        dist         = torch.distributions.Categorical(probs)
        action       = dist.sample()

        saved_log_probs.append(dist.log_prob(action))
        saved_values.append(value)

        next_state, reward, terminated, truncated, _ = env.step(action.item())
        rewards_list.append(reward)
        state = next_state
        done  = terminated or truncated

    G       = 0
    returns = []
    for r in reversed(rewards_list):
        G = r + gamma * G
        returns.insert(0, G)

    actor_loss  = 0
    critic_loss = 0
    for lp, val, ret in zip(saved_log_probs, saved_values, returns):
        ret_t        = torch.tensor([ret])
        adv          = ret_t - val.detach()
        actor_loss  += -lp * adv
        critic_loss += (ret_t - val) ** 2

    loss = actor_loss + 0.5 * critic_loss
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    score = sum(rewards_list)
    all_scores.append(score)
    print(f"Ep {ep:4d} | score {score:6.1f}")

env.close()
print("\nDone training.")

plt.figure(figsize=(8, 5))
plt.plot(all_scores, color="steelblue", linewidth=0.9)
plt.title("A2C CartPole - Reward vs Episode (600 episodes)")
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=150)
print(f"Plot saved -> {PLOT_PATH}")
plt.show()
