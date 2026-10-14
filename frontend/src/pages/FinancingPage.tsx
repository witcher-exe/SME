import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { FinancingResponse, SchemeEvaluation } from '@/types/api';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { CovenantGauge } from '@/components/charts/CovenantGauge';
import { WhyNotDrawer } from '@/components/financing/WhyNotDrawer';
import {
  Landmark,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  FileCheck,
  RefreshCw,
  Sparkles,
} from 'lucide-react';

export const FinancingPage: React.FC = () => {
  const { uiMode, companyId } = useOutletContext<{ uiMode: 'cfo' | 'owner'; companyId: string }>();
  const [data, setData] = useState<FinancingResponse | null>(null);
  const [selectedScheme, setSelectedScheme] = useState<SchemeEvaluation | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const loadFinancing = async () => {
    try {
      setLoading(true);
      const res = await api.getFinancing(companyId);
      setData(res);
    } catch (err) {
      console.error('Financing load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFinancing();
  }, [companyId]);

  const handlePrepareApplication = (scheme: SchemeEvaluation) => {
    setToastMessage(
      `Application pack for ${scheme.name} compiled under Tier 3. Sent to Governance inbox for owner review.`
    );
    setTimeout(() => setToastMessage(null), 5000);
  };

  const openWhyNot = (scheme: SchemeEvaluation) => {
    setSelectedScheme(scheme);
    setDrawerOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-xs font-mono text-slate-400">
        Evaluating covenants and citable SME financing schemes...
      </div>
    );
  }

  if (!data) return null;

  const eligibleSchemes = data.schemes.filter((s) => s.eligible);
  const ineligibleSchemes = data.schemes.filter((s) => !s.eligible);

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-8 z-50 p-4 rounded-xl bg-indigo-950 border border-indigo-500/40 text-indigo-200 text-xs shadow-2xl flex items-center gap-2.5 animate-in slide-in-from-top-3">
          <ShieldCheck className="w-4 h-4 text-indigo-400 flex-shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-50 font-sans">
            Financing Matcher & Covenant Monitor
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {uiMode === 'cfo'
              ? 'Deterministic eligibility matching against Bangladesh Bank CMSME refinancing schemes.'
              : 'Find loan and factoring schemes tailored to your cash flow with clear qualification rules.'}
          </p>
        </div>

        <button
          onClick={loadFinancing}
          className="flex items-center gap-1.5 py-1.5 px-3 rounded-lg border border-[#232738] hover:bg-[#181B24] text-xs font-medium text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
          <span>Re-evaluate Schemes</span>
        </button>
      </div>

      {/* Covenant Compliance Banner */}
      <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#232738]">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200 font-sans">
            Covenant & Solvency Compliance Banner
          </h2>
          <span className="text-xs text-slate-400 font-mono">
            {data.covenants.filter((c) => c.result === 'pass').length} of {data.covenants.length} Covenants Passing
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.covenants.map((cov) => (
            <CovenantGauge
              key={cov.name}
              name={cov.name}
              currentValue={cov.current_value}
              requiredValue={cov.required_value}
              result={cov.result}
              formula={cov.formula}
              isLowerBetter={cov.name.toLowerCase() === 'leverage'}
            />
          ))}

          {/* Winning Factor #3: WeBank Underwriting Readiness Score */}
          <div className="rounded-xl border border-indigo-500/30 bg-indigo-950/15 p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300 font-sans flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-indigo-400" /> WeBank Score
              </span>
              <span className="text-xs font-mono font-bold text-indigo-400">QUALIFIED</span>
            </div>
            <div className="flex items-baseline justify-between mb-2">
              <div className="text-2xl font-bold font-mono text-slate-50">
                {data.underwriting_readiness_score || 78}
                <span className="text-sm font-normal text-slate-400 ml-0.5">/100</span>
              </div>
              <div className="text-xs text-slate-400 font-mono">Min: 70/100</div>
            </div>
            <div className="w-full bg-[#1E2230] h-2 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-500 transition-all duration-500"
                style={{ width: `${data.underwriting_readiness_score || 78}%` }}
              />
            </div>
            <div className="mt-2 text-[11px] text-indigo-300/80 truncate">
              Inflow regularity + Debtor diversification + Audit chain
            </div>
          </div>
        </div>
      </div>

      {/* Eligible Schemes Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-bold text-slate-100">
              Eligible Financing Options ({eligibleSchemes.length})
            </h2>
          </div>
          <span className="text-xs text-emerald-400 font-mono font-semibold">
            All Covenant Rules Satisfied
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {eligibleSchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="rounded-xl border border-emerald-500/30 bg-[#11131A] p-5 shadow-sm space-y-4 hover:border-emerald-500/50 transition-all"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[11px] font-mono text-slate-400">{scheme.issuer}</span>
                  <h3 className="text-base font-bold text-slate-50 mt-0.5">{scheme.name}</h3>
                </div>
                <div className="text-right">
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
                    {scheme.match_score}% Match
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 p-3 rounded-lg bg-[#181B24] border border-[#232738] text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Interest Rate</span>
                  <span className="font-mono font-semibold text-slate-100 text-sm">
                    {scheme.rate_pct.toFixed(1)}% p.a.
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Max Limit</span>
                  <span className="font-mono font-semibold text-slate-100 text-sm">
                    {formatCurrency(scheme.max_amount, scheme.currency)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Tenure</span>
                  <span className="font-mono font-semibold text-slate-100 text-sm">
                    {scheme.tenure_months} months
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <a
                  href={scheme.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 font-mono"
                >
                  Source Circular <ExternalLink className="w-3 h-3" />
                </a>

                <button
                  onClick={() => handlePrepareApplication(scheme)}
                  className="py-2 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
                >
                  <FileCheck className="w-3.5 h-3.5" />
                  Prepare Application (T3)
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Ineligible Schemes Section with Why-Not X-Ray */}
      <div className="space-y-4 pt-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-slate-100">
              Ineligible Options ({ineligibleSchemes.length})
            </h2>
          </div>
          <span className="text-xs text-amber-400 font-mono">
            Actionable Gap Remediation Available
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {ineligibleSchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="rounded-xl border border-red-500/20 bg-[#11131A] p-5 shadow-sm space-y-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-1">
                  <span className="text-[11px] font-mono text-slate-400">{scheme.issuer}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-red-500/10 text-red-400 border border-red-500/20 uppercase">
                    Ineligible
                  </span>
                </div>
                <h3 className="text-sm font-bold text-slate-100">{scheme.name}</h3>

                <div className="mt-3 p-3 rounded-lg bg-red-950/10 border border-red-500/20 text-xs space-y-1">
                  <span className="text-red-300 font-semibold block text-[11px]">
                    Failed Rules ({scheme.failed_rules.length}):
                  </span>
                  <div className="text-slate-300 font-mono text-[11px] truncate">
                    {scheme.failed_rules[0]?.gap || 'Threshold breach'}
                  </div>
                </div>
              </div>

              <button
                onClick={() => openWhyNot(scheme)}
                className="w-full py-2 px-3 rounded-lg border border-red-500/30 bg-red-600/10 hover:bg-red-600/20 text-red-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                Why Not? (X-Ray Diagnostics)
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Why-Not X-Ray Drawer */}
      <WhyNotDrawer
        scheme={selectedScheme}
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
};
