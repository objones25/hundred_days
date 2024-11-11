import matplotlib.pyplot as plt
from typing import List, Dict
import numpy as np

def plot_training_stats(scores: List[float], mean_scores: List[float], training_stats: Dict) -> None:
    """Plot training statistics with better visibility and error handling"""
    try:
        plt.figure(2, figsize=(12, 8))  # Use figure 2 to avoid conflicts
        plt.clf()
        
        # Plot scores
        plt.subplot(2, 2, 1)
        plt.title('Training Progress')
        plt.xlabel('Game')
        plt.ylabel('Score')
        plt.plot(scores, label='Score', color='lightblue', alpha=0.6)
        plt.plot(mean_scores, label='Average', color='blue', linewidth=2)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Plot epsilon decay
        plt.subplot(2, 2, 2)
        plt.title('Exploration Rate (ε)')
        plt.xlabel('Game')
        plt.ylabel('Epsilon')
        plt.plot(training_stats['epsilons'], color='green')
        plt.grid(True, alpha=0.3)
        
        # Plot rewards
        plt.subplot(2, 2, 3)
        plt.title('Rewards per Episode')
        plt.xlabel('Game')
        plt.ylabel('Total Reward')
        plt.plot(training_stats['rewards'], color='red')
        plt.grid(True, alpha=0.3)
        
        # Plot memory usage
        plt.subplot(2, 2, 4)
        plt.title('Experience Memory')
        plt.xlabel('Game')
        plt.ylabel('Stored Experiences')
        plt.plot(training_stats['memory_size'], color='purple')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.draw()  # Draw the plot
        plt.pause(0.001)  # Very short pause to allow plot to update
    except Exception as e:
        print(f"Error in visualization: {e}")