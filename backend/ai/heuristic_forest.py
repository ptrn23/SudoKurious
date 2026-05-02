import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

def extract_features(board):
    """Calculates heuristic data for a single 9x9 Sudoku board."""
    clues = np.sum(board != 0)
    empty_coords = np.argwhere(board == 0)
    
    naked_singles = 0
    total_candidates = 0
    max_candidates = 0
    
    for r, c in empty_coords:
        row_used = board[r, :]
        col_used = board[:, c]
        box_r, box_c = (r // 3) * 3, (c // 3) * 3
        box_used = board[box_r:box_r+3, box_c:box_c+3].flatten()
        
        used = set(row_used) | set(col_used) | set(box_used)
        used.discard(0)
        
        candidates = 9 - len(used)
        total_candidates += candidates
        
        if candidates == 1:
            naked_singles += 1
        if candidates > max_candidates:
            max_candidates = candidates
            
    avg_candidates = total_candidates / len(empty_coords) if len(empty_coords) > 0 else 0
    
    return [clues, naked_singles, avg_candidates, max_candidates]

def run_heuristic_forest(npz_path):
    print("Loading continuous dataset...")
    data = np.load(npz_path)
    
    limit = 50000 
    puzzles_np = data['puzzles'][:limit]
    ratings_np = data['ratings'][:limit]
    
    print(f"Extracting Heuristic Features for {limit} boards. This will take ~10-20 seconds...")
    start_time = time.time()
    
    X_features = np.array([extract_features(b) for b in puzzles_np])
    y_target = ratings_np
    
    print(f"Feature Extraction Complete! (Took {time.time() - start_time:.1f}s)")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_features, y_target, test_size=0.2, random_state=42
    )
    
    print("Training Random Forest on Heuristics...")
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    print("Evaluating Model...")
    predictions = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("\n=== HEURISTIC FOREST STATISTICS ===")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"R-squared (R2 Score): {r2:.4f}")
    
    print("\n=== WHAT DID THE AI LEARN? ===")
    feature_names = ["Total Clues", "Naked Singles", "Avg Degrees of Freedom", "Max Candidates"]
    importances = model.feature_importances_
    
    for name, importance in zip(feature_names, importances):
        print(f"{name}: {importance * 100:.2f}% importance")

if __name__ == "__main__":
    run_heuristic_forest("data/sudoku_dataset.npz")