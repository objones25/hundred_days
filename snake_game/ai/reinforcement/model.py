# model.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class SnakeNN(nn.Module):
    """Neural network model for the Snake agent"""
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network"""
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x
    
    def save(self, file_name: str = 'model.pth') -> None:
        """Save the model to a file"""
        model_folder_path = './models'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
            
        file_path = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_path)
        
    def load(self, file_name: str = 'model.pth') -> None:
        """Load the model from a file"""
        model_folder_path = './models'
        file_path = os.path.join(model_folder_path, file_name)
        
        if os.path.exists(file_path):
            self.load_state_dict(torch.load(file_path))
            self.eval()  # Set to evaluation mode
