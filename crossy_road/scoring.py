import json
import time
from constants import *

class ScoreManager:
    def __init__(self):
        self.high_scores = self.load_high_scores()
        self.current_score = 0
        self.start_time = time.time()
        
    def load_high_scores(self):
        try:
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'easy': [], 'medium': [], 'hard': []}
            
    def save_high_scores(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump(self.high_scores, f)
            
    def add_score(self, player_score, difficulty):
        player_name = self.get_player_name()  # You'd implement this to get name input
        time_bonus = max(0, int((300 - (time.time() - self.start_time)) * 10))
        final_score = player_score + time_bonus
        
        score_entry = {
            'name': player_name,
            'score': final_score,
            'date': time.strftime("%Y-%m-%d")
        }
        
        self.high_scores[difficulty].append(score_entry)
        self.high_scores[difficulty].sort(key=lambda x: x['score'], reverse=True)
        self.high_scores[difficulty] = self.high_scores[difficulty][:10]  # Keep top 10
        self.save_high_scores()
        
        return final_score
    
    def get_player_name(self):
        # This would be implemented with pygame input handling
        # For now, return default name
        return "Player"
    
    def format_high_scores(self, difficulty):
        scores = self.high_scores.get(difficulty, [])
        formatted = "High Scores:\n\n"
        for i, score in enumerate(scores[:10], 1):
            formatted += f"{i}. {score['name']}: {score['score']} ({score['date']})\n"
        return formatted