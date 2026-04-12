from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from ai.heuristics import find_naked_single

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Cage(BaseModel):
    sum: int
    cells: List[List[int]]

class SudokuRequest(BaseModel):
    variant: str
    board: List[List[int]]
    cages: Optional[List[Cage]] = []

@app.post("/api/get-hint")
def get_hint(request: SudokuRequest):
    naked_single_result = find_naked_single(request.board)
    
    if naked_single_result:
        row, col, value, explanation = naked_single_result
        print(f"Hint found: Naked Single at ({row}, {col}) -> {value}")
        return {
            "status": "success",
            "technique_used": "Naked Single",
            "highlight_cells": [[row, col]],
            "suggested_value": value,
            "explanation_text": explanation
        }
    
    print("No Naked Single found.")
    return {
        "status": "pending",
        "technique_used": "none",
        "highlight_cells": [],
        "suggested_value": None,
        "explanation_text": "Hmm, I couldn't find a simple 'Naked Single' here."
    }