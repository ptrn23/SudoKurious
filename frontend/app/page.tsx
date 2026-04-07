"use client";
import { useState } from "react";
import { Outfit, Newsreader } from "next/font/google";
import { Grid3X3, X as XIcon, Calculator, Plus, Trash2, Eraser } from "lucide-react";

const outfit = Outfit({ subsets: ["latin"] });
const newsreader = Newsreader({ subsets: ["latin"], style: ['normal', 'italic'] });

export default function Home() {
  const [board, setBoard] = useState(
    Array(9).fill(null).map(() => Array(9).fill(0))
  );
  const [variant, setVariant] = useState<"standard" | "x-sudoku" | "killer">("standard");
  const [hint, setHint] = useState("Click 'Get Hint' to test the AI!");
  const [hintCells, setHintCells] = useState<[number, number][]>([]);
  
  const [cages, setCages] = useState<{ sum: number; cells: [number, number][] }[]>([]);
  const [isAddingCage, setIsAddingCage] = useState(false);
  const [selectedCells, setSelectedCells] = useState<[number, number][]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [cageSumInput, setCageSumInput] = useState("");
  const [isDeletingCage, setIsDeletingCage] = useState(false);

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

  const isCellCaged = (r: number, c: number) => {
    return cages.some(cage => cage.cells.some(([cr, cc]) => cr === r && cc === c));
  };

  const handleFinishCage = () => {
    if (!cageSumInput || selectedCells.length === 0) {
      setSelectedCells([]);
      setIsAddingCage(false);
      setCageSumInput("");
      return;
    }

    setCages([...cages, { sum: parseInt(cageSumInput), cells: selectedCells }]);
    setSelectedCells([]);
    setIsAddingCage(false);
    setCageSumInput("");
  };

  const handleMouseDown = (r: number, c: number) => {
    if (isDeletingCage) {
      const targetCageIndex = cages.findIndex(cage => 
        cage.cells.some(([cr, cc]) => cr === r && cc === c)
      );
      
      if (targetCageIndex !== -1) {
        // Remove the clicked cage
        const updatedCages = [...cages];
        updatedCages.splice(targetCageIndex, 1);
        setCages(updatedCages);
      }
      return;
    }

    if (!isAddingCage || isCellCaged(r, c)) return; 
    setIsDrawing(true);
    
    const isAlreadySelected = selectedCells.some(([sr, sc]) => sr === r && sc === c);
    if (!isAlreadySelected) setSelectedCells([...selectedCells, [r, c]]);
  };

  const handleMouseEnter = (r: number, c: number) => {
    if (!isAddingCage || !isDrawing || isCellCaged(r, c)) return;
    
    const isAlreadySelected = selectedCells.some(([sr, sc]) => sr === r && sc === c);
    if (!isAlreadySelected) setSelectedCells((prev) => [...prev, [r, c]]);
  };

  const handleMouseUp = () => {
    if (!isAddingCage) return;
    setIsDrawing(false);
  };

  const fetchHint = async () => {
    setHint("Thinking...");
    setHintCells([]);
    
    try {
      const response = await fetch("http://localhost:8000/api/get-hint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          variant: variant, 
          board: board,
          cages: variant === "killer" ? cages : [] 
        }),
      });
      const data = await response.json();
      setHint(data.explanation_text);
      
      if (data.highlight_cells) {
        setHintCells(data.highlight_cells);
      }
      
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
      {variant === "killer" && (
        <div className="mb-6 flex items-center space-x-3 animate-in fade-in slide-in-from-top-2 duration-300">
          {isAddingCage ? (
            <div className="flex items-center space-x-2 bg-red-50 p-1 pr-1.5 rounded-full border border-red-200 shadow-sm animate-in zoom-in-95 duration-200">
              <input
                type="number"
                placeholder="Sum?"
                value={cageSumInput}
                onChange={(e) => setCageSumInput(e.target.value)}
                className="w-20 px-3 py-1.5 text-sm font-bold text-red-700 bg-white border border-red-300 rounded-full outline-none focus:border-red-500 focus:ring-2 focus:ring-red-200"
                autoFocus
              />
              <button 
                onClick={handleFinishCage}
                className={`${outfit.className} px-4 py-1.5 bg-red-600 text-white hover:bg-red-700 rounded-full font-bold transition-colors text-sm shadow-md`}
              >
                Finish
              </button>
            </div>
          ) : (
            <button 
              className={`${outfit.className} flex items-center px-4 py-2 bg-red-100 text-red-700 hover:bg-red-200 rounded-lg font-bold transition-colors text-sm`}
              onClick={() => {
                setIsAddingCage(true);
                setIsDeletingCage(false); // Ensure delete mode turns off
              }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Sum Cage
            </button>
          )}
          
          <button 
            className={`${outfit.className} flex items-center px-4 py-2 rounded-lg font-bold transition-colors text-sm ${
              isDeletingCage 
                ? "bg-orange-100 text-orange-700 border border-orange-300 shadow-inner" 
                : "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-transparent"
            }`}
            onClick={() => {
              setIsDeletingCage(!isDeletingCage);
              setIsAddingCage(false);
              setSelectedCells([]);
              setCageSumInput("");
            }}
          >
            <Eraser className="w-4 h-4 mr-2" />
            {isDeletingCage ? "Click a cage to erase" : "Delete Sum Cage"}
          </button>
          
          <button 
            className={`${outfit.className} flex items-center px-4 py-2 bg-white border border-slate-200 text-slate-500 hover:bg-slate-50 hover:text-red-600 rounded-lg font-bold transition-colors text-sm`}
            onClick={() => {
              setCages([]);
              setSelectedCells([]);
              setIsAddingCage(false);
              setCageSumInput("");
            }}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear Cages
          </button>
        </div>
      )}
      
      <div 
        className="bg-white p-3 shadow-xl border border-slate-100 mb-8 select-none"
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div className="grid grid-cols-9 border-4 border-slate-700 overflow-hidden">
          {board.map((row, rIndex) =>
            row.map((cell, cIndex) => {
              const isRightBorder = (cIndex + 1) % 3 === 0 && cIndex !== 8;
              const isBottomBorder = (rIndex + 1) % 3 === 0 && rIndex !== 8;
              const isXDiagonal = variant === "x-sudoku" && (rIndex === cIndex || rIndex + cIndex === 8);
              
              const isKiller = variant === "killer";
              const isSelectedForCage = isKiller && selectedCells.some(([sr, sc]) => sr === rIndex && sc === cIndex);
              const matchingCage = isKiller 
                ? cages.find(cage => cage.cells.some(([cr, cc]) => cr === rIndex && cc === cIndex)) 
                : undefined;
              
              const activeCells = matchingCage ? matchingCage.cells : isSelectedForCage ? selectedCells : null;
              
              let hasTop = false, hasBottom = false, hasLeft = false, hasRight = false;
              if (activeCells) {
                hasTop = !activeCells.some(([cr, cc]) => cr === rIndex - 1 && cc === cIndex);
                hasBottom = !activeCells.some(([cr, cc]) => cr === rIndex + 1 && cc === cIndex);
                hasLeft = !activeCells.some(([cr, cc]) => cr === rIndex && cc === cIndex - 1);
                hasRight = !activeCells.some(([cr, cc]) => cr === rIndex && cc === cIndex + 1);
              }

              let isTopLeftOfCage = false;
              if (matchingCage) {
                const topLeftCell = matchingCage.cells.reduce((acc, curr) => {
                  if (curr[0] < acc[0]) return curr;
                  if (curr[0] === acc[0] && curr[1] < acc[1]) return curr;
                  return acc;
                });
                if (topLeftCell[0] === rIndex && topLeftCell[1] === cIndex) {
                  isTopLeftOfCage = true;
                }
              }

              return (
                <div key={`${rIndex}-${cIndex}`} className="relative w-12 h-12 sm:w-14 sm:h-14">
                  {isTopLeftOfCage && (
                    <span className="absolute top-0.5 left-1.5 text-[11px] font-bold text-red-700 z-20 pointer-events-none">
                      {matchingCage?.sum}
                    </span>
                  )}
                  
                  {activeCells && (
                    <div 
                      className={`absolute inset-0 pointer-events-none border-dashed border-red-500 z-10
                        ${hasTop ? 'border-t-[3px]' : ''}
                        ${hasBottom ? 'border-b-[3px]' : ''}
                        ${hasLeft ? 'border-l-[3px]' : ''}
                        ${hasRight ? 'border-r-[3px]' : ''}
                      `} 
                    />
                  )}
                  
                  <input
                    type="text"
                    value={cell === 0 ? "" : cell}
                    onChange={(e) => handleChange(rIndex, cIndex, e.target.value)}
                    readOnly={isAddingCage || isDeletingCage}
                    draggable={false}
                    onMouseDown={() => handleMouseDown(rIndex, cIndex)}
                    onMouseEnter={() => handleMouseEnter(rIndex, cIndex)}
                    className={`${outfit.className} absolute inset-0 w-full h-full text-center text-2xl font-bold text-slate-800 cursor-pointer
                      focus:outline-none focus:ring-4 focus:ring-inset focus:z-0 ${themeColors[variant].ring}
                      ${isRightBorder ? "border-r-2 border-r-slate-400" : "border-r border-r-slate-200"}
                      ${isBottomBorder ? "border-b-2 border-b-slate-400" : "border-b border-b-slate-200"}
                      ${isSelectedForCage ? "bg-red-200 transition-colors" : matchingCage ? "bg-red-50" : isXDiagonal ? "bg-orange-50" : "bg-white"} 
                    `}
                  />
                </div>
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