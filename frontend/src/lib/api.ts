import {
  DashboardResponse,
  ForecastResponse,
  ScenarioResponse,
  FinancingResponse,
  InvoiceListResponse,
  DraftCollectionResponse,
  ApprovalListResponse,
  AuditTrailResponse,
  SeedBenchmarkResponse,
} from '@/types/api';

const BASE_URL = '/api';

export const api = {
  async getDashboard(companyId: string): Promise<DashboardResponse> {
    const res = await fetch(`${BASE_URL}/dashboard/${companyId}`);
    if (!res.ok) throw new Error(`Dashboard fetch failed: ${res.statusText}`);
    return res.json();
  },

  async runForecast(companyId: string, horizonDays: number = 90, mcRuns: number = 1000): Promise<ForecastResponse> {
    const res = await fetch(`${BASE_URL}/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_id: companyId, horizon_days: horizonDays, mc_runs: mcRuns }),
    });
    if (!res.ok) throw new Error(`Forecast failed: ${res.statusText}`);
    return res.json();
  },

  async runScenario(
    companyId: string,
    debtorDelayDays: number = 0,
    supplierCostDeltaPct: number = 0,
    capexSpend: number = 0,
    applyFactoringAdvance: boolean = false
  ): Promise<ScenarioResponse> {
    const res = await fetch(`${BASE_URL}/scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: companyId,
        debtor_delay_days: debtorDelayDays,
        supplier_cost_delta_pct: supplierCostDeltaPct,
        capex_spend: capexSpend,
        apply_factoring_advance: applyFactoringAdvance,
      }),
    });
    if (!res.ok) throw new Error(`Scenario failed: ${res.statusText}`);
    return res.json();
  },

  async getFinancing(companyId: string): Promise<FinancingResponse> {
    const res = await fetch(`${BASE_URL}/financing/${companyId}`);
    if (!res.ok) throw new Error(`Financing fetch failed: ${res.statusText}`);
    return res.json();
  },

  async listInvoices(
    companyId: string,
    status?: string,
    offset: number = 0,
    limit: number = 50
  ): Promise<InvoiceListResponse> {
    const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
    if (status) params.append('status', status);
    const res = await fetch(`${BASE_URL}/invoices/${companyId}?${params.toString()}`);
    if (!res.ok) throw new Error(`Invoice list failed: ${res.statusText}`);
    return res.json();
  },

  async draftCollection(
    companyId: string,
    invoiceId: string,
    tone: string = 'standard_firm'
  ): Promise<DraftCollectionResponse> {
    const res = await fetch(`${BASE_URL}/draft-collection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: companyId,
        invoice_id: invoiceId,
        tone: tone,
        queue_for_approval: true,
      }),
    });
    if (!res.ok) throw new Error(`Draft collection failed: ${res.statusText}`);
    return res.json();
  },

  async listApprovals(companyId: string): Promise<ApprovalListResponse> {
    const res = await fetch(`${BASE_URL}/approvals/${companyId}`);
    if (!res.ok) throw new Error(`Approvals fetch failed: ${res.statusText}`);
    return res.json();
  },

  async approveAction(approvalId: string, decision: 'approved' | 'rejected', reason?: string): Promise<any> {
    const res = await fetch(`${BASE_URL}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        approval_id: approvalId,
        decision,
        reason: reason || 'Authorized by human reviewer',
      }),
    });
    if (!res.ok) throw new Error(`Approval action failed: ${res.statusText}`);
    return res.json();
  },

  async getAuditTrail(companyId: string, offset: number = 0, limit: number = 100): Promise<AuditTrailResponse> {
    const res = await fetch(`${BASE_URL}/audit-trail/${companyId}?offset=${offset}&limit=${limit}`);
    if (!res.ok) throw new Error(`Audit trail failed: ${res.statusText}`);
    return res.json();
  },

  async seedBenchmark(scenario: 'bengal_craft' | 'shenzhen_importer'): Promise<SeedBenchmarkResponse> {
    const res = await fetch(`${BASE_URL}/seed-benchmark`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario }),
    });
    if (!res.ok) throw new Error(`Benchmark seed failed: ${res.statusText}`);
    return res.json();
  },

  async ingestCSV(companyId: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/ingest?company_id=${companyId}`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`CSV ingestion failed: ${res.statusText}`);
    return res.json();
  },
};
