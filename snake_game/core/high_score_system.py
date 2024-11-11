import sqlite3
from datetime import datetime
from typing import List, Tuple
import os

class HighScoreSystem:
    def __init__(self, db_path: str = "snake_scores.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    ai_assisted BOOLEAN NOT NULL,
                    date_achieved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_score(self, player_name: str, score: int, difficulty: str = "normal", ai_assisted: bool = False) -> bool:
        """Add a new score to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO high_scores (player_name, score, difficulty, ai_assisted)
                    VALUES (?, ?, ?, ?)
                ''', (player_name, score, difficulty, ai_assisted))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding score: {e}")
            return False
    
    def get_top_scores(self, limit: int = 10, difficulty: str = None, include_ai: bool = True) -> List[Tuple]:
        """Get the top scores, optionally filtered by difficulty and AI usage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = "SELECT player_name, score, difficulty, ai_assisted, date_achieved FROM high_scores"
                params = []
                
                conditions = []
                if difficulty:
                    conditions.append("difficulty = ?")
                    params.append(difficulty)
                if not include_ai:
                    conditions.append("ai_assisted = 0")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY score DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting scores: {e}")
            return []
    
    def is_high_score(self, score: int, difficulty: str = "normal", include_ai: bool = True) -> bool:
        """Check if a score qualifies as a high score."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = "SELECT MIN(score) FROM (SELECT score FROM high_scores"
                params = []
                
                conditions = []
                if difficulty:
                    conditions.append("difficulty = ?")
                    params.append(difficulty)
                if not include_ai:
                    conditions.append("ai_assisted = 0")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY score DESC LIMIT ?) as top_scores"
                params.append(10)  # Check against top 10 scores
                
                cursor.execute(query, params)
                min_score = cursor.fetchone()[0]
                
                # If there are fewer than 10 scores, this is automatically a high score
                if min_score is None:
                    return True
                
                return score > min_score
        except sqlite3.Error as e:
            print(f"Error checking high score: {e}")
            return False
    
    def get_player_best_score(self, player_name: str, difficulty: str = None) -> int:
        """Get the best score for a specific player."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = "SELECT MAX(score) FROM high_scores WHERE player_name = ?"
                params = [player_name]
                
                if difficulty:
                    query += " AND difficulty = ?"
                    params.append(difficulty)
                
                cursor.execute(query, params)
                result = cursor.fetchone()[0]
                return result if result is not None else 0
        except sqlite3.Error as e:
            print(f"Error getting player best score: {e}")
            return 0
    
    def get_scores_by_difficulty(self, difficulty: str, limit: int = 10) -> List[Tuple]:
        """Get top scores for a specific difficulty level."""
        return self.get_top_scores(limit=limit, difficulty=difficulty)
    
    def get_non_ai_scores(self, limit: int = 10) -> List[Tuple]:
        """Get top scores excluding AI-assisted games."""
        return self.get_top_scores(limit=limit, include_ai=False)
    
    def clear_scores(self):
        """Clear all scores from the database. Use with caution!"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM high_scores")
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error clearing scores: {e}")
            return False
    
    def get_total_games_played(self) -> int:
        """Get the total number of games played."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM high_scores")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting total games: {e}")
            return 0
    
    def get_average_score(self) -> float:
        """Get the average score across all games."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT AVG(score) FROM high_scores")
                result = cursor.fetchone()[0]
                return float(result) if result is not None else 0.0
        except sqlite3.Error as e:
            print(f"Error getting average score: {e}")
            return 0.0
    
    def backup_database(self, backup_path: str = "snake_scores_backup.db"):
        """Create a backup of the high scores database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                backup = sqlite3.connect(backup_path)
                conn.backup(backup)
                backup.close()
                return True
        except sqlite3.Error as e:
            print(f"Error backing up database: {e}")
            return False