import joblib
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def extract_advanced_features(board):
    clues = np.sum(board != 0)
    empty_coords = np.argwhere(board == 0)
    
    if len(empty_coords) == 0:
        return [clues, 0, 0, 0, 0, 0, 0]
    
    candidates_list = []
    
    for r, c in empty_coords:
        row_used = board[r, :]
        col_used = board[:, c]
        box_r, box_c = (r // 3) * 3, (c // 3) * 3
        box_used = board[box_r:box_r+3, box_c:box_c+3].flatten()
        
        used = set(row_used) | set(col_used) | set(box_used)
        used.discard(0)
        
        candidates_list.append(9 - len(used))
        
    candidates_arr = np.array(candidates_list)
    
    naked_singles = np.sum(candidates_arr == 1)
    min_candidates = np.min(candidates_arr)
    max_candidates = np.max(candidates_arr)
    avg_candidates = np.mean(candidates_arr)
    search_space = np.sum(np.log(np.maximum(candidates_arr, 1)))
    almost_full_rows = np.sum((np.sum(board != 0, axis=1) >= 7) & (np.sum(board != 0, axis=1) < 9))
    almost_full_cols = np.sum((np.sum(board != 0, axis=0) >= 7) & (np.sum(board != 0, axis=0) < 9))
    
    box_clues = []
    for br in range(3):
        for bc in range(3):
            box_clues.append(np.sum(board[br*3:(br+1)*3, bc*3:(bc+1)*3] != 0))
    almost_full_boxes = np.sum((np.array(box_clues) >= 7) & (np.array(box_clues) < 9))
    
    easy_zones = almost_full_rows + almost_full_cols + almost_full_boxes
    
    return [
        clues, 
        naked_singles, 
        min_candidates, 
        max_candidates, 
        avg_candidates, 
        search_space, 
        easy_zones
    ]

def run_advanced_forest(npz_path):
    print("Loading continuous dataset...")
    data = np.load(npz_path)
    
    limit = 500000
    puzzles_np = data['puzzles'][:limit]
    raw_ratings = data['ratings'][:limit]
    
    print("Remapping difficulty scale to 1-5...")
    ratings_np = 1 + (raw_ratings / 8.5) * 4
    
    print(f"Extracting Advanced Features for {limit} boards. This might take ~25 seconds...")
    start_time = time.time()
    
    X_features = np.array([extract_advanced_features(b) for b in puzzles_np])
    y_target = ratings_np
    
    print(f"Feature Extraction Complete! (Took {time.time() - start_time:.1f}s)")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_features, y_target, test_size=0.2, random_state=42
    )
    
    print("Training Advanced Random Forest...")
    model = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    print("Evaluating Model...")
    predictions = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("\n=== ADVANCED FOREST STATISTICS ===")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"R-squared (R2 Score): {r2:.4f}")
    
    print("\n=== FEATURE IMPORTANCE RANKING ===")
    feature_names = [
        "Total Clues", 
        "Naked Singles", 
        "Min Candidates", 
        "Max Candidates", 
        "Avg Candidates", 
        "Log Search Space", 
        "Easy Zones"
    ]
    
    importances = model.feature_importances_
    ranked_features = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    
    for name, importance in ranked_features:
        print(f"{name}: {importance * 100:.2f}%")

    print("\nSaving the Advanced Random Forest for production...")
    joblib.dump(model, "ai/advanced_forest.pkl", compress=3) 
    print("Saved to ai/advanced_forest.pkl!")

if __name__ == "__main__":
    run_advanced_forest("data/sudoku_dataset.npz")