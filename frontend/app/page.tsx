"use client";
import { useState } from "react";

export default function Home() {
  const [board, setBoard] = useState(
    Array(9).fill(null).map(() => Array(9).fill(0))
  );

  const [variant, setVariant] = useState("standard");
  const [hint, setHint] = useState("Click 'Get Hint' to test the AI!");

  const handleChange = (row: number, col: number, value: string) => {
    const newBoard = [...board];
    newBoard[row][col] = value === "" ? 0 : parseInt(value.slice(-1)) || 0; 
    setBoard(newBoard);
  };

  const fetchHint = async () => {
    setHint("Thinking...");
    try {
      const response = await fetch("http://localhost:8000/api/get-hint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          variant: variant,
          board: board,
        }),
      });
      
      const data = await response.json();
      setHint(data.explanation_text);
      
    } catch (error) {
      setHint("Error: Could not connect to the AI server.");
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 text-white p-4">
      <h1 className="text-4xl font-bold mb-8 text-emerald-400">SudoKurious</h1>
      
      <div className="mb-6 flex items-center space-x-3">
        <label className="text-slate-300 font-medium">Game Mode:</label>
        <select 
          value={variant} 
          onChange={(e) => setVariant(e.target.value)}
          className="p-2 bg-slate-800 text-white rounded border border-slate-600 focus:outline-none focus:border-emerald-400"
        >
          <option value="standard">Standard (9x9)</option>
          <option value="x-sudoku">X-Sudoku (Diagonals)</option>
          <option value="killer">Killer Sudoku (Sum Cages)</option>
        </select>
      </div>

      {/* The 9x9 Grid */}
      <div className="grid grid-cols-9 gap-1 bg-slate-700 p-1 rounded-sm">
        {board.map((row, rIndex) =>
          row.map((cell, cIndex) => (
            <input
              key={`${rIndex}-${cIndex}`}
              type="text"
              value={cell === 0 ? "" : cell}
              onChange={(e) => handleChange(rIndex, cIndex, e.target.value)}
              className="w-10 h-10 text-center text-xl bg-slate-800 text-white focus:bg-slate-600 focus:outline-none"
            />
          ))
        )}
      </div>

      {/* The Controls */}
      <button 
        onClick={fetchHint}
        className="mt-8 px-6 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold rounded"
      >
        Get Hint
      </button>

      {/* The Output Box */}
      <div className="mt-6 p-4 bg-slate-800 rounded w-80 text-center border border-slate-700">
        <p className="text-slate-300">{hint}</p>
      </div>
    </main>
  );
}