import pandas as pd
import numpy as np
import time

def parse_board(board):
    board = str(board).replace('.', '0')
    return np.array([int(char) for char in board]).reshape((9, 9))

def process_dataset(csv_path):
    print(f"Loading dataset from {csv_path}...")
    start_time = time.time()
    df = pd.read_csv(csv_path, nrows=1000) 
    print("Converting strings to 9x9 matrices...")
    df['parsed_puzzle'] = df['puzzle'].apply(parse_board)
    df['parsed_solution'] = df['solution'].apply(parse_board)
    end_time = time.time()
    print(f"Processed {len(df)} puzzles in {round(end_time - start_time, 4)} seconds.")
    
    print("\nsample board:")
    print(df['parsed_puzzle'].iloc[0])

if __name__ == "__main__":
    process_dataset("data/sudoku-3m.csv")