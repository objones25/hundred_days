import pygame
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hovered = False
        
    def draw(self, screen, font):
        color = (min(self.color[0] + 30, 255),
                min(self.color[1] + 30, 255),
                min(self.color[2] + 30, 255)) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                return True
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.SysFont(*FONT_LARGE)
        self.font_medium = pygame.font.SysFont(*FONT_MEDIUM)
        self.state = 'main'  # main, character_select, difficulty, high_scores
        self.selected_character = 'frog'
        self.selected_difficulty = 'medium'
        self.setup_buttons()
        
    def setup_buttons(self):
        # Increased button width from 200 to 300 for main menu buttons
        # and adjusted x positions to maintain center alignment
        center_x = SCREEN_WIDTH // 2
        button_width = 320
        x_position = center_x - button_width // 2
        
        self.buttons = {
            'main': [
                Button(x_position, 200, button_width, 50, "Start Game"),
                Button(x_position, 270, button_width, 50, "Character Selection"),
                Button(x_position, 340, button_width, 50, "High Scores"),
                Button(x_position, 410, button_width, 50, "Quit")
            ],
            'character_select': [
                Button(center_x - 250, 200, 150, 50, "Frog"),
                Button(center_x - 75, 200, 150, 50, "Turtle"),
                Button(center_x + 100, 200, 150, 50, "Duck"),
                Button(x_position, 410, button_width, 50, "Back")
            ],
            'difficulty': [
                Button(center_x - 250, 200, 150, 50, "Easy"),
                Button(center_x - 75, 200, 150, 50, "Medium"),
                Button(center_x + 100, 200, 150, 50, "Hard"),
                Button(x_position, 410, button_width, 50, "Back")
            ]
        }
        
    def handle_main_menu(self, button_text):
        if button_text == "Start Game":
            self.state = 'difficulty'
        elif button_text == "Character Selection":
            self.state = 'character_select'
        elif button_text == "High Scores":
            self.state = 'high_scores'
        elif button_text == "Quit":
            return False
        return True
        
    def handle_character_select(self, button_text):
        if button_text == "Back":
            self.state = 'main'
        else:
            self.selected_character = button_text.lower()
            
    def handle_difficulty(self, button_text):
        if button_text == "Back":
            self.state = 'main'
        else:
            self.selected_difficulty = button_text.lower()
            return ('start_game', self.selected_character, self.selected_difficulty)
            
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            for button in self.buttons.get(self.state, []):
                if button.handle_event(event):
                    if self.state == 'main':
                        return self.handle_main_menu(button.text)
                    elif self.state == 'character_select':
                        self.handle_character_select(button.text)
                    elif self.state == 'difficulty':
                        result = self.handle_difficulty(button.text)
                        if result:
                            return result
                            
        return True
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title = "Crossy Road Clone" if self.state == 'main' else self.state.replace('_', ' ').title()
        title_surface = self.font_large.render(title, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons
        for button in self.buttons.get(self.state, []):
            button.draw(self.screen, self.font_medium)
            
        pygame.display.flip()