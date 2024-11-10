import pygame
import random
import sys
from typing import Optional, Tuple, List
from core.constants import Direction, GameState, GameSettings, AIType
from core.theme import ThemeManager
from ai.base import SnakeAI
from enum import Enum
from ai.reinforcement import RLAgent, RLConfig
import numpy as np
from utils.visualization import plot_training_stats

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
        self.selected_menu_item = 0
        self.current_speed = self.settings.INITIAL_SPEED
        
        # AI related
        self.ai_agent = None
        self.ai_type = None
        self.selected_ai_item = 0
        self.config = RLConfig()
        self.game_count = 0
        self.record = 0
        self.total_score = 0
        self.scores = []
        self.mean_scores = []
        
        # High score related
        self.input_active = False
        self.name_input = ""
        self.player_name = "Player"
        
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game state"""
        grid_count = self.settings.WINDOW_SIZE // self.settings.GRID_SIZE
        center = (grid_count // 2) * self.settings.GRID_SIZE
        self.snake_pos = [(center, center)]
        self.snake_direction = Direction.RIGHT
        self.food_pos = self.generate_food()
        self.score = 0
        self.game_over = False
        self.prev_food_distance = float('inf')
        if self.ai_agent:
            self.game_count += 1
            if self.score > self.record:
                self.record = self.score
                self.ai_agent.model.save()
                
            self.total_score += self.score
            mean_score = self.total_score / self.game_count
            
            self.scores.append(self.score)
            self.mean_scores.append(mean_score)
            
            # Train long memory
            if self.game_count > 1:
                self.ai_agent.train_long_memory()

    def generate_food(self) -> Tuple[int, int]:
        """Generate new food position"""
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

        if not self.game_over and not self.ai_agent and self.state == GameState.PLAYING:
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
                if event.key == pygame.K_1:  # Reinforcement Learning
                    self.ai_type = AIType.REINFORCEMENT_LEARNING
                    self.ai_agent = RLAgent(self)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_2:  # A* Pathfinding
                    self.ai_type = AIType.ASTAR
                    # self.ai_agent = AStarAgent(self)  # To be implemented
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_3:  # Hamiltonian
                    self.ai_type = AIType.HAMILTONIAN
                    # self.ai_agent = HamiltonianAgent(self)  # To be implemented
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_4:  # Hybrid
                    self.ai_type = AIType.HYBRID
                    # self.ai_agent = HybridAgent(self)  # To be implemented
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
        if self.ai_agent:
            next_direction = self.ai_agent.get_next_move()
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
            return
            
        self.snake_pos.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food_pos:
            self.score += 1
            self.food_pos = self.generate_food()
            # Increase speed with score if not in AI mode
            if not self.ai_agent:
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
        title = font.render('Select AI Type', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        menu_items = [
            '1: Reinforcement Learning - Deep Q-Learning',
            '2: A* Pathfinding - Shortest Path',
            '3: Hamiltonian Cycle - Complete Coverage',
            '4: Hybrid AI - Combined Strategies',
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
        
        # Draw AI info
        if self.ai_agent:
            if isinstance(self.ai_agent, RLAgent):
                # Show RL specific info
                ai_text = font.render(f'AI: {self.ai_type.value}', True, self.current_theme.snake_color)
                self.screen.blit(ai_text, (10, 40))
                
                games_text = font.render(f'Games: {self.ai_agent.n_games}', True, self.current_theme.snake_color)
                self.screen.blit(games_text, (10, 70))
                
                record_text = font.render(f'Record: {self.record}', True, self.current_theme.snake_color)
                self.screen.blit(record_text, (10, 100))
                
                epsilon_text = font.render(f'ε: {self.ai_agent.epsilon:.3f}', True, self.current_theme.snake_color)
                self.screen.blit(epsilon_text, (10, 130))
                
                # Draw AI debug visualization
                self.ai_agent.draw_debug_info(self.screen)
    
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
    
    def ai_step(self) -> Tuple[float, bool, int]:
        """Execute one step with AI agent"""
        if not self.ai_agent:
            return 0, False, 0
            
        # Get old state
        state_old = self.ai_agent.get_state()
        
        # Get move
        final_move = self.ai_agent.get_next_move()
        
        # Perform move and get new state
        reward, done, score = self._move(final_move)
        state_new = self.ai_agent.get_state()
        
        # Train short memory
        self.ai_agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        # Remember
        self.ai_agent.remember(state_old, final_move, reward, state_new, done)
        
        return reward, done, score

    def calculate_reward(self, ate_food: bool, died: bool) -> float:
        """Calculate reward for the current step"""
        if died:
            return self.config.REWARD_DEATH
        if ate_food:
            return self.config.REWARD_EAT
            
        # Calculate if snake got closer or further from food
        head = self.snake_pos[0]
        old_distance = self.prev_food_distance
        new_distance = abs(head[0] - self.food_pos[0]) + abs(head[1] - self.food_pos[1])
        self.prev_food_distance = new_distance
        
        if new_distance < old_distance:
            return self.config.REWARD_CLOSER
        return self.config.REWARD_FARTHER

    def _move(self, action: List[int]) -> Tuple[float, bool, int]:
        """Execute move and return (reward, done, score)"""
        # Convert action to direction if needed
        if self.ai_agent:
            self.snake_direction = self.ai_agent._action_to_direction(action)
        
        # Get current head position
        head_x, head_y = self.snake_pos[0]
        
        # Calculate new head position
        if self.snake_direction == Direction.UP:
            head_y -= self.settings.GRID_SIZE
        elif self.snake_direction == Direction.DOWN:
            head_y += self.settings.GRID_SIZE
        elif self.snake_direction == Direction.LEFT:
            head_x -= self.settings.GRID_SIZE
        elif self.snake_direction == Direction.RIGHT:
            head_x += self.settings.GRID_SIZE
        
        new_head = (head_x, head_y)
        
        # Check for collision/game over
        done = (
            head_x < 0 or 
            head_x >= self.settings.WINDOW_SIZE or
            head_y < 0 or 
            head_y >= self.settings.WINDOW_SIZE or
            new_head in self.snake_pos[:-1]
        )
        
        if done:
            self.game_over = True
            return self.config.REWARD_DEATH, True, self.score
        
        # Update snake position
        self.snake_pos.insert(0, new_head)
        
        # Check food collision
        ate_food = new_head == self.food_pos
        if ate_food:
            self.score += 1
            self.food_pos = self.generate_food()
        else:
            self.snake_pos.pop()
        
        # Calculate reward
        reward = self.calculate_reward(ate_food, done)
        
        return reward, done, self.score

    def run(self):
        while True:
            self.handle_input()
            
            if self.state == GameState.PLAYING:
                if self.ai_agent and isinstance(self.ai_agent, RLAgent):
                    # RL Agent gameplay
                    reward, done, score = self.ai_step()
                    if done:
                        self.reset_game()
                        # Update visualization if we have enough data
                        if len(self.scores) > 2:
                            plot_training_stats(self.scores, self.mean_scores)
                else:
                    # Normal gameplay or other AI types
                    self.update()
                    
            self.draw()
            self.clock.tick(self.current_speed)