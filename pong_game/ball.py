import pygame
import random
import math

class Ball:
    def __init__(self, x, y, size=15, speed=7, sound_manager=None):
        """
        Initialize a new ball
        
        Args:
            x (int): Initial x position
            y (int): Initial y position
            size (int): Ball diameter in pixels
            speed (int): Movement speed in pixels per frame
            sound_manager (SoundManager): Sound manager instance
        """
        self.rect = pygame.Rect(x, y, size, size)
        self.initial_speed = speed
        self.speed = speed
        self.color = (255, 255, 255)
        self.reset_position = (x, y)
        self.velocity_x = 0
        self.velocity_y = 0
        self.sound_manager = sound_manager
        self.reset()
    
    def reset(self):
        """Reset ball to center with random direction"""
        self.rect.x = self.reset_position[0]
        self.rect.y = self.reset_position[1]
        self.speed = self.initial_speed
        
        # Random angle between -45 and 45 degrees
        angle = random.uniform(-45, 45)
        # Randomly choose initial direction (left or right)
        if random.random() < 0.5:
            angle += 180
            
        # Convert angle to radians and calculate velocity components
        rad = math.radians(angle)
        self.velocity_x = self.speed * math.cos(rad)
        self.velocity_y = self.speed * math.sin(rad)
    
    def update(self, screen_height, paddles):
        """
        Update ball position and handle collisions
        
        Args:
            screen_height (int): Height of the game window
            paddles (list): List of paddle objects to check for collisions
        
        Returns:
            int: 0 for no score, 1 for player 1 score, 2 for player 2 score
        """
        # Store previous position for better collision detection
        previous_x = self.rect.x
        previous_y = self.rect.y
        
        # Move the ball
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Check for scoring (ball going off screen)
        if self.rect.left < 0:
            if self.sound_manager:
                self.sound_manager.play_sound('score')
            self.reset()
            return 2
        elif self.rect.right > 800:  # Assuming screen width is 800
            if self.sound_manager:
                self.sound_manager.play_sound('score')
            self.reset()
            return 1
            
        # Bounce off top and bottom
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = abs(self.velocity_y)  # Ensure downward velocity
            if self.sound_manager:
                self.sound_manager.play_sound('wall_hit')
        elif self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.velocity_y = -abs(self.velocity_y)  # Ensure upward velocity
            if self.sound_manager:
                self.sound_manager.play_sound('wall_hit')
            
        # Check paddle collisions
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                # Determine which side of the paddle was hit
                if previous_x + self.rect.width <= paddle.rect.left:  # Hit from left
                    self.rect.right = paddle.rect.left
                    self._handle_paddle_collision(paddle, 'left')
                elif previous_x >= paddle.rect.right:  # Hit from right
                    self.rect.left = paddle.rect.right
                    self._handle_paddle_collision(paddle, 'right')
                
                if self.sound_manager:
                    self.sound_manager.play_sound('paddle_hit')
                break  # Only collide with one paddle per frame
                
        return 0
    
    def _handle_paddle_collision(self, paddle, side):
        """
        Handle collision response with a paddle
        
        Args:
            paddle: Paddle object that the ball collided with
            side: Which side of the paddle was hit ('left' or 'right')
        """
        # Calculate relative intersection point (-1 to 1)
        relative_intersect_y = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height / 2)
        
        # Bounce angle between -45 and 45 degrees
        bounce_angle = relative_intersect_y * 45
        
        # Convert to radians
        rad = math.radians(bounce_angle)
        
        # Increase speed slightly with each hit (up to a maximum)
        self.speed = min(self.speed * 1.1, self.initial_speed * 1.5)
        
        # Calculate new velocities
        if side == 'left':
            self.velocity_x = -abs(self.speed * math.cos(rad))
        else:
            self.velocity_x = abs(self.speed * math.cos(rad))
            
        self.velocity_y = -self.speed * math.sin(rad)
    
    def draw(self, screen):
        """
        Draw the ball on the screen
        
        Args:
            screen: Pygame surface to draw on
        """
        pygame.draw.rect(screen, self.color, self.rect)