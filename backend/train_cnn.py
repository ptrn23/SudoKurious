import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
import numpy as np
import time

from ai.cnn_model import SudokuDifficultyPredictor

def load_data_with_split(npz_path, batch_size=256):
    print(f"Loading dataset from {npz_path}...")
    data = np.load(npz_path)
    
    puzzles_np = data['puzzles']
    ratings_np = data['ratings']
    
    print("Balancing zero-inflated dataset...")
    zeros_idx = np.where(ratings_np == 0.0)[0]
    non_zeros_idx = np.where(ratings_np > 0.0)[0]
    
    np.random.seed(42)
    np.random.shuffle(zeros_idx)
    balanced_zeros_idx = zeros_idx[:len(non_zeros_idx)]
    
    balanced_idx = np.concatenate([balanced_zeros_idx, non_zeros_idx])
    np.random.shuffle(balanced_idx)
    balanced_idx = balanced_idx[:400000]
    
    puzzles_np = puzzles_np[balanced_idx]
    ratings_np = ratings_np[balanced_idx]
    print(f"Balanced Dataset Size: {len(ratings_np)} puzzles.")
    
    X_tensor = torch.tensor(puzzles_np, dtype=torch.long)
    empty_counts = (X_tensor == 0).sum(dim=(1, 2)).to(torch.float32).view(-1, 1) / 81.0
    X_one_hot = F.one_hot(X_tensor, num_classes=10).to(torch.float32)
    X_one_hot = X_one_hot.permute(0, 3, 1, 2)
    
    y_tensor = torch.tensor(ratings_np, dtype=torch.float32).view(-1, 1)
    
    print("Splitting into 80% Training and 20% Validation...")
    X_train, X_val, counts_train, counts_val, y_train, y_val = train_test_split(
        X_one_hot, empty_counts, y_tensor, test_size=0.2, random_state=42
    )
    
    train_loader = DataLoader(TensorDataset(X_train, counts_train, y_train), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_val, counts_val, y_val), batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader

def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    model = SudokuDifficultyPredictor().to(device)
    criterion = nn.L1Loss() 
    
    optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-5)
    
    train_loader, val_loader = load_data_with_split("data/sudoku_dataset.npz")
    epochs = 5 
    
    print("\n--- START TRAINING LOOP ---")
    
    for epoch in range(epochs):
        start_time = time.time()
        
        model.train()
        train_loss = 0.0
        
        for batch_idx, (boards, counts, ratings) in enumerate(train_loader):
            boards, counts, ratings = boards.to(device), counts.to(device), ratings.to(device)
            
            optimizer.zero_grad()
            
            predictions = model(boards, counts)
            
            loss = criterion(predictions, ratings)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            if batch_idx % 100 == 99:
                print(f"Epoch [{epoch+1}/{epochs}], Train Batch [{batch_idx+1}/{len(train_loader)}], Train MAE: {loss.item():.4f}")
        
        avg_train_loss = train_loss / len(train_loader)
        
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for boards, counts, ratings in val_loader:
                boards, counts, ratings = boards.to(device), counts.to(device), ratings.to(device)
                predictions = model(boards, counts)
                loss = criterion(predictions, ratings)
                val_loss += loss.item()
                
        avg_val_loss = val_loss / len(val_loader)
        
        epoch_time = time.time() - start_time
        print(f"*** Epoch {epoch+1} | Time: {epoch_time:.1f}s | Train MAE: {avg_train_loss:.4f} | VAL MAE: {avg_val_loss:.4f} ***\n")
        
    torch.save(model.state_dict(), "ai/cnn_weights.pth")
    print("Training complete! Deep model saved.")

if __name__ == "__main__":
    train_model()