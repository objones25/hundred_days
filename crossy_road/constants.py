import pygame
import os

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
CAR_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0),
              (0, 255, 0), (0, 0, 255), (128, 0, 128)]

# Game elements
PLAYER_SIZE = 40
CAR_WIDTH = 80
CAR_HEIGHT = 40
LOG_WIDTH = 120
LOG_HEIGHT = 40
LANE_HEIGHT = 60
MOVE_DISTANCE = 60

# Game mechanics
STARTING_CAR_SPEED = 5
SPEED_INCREMENT = 2
LOG_SPEED = 3
WATER_LANES = 2  # Number of water lanes with logs

# Difficulty settings
DIFFICULTY_SETTINGS = {
    'easy': {
        'car_frequency': 30,
        'starting_speed': 3,
        'speed_increment': 1,
        'lives': 5
    },
    'medium': {
        'car_frequency': 20,
        'starting_speed': 5,
        'speed_increment': 2,
        'lives': 3
    },
    'hard': {
        'car_frequency': 15,
        'starting_speed': 7,
        'speed_increment': 3,
        'lives': 1
    }
}

# File paths
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(GAME_DIR, 'assets')
SAVE_FILE = os.path.join(GAME_DIR, 'highscores.json')

# Character skins - paths would point to actual image files
CHARACTER_SKINS = {
    'frog': {
        'image': 'frog.png',
        'scale': 1.0,
        'offset': (0, 0)
    },
    'turtle': {
        'image': 'turtle.png',
        'scale': 1.1,
        'offset': (0, -5)
    },
    'duck': {
        'image': 'duck.png',
        'scale': 0.9,
        'offset': (0, 0)
    }
}

# Fonts
FONT_LARGE = ("Arial", 48)
FONT_MEDIUM = ("Arial", 36)
FONT_SMALL = ("Arial", 24)