from typing import Optional, Tuple
from core.constants import Direction
from .astar import AStarPathfinder
from .hamilton import HamiltonianPathfinder

class HybridPathfinder:
    """Combines A* and Hamiltonian strategies for optimal performance"""
    
    def __init__(self, game):
        self.game = game
        self.astar = AStarPathfinder(game)
        self.hamilton = HamiltonianPathfinder(game)
        self.use_astar = True  # Start with A* for efficiency
        
    def get_next_move(self) -> Direction:
        """Get next move using hybrid strategy"""
        # Calculate grid coverage (how much of the grid is occupied by snake)
        grid_size = self.game.width * self.game.height
        coverage = len(self.game.snake_pos) / grid_size
        
        # Switch to Hamiltonian cycle when snake gets longer
        # This prevents the snake from trapping itself
        if coverage > 0.5:  # Adjust this threshold as needed
            self.use_astar = False
        else:
            self.use_astar = True
            
        # Use appropriate strategy
        if self.use_astar:
            # Try A* first
            path = self.astar.find_path(self.game.snake_pos[0], self.game.food_pos)
            if path:
                return self.astar.get_direction_to_position(
                    self.game.snake_pos[0], 
                    path[1] if len(path) > 1 else path[0]
                )
            
            # If A* fails, switch to Hamiltonian
            self.use_astar = False
            
        # Use Hamiltonian cycle as fallback
        return self.hamilton.get_next_move()
    
    def draw_debug_info(self, screen) -> None:
        """Draw debug visualization"""
        import pygame
        font = pygame.font.Font(None, 24)
        strategy = "A*" if self.use_astar else "Hamiltonian"
        text = font.render(f"Strategy: {strategy}", True, (255, 255, 255))
        screen.blit(text, (10, 160))
        
        # Draw current path if using A*
        if self.use_astar and hasattr(self.astar, 'current_path'):
            for pos in self.astar.current_path:
                pygame.draw.rect(screen, (0, 255, 0), 
                               (pos[0], pos[1], 5, 5))