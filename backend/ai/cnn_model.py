import torch
import torch.nn as nn
import torch.nn.functional as F

class SudokuDifficultyPredictor(nn.Module):
    def __init__(self):
        super(SudokuDifficultyPredictor, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 9 * 9, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)

    def forward(self, x):
        # x expected shape: [batch_size, 1, 9, 9]
        
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        x = self.fc3(x)
        
        return x

if __name__ == "__main__":
    model = SudokuDifficultyPredictor()
    dummy_input = torch.zeros((5, 1, 9, 9)) 
    output = model(dummy_input)
    
    print(f"Model successfully built!")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape} (Batch of 5, single difficulty score)")