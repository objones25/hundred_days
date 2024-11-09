import pygame
from constants import *

class Player(pygame.sprite.Sprite):
    def __init__(self, skin='frog'):
        super().__init__()
        self.skin_name = skin
        self.lives = 3
        self.score = 0
        self.time_bonus = 0
        self.on_log = None
        
        # Create the player image
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        if skin == 'frog':
            self.image.fill(GREEN)
        elif skin == 'turtle':
            self.image.fill(GRAY)
        elif skin == 'duck':
            self.image.fill((255, 255, 0))  # Yellow
        self.rect = self.image.get_rect()
        
        self.go_to_start()
        
    def go_to_start(self):
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE - 20
        self.on_log = None
        
    def move(self, direction):
        if direction == "up" and self.rect.top > 0:
            self.rect.y -= MOVE_DISTANCE
            self.score += 10  # Points for moving forward
        elif direction == "down" and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += MOVE_DISTANCE
        elif direction == "left" and self.rect.left > 0:
            self.rect.x -= MOVE_DISTANCE
        elif direction == "right" and self.rect.right < SCREEN_WIDTH:
            self.rect.x += MOVE_DISTANCE
            
    def update(self):
        if self.on_log:
            # Store the previous position in case we need to revert
            prev_x = self.rect.x
            self.rect.x += self.on_log.speed
            
            # If moving with the log would put us off screen, revert the movement
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.rect.x = prev_x
                self.die()
                
    def die(self):
        """Returns True if game should end, False otherwise"""
        self.lives -= 1
        self.on_log = None  # Clear log reference when dying
        if self.lives > 0:
            self.go_to_start()
            return False
        return True
            
    def is_at_finish_line(self):
        return self.rect.top <= PLAYER_SIZE
    
    def get_score(self):
        return self.score + self.time_bonus