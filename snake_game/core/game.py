import pygame
import random
import sys
from typing import Optional, Tuple, List
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue

from core.constants import Direction, GameState, GameSettings, AIType
from core.theme import ThemeManager, Theme
from ai.base import SnakeAI
from ai.reinforcement import RLAgent, RLConfig
from ai.pathfinding.astar import AStarPathfinder
from ai.pathfinding.hamilton import HamiltonianPathfinder
from ai.pathfinding.hybrid import HybridPathfinder
from utils.visualization import plot_training_stats
from core.high_score_system import HighScoreSystem

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.settings = GameSettings()
        
        # Setup display
        self.screen = pygame.display.set_mode((self.settings.WINDOW_SIZE, self.settings.WINDOW_SIZE))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        
        # Initialize themes first
        self.themes = ThemeManager.get_themes()
        self.current_theme = self.themes.get("classic", ThemeManager.get_default_theme())
        
        # Initialize high score system
        self.high_scores = HighScoreSystem()
        
        # Load record from database
        all_scores = self.high_scores.get_top_scores(limit=1)
        self.record = all_scores[0][1] if all_scores else 0
        
        # Game state
        self.state = GameState.TITLE
        self.selected_pause_item = 0
        self.selected_game_over_item = 0
        self.selected_menu_item = 0
        self.current_speed = self.settings.INITIAL_SPEED
        
        # Game variables
        self.score = 0
        self.game_over = False
        self.prev_food_distance = float('inf')
        self.input_active = False
        self.name_input = ""
        
        # AI related
        self.ai_agent = None
        self.ai_type = None
        self.selected_ai_item = 0
        self.game_count = 0
        self.total_score = 0
        self.scores = []
        self.mean_scores = []
        self.config = RLConfig()
        
        # Initialize game state
        self.reset_game()

    def save_high_score(self):
        """Save the current score to high scores database"""
        if self.input_active and self.score > 0:
            player_name = self.name_input if self.name_input else "Anonymous"
            self.high_scores.add_score(
                player_name=player_name,
                score=self.score,
                difficulty="normal",  # You can modify this based on game settings
                ai_assisted=bool(self.ai_agent)
            )
            self.input_active = False

    def reset_game(self) -> None:
        """Reset the game state"""
        # Handle high scores before any state is reset
        if self.game_over and self.score > 0:
            # Update record in database if necessary
            self.update_record(self.score)
            
            # Check if it's a high score for name input
            if (not self.ai_agent and  # Only prompt for name if not AI
                self.high_scores.is_high_score(
                    self.score, 
                    difficulty="normal", 
                    include_ai=False
                )):
                self.input_active = True
                self.name_input = ""
            else:
                self.input_active = False
        
        # Update AI-related stats if AI is active
        if self.ai_agent:
            self.game_count += 1
            if hasattr(self.ai_agent, 'train_long_memory') and self.game_count > 1:
                self.ai_agent.train_long_memory()
                
            # Update AI metrics
            self.total_score += self.score
            mean_score = self.total_score / self.game_count if self.game_count > 0 else 0
            self.scores.append(self.score)
            self.mean_scores.append(mean_score)
            
            # Update AI agent's specific stats if available
            if hasattr(self.ai_agent, 'update_training_stats'):
                self.ai_agent.update_training_stats(self.score)
        
        # Reset core game state
        grid_count = self.settings.WINDOW_SIZE // self.settings.GRID_SIZE
        center = (grid_count // 2) * self.settings.GRID_SIZE
        self.snake_pos = [(center, center)]
        self.snake_direction = Direction.RIGHT
        self.food_pos = self.generate_food()
        self.score = 0
        self.game_over = False
        self.prev_food_distance = float('inf')
        
        # Reset any temporary game state flags
        self.input_active = False
        self.name_input = ""

    def generate_food(self) -> Tuple[int, int]:
        """Generate new food position"""
        while True:
            x = random.randrange(0, self.settings.WINDOW_SIZE, self.settings.GRID_SIZE)
            y = random.randrange(0, self.settings.WINDOW_SIZE, self.settings.GRID_SIZE)
            if (x, y) not in self.snake_pos:
                return (x, y)

    def handle_title_input(self):
        """Handle input on the title screen"""
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
        """Handle input during gameplay"""
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
                elif self.input_active:
                    if event.key == pygame.K_RETURN:
                        self.save_high_score()
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                    elif len(self.name_input) < 20:
                        self.name_input += event.unicode

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
        """Handle input in the AI menu"""
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
                    self.ai_agent = AStarPathfinder(self)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_3:  # Hamiltonian Cycle
                    self.ai_type = AIType.HAMILTONIAN
                    self.ai_agent = HamiltonianPathfinder(self)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_4:  # Hybrid
                    self.ai_type = AIType.HYBRID
                    self.ai_agent = HybridPathfinder(self)
                    self.state = GameState.PLAYING
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.TITLE

    def handle_pause_input(self):
        """Handle input when game is paused"""
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
        """Handle input in the settings menu"""
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
        """Handle input on the game over screen"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not self.input_active:
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
                else:
                    if event.key == pygame.K_RETURN:
                        self.save_high_score()
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                    elif len(self.name_input) < 20:
                        self.name_input += event.unicode

    def handle_input(self):
        """Main input handler"""
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
        """Update game state"""
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

    def calculate_reward(self, ate_food: bool, died: bool) -> float:
        """Calculate reward for the current step"""
        if died:
            return self.config.REWARD_DEATH
        if ate_food:
            return self.config.REWARD_EAT
            
        head = self.snake_pos[0]
        old_distance = self.prev_food_distance
        new_distance = abs(head[0] - self.food_pos[0]) + abs(head[1] - self.food_pos[1])
        self.prev_food_distance = new_distance
        
        if new_distance < old_distance:
            return self.config.REWARD_CLOSER
        return self.config.REWARD_FARTHER

    def _move(self, action: List[int]) -> Tuple[float, bool, int]:
        """Execute move and return (reward, done, score)"""
        if self.ai_agent:
            self.snake_direction = self.ai_agent._action_to_direction(action)
        
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

    def create_parallel_games(self):
        """Create multiple game instances for parallel training"""
        self.parallel_games = []
        for _ in range(self.num_parallel_games):
            game = SnakeGame()
            game.ai_agent = self.ai_agent.__class__(game)  # Create new AI agent instance
            game.ai_agent.model = self.ai_agent.model  # Share the same model
            self.parallel_games.append(game)

    def process_parallel_game(self, game_index: int) -> Tuple[int, float, bool, int]:
        """Process one step of a parallel game"""
        game = self.parallel_games[game_index]
        if not game.game_over:
            reward, done, score = game.ai_step()
            return game_index, reward, done, score
        return game_index, 0, True, game.score

    def update_parallel_games(self):
        """Update all parallel games"""
        results = []
        with ThreadPoolExecutor(max_workers=self.num_parallel_games) as executor:
            futures = [executor.submit(self.process_parallel_game, i) 
                      for i in range(self.num_parallel_games)]
            for future in futures:
                results.append(future.result())
        
        # Process results
        for game_index, reward, done, score in results:
            if done:
                # Update stats and reset the game
                self.parallel_games[game_index].ai_agent.update_training_stats(score)
                self.parallel_games[game_index].reset_game()
                
                # Put result in queue for visualization
                self.game_results_queue.put({
                    'game_index': game_index,
                    'score': score,
                    'total_games': self.ai_agent.n_games
                })

    def save_high_score(self):
        """Save the current score to high scores if it qualifies"""
        if hasattr(self, 'high_scores'):
            self.high_scores.add_score(
                self.name_input or "Anonymous",
                self.score,
                difficulty="normal",
                ai_assisted=bool(self.ai_agent)
            )
    
    def update_record(self, new_score: int) -> None:
        """Update record if new score is higher and save to database"""
        if new_score > self.record:
            self.record = new_score
            # Save to database with appropriate metadata
            self.high_scores.add_score(
                player_name=f"AI_{self.ai_type.value}" if self.ai_agent else self.name_input or "Anonymous",
                score=new_score,
                difficulty="normal",
                ai_assisted=bool(self.ai_agent)
            )
            # If it's an AI agent, also save the model
            if self.ai_agent and hasattr(self.ai_agent, 'model'):
                self.ai_agent.model.save(f'model_record_{new_score}.pth')

    def run(self):
        """Main game loop"""
        # Initialize plotting
        plt.ion()  # Turn on interactive mode
        
        while True:
            self.handle_input()
            
            if self.state == GameState.PLAYING:
                if self.ai_agent and isinstance(self.ai_agent, RLAgent):
                    try:
                        # Get old state
                        state_old = self.ai_agent.get_state()
                        
                        # Get move
                        action = self.ai_agent._get_action(state_old)
                        
                        # Perform move and get new state
                        reward, done, score = self._move(action)
                        state_new = self.ai_agent.get_state()
                        
                        # Train short memory
                        self.ai_agent.train_short_memory(state_old, action, reward, state_new, done)
                        
                        # Remember
                        self.ai_agent.remember(state_old, action, reward, state_new, done)
                        
                        if done:
                            # Update training stats
                            self.ai_agent.update_training_stats(score)
                            
                            # Update visualization every N games
                            if self.ai_agent.n_games % 5 == 0:
                                try:
                                    plot_training_stats(
                                        self.ai_agent.scores,
                                        self.ai_agent.mean_scores,
                                        self.ai_agent.training_stats
                                    )
                                except Exception as viz_error:
                                    print(f"Visualization error: {viz_error}")
                            
                            self.reset_game()
                    except Exception as e:
                        print(f"Error in AI loop: {str(e)}")
                        raise e
                else:
                    self.update()
            
            # Draw the current game state
            self.draw()
            
            # Control game speed
            self.clock.tick(60 if self.ai_agent else self.current_speed)

    def draw_title_screen(self):
        """Draw the title/menu screen"""
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

    def draw_game_screen(self):
        """Updated draw method to show correct high score info"""
        self.screen.fill(self.current_theme.bg_color)
        
        # Draw snake and food as before...
        for segment in self.snake_pos:
            pygame.draw.rect(self.screen, self.current_theme.snake_color,
                        (segment[0], segment[1], self.settings.GRID_SIZE, self.settings.GRID_SIZE))
        
        pygame.draw.rect(self.screen, self.current_theme.food_color,
                    (self.food_pos[0], self.food_pos[1], self.settings.GRID_SIZE, self.settings.GRID_SIZE))
        
        # Draw scores and info
        font = pygame.font.Font(None, 24)
        
        # Get all-time high score
        all_time_high = self.high_scores.get_top_scores(limit=1)
        high_score = all_time_high[0][1] if all_time_high else 0
        
        if self.ai_agent:
            if isinstance(self.ai_agent, RLAgent):
                stats = [
                    f'Score: {self.score}',
                    f'All-Time High: {high_score}',
                    f'AI: {self.ai_type.value}',
                    f'Games: {self.ai_agent.n_games}',
                    f'Record: {self.record}',
                    f'Memory: {len(self.ai_agent.memory)}/{self.ai_agent.config.MAX_MEMORY}',
                    f'Batch: {self.ai_agent.config.BATCH_SIZE}',
                    f'Current Reward: {self.ai_agent.current_reward:.1f}',
                    f'ε: {self.ai_agent.epsilon:.3f}'
                ]
            else:
                stats = [
                    f'Score: {self.score}',
                    f'All-Time High: {high_score}',
                    f'AI: {self.ai_type.value}',
                    f'Strategy: {self.ai_type.value}'
                ]
        else:
            stats = [
                f'Score: {self.score}',
                f'All-Time High: {high_score}'
            ]
        
        for i, stat in enumerate(stats):
            text = font.render(stat, True, self.current_theme.snake_color)
            self.screen.blit(text, (10, 10 + i * 20))

    def draw_pause_screen(self):
        """Draw the pause screen overlay"""
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
        """Draw the game over screen overlay"""
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

        # Draw high scores if available
        if hasattr(self, 'high_scores'):
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
        """Main draw method that handles all game states"""
        if self.state == GameState.TITLE:
            self.draw_title_screen()
        elif self.state == GameState.PLAYING:
            self.draw_game_screen()
        elif self.state == GameState.PAUSED:
            self.draw_game_screen()  # Draw game state first
            self.draw_pause_screen()  # Then overlay pause menu
        elif self.state == GameState.GAME_OVER:
            self.draw_game_screen()  # Draw final game state
            self.draw_game_over_screen()  # Then overlay game over menu
        elif self.state == GameState.AI_MENU:
            self.draw_ai_menu()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
            
        pygame.display.flip()  # Update the display

    def draw_ai_menu(self):
        """Draw the AI selection menu"""
        self.screen.fill(self.current_theme.bg_color)
        font = pygame.font.Font(None, 48)
        title = font.render('Select AI Type', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        # Updated menu items with more descriptive text
        menu_items = [
            ('1: Reinforcement Learning', 'Self-learning AI using Deep Q-Network'),
            ('2: A* Pathfinding', 'Finds optimal path to food'),
            ('3: Hamiltonian Cycle', 'Never fails but slower'),
            ('4: Hybrid AI', 'Combines A* and Hamiltonian strategies'),
            ('ESC: Back to Menu', '')
        ]

        menu_font = pygame.font.Font(None, 36)
        desc_font = pygame.font.Font(None, 24)
        y_pos = 200

        for item, desc in menu_items:
            # Draw main menu item
            text = menu_font.render(item, True, self.current_theme.snake_color)
            rect = text.get_rect(center=(self.settings.WINDOW_SIZE//2, y_pos))
            self.screen.blit(text, rect)
            
            # Draw description if it exists
            if desc:
                desc_text = desc_font.render(desc, True, self.current_theme.snake_color)
                desc_rect = desc_text.get_rect(center=(self.settings.WINDOW_SIZE//2, y_pos + 25))
                self.screen.blit(desc_text, desc_rect)
            
            y_pos += 70  # Increased spacing to accommodate descriptions

    def draw_settings(self):
        """Draw the settings menu"""
        self.screen.fill(self.current_theme.bg_color)
        font = pygame.font.Font(None, 48)
        title = font.render('Settings', True, self.current_theme.snake_color)
        title_rect = title.get_rect(center=(self.settings.WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)

        # Settings items with current values
        menu_items = [
            ('1: Theme', f'Current: {self.current_theme.name}'),
            ('2: Speed', f'Current: {self.current_speed}'),
            ('ESC: Back to Menu', '')
        ]

        menu_font = pygame.font.Font(None, 36)
        value_font = pygame.font.Font(None, 24)
        y_pos = 200

        for item, value in menu_items:
            # Draw setting name
            text = menu_font.render(item, True, self.current_theme.snake_color)
            rect = text.get_rect(midleft=(self.settings.WINDOW_SIZE//4, y_pos))
            self.screen.blit(text, rect)
            
            # Draw current value if it exists
            if value:
                value_text = value_font.render(value, True, self.current_theme.snake_color)
                value_rect = value_text.get_rect(midleft=(self.settings.WINDOW_SIZE//4, y_pos + 25))
                self.screen.blit(value_text, value_rect)
            
            y_pos += 70

        # Draw any additional settings info
        info_font = pygame.font.Font(None, 24)
        info_text = info_font.render('Use number keys to change settings', True, self.current_theme.snake_color)
        info_rect = info_text.get_rect(center=(self.settings.WINDOW_SIZE//2, self.settings.WINDOW_SIZE - 50))
        self.screen.blit(info_text, info_rect)