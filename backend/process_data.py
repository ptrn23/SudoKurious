import pandas as pd
import numpy as np
import time
import os

def parse_board(board):
    board = str(board).replace('.', '0')
    # use int8 to save memory since values are between 0-9
    return np.array([int(char) for char in board], dtype=np.int8).reshape((9, 9))

def process_and_save_dataset(csv_path, output_dir="data", limit=None):
    print(f"Loading dataset from {csv_path}...")
    start_time = time.time()
    df = pd.read_csv(csv_path, nrows=limit) 
    
    print("Converting strings to 9x9 matrices...")
    X_puzzles = np.array([parse_board(b) for b in df['puzzle']])
    y_solutions = np.array([parse_board(b) for b in df['solution']])
    y_ratings = df['difficulty'].values
    
    print("Saving to compressed NumPy file...")
    os.makedirs(output_dir, exist_ok=True)
    
    save_path = os.path.join(output_dir, "sudoku_dataset.npz")
    np.savez_compressed(
        save_path,
        puzzles=X_puzzles,
        solutions=y_solutions,
        ratings=y_ratings
    )
    
    end_time = time.time()
    print(f"Success! Saved {len(df)} puzzles to {save_path} in {round(end_time - start_time, 2)} seconds.")

if __name__ == "__main__":
    process_and_save_dataset("data/sudoku-3m.csv", limit=1000000)