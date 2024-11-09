from typing import List, Tuple, Optional, Dict
import heapq
import random
from enum import Enum
from constants import Direction, GameSettings
import pygame

class AIDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class SnakeAI:
    def __init__(self, game, difficulty: AIDifficulty = AIDifficulty.MEDIUM):
        self.game = game
        self.settings = GameSettings()
        self.difficulty = difficulty
        self.path = []
        self.debug_points: List[Tuple[int, int]] = []  # Points to visualize
        self.debug_lines: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []  # Lines to visualize

    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_next_move(self) -> Optional[Direction]:
        """Get the next move based on difficulty level."""
        if self.difficulty == AIDifficulty.EASY:
            return self._get_easy_move()
        elif self.difficulty == AIDifficulty.MEDIUM:
            return self._get_medium_move()
        elif self.difficulty == AIDifficulty.HARD:
            return self._get_hard_move()
        else:  # EXPERT
            return self._get_expert_move()
    
    def _get_easy_move(self) -> Optional[Direction]:
        """Simple greedy algorithm with random mistakes."""
        if random.random() < 0.2:  # 20% chance to make a mistake
            return random.choice(list(Direction))
        
        return self._basic_pathfinding()
    
    def _get_medium_move(self) -> Optional[Direction]:
        """A* pathfinding with occasional mistakes."""
        if random.random() < 0.1:  # 10% chance to make a mistake
            return random.choice(list(Direction))
        
        if not self.path:
            self.path = self._a_star_pathfinding()
        return self.path.pop(0) if self.path else self._basic_pathfinding()
    
    def _get_hard_move(self) -> Optional[Direction]:
        """Advanced A* with tail-chasing when no direct path exists."""
        if not self.path:
            self.path = self._a_star_pathfinding()
            if not self.path:
                self.path = self._tail_chasing_pathfinding()
        return self.path.pop(0) if self.path else self._basic_pathfinding()
    
    def _get_expert_move(self) -> Optional[Direction]:
        """Hamiltonian cycle with shortcuts."""
        if not self.path:
            self.path = self._optimal_hamiltonian()
        return self.path.pop(0) if self.path else self._basic_pathfinding()

    def get_valid_neighbors(self, pos: Tuple[int, int], snake_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = []
        
        for dx, dy in [(0, self.settings.GRID_SIZE), (self.settings.GRID_SIZE, 0), 
                       (0, -self.settings.GRID_SIZE), (-self.settings.GRID_SIZE, 0)]:
            new_x, new_y = x + dx, y + dy
            
            if (0 <= new_x < self.settings.WINDOW_SIZE and 
                0 <= new_y < self.settings.WINDOW_SIZE and 
                (new_x, new_y) not in snake_positions):
                neighbors.append((new_x, new_y))
                self.debug_points.append((new_x, new_y))  # Visualize considered positions
                
        return neighbors

    def _basic_pathfinding(self) -> Optional[Direction]:
        """Simple greedy pathfinding towards food."""
        head = self.game.snake_pos[0]
        food = self.game.food_pos
        
        dx = food[0] - head[0]
        dy = food[1] - head[1]
        
        # Try horizontal movement first
        if dx > 0 and self._is_safe_move(Direction.RIGHT):
            return Direction.RIGHT
        elif dx < 0 and self._is_safe_move(Direction.LEFT):
            return Direction.LEFT
        
        # Try vertical movement
        if dy > 0 and self._is_safe_move(Direction.DOWN):
            return Direction.DOWN
        elif dy < 0 and self._is_safe_move(Direction.UP):
            return Direction.UP
        
        # If no direct path, try any safe direction
        for direction in Direction:
            if self._is_safe_move(direction):
                return direction
        
        return None

    def _is_safe_move(self, direction: Direction) -> bool:
        """Check if a move is safe (won't result in immediate collision)."""
        head_x, head_y = self.game.snake_pos[0]
        
        if direction == Direction.UP:
            new_pos = (head_x, head_y - self.settings.GRID_SIZE)
        elif direction == Direction.DOWN:
            new_pos = (head_x, head_y + self.settings.GRID_SIZE)
        elif direction == Direction.LEFT:
            new_pos = (head_x - self.settings.GRID_SIZE, head_y)
        else:  # RIGHT
            new_pos = (head_x + self.settings.GRID_SIZE, head_y)
        
        # Check bounds
        if (new_pos[0] < 0 or new_pos[0] >= self.settings.WINDOW_SIZE or
            new_pos[1] < 0 or new_pos[1] >= self.settings.WINDOW_SIZE):
            return False
        
        # Check snake collision
        return new_pos not in self.game.snake_pos[:-1]

    def _a_star_pathfinding(self) -> List[Direction]:
        """A* pathfinding algorithm."""
        start = self.game.snake_pos[0]
        goal = self.game.food_pos
        
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            for next_pos in self.get_valid_neighbors(current, self.game.snake_pos):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.manhattan_distance(next_pos, goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
                    self.debug_lines.append((current, next_pos))  # Visualize pathfinding
        
        # Reconstruct path
        path = []
        current = goal
        while current != start:
            prev = came_from.get(current)
            if not prev:
                return []
            path.append(self._get_direction(prev, current))
            current = prev
            
        path.reverse()
        return path

    def _tail_chasing_pathfinding(self) -> List[Direction]:
        """Find path to snake's tail when no direct path to food exists."""
        head = self.game.snake_pos[0]
        tail = self.game.snake_pos[-1]
        
        frontier = [(0, head)]
        came_from = {head: None}
        cost_so_far = {head: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == tail:
                break
                
            for next_pos in self.get_valid_neighbors(current, self.game.snake_pos[:-1]):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.manhattan_distance(next_pos, tail)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # Reconstruct path
        path = []
        current = tail
        while current != head:
            prev = came_from.get(current)
            if not prev:
                return []
            path.append(self._get_direction(prev, current))
            current = prev
            
        path.reverse()
        return path

    def _optimal_hamiltonian(self) -> List[Direction]:
        """Create an optimal Hamiltonian cycle with shortcuts."""
        grid_size = self.settings.WINDOW_SIZE // self.settings.GRID_SIZE
        path = []
        
        # Generate basic Hamiltonian cycle
        for y in range(grid_size):
            if y % 2 == 0:
                for x in range(grid_size - 1):
                    path.append(Direction.RIGHT)
                if y < grid_size - 1:
                    path.append(Direction.DOWN)
            else:
                for x in range(grid_size - 1):
                    path.append(Direction.LEFT)
                if y < grid_size - 1:
                    path.append(Direction.DOWN)
        
        # Look for safe shortcuts
        head = self.game.snake_pos[0]
        food = self.game.food_pos
        if self.manhattan_distance(head, food) < len(path) // 2:
            shortcut = self._a_star_pathfinding()
            if shortcut:
                return shortcut
        
        return path

    def _get_direction(self, current: Tuple[int, int], next_pos: Tuple[int, int]) -> Direction:
        """Convert two positions into a direction."""
        dx = next_pos[0] - current[0]
        dy = next_pos[1] - current[1]
        
        if dx > 0:
            return Direction.RIGHT
        elif dx < 0:
            return Direction.LEFT
        elif dy < 0:
            return Direction.UP
        else:
            return Direction.DOWN

    def draw_debug_info(self, screen: pygame.Surface):
        """Draw debug visualization of AI decision-making."""
        # Draw considered points
        for point in self.debug_points:
            pygame.draw.circle(screen, (255, 255, 0), point, 3)
        
        # Draw pathfinding lines
        for start, end in self.debug_lines:
            pygame.draw.line(screen, (0, 255, 255), start, end, 2)
        
        # Draw predicted path
        if self.path:
            current = self.game.snake_pos[0]
            for direction in self.path:
                if direction == Direction.UP:
                    next_pos = (current[0], current[1] - self.settings.GRID_SIZE)
                elif direction == Direction.DOWN:
                    next_pos = (current[0], current[1] + self.settings.GRID_SIZE)
                elif direction == Direction.LEFT:
                    next_pos = (current[0] - self.settings.GRID_SIZE, current[1])
                else:  # RIGHT
                    next_pos = (current[0] + self.settings.GRID_SIZE, current[1])
                
                pygame.draw.line(screen, (0, 255, 0), current, next_pos, 2)
                current = next_pos
        
        # Clear debug info for next frame
        self.debug_points.clear()
        self.debug_lines.clear()