from enum import Enum

class GameState(Enum):
    TITLE = 1
    DIFFICULTY = 2  # Added DIFFICULTY state
    GAME_SINGLE = 3
    GAME_MULTI = 4
    PAUSE = 5
    GAME_OVER = 6

class Difficulty(Enum):
    EASY = 0.3
    MEDIUM = 0.5
    HARD = 0.7
    EXPERT = 0.9