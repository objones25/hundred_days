# AI Snake Game

An implementation of the classic Snake game with multiple AI approaches including Reinforcement Learning, A* Pathfinding, and Hamiltonian Cycle algorithms.

## Features

- Classic Snake game implementation
- Multiple AI approaches:
  - Deep Q-Learning (Reinforcement Learning)
  - A* Pathfinding
  - Hamiltonian Cycle
  - Hybrid approach (configurable)
- Training visualization with real-time metrics
- High score system with SQLite database
- Configurable game settings and themes
- Save/Load functionality for trained models

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/snake-game.git
cd snake-game
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the game:
```bash
python main.py
```

### Controls
- Arrow keys: Control snake direction
- ESC: Pause game/Return to menu
- Enter: Select menu item

### Game Modes
1. Manual Play
   - Classic snake game controlled by the player

2. AI Mode
   - Reinforcement Learning: Self-learning AI using Deep Q-Learning
   - A* Pathfinding: Optimal pathfinding to food
   - Hamiltonian Cycle: Complete coverage strategy
   - Hybrid: Combined approach for optimal performance

## Project Structure
```
snake_game/
├── ai/
│   ├── base.py
│   ├── pathfinding/
│   │   ├── astar.py
│   │   └── hamilton.py
│   └── reinforcement/
│       ├── agent.py
│       ├── model.py
│       ├── memory.py
│       └── trainer.py
├── core/
│   ├── game.py
│   ├── constants.py
│   └── theme.py
├── utils/
│   ├── visualization.py
│   ├── persistence.py
│   └── logger.py
└── main.py
```

## Configuration

Game settings can be modified in `core/constants.py`:
- Window size
- Grid size
- Initial speed
- AI difficulty levels

AI parameters can be adjusted in `ai/reinforcement/config.py`:
- Learning rate
- Discount factor
- Memory size
- Exploration parameters

## Training Data

All training data is stored in:
- `training_states/`: Saved model states
- `training_stats/`: Training statistics
- `models/`: Trained model weights
- `snake_scores.db`: High score database

Note: These directories are excluded from version control.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Reinforcement Learning implementation inspired by DeepMind's DQN papers
- A* pathfinding algorithm based on classic implementations
- Special thanks to contributors and testers