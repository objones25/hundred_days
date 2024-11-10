# config.py
import logging
from dataclasses import dataclass

@dataclass
class RLConfig:
    """Configuration for reinforcement learning parameters"""
    # Training hyperparameters
    LEARNING_RATE: float = 0.001
    BATCH_SIZE: int = 64  # Reduced from 1000 for more frequent updates
    GAMMA: float = 0.9  # Discount rate
    
    # Memory settings
    MAX_MEMORY: int = 100_000
    
    # Exploration settings
    EPSILON_START: float = 1.0
    EPSILON_END: float = 0.01
    EPSILON_DECAY: float = 0.995
    
    # Rewards
    REWARD_EAT: float = 10.0
    REWARD_DEATH: float = -10.0
    REWARD_CLOSER: float = 1.0
    REWARD_FARTHER: float = -1.0
    
    # Debug settings
    DEBUG: bool = True
    LOG_INTERVAL: int = 10  # Log stats every N games
    
    def __post_init__(self):
        self.logger = logging.getLogger('RLAgent')
        if self.DEBUG:
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)