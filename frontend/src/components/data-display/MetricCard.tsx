import React from 'react';
import { cn } from '@/lib/utils';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  sublabel?: string;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  status?: 'solvency' | 'shortfall' | 'warning' | 'neutral';
  className?: string;
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  sublabel,
  trend,
  trendDirection = 'neutral',
  status = 'neutral',
  className,
  icon,
}) => {
  const statusColorMap = {
    solvency: 'border-emerald-500/30 bg-emerald-950/10 text-emerald-400',
    shortfall: 'border-red-500/30 bg-red-950/10 text-red-400',
    warning: 'border-amber-500/30 bg-amber-950/10 text-amber-400',
    neutral: 'border-[#232738] bg-[#11131A] text-slate-100',
  };

  const statusBadgeMap = {
    solvency: 'text-emerald-400 bg-emerald-500/10',
    shortfall: 'text-red-400 bg-red-500/10',
    warning: 'text-amber-400 bg-amber-500/10',
    neutral: 'text-slate-400 bg-slate-800/40',
  };

  return (
    <div
      className={cn(
        'rounded-xl border p-5 transition-all duration-200 hover:border-[#33394D]',
        statusColorMap[status],
        className
      )}
      aria-label={`${title}: ${value}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-sans">
          {title}
        </span>
        {icon && <span className="text-slate-400">{icon}</span>}
      </div>

      <div className="flex items-baseline justify-between">
        <div className="text-2xl sm:text-3xl font-semibold tracking-tight font-mono text-slate-50">
          {value}
        </div>
        {trend && (
          <div
            className={cn(
              'flex items-center text-xs font-medium px-2 py-0.5 rounded-full font-mono',
              statusBadgeMap[status]
            )}
          >
            {trendDirection === 'up' && <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />}
            {trendDirection === 'down' && <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
            {trendDirection === 'neutral' && <Minus className="w-3.5 h-3.5 mr-0.5" />}
            {trend}
          </div>
        )}
      </div>

      {sublabel && (
        <div className="mt-2 text-xs text-slate-400 flex items-center gap-1 font-sans">
          {sublabel}
        </div>
      )}
    </div>
  );
};
