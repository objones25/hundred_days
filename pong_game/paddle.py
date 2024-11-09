import pygame

class Paddle:
    def __init__(self, x, y, width=15, height=90, speed=5):
        """
        Initialize a new paddle
        
        Args:
            x (int): Initial x position
            y (int): Initial y position
            width (int): Paddle width in pixels
            height (int): Paddle height in pixels
            speed (int): Movement speed in pixels per frame
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.color = (255, 255, 255)  # White color
        self.score = 0
        # Add velocity for smooth movement
        self.velocity = 0
    
    def move_up(self):
        """Update velocity for upward movement"""
        self.velocity = -self.speed
    
    def move_down(self):
        """Update velocity for downward movement"""
        self.velocity = self.speed
    
    def stop(self):
        """Stop paddle movement"""
        self.velocity = 0
    
    def update(self, screen_height):
        """
        Update paddle position while keeping it within screen bounds
        
        Args:
            screen_height (int): Height of the game window
        """
        # Update position based on velocity
        self.rect.y += self.velocity
        
        # Keep paddle within screen bounds
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
    
    def draw(self, screen):
        """
        Draw the paddle on the screen
        
        Args:
            screen: Pygame surface to draw on
        """
        pygame.draw.rect(screen, self.color, self.rect)