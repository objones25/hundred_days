from typing import List, Tuple, Optional
import heapq
from constants import Direction, GameSettings

class SnakeAI:
    def __init__(self, game, algorithm="a_star"):
        self.game = game
        self.algorithm = algorithm
        self.path = []
        self.settings = GameSettings()

    def get_next_move(self) -> Optional[Direction]:
        if not self.path:
            if self.algorithm == "a_star":
                self.path = self.a_star_pathfinding()
            elif self.algorithm == "hamiltonian":
                self.path = self.hamiltonian_cycle()
            else:
                self.path = self.greedy_pathfinding()
        
        return self.path.pop(0) if self.path else None

    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

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
                
        return neighbors

    def position_to_direction(self, current_pos: Tuple[int, int], next_pos: Tuple[int, int]) -> Direction:
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        if dx > 0:
            return Direction.RIGHT
        elif dx < 0:
            return Direction.LEFT
        elif dy < 0:
            return Direction.UP
        else:
            return Direction.DOWN

    def a_star_pathfinding(self) -> List[Direction]:
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
        
        # Reconstruct path
        path = []
        current = goal
        while current != start:
            prev = came_from.get(current)
            if not prev:
                return []
            path.append(self.position_to_direction(prev, current))
            current = prev
            
        path.reverse()
        return path

    def hamiltonian_cycle(self) -> List[Direction]:
        grid_width = self.settings.WINDOW_SIZE // self.settings.GRID_SIZE
        grid_height = self.settings.WINDOW_SIZE // self.settings.GRID_SIZE
        path = []
        
        # Create a Hamiltonian cycle path
        for y in range(0, self.settings.WINDOW_SIZE, self.settings.GRID_SIZE):
            # Move right
            if y // self.settings.GRID_SIZE % 2 == 0:
                for x in range(0, self.settings.WINDOW_SIZE - self.settings.GRID_SIZE, self.settings.GRID_SIZE):
                    path.append(Direction.RIGHT)
                if y < self.settings.WINDOW_SIZE - self.settings.GRID_SIZE:
                    path.append(Direction.DOWN)
            # Move left
            else:
                for x in range(0, self.settings.WINDOW_SIZE - self.settings.GRID_SIZE, self.settings.GRID_SIZE):
                    path.append(Direction.LEFT)
                if y < self.settings.WINDOW_SIZE - self.settings.GRID_SIZE:
                    path.append(Direction.DOWN)
                    
        return path

    def greedy_pathfinding(self) -> List[Direction]:
        path = []
        current = self.game.snake_pos[0]
        goal = self.game.food_pos
        
        while current != goal:
            neighbors = self.get_valid_neighbors(current, self.game.snake_pos)
            if not neighbors:
                break
                
            # Find the neighbor closest to the goal
            next_pos = min(neighbors, 
                          key=lambda pos: self.manhattan_distance(pos, goal))
            
            path.append(self.position_to_direction(current, next_pos))
            current = next_pos
            
        return path