"use client";
import { useState } from "react";
import { Outfit, Newsreader } from "next/font/google";
import { Grid3X3, X as XIcon, Calculator } from "lucide-react";

const outfit = Outfit({ subsets: ["latin"] });
const newsreader = Newsreader({ subsets: ["latin"], style: ['normal', 'italic'] });

export default function Home() {
  const [board, setBoard] = useState(
    Array(9).fill(null).map(() => Array(9).fill(0))
  );
  const [variant, setVariant] = useState<"standard" | "x-sudoku" | "killer">("standard");
  const [hint, setHint] = useState("Click 'Get Hint' to test the AI!");

  const themeColors = {
    "standard": { button: "bg-blue-600 hover:bg-blue-700", text: "text-blue-600", ring: "focus:ring-blue-200" },
    "x-sudoku": { button: "bg-orange-500 hover:bg-orange-600", text: "text-orange-500", ring: "focus:ring-orange-200" },
    "killer":   { button: "bg-red-500 hover:bg-red-600", text: "text-red-500", ring: "focus:ring-red-200" }
  };

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
        body: JSON.stringify({ variant, board }),
      });
      const data = await response.json();
      setHint(data.explanation_text);
    } catch (error) {
      setHint("Error: Could not connect to the AI server.");
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center py-16 bg-slate-50">
      
      <h1 className={`${newsreader.className} text-6xl font-bold tracking-tight mb-2 ${themeColors[variant].text}`}>
        SudoKurious
      </h1>

      <div className="mb-8 flex items-center space-x-3">
        <button
          onClick={() => setVariant("standard")}
          className={`${outfit.className} flex items-center px-5 py-2 rounded-full border-2 font-bold transition-all ${
            variant === "standard" 
              ? "bg-blue-50 border-blue-500 text-blue-600 shadow-sm" 
              : "bg-white border-slate-200 text-slate-500 hover:bg-slate-50"
          }`}
        >
          <Grid3X3 className="w-5 h-5 mr-2" />
          Standard
        </button>

        <button
          onClick={() => setVariant("x-sudoku")}
          className={`${outfit.className} flex items-center px-5 py-2 rounded-full border-2 font-bold transition-all ${
            variant === "x-sudoku" 
              ? "bg-orange-50 border-orange-500 text-orange-600 shadow-sm" 
              : "bg-white border-slate-200 text-slate-500 hover:bg-slate-50"
          }`}
        >
          <XIcon className="w-5 h-5 mr-2" />
          X-Sudoku
        </button>

        <button
          onClick={() => setVariant("killer")}
          className={`${outfit.className} flex items-center px-5 py-2 rounded-full border-2 font-bold transition-all ${
            variant === "killer" 
              ? "bg-red-50 border-red-500 text-red-600 shadow-sm" 
              : "bg-white border-slate-200 text-slate-500 hover:bg-slate-50"
          }`}
        >
          <Calculator className="w-5 h-5 mr-2" />
          Killer Sudoku
        </button>
      </div>

      <div className="bg-white p-3 rounded-2xl shadow-xl border border-slate-100 mb-8">
        <div className="grid grid-cols-9 border-4 border-slate-700 rounded-sm overflow-hidden">
          {board.map((row, rIndex) =>
            row.map((cell, cIndex) => {
              const isRightBorder = (cIndex + 1) % 3 === 0 && cIndex !== 8;
              const isBottomBorder = (rIndex + 1) % 3 === 0 && rIndex !== 8;
              
              return (
                <input
                  key={`${rIndex}-${cIndex}`}
                  type="text"
                  value={cell === 0 ? "" : cell}
                  onChange={(e) => handleChange(rIndex, cIndex, e.target.value)}
                  className={`${outfit.className} w-12 h-12 sm:w-14 sm:h-14 text-center text-2xl font-bold text-slate-800 bg-white 
                    focus:bg-slate-50 focus:outline-none focus:ring-4 focus:ring-inset focus:z-10 ${themeColors[variant].ring}
                    ${isRightBorder ? "border-r-2 border-r-slate-400" : "border-r border-r-slate-200"}
                    ${isBottomBorder ? "border-b-2 border-b-slate-400" : "border-b border-b-slate-200"}
                  `}
                />
              );
            })
          )}
        </div>
      </div>
      
      <button 
        onClick={fetchHint}
        className={`${outfit.className} px-8 py-3 text-white font-bold rounded-full shadow-md transition-colors duration-200 ${themeColors[variant].button}`}
      >
        Get Hint
      </button>

      <div className="mt-8 p-6 bg-white rounded-2xl w-full max-w-md shadow-md border border-slate-100 text-center">
        <p className={`${outfit.className} text-slate-700 font-medium leading-relaxed`}>{hint}</p>
      </div>

    </main>
  );
}