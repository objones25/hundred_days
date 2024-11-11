import os
import json
import torch
import shutil
from datetime import datetime
from typing import Optional, Dict, List

class SaveLoadManager:
    def __init__(self, base_dir: str = 'training_states', max_saves: int = 5):
        self.base_dir = base_dir
        self.max_saves = max_saves
        os.makedirs(self.base_dir, exist_ok=True)
        
    def save_state(self, agent, force: bool = False) -> None:
        """Save training state with improved efficiency"""
        # Only save every 50 games unless forced
        if not force and agent.n_games % 50 != 0:
            return
            
        # Create new state directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        state_path = os.path.join(self.base_dir, f'training_state_{timestamp}')
        os.makedirs(state_path, exist_ok=True)
        
        try:
            # Save model state
            model_path = os.path.join(state_path, 'model.pth')
            torch.save({
                'model_state_dict': agent.model.state_dict(),
                'optimizer_state_dict': agent.trainer.optimizer.state_dict(),
                'n_games': agent.n_games,
                'epsilon': agent.epsilon,
                'record': agent.record
            }, model_path)
            
            # Save minimal training stats
            stats_path = os.path.join(state_path, 'stats.json')
            essential_stats = {
                'scores': agent.scores[-1000:],  # Keep last 1000 scores
                'mean_scores': agent.mean_scores[-1000:],
                'record': agent.record,
                'n_games': agent.n_games
            }
            with open(stats_path, 'w') as f:
                json.dump(essential_stats, f)
                
            # Cleanup old saves
            self._cleanup_old_saves()
            
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def load_latest_state(self, agent) -> Optional[Dict]:
        """Load the most recent training state"""
        try:
            # Find most recent state
            states = sorted([d for d in os.listdir(self.base_dir) 
                           if d.startswith('training_state_')])
            if not states:
                return None
                
            latest_state = states[-1]
            state_path = os.path.join(self.base_dir, latest_state)
            
            # Load model
            model_path = os.path.join(state_path, 'model.pth')
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path)
                agent.model.load_state_dict(checkpoint['model_state_dict'])
                agent.trainer.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                agent.n_games = checkpoint['n_games']
                agent.epsilon = checkpoint['epsilon']
                agent.record = checkpoint['record']
                
                # Load stats
                stats_path = os.path.join(state_path, 'stats.json')
                if os.path.exists(stats_path):
                    with open(stats_path, 'r') as f:
                        stats = json.load(f)
                        agent.scores = stats['scores']
                        agent.mean_scores = stats['mean_scores']
                
                print(f"Loaded training state from {state_path}")
                return stats
            
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    def _cleanup_old_saves(self):
        """Keep only the most recent max_saves states"""
        states = sorted([d for d in os.listdir(self.base_dir) 
                        if d.startswith('training_state_')])
        
        # Remove oldest states if we exceed max_saves
        while len(states) > self.max_saves:
            oldest_state = states.pop(0)
            shutil.rmtree(os.path.join(self.base_dir, oldest_state))
    
    def load_best_model(self, agent) -> Optional[Dict]:
        """Load the model with the highest score"""
        try:
            best_score = -1
            best_state = None
            
            # Find state with highest score
            for state in os.listdir(self.base_dir):
                if state.startswith('training_state_'):
                    state_path = os.path.join(self.base_dir, state)
                    stats_path = os.path.join(state_path, 'stats.json')
                    
                    if os.path.exists(stats_path):
                        with open(stats_path, 'r') as f:
                            stats = json.load(f)
                            if stats['record'] > best_score:
                                best_score = stats['record']
                                best_state = state
            
            if best_state:
                state_path = os.path.join(self.base_dir, best_state)
                model_path = os.path.join(state_path, 'model.pth')
                
                checkpoint = torch.load(model_path)
                agent.model.load_state_dict(checkpoint['model_state_dict'])
                print(f"Loaded best model from {state_path} (score: {best_score})")
                return {'record': best_score}
                
        except Exception as e:
            print(f"Error loading best model: {e}")
            return None