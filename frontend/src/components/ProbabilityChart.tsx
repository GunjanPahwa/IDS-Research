"use client";

interface ProbabilityChartProps {
  probabilities: Record<string, number>;
  predictedLabel: string;
}

export default function ProbabilityChart({ probabilities, predictedLabel }: ProbabilityChartProps) {
  const sorted = Object.entries(probabilities).sort(([, a], [, b]) => b - a);

  return (
    <div className="space-y-2.5">
      <div className="flex justify-between items-center text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
        <span>Target Category Class</span>
        <span>Model Probability</span>
      </div>

      {sorted.map(([cls, prob]) => {
        const percent = (prob * 100).toFixed(1);
        const isPredicted = cls === predictedLabel;
        const isBenign = cls === "BENIGN";

        let barColor = "bg-slate-300 dark:bg-slate-700";
        if (isPredicted) {
          barColor = isBenign
            ? "bg-gradient-to-r from-emerald-500 to-teal-400"
            : "bg-gradient-to-r from-rose-500 to-amber-500";
        }

        return (
          <div key={cls} className="space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span
                className={`font-mono font-medium ${
                  isPredicted
                    ? "font-bold text-slate-900 dark:text-white"
                    : "text-slate-600 dark:text-slate-400"
                }`}
              >
                {cls}
                {isPredicted && (
                  <span className="ml-1.5 text-[10px] font-sans px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                    Predicted
                  </span>
                )}
              </span>
              <span className="font-mono text-slate-700 dark:text-slate-300 font-semibold">{percent}%</span>
            </div>

            <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                style={{ width: `${Math.max(prob * 100, 0.5)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
