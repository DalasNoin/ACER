# -*- coding: utf-8 -*-
from torch import nn
from torch.nn import functional as F
from gym.spaces import box


class ActorCritic(nn.Module):
  def __init__(self, observation_space, action_space, hidden_size):
    super(ActorCritic, self).__init__()
    self.state_size = observation_space.shape[0]
    if isinstance(action_space, box.Box):
        action_shape = action_space.shape
        if len(action_shape)==1:
            self.action_size=action_shape[0]
    else:   
        self.action_size = action_space.n

    self.fc1 = nn.Linear(self.state_size, hidden_size)
    self.lstm = nn.LSTMCell(hidden_size, hidden_size)
    self.fc_actor = nn.Linear(hidden_size, self.action_size)
    self.fc_critic = nn.Linear(hidden_size, self.action_size)

  def forward(self, x, h):
    x = F.relu(self.fc1(x))
    h = self.lstm(x, h)  # h is (hidden state, cell state)
    x = h[0]
    policy = F.softmax(self.fc_actor(x), dim=1).clamp(max=1 - 1e-20)  # Prevent 1s and hence NaNs
    Q = self.fc_critic(x)
    V = (Q * policy).sum(1, keepdim=True)  # V is expectation of Q under π
    return policy, Q, V, h
