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
    ISSUED = "issued"            # Created, not yet due
    OVERDUE = "overdue"          # Past due date, not paid
    PAID = "paid"                # Payment received
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
