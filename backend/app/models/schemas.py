from typing import List, Optional, Dict, Any, Generic, TypeVar, Literal
from pydantic import BaseModel, Field
from app.models.enums import (
    Tier,
    Direction,
    InvoiceStatus,
    RiskLevel,
    AlertSeverity,
    ApprovalStatus,
    ApprovalActionType,
    SchemeEligibility,
    Persona,
    CollectionTone,
    RunwayStatus,
    CovenantResult,
    PIICategory,
    BenchmarkScenario,
)

T = TypeVar("T")

# --- 1. Shared & Error Responses ---

class ErrorResponse(BaseModel):
    error: str
    detail: str
    code: str

class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = 50

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    offset: int
    limit: int
    has_more: bool

# --- 2. Dashboard Schemas ---

class MetricsData(BaseModel):
    liquid_cash: float
    pending_receivables: float
    overdue_receivables: float
    overdue_count: int
    monthly_net_burn: float
    cash_conversion_cycle: Optional[float] = None
    dso: Optional[float] = None
    dpo: Optional[float] = None
    concentration_risk_pct: Optional[float] = None
    concentration_debtor: Optional[str] = None

class RunwayData(BaseModel):
    days_left: int
    shortfall_date: Optional[str] = None
    shortfall_amount: Optional[float] = None
    status: RunwayStatus

class ForecastChartData(BaseModel):
    weeks: List[str]
    dates: List[str]
    p10_conservative: List[float]
    p50_median: List[float]
    p90_optimistic: List[float]
    safety_floor: float

class AlertData(BaseModel):
    id: str
    severity: AlertSeverity
    title: str
    description: str
    action_label: str
    action_type: str
    related_entity_id: Optional[str] = None

class CompanySummary(BaseModel):
    id: str
    name: str
    currency: str

class DashboardResponse(BaseModel):
    company: CompanySummary
    runway: RunwayData
    metrics: MetricsData
    forecast_chart: ForecastChartData
    alerts: List[AlertData]

# --- 3. Forecast Schemas ---

class ForecastRequest(BaseModel):
    company_id: str
    horizon_days: int = 90
    mc_runs: int = 1000
    seed: Optional[int] = None

class InvoiceDelayPrediction(BaseModel):
    invoice_id: str
    invoice_number: str
    debtor_name: str
    amount: float
    due_date: str
    p_delay: float
    predicted_delay_days: int
    risk_level: RiskLevel
    historical_avg_delay: Optional[float] = None

class ForecastResponse(BaseModel):
    company_id: str
    forecast_chart: ForecastChartData
    shortfall_date: Optional[str] = None
    shortfall_amount: Optional[float] = None
    runway_days: int
    confidence: float
    invoice_risks: List[InvoiceDelayPrediction]
    computed_at: str

# --- 4. Scenario Schemas ---

class ScenarioRequest(BaseModel):
    company_id: str
    debtor_delay_days: int = 0
    supplier_cost_delta_pct: float = 0.0
    capex_spend: float = 0.0
    apply_factoring_advance: bool = False

class WeeklyComparison(BaseModel):
    week: str
    date: str
    baseline_cash: float
    simulated_cash: float
    projected_inflow: float
    projected_outflow: float

class ScenarioResponse(BaseModel):
    company_id: str
    baseline_shortfall_day: Optional[int] = None
    scenario_shortfall_day: Optional[int] = None
    delta_days: int
    weekly_simulation: List[WeeklyComparison]
    debtor_risks: List[InvoiceDelayPrediction]
    factoring_advance_amount: Optional[float] = None
    computed_at: str

# --- 5. Financing Schemas ---

class CovenantStatus(BaseModel):
    name: str
    current_value: float
    required_value: Optional[float] = None
    result: CovenantResult
    formula: str

class FailedRule(BaseModel):
    rule_name: str
    required: str
    actual: str
    gap: str

class SchemeEvaluation(BaseModel):
    id: str
    name: str
    issuer: str
    rate_pct: float
    max_amount: float
    currency: str
    tenure_months: int
    eligible: bool
    match_score: int
    effective_date: str
    source_url: str
    is_stale: bool
    status_tag: str
    failed_rules: List[FailedRule]
    remediation_steps: List[str]
    required_documents: List[str]

class FinancingResponse(BaseModel):
    company_id: str
    covenants: List[CovenantStatus]
    schemes: List[SchemeEvaluation]
    eligible_count: int
    ineligible_count: int
    computed_at: str

# --- 6. Invoice Schemas ---

class InvoiceData(BaseModel):
    id: str
    invoice_number: str
    debtor_name: str
    debtor_email: Optional[str] = None
    amount: float
    currency: str
    issued_date: str
    due_date: str
    paid_date: Optional[str] = None
    status: InvoiceStatus
    days_overdue: int
    p_delay: Optional[float] = None
    predicted_delay_days: Optional[int] = None
    risk_level: Optional[RiskLevel] = None

class InvoiceListResponse(BaseModel):
    items: List[InvoiceData]
    total: int
    offset: int
    limit: int
    has_more: bool
    aging_summary: Dict[str, float]
    aging_counts: Dict[str, int]

# --- 7. Draft Collection Schemas ---

class DraftCollectionRequest(BaseModel):
    company_id: str
    invoice_id: str
    tone: CollectionTone = CollectionTone.STANDARD_FIRM
    queue_for_approval: bool = True  # Creates a PENDING T4 Approval record in approval table

class DraftCollectionResponse(BaseModel):
    draft_id: str
    approval_id: Optional[str] = None  # UUID of queued PENDING Approval record (for POST /api/approve)
    invoice_id: str
    invoice_number: str
    recipient_email: str
    subject: str
    body: str
    tone: CollectionTone
    tier: str = "T2"
    governance_note: str = "This draft requires T4 approval to send."
    created_at: str

# --- 8. Approvals & Governance Schemas ---

class ApprovalData(BaseModel):
    id: str
    action_type: ApprovalActionType
    payload_summary: str
    payload: Dict[str, Any]
    justification: Optional[str] = None
    status: ApprovalStatus
    requested_by: str
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None

class PIITelemetryItem(BaseModel):
    hmac_token: str                       # e.g., "HMAC_CUST_8821"
    entity_category: PIICategory
    masked_preview: str                   # e.g., "Md. K*** U***" (safe for display)
    raw_sample_context: str               # e.g., "Payment from [REDACTED_PERSON_NAME]"
    sanitized_context: str                # e.g., "Payment from HMAC_CUST_8821"

class ApprovalListResponse(BaseModel):
    items: List[ApprovalData]
    pending_count: int
    approved_count: int
    rejected_count: int
    pii_telemetry: List[PIITelemetryItem] = []  # Populates PIIRedactionDiff on /governance

class ApproveRequest(BaseModel):
    approval_id: str
    decision: str  # "approved" or "rejected"
    reason: Optional[str] = None

class ApproveResponse(BaseModel):
    approval_id: str
    status: ApprovalStatus
    resolved_at: str
    audit_block: int
    message: str

# --- 9. Audit Trail Schemas ---

class AuditEntryData(BaseModel):
    id: str
    block_number: int
    timestamp: str
    agent_role: str
    tool_name: str
    input_hash: str
    output_hash: str
    permission_tier: str
    current_hash: str
    previous_hash: str
    verified: bool

class AuditTrailResponse(BaseModel):
    items: List[AuditEntryData]
    total: int
    offset: int
    limit: int
    has_more: bool
    chain_intact: bool

# --- 10. Ingestion & Benchmark Schemas ---

class SeedBenchmarkRequest(BaseModel):
    scenario: BenchmarkScenario = BenchmarkScenario.BENGAL_CRAFT

class SeedBenchmarkResponse(BaseModel):
    company_id: str
    company_name: str
    transactions_count: int
    invoices_count: int
    pii_entities_redacted: int
    date_range: Dict[str, str]
    initial_cash_balance: float
    message: str

class RedactionPreview(BaseModel):
    original: str
    token: str
    category: PIICategory

class IngestPreviewResponse(BaseModel):
    detected_rows: int
    sample_rows: List[Dict[str, Any]]
    pii_redactions_detected: int
    sample_redactions: List[RedactionPreview]
    columns_matched: List[str]
    columns_missing: List[str]

class IngestCommitResponse(BaseModel):
    company_id: str
    transactions_imported: int
    invoices_imported: int
    pii_tokens_created: int
    message: str

# --- 11. Chat & SSE Stream Schemas ---

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    company_id: str
    message: str
    persona: Persona = Persona.OWNER
    conversation_history: List[ChatMessage] = []

class ActionChip(BaseModel):
    label: str
    action: str

class ThoughtEvent(BaseModel):
    type: Literal["thought"] = "thought"
    agent: str
    text: str
    timestamp: str

class ToolCallEvent(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    agent: str
    tool: str
    args: Dict[str, Any]
    timestamp: str

class ToolResultEvent(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    agent: str
    tool: str
    result: Dict[str, Any]
    duration_ms: int
    timestamp: str

class SynthesisEvent(BaseModel):
    type: Literal["synthesis"] = "synthesis"
    text: str
    citations: List[str] = []
    action_chips: List[ActionChip] = []
    timestamp: str

class ApprovalRequiredEvent(BaseModel):
    type: Literal["approval_required"] = "approval_required"
    approval_id: str
    action_type: ApprovalActionType
    summary: str
    timestamp: str

class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str
    timestamp: str

class DoneEvent(BaseModel):
    type: Literal["done"] = "done"
    thread_id: str
    timestamp: str

# --- 12. Scheme Catalog Definition Schemas ---

class EligibilityRules(BaseModel):
    cib_clearance: bool = False
    min_dscr: Optional[float] = None
    min_turnover_bdt: Optional[float] = None
    min_operating_months: Optional[int] = None
    max_leverage: Optional[float] = None
    ownership_requirement: Optional[str] = None
    required_documents: List[str] = []

class SchemeDefinition(BaseModel):
    id: str
    name: str
    issuer: str
    effective_date: str
    expiry_date: Optional[str] = None
    source_url: str
    retrieval_date: str
    rate_cap_pct: float
    max_amount_bdt: float
    tenure_months: int
    eligibility_rules: EligibilityRules
    status: str
