import pygame
import random
from constants import *
from player import Player
from obstacles import Car, Log, Water
from scoring import ScoreManager
from menu import Menu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Crossy Road")
        self.clock = pygame.time.Clock()
        
        # Initialize menu and scoring
        self.menu = Menu(self.screen)
        self.score_manager = ScoreManager()
        
        # Initialize game state
        self.reset_game()
        
    def reset_game(self, character='frog', difficulty='medium'):
        # Create separate sprite groups for layering
        self.all_sprites = pygame.sprite.LayeredUpdates()  # Use LayeredUpdates instead of Group
        self.cars = pygame.sprite.Group()
        self.logs = pygame.sprite.Group()
        self.water_areas = pygame.sprite.Group()
        
        # Create water areas and initial logs first
        self.setup_water_lanes()
        
        # Create player last so it's on top
        self.player = Player(character)
        self.all_sprites.add(self.player, layer=10)  # Higher layer number = drawn on top
        
        # Set difficulty
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS[difficulty]
        self.car_speed = self.settings['starting_speed']
        self.lives = self.settings['lives']
        
        # Game state
        self.level = 1
        self.game_over = False
        self.score = 0
        
    def setup_water_lanes(self):
        # Create water lanes in the middle of the screen
        water_start = SCREEN_HEIGHT // 2 - (WATER_LANES * LANE_HEIGHT) // 2
        for i in range(WATER_LANES):
            water = Water(water_start + i * LANE_HEIGHT)
            self.water_areas.add(water)
            self.all_sprites.add(water, layer=1)  # Bottom layer
            
            # Add initial logs to each water lane
            self.create_log(water.rect.y, True)
            self.create_log(water.rect.y, False)
            
    def create_car(self):
        if random.randint(1, self.settings['car_frequency']) == 1:
            # Don't spawn cars in water lanes
            possible_lanes = [y for y in range(LANE_HEIGHT, SCREEN_HEIGHT - LANE_HEIGHT, LANE_HEIGHT)
                            if not any(water.rect.collidepoint(0, y) for water in self.water_areas)]
            if possible_lanes:
                lane = random.choice(possible_lanes)
                car = Car(self.car_speed, lane)
                self.cars.add(car)
                self.all_sprites.add(car, layer=5)  # Middle layer
                
    def create_log(self, lane_y, moving_right=True):
        log = Log(LOG_SPEED, lane_y, moving_right)
        self.logs.add(log)
        self.all_sprites.add(log, layer=2)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Allow escape to menu both during gameplay and game over
                    return 'menu'
                if not self.game_over:
                    if event.key == pygame.K_UP:
                        self.player.move("up")
                    elif event.key == pygame.K_DOWN:
                        self.player.move("down")
                    elif event.key == pygame.K_LEFT:
                        self.player.move("left")
                    elif event.key == pygame.K_RIGHT:
                        self.player.move("right")
        return True
        
    def check_collisions(self):
        # Check car collisions
        if pygame.sprite.spritecollide(self.player, self.cars, False):
            if self.player.die():
                self.game_over = True
                
        # Check water collisions
        in_water = False
        for water in self.water_areas:
            if water.rect.colliderect(self.player.rect):
                in_water = True
                # Check if player is on a log
                log_collisions = pygame.sprite.spritecollide(self.player, self.logs, False)
                if log_collisions:
                    # Player is safe on a log
                    self.player.on_log = log_collisions[0]
                else:
                    # Player is in water but not on a log
                    self.player.on_log = None
                    if self.player.die():
                        self.game_over = True
                break
                
        if not in_water:
            self.player.on_log = None
            
    def level_up(self):
        self.level += 1
        self.score += 100 * self.level  # Bonus points for completing level
        self.car_speed += self.settings['speed_increment']
        self.player.go_to_start()
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw HUD
        font = pygame.font.SysFont(*FONT_SMALL)
        level_text = font.render(f'Level: {self.level}', True, WHITE)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        lives_text = font.render(f'Lives: {self.player.lives}', True, WHITE)
        
        self.screen.blit(level_text, (10, 10))
        self.screen.blit(score_text, (10, 40))
        self.screen.blit(lives_text, (10, 70))
        
        if self.game_over:
            game_over_text = font.render('GAME OVER - Press ESC for Menu', True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)
            
        pygame.display.flip()
        
    def run(self):
        running = True
        game_state = 'menu'
        
        while running:
            if game_state == 'menu':
                menu_result = self.menu.update()
                if menu_result == False:
                    running = False
                elif isinstance(menu_result, tuple) and menu_result[0] == 'start_game':
                    _, character, difficulty = menu_result
                    self.reset_game(character, difficulty)
                    game_state = 'game'
                else:
                    self.menu.draw()
                    
            elif game_state == 'game':
                result = self.handle_events()
                if result == False:
                    running = False
                elif result == 'menu':
                    if self.game_over:
                        # Save score before returning to menu if game is over
                        self.score_manager.add_score(self.score, self.difficulty)
                    game_state = 'menu'
                else:
                    if not self.game_over:
                        self.create_car()
                        
                        # Create new logs as needed
                        for water in self.water_areas:
                            if random.randint(1, 60) == 1:  # Adjust frequency as needed
                                self.create_log(water.rect.y, random.choice([True, False]))
                        
                        self.all_sprites.update()
                        self.check_collisions()
                        
                        # Update score based on player's progress
                        if self.player.is_at_finish_line():
                            self.level_up()
                            
                    self.draw()
                    
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()