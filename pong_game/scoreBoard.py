import pygame

class ScoreBoard:
    def __init__(self, screen_width, screen_height):
        """
        Initialize the scoreboard
        
        Args:
            screen_width (int): Width of the game window
            screen_height (int): Height of the game window
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player1_score = 0
        self.player2_score = 0
        
        # Initialize font - using system font for reliability
        try:
            self.font = pygame.font.Font(None, 74)  # None uses default system font
        except pygame.error:
            print("Font initialization failed. Using fallback.")
            self.font = pygame.font.SysFont('arial', 74)
            
        self.color = (255, 255, 255)  # White color
        
        # Position calculations for various display elements
        self.score_padding = 20  # Distance from top of screen
        self.center_line_width = 4
        self.dash_length = 15
        self.dash_gap = 15
        
    def update_score(self, player, points=1):
        """
        Update the score for a specified player
        
        Args:
            player (int): Player number (1 or 2)
            points (int): Points to add (default 1)
        """
        if player == 1:
            self.player1_score += points
        elif player == 2:
            self.player2_score += points
            
    def draw(self, screen):
        """
        Draw the scoreboard and center line
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw center line (dashed)
        center_x = self.screen_width // 2
        for y in range(0, self.screen_height, self.dash_length + self.dash_gap):
            pygame.draw.rect(
                screen,
                self.color,
                (center_x - self.center_line_width // 2,
                 y,
                 self.center_line_width,
                 self.dash_length)
            )
        
        # Render scores
        p1_text = self.font.render(str(self.player1_score), True, self.color)
        p2_text = self.font.render(str(self.player2_score), True, self.color)
        
        # Position scores
        p1_pos = (self.screen_width // 4 - p1_text.get_width() // 2,
                  self.score_padding)
        p2_pos = (3 * self.screen_width // 4 - p2_text.get_width() // 2,
                  self.score_padding)
        
        # Draw scores
        screen.blit(p1_text, p1_pos)
        screen.blit(p2_text, p2_pos)
        
    def reset_scores(self):
        """Reset both players' scores to zero"""
        self.player1_score = 0
        self.player2_score = 0
        
    def get_winner(self, winning_score=11):
        """
        Check if there's a winner
        
        Args:
            winning_score (int): Score needed to win (default 11)
            
        Returns:
            int: 0 if no winner yet, 1 or 2 for player number who won
        """
        if self.player1_score >= winning_score:
            return 1
        elif self.player2_score >= winning_score:
            return 2
        return 0