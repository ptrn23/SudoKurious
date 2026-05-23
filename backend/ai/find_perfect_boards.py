import numpy as np
import joblib
from ai.advanced_forest import extract_advanced_features

def board_to_string(board_array):
    return "".join(str(int(cell)) if cell != 0 else "." for cell in board_array.flatten())

def find_perfect_boards(npz_path, model_path, sample_size=500000):
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
    
    easy_mask     = (actual_ratings >= 0.2) & (actual_ratings <= 0.8) & (predicted_ratings >= 0.2) & (predicted_ratings <= 0.8)
    medium_mask   = (actual_ratings >= 1.2) & (actual_ratings <= 1.8) & (predicted_ratings >= 1.2) & (predicted_ratings <= 1.8)
    hard_mask     = (actual_ratings >= 2.2) & (actual_ratings <= 2.8) & (predicted_ratings >= 2.2) & (predicted_ratings <= 2.8)
    fiendish_mask = (actual_ratings >= 3.2) & (actual_ratings <= 3.8) & (predicted_ratings >= 3.2) & (predicted_ratings <= 3.8)
    evil_mask     = (actual_ratings >= 4.2) & (actual_ratings <= 4.8) & (predicted_ratings >= 4.2) & (predicted_ratings <= 4.8)
    
    print("\n" + "="*40)
    print("=== SAMPLE BOARDS ===")
    print("="*40)
    
    categories = [
        ("EASY", easy_mask), 
        ("MEDIUM", medium_mask), 
        ("HARD", hard_mask),
        ("FIENDISH", fiendish_mask),
        ("EVIL", evil_mask)
    ]
    
    for label, mask in categories:
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