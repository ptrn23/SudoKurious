from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SudokuRequest(BaseModel):
    variant: str
    board: List[List[int]]

@app.post("/api/get-hint")
def get_hint(request: SudokuRequest):
    print(f"Received a {request.variant} board!")
    
    return {
        "status": "success",
        "technique_used": "handshake_test",
        "highlight_cells": [[0, 0]],
        "suggested_value": 7,
        "explanation_text": f"Connection successful! You are playing {request.variant.upper()}."
    }