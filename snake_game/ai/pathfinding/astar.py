from typing import List, Tuple, Set, Dict
import heapq
from core.constants import Direction
from collections import defaultdict
import numpy as np

class Node:
    def __init__(self, position: Tuple[int, int], parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start to current node
        self.h = 0  # Estimated cost from current node to end
        self.f = 0  # Total cost (g + h)

    def __eq__(self, other):
        return self.position == other.position
    
    def __lt__(self, other):
        return self.f < other.f

class AStarPathfinder:
    def __init__(self, game):
        self.game = game
        self.grid_size = game.settings.GRID_SIZE
        self.width = game.settings.WINDOW_SIZE // self.grid_size
        self.height = game.settings.WINDOW_SIZE // self.grid_size
        self.current_path = []
        
    def get_next_move(self) -> Direction:
        """Get the next move using A* pathfinding"""
        # If we don't have a path or reached end of current path, calculate new path
        if not self.current_path:
            # First try path to food
            path = self.find_path(self.game.snake_pos[0], self.game.food_pos)
            
            # If can't reach food, try to find path to tail
            if not path:
                path = self.find_path(self.game.snake_pos[0], self.game.snake_pos[-1])
            
            if path:
                self.current_path = path
            else:
                # If no path found, try to move to the safest direction
                return self.get_safe_direction()
        
        # Get next position from path
        next_pos = self.current_path.pop(0)
        return self.get_direction_to_position(self.game.snake_pos[0], next_pos)
    
    def find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using A* algorithm"""
        start_node = Node(start)
        end_node = Node(end)
        
        # Initialize open and closed lists
        open_list = []
        closed_list = set()
        
        # Add start node to open list
        heapq.heappush(open_list, start_node)
        
        while open_list:
            # Get node with lowest f score
            current_node = heapq.heappop(open_list)
            closed_list.add(current_node.position)
            
            # Found the goal
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Return reversed path
            
            # Generate neighbors
            for new_position in self.get_neighbors(current_node.position):
                # Skip if position is in closed list
                if new_position in closed_list:
                    continue
                
                # Create neighbor node
                neighbor = Node(new_position, current_node)
                
                # Skip if position collides with snake
                if self.is_collision(new_position):
                    continue
                
                # Calculate costs
                neighbor.g = current_node.g + 1
                neighbor.h = self.manhattan_distance(neighbor.position, end_node.position)
                neighbor.f = neighbor.g + neighbor.h
                
                # Check if neighbor is in open list and if it has a lower f value
                if self.should_add_to_open(open_list, neighbor):
                    heapq.heappush(open_list, neighbor)
        
        return []  # No path found
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        x, y = position
        neighbors = []
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left
            new_x = x + dx * self.grid_size
            new_y = y + dy * self.grid_size
            
            # Check bounds
            if (0 <= new_x < self.game.settings.WINDOW_SIZE and 
                0 <= new_y < self.game.settings.WINDOW_SIZE):
                neighbors.append((new_x, new_y))
        
        return neighbors
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])) // self.grid_size
    
    def is_collision(self, position: Tuple[int, int]) -> bool:
        """Check if position collides with snake body"""
        return position in self.game.snake_pos[:-1]
    
    def should_add_to_open(self, open_list: List[Node], neighbor: Node) -> bool:
        """Check if neighbor should be added to open list"""
        for node in open_list:
            if neighbor == node and neighbor.f >= node.f:
                return False
        return True
    
    def get_safe_direction(self) -> Direction:
        """Get the safest direction when no path is found"""
        head = self.game.snake_pos[0]
        possible_moves = []
        
        for direction in Direction:
            next_pos = self.get_next_position(head, direction)
            if next_pos and not self.is_collision(next_pos):
                # Calculate number of free squares accessible from this move
                free_squares = self.count_free_squares(next_pos)
                possible_moves.append((direction, free_squares))
        
        if possible_moves:
            # Return direction that leads to most free squares
            return max(possible_moves, key=lambda x: x[1])[0]
        
        # If no safe moves, return current direction
        return self.game.snake_direction
    
    def count_free_squares(self, start_pos: Tuple[int, int]) -> int:
        """Count number of free squares accessible from a position"""
        visited = set([start_pos])
        queue = [start_pos]
        count = 0
        
        while queue:
            pos = queue.pop(0)
            count += 1
            
            for next_pos in self.get_neighbors(pos):
                if (next_pos not in visited and 
                    not self.is_collision(next_pos)):
                    visited.add(next_pos)
                    queue.append(next_pos)
        
        return count
    
    def get_next_position(self, position: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
        """Get next position based on direction"""
        x, y = position
        if direction == Direction.UP:
            y -= self.grid_size
        elif direction == Direction.DOWN:
            y += self.grid_size
        elif direction == Direction.LEFT:
            x -= self.grid_size
        elif direction == Direction.RIGHT:
            x += self.grid_size
            
        # Check bounds
        if (0 <= x < self.game.settings.WINDOW_SIZE and 
            0 <= y < self.game.settings.WINDOW_SIZE):
            return (x, y)
        return None
    
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