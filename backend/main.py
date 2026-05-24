from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import torch
import torch.nn.functional as F

from ai.heuristics import get_best_h_move, check_sudoku
from ai.genetic_algorithm import GeneticSudokuSolver
from ai.cnn_model import SudokuDifficultyPredictor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       "https://sudo-kurious.vercel.app",
       "http://localhost:3000"
    ],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading CNN Difficulty Predictor...")
device = torch.device("cpu")
difficulty_model = SudokuDifficultyPredictor().to(device)
difficulty_model.load_state_dict(torch.load("ai/cnn_weights.pth", map_location=device))
difficulty_model.eval()
print("Model loaded successfully!")

class Cage(BaseModel):
    sum: int
    cells: List[List[int]]

class SudokuRequest(BaseModel):
    variant: str
    board: List[List[int]]
    cages: Optional[List[Cage]] = []

@app.post("/api/get-hint")
def get_hint(request: SudokuRequest):
    print(f"\n--- NEW AI REQUEST: {request.variant.upper()} ---")
    
    board_tensor = torch.tensor(request.board, dtype=torch.long)
    empty_count = (board_tensor == 0).sum().to(torch.float32).view(1, 1) / 81.0
    board_one_hot = F.one_hot(board_tensor, num_classes=10).to(torch.float32)
    board_one_hot = board_one_hot.permute(2, 0, 1).unsqueeze(0) 
    
    with torch.no_grad():
        predicted_difficulty = difficulty_model(board_one_hot, empty_count).item()
        
    formatted_difficulty = round(predicted_difficulty, 1)
    print(f"CNN Predicted Difficulty: {formatted_difficulty}")
    
    h_result = get_best_h_move(request.board, request.variant, request.cages)
    if h_result:
        row, col, value, explanation = h_result.return_summary()
        print(f"Hint found: Naked Single at ({row}, {col}) -> {value}")
        return {
            "status": "success",
            "technique_used": "Naked Single",
            "highlight_cells": [[row, col]],
            "suggested_value": value,
            "explanation_text": explanation,
            "difficulty_score": formatted_difficulty 
        }
        
    print("Heuristics exhausted. Booting Genetic Algorithm...")
    
    ga_solver = GeneticSudokuSolver(
        request.board, 
        variant=request.variant, 
        cages=request.cages, 
        pop_size=250, 
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
                        f"I booted up the Genetic Algorithm, and after simulating thousands of generations, "
                        f"it guarantees that row {r + 1}, column {c + 1} must be {value}."
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
    
@app.post("/api/check-sudoku")
def get_hint(request: SudokuRequest):
    print(f"\n--- CHECKER REQUEST: {request.variant.upper()} ---")
    
    error_msg = check_sudoku(request.board, request.variant, request.cages)
    if error_msg:
        # paul, checks return_summary method ng class incorrectSudoku para alam mu ano rinereturn or ano usto mo pang i return
        if (error_msg == "Complete Sudoku"):
            return {
                "status": "success",
                "explanation_text": "Complete Sudoku",
            }
        
        offending_locs, value, explanation = error_msg.return_summary()
        return {
            "status": "success",
            "highlight_cells": offending_locs,
            "error_value": value,
            "explanation_text": explanation,
        }
        
