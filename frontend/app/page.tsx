"use client";
import { useState, useEffect } from "react";
import { Outfit, Newsreader } from "next/font/google";
import { Grid3X3, X as XIcon, Calculator, Plus, Trash2, Eraser, Flame, Lightbulb, Brain, AlertTriangle, CheckCircle, Loader2, X, ChartNoAxesCombined, History } from "lucide-react";

import FeedbackModal from "../components/FeedbackModal";
import AnimatedBackground from "../components/AnimatedBackground";

const outfit = Outfit({ subsets: ["latin"] });
const newsreader = Newsreader({ subsets: ["latin"], style: ['normal', 'italic'] });

type SampleBoard = {
  name: string;
  gridString: string;
  cages?: { sum: number; cells: [number, number][] }[];
};

const SAMPLE_BOARDS: SampleBoard[] = [
  {
    name: "Easy",
    gridString: ".467....5.3.......5....93..4....1...39...258........291...2.76....5.8...86......."
  },
  {
    name: "Medium",
    gridString: "..78.956...5......96.7....2.5.....174..3.....1.3.5...8.....6..1...9.8.7.....7.6.9"
  },
  {
    name: "Hard",
    gridString: "....634..5..217.3..1.4.9...1..9.......2...7..9....4..3756..1..4.......7..21...5.."
  },
  {
    name: "Almost Complete",
    gridString: "35976184.47298563186..34759185347926743629185296.58374928513467514876.93637492518"
  },
  {
    name: "Complete",
    gridString: "359761842472985631861234759185347926743629185296158374928513467514876293637492518"
  },
  {
    name: "X-Sudoku",
    gridString: "9..5....77.......1...1..2...1.3........7..........8.6...6..9...2..8.....5....3..."
  },
  {
    name: "Killer Sudoku",
    gridString: ".................................................................................",
    cages: [
      { sum: 23, cells: [[3, 4], [4, 4], [5, 4]] },
      { sum: 13, cells: [[3, 2], [3, 3], [2, 3]] },
      { sum: 9,  cells: [[8, 7], [8, 8], [7, 8]] },
      { sum: 18, cells: [[0, 5], [1, 5], [1, 4]] },
      { sum: 16, cells: [[6, 6], [5, 6], [5, 7]] },
      { sum: 13, cells: [[3, 7], [2, 7], [1, 7]] },
      { sum: 11, cells: [[4, 7], [4, 6]] },
      { sum: 11, cells: [[4, 5], [5, 5]] },
      { sum: 13, cells: [[7, 4], [8, 4], [8, 5]] },
      { sum: 15, cells: [[2, 2], [1, 2], [1, 3]] },
      { sum: 5,  cells: [[3, 5], [3, 6]] },
      { sum: 18, cells: [[1, 0], [2, 0], [3, 0]] },
      { sum: 12, cells: [[0, 4], [0, 3], [0, 2]] },
      { sum: 10, cells: [[2, 4], [2, 5], [2, 6]] },
      { sum: 13, cells: [[1, 6], [0, 6]] },
      { sum: 10, cells: [[2, 8], [3, 8]] },
      { sum: 10, cells: [[7, 5], [6, 5], [6, 4]] },
      { sum: 8,  cells: [[4, 2], [5, 2]] },
      { sum: 9,  cells: [[5, 1], [6, 1]] },
      { sum: 21, cells: [[8, 2], [8, 3], [7, 3]] },
      { sum: 21, cells: [[1, 1], [2, 1], [3, 1]] },
      { sum: 15, cells: [[6, 3], [6, 2]] },
      { sum: 10, cells: [[4, 1], [4, 0]] },
      { sum: 10, cells: [[7, 2], [7, 1]] },
      { sum: 19, cells: [[7, 7], [6, 7], [6, 8]] },
      { sum: 6,  cells: [[4, 8], [5, 8]] },
      { sum: 7,  cells: [[5, 3], [4, 3]] },
      { sum: 3,  cells: [[0, 1], [0, 0]] },
      { sum: 18, cells: [[5, 0], [6, 0], [7, 0]] },
      { sum: 21, cells: [[0, 7], [0, 8], [1, 8]] },
      { sum: 12, cells: [[8, 6], [7, 6]] },
      { sum: 5,  cells: [[8, 0], [8, 1]] }
    ]
  }
];

export type PlayHistory = {
  date: string;
  variant: string;
  difficultyScore: number;
  solved: boolean;
  rating?: number;
  timeTaken?: number;
};

export const savePlayHistory = (variant: string, difficultyScore: number, solved: boolean, timeTaken: number) => {
  if (typeof window === "undefined") return;
  const history: PlayHistory[] = JSON.parse(localStorage.getItem('sudokuHistory') || '[]');
  
  const newEntry = { date: new Date().toISOString(), variant, difficultyScore, solved, timeTaken };
  
  localStorage.setItem('sudokuHistory', JSON.stringify([newEntry, ...history].slice(0, 20)));
};

export default function Home() {
  const [board, setBoard] = useState(
    Array(9).fill(null).map(() => Array(9).fill(0))
  );
  const [variant, setVariant] = useState<"standard" | "x-sudoku" | "killer">("standard");
  const [hintInfo, setHintInfo] = useState<{
    text: string;
    type: 'default' | 'loading' | 'heuristic' | 'genetic' | 'error' | 'success';
  }>({ text: "", type: 'default' });
  const [hintCells, setHintCells] = useState<[number, number][]>([]);
  const [errorCells, setErrorCells] = useState<[number, number][]>([]);
  const [difficulty, setDifficulty] = useState<number | null>(null);
  const [assessmentText, setAssessmentText] = useState<string | null>(null);
  const [isSolved, setIsSolved] = useState(false);
  const [hasRated, setHasRated] = useState(false);
  const [isAssessmentOpen, setIsAssessmentOpen] = useState(false);
  
  const [cages, setCages] = useState<{ sum: number; cells: [number, number][] }[]>([]);
  const [isAddingCage, setIsAddingCage] = useState(false);
  const [selectedCells, setSelectedCells] = useState<[number, number][]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [cageSumInput, setCageSumInput] = useState("");
  const [isDeletingCage, setIsDeletingCage] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [infoModal, setInfoModal] = useState<"standard" | "x-sudoku" | "killer" | null>(null);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isTimerRunning && !isSolved) {
      interval = setInterval(() => setTimeElapsed((prev) => prev + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, isSolved]);

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
    setHasRated(false);
    setIsTimerRunning(true);
    setHintInfo({ text: "Click 'Get Hint' to test the AI!", type: 'default' });
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

  const loadSampleBoard = (sample: typeof SAMPLE_BOARDS[0]) => {
    const newBoard = Array(9).fill(0).map(() => Array(9).fill(0));
    
    for (let i = 0; i < 81; i++) {
      const row = Math.floor(i / 9);
      const col = i % 9;
      const char = sample.gridString[i];
      
      if (char >= '1' && char <= '9') {
        newBoard[row][col] = parseInt(char, 10);
      }
    }
    
    setBoard(newBoard);
    
    if (sample.name === "Killer Sudoku") {
        setVariant("killer");
        setCages(sample.cages || []);
    } else if (sample.name === "X-Sudoku") {
        setVariant("x-sudoku");
        setCages([]);
    } else {
        setVariant("standard");
        setCages([]);
    }

    setHintInfo({ text: "Click 'Get Hint' to ask the AI!", type: 'default' });
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    setHasRated(false);
    setIsTimerRunning(true);
    setTimeElapsed(0);
    setDifficulty(null);
  };

  const clearBoard = () => {
    setBoard(Array(9).fill(0).map(() => Array(9).fill(0)));
    setHintInfo({ text: "Click 'Get Hint' to ask the AI!", type: 'default' });
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    setHasRated(false);
    setDifficulty(null);
  };

  const fetchHint = async () => {
    setHintInfo({ text: "Analyzing the board...", type: 'loading' });
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/api/get-hint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variant, board, cages: variant === "killer" ? cages : [] }),
      });
      const data = await response.json();
      
      // Determine the hint type based on the backend's technique
      let hintType: 'heuristic' | 'genetic' | 'success' = 'success';
      if (data.technique_used === "Logic Heuristic") hintType = 'heuristic';
      if (data.technique_used === "Genetic Algorithm Fallback") hintType = 'genetic';
      
      setHintInfo({ text: data.explanation_text, type: hintType });
      
      if (data.highlight_cells) setHintCells(data.highlight_cells);
      if (data.difficulty_score !== undefined) setDifficulty(data.difficulty_score);

      if (data.explanation_text && data.explanation_text.includes("Congratulations")) {
        savePlayHistory(variant, data.difficulty_score, true, timeElapsed);
        setIsSolved(true);
      }
      
    } catch (error) {
      setHintInfo({ text: "Error: Could not connect to the AI server.", type: 'error' });
    }
  };

  const checkSudoku = async () => {
    setHintInfo({ text: "Scanning for rule violations...", type: 'loading' });
    setHintCells([]);
    setErrorCells([]);
    setIsSolved(false);
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/api/check-sudoku`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variant, board, cages: variant === "killer" ? cages : [] }),
      });
      const data = await response.json();
      
      const isError = data.status === "error";
      setHintInfo({ text: data.explanation_text, type: isError ? 'error' : 'success' });
      
      if (isError && data.highlight_cells) {
        setErrorCells(data.highlight_cells);
      }

      if (data.status === "success" && data.explanation_text && data.explanation_text.includes("Congratulations")) {
        savePlayHistory(variant, data.difficulty_score, true, timeElapsed);
        setIsSolved(true);
      }
      
    } catch (error) {
      setHintInfo({ text: "Error: Could not connect to the API.", type: 'error' });
    }
  };

  const getDifficultyTheme = (score: number) => {
    if (score < 1.0) return { name: "Easy", color: "text-emerald-500", fill: "fill-emerald-500", bg: "bg-emerald-50", border: "border-emerald-200" };
    if (score < 2.0) return { name: "Easy", color: "text-blue-500", fill: "fill-blue-500", bg: "bg-blue-50", border: "border-blue-200" };
    if (score < 3.0) return { name: "Medium", color: "text-orange-500", fill: "fill-orange-500", bg: "bg-orange-50", border: "border-orange-200" };
    if (score < 4.0) return { name: "Hard", color: "text-red-500", fill: "fill-red-500", bg: "bg-red-50", border: "border-red-200" };
    return { name: "Evil", color: "text-purple-600", fill: "fill-purple-600", bg: "bg-purple-50", border: "border-purple-200" };
  };

  const getPersonalizedAssessment = () => {
    if (typeof window === "undefined") return null;
    const history: PlayHistory[] = JSON.parse(localStorage.getItem('sudokuHistory') || '[]');
    
    if (history.length === 0) {
      return "Welcome! Try solving an Easy board first so I can assess your skill level.";
    }

    const recentPlays = history.slice(0, 5);
    const lastPlay = recentPlays[0];
    
    if (lastPlay && lastPlay.rating && lastPlay.rating <= 2) {
      return `I noticed you didn't find my recent hints very helpful. Sudoku heuristics can be tricky! Try dropping down to an Easy board, or use the 'Check Board' button more frequently to catch errors early.`;
    }

    if (lastPlay && lastPlay.rating && lastPlay.rating >= 4) {
      return `Awesome! I'm glad my explanations are clicking for you. Since you rated the last board highly, you are definitely ready to tackle a harder difficulty.`;
    }

    const wins = recentPlays.filter(h => h.solved).length;
    const avgDifficulty = recentPlays.reduce((sum, h) => sum + h.difficultyScore, 0) / recentPlays.length;

    if (wins === 0 && history.length >= 2) {
      return "I notice you've been struggling with your recent boards. Don't forget to use the 'Get Hint' button to learn new heuristics!";
    }

    if (wins >= 3 && avgDifficulty < 2.0) {
      return "You are crushing these Easy and Medium boards! Based on your win rate, I highly recommend challenging yourself with a Hard board next.";
    }

    const killerPlays = history.filter(h => h.variant === 'killer');
    if (killerPlays.length > 3 && killerPlays.filter(h => h.solved).length > 2) {
      return "Your cage-math skills are excellent. You've mastered Killer Sudoku! Have you tried X-Sudoku yet?";
    }

    return `You've played ${history.length} games recently! Keep practicing to sharpen your skills.`;
  };

  const clearPlayHistory = () => {
    if (typeof window === "undefined") return;
    localStorage.removeItem('sudokuHistory');
    setAssessmentText(getPersonalizedAssessment());
  };

  const submitRating = (stars: number) => {
    setHasRated(true);
    
    if (typeof window === "undefined") return;
    const history: PlayHistory[] = JSON.parse(localStorage.getItem('sudokuHistory') || '[]');
    
    if (history.length > 0) {
      history[0].rating = stars;
      localStorage.setItem('sudokuHistory', JSON.stringify(history));
      setAssessmentText(getPersonalizedAssessment());
    }
  };

  useEffect(() => {
    setAssessmentText(getPersonalizedAssessment());
  }, [isSolved]);

  return (
    <main className="flex min-h-screen flex-col items-center py-8">
      <AnimatedBackground variant={variant} />
      
      <div className="relative z-10 w-full flex flex-col items-center">
        <header className="w-full max-w-5xl mx-auto px-6 py-4 flex items-center justify-between mb-6">
          <h1 className={`${newsreader.className} text-3xl sm:text-4xl font-bold tracking-tight ${themeColors[variant].text} transition-colors duration-300`}>
            SudoKurious
          </h1>
          
          <button 
            onClick={() => setIsAssessmentOpen(true)}
            className={`${outfit.className} flex items-center px-4 py-2 rounded-full font-bold text-sm transition-all shadow-sm border
              ${variant === 'standard' ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100' : ''}
              ${variant === 'x-sudoku' ? 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100' : ''}
              ${variant === 'killer' ? 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100' : ''}
            `}
          >
            <ChartNoAxesCombined className="w-4 h-4 mr-2" />
            AI Insights
          </button>
        </header>

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
          className="bg-white p-3 pb-0 shadow-xl border border-slate-100 mb-8 select-none rounded-2xl overflow-hidden flex flex-col w-full max-w-md"
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <div className="grid grid-cols-9 border-4 border-slate-700 bg-white">
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
                  <div key={`${rIndex}-${cIndex}`} className="relative w-full aspect-square">
                    {isTopLeftOfCage && (
                      <span className="absolute top-0.5 left-1 text-[9px] sm:text-[11px] font-bold text-red-700 z-30 pointer-events-none">
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
                      className={`${outfit.className} absolute inset-0 w-full h-full text-center text-xl sm:text-2xl font-bold text-slate-800 cursor-pointer transition-all duration-500
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
                      style={{ transitionDelay: isSolved ? `${(rIndex + cIndex) * 50}ms` : '0ms' }}
                    />
                  </div>
                );
              })
            )}
          </div>

          {difficulty !== null ? (
            <div className={`mt-3 -mx-3 px-4 py-3 flex items-center justify-between transition-colors duration-500 ${getDifficultyTheme(difficulty).bg} border-t ${getDifficultyTheme(difficulty).border}`}>
              <div className="flex flex-col text-left">
                <span className={`${outfit.className} text-[10px] font-bold uppercase tracking-widest opacity-60 ${getDifficultyTheme(difficulty).color}`}>
                  Difficulty
                </span>
                <span className={`${outfit.className} text-lg font-bold leading-none mt-0.5 ${getDifficultyTheme(difficulty).color}`}>
                  {getDifficultyTheme(difficulty).name} <span className="opacity-75 text-sm ml-1">({difficulty.toFixed(1)})</span>
                </span>
              </div>
              
              <div className="flex gap-0.5">
                {Array.from({ length: 5 }).map((_, index) => {
                  const activeFires = Math.min(5, Math.floor(difficulty));
                  const isActive = index < activeFires;
                  
                  return (
                    <Flame 
                      key={index} 
                      className={`w-5 h-5 transition-all duration-300 ${
                        isActive 
                          ? `${getDifficultyTheme(difficulty).color} ${getDifficultyTheme(difficulty).fill} drop-shadow-sm` 
                          : "text-slate-300/40"
                      }`} 
                      strokeWidth={isActive ? 1.5 : 2}
                    />
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="h-3 bg-slate-50 border-t border-slate-100 -mx-3 mt-3"></div>
          )}
        </div>
        
        <div className="w-full max-w-md mt-6 mb-2">
          <div className="flex items-center justify-between mb-3 px-1">
            <p className={`${outfit.className} text-xs font-bold text-slate-400 uppercase tracking-widest`}>
              Sample Boards
            </p>
            <button
              onClick={clearBoard}
              className={`${outfit.className} text-xs font-bold text-red-500 hover:text-red-600 flex items-center transition-colors`}
            >
              <Eraser className="w-3 h-3 mr-1" /> Clear Grid
            </button>
          </div>
          
          <div className="flex overflow-x-auto gap-2 pb-4 -mx-4 px-4 sm:mx-0 sm:px-0 hide-scrollbar snap-x">
            {SAMPLE_BOARDS.map((sample, index) => (
              <button
                key={index}
                onClick={() => loadSampleBoard(sample)}
                className={`${outfit.className} flex-none snap-start px-5 py-2 font-bold rounded-full bg-white text-slate-600 text-sm transition-all border border-slate-200 shadow-sm hover:border-indigo-300 hover:text-indigo-600 hover:shadow-md`}
              >
                {sample.name}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col items-center mt-2 mb-4 w-full max-w-md">
          <div className={`${outfit.className} text-slate-400 font-mono text-sm tracking-widest mb-4 flex items-center`}>
              <span className={`w-2 h-2 rounded-full mr-2 ${isTimerRunning && !isSolved ? 'bg-red-500 animate-pulse' : 'bg-slate-300'}`}></span>
              {formatTime(timeElapsed)}
          </div>

          <div className="flex gap-4 w-full justify-center">
            <button 
              onClick={fetchHint}
              className={`${outfit.className} px-8 py-3 text-white font-bold rounded-full shadow-md transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 ${themeColors[variant].button}`}
            >
              Get Hint
            </button>
            
            <button
              onClick={checkSudoku}
              className={`${outfit.className} px-8 py-3 font-bold rounded-full bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-sm transition-all duration-200`}
            >
              Check Board
            </button>
          </div>
        </div>

        {hintInfo.type !== 'default' && (
          <div className={`mt-6 p-4 rounded-2xl w-full max-w-md shadow-md border animate-in slide-in-from-top-4 fade-in duration-300 relative flex items-start text-left transition-colors
            ${hintInfo.type === 'heuristic' ? 'bg-blue-50 border-blue-200' : ''}
            ${hintInfo.type === 'genetic' ? 'bg-purple-50 border-purple-200 shadow-purple-900/10' : ''}
            ${hintInfo.type === 'error' ? 'bg-red-50 border-red-200' : ''}
            ${hintInfo.type === 'success' ? 'bg-emerald-50 border-emerald-200' : ''}
            ${hintInfo.type === 'loading' ? 'bg-slate-50 border-slate-200' : ''}
          `}>
            
            <div className="flex-shrink-0 mr-3 mt-0.5">
              {hintInfo.type === 'heuristic' && <Lightbulb className="w-5 h-5 text-blue-600" />}
              {hintInfo.type === 'genetic' && <Brain className="w-5 h-5 text-purple-600 animate-pulse" />}
              {hintInfo.type === 'error' && <AlertTriangle className="w-5 h-5 text-red-600" />}
              {hintInfo.type === 'success' && <CheckCircle className="w-5 h-5 text-emerald-600" />}
              {hintInfo.type === 'loading' && <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />}
            </div>
            
            <div className="flex-1 pr-6">
              <h4 className={`${outfit.className} text-xs font-bold uppercase tracking-wider mb-1
                ${hintInfo.type === 'heuristic' ? 'text-blue-800' : ''}
                ${hintInfo.type === 'genetic' ? 'text-purple-800' : ''}
                ${hintInfo.type === 'error' ? 'text-red-800' : ''}
                ${hintInfo.type === 'success' ? 'text-emerald-800' : ''}
                ${hintInfo.type === 'loading' ? 'text-slate-500' : ''}
              `}>
                {hintInfo.type === 'heuristic' ? 'Logic Deduction' : ''}
                {hintInfo.type === 'genetic' ? 'Deep AI Search' : ''}
                {hintInfo.type === 'error' ? 'Rule Violation' : ''}
                {hintInfo.type === 'success' ? 'Puzzle Solved' : ''}
                {hintInfo.type === 'loading' ? 'Processing...' : ''}
              </h4>
              <p className={`${outfit.className} text-slate-700 text-sm leading-relaxed`}>
                {hintInfo.text}
              </p>
            </div>

            {hintInfo.type !== 'loading' && (
              <button 
                onClick={() => setHintInfo({text: '', type: 'default'})}
                className="absolute top-3 right-3 text-slate-400 hover:text-slate-700 bg-white/50 hover:bg-white rounded-full p-1 transition-all"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        )}

        <FeedbackModal 
          isOpen={isSolved && !hasRated} 
          onSubmit={submitRating} 
        />

        <div 
          className={`fixed inset-0 z-50 transition-all duration-500 ${isAssessmentOpen ? "visible" : "invisible"}`}
        >
          <div 
            className={`absolute inset-0 bg-slate-900/20 backdrop-blur-sm transition-opacity duration-500 ${isAssessmentOpen ? "opacity-100" : "opacity-0"}`}
            onClick={() => setIsAssessmentOpen(false)}
          />
          
          <div 
            className={`absolute inset-y-0 right-0 w-full sm:w-96 bg-white shadow-2xl transform transition-transform duration-500 ease-out border-l border-slate-100 flex flex-col
              ${isAssessmentOpen ? "translate-x-0" : "translate-x-full"}
            `}
          >
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h2 className={`${outfit.className} text-lg font-bold text-slate-800 flex items-center`}>
                <span className="text-2xl mr-2"></span> AI Tutor Profile
              </h2>
              <button 
                onClick={() => setIsAssessmentOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 flex-1 overflow-y-auto">
              <div className="bg-indigo-50/50 rounded-2xl p-5 border border-indigo-100 relative group">
                <h3 className={`${outfit.className} text-xs font-bold text-indigo-900 uppercase tracking-widest mb-3 opacity-70`}>
                  Current Assessment
                </h3>
                <p className={`${outfit.className} text-indigo-800 text-sm font-medium leading-relaxed`}>
                  {assessmentText || "Analyzing your play history..."} 
                </p>
                <button 
                  onClick={clearPlayHistory}
                  className="absolute top-4 right-4 p-1.5 text-indigo-300 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                  title="Wipe Tutor Memory"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              
              <div className="mt-8">
                <h3 className={`${outfit.className} text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center`}>
                  <History className="w-3 h-3 mr-1.5" /> Session Log
                </h3>
                <p className="text-sm text-slate-500 italic text-center py-4">Detailed history coming soon...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}