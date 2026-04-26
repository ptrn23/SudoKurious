from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import torch
import torch.nn.functional as F

from ai.heuristics import find_naked_single, find_hidden_single
from ai.cnn_model import SudokuDifficultyPredictor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #    "https://sudo-kurious.vercel.app",
    #    "http://localhost:3000"
    # ],
    allow_origins=["*"],
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
    
    naked_single_result = find_naked_single(request.board, request.variant, request.cages)
    if naked_single_result:
        row, col, value, explanation = naked_single_result
        print(f"Hint found: Naked Single at ({row}, {col}) -> {value}")
        return {
            "status": "success",
            "technique_used": "Naked Single",
            "highlight_cells": [[row, col]],
            "suggested_value": value,
            "explanation_text": explanation,
            "difficulty_score": formatted_difficulty 
        }

    hidden_single_result = find_hidden_single(request.board, request.variant, request.cages)
    if hidden_single_result:
        row, col, value, explanation = hidden_single_result
        print(f"Hint found: Hidden Single at ({row}, {col}) -> {value}")
        return {
            "status": "success",
            "technique_used": "Hidden Single",
            "highlight_cells": [[row, col]],
            "suggested_value": value,
            "explanation_text": explanation,
            "difficulty_score": formatted_difficulty 
        }
        
    return {
        "status": "pending",
        "technique_used": "none",
        "highlight_cells": [],
        "suggested_value": None,
        "explanation_text": "Hmm, I couldn't find a Naked or Hidden Single. The board requires more advanced logic!",
        "difficulty_score": formatted_difficulty 
    }