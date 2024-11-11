import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple

class QTrainer:
    def __init__(self, model: nn.Module, learning_rate: float, gamma: float):
        self.model = model
        self.lr = learning_rate
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state: torch.Tensor, action: torch.Tensor, 
                  reward: torch.Tensor, next_state: torch.Tensor, done: torch.Tensor,
                  weights: torch.Tensor = None):
        """
        Train the model with optional importance sampling weights
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
            weights: Optional importance sampling weights for prioritized replay
        """
        # Get predicted Q values for current state
        pred = self.model(state)

        # Calculate target Q values
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            target[idx][torch.argmax(action[idx])] = Q_new

        # Calculate weighted loss if weights provided
        self.optimizer.zero_grad()
        if weights is not None:
            loss = (weights * self.criterion(target, pred)).mean()
        else:
            loss = self.criterion(target, pred)
            
        loss.backward()
        self.optimizer.step()