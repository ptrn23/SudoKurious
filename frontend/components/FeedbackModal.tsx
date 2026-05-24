import { Outfit } from "next/font/google";

const outfit = Outfit({ subsets: ["latin"] });

type FeedbackModalProps = {
  isOpen: boolean;
  onSubmit: (stars: number) => void;
};

export default function FeedbackModal({ isOpen, onSubmit }: FeedbackModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-md animate-in fade-in duration-300 p-4">
      <div className="bg-white/90 p-8 rounded-3xl w-full max-w-sm shadow-2xl border border-white/50 text-center animate-in zoom-in-95 slide-in-from-bottom-4 duration-500">
        
        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4 shadow-inner">
          <span className="text-3xl">🎉</span>
        </div>

        <h2 className={`${outfit.className} text-2xl font-bold text-slate-800 mb-2`}>
          Puzzle Solved!
        </h2>
        
        <p className={`${outfit.className} text-slate-500 text-sm mb-6 leading-relaxed`}>
          How well did the AI Tutor help you understand and solve this board?
        </p>

        <div className="flex justify-center gap-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button 
              key={star} 
              onClick={() => onSubmit(star)}
              className="text-4xl hover:scale-125 hover:-translate-y-1 transition-all duration-200 drop-shadow-sm hover:drop-shadow-md"
              title={`Rate ${star} stars`}
            >
              ⭐
            </button>
          ))}
        </div>
        
      </div>
    </div>
  );
}