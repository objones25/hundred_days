# memory.py
import random
import numpy as np
from typing import List, Tuple
import heapq

class PrioritizedReplayMemory:
    """Experience replay memory with prioritized sampling"""
    
    def __init__(self, capacity: int, alpha: float = 0.6, beta_start: float = 0.4):
        self.capacity = capacity
        self.memory = []  # List of (priority, experience) tuples
        self.priorities = []  # Separate list for quick priority updates
        self.position = 0
        self.alpha = alpha
        self.beta = beta_start
        self.beta_increment = 0.001
        self.epsilon = 1e-6
        
        # Stats
        self.total_added = 0
        self.priority_sum = 0
    
    def push(self, state: List[bool], action: List[int], 
             reward: float, next_state: List[bool], done: bool) -> None:
        """Store a transition with maximum priority for new experiences"""
        max_priority = max(self.priorities) if self.priorities else 1.0
        
        experience = (state, action, reward, next_state, done)
        
        if len(self.memory) < self.capacity:
            self.memory.append((max_priority, experience))
            self.priorities.append(max_priority)
        else:
            # Replace oldest experience
            idx = self.position % self.capacity
            self.memory[idx] = (max_priority, experience)
            self.priorities[idx] = max_priority
        
        self.position = (self.position + 1) % self.capacity
        self.total_added += 1
        self.priority_sum = sum(self.priorities)
    
    def sample(self, batch_size: int) -> Tuple:
        """Sample a batch of experiences based on their priorities"""
        if batch_size > len(self.memory):
            batch_size = len(self.memory)
        
        # Calculate sampling probabilities
        probs = np.array(self.priorities) ** self.alpha
        probs /= probs.sum()
        
        # Sample indices based on priorities
        indices = np.random.choice(len(self.memory), batch_size, p=probs)
        
        # Calculate importance sampling weights
        self.beta = min(1.0, self.beta + self.beta_increment)
        weights = (len(self.memory) * probs[indices]) ** (-self.beta)
        weights /= weights.max()  # Normalize weights
        
        # Unpack experiences
        batch = [self.memory[idx][1] for idx in indices]
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states),
            np.array(actions),
            np.array(rewards),
            np.array(next_states),
            np.array(dones),
            indices,
            weights
        )
    
    def update_priorities(self, indices: List[int], td_errors: np.ndarray) -> None:
        """Update priorities based on TD errors"""
        for idx, td_error in zip(indices, td_errors):
            priority = (abs(td_error) + self.epsilon) ** self.alpha
            self.priorities[idx] = priority
            self.memory[idx] = (priority, self.memory[idx][1])
        
        self.priority_sum = sum(self.priorities)
    
    def get_top_experiences(self, n: int = 10) -> List:
        """Get the n most important experiences"""
        return heapq.nlargest(n, self.memory, key=lambda x: x[0])
    
    def __len__(self) -> int:
        return len(self.memory)
    
    def get_stats(self) -> dict:
        return {
            'size': len(self.memory),
            'capacity': self.capacity,
            'utilization': len(self.memory) / self.capacity * 100,
            'total_added': self.total_added,
            'avg_priority': self.priority_sum / len(self.memory) if self.memory else 0,
            'beta': self.beta
        }
    
    append = push  # Alias for compatibility