from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import joblib

from ai.advanced_forest import extract_advanced_features
from ai.heuristics import find_naked_single, find_hidden_single, get_best_h_move, check_sudoku
from ai.genetic_algorithm import GeneticSudokuSolver

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       "https://sudo-kurious.vercel.app",
       "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Advanced Random Forest Predictor...")
difficulty_model = joblib.load("ai/advanced_forest.pkl")
print("Random Forest Model loaded successfully!")

class Cage(BaseModel):
    sum: int
    cells: List[List[int]]

class SudokuRequest(BaseModel):
    variant: str
    board: List[List[int]]
    cages: Optional[List[Cage]] = []

class HintResponse(BaseModel):
    status: str
    technique_used: str
    highlight_cells: List[List[int]]
    suggested_value: Optional[int] = None
    explanation_text: str
    difficulty_score: float

class CheckResponse(BaseModel):
    status: str
    explanation_text: str
    highlight_cells: Optional[List[List[int]]] = []
    error_value: Optional[int] = None

def predict_difficulty(grid):
    board_np = np.array(grid)
    
    features = extract_advanced_features(board_np)
    prediction = difficulty_model.predict([features])[0]
    
    final_difficulty = max(0.0, min(8.5, prediction))
    
    return round(final_difficulty, 1)


@app.post("/api/get-hint", response_model=HintResponse)
def get_hint(request: SudokuRequest):
    print(f"\n--- NEW AI REQUEST: {request.variant.upper()} ---")
    
    formatted_difficulty = predict_difficulty(request.board)
    print(f"Random Forest Predicted Difficulty: {formatted_difficulty}")

    is_full = all(all(cell != 0 for cell in row) for row in request.board)
    if is_full:
        error_check = check_sudoku(request.board, request.variant, request.cages)
        if error_check == "Complete Sudoku":
            return {
                "status": "success",
                "technique_used": "Full Board",
                "highlight_cells": [],
                "suggested_value": None,
                "explanation_text": "The Sudoku is already solved! Congratulations!",
                "difficulty_score": formatted_difficulty 
            }
    
    h_result = get_best_h_move(request.board, request.variant, request.cages)
    if h_result:
        if hasattr(h_result, 'return_summary'):
            row, col, value, explanation = h_result.return_summary()
        elif isinstance(h_result, tuple):
            row, col, value, explanation = h_result
        else:
            return {
                "status": "error",
                "technique_used": "Error",
                "highlight_cells": [],
                "suggested_value": None,
                "explanation_text": "Backend error: Unrecognized move format.",
                "difficulty_score": formatted_difficulty
            }

        print(f"Hint found at ({row}, {col}) -> {value}")
        return {
            "status": "success",
            "technique_used": "Logic Heuristic", 
            "highlight_cells": [[int(row), int(col)]],
            "suggested_value": int(value),
            "explanation_text": str(explanation),
            "difficulty_score": formatted_difficulty 
        }
        
    print("Heuristics exhausted. Booting Memetic Algorithm...")
    
    ga_solver = GeneticSudokuSolver(
        request.board, 
        variant=request.variant, 
        cages=request.cages, 
        pop_size=100, 
        max_generations=1500
    )
    
    solved_board = ga_solver.solve()
    
    if solved_board:
        for r in range(9):
            for c in range(9):
                if request.board[r][c] == 0:
                    value = solved_board[r][c]
                    explanation = (
                        f"This board is too complex for basic human logic! "
                        f"I booted up the Memetic Algorithm, and after simulating thousands of generations, "
                        f"we can try {value} in row {r + 1}, column {c + 1}."
                    )
                    return {
                        "status": "success",
                        "technique_used": "Genetic Algorithm Fallback",
                        "highlight_cells": [[r, c]],
                        "suggested_value": value,
                        "explanation_text": explanation,
                        "difficulty_score": formatted_difficulty 
                    }
                    
    return {
        "status": "pending",
        "technique_used": "none",
        "highlight_cells": [],
        "suggested_value": None,
        "explanation_text": "I threw my best heuristics and genetic algorithms at this, and I'm stumped! Make sure the board doesn't have any conflicting numbers.",
        "difficulty_score": formatted_difficulty 
    }
    
@app.post("/api/check-sudoku", response_model=CheckResponse)
def check_sudoku_endpoint(request: SudokuRequest):
    print(f"\n--- CHECKER REQUEST: {request.variant.upper()} ---")
    
    error_msg = check_sudoku(request.board, request.variant, request.cages)
    
    if error_msg == "Complete Sudoku":
        return {
            "status": "success",
            "explanation_text": "Congratulations! The Sudoku is completely solved and valid!",
            "highlight_cells": [],
            "error_value": None
        }
    
    elif error_msg:
        offending_locs, value, friendly_explanation = error_msg.return_summary()
        
        formatted_highlights = [list(loc) for loc in offending_locs]
        
        return {
            "status": "error",
            "highlight_cells": formatted_highlights,
            "error_value": value,
            "explanation_text": friendly_explanation,
        }
        
    return {
        "status": "valid",
        "explanation_text": "Looking good so far! No conflicts detected.",
        "highlight_cells": [],
        "error_value": None
    }