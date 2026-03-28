from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
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
    print("BOARD RECEIVED!")
    print(f"Variant: {request.variant.upper()}")
    
    if request.variant == "killer":
        print(f"Total Cages Received: {len(request.cages)}")
        for i, cage in enumerate(request.cages):
            print(f"  Cage {i+1} -> Sum: {cage.sum}, Coordinates: {cage.cells}")
    
        return {
            "status": "success",
            "technique_used": "handshake_test",
            "highlight_cells": [[0, 0]],
            "suggested_value": 7,
            "explanation_text": f"Success! Backend received {request.variant.upper()} mode with {len(request.cages)} cages!"
        }
    
    return {
        "status": "success",
        "technique_used": "handshake_test",
        "highlight_cells": [[0, 0]],
        "suggested_value": 7,
        "explanation_text": f"Success! Backend received {request.variant.upper()} board!"
    }