import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SchemeEvaluation } from '@/types/api';
import { X, AlertCircle, CheckCircle2, ArrowRight, FileText, Sliders } from 'lucide-react';

interface WhyNotDrawerProps {
  scheme: SchemeEvaluation | null;
  isOpen: boolean;
  onClose: () => void;
}

export const WhyNotDrawer: React.FC<WhyNotDrawerProps> = ({ scheme, isOpen, onClose }) => {
  const navigate = useNavigate();

  if (!isOpen || !scheme) return null;

  const handleSimulateFix = () => {
    onClose();
    // Navigate to forecast studio with scenario remediation applied
    navigate('/forecast?simulate=factoring_advance');
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-[#11131A] border-l border-[#232738] h-full overflow-y-auto flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-[#232738] flex items-start justify-between bg-[#181B24]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                Ineligible (X-Ray Gap Analysis)
              </span>
              <span className="text-xs text-slate-400">{scheme.issuer}</span>
            </div>
            <h2 className="text-lg font-bold text-slate-50">{scheme.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-[#232738] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 flex-1">
          {/* Failed Rules Section */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-red-400" />
              Failed Eligibility Rules ({scheme.failed_rules.length})
            </h3>
            <div className="space-y-3">
              {scheme.failed_rules.map((rule, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-red-500/20 bg-red-950/10 space-y-2"
                >
                  <div className="text-sm font-semibold text-red-300 font-mono">
                    {rule.rule_name}
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-slate-400 block">Required:</span>
                      <span className="font-mono text-slate-200">{rule.required}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Your Value:</span>
                      <span className="font-mono text-red-400 font-semibold">{rule.actual}</span>
                    </div>
                  </div>
                  <div className="text-xs text-amber-300/90 bg-amber-500/10 p-2 rounded border border-amber-500/20">
                    <span className="font-medium">Gap:</span> {rule.gap}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actionable Remediation Section */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Actionable Remediation Pathway
            </h3>
            <div className="space-y-2">
              {scheme.remediation_steps.map((step, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg border border-[#232738] bg-[#181B24] text-xs text-slate-200 flex items-start gap-2.5"
                >
                  <ArrowRight className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span>{step}</span>
                </div>
              ))}
            </div>

            {/* Closed-loop Winning Upgrade button */}
            <button
              onClick={handleSimulateFix}
              className="mt-4 w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-indigo-600/20"
            >
              <Sliders className="w-4 h-4" />
              Simulate Fix in Forecast Studio
            </button>
          </div>

          {/* Required Documents */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-slate-400" />
              Required Checklist Documents
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {scheme.required_documents.map((doc, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
                  {doc}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
