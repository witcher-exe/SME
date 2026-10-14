import React, { useState } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { SeedBenchmarkResponse } from '@/types/api';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import {
  Database,
  UploadCloud,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  FileSpreadsheet,
} from 'lucide-react';

export const DataPage: React.FC = () => {
  const { uiMode, companyId } = useOutletContext<{ uiMode: 'cfo' | 'owner'; companyId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SeedBenchmarkResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSeed = async (scenario: 'bengal_craft' | 'shenzhen_importer') => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.seedBenchmark(scenario);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to seed benchmark scenario.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-50 font-sans">
          Data Ingestion & Benchmark Scenarios
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          {uiMode === 'cfo'
            ? 'Deterministic dataset ingestion with automated PII tokenization and SHA-256 hash chaining.'
            : 'Load real-world business scenarios or upload your own banking transactions.'}
        </p>
      </div>

      {/* 1-Click Benchmark Scenarios Card */}
      <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[#232738]">
          <Database className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-100 font-sans">
            Pre-Built Benchmark Scenarios
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Scenario 1: Bengal Craft & Retail */}
          <div className="p-5 rounded-xl border border-indigo-500/30 bg-[#181B24] space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-indigo-400 uppercase font-mono">
                  Primary Benchmark
                </span>
                <span className="text-[11px] text-slate-400 font-mono">128 Txns · 56 Invoices</span>
              </div>
              <h3 className="text-base font-bold text-slate-50">Bengal Craft & Retail</h3>
              <p className="text-xs text-slate-400 leading-relaxed mt-1 font-sans">
                Dhaka handicraft exporter experiencing working capital stress due to overdue customer payments.
                Demonstrates Day 21 shortfall trigger and DSCR covenant remediation.
              </p>
            </div>

            <button
              onClick={() => handleSeed('bengal_craft')}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-sm"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? 'Seeding Dataset...' : 'Load Bengal Craft & Retail'}
            </button>
          </div>

          {/* Scenario 2: Shenzhen Importer */}
          <div className="p-5 rounded-xl border border-[#232738] bg-[#181B24] space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-400 uppercase font-mono">
                  Cross-Border Scenario
                </span>
                <span className="text-[11px] text-slate-400 font-mono">60 Txns · FX / Customs</span>
              </div>
              <h3 className="text-base font-bold text-slate-50">Shenzhen Cross-Border Importer</h3>
              <p className="text-xs text-slate-400 leading-relaxed mt-1 font-sans">
                Consumer electronics distributor dealing with supplier component price inflation and port clearance delays.
              </p>
            </div>

            <button
              onClick={() => handleSeed('shenzhen_importer')}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg border border-[#232738] hover:bg-[#232738] text-slate-300 text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              <Database className="w-4 h-4" />
              {loading ? 'Seeding Dataset...' : 'Load Shenzhen Importer'}
            </button>
          </div>
        </div>

        {/* Success Confirmation Card */}
        {result && (
          <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/15 text-xs text-emerald-200 space-y-2 animate-in fade-in">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-slate-100">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>{result.message}</span>
              </div>
              <button
                onClick={() => navigate('/dashboard')}
                className="py-1 px-3 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1"
              >
                Go to Dashboard <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-emerald-500/20 font-mono text-[11px]">
              <div>
                <span className="text-slate-400 block">Transactions:</span>
                <span className="text-slate-100 font-bold">{result.transactions_count} rows</span>
              </div>
              <div>
                <span className="text-slate-400 block">Invoices:</span>
                <span className="text-slate-100 font-bold">{result.invoices_count} rows</span>
              </div>
              <div>
                <span className="text-slate-400 block">PII Redacted:</span>
                <span className="text-emerald-400 font-bold">{result.pii_entities_redacted} entities</span>
              </div>
              <div>
                <span className="text-slate-400 block">Starting Cash:</span>
                <span className="text-slate-100 font-bold">
                  {formatCurrency(result.initial_cash_balance, 'BDT')}
                </span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 rounded-lg border border-red-500/30 bg-red-950/20 text-xs text-red-400">
            {error}
          </div>
        )}
      </div>

      {/* Custom CSV Upload Dropzone */}
      <div className="rounded-xl border border-[#232738] bg-[#11131A] p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[#232738]">
          <UploadCloud className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-100 font-sans">
            Custom Ledger Ingestion (CSV / XLSX)
          </h2>
        </div>

        <div className="p-8 border-2 border-dashed border-[#232738] hover:border-indigo-500/40 rounded-xl text-center space-y-3 bg-[#090A0F] transition-all cursor-pointer">
          <FileSpreadsheet className="w-10 h-10 text-slate-500 mx-auto" />
          <div>
            <div className="text-xs font-semibold text-slate-200">
              Drag and drop banking statement or invoice register CSV
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Automated PII scrubbing will anonymize names, phone numbers, and TIN tax IDs before storage.
            </p>
          </div>
          <button className="py-2 px-4 rounded-lg bg-[#181B24] hover:bg-[#232738] text-xs font-medium text-slate-300 border border-[#232738]">
            Browse Local File
          </button>
        </div>
      </div>
    </div>
  );
};
