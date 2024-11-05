from enum import Enum
from dataclasses import dataclass

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class GameState(Enum):
    TITLE = 1
    PLAYING = 2
    PAUSED = 3  # New state
    GAME_OVER = 4
    SETTINGS = 5
    AI_MENU = 6

@dataclass
class GameSettings:
    WINDOW_SIZE: int = 600
    GRID_SIZE: int = 20
    INITIAL_SPEED: int = 10
    MAX_SPEED: int = 20
    MIN_SPEED: int = 5