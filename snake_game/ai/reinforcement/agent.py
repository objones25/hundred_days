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
from .memory import ReplayMemory

class RLAgent(SnakeAI):
    """Reinforcement Learning agent using Deep Q-Learning"""
    
    def __init__(self, game):
        super().__init__(game)
        self.config = RLConfig()
        self.n_games = 0
        self.epsilon = self.config.EPSILON_START
        self.memory = ReplayMemory(self.config.MAX_MEMORY)
        self.model = SnakeNN(input_size=11, hidden_size=256, output_size=3)
        self.trainer = QTrainer(
            self.model,
            learning_rate=self.config.LEARNING_RATE,
            gamma=self.config.GAMMA
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
            'rewards': []
        }
        self.current_reward = 0
        self.record = 0
        
        # Load previous training data if it exists
        self.load_training_stats()

    def get_next_move(self) -> List[int]:
        """Get the next action based on current state"""
        state = self.get_state()
        return self._get_action(state)

    def remember(self, state: List[bool], action: List[int], reward: float, 
                next_state: List[bool], done: bool) -> None:
        """Store experience in memory"""
        self.memory.push(state, action, reward, next_state, done)
        self.current_reward += reward
        
        if self.config.DEBUG:
            self.config.logger.debug(f"Stored experience - Memory size: {len(self.memory)}")
            self.config.logger.debug(f"Action: {action}, Reward: {reward}, Done: {done}")

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
        """Train on a batch of experiences"""
        if len(self.memory) < self.config.BATCH_SIZE:
            if self.config.DEBUG:
                self.config.logger.debug(f"Skipping long memory training - insufficient memories: {len(self.memory)}/{self.config.BATCH_SIZE}")
            return
            
        states, actions, rewards, next_states, dones = self.memory.sample(self.config.BATCH_SIZE)
        
        self.trainer.train_step(
            torch.FloatTensor(states),
            torch.FloatTensor(actions),
            torch.FloatTensor(rewards),
            torch.FloatTensor(next_states),
            torch.BoolTensor(dones)
        )
        
        if self.config.DEBUG:
            self.config.logger.debug(f"Completed long memory training with batch size: {self.config.BATCH_SIZE}")
    
    def update_training_stats(self, score: int):
        """Update and save training statistics"""
        self.n_games += 1
        self.scores.append(score)
        mean_score = sum(self.scores) / len(self.scores)
        self.mean_scores.append(mean_score)
        
        if score > self.record:
            self.record = score
            self.model.save(f'model_record_{score}.pth')
        
        # Update training stats
        self.training_stats['episodes'].append(self.n_games)
        self.training_stats['scores'].append(score)
        self.training_stats['mean_scores'].append(mean_score)
        self.training_stats['epsilons'].append(self.epsilon)
        self.training_stats['memory_size'].append(len(self.memory))
        self.training_stats['rewards'].append(self.current_reward)
        
        # Reset current reward for next episode
        self.current_reward = 0
        
        # Log progress
        if self.n_games % self.config.LOG_INTERVAL == 0:
            self.config.logger.info(
                f"Game {self.n_games}, Score {score}, Record {self.record}, "
                f"Epsilon {self.epsilon:.3f}, Memory {len(self.memory)}"
            )
            self.save_training_stats()
    
    def save_training_stats(self):
        """Save training statistics to file"""
        stats_dir = 'training_stats'
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir)
            
        filename = os.path.join(stats_dir, 'training_stats.json')
        with open(filename, 'w') as f:
            json.dump(self.training_stats, f)
    
    def load_training_stats(self):
        """Load training statistics from file"""
        filename = os.path.join('training_stats', 'training_stats.json')
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.training_stats = json.load(f)
                
            # Restore the latest game count and record
            if self.training_stats['episodes']:
                self.n_games = self.training_stats['episodes'][-1]
                self.record = max(self.training_stats['scores'])
                
                if self.config.DEBUG:
                    self.config.logger.info(f"Loaded previous training stats - Games: {self.n_games}, Record: {self.record}")

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