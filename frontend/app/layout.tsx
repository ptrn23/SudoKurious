import type { Metadata } from "next";
import { Outfit, Newsreader } from "next/font/google";
import "./globals.css";

const outfit = Outfit({ 
  subsets: ["latin"], 
  variable: "--font-outfit" 
});

const newsreader = Newsreader({ 
  subsets: ["latin"], 
  variable: "--font-newsreader",
  style: ['normal', 'italic']
});

export const metadata: Metadata = {
  title: "SudoKurious",
  description: "The Intelligent Sudoku Tutor",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${outfit.variable} ${newsreader.variable}`}>
      <body className="font-sans bg-slate-50 text-slate-900">{children}</body>
    </html>
  );
}