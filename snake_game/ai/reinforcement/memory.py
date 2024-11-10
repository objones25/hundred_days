# memory.py
from collections import deque
import random
import numpy as np
from typing import List, Tuple

class ReplayMemory:
    """Experience replay memory for storing and sampling transitions"""
    def __init__(self, capacity: int):
        """Initialize replay memory with given capacity"""
        self.memory = deque(maxlen=capacity)
        
    def push(self, state: List[bool], action: List[int], 
             reward: float, next_state: List[bool], done: bool) -> None:
        """Store a transition"""
        self.memory.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size: int) -> Tuple:
        """Sample a random batch of transitions"""
        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states), 
            np.array(actions), 
            np.array(rewards), 
            np.array(next_states), 
            np.array(dones)
        )
        
    def __len__(self) -> int:
        """Return current size of memory"""
        return len(self.memory)

    # Alias append to push for compatibility
    append = push