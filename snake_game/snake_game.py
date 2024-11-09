import pygame
import random
import sys
from typing import List, Tuple, Optional
from constants import Direction, GameState, GameSettings
from theme import ThemeManager
from snake_ai import SnakeAI, AIDifficulty
from high_score_system import HighScoreSystem

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.settings = GameSettings()
        
        # Setup display
        self.screen = pygame.display.set_mode((self.settings.WINDOW_SIZE, self.settings.WINDOW_SIZE))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        
        # Initialize themes
        self.themes = ThemeManager.get_themes()
        self.current_theme = self.themes["classic"]
        
        # Game state
        self.state = GameState.TITLE
        self.selected_pause_item = 0
        self.selected_game_over_item = 0
        self.ai_solver = None
        self.current_speed = self.settings.INITIAL_SPEED
        self.selected_menu_item = 0
        self.ai_difficulty = AIDifficulty.MEDIUM
        
        # Initialize high score system
        self.high_scores = HighScoreSystem()
        self.player_name = "Player"  # Default name
        self.input_active = False
        self.name_input = ""
        
        self.reset_game()

    def reset_game(self):
        grid_count = self.settings.WINDOW_SIZE // self.settings.GRID_SIZE
        center = (grid_count // 2) * self.settings.GRID_SIZE
        self.snake_pos = [(center, center)]
        self.snake_direction = Direction.RIGHT
        self.food_pos = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self) -> Tuple[int, int]:
        while True:
            x = random.randrange(0, self.settings.WINDOW_SIZE, self.settings.GRID_SIZE)
            y = random.randrange(0, self.settings.WINDOW_SIZE, self.settings.GRID_SIZE)
            if (x, y) not in self.snake_pos:
                return (x, y)

    def handle_title_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.selected_menu_item == 0:  # Start Game
                        self.state = GameState.PLAYING
                        self.reset_game()
                    elif self.selected_menu_item == 1:  # AI Mode
                        self.state = GameState.AI_MENU
                    elif self.selected_menu_item == 2:  # Settings
                        self.state = GameState.SETTINGS
                    elif self.selected_menu_item == 3:  # Quit
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_UP:
                    self.selected_menu_item = (self.selected_menu_item - 1) % 4
                elif event.key == pygame.K_DOWN:
                    self.selected_menu_item = (self.selected_menu_item + 1) % 4

    def handle_game_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_over:
                        self.state = GameState.TITLE
                    else:
                        self.state = GameState.PAUSED
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

        if not self.game_over and not self.ai_solver and self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and self.snake_direction != Direction.DOWN:
                self.snake_direction = Direction.UP
            elif keys[pygame.K_DOWN] and self.snake_direction != Direction.UP:
                self.snake_direction = Direction.DOWN
            elif keys[pygame.K_LEFT] and self.snake_direction != Direction.RIGHT:
                self.snake_direction = Direction.LEFT
            elif keys[pygame.K_RIGHT] and self.snake_direction != Direction.LEFT:
                self.snake_direction = Direction.RIGHT

    def handle_ai_menu_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.ai_difficulty = AIDifficulty.EASY
                    self.ai_solver = SnakeAI(self, self.ai_difficulty)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_2:
                    self.ai_difficulty = AIDifficulty.MEDIUM
                    self.ai_solver = SnakeAI(self, self.ai_difficulty)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_3:
                    self.ai_difficulty = AIDifficulty.HARD
                    self.ai_solver = SnakeAI(self, self.ai_difficulty)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_4:
                    self.ai_difficulty = AIDifficulty.EXPERT
                    self.ai_solver = SnakeAI(self, self.ai_difficulty)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.TITLE

    def handle_pause_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_RETURN:
                    if self.selected_pause_item == 0:  # Resume
                        self.state = GameState.PLAYING
                    elif self.selected_pause_item == 1:  # Restart
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif self.selected_pause_item == 2:  # Main Menu
                        self.state = GameState.TITLE
                elif event.key == pygame.K_UP:
                    self.selected_pause_item = (self.selected_pause_item - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.selected_pause_item = (self.selected_pause_item + 1) % 3

    def handle_settings_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.TITLE
                elif event.key == pygame.K_1:  # Change theme
                    themes = list(self.themes.keys())
                    current_index = themes.index(self.current_theme.name.lower())
                    next_index = (current_index + 1) % len(themes)
                    self.current_theme = self.themes[themes[next_index]]
                elif event.key == pygame.K_2:  # Change speed
                    self.current_speed = (self.current_speed + 5) % (self.settings.MAX_SPEED + 5)
                    if self.current_speed < self.settings.MIN_SPEED:
                        self.current_speed = self.settings.MIN_SPEED
    
    def handle_game_over_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        self.player_name = self.name_input if self.name_input else "Player"
                        self.high_scores.add_score(
                            self.player_name,
                            self.score,
                            self.ai_difficulty.value if self.ai_solver else "normal",
                            bool(self.ai_solver)
                        )
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                    else:
                        if len(self.name_input) < 10:  # Limit name length
                            self.name_input += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        if self.selected_game_over_item == 0:  # Restart
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif self.selected_game_over_item == 1:  # Main Menu
                            self.state = GameState.TITLE
                    elif event.key == pygame.K_UP:
                        self.selected_game_over_item = (self.selected_game_over_item - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        self.selected_game_over_item = (self.selected_game_over_item + 1) % 2


    def handle_input(self):
        if self.state == GameState.TITLE:
            self.handle_title_input()
        elif self.state == GameState.PLAYING:
            self.handle_game_input()
        elif self.state == GameState.PAUSED:
            self.handle_pause_input()
        elif self.state == GameState.GAME_OVER:
            self.handle_game_over_input()
        elif self.state == GameState.AI_MENU:
            self.handle_ai_menu_input()
        elif self.state == GameState.SETTINGS:
            self.handle_settings_input()

    def update(self):
        if self.state != GameState.PLAYING or self.game_over:
            return

        # Get AI move if AI is enabled
        if self.ai_solver:
            next_direction = self.ai_solver.get_next_move()
            if next_direction:
                self.snake_direction = next_direction

        # Calculate new head position
        head_x, head_y = self.snake_pos[0]
        if self.snake_direction == Direction.UP:
            head_y -= self.settings.GRID_SIZE
        elif self.snake_direction == Direction.DOWN:
            head_y += self.settings.GRID_SIZE
        elif self.snake_direction == Direction.LEFT:
            head_x -= self.settings.GRID_SIZE
        elif self.snake_direction == Direction.RIGHT:
            head_x += self.settings.GRID_SIZE
        
        new_head = (head_x, head_y)
        
        # Check collisions
        if (
            head_x < 0 or head_x >= self.settings.WINDOW_SIZE or
            head_y < 0 or head_y >= self.settings.WINDOW_SIZE or
            new_head in self.snake_pos[:-1]
        ):
            self.game_over = True
            # Check if it's a high score
            if self.high_scores.is_high_score(
                self.score,
                self.ai_difficulty.value if self.ai_solver else "normal",
                not bool(self.ai_solver)
            ):
                self.input_active = True
                self.name_input = ""
            return
            
        self.snake_pos.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food_pos:
            self.score += 1
            self.food_pos = self.generate_food()
            # Increase speed with score if not in AI mode
            if not self.ai_solver:
                self.current_speed = min(
                    self.settings.MAX_SPEED,
                    self.settings.INITIAL_SPEED + self.score // 5
                )
        else:
            self.snake_pos.pop()

    def draw_title_screen(self):
        self.screen.fill(self.current_theme.bg_color)
        font = pygame.font.Font(None, 74)
        title = font.render('Snake Game', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        menu_items = ['Start Game', 'AI Mode', 'Settings', 'Quit']
        menu_font = pygame.font.Font(None, 36)
        for i, item in enumerate(menu_items):
            color = self.current_theme.food_color if i == self.selected_menu_item else self.current_theme.snake_color
            text = menu_font.render(item, True, color)
            rect = text.get_rect(center=(self.settings.WINDOW_SIZE//2, 250 + i * 50))
            self.screen.blit(text, rect)

    def draw_ai_menu(self):
        self.screen.fill(self.current_theme.bg_color)
        font = pygame.font.Font(None, 48)
        title = font.render('Select AI Difficulty', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        menu_items = [
            '1: Easy - Basic pathfinding with mistakes',
            '2: Medium - A* with occasional mistakes',
            '3: Hard - Advanced A* with tail chasing',
            '4: Expert - Optimal Hamiltonian paths',
            'ESC: Back to Menu'
        ]
        menu_font = pygame.font.Font(None, 36)
        for i, item in enumerate(menu_items):
            text = menu_font.render(item, True, self.current_theme.snake_color)
            rect = text.get_rect(center=(self.settings.WINDOW_SIZE//2, 250 + i * 50))
            self.screen.blit(text, rect)

    def draw_settings(self):
        self.screen.fill(self.current_theme.bg_color)
        font = pygame.font.Font(None, 48)
        title = font.render('Settings', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        menu_items = [
            f'1: Theme: {self.current_theme.name}',
            f'2: Speed: {self.current_speed}',
            'ESC: Back to Menu'
        ]
        menu_font = pygame.font.Font(None, 36)
        for i, item in enumerate(menu_items):
            text = menu_font.render(item, True, self.current_theme.snake_color)
            rect = text.get_rect(center=(self.settings.WINDOW_SIZE//2, 250 + i * 50))
            self.screen.blit(text, rect)

    def draw_game_screen(self):
        self.screen.fill(self.current_theme.bg_color)
        
        # Draw snake
        for segment in self.snake_pos:
            pygame.draw.rect(self.screen, self.current_theme.snake_color,
                           (segment[0], segment[1], self.settings.GRID_SIZE, self.settings.GRID_SIZE))
        
        # Draw food
        pygame.draw.rect(self.screen, self.current_theme.food_color,
                        (self.food_pos[0], self.food_pos[1], self.settings.GRID_SIZE, self.settings.GRID_SIZE))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, self.current_theme.snake_color)
        self.screen.blit(score_text, (10, 10))
        
        # Draw AI info if AI is active
        if self.ai_solver:
            ai_text = font.render(f'AI: {self.ai_difficulty.value}', True, self.current_theme.snake_color)
            self.screen.blit(ai_text, (10, 40))
            # Draw AI debug visualization
            self.ai_solver.draw_debug_info(self.screen)
    
    def draw_pause_screen(self):
        # Add semi-transparent overlay
        overlay = pygame.Surface((self.settings.WINDOW_SIZE, self.settings.WINDOW_SIZE))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 74)
        title = font.render('Paused', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        menu_items = ['Resume', 'Restart', 'Main Menu']
        menu_font = pygame.font.Font(None, 36)
        for i, item in enumerate(menu_items):
            color = self.current_theme.food_color if i == self.selected_pause_item else self.current_theme.snake_color
            text = menu_font.render(item, True, color)
            rect = text.get_rect(center=(self.settings.WINDOW_SIZE//2, 250 + i * 50))
            self.screen.blit(text, rect)
    
    def draw_game_over_screen(self):
        # Add semi-transparent overlay
        overlay = pygame.Surface((self.settings.WINDOW_SIZE, self.settings.WINDOW_SIZE))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 74)
        title = font.render('Game Over', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f'Score: {self.score}', True, self.current_theme.snake_color)
        score_rect = score_text.get_rect(center=(self.settings.WINDOW_SIZE//2, 180))
        self.screen.blit(score_text, score_rect)

        # Draw high scores
        high_scores = self.high_scores.get_top_scores(limit=5)
        if high_scores:
            title_font = pygame.font.Font(None, 36)
            title_text = title_font.render('High Scores:', True, self.current_theme.snake_color)
            self.screen.blit(title_text, (self.settings.WINDOW_SIZE//4, 220))
            
            score_font = pygame.font.Font(None, 24)
            for i, (name, score, diff, ai, date) in enumerate(high_scores):
                score_text = score_font.render(
                    f'{name}: {score} ({diff}{"[AI]" if ai else ""})',
                    True, self.current_theme.snake_color
                )
                self.screen.blit(score_text, (self.settings.WINDOW_SIZE//4, 250 + i * 25))

        # Name input if it's a high score
        if self.input_active:
            input_font = pygame.font.Font(None, 36)
            prompt = input_font.render('Enter your name:', True, self.current_theme.snake_color)
            self.screen.blit(prompt, (self.settings.WINDOW_SIZE//4, 400))
            
            name = input_font.render(self.name_input + '_', True, self.current_theme.food_color)
            self.screen.blit(name, (self.settings.WINDOW_SIZE//4, 430))
        else:
            menu_items = ['Restart', 'Main Menu']
            menu_font = pygame.font.Font(None, 36)
            for i, item in enumerate(menu_items):
                color = self.current_theme.food_color if i == self.selected_game_over_item else self.current_theme.snake_color
                text = menu_font.render(item, True, color)
                rect = text.get_rect(center=(self.settings.WINDOW_SIZE//2, 400 + i * 50))
                self.screen.blit(text, rect)

    def draw(self):
        if self.state == GameState.TITLE:
            self.draw_title_screen()
        elif self.state == GameState.PLAYING:
            self.draw_game_screen()
        elif self.state == GameState.PAUSED:
            self.draw_game_screen()
            self.draw_pause_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_screen()
            self.draw_game_over_screen()
        elif self.state == GameState.AI_MENU:
            self.draw_ai_menu()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.current_speed)