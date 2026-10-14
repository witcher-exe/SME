export type RunwayStatus = 'healthy' | 'warning' | 'critical';
export type InvoiceStatus = 'issued' | 'paid' | 'overdue' | 'disputed';
export type RiskLevel = 'low' | 'medium' | 'high';
export type CollectionTone = 'polite_nudge' | 'standard_firm' | 'formal_demand';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'auto_approved';
export type UIMode = 'cfo' | 'owner';

export interface CompanySummary {
  id: string;
  name: string;
  currency: string;
  industry?: string;
  initial_cash_balance: number;
}

export interface RunwayData {
  days_left: number;
  burn_rate_daily: number;
  burn_rate_monthly: number;
  status: RunwayStatus;
  shortfall_date?: string | null;
  shortfall_amount?: number | null;
}

export interface MetricsData {
  liquid_cash: number;
  open_ar: number;
  overdue_ar: number;
  overdue_count: number;
  cash_conversion_cycle_days: number;
  days_sales_outstanding: number;
  days_payable_outstanding: number;
  concentration_pct?: number | null;
  top_debtor?: string | null;
}

export interface ForecastChartData {
  weeks: string[];
  dates: string[];
  p10_conservative: number[];
  p50_median: number[];
  p90_optimistic: number[];
  safety_floor: number;
}

export interface AlertData {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  action_label?: string | null;
  action_route?: string | null;
  created_at: string;
}

export interface InvoiceData {
  id: string;
  invoice_number: string;
  debtor_name: string;
  debtor_email?: string | null;
  amount: number;
  currency: string;
  issued_date: string;
  due_date: string;
  paid_date?: string | null;
  status: InvoiceStatus;
  days_overdue: number;
  p_delay?: number | null;
  predicted_delay_days?: number | null;
  risk_level?: RiskLevel | null;
}

export interface DashboardResponse {
  company: CompanySummary;
  runway: RunwayData;
  metrics: MetricsData;
  forecast_chart: ForecastChartData;
  alerts: AlertData[];
  high_risk_invoices: InvoiceData[];
}

export interface InvoiceDelayPrediction {
  invoice_id: string;
  invoice_number: string;
  debtor_name: string;
  amount: number;
  due_date: string;
  p_delay: number;
  predicted_delay_days: number;
  risk_level: RiskLevel;
  historical_avg_delay: number;
}

export interface ForecastResponse {
  company_id: string;
  forecast_chart: ForecastChartData;
  shortfall_date?: string | null;
  shortfall_amount?: number | null;
  runway_days: number;
  confidence: number;
  invoice_risks: InvoiceDelayPrediction[];
  computed_at: string;
}

export interface SimulationWeek {
  week: string;
  date: string;
  baseline_cash: number;
  simulated_cash: number;
}

export interface ScenarioResponse {
  scenario_name: string;
  baseline_shortfall_date?: string | null;
  simulated_shortfall_date?: string | null;
  delta_days: number;
  simulated_runway_days: number;
  weekly_simulation: SimulationWeek[];
  recommendation: string;
  computed_at: string;
}

export interface CovenantStatus {
  name: string;
  current_value: number;
  required_value: number;
  result: 'pass' | 'fail' | 'warning';
  formula: string;
}

export interface FailedRule {
  rule_name: string;
  required: string;
  actual: string;
  gap: string;
}

export interface SchemeEvaluation {
  id: string;
  name: string;
  issuer: string;
  rate_pct: number;
  max_amount: number;
  currency: string;
  tenure_months: number;
  eligible: boolean;
  match_score: number;
  effective_date: string;
  source_url: string;
  is_stale: boolean;
  status_tag: string;
  failed_rules: FailedRule[];
  remediation_steps: string[];
  required_documents: string[];
}

export interface FinancingResponse {
  company_id: string;
  covenants: CovenantStatus[];
  schemes: SchemeEvaluation[];
  eligible_count: number;
  ineligible_count: number;
  computed_at: string;
  underwriting_readiness_score?: number;
}

export interface InvoiceListResponse {
  items: InvoiceData[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
  aging_summary: {
    current: number;
    days_1_30: number;
    days_31_60: number;
    days_60_plus: number;
  };
}

export interface DraftCollectionResponse {
  draft_id: string;
  approval_id?: string | null;
  invoice_id: string;
  invoice_number: string;
  recipient_email: string;
  subject: string;
  body: string;
  tone: CollectionTone;
  tier: string;
  governance_note: string;
  created_at: string;
}

export interface ApprovalData {
  id: string;
  company_id: string;
  tier: string;
  action_type: string;
  payload: Record<string, any>;
  justification?: string | null;
  status: ApprovalStatus;
  requested_by: string;
  approved_by?: string | null;
  rejection_reason?: string | null;
  created_at: string;
  resolved_at?: string | null;
}

export interface PIITelemetryItem {
  hmac_token: string;
  entity_category: string;
  masked_preview: string;
  raw_sample_context: string;
  sanitized_context: string;
}

export interface ApprovalListResponse {
  items: ApprovalData[];
  pending_count: number;
  approved_count: number;
  rejected_count: number;
  pii_telemetry: PIITelemetryItem[];
}

export interface AuditEntryData {
  id: string;
  block_number: number;
  timestamp: string;
  agent_role: string;
  tool_name: string;
  input_hash: string;
  output_hash: string;
  permission_tier: string;
  current_hash: string;
  previous_hash: string;
  verified: boolean;
}

export interface AuditTrailResponse {
  items: AuditEntryData[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
  chain_intact: boolean;
}

export interface SeedBenchmarkResponse {
  company_id: string;
  company_name: string;
  transactions_count: number;
  invoices_count: number;
  pii_entities_redacted: number;
  date_range: { start: string; end: string };
  initial_cash_balance: number;
  message: string;
}

export interface ThoughtTrace {
  step: string;
  detail: string;
  timestamp: string;
  tool_call?: {
    tool: string;
    params: Record<string, any>;
  };
}

export interface ActionChip {
  label: string;
  action: string;
  route?: string;
  params?: Record<string, any>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  thoughts?: ThoughtTrace[];
  actionChips?: ActionChip[];
  tier?: string;
  blocked?: boolean;
}
