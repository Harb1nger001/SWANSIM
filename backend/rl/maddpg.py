import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*batch)
        return (
            torch.FloatTensor(np.array(state)),
            torch.FloatTensor(np.array(action)),
            torch.FloatTensor(np.array(reward)).unsqueeze(1),
            torch.FloatTensor(np.array(next_state)),
            torch.FloatTensor(np.array(done)).unsqueeze(1)
        )

    def __len__(self):
        return len(self.buffer)

class Actor(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super(Actor, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, act_dim),
            nn.Sigmoid() # Output 0-1 for normalized action space
        )
        
    def forward(self, x):
        return self.net(x)

class Critic(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super(Critic, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim + act_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, obs, act):
        return self.net(torch.cat([obs, act], dim=1))

class MADDPG:
    def __init__(self, obs_dim, act_dim, config):
        self.gamma = config.get("rl", {}).get("gamma", 0.99)
        self.tau = config.get("rl", {}).get("tau", 0.01)
        self.batch_size = config.get("rl", {}).get("batch_size", 64)
        lr_actor = config.get("rl", {}).get("lr_actor", 0.001)
        lr_critic = config.get("rl", {}).get("lr_critic", 0.002)

        # Single Agent (Government) but structured for MADDPG expansion
        self.actor = Actor(obs_dim, act_dim)
        self.target_actor = Actor(obs_dim, act_dim)
        self.target_actor.load_state_dict(self.actor.state_dict())
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr_actor)

        self.critic = Critic(obs_dim, act_dim)
        self.target_critic = Critic(obs_dim, act_dim)
        self.target_critic.load_state_dict(self.critic.state_dict())
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr_critic)

        self.memory = ReplayBuffer(100000)

    def select_action(self, state, noise=0.0):
        state = torch.FloatTensor(state).unsqueeze(0)
        action = self.actor(state).detach().numpy()[0]
        if noise > 0:
            action += noise * np.random.randn(len(action))
        return np.clip(action, 0.0, 1.0)

    def update(self):
        if len(self.memory) < self.batch_size:
            return

        state, action, reward, next_state, done = self.memory.sample(self.batch_size)

        # ----------------------------
        # Update Critic
        # ----------------------------
        with torch.no_grad():
            next_action = self.target_actor(next_state)
            target_q = self.target_critic(next_state, next_action)
            y = reward + (1 - done) * self.gamma * target_q
        
        q_value = self.critic(state, action)
        critic_loss = nn.MSELoss()(q_value, y)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # ----------------------------
        # Update Actor
        # ----------------------------
        # Maximize Q(s, a)
        actor_loss = -self.critic(state, self.actor(state)).mean()

        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # ----------------------------
        # Update Target Networks
        # ----------------------------
        for target_param, param in zip(self.target_actor.parameters(), self.actor.parameters()):
            target_param.data.copy_(target_param.data * (1.0 - self.tau) + param.data * self.tau)
            
        for target_param, param in zip(self.target_critic.parameters(), self.critic.parameters()):
            target_param.data.copy_(target_param.data * (1.0 - self.tau) + param.data * self.tau)
