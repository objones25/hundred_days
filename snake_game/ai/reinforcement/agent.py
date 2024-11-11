import torch
import random
import numpy as np
import pygame
from typing import List, Optional, Tuple, Dict
from collections import deque
import json
import os
from datetime import datetime

from core.constants import Direction
from ..base import SnakeAI
from .model import SnakeNN
from .config import RLConfig
from .trainer import QTrainer
from .memory import PrioritizedReplayMemory
from utils.persistence import SaveLoadManager

class RLAgent(SnakeAI):
    def __init__(self, game):
        super().__init__(game)
        self.config = RLConfig()
        self.n_games = 0
        self.epsilon = self.config.EPSILON_START
        
        # Initialize model and trainer
        self.model = SnakeNN(input_size=11, hidden_size=256, output_size=3)
        self.trainer = QTrainer(
            self.model,
            learning_rate=self.config.LEARNING_RATE,
            gamma=self.config.GAMMA
        )
        
        # Initialize prioritized replay memory
        self.memory = PrioritizedReplayMemory(
            capacity=self.config.MAX_MEMORY,
            alpha=0.6,
            beta_start=0.4
        )
        
        # Training metrics
        self.scores = []
        self.mean_scores = []
        self.training_stats = {
            'episodes': [],
            'scores': [],
            'mean_scores': [],
            'epsilons': [],
            'memory_size': [],
            'rewards': [],
            'memory_utilization': [],
            'avg_priorities': []
        }
        self.current_reward = 0
        self.record = 0
        
        # Initialize save/load manager
        self.save_load_manager = SaveLoadManager(max_saves=5)
        
        # Load previous training state if available
        self.load_training_state()

    def get_next_move(self) -> Direction:
        """Get the next move based on current state"""
        state = self.get_state()
        action = self._get_action(state)
        return self._action_to_direction(action)

    def remember(self, state: List[bool], action: List[int], reward: float, 
                next_state: List[bool], done: bool) -> None:
        """Store experience in memory with memory management"""
        self.memory.push(state, action, reward, next_state, done)
        self.current_reward += reward
        
        # Log memory stats periodically
        if len(self.memory) % 1000 == 0:  # Adjust logging frequency as needed
            stats = self.memory.get_stats()
            self.config.logger.debug(
                f"Memory stats - Size: {stats['size']}, "
                f"Capacity: {stats['capacity']}, "
                f"Utilization: {stats['utilization']:.1f}%"
            )

    def train_short_memory(self, state, action, reward, next_state, done):
        """Train the agent on a single step"""
        self.trainer.train_step(
            torch.FloatTensor(state).unsqueeze(0),
            torch.FloatTensor(action).unsqueeze(0),
            torch.FloatTensor([reward]),
            torch.FloatTensor(next_state).unsqueeze(0),
            torch.BoolTensor([done])
        )
        
        if self.config.DEBUG:
            self.config.logger.debug("Completed short memory training step")

    def train_long_memory(self):
        """Train on a batch of experiences using prioritized replay"""
        if len(self.memory) < self.config.BATCH_SIZE:
            return
            
        # Sample batch with priorities and importance sampling weights
        states, actions, rewards, next_states, dones, indices, weights = self.memory.sample(self.config.BATCH_SIZE)
        
        # Convert to tensors
        states = torch.FloatTensor(states)
        next_states = torch.FloatTensor(next_states)
        actions = torch.FloatTensor(actions)
        rewards = torch.FloatTensor(rewards)
        dones = torch.BoolTensor(dones)
        weights = torch.FloatTensor(weights)
        
        # Calculate TD errors
        current_q_values = self.model(states)
        next_q_values = self.model(next_states)
        target_q_values = current_q_values.clone()
        
        for idx in range(len(dones)):
            Q_new = rewards[idx]
            if not dones[idx]:
                Q_new = rewards[idx] + self.config.GAMMA * torch.max(next_q_values[idx])
            target_q_values[idx][torch.argmax(actions[idx]).item()] = Q_new
        
        # Calculate loss with importance sampling weights
        td_errors = torch.abs(target_q_values - current_q_values).mean(dim=1).detach().numpy()
        
        # Update priorities in memory
        self.memory.update_priorities(indices, td_errors)
        
        # Train with weighted loss
        self.trainer.train_step(states, actions, rewards, next_states, dones, weights)
    
    def update_training_stats(self, score: int):
        """Update training statistics with enhanced memory metrics"""
        super().update_training_stats(score)
        
        # Add memory-specific stats
        memory_stats = self.memory.get_stats()
        self.training_stats['memory_utilization'].append(memory_stats['utilization'])
        self.training_stats['avg_priorities'].append(memory_stats['avg_priority'])
        
        # Save state periodically
        if self.n_games % 100 == 0:  # Adjust saving frequency as needed
            self.save_training_state()

    def update_training_stats(self, score: int):
        """Update training statistics with enhanced memory metrics"""
        self.n_games += 1
        self.scores.append(score)
        mean_score = sum(self.scores) / len(self.scores)
        self.mean_scores.append(mean_score)
        
        if score > self.record:
            self.record = score
            self.model.save(f'model_record_{score}.pth')
        
        # Get memory stats
        memory_stats = self.memory.get_stats()
        
        # Update training stats
        self.training_stats['episodes'].append(self.n_games)
        self.training_stats['scores'].append(score)
        self.training_stats['mean_scores'].append(mean_score)
        self.training_stats['epsilons'].append(self.epsilon)
        self.training_stats['memory_size'].append(memory_stats['size'])
        self.training_stats['rewards'].append(self.current_reward)
        self.training_stats['memory_utilization'].append(memory_stats['utilization'])
        self.training_stats['avg_priorities'].append(memory_stats['avg_priority'])
        
        # Reset current reward for next episode
        self.current_reward = 0
        
        # Log progress
        if self.n_games % self.config.LOG_INTERVAL == 0:
            self.config.logger.info(
                f"Game {self.n_games}, Score {score}, Record {self.record}, "
                f"Epsilon {self.epsilon:.3f}, Memory {memory_stats['size']}/{memory_stats['capacity']} "
                f"({memory_stats['utilization']:.1f}% full)"
            )
            self.save_training_state()
            
    def save_training_state(self, force=False):
        """Save current training state"""
        self.save_load_manager.save_state(self, force)
    
    def load_training_state(self):
        """Load most recent training state"""
        return self.save_load_manager.load_latest_state(self)
    
    def load_best_model(self):
        """Load the best performing model"""
        return self.save_load_manager.load_best_model(self)

    def _get_action(self, state: List[bool]) -> List[int]:
        """Choose action using epsilon-greedy strategy"""
        # Random moves: tradeoff exploration / exploitation
        self.epsilon = max(self.config.EPSILON_END, 
                         self.epsilon * self.config.EPSILON_DECAY)
        
        final_move = [0, 0, 0]  # [straight, right, left]
        
        if random.random() < self.epsilon:
            # Exploration: random action
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            # Exploitation: predicted action
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            prediction = self.model(state_tensor)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            
        return final_move

    def _action_to_direction(self, action: List[int]) -> Direction:
        """Convert action array to Direction enum"""
        # Get current direction index
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.game.snake_direction)
        
        # [1,0,0] -> straight, [0,1,0] -> right turn, [0,0,1] -> left turn
        if np.array_equal(action, [1, 0, 0]):
            new_direction = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_direction = clock_wise[next_idx]  # right turn
        else:  # [0,0,1]
            next_idx = (idx - 1) % 4
            new_direction = clock_wise[next_idx]  # left turn
            
        return new_direction

    def draw_debug_info(self, screen) -> None:
        """Draw AI debug visualization with enhanced information"""
        # Draw state information
        state = self.get_state()
        font = pygame.font.Font(None, 24)
        
        # Draw danger indicators
        if state[0]:  # Danger straight
            pygame.draw.circle(screen, (255,0,0), (20, 20), 5)
        if state[1]:  # Danger right
            pygame.draw.circle(screen, (255,0,0), (30, 20), 5)
        if state[2]:  # Danger left
            pygame.draw.circle(screen, (255,0,0), (10, 20), 5)
            
        # Enhanced debug information
        y_pos = 40
        texts = [
            f'ε: {self.epsilon:.3f}',
            f'Games: {self.n_games}',
            f'Record: {self.record}',
            f'Memory: {len(self.memory)}/{self.config.MAX_MEMORY}',
            f'Batch: {self.config.BATCH_SIZE}',
            f'Current Reward: {self.current_reward:.1f}'
        ]
        
        for text in texts:
            text_surface = font.render(text, True, (255,255,255))
            screen.blit(text_surface, (10, y_pos))
            y_pos += 20