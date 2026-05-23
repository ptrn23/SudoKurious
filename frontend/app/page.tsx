"use client";
import { useState } from "react";
import { Outfit, Newsreader } from "next/font/google";
import { Grid3X3, X as XIcon, Calculator, Plus, Trash2, Eraser, Flame } from "lucide-react";

const outfit = Outfit({ subsets: ["latin"] });
const newsreader = Newsreader({ subsets: ["latin"], style: ['normal', 'italic'] });

const SAMPLE_BOARDS = [
  {
    name: "Easy",
    gridString: ".6.12..9.2...37........5....4..5.2.78.5........1....83.1.....7...8...9..95..8..1."
  },
  {
    name: "Medium",
    gridString: ".19.8.56.....543.13.........87.2.......5.6.781........6748....2....75....3.....4."
  },
  {
    name: "Hard",
    gridString: "3......6...4..2..9.5.4.....6351.......9.2.8..4.......1..2.49..........3.........7"
  },
  {
    name: "Almost Complete",
    gridString: "35976184.47298563186..34759185347926743629185296.58374928513467514876.93637492518"
  },
  {
    name: "Complete",
    gridString: "359761842472985631861234759185347926743629185296158374928513467514876293637492518"
  }
];

export default function Home() {
  const [board, setBoard] = useState(
    Array(9).fill(null).map(() => Array(9).fill(0))
  );
  const [variant, setVariant] = useState<"standard" | "x-sudoku" | "killer">("standard");
  const [hint, setHint] = useState("Click 'Get Hint' to test the AI!");
  const [hintCells, setHintCells] = useState<[number, number][]>([]);
  const [errorCells, setErrorCells] = useState<[number, number][]>([]);
  const [difficulty, setDifficulty] = useState<number | null>(null);
  const [isSolved, setIsSolved] = useState(false);
  
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
    setHintCells([]); 
    setErrorCells([]);
    setIsSolved(false);
    setHint("Click 'Get Hint' to test the AI!");
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

  const loadSampleBoard = (gridString: string) => {
    const newBoard = Array(9).fill(0).map(() => Array(9).fill(0));
    
    for (let i = 0; i < 81; i++) {
      const row = Math.floor(i / 9);
      const col = i % 9;
      const char = gridString[i];
      
      if (char >= '1' && char <= '9') {
        newBoard[row][col] = parseInt(char, 10);
      }
    }
    
    setBoard(newBoard);
    setHint("Click 'Get Hint' to ask the AI!");
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    setDifficulty(null);
  };

  const clearBoard = () => {
    setBoard(Array(9).fill(0).map(() => Array(9).fill(0)));
    setHint("Click 'Get Hint' to ask the AI!");
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    setDifficulty(null);
  };

  const fetchHint = async () => {
    setHint("Thinking...");
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/api/get-hint`, {
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

      if (data.difficulty_score !== undefined) {
        setDifficulty(data.difficulty_score);
      }

      if (data.explanation_text && data.explanation_text.includes("Congratulations")) {
        setIsSolved(true);
      }
      
    } catch (error) {
      setHint("Error: Could not connect to the AI server.");
    }
  };

  const checkSudoku = async () => {
    setHint("Checking board...");
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/api/check-sudoku`, {
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
      
      if (data.status === "error" && data.highlight_cells) {
        setErrorCells(data.highlight_cells);
      }

      if (data.status === "success" && data.explanation_text && data.explanation_text.includes("Congratulations")) {
        setIsSolved(true);
      }
      
    } catch (error) {
      setHint("Error: Could not connect to the API.");
    }
  };

  const getDifficultyTheme = (score: number) => {
    if (score < 1.0) return { name: "Easy", color: "text-emerald-500", fill: "fill-emerald-500", bg: "bg-emerald-50", border: "border-emerald-200" };
    if (score < 2.0) return { name: "Medium", color: "text-blue-500", fill: "fill-blue-500", bg: "bg-blue-50", border: "border-blue-200" };
    if (score < 3.0) return { name: "Hard", color: "text-orange-500", fill: "fill-orange-500", bg: "bg-orange-50", border: "border-orange-200" };
    if (score < 4.0) return { name: "Really Hard", color: "text-red-500", fill: "fill-red-500", bg: "bg-red-50", border: "border-red-200" };
    return { name: "Evil", color: "text-purple-600", fill: "fill-purple-600", bg: "bg-purple-50", border: "border-purple-200" };
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
                setIsDeletingCage(false);
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
              setHintCells([]);
              setErrorCells([]);
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

              const isHintCell = hintCells.some(([hr, hc]) => hr === rIndex && hc === cIndex);
              const isErrorCell = errorCells.some(([er, ec]) => er === rIndex && ec === cIndex);

              return (
                <div key={`${rIndex}-${cIndex}`} className="relative w-12 h-12 sm:w-14 sm:h-14">
                  {isTopLeftOfCage && (
                    <span className="absolute top-0.5 left-1.5 text-[11px] font-bold text-red-700 z-30 pointer-events-none">
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
                    className={`${outfit.className} absolute inset-0 w-full h-full text-center text-2xl font-bold text-slate-800 cursor-pointer transition-all duration-500
                      focus:outline-none focus:ring-4 focus:ring-inset focus:z-0 ${themeColors[variant].ring}
                      ${isRightBorder ? "border-r-2 border-r-slate-400" : "border-r border-r-slate-200"}
                      ${isBottomBorder ? "border-b-2 border-b-slate-400" : "border-b border-b-slate-200"}
                      ${isSolved ? "!bg-emerald-500 !text-white !border-emerald-600 shadow-md z-20 scale-100" : 
                        isErrorCell ? "bg-red-200 text-red-900 shadow-inner z-0" : 
                        isHintCell ? "bg-emerald-200 shadow-inner z-0" : 
                        isSelectedForCage ? "bg-red-200 z-0" : 
                        matchingCage ? "bg-red-50 z-0" : 
                        isXDiagonal ? "bg-orange-50 z-0" : "bg-white z-0"}
                    `}
                    // Calculate delay based on distance from top-left (0,0)
                    style={{ transitionDelay: isSolved ? `${(rIndex + cIndex) * 50}ms` : '0ms' }}
                  />
                </div>
              );
            })
          )}
        </div>
      </div>
      
      <div className="mt-6 flex flex-col items-center gap-3 w-full max-w-md">
        <p className={`${outfit.className} text-xs font-bold text-slate-400 uppercase tracking-widest`}>
          Sample Boards
        </p>
        
        <div className="flex flex-wrap justify-center gap-2">
          {SAMPLE_BOARDS.map((sample, index) => (
            <button
              key={index}
              onClick={() => loadSampleBoard(sample.gridString)}
              className={`${outfit.className} px-6 py-2.5 font-bold rounded-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-sm transition-colors border border-indigo-100 shadow-sm`}
            >
              {sample.name}
            </button>
          ))}
          
          <button
            onClick={clearBoard}
            className={`${outfit.className} px-6 py-2.5 font-bold rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 text-sm transition-colors border border-slate-200 shadow-sm`}
          >
            Clear Grid
          </button>
        </div>
      </div>

      <div className="mt-6 flex gap-4 w-full max-w-md justify-center">
        <button 
          onClick={fetchHint}
          className={`${outfit.className} px-8 py-3 text-white font-bold rounded-full shadow-md transition-colors duration-200 ${themeColors[variant].button}`}
        >
          Get Hint
        </button>

        <button
          onClick={checkSudoku}
          className={`${outfit.className} px-8 py-3 font-bold rounded-full bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 shadow-sm transition-colors duration-200`}
        >
          Check Board
        </button>
      </div>

      <div className="mt-8 p-6 bg-white rounded-2xl w-full max-w-md shadow-md border border-slate-100 text-center">
        <p className={`${outfit.className} text-slate-700 font-medium leading-relaxed`}>{hint}</p>
      </div>

      {difficulty !== null && (
        <div className={`mt-4 p-4 rounded-2xl w-full max-w-md shadow-sm border text-center transition-all duration-500 animate-in fade-in slide-in-from-bottom-2 ${getDifficultyTheme(difficulty).bg} ${getDifficultyTheme(difficulty).border}`}>
          
          <p className={`${outfit.className} text-xs uppercase tracking-widest font-bold mb-1 opacity-70 ${getDifficultyTheme(difficulty).color}`}>
            DIFFICULTY
          </p>
          
          <div className="flex flex-col items-center justify-center">
            <p className={`${outfit.className} text-2xl font-bold ${getDifficultyTheme(difficulty).color}`}>
              {getDifficultyTheme(difficulty).name} 
              <span className="opacity-75 ml-2">({difficulty.toFixed(1)})</span>
            </p>
            
            <div className="flex gap-1 mt-2">
              {Array.from({ length: 5 }).map((_, index) => {
                const activeFires = Math.min(5, Math.floor(difficulty));
                const isActive = index < activeFires;
                
                return (
                  <Flame 
                    key={index} 
                    className={`w-6 h-6 transition-all duration-300 ${
                      isActive 
                        ? `${getDifficultyTheme(difficulty).color} ${getDifficultyTheme(difficulty).fill} drop-shadow-sm scale-110` 
                        : "text-slate-300 scale-100"
                    }`} 
                    strokeWidth={isActive ? 1.5 : 2}
                  />
                );
              })}
            </div>
          </div>
          
        </div>
      )}
    </main>
  );
}