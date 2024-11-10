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

    def train_step(self, state: List[bool], action: List[int], reward: float, 
                  next_state: List[bool], done: bool) -> None:
        # Convert to tensors
        state = torch.FloatTensor(np.array(state))
        next_state = torch.FloatTensor(np.array(next_state))
        action = torch.FloatTensor(np.array(action))
        
        if len(state.shape) == 1:  # Single sample
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = torch.FloatTensor([reward])
            done = (done,)
        else:  # Multiple samples
            reward = torch.FloatTensor(reward)

        # Predicted Q values with current state
        pred = self.model(state)

        # Q_new = reward + gamma * max(Q(next_state)) -> only do this if not done
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(
                    self.model(next_state[idx].unsqueeze(0)))
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # Train
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()