import React, { useState } from 'react';
import { InvoiceData, CollectionTone, DraftCollectionResponse } from '@/types/api';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { X, Send, ShieldCheck, Mail, CheckCircle } from 'lucide-react';

interface CollectionNoticeDrawerProps {
  invoice: InvoiceData | null;
  companyId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (approvalId: string) => void;
}

export const CollectionNoticeDrawer: React.FC<CollectionNoticeDrawerProps> = ({
  invoice,
  companyId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [tone, setTone] = useState<CollectionTone>('standard_firm');
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState<DraftCollectionResponse | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !invoice) return null;

  const handleGenerateDraft = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.draftCollection(companyId, invoice.id, tone);
      setDraft(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate draft');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitForApproval = () => {
    if (draft?.approval_id) {
      setSubmitted(true);
      onSuccess(draft.approval_id);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-[#11131A] border-l border-[#232738] h-full overflow-y-auto flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-[#232738] flex items-start justify-between bg-[#181B24]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Tier 2 Action (Draft)
              </span>
              <span className="text-xs text-slate-400">{invoice.invoice_number}</span>
            </div>
            <h2 className="text-lg font-bold text-slate-50">Draft Collection Notice</h2>
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
          {/* Invoice Summary */}
          <div className="p-4 rounded-xl border border-[#232738] bg-[#181B24] space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Debtor:</span>
              <span className="font-semibold text-slate-200">{invoice.debtor_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Amount:</span>
              <span className="font-mono font-semibold text-slate-50">
                {formatCurrency(invoice.amount, invoice.currency)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Days Overdue:</span>
              <span className="font-mono text-red-400 font-semibold">{invoice.days_overdue} days</span>
            </div>
          </div>

          {/* Tone Selector */}
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
              Communication Tone
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'polite_nudge', label: 'Polite Nudge' },
                { id: 'standard_firm', label: 'Standard Firm' },
                { id: 'formal_demand', label: 'Formal Demand' },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => {
                    setTone(t.id as CollectionTone);
                    setDraft(null);
                  }}
                  className={`py-2 px-3 rounded-lg text-xs font-medium border text-center transition-all ${
                    tone === t.id
                      ? 'border-indigo-500 bg-indigo-500/10 text-indigo-300'
                      : 'border-[#232738] bg-[#181B24] text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Generate Draft Button */}
          {!draft && (
            <button
              onClick={handleGenerateDraft}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              <Mail className="w-4 h-4" />
              {loading ? 'Synthesizing Draft...' : 'Generate Email Draft'}
            </button>
          )}

          {error && (
            <div className="p-3 rounded-lg border border-red-500/20 bg-red-950/20 text-xs text-red-400">
              {error}
            </div>
          )}

          {/* Draft Preview */}
          {draft && !submitted && (
            <div className="space-y-4 animate-in fade-in duration-150">
              <div className="border border-[#232738] rounded-xl bg-[#090A0F] p-4 text-xs font-sans space-y-2">
                <div className="text-slate-400">
                  <span className="font-medium text-slate-300">Subject: </span>
                  {draft.subject}
                </div>
                <div className="border-t border-[#1E2230] pt-2 whitespace-pre-wrap text-slate-300 leading-relaxed font-sans">
                  {draft.body}
                </div>
              </div>

              <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Governance Policy:</strong> {draft.governance_note}
                </span>
              </div>

              {/* Submit for Approval */}
              <button
                onClick={handleSubmitForApproval}
                className="w-full py-2.5 px-4 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-amber-600/20"
              >
                <Send className="w-4 h-4" />
                Submit to Owner Approval Inbox (T4)
              </button>
            </div>
          )}

          {submitted && (
            <div className="p-6 text-center space-y-3 bg-emerald-950/10 border border-emerald-500/20 rounded-xl">
              <CheckCircle className="w-10 h-10 text-emerald-400 mx-auto" />
              <div className="text-sm font-semibold text-slate-50">Notice Submitted for T4 Approval</div>
              <p className="text-xs text-slate-400">
                Action queued. Navigate to Governance inbox to review and authorize sending.
              </p>
              <button
                onClick={onClose}
                className="mt-2 py-2 px-4 rounded-lg bg-[#232738] hover:bg-[#33394D] text-xs text-slate-200"
              >
                Close Drawer
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
