import matplotlib.pyplot as plt
from typing import List

def plot_training_stats(scores: List[float], mean_scores: List[float]) -> None:
    """
    Plot the training statistics for the AI
    
    Args:
        scores: List of scores from each game
        mean_scores: List of running mean scores
    """
    plt.figure(2)
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    if len(scores) > 0:
        plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    if len(mean_scores) > 0:
        plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)