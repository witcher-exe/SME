import React from 'react';
import { cn } from '@/lib/utils';
import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

interface CovenantGaugeProps {
  name: string;
  currentValue: number;
  requiredValue: number;
  result: 'pass' | 'fail' | 'warning';
  formula?: string;
  unit?: string;
  isLowerBetter?: boolean;
}

export const CovenantGauge: React.FC<CovenantGaugeProps> = ({
  name,
  currentValue,
  requiredValue,
  result,
  formula,
  unit = 'x',
  isLowerBetter = false,
}) => {
  // Calculate percentage of target achieved
  let pct = 0;
  if (isLowerBetter) {
    pct = Math.max(0, Math.min(100, (requiredValue / Math.max(0.1, currentValue)) * 100));
  } else {
    pct = Math.max(0, Math.min(100, (currentValue / Math.max(0.1, requiredValue)) * 100));
  }

  const resultColor = {
    pass: 'text-emerald-400 border-emerald-500/30 bg-emerald-950/10',
    warning: 'text-amber-400 border-amber-500/30 bg-amber-950/10',
    fail: 'text-red-400 border-red-500/30 bg-red-950/10',
  }[result];

  const barColor = {
    pass: 'bg-emerald-500',
    warning: 'bg-amber-500',
    fail: 'bg-red-500',
  }[result];

  const ResultIcon = {
    pass: CheckCircle2,
    warning: AlertTriangle,
    fail: XCircle,
  }[result];

  return (
    <div className={cn('rounded-xl border p-4 transition-all duration-200', resultColor)}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1.5 font-sans">
          {name}
        </span>
        <div className="flex items-center gap-1 text-xs font-medium uppercase tracking-wider font-mono">
          <ResultIcon className="w-3.5 h-3.5" />
          <span>{result}</span>
        </div>
      </div>

      <div className="flex items-baseline justify-between mb-2">
        <div className="text-2xl font-bold font-mono text-slate-50">
          {currentValue.toFixed(2)}
          <span className="text-sm font-normal text-slate-400 ml-0.5">{unit}</span>
        </div>
        <div className="text-xs text-slate-400 font-mono">
          Required: {isLowerBetter ? '≤' : '≥'} {requiredValue.toFixed(2)}
          {unit}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-[#1E2230] h-2 rounded-full overflow-hidden">
        <div
          className={cn('h-full transition-all duration-500', barColor)}
          style={{ width: `${pct}%` }}
        />
      </div>

      {formula && (
        <div className="mt-2 text-[11px] text-slate-400 flex items-center gap-1 truncate font-sans">
          <Info className="w-3 h-3 flex-shrink-0 text-slate-500" />
          <span className="truncate">{formula}</span>
        </div>
      )}
    </div>
  );
};
