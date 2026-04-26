import torch
import torch.nn as nn
import torch.nn.functional as F

class SudokuDifficultyPredictor(nn.Module):
    def __init__(self):
        super(SudokuDifficultyPredictor, self).__init__()
        
        self.conv1 = nn.Conv2d(10, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32) 
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64) 
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        self.fc1 = nn.Linear(10368 + 1, 256)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, 1)

    def forward(self, x, empty_count):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        
        x = x.view(x.size(0), -1) 
        x = torch.cat((x, empty_count), dim=1)
        
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        
        return x

# Quick test 
if __name__ == "__main__":
    model = SudokuDifficultyPredictor()
    dummy_grid = torch.zeros((5, 10, 9, 9))
    dummy_empty_spaces = torch.zeros((5, 1))
    output = model(dummy_grid, dummy_empty_spaces)
    print(f"Model built! Output shape: {output.shape}")