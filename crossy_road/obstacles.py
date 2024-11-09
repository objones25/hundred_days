import pygame
import random
from constants import *

class Car(pygame.sprite.Sprite):
    def __init__(self, speed, lane_y):
        super().__init__()
        self.image = pygame.Surface([CAR_WIDTH, CAR_HEIGHT])
        self.image.fill(random.choice(CAR_COLORS))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = lane_y
        self.speed = speed
        
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Log(pygame.sprite.Sprite):
    def __init__(self, speed, lane_y, moving_right=True):
        super().__init__()
        self.image = pygame.Surface([LOG_WIDTH, LOG_HEIGHT])
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.speed = speed if moving_right else -speed
        self.moving_right = moving_right
        
        # Position log based on movement direction
        if moving_right:
            self.rect.x = -LOG_WIDTH
        else:
            self.rect.x = SCREEN_WIDTH
        self.rect.y = lane_y
        
    def update(self):
        self.rect.x += self.speed
        # Remove log if it's off screen
        if (self.moving_right and self.rect.left > SCREEN_WIDTH) or \
           (not self.moving_right and self.rect.right < 0):
            self.kill()

class Water(pygame.sprite.Sprite):
    def __init__(self, y_pos, width=SCREEN_WIDTH, height=LANE_HEIGHT):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(BLUE)
        self.image.set_alpha(128)  # Semi-transparent
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = y_pos