# AuraCFO — Backend API Schema & Endpoints
## FinTechathon 2026 · Topic E · SME Finance Copilot

> **Version:** 1.1 · **Date:** 2026-10-14 · **Status:** PATCHED & VERIFIED FOR BUILD
> **Purpose:** Definitive API contract. Every endpoint, every Pydantic model, every DB table, every enum. Coding agents MUST NOT deviate from this document.
> **Companion to:** TRD.md (tech rules) → APP_FLOW.md (user journeys) → this doc (exact data shapes)

---

## Table of Contents

1. [Enum Definitions](#1-enum-definitions)
2. [Database Tables (SQLAlchemy Models)](#2-database-tables)
3. [Shared Response Patterns](#3-shared-response-patterns)
4. [API Endpoints](#4-api-endpoints)
5. [SSE Streaming Contract (`/api/chat`)](#5-sse-streaming-contract)
6. [Scheme Catalog JSON Schema](#6-scheme-catalog-json-schema)
7. [Cross-Reference: Endpoint → Flow → Component](#7-cross-reference)

---

## 1. Enum Definitions

These enums are defined in `backend/app/models/enums.py` and imported wherever needed. They are the canonical set — no ad-hoc string literals elsewhere.

```python
# backend/app/models/enums.py
from enum import Enum, IntEnum

class Tier(IntEnum):
    """Permission tier for tool execution. Enforced by @requires_tier decorator."""
    T0_READ = 0
    T1_ANALYZE = 1
    T2_DRAFT = 2
    T3_PREPARE = 3
    T4_EXECUTE = 4

class Direction(str, Enum):
    """Transaction direction."""
    CREDIT = "credit"    # Money in (customer payment, revenue)
    DEBIT = "debit"      # Money out (expense, payroll, rent)

class InvoiceStatus(str, Enum):
    """Invoice lifecycle state."""
    ISSUED = "issued"        # Created, not yet due
    OVERDUE = "overdue"      # Past due date, not paid
    PAID = "paid"            # Payment received
    WRITTEN_OFF = "written_off"  # Deemed uncollectable

class RiskLevel(str, Enum):
    """Payment delay risk classification."""
    LOW = "low"          # P(delay) < 0.30
    MEDIUM = "medium"    # 0.30 <= P(delay) <= 0.60
    HIGH = "high"        # P(delay) > 0.60

class AlertSeverity(str, Enum):
    """Alert urgency level."""
    CRITICAL = "critical"  # Shortfall within 21 days
    WARNING = "warning"    # Shortfall within 30 days
    INFO = "info"          # Informational (e.g., concentration risk)

class ApprovalStatus(str, Enum):
    """Approval lifecycle state (one-way transitions only)."""
    PENDING = "pending"      # Awaiting human decision
    APPROVED = "approved"    # Owner approved — immutable
    REJECTED = "rejected"    # Owner rejected — immutable

class ApprovalActionType(str, Enum):
    """Types of actions that require T4 approval."""
    COLLECTION_EMAIL = "collection_email"
    LOAN_APPLICATION = "loan_application"
    FINANCING_PACK = "financing_pack"

class SchemeEligibility(str, Enum):
    """Financing scheme match result."""
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"

class Persona(str, Enum):
    """Copilot communication mode."""
    OWNER = "owner"  # Plain English, analogies, no jargon
    CFO = "cfo"      # Formal terms, DSCR, p-values, formulas

class CollectionTone(str, Enum):
    """Tone for collection email drafts."""
    POLITE_NUDGE = "polite_nudge"
    STANDARD_FIRM = "standard_firm"
    FORMAL_DEMAND = "formal_demand"

class RunwayStatus(str, Enum):
    """Cash runway health classification."""
    HEALTHY = "healthy"    # > 60 days
    WARNING = "warning"    # 30-60 days
    CRITICAL = "critical"  # < 30 days

class CovenantResult(str, Enum):
    """Individual covenant evaluation result."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"  # Within 10% of threshold

class PIICategory(str, Enum):
    """Category of detected PII entity."""
    PERSON_NAME = "person_name"
    NATIONAL_ID = "national_id"    # BD: 13 or 17 digit NID
    TAX_ID = "tax_id"              # TIN
    BANK_ACCOUNT = "bank_account"
    PHONE_NUMBER = "phone_number"
    EMAIL_ADDRESS = "email_address"

class BenchmarkScenario(str, Enum):
    """Available benchmark datasets."""
    BENGAL_CRAFT = "bengal_craft"
    SHENZHEN_IMPORTER = "shenzhen_importer"
```

---

## 2. Database Tables

All tables are defined in `backend/app/models/`. All primary keys are UUID4, all timestamps are UTC.

### 2.1 Company

```python
# backend/app/models/company.py
class Company(Base):
    __tablename__ = "company"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID4
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BDT")  # ISO 4217
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    owner_name_hash: Mapped[str] = mapped_column(String(64), nullable=True)  # SHA-256 of real name
    tax_id_hash: Mapped[str] = mapped_column(String(64), nullable=True)  # SHA-256 of TIN
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    initial_cash_balance: Mapped[float] = mapped_column(Float, default=0.0)
    balance_sheet_snapshot: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )  # Keys: inventory_bdt, accounts_payable_bdt, current_liabilities_bdt, total_debt_bdt, total_equity_bdt, monthly_debt_service_bdt

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="company")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="company")
    audit_entries: Mapped[list["AuditEntry"]] = relationship(back_populates="company")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="company")
    pii_tokens: Mapped[list["PIIToken"]] = relationship(back_populates="company")
```

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `String(36)` | PK | UUID4, generated in Python |
| `name` | `String(255)` | NOT NULL | Display name (e.g., "Bengal Craft & Retail") |
| `currency` | `String(3)` | NOT NULL, default `"BDT"` | ISO 4217 code |
| `industry` | `String(100)` | nullable | e.g., "Retail", "Manufacturing" |
| `owner_name_hash` | `String(64)` | nullable | SHA-256 hash — real name never stored |
| `tax_id_hash` | `String(64)` | nullable | SHA-256 hash — real TIN never stored |
| `created_at` | `DateTime` | NOT NULL | UTC timestamp |
| `initial_cash_balance` | `Float` | default 0.0 | Starting balance for forecast engine |

### 2.2 Transaction

```python
# backend/app/models/transaction.py
class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # Direction enum
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # revenue, expense, transfer
    counterparty: Mapped[str] = mapped_column(String(255), nullable=True)  # HMAC token, not real name
    raw_narration: Mapped[str] = mapped_column(Text, nullable=True)  # PII-scrubbed narration
    pii_scrubbed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="transactions")
```

| Column | Type | Constraints | Index? | Notes |
|---|---|---|---|---|
| `id` | `String(36)` | PK | — | UUID4 |
| `company_id` | `String(36)` | FK → company.id, NOT NULL | ✅ | Parent company |
| `date` | `Date` | NOT NULL | ✅ | Transaction date |
| `amount` | `Float` | NOT NULL | — | Always positive; direction indicates in/out |
| `direction` | `String(10)` | NOT NULL | — | `"credit"` or `"debit"` |
| `category` | `String(50)` | nullable | — | Auto-categorized or user-assigned |
| `counterparty` | `String(255)` | nullable | — | HMAC token if PII detected |
| `raw_narration` | `Text` | nullable | — | Bank memo, PII-scrubbed |
| `pii_scrubbed` | `Boolean` | default False | — | Whether PII sanitizer ran |
| `created_at` | `DateTime` | NOT NULL | — | Ingestion timestamp |

### 2.3 Invoice

```python
# backend/app/models/invoice.py
class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False)
    debtor_name: Mapped[str] = mapped_column(String(255), nullable=False)  # HMAC token if PII
    debtor_email: Mapped[str] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    paid_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="issued")  # InvoiceStatus
    p_delay: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 to 1.0
    predicted_delay_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # RiskLevel
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="invoices")
```

### 2.4 AuditEntry

```python
# backend/app/models/audit_entry.py
class AuditEntry(Base):
    __tablename__ = "audit_entry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    block_number: Mapped[int] = mapped_column(Integer, nullable=False)  # Sequential, per company
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    agent_role: Mapped[str] = mapped_column(String(50), nullable=False)  # orchestrator, quant_modeler, etc.
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)  # forecast_cash, match_financing, etc.
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of input payload
    output_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of output payload
    permission_tier: Mapped[str] = mapped_column(String(5), nullable=False)  # T0, T1, T2, T3, T4
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)  # H_n
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # H_{n-1}

    company: Mapped["Company"] = relationship(back_populates="audit_entries")
```

**Constraints:** No UPDATE or DELETE allowed. Append-only table. `block_number` is sequential per `company_id`. `current_hash` is globally unique.

**Hash formula:** `H_n = SHA-256(f"{previous_hash}|{timestamp.isoformat()}|{agent_role}|{tool_name}|{input_hash}|{output_hash}".encode("utf-8"))`

### 2.5 Approval

```python
# backend/app/models/approval.py
class Approval(Base):
    __tablename__ = "approval"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ApprovalActionType
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # Full action details (draft email, loan pack)
    justification: Mapped[str] = mapped_column(Text, nullable=True)  # Agent's reason for the action
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # ApprovalStatus
    requested_by: Mapped[str] = mapped_column(String(50), nullable=False)  # Agent role that created it
    approved_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "owner" or null
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approval_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # Cryptographic token
    thread_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # LangGraph thread_id for resuming interrupt()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="approvals")
```

**Status transitions:** `pending` → `approved` (one-way, immutable) or `pending` → `rejected` (one-way, immutable). No other transitions allowed.

### 2.6 PIIToken

```python
# backend/app/models/pii_token.py
class PIIToken(Base):
    __tablename__ = "pii_token"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    hmac_token: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # e.g., HMAC_CUST_8821
    entity_category: Mapped[str] = mapped_column(String(30), nullable=False)  # PIICategory
    original_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of original value
    display_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # For client-side re-hydration only
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="pii_tokens")
```

---

## 3. Shared Response Patterns

### 3.1 Error Response

All errors return this shape. **Never** return stack traces or raw exception messages to the client.

```python
# Pydantic model for all error responses
class ErrorResponse(BaseModel):
    error: str          # Human-readable error message
    detail: str         # Technical detail (safe for client)
    code: str           # Machine-readable error code

# Error codes (exhaustive list):
# VALIDATION_ERROR     — Pydantic validation failed
# NOT_FOUND            — Resource not found
# PERMISSION_DENIED    — Tier violation (T0-T4)
# INJECTION_BLOCKED    — Injection guard triggered
# APPROVAL_REQUIRED    — T4 action requires human approval
# APPROVAL_INVALID     — Invalid approval token or already resolved
# INGESTION_FAILED     — File parsing or DB write failed
# ENGINE_ERROR         — Deterministic engine computation failed
# LLM_UNAVAILABLE      — LLM API unreachable (will auto-fallback to mock)
# INTERNAL_ERROR       — Unexpected server error
```

**HTTP status codes used:**

| Status | When |
|---|---|
| `200` | Success |
| `400` | Validation error, bad request body |
| `403` | Permission denied (tier violation) |
| `404` | Resource not found |
| `422` | Pydantic validation error (FastAPI default) |
| `500` | Internal server error |

### 3.2 Pagination

Used by: `GET /api/audit-trail/{cid}`, `GET /api/invoices/{cid}`

```python
class PaginationParams(BaseModel):
    offset: int = 0        # Skip N records
    limit: int = 50        # Return at most N records (max: 200)

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int
    has_more: bool
```

Query string format: `?offset=0&limit=50`

### 3.3 Company ID

All endpoints that are company-scoped use `{company_id}` as a path parameter (UUID string). In demo mode, there is typically one company created by the benchmark seeder.

---

## 4. API Endpoints

### 4.1 Dashboard

#### `GET /api/dashboard/{company_id}`

**Purpose:** Aggregate all dashboard data in a single call — metrics, mini forecast, alerts.
**Tier:** T0 (Read)

**Path params:**
| Param | Type | Description |
|---|---|---|
| `company_id` | `str` (UUID) | Target company |

**Response: `200 OK`**

```python
class MetricsData(BaseModel):
    liquid_cash: float
    pending_receivables: float
    overdue_receivables: float
    overdue_count: int
    monthly_net_burn: float
    cash_conversion_cycle: float | None   # DIO + DSO - DPO (null if insufficient data)
    dso: float | None                     # Days Sales Outstanding
    dpo: float | None                     # Days Payable Outstanding
    concentration_risk_pct: float | None  # Top debtor's share of AR (null if no AR)
    concentration_debtor: str | None      # Name of top debtor

class RunwayData(BaseModel):
    days_left: int
    shortfall_date: str | None           # ISO date "2026-11-04" or null
    shortfall_amount: float | None
    status: RunwayStatus                  # healthy, warning, critical

class ForecastChartData(BaseModel):
    weeks: list[str]                      # ["W1", "W2", ..., "W13"]
    dates: list[str]                      # ["2026-10-14", ...]
    p10_conservative: list[float]
    p50_median: list[float]
    p90_optimistic: list[float]
    safety_floor: float

class AlertData(BaseModel):
    id: str
    severity: AlertSeverity
    title: str
    description: str
    action_label: str
    action_type: str                      # "open_financing", "draft_reminder", "view_forecast"
    related_entity_id: str | None         # Invoice ID or scheme ID if applicable

class DashboardResponse(BaseModel):
    company: dict                          # { id, name, currency }
    runway: RunwayData
    metrics: MetricsData
    forecast_chart: ForecastChartData
    alerts: list[AlertData]
```

---

### 4.2 Forecast

#### `POST /api/forecast`

**Purpose:** Run full 13-week Monte Carlo forecast.
**Tier:** T1 (Analyze)

**Request body:**

```python
class ForecastRequest(BaseModel):
    company_id: str
    horizon_days: int = 90               # Default 13 weeks
    mc_runs: int = 1000                  # Monte Carlo paths
    seed: int | None = None              # For reproducibility (optional)
```

**Response: `200 OK`**

```python
class InvoiceDelayPrediction(BaseModel):
    invoice_id: str
    invoice_number: str
    debtor_name: str
    amount: float
    due_date: str
    p_delay: float                        # 0.0 to 1.0
    predicted_delay_days: int
    risk_level: RiskLevel
    historical_avg_delay: float | None

class ForecastResponse(BaseModel):
    company_id: str
    forecast_chart: ForecastChartData
    shortfall_date: str | None
    shortfall_amount: float | None
    runway_days: int
    confidence: float                     # Model confidence (0.0 to 1.0)
    invoice_risks: list[InvoiceDelayPrediction]
    computed_at: str                       # ISO timestamp
```

---

### 4.3 Scenario Simulation

#### `POST /api/scenario`

**Purpose:** Run what-if stress simulation on top of baseline forecast.
**Tier:** T1 (Analyze)

**Request body:**

```python
class ScenarioRequest(BaseModel):
    company_id: str
    debtor_delay_days: int = 0            # 0-90
    supplier_cost_delta_pct: float = 0.0  # 0.0-30.0 (percent)
    capex_spend: float = 0.0             # 0-50000
    apply_factoring_advance: bool = False
```

**Response: `200 OK`**

```python
class WeeklyComparison(BaseModel):
    week: str                             # "W1", "W2", etc.
    date: str
    baseline_cash: float
    simulated_cash: float
    projected_inflow: float
    projected_outflow: float

class ScenarioResponse(BaseModel):
    company_id: str
    baseline_shortfall_day: int | None    # Day number from today (null = no shortfall)
    scenario_shortfall_day: int | None
    delta_days: int                       # Positive = delayed, negative = accelerated
    weekly_simulation: list[WeeklyComparison]
    debtor_risks: list[InvoiceDelayPrediction]  # Re-uses forecast model
    factoring_advance_amount: float | None       # If toggle is on
    computed_at: str
```

---

### 4.4 Financing

#### `GET /api/financing/{company_id}`

**Purpose:** Evaluate all schemes + compute covenants.
**Tier:** T1 (Analyze)

**Response: `200 OK`**

```python
class CovenantStatus(BaseModel):
    name: str                             # "DSCR", "Quick Ratio", "Leverage", "Burn Rate"
    current_value: float
    required_value: float | None          # Threshold from most relevant failed scheme
    result: CovenantResult                # pass, fail, warning
    formula: str                          # "NOI / TDS" (for CFO mode)

class FailedRule(BaseModel):
    rule_name: str                        # "min_dscr"
    required: str                         # "≥ 1.25x"
    actual: str                           # "1.18x"
    gap: str                              # "0.07x below threshold"

class SchemeEvaluation(BaseModel):
    id: str
    name: str
    issuer: str
    rate_pct: float
    max_amount: float
    currency: str
    tenure_months: int
    eligible: bool
    match_score: int                      # 0-100
    effective_date: str                   # ISO date
    source_url: str
    is_stale: bool                        # True if > 180 days old
    status_tag: str                       # "[verify]" or "confirmed"
    failed_rules: list[FailedRule]        # Empty if eligible
    remediation_steps: list[str]          # Empty if eligible
    required_documents: list[str]

class FinancingResponse(BaseModel):
    company_id: str
    covenants: list[CovenantStatus]
    schemes: list[SchemeEvaluation]
    eligible_count: int
    ineligible_count: int
    computed_at: str
```

---

### 4.5 Invoices

#### `GET /api/invoices/{company_id}`

**Purpose:** Paginated invoice ledger with delay risk predictions.
**Tier:** T0 (Read)

**Query params:** `?offset=0&limit=50&status=overdue` (status filter is optional)

**Response: `200 OK`**

```python
class InvoiceData(BaseModel):
    id: str
    invoice_number: str
    debtor_name: str
    debtor_email: str | None
    amount: float
    currency: str
    issued_date: str
    due_date: str
    paid_date: str | None
    status: InvoiceStatus
    days_overdue: int                     # 0 if not overdue
    p_delay: float | None                # 0.0 to 1.0
    predicted_delay_days: int | None
    risk_level: RiskLevel | None

class InvoiceListResponse(BaseModel):
    items: list[InvoiceData]
    total: int
    offset: int
    limit: int
    has_more: bool
    aging_summary: dict                   # { "current": float, "1_30": float, "31_60": float, "60_plus": float }
    aging_counts: dict                    # { "current": int, "1_30": int, "31_60": int, "60_plus": int }
```

---

### 4.6 Draft Collection

#### `POST /api/draft-collection`

**Purpose:** Generate a collection email draft for an overdue invoice.
**Tier:** T2 (Draft) — creates content but **never** dispatches.

**Request body:**

```python
class DraftCollectionRequest(BaseModel):
    company_id: str
    invoice_id: str
    tone: CollectionTone                  # polite_nudge, standard_firm, formal_demand
    queue_for_approval: bool = True       # Creates a PENDING T4 Approval record in the approval table
```

**Response: `200 OK`**

```python
class DraftCollectionResponse(BaseModel):
    draft_id: str                         # UUID for tracking
    approval_id: str | None               # UUID of the queued PENDING Approval record (for POST /api/approve)
    invoice_id: str
    invoice_number: str
    recipient_email: str
    subject: str
    body: str                             # Full email text
    tone: CollectionTone
    tier: str                             # Always "T2"
    governance_note: str                  # "This draft requires T4 approval to send."
    created_at: str
```

---

### 4.7 Approvals

#### `GET /api/approvals/{company_id}`

**Purpose:** List pending (and optionally resolved) T4 approval requests.
**Tier:** T0 (Read)

**Query params:** `?status=pending` (optional, default returns all)

**Response: `200 OK`**

```python
class ApprovalData(BaseModel):
    id: str
    action_type: ApprovalActionType
    payload_summary: str                  # Human-readable summary
    payload: dict                         # Full JSON payload (draft email content, etc.)
    justification: str | None
    status: ApprovalStatus
    requested_by: str                     # Agent role
    approved_by: str | None
    rejection_reason: str | None
    created_at: str
    resolved_at: str | None

class PIITelemetryItem(BaseModel):
    hmac_token: str                       # e.g., "HMAC_CUST_8821"
    entity_category: PIICategory
    masked_preview: str                   # e.g., "Md. K*** U***" (safe for display)
    raw_sample_context: str               # e.g., "Payment from [REDACTED_PERSON_NAME]"
    sanitized_context: str                # e.g., "Payment from HMAC_CUST_8821"

class ApprovalListResponse(BaseModel):
    items: list[ApprovalData]
    pending_count: int
    approved_count: int
    rejected_count: int
    pii_telemetry: list[PIITelemetryItem] = []  # Populates PIIRedactionDiff on /governance
```

#### `POST /api/approve`

**Purpose:** Approve or reject a pending T4 action.
**Tier:** T4 (Execute gate)

**Request body:**

```python
class ApproveRequest(BaseModel):
    approval_id: str
    decision: str                         # "approved" or "rejected"
    reason: str | None = None             # Required if rejected, optional if approved
```

**Response: `200 OK`**

```python
class ApproveResponse(BaseModel):
    approval_id: str
    status: ApprovalStatus                # approved or rejected
    resolved_at: str
    audit_block: int                      # Block number of the audit entry created
    message: str                          # "Action approved and logged." or "Action rejected."
```

**Error: `400` if approval is already resolved (not pending).**
**Error: `404` if approval_id not found.**

---

### 4.8 Audit Trail

#### `GET /api/audit-trail/{company_id}`

**Purpose:** Paginated SHA-256 hash-chained audit log.
**Tier:** T0 (Read)

**Query params:** `?offset=0&limit=50`

**Response: `200 OK`**

```python
class AuditEntryData(BaseModel):
    id: str
    block_number: int
    timestamp: str
    agent_role: str
    tool_name: str
    input_hash: str                       # SHA-256 (truncated to first 8 chars in UI)
    output_hash: str
    permission_tier: str                  # "T0", "T1", etc.
    current_hash: str                     # H_n
    previous_hash: str                    # H_{n-1}
    verified: bool                        # True if H_n matches recomputed hash

class AuditTrailResponse(BaseModel):
    items: list[AuditEntryData]
    total: int
    offset: int
    limit: int
    has_more: bool
    chain_intact: bool                    # True if ALL entries verified in this page
```

---

### 4.9 Data Ingestion

#### `POST /api/seed-benchmark`

**Purpose:** Load a pre-built benchmark dataset (1-click judge mode).
**Tier:** T0

**Request body:**

```python
class SeedBenchmarkRequest(BaseModel):
    scenario: BenchmarkScenario           # "bengal_craft" or "shenzhen_importer"
```

**Response: `200 OK`**

```python
class SeedBenchmarkResponse(BaseModel):
    company_id: str
    company_name: str
    transactions_count: int
    invoices_count: int
    pii_entities_redacted: int
    date_range: dict                      # { "start": "2026-04-01", "end": "2026-10-12" }
    initial_cash_balance: float
    message: str                          # "Bengal Craft & Retail loaded successfully."
```

**Idempotency:** If data already exists, existing data is deleted first (clean re-seed).

#### `POST /api/ingest`

**Purpose:** Upload and process a user's CSV/PDF/image file.
**Tier:** T0

**Content-Type:** `multipart/form-data`

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | `UploadFile` | Yes | The CSV, XLSX, PDF, PNG, or JPG file |
| `company_name` | `str` | No | Defaults to filename stem |
| `currency` | `str` | No | Defaults to "BDT" |
| `commit` | `bool` | No | If false (default): preview only. If true: write to DB |

**Response (preview mode, `commit=false`): `200 OK`**

```python
class ColumnMapping(BaseModel):
    date_column: str | None
    amount_column: str | None
    description_column: str | None
    direction_column: str | None
    confidence: float                     # Auto-detection confidence 0.0-1.0

class PIIEntity(BaseModel):
    original_text: str
    hmac_token: str
    category: PIICategory
    row_index: int

class IngestionPreviewResponse(BaseModel):
    file_name: str
    file_type: str                        # "csv", "xlsx", "pdf", "image"
    total_rows: int
    sample_rows: list[dict]               # First 10 rows as dicts
    column_mapping: ColumnMapping
    pii_entities: list[PIIEntity]
    injection_flags: list[dict]           # Any blocked narrations { row, pattern }
```

**Response (commit mode, `commit=true`): `200 OK`**

```python
class IngestionCommitResponse(BaseModel):
    company_id: str
    transactions_count: int
    invoices_count: int
    pii_entities_redacted: int
    date_range: dict
    initial_cash_balance: float
    message: str
```

---

### 4.10 Chat (SSE Streaming)

#### `POST /api/chat`

**Purpose:** Send a natural-language message to the copilot agent system. Response is streamed via SSE.
**Tier:** T0–T3 (depends on what the agent does internally; T4 triggers `interrupt()`)

**Request body:**

```python
class ChatRequest(BaseModel):
    company_id: str
    message: str
    persona: Persona = Persona.OWNER      # owner or cfo
    thread_id: str | None = None          # For conversation continuity (optional)
```

**Response:** `200 OK`, Content-Type: `text/event-stream`

See [Section 5: SSE Streaming Contract](#5-sse-streaming-contract) for the full event schema.

---

### 4.11 Prepare Application (via Approval)

#### Behavior Note

There is no separate `/api/prepare-application` endpoint. The "Prepare Application" action on the Financing page works as follows:

1. Frontend calls `POST /api/chat` with message: `"Prepare financing application for scheme {scheme_id}"`
2. Agent processes via Treasurer → `compile_application_pack()` (T3)
3. Agent calls `request_execution_approval()` (T3) → creates an Approval record with `action_type: "financing_pack"`
4. SSE emits `approval_required` event
5. User navigates to Governance page to approve

This keeps the API surface minimal and routes all complex actions through the agent graph.

### 4.12 Verify Audit Chain

#### Behavior Note

Audit chain verification is computed **client-side** or as a property of the `GET /api/audit-trail` response (`chain_intact` field). The frontend can also verify by:

1. Fetching all audit entries via paginated `GET /api/audit-trail/{cid}`
2. For each entry: recompute `SHA-256(f"{previous_hash}|{timestamp}|{agent_role}|{tool_name}|{input_hash}|{output_hash}".encode("utf-8"))` (Note: the API always returns full 64-character hex strings for `input_hash` and `output_hash`; truncation to 8 characters happens strictly in the React UI layer).
3. Compare recomputed hash with `current_hash`
4. If any mismatch → mark that entry as tampered

No separate endpoint needed. The `verified` field on each `AuditEntryData` confirms server-side verification was done on read.

---

## 5. SSE Streaming Contract

The `POST /api/chat` endpoint returns an SSE event stream. Each event is a JSON object with a `type` discriminator.

### Event Types

```python
# These are the exact Pydantic models serialized as SSE data payloads

class ThoughtEvent(BaseModel):
    type: Literal["thought"] = "thought"
    agent: str                            # "risk_sentinel", "orchestrator", "quant_modeler", "treasurer"
    text: str                             # "Checking input for injection patterns..."
    timestamp: str

class ToolCallEvent(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    agent: str
    tool: str                             # "forecast_cash", "match_financing", etc.
    args: dict                            # Tool arguments (redacted if contains PII)
    timestamp: str

class ToolResultEvent(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    agent: str
    tool: str
    result: dict                          # Deterministic engine output
    duration_ms: int                      # How long the tool took
    timestamp: str

class SynthesisEvent(BaseModel):
    type: Literal["synthesis"] = "synthesis"
    text: str                             # Executive narrative
    citations: list[str]                  # ["forecast_engine", "covenant_engine"]
    action_chips: list[dict]              # [{ "label": "Prepare Factoring", "action": "..." }]
    timestamp: str

class ApprovalRequiredEvent(BaseModel):
    type: Literal["approval_required"] = "approval_required"
    approval_id: str
    action_type: ApprovalActionType
    summary: str                          # "Send collection email to Acme Corp"
    timestamp: str

class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    code: str                             # From ErrorResponse codes
    message: str
    timestamp: str

class DoneEvent(BaseModel):
    type: Literal["done"] = "done"
    thread_id: str                        # For conversation continuity
    timestamp: str
```

### SSE Wire Format

```
data: {"type":"thought","agent":"risk_sentinel","text":"Checking input...","timestamp":"2026-10-14T10:42:15Z"}

data: {"type":"thought","agent":"orchestrator","text":"Routing to Quant Modeler...","timestamp":"2026-10-14T10:42:15Z"}

data: {"type":"tool_call","agent":"quant_modeler","tool":"forecast_cash","args":{"company_id":"...","horizon_days":90},"timestamp":"2026-10-14T10:42:16Z"}

data: {"type":"tool_result","agent":"quant_modeler","tool":"forecast_cash","result":{"shortfall_date":"2026-11-04","runway_days":34},"duration_ms":1200,"timestamp":"2026-10-14T10:42:17Z"}

data: {"type":"synthesis","text":"You have 34 days of cash runway...","citations":["forecast_engine"],"action_chips":[{"label":"View Forecast","action":"navigate:/forecast"}],"timestamp":"2026-10-14T10:42:18Z"}

data: {"type":"done","thread_id":"abc123","timestamp":"2026-10-14T10:42:18Z"}

```

### Frontend Parsing

```typescript
// In useChat.ts hook
const eventSource = new EventSource('/api/chat', { ... });

type SSEEvent =
  | { type: "thought"; agent: string; text: string; timestamp: string }
  | { type: "tool_call"; agent: string; tool: string; args: Record<string, unknown>; timestamp: string }
  | { type: "tool_result"; agent: string; tool: string; result: Record<string, unknown>; duration_ms: number; timestamp: string }
  | { type: "synthesis"; text: string; citations: string[]; action_chips: { label: string; action: string }[]; timestamp: string }
  | { type: "approval_required"; approval_id: string; action_type: string; summary: string; timestamp: string }
  | { type: "error"; code: string; message: string; timestamp: string }
  | { type: "done"; thread_id: string; timestamp: string };
```

**Note:** SSE uses POST, not GET. Since the native `EventSource` API only supports GET, use `fetch()` with `ReadableStream` or a library like `@microsoft/fetch-event-source` for POST-based SSE.

---

## 6. Scheme Catalog JSON Schema

Scheme data lives in `backend/app/knowledge/schemes/*.json` — NOT in the database. This makes them version-controllable, auditable, and citable.

```python
# Pydantic model for scheme JSON files
class EligibilityRules(BaseModel):
    cib_clearance: bool = False           # Requires CIB report clearance
    min_dscr: float | None = None         # Minimum DSCR (e.g., 1.25)
    min_turnover_bdt: float | None = None # Minimum annual turnover in BDT
    min_operating_months: int | None = None  # Minimum months in operation
    max_leverage: float | None = None     # Maximum leverage ratio
    ownership_requirement: str | None = None  # e.g., "51% women-owned"
    required_documents: list[str] = []    # ["Trade License", "Bank Statement", ...]

class SchemeDefinition(BaseModel):
    id: str                               # Unique ID (e.g., "cmsme_working_capital_2026")
    name: str                             # Full scheme name
    issuer: str                           # "Bangladesh Bank", "Prime Bank", etc.
    effective_date: str                   # ISO date — when scheme became active
    expiry_date: str | None               # ISO date or null (ongoing)
    source_url: str                       # Citation URL
    retrieval_date: str                   # When we last fetched the data
    rate_cap_pct: float                   # Interest rate cap (APR)
    max_amount_bdt: float                 # Maximum loan amount in BDT
    tenure_months: int                    # Maximum loan tenure
    eligibility_rules: EligibilityRules
    status: str                           # "[verify]" or "confirmed"
```

### Available Schemes (MVP)

| File | Scheme | Issuer | Rate | Status |
|---|---|---|---|---|
| `cmsme_working_capital.json` | CMSME Working Capital Refinance Fund | Bangladesh Bank | 9.0% | [verify] |
| `women_entrepreneur.json` | Women Entrepreneur Refinance Facility | Bangladesh Bank | 5.0% | [verify] |
| `agro_processing.json` | Agro-Processing Credit Facility | BFID/JICA | 7.0% | [verify] |
| `invoice_factoring.json` | Invoice Factoring Advance | Commercial Bank | 2.5% fee | [verify] |
| `nano_credit.json` | Digital Nano Credit | MFS Provider | 12.0% | [verify] |

---

## 7. Cross-Reference: Endpoint → Flow → Component

| Endpoint | Method | Flow(s) | Frontend Component | Hook |
|---|---|---|---|---|
| `/api/dashboard/{cid}` | GET | F1.6, F3 | `DashboardPage` | `useDashboard(cid)` |
| `/api/forecast` | POST | F1.8, F4.1 | `ForecastPage` | `useForecast(cid)` |
| `/api/scenario` | POST | F4.4-F4.8 | `ForecastPage` | `useScenario()` |
| `/api/financing/{cid}` | GET | F5.1-F5.7 | `FinancingPage` | `useFinancing(cid)` |
| `/api/invoices/{cid}` | GET | F3.8, F6.1 | `OperationsPage` | `useInvoices(cid)` |
| `/api/draft-collection` | POST | F6.5-F6.8 | Collection Drawer | `useDraftCollection()` |
| `/api/approvals/{cid}` | GET | F8.1-F8.3 | `GovernancePage` | `useApprovals(cid)` |
| `/api/approve` | POST | F8.4-F8.5 | `ApprovalCard` | `useApprove()` |
| `/api/audit-trail/{cid}` | GET | F8.6-F8.7 | `AuditTrailTable` | `useAuditTrail(cid)` |
| `/api/seed-benchmark` | POST | F1.3-F1.5 | `BenchmarkSeeder` | `useSeedBenchmark()` |
| `/api/ingest` | POST | F2.2-F2.7 | `FileDropzone` + `IngestionPreview` | `useIngestion()` |
| `/api/chat` | POST (SSE) | F7 | `CopilotDrawer` | `useChat()` |

---

## Summary: Complete API Surface

| # | Endpoint | Method | Tier | Request Model | Response Model |
|---|---|---|---|---|---|
| 1 | `/api/dashboard/{cid}` | GET | T0 | — | `DashboardResponse` |
| 2 | `/api/forecast` | POST | T1 | `ForecastRequest` | `ForecastResponse` |
| 3 | `/api/scenario` | POST | T1 | `ScenarioRequest` | `ScenarioResponse` |
| 4 | `/api/financing/{cid}` | GET | T1 | — | `FinancingResponse` |
| 5 | `/api/invoices/{cid}` | GET | T0 | Pagination + filter | `InvoiceListResponse` |
| 6 | `/api/draft-collection` | POST | T2 | `DraftCollectionRequest` | `DraftCollectionResponse` |
| 7 | `/api/approvals/{cid}` | GET | T0 | Optional status filter | `ApprovalListResponse` |
| 8 | `/api/approve` | POST | T4 | `ApproveRequest` | `ApproveResponse` |
| 9 | `/api/audit-trail/{cid}` | GET | T0 | Pagination | `AuditTrailResponse` |
| 10 | `/api/seed-benchmark` | POST | T0 | `SeedBenchmarkRequest` | `SeedBenchmarkResponse` |
| 11 | `/api/ingest` | POST | T0 | multipart/form-data | `IngestionPreviewResponse` or `IngestionCommitResponse` |
| 12 | `/api/chat` | POST | T0-T3 | `ChatRequest` | SSE stream |

**Total: 12 endpoints. No hidden endpoints. No undocumented routes.**
