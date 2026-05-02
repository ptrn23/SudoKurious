import numpy as np
import joblib
import time
from ai.advanced_forest import extract_advanced_features

def board_to_string(board_array):
    return "".join(str(int(cell)) if cell != 0 else "." for cell in board_array.flatten())

def find_perfect_boards(npz_path, model_path, sample_size=200000):
    print("Loading Dataset and Model...")
    data = np.load(npz_path)
    
    puzzles = data['puzzles'][:sample_size]
    actual_ratings = data['ratings'][:sample_size]
    
    model = joblib.load(model_path)
    
    print(f"Extracting features for {sample_size} boards (this takes ~5 seconds)...")
    features = np.array([extract_advanced_features(b) for b in puzzles])
    
    print("Predicting difficulties on 1-5 scale...")
    predicted_ratings = model.predict(features)
    
    errors = np.abs(actual_ratings - predicted_ratings)
    
    easy_mask = (actual_ratings >= 1.2) & (actual_ratings <= 1.8)
    medium_mask = (actual_ratings >= 2.5) & (actual_ratings <= 3.5)
    hard_mask = (actual_ratings >= 4.2) & (actual_ratings <= 5.0)
    
    print("\n" + "="*40)
    print("=== THE GOLDEN SAMPLE BOARDS (1-5 SCALE) ===")
    print("="*40)
    
    for label, mask in [("EASY", easy_mask), ("MEDIUM", medium_mask), ("HARD", hard_mask)]:
        if not np.any(mask):
            print(f"\nNo {label} boards found in this sample!")
            continue
        
        valid_indices = np.where(mask)[0]
        best_idx = valid_indices[np.argmin(errors[valid_indices])]
        
        board_str = board_to_string(puzzles[best_idx])
        actual = actual_ratings[best_idx]
        pred = predicted_ratings[best_idx]
        error = errors[best_idx]
        
        print(f"\n[{label} BOARD]")
        print(f"Actual Truth : {actual:.2f}")
        print(f"AI Predicted : {pred:.2f}")
        print(f"Margin Error : {error:.4f}")
        print(f"Board String : {board_str}")

if __name__ == "__main__":
    find_perfect_boards("data/sudoku_dataset.npz", "ai/advanced_forest.pkl")