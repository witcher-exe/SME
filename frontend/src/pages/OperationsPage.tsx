import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { InvoiceListResponse, InvoiceData } from '@/types/api';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { CollectionNoticeDrawer } from '@/components/operations/CollectionNoticeDrawer';
import {
  Layers,
  Filter,
  Mail,
  AlertCircle,
  Clock,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';

export const OperationsPage: React.FC = () => {
  const { uiMode, companyId } = useOutletContext<{ uiMode: 'cfo' | 'owner'; companyId: string }>();
  const [data, setData] = useState<InvoiceListResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedInvoice, setSelectedInvoice] = useState<InvoiceData | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const res = await api.listInvoices(companyId, statusFilter || undefined, 0, 100);
      setData(res);
    } catch (err) {
      console.error('Invoices load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInvoices();
  }, [companyId, statusFilter]);

  const handleOpenDraft = (invoice: InvoiceData) => {
    setSelectedInvoice(invoice);
    setDrawerOpen(true);
  };

  const handleDraftSuccess = (approvalId: string) => {
    setToastMessage(`Tier 2 collection notice drafted. Approval ID: ${approvalId} queued in Governance.`);
    setTimeout(() => setToastMessage(null), 5000);
    loadInvoices();
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Toast */}
      {toastMessage && (
        <div className="fixed top-20 right-8 z-50 p-4 rounded-xl bg-indigo-950 border border-indigo-500/40 text-indigo-200 text-xs shadow-2xl flex items-center gap-2.5 animate-in slide-in-from-top-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-50 font-sans">
            Operations & Receivables Ledger
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {uiMode === 'cfo'
              ? 'Invoice aging schedule, payment probability distribution, and automated collection workflows.'
              : 'Track invoices, follow up on late payments, and draft collection reminders.'}
          </p>
        </div>

        <button
          onClick={loadInvoices}
          className="flex items-center gap-1.5 py-1.5 px-3 rounded-lg border border-[#232738] hover:bg-[#181B24] text-xs font-medium text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Aging Summary Cards */}
      {data && data.aging_summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-[#232738] bg-[#11131A]">
            <span className="text-[11px] font-semibold uppercase text-slate-400 block mb-1">
              Current (0–30 Days)
            </span>
            <div className="text-xl font-bold font-mono text-emerald-400">
              {formatCurrency(data.aging_summary.days_1_30, 'BDT')}
            </div>
          </div>
          <div className="p-4 rounded-xl border border-[#232738] bg-[#11131A]">
            <span className="text-[11px] font-semibold uppercase text-slate-400 block mb-1">
              31–60 Days
            </span>
            <div className="text-xl font-bold font-mono text-amber-400">
              {formatCurrency(data.aging_summary.days_31_60, 'BDT')}
            </div>
          </div>
          <div className="p-4 rounded-xl border border-[#232738] bg-[#11131A]">
            <span className="text-[11px] font-semibold uppercase text-slate-400 block mb-1">
              60+ Days (Severe)
            </span>
            <div className="text-xl font-bold font-mono text-red-400">
              {formatCurrency(data.aging_summary.days_60_plus, 'BDT')}
            </div>
          </div>
          <div className="p-4 rounded-xl border border-[#232738] bg-[#11131A]">
            <span className="text-[11px] font-semibold uppercase text-slate-400 block mb-1">
              Total Invoices
            </span>
            <div className="text-xl font-bold font-mono text-slate-100">
              {data.total}
            </div>
          </div>
        </div>
      )}

      {/* Filter Tabs & Table */}
      <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#232738]">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <div className="flex gap-1.5">
              {[
                { id: '', label: 'All Invoices' },
                { id: 'issued', label: 'Active / Issued' },
                { id: 'overdue', label: 'Overdue' },
                { id: 'paid', label: 'Paid' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setStatusFilter(tab.id)}
                  className={`py-1.5 px-3 rounded-lg text-xs font-medium transition-all ${
                    statusFilter === tab.id
                      ? 'bg-indigo-600 text-white font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#181B24]'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <span className="text-xs text-slate-400 font-mono">
            Showing {data?.items.length || 0} of {data?.total || 0} invoices
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-slate-500 font-mono">
            Loading invoice ledger...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead>
                <tr className="border-b border-[#232738] text-slate-400 uppercase tracking-wider font-medium">
                  <th className="py-3 px-3">Invoice #</th>
                  <th className="py-3 px-3">Debtor</th>
                  <th className="py-3 px-3">Amount</th>
                  <th className="py-3 px-3">Due Date</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Delay Risk</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E2230]">
                {data?.items.map((inv) => (
                  <tr key={inv.id} className="hover:bg-[#181B24]/60 transition-colors">
                    <td className="py-3.5 px-3 font-mono font-medium text-slate-200">
                      {inv.invoice_number}
                    </td>
                    <td className="py-3.5 px-3">
                      <div className="font-medium text-slate-200">{inv.debtor_name}</div>
                      {inv.debtor_email && (
                        <div className="text-[11px] text-slate-500 font-mono">{inv.debtor_email}</div>
                      )}
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-100 font-semibold text-sm">
                      {formatCurrency(inv.amount, inv.currency)}
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-400">{inv.due_date}</td>
                    <td className="py-3.5 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                          inv.status === 'overdue'
                            ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                            : inv.status === 'paid'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                        }`}
                      >
                        {inv.status}
                        {inv.days_overdue > 0 && ` (${inv.days_overdue}d)`}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 font-mono">
                      {inv.status !== 'paid' ? (
                        <div>
                          <span
                            className={
                              (inv.p_delay || 0) > 0.6
                                ? 'text-red-400 font-bold'
                                : (inv.p_delay || 0) > 0.3
                                ? 'text-amber-400 font-bold'
                                : 'text-emerald-400'
                            }
                          >
                            {((inv.p_delay || 0.2) * 100).toFixed(0)}%
                          </span>
                          <span className="text-slate-500 text-[11px] ml-1">
                            (+{inv.predicted_delay_days || 0}d)
                          </span>
                        </div>
                      ) : (
                        <span className="text-slate-500 font-mono">Settled</span>
                      )}
                    </td>
                    <td className="py-3.5 px-3 text-right">
                      {inv.status !== 'paid' ? (
                        <button
                          onClick={() => handleOpenDraft(inv)}
                          className="py-1.5 px-3 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 font-medium text-xs flex items-center gap-1.5 ml-auto"
                        >
                          <Mail className="w-3.5 h-3.5" />
                          Draft Notice
                        </button>
                      ) : (
                        <span className="text-slate-500 text-xs flex items-center gap-1 justify-end">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500/60" /> Paid
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Collection Notice Drawer */}
      <CollectionNoticeDrawer
        invoice={selectedInvoice}
        companyId={companyId}
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSuccess={handleDraftSuccess}
      />
    </div>
  );
};
