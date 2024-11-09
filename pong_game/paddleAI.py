import random
import math

class PaddleAI:
    def __init__(self, difficulty=0.7):
        """
        Initialize AI controller with improved difficulty scaling and human-like behavior
        
        Args:
            difficulty (float): AI difficulty between 0 and 1
                              1 is perfect, 0 is very easy
        """
        self.difficulty = max(0.0, min(1.0, difficulty))
        
        # Difficulty-based parameters
        self.prediction_error = (1 - self.difficulty) * 100  # Base prediction error
        self.reaction_delay = int((1 - self.difficulty) * 15)  # Frames of delay before reacting
        self.mistake_chance = (1 - self.difficulty) * 0.15  # Chance to make an intentional mistake
        
        # State tracking
        self.current_delay = 0
        self.last_predicted_y = None
        self.making_mistake = False
        self.mistake_duration = 0
        
    def update(self, paddle, ball, screen_height):
        """
        Update AI paddle movement with more human-like behavior
        
        Args:
            paddle: The paddle controlled by AI
            ball: The game ball
            screen_height: Height of the game screen
        """
        # Update mistake state
        if self.mistake_duration > 0:
            self.mistake_duration -= 1
            if self.mistake_duration <= 0:
                self.making_mistake = False
        
        # Randomly decide to make a mistake
        if not self.making_mistake and random.random() < self.mistake_chance:
            self.making_mistake = True
            self.mistake_duration = random.randint(10, 30)  # Mistake lasts for 10-30 frames
            
        # Handle reaction delay
        if self.current_delay > 0:
            self.current_delay -= 1
            if self.last_predicted_y is not None:
                self._move_paddle(paddle, self.last_predicted_y)
            return
            
        # Predict ball position
        predicted_y = self._predict_ball_y(ball, paddle.rect.x, screen_height)
        
        # Add prediction error based on difficulty
        if not self.making_mistake:
            error = random.uniform(-self.prediction_error, self.prediction_error)
            predicted_y += error
        else:
            # When making a mistake, move in wrong direction occasionally
            predicted_y = random.uniform(0, screen_height)
        
        # Keep prediction within screen bounds
        predicted_y = max(paddle.rect.height/2, min(screen_height - paddle.rect.height/2, predicted_y))
        
        # Reset reaction delay if ball direction changes
        if ball.velocity_x * (paddle.rect.x - ball.rect.x) > 0:  # Ball is moving toward paddle
            if random.random() < 0.1:  # 10% chance to add reaction delay
                self.current_delay = self.reaction_delay
                
        # Store last prediction for use during delay
        self.last_predicted_y = predicted_y
        self._move_paddle(paddle, predicted_y)
    
    def _predict_ball_y(self, ball, paddle_x, screen_height):
        """
        Predict ball y-position with improved bounce prediction
        
        Args:
            ball: The game ball
            paddle_x: x-position of the paddle
            screen_height: Height of the game screen
            
        Returns:
            float: Predicted y-position where ball will intersect
        """
        if abs(ball.velocity_x) < 0.1:
            return ball.rect.y
            
        # Calculate time until interception
        time = abs((paddle_x - ball.rect.x) / ball.velocity_x)
        
        # Initial prediction
        predicted_y = ball.rect.y + (ball.velocity_y * time)
        
        # Calculate number of bounces
        total_distance = abs(predicted_y)
        num_bounces = total_distance // screen_height
        
        # Final position after bounces
        if num_bounces % 2 == 0:
            final_y = total_distance % screen_height
        else:
            final_y = screen_height - (total_distance % screen_height)
            
        # Add slight randomization to prediction based on difficulty
        prediction_noise = (1 - self.difficulty) * random.uniform(-20, 20)
        final_y += prediction_noise
        
        return final_y
    
    def _move_paddle(self, paddle, target_y):
        """
        Move paddle toward target position with variable accuracy
        
        Args:
            paddle: The paddle to move
            target_y: Target y position
        """
        # Add "sloppiness" to movement based on difficulty
        movement_threshold = 5 + (1 - self.difficulty) * 15
        
        diff = target_y - paddle.rect.centery
        
        if abs(diff) < movement_threshold:
            paddle.stop()
        elif diff > 0:
            paddle.move_down()
        else:
            paddle.move_up()
            
    def reset(self):
        """Reset AI state for new round"""
        self.current_delay = 0
        self.last_predicted_y = None
        self.making_mistake = False
        self.mistake_duration = 0