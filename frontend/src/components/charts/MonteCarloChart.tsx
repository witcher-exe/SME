import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  ReferenceLine,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { ForecastChartData } from '@/types/api';
import { formatCurrency } from '@/lib/utils';

interface MonteCarloChartProps {
  data: ForecastChartData;
  shortfallDate?: string | null;
  height?: number;
  currency?: string;
}

export const MonteCarloChart: React.FC<MonteCarloChartProps> = ({
  data,
  shortfallDate,
  height = 360,
  currency = 'BDT',
}) => {
  if (!data || !data.weeks || data.weeks.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
        No forecast data available
      </div>
    );
  }

  const chartData = data.weeks.map((week, idx) => ({
    week,
    date: data.dates ? data.dates[idx] : '',
    p10: data.p10_conservative[idx],
    p50: data.p50_median[idx],
    p90: data.p90_optimistic[idx],
    corridor: [data.p10_conservative[idx], data.p90_optimistic[idx]],
    safetyFloor: data.safety_floor,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const p10Val = payload.find((p: any) => p.dataKey === 'p10')?.value;
      const p50Val = payload.find((p: any) => p.dataKey === 'p50')?.value;
      const p90Val = payload.find((p: any) => p.dataKey === 'p90')?.value;
      const itemDate = payload[0]?.payload?.date;

      return (
        <div className="bg-[#181B24] border border-[#33394D] p-3 rounded-lg shadow-xl text-xs space-y-1.5 font-sans">
          <div className="font-semibold text-slate-200 border-b border-[#232738] pb-1">
            {label} {itemDate ? `(${itemDate})` : ''}
          </div>
          <div className="text-emerald-400 font-mono">
            P90 (Optimistic): {formatCurrency(p90Val, currency)}
          </div>
          <div className="text-indigo-300 font-mono font-medium">
            P50 (Median): {formatCurrency(p50Val, currency)}
          </div>
          <div className="text-amber-400 font-mono">
            P10 (Conservative): {formatCurrency(p10Val, currency)}
          </div>
          <div className="text-red-400/80 font-mono border-t border-[#232738] pt-1">
            Safety Floor: {formatCurrency(data.safety_floor, currency)}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5 text-indigo-400">
            <span className="w-3 h-3 rounded-full bg-indigo-500/30 border border-indigo-500 inline-block"></span>
            P10–P90 Corridor (1,000 runs)
          </div>
          <div className="flex items-center gap-1.5 text-slate-200">
            <span className="w-4 h-0.5 bg-indigo-400 inline-block"></span>
            P50 Median Trajectory
          </div>
          <div className="flex items-center gap-1.5 text-red-400">
            <span className="w-4 h-0.5 border-b border-dashed border-red-500 inline-block"></span>
            Safety Floor
          </div>
        </div>
        {shortfallDate && (
          <div className="text-xs px-2.5 py-1 rounded-md bg-red-500/10 border border-red-500/20 text-red-400 font-medium">
            Projected Breach: {shortfallDate}
          </div>
        )}
      </div>

      <div style={{ width: '100%', height }}>
        <ResponsiveContainer>
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="corridorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366F1" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#6366F1" stopOpacity={0.03} />
              </linearGradient>
            </defs>

            <CartesianGrid stroke="#1E2230" strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="week"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#232738' }}
            />
            <YAxis
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#232738' }}
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
            />

            <Tooltip content={<CustomTooltip />} />

            {/* Area between P10 and P90 */}
            <Area
              type="monotone"
              dataKey="p90"
              stroke="transparent"
              fill="url(#corridorGradient)"
            />
            <Area
              type="monotone"
              dataKey="p10"
              stroke="#F59E0B"
              strokeWidth={1}
              strokeDasharray="4 4"
              fill="#090A0F"
            />

            {/* P50 Median Line */}
            <Line
              type="monotone"
              dataKey="p50"
              stroke="#818CF8"
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#6366F1' }}
              activeDot={{ r: 5 }}
            />

            {/* Safety Floor Line */}
            <ReferenceLine
              y={data.safety_floor}
              stroke="#EF4444"
              strokeDasharray="4 4"
              strokeWidth={1.5}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
