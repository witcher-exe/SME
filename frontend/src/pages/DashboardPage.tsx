import React, { useEffect, useState } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { DashboardResponse } from '@/types/api';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { MetricCard } from '@/components/data-display/MetricCard';
import { MonteCarloChart } from '@/components/charts/MonteCarloChart';
import {
  Wallet,
  Clock,
  AlertTriangle,
  RefreshCw,
  ArrowRight,
  TrendingDown,
  Layers,
  ChevronRight,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { uiMode, companyId } = useOutletContext<{ uiMode: 'cfo' | 'owner'; companyId: string }>();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDashboard(companyId);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [companyId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-3">
        <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
        <span className="text-xs font-mono text-slate-400">Loading deterministic financial model...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 rounded-xl border border-red-500/20 bg-red-950/10 text-center space-y-3">
        <div className="text-red-400 font-semibold text-sm">Failed to load dashboard</div>
        <p className="text-xs text-slate-400">{error || 'Unknown error occurred'}</p>
        <button
          onClick={loadDashboard}
          className="py-2 px-4 rounded-lg bg-[#232738] hover:bg-[#33394D] text-xs font-medium text-slate-200"
        >
          Retry Load
        </button>
      </div>
    );
  }

  const { runway, metrics, forecast_chart, alerts, high_risk_invoices } = data;

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Top Banner / Heading */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-50 font-sans">
            Executive Financial Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {uiMode === 'cfo'
              ? 'Multi-horizon liquidity variance, covenant monitoring, and AR credit scoring.'
              : 'Real-time overview of your business cash, runway, and overdue customer payments.'}
          </p>
        </div>

        <button
          onClick={loadDashboard}
          className="flex items-center gap-1.5 py-1.5 px-3 rounded-lg border border-[#232738] hover:bg-[#181B24] text-xs font-medium text-slate-300 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* 4 Hero Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Liquid Cash */}
        <MetricCard
          title="Liquid Cash Balance"
          value={formatCurrency(metrics.liquid_cash, data.company.currency)}
          sublabel="Available immediately in operating accounts"
          status={metrics.liquid_cash > 250000 ? 'solvency' : 'warning'}
          icon={<Wallet className="w-4 h-4" />}
        />

        {/* Card 2: Cash Runway */}
        <MetricCard
          title="Cash Runway"
          value={`${runway.days_left} days`}
          sublabel={
            runway.shortfall_date
              ? `Deficit expected on ${runway.shortfall_date}`
              : 'Solvent across 90 days'
          }
          trend={runway.status.toUpperCase()}
          trendDirection={runway.days_left < 30 ? 'down' : 'neutral'}
          status={runway.days_left < 30 ? 'shortfall' : 'solvency'}
          icon={<Clock className="w-4 h-4" />}
        />

        {/* Card 3: Overdue AR */}
        <MetricCard
          title="High-Risk Overdue AR"
          value={formatCurrency(metrics.overdue_ar, data.company.currency)}
          sublabel={`${metrics.overdue_count} customer invoices past due date`}
          trend={metrics.overdue_ar > 0 ? 'CRITICAL' : 'CLEAN'}
          trendDirection={metrics.overdue_ar > 0 ? 'down' : 'up'}
          status={metrics.overdue_ar > 0 ? 'shortfall' : 'solvency'}
          icon={<AlertTriangle className="w-4 h-4" />}
        />

        {/* Card 4: Working Capital CCC */}
        <MetricCard
          title="Cash Conversion Cycle"
          value={`${metrics.cash_conversion_cycle_days.toFixed(0)} days`}
          sublabel={`DSO: ${metrics.days_sales_outstanding.toFixed(0)}d · DPO: ${metrics.days_payable_outstanding.toFixed(0)}d`}
          status={metrics.cash_conversion_cycle_days > 60 ? 'warning' : 'solvency'}
          icon={<Layers className="w-4 h-4" />}
        />
      </div>

      {/* Main Grid: Forecast Chart (2/3) + Alerts Feed (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Forecast Studio Panel */}
        <div className="lg:col-span-2 rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider font-sans">
                13-Week Cash-Flow Forecast (Monte Carlo)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                P10 conservative, P50 median, and P90 optimistic corridor from 1,000 simulations
              </p>
            </div>
            <button
              onClick={() => navigate('/forecast')}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              Interactive Studio <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <MonteCarloChart
            data={forecast_chart}
            shortfallDate={runway.shortfall_date}
            currency={data.company.currency}
          />
        </div>

        {/* Prioritized Lead-Time Alerts Feed */}
        <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 flex flex-col shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider font-sans">
              Lead-Time Alerts
            </h2>
            <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
              {alerts.length} Active
            </span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto">
            {alerts.map((alert) => {
              const severityColor = {
                critical: 'border-red-500/30 bg-red-950/15 text-red-300',
                warning: 'border-amber-500/30 bg-amber-950/15 text-amber-300',
                info: 'border-indigo-500/30 bg-indigo-950/15 text-indigo-300',
              }[alert.severity];

              return (
                <div
                  key={alert.id}
                  className={`p-3.5 rounded-xl border ${severityColor} space-y-2`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wide">
                      {alert.title}
                    </span>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-black/40">
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    {alert.description}
                  </p>
                  {alert.action_label && alert.action_route && (
                    <button
                      onClick={() => navigate(alert.action_route!)}
                      className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 pt-1"
                    >
                      {alert.action_label} <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* High-Risk Invoices Preview */}
      <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider font-sans">
              Receivables at Risk of Delay (XGBoost Classifier)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              High-impact overdue invoices requiring Tier 2 collection notices
            </p>
          </div>
          <button
            onClick={() => navigate('/operations')}
            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
          >
            Full Invoice Ledger <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead>
              <tr className="border-b border-[#232738] text-slate-400 uppercase tracking-wider font-medium">
                <th className="py-2.5 px-3">Invoice #</th>
                <th className="py-2.5 px-3">Debtor</th>
                <th className="py-2.5 px-3">Amount</th>
                <th className="py-2.5 px-3">Due Date</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Delay Probability</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2230]">
              {high_risk_invoices.slice(0, 4).map((inv) => (
                <tr key={inv.id} className="hover:bg-[#181B24]/60 transition-colors">
                  <td className="py-3 px-3 font-mono font-medium text-slate-200">
                    {inv.invoice_number}
                  </td>
                  <td className="py-3 px-3 text-slate-300">{inv.debtor_name}</td>
                  <td className="py-3 px-3 font-mono text-slate-100 font-semibold">
                    {formatCurrency(inv.amount, inv.currency)}
                  </td>
                  <td className="py-3 px-3 text-slate-400 font-mono">{inv.due_date}</td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase ${
                        inv.status === 'overdue'
                          ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                          : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      }`}
                    >
                      {inv.status}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono">
                    <span className="text-amber-400 font-semibold">
                      {((inv.p_delay || 0.65) * 100).toFixed(0)}%
                    </span>
                    <span className="text-slate-500 text-[11px] ml-1">
                      (+{inv.predicted_delay_days || 14}d)
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => navigate('/operations')}
                      className="py-1 px-2.5 rounded bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 font-medium"
                    >
                      Draft Notice
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
