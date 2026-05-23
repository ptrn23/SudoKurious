"use client";
import { useEffect, useState, useMemo } from "react";

const variantColors = {
    standard: ["bg-blue-400", "bg-blue-500", "bg-indigo-400"],
    "x-sudoku": ["bg-orange-400", "bg-amber-500", "bg-orange-500"],
    killer: ["bg-red-400", "bg-rose-500", "bg-pink-500"],
};

export default function AnimatedBackground({ variant }: { variant: "standard" | "x-sudoku" | "killer" }) {
    const [squares, setSquares] = useState<any[]>([]);

    useEffect(() => {
        const cols = Math.floor(window.innerWidth / 40);
        const rows = Math.floor(window.innerHeight / 40);

        const newSquares = Array.from({ length: 25 }).map((_, i) => ({
            id: i,
            left: `${Math.floor(Math.random() * cols) * 40 + 4}px`,
            top: `${Math.floor(Math.random() * rows) * 40 + 4}px`,
            delay: `${Math.random() * 6}s`,
            color: variantColors[variant][Math.floor(Math.random() * 3)]
        }));

        setSquares(newSquares);
    }, [variant]);

    return (
        <div className="fixed inset-0 pointer-events-none z-[-1] bg-slate-50">
            <div
                className="absolute inset-0 opacity-[0.01]"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='4' y='4' width='32' height='32' fill='%230f172a' rx='4' ry='4' /%3E%3C/svg%3E")`,
                    backgroundSize: '40px 40px'
                }}
            />

            {squares.map((sq) => (
                <div
                    key={sq.id}
                    className={`absolute w-8 h-8 rounded-md grid-square-smooth ${sq.color}`}
                    style={{ left: sq.left, top: sq.top, animationDelay: sq.delay }}
                />
            ))}

            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-50/20 to-slate-50/95 pointer-events-none" />
        </div>
    );
}