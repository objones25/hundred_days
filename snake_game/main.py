# main.py
import pygame
import sys
from core.game import SnakeGame
from core.constants import GameState
from utils.logger import setup_logger

def main():
    logger = setup_logger()
    try:
        game = SnakeGame()
        # Call the run method to start the game loop
        game.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()