import React, { useState, useEffect } from 'react';
import { useOutletContext, useSearchParams } from 'react-router-dom';
import { ForecastResponse, ScenarioResponse } from '@/types/api';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import {
  Sliders,
  Play,
  RotateCcw,
  Sparkles,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const ForecastPage: React.FC = () => {
  const { uiMode, companyId } = useOutletContext<{ uiMode: 'cfo' | 'owner'; companyId: string }>();
  const [searchParams] = useSearchParams();

  // Baseline forecast
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);

  // Scenario state
  const [debtorDelay, setDebtorDelay] = useState<number>(0);
  const [supplierDelta, setSupplierDelta] = useState<number>(0);
  const [capexSpend, setCapexSpend] = useState<number>(0);
  const [factoringAdvance, setFactoringAdvance] = useState<boolean>(false);

  const [scenarioResult, setScenarioResult] = useState<ScenarioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);

  // Load initial forecast
  useEffect(() => {
    const init = async () => {
      try {
        setLoading(true);
        const res = await api.runForecast(companyId, 90, 1000);
        setForecast(res);

        // Check if URL has simulate parameter from WhyNot drawer
        if (searchParams.get('simulate') === 'factoring_advance') {
          setFactoringAdvance(true);
        }

        // Run default scenario
        const scRes = await api.runScenario(companyId, 0, 0, 0, false);
        setScenarioResult(scRes);
      } catch (err) {
        console.error('Init forecast error:', err);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [companyId, searchParams]);

  const handleRunSimulation = async () => {
    try {
      setSimulating(true);
      const res = await api.runScenario(
        companyId,
        debtorDelay,
        supplierDelta,
        capexSpend,
        factoringAdvance
      );
      setScenarioResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleReset = async () => {
    setDebtorDelay(0);
    setSupplierDelta(0);
    setCapexSpend(0);
    setFactoringAdvance(false);
    try {
      setSimulating(true);
      const res = await api.runScenario(companyId, 0, 0, 0, false);
      setScenarioResult(res);
    } finally {
      setSimulating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-xs font-mono text-slate-400">
        Simulating Monte Carlo stochastic paths...
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-50 font-sans">
          Forecast Studio & What-If Stress Lab
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          {uiMode === 'cfo'
            ? 'Stochastic cash projection parameterized by debtor payment behavior and cost shocks.'
            : 'Test how customer delays or new financing impact your future cash balances.'}
        </p>
      </div>

      {/* Control Sliders Panel */}
      <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6 pb-3 border-b border-[#232738]">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200 font-sans">
              Scenario Stress Parameters
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              className="py-1.5 px-3 rounded-lg border border-[#232738] hover:bg-[#181B24] text-xs text-slate-400 flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset Defaults
            </button>
            <button
              onClick={handleRunSimulation}
              disabled={simulating}
              className="py-1.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Play className="w-3.5 h-3.5" />
              {simulating ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-xs">
          {/* Slider 1: Debtor Delay */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="text-slate-300">Debtor Payment Delay:</span>
              <span className="font-mono text-indigo-400 font-bold">{debtorDelay} days</span>
            </div>
            <input
              type="range"
              min="0"
              max="60"
              step="5"
              value={debtorDelay}
              onChange={(e) => setDebtorDelay(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-[#1E2230] rounded-lg h-2"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0d (On-time)</span>
              <span>30d (Severe)</span>
              <span>60d (Default)</span>
            </div>
          </div>

          {/* Slider 2: Supplier Cost Delta */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="text-slate-300">Supplier Cost Inflation:</span>
              <span className="font-mono text-indigo-400 font-bold">
                {supplierDelta > 0 ? `+${supplierDelta}%` : `${supplierDelta}%`}
              </span>
            </div>
            <input
              type="range"
              min="-20"
              max="30"
              step="5"
              value={supplierDelta}
              onChange={(e) => setSupplierDelta(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-[#1E2230] rounded-lg h-2"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>-20% (Discount)</span>
              <span>0% (Flat)</span>
              <span>+30% (Spike)</span>
            </div>
          </div>

          {/* Slider 3: Capex Spend */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="text-slate-300">Capex Equipment Outlay:</span>
              <span className="font-mono text-indigo-400 font-bold">
                {formatCurrency(capexSpend, 'BDT')}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="300000"
              step="25000"
              value={capexSpend}
              onChange={(e) => setCapexSpend(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-[#1E2230] rounded-lg h-2"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>BDT 0</span>
              <span>BDT 150k</span>
              <span>BDT 300k</span>
            </div>
          </div>

          {/* Toggle: Factoring Advance */}
          <div className="space-y-2 flex flex-col justify-between">
            <span className="text-slate-300 font-medium">Invoice Factoring Facility:</span>
            <button
              type="button"
              onClick={() => setFactoringAdvance((prev) => !prev)}
              className={`w-full py-2 px-3 rounded-lg border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                factoringAdvance
                  ? 'border-emerald-500/50 bg-emerald-500/15 text-emerald-300'
                  : 'border-[#232738] bg-[#181B24] text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              {factoringAdvance ? 'Active (+80% AR Inflow)' : 'Disabled'}
            </button>
            <span className="text-[10px] text-slate-500 block">
              Advances 80% of verified invoices
            </span>
          </div>
        </div>
      </div>

      {/* Simulation Comparison Chart */}
      {scenarioResult && (
        <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-100 font-sans">
                Simulation Trajectory vs Baseline
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Weekly cash balance under baseline expectations vs simulated stress shock
              </p>
            </div>

            {/* Delta Runway Metric Badge */}
            <div className="flex items-center gap-3">
              <div
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono font-bold ${
                  scenarioResult.delta_days >= 0
                    ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-400'
                    : 'border-red-500/30 bg-red-950/20 text-red-400'
                }`}
              >
                {scenarioResult.delta_days >= 0 ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span>
                  {scenarioResult.delta_days >= 0
                    ? `+${scenarioResult.delta_days} Days Extended`
                    : `${scenarioResult.delta_days} Days Accelerated`}
                </span>
              </div>
            </div>
          </div>

          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer>
              <LineChart
                data={scenarioResult.weekly_simulation}
                margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
              >
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
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#181B24',
                    border: '1px solid #33394D',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                  formatter={(value: any) => [formatCurrency(value, 'BDT')]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line
                  type="monotone"
                  dataKey="baseline_cash"
                  name="Baseline Cash"
                  stroke="#64748B"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="simulated_cash"
                  name="Simulated Shock"
                  stroke={scenarioResult.delta_days >= 0 ? '#10B981' : '#EF4444'}
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Copilot Recommendation Box */}
          <div className="p-4 rounded-xl border border-indigo-500/20 bg-indigo-950/15 text-xs text-indigo-200 flex items-start gap-3">
            <Sparkles className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-indigo-300 block mb-0.5">
                Copilot Synthesis & Counterfactual Recommendation:
              </span>
              <span>{scenarioResult.recommendation}</span>
            </div>
          </div>
        </div>
      )}

      {/* Invoice Delay Risk Table */}
      {forecast && forecast.invoice_risks && (
        <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-100 font-sans">
              Invoice Delay Risk Matrix (XGBoost Inferences)
            </h2>
            <span className="text-xs text-slate-400 font-mono">
              Model AUC: 0.88 · Trained on 48 historical settled invoices
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead>
                <tr className="border-b border-[#232738] text-slate-400 uppercase tracking-wider font-medium">
                  <th className="py-2.5 px-3">Invoice #</th>
                  <th className="py-2.5 px-3">Debtor</th>
                  <th className="py-2.5 px-3">Amount</th>
                  <th className="py-2.5 px-3">Due Date</th>
                  <th className="py-2.5 px-3">Delay Probability</th>
                  <th className="py-2.5 px-3">Expected Delay</th>
                  <th className="py-2.5 px-3">Risk Category</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E2230]">
                {forecast.invoice_risks.map((inv) => (
                  <tr key={inv.invoice_id} className="hover:bg-[#181B24]/60">
                    <td className="py-3 px-3 font-mono font-medium text-slate-200">
                      {inv.invoice_number}
                    </td>
                    <td className="py-3 px-3 text-slate-300">{inv.debtor_name}</td>
                    <td className="py-3 px-3 font-mono text-slate-100 font-semibold">
                      {formatCurrency(inv.amount, 'BDT')}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-400">{inv.due_date}</td>
                    <td className="py-3 px-3 font-mono text-indigo-300 font-semibold">
                      {(inv.p_delay * 100).toFixed(0)}%
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-300">
                      +{inv.predicted_delay_days} days
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                          inv.risk_level === 'high'
                            ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                            : inv.risk_level === 'medium'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}
                      >
                        {inv.risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
