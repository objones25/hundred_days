import pygame
from paddle import Paddle
from ball import Ball
from scoreBoard import ScoreBoard
from soundManager import SoundManager
from gameState import GameState, Difficulty
from paddleAI import PaddleAI
import random

class PongGame:
    def __init__(self, width=800, height=600, fps=60):
        pygame.init()
        pygame.display.set_caption('Pong')
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fps = fps
        
        # Initialize sound
        self.sound_manager = SoundManager()
        
        # Game objects
        self.reset_game_objects()
        
        # Game state
        self.state = GameState.TITLE
        self.running = True
        self.bg_color = (0, 0, 0)
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        
        # Menu selection
        self.selected_difficulty = 0
        self.difficulties = list(Difficulty)
        
        # AI controller (will be initialized with selected difficulty)
        self.ai = None
        
    def reset_game_objects(self):
        """Reset all game objects to initial state"""
        paddle_offset = 50
        self.player1 = Paddle(paddle_offset, self.height // 2 - 45)
        self.player2 = Paddle(self.width - paddle_offset - 15, self.height // 2 - 45)
        self.ball = Ball(self.width // 2, self.height // 2, sound_manager=self.sound_manager)
        self.scoreboard = ScoreBoard(self.width, self.height)
        
    def handle_input(self):
        """Handle keyboard input for game control"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
                
        # Handle continuous key presses for game movement
        if self.state in [GameState.GAME_SINGLE, GameState.GAME_MULTI]:
            keys = pygame.key.get_pressed()
            
            # Player 1 controls
            if keys[pygame.K_w]:
                self.player1.move_up()
            elif keys[pygame.K_s]:
                self.player1.move_down()
            else:
                self.player1.stop()
                
            # Player 2 controls (only in multiplayer)
            if self.state == GameState.GAME_MULTI:
                if keys[pygame.K_UP]:
                    self.player2.move_up()
                elif keys[pygame.K_DOWN]:
                    self.player2.move_down()
                else:
                    self.player2.stop()
                    
    def handle_keydown(self, key):
        """Handle single key press events"""
        if self.state == GameState.TITLE:
            if key == pygame.K_1:
                self.state = GameState.DIFFICULTY
            elif key == pygame.K_2:
                self.state = GameState.GAME_MULTI
                self.reset_game_objects()
            elif key == pygame.K_ESCAPE:
                self.running = False
                
        elif self.state == GameState.DIFFICULTY:
            if key == pygame.K_UP:
                self.selected_difficulty = (self.selected_difficulty - 1) % len(self.difficulties)
            elif key == pygame.K_DOWN:
                self.selected_difficulty = (self.selected_difficulty + 1) % len(self.difficulties)
            elif key == pygame.K_RETURN:
                # Start single player game with selected difficulty
                self.reset_game_objects()
                difficulty = self.difficulties[self.selected_difficulty].value
                self.ai = PaddleAI(difficulty=difficulty)
                self.state = GameState.GAME_SINGLE
            elif key == pygame.K_ESCAPE:
                self.state = GameState.TITLE
                
        else:  # In-game states
            if key == pygame.K_ESCAPE:
                self.state = GameState.TITLE
            elif key == pygame.K_SPACE:
                if self.state in [GameState.GAME_SINGLE, GameState.GAME_MULTI]:
                    self.state = GameState.PAUSE
                elif self.state == GameState.PAUSE:
                    self.state = GameState.GAME_SINGLE if self.ai else GameState.GAME_MULTI
                    
    def update(self):
        """Update game state"""
        if self.state in [GameState.GAME_SINGLE, GameState.GAME_MULTI]:
            # Update paddles
            self.player1.update(self.height)
            
            # Update AI or player 2
            if self.state == GameState.GAME_SINGLE:
                self.ai.update(self.player2, self.ball, self.height)
            self.player2.update(self.height)
            
            # Update ball and check for scoring
            score_result = self.ball.update(self.height, [self.player1, self.player2])
            
            # Update scores
            if score_result > 0:
                self.scoreboard.update_score(score_result)
                
            # Check for winner
            winner = self.scoreboard.get_winner()
            if winner > 0:
                self.sound_manager.play_sound('game_win')
                self.state = GameState.TITLE
                
    def draw_title_screen(self):
        """Draw the title screen"""
        # Title
        title_text = self.title_font.render("PONG", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 4))
        
        # Menu options
        single_text = self.menu_font.render("Press 1 for Single Player", True, (255, 255, 255))
        multi_text = self.menu_font.render("Press 2 for Two Players", True, (255, 255, 255))
        exit_text = self.menu_font.render("Press ESC to Exit", True, (255, 255, 255))
        
        single_rect = single_text.get_rect(center=(self.width // 2, self.height // 2))
        multi_rect = multi_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        exit_rect = exit_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
        
        # Draw everything
        self.screen.blit(title_text, title_rect)
        self.screen.blit(single_text, single_rect)
        self.screen.blit(multi_text, multi_rect)
        self.screen.blit(exit_text, exit_rect)
        
    def draw_difficulty_screen(self):
        """Draw the difficulty selection screen"""
        # Title
        title_text = self.title_font.render("SELECT DIFFICULTY", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        inst_text = self.menu_font.render("Use UP/DOWN arrows to select, ENTER to start", True, (255, 255, 255))
        inst_rect = inst_text.get_rect(center=(self.width // 2, self.height // 4 + 60))
        self.screen.blit(inst_text, inst_rect)
        
        # Draw difficulty options
        start_y = self.height // 2
        for i, diff in enumerate(self.difficulties):
            # Highlight selected difficulty
            color = (255, 255, 0) if i == self.selected_difficulty else (255, 255, 255)
            # Add arrow indicator for selected item
            prefix = "→ " if i == self.selected_difficulty else "  "
            
            text = self.menu_font.render(f"{prefix}{diff.name}", True, color)
            rect = text.get_rect(center=(self.width // 2, start_y + i * 50))
            self.screen.blit(text, rect)
            
        # Back option
        back_text = self.menu_font.render("Press ESC to go back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(self.width // 2, self.height - 50))
        self.screen.blit(back_text, back_rect)

    def draw_pause_screen(self):
        """Draw the pause screen overlay"""
        pause_text = self.title_font.render("PAUSED", True, (255, 255, 255))
        continue_text = self.menu_font.render("Press SPACE to Continue", True, (255, 255, 255))
        menu_text = self.menu_font.render("Press ESC for Menu", True, (255, 255, 255))
        
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        menu_rect = menu_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(continue_text, continue_rect)
        self.screen.blit(menu_text, menu_rect)
        
    def render(self):
        """Render the game state"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        if self.state == GameState.TITLE:
            self.draw_title_screen()
        elif self.state == GameState.DIFFICULTY:
            self.draw_difficulty_screen()
        else:
            # Draw game objects
            self.scoreboard.draw(self.screen)
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.ball.draw(self.screen)
            
            if self.state == GameState.PAUSE:
                self.draw_pause_screen()
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(self.fps)
            
        pygame.quit()

if __name__ == "__main__":
    game = PongGame()
    game.run()