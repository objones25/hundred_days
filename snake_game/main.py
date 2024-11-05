import pygame
import sys
from snake_game import SnakeGame

def main():
    try:
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()