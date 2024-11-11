from typing import List, Tuple, Dict, Set
from core.constants import Direction
import numpy as np

class HamiltonianPathfinder:
    def __init__(self, game):
        self.game = game
        self.grid_size = game.settings.GRID_SIZE
        self.width = game.settings.WINDOW_SIZE // self.grid_size
        self.height = game.settings.WINDOW_SIZE // self.grid_size
        self.cycle = []
        self.cycle_index = 0
        self.position_to_index = {}
        
        # Generate the Hamiltonian cycle once
        self.generate_cycle()
    
    def generate_cycle(self):
        """Generate a Hamiltonian cycle using a modified snaking pattern"""
        # Create a snaking pattern that covers all squares
        positions = []
        # Start from top-left corner
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                pos = (x * self.grid_size, y * self.grid_size)
                row.append(pos)
            # Reverse every other row to create snaking pattern
            if y % 2 == 1:
                row.reverse()
            positions.extend(row)
        
        # Connect last position back to first to complete the cycle
        self.cycle = positions
        
        # Create mapping of positions to their index in cycle
        self.position_to_index = {pos: idx for idx, pos in enumerate(self.cycle)}
    
    def get_next_move(self) -> Direction:
        """Get the next move following the Hamiltonian cycle"""
        current_pos = self.game.snake_pos[0]
        
        # Find where we are in the cycle
        current_index = self.position_to_index.get(current_pos, 0)
        
        # Look ahead for food and check if we can take shortcuts
        if self.can_take_shortcut():
            # Try to find a shorter path to food
            food_index = self.position_to_index.get(self.game.food_pos)
            if food_index is not None:
                next_pos = self.find_shortcut_to_food(current_index, food_index)
                if next_pos:
                    return self.get_direction_to_position(current_pos, next_pos)
        
        # If no shortcut possible, follow the cycle
        next_index = (current_index + 1) % len(self.cycle)
        next_pos = self.cycle[next_index]
        
        return self.get_direction_to_position(current_pos, next_pos)
    
    def can_take_shortcut(self) -> bool:
        """Determine if it's safe to take a shortcut based on snake length"""
        # Only take shortcuts if snake length is less than 70% of total squares
        max_length = self.width * self.height
        return len(self.game.snake_pos) < (0.7 * max_length)
    
    def find_shortcut_to_food(self, current_index: int, food_index: int) -> Tuple[int, int]:
        """Try to find a safe shortcut to food"""
        head = self.game.snake_pos[0]
        snake_positions = set(self.game.snake_pos)
        
        # Check all neighboring positions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x = head[0] + dx * self.grid_size
            next_y = head[1] + dy * self.grid_size
            next_pos = (next_x, next_y)
            
            # Skip if position is invalid or unsafe
            if not self.is_valid_position(next_pos) or next_pos in snake_positions:
                continue
            
            # Check if this move gets us closer to food in cycle
            next_index = self.position_to_index.get(next_pos)
            if next_index is None:
                continue
                
            # Calculate distances in cycle
            cycle_distance = (food_index - current_index) % len(self.cycle)
            shortcut_distance = (food_index - next_index) % len(self.cycle)
            
            # Take shortcut if it reduces cycle distance and doesn't trap snake
            if shortcut_distance < cycle_distance and self.is_safe_move(next_pos):
                return next_pos
        
        return None
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        x, y = position
        return (0 <= x < self.game.settings.WINDOW_SIZE and 
                0 <= y < self.game.settings.WINDOW_SIZE)
    
    def is_safe_move(self, position: Tuple[int, int]) -> bool:
        """Check if moving to position is safe (won't trap snake)"""
        # Simple flood fill to check if we can still reach snake tail
        visited = set([position])
        queue = [position]
        tail = self.game.snake_pos[-1]
        snake_positions = set(self.game.snake_pos[:-1])  # Exclude tail
        
        while queue:
            current = queue.pop(0)
            if current == tail:
                return True
                
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x = current[0] + dx * self.grid_size
                next_y = current[1] + dy * self.grid_size
                next_pos = (next_x, next_y)
                
                if (self.is_valid_position(next_pos) and 
                    next_pos not in visited and 
                    next_pos not in snake_positions):
                    visited.add(next_pos)
                    queue.append(next_pos)
        
        return False
    
    def get_direction_to_position(self, current: Tuple[int, int], target: Tuple[int, int]) -> Direction:
        """Get direction to move from current position to target position"""
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        
        if dx > 0:
            return Direction.RIGHT
        elif dx < 0:
            return Direction.LEFT
        elif dy > 0:
            return Direction.DOWN
        else:
            return Direction.UP