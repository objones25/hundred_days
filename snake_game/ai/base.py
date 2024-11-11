from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Tuple
from core.constants import Direction

class AIDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class SnakeAI(ABC):
    """Base class for all Snake AI implementations"""
    
    def __init__(self, game):
        self.game = game
        self.current_path = []
    
    @abstractmethod
    def get_next_move(self) -> Optional[Direction]:
        """Get the next move for the snake"""
        pass

    def get_state(self) -> List[bool]:
        """Get the current state of the game environment"""
        head = self.game.snake_pos[0]
        grid_size = self.game.settings.GRID_SIZE
        
        # Points around the head
        point_l = (head[0] - grid_size, head[1])
        point_r = (head[0] + grid_size, head[1])
        point_u = (head[0], head[1] - grid_size)
        point_d = (head[0], head[1] + grid_size)

        # Current direction
        dir_l = self.game.snake_direction == Direction.LEFT
        dir_r = self.game.snake_direction == Direction.RIGHT
        dir_u = self.game.snake_direction == Direction.UP
        dir_d = self.game.snake_direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and self._is_collision(point_r)) or
            (dir_l and self._is_collision(point_l)) or
            (dir_u and self._is_collision(point_u)) or
            (dir_d and self._is_collision(point_d)),

            # Danger right
            (dir_u and self._is_collision(point_r)) or
            (dir_d and self._is_collision(point_l)) or
            (dir_l and self._is_collision(point_u)) or
            (dir_r and self._is_collision(point_d)),

            # Danger left
            (dir_d and self._is_collision(point_r)) or
            (dir_u and self._is_collision(point_l)) or
            (dir_r and self._is_collision(point_u)) or
            (dir_l and self._is_collision(point_d)),

            # Move direction
            dir_l, dir_r, dir_u, dir_d,

            # Food location relative to head
            self.game.food_pos[0] < head[0],  # food left
            self.game.food_pos[0] > head[0],  # food right
            self.game.food_pos[1] < head[1],  # food up
            self.game.food_pos[1] > head[1]   # food down
        ]
        
        return state

    def _is_collision(self, point: Tuple[int, int]) -> bool:
        """Check if a point results in collision"""
        x, y = point
        
        # Hits boundary
        if (x >= self.game.settings.WINDOW_SIZE or x < 0 or 
            y >= self.game.settings.WINDOW_SIZE or y < 0):
            return True
        
        # Hits itself
        if point in self.game.snake_pos[:-1]:
            return True
            
        return False

    def _get_manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def draw_debug_info(self, screen) -> None:
        """Draw debug visualization for AI decision making"""
        pass  # Implemented by subclasses if needed