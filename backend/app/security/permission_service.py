"""
Permission Service: T0-T4 Autonomy Boundary Enforcement
Enforces tool execution tiers and air-gapped T4 Human-in-the-Loop signatures.
"""
from functools import wraps
from typing import Callable, Any, Optional
import hmac
import hashlib
from app.models.enums import Tier
from app.config import settings

class PermissionDenied(Exception):
    """Raised when an agent or session violates the T0-T4 permission matrix."""
    pass

TOOL_TIER_MAP = {
    "get_cash_position": Tier.T0_READ,
    "get_invoice_ledger": Tier.T0_READ,
    "get_audit_trail": Tier.T0_READ,
    "forecast_cash": Tier.T1_ANALYZE,
    "simulate_scenario": Tier.T1_ANALYZE,
    "match_financing": Tier.T1_ANALYZE,
    "compute_covenants": Tier.T1_ANALYZE,
    "draft_collection_notice": Tier.T2_DRAFT,
    "compile_application_pack": Tier.T3_PREPARE,
    "request_execution_approval": Tier.T3_PREPARE,
    "send_collection_email": Tier.T4_EXECUTE,
    "submit_loan_application": Tier.T4_EXECUTE,
}

class PermissionService:
    """Manages autonomy tier verification and cryptographic approval tokens."""

    @classmethod
    def generate_approval_token(cls, approval_id: str, company_id: str) -> str:
        """Generates a cryptographic approval token for an authorized human action."""
        msg = f"{approval_id}:{company_id}:approved"
        return hmac.new(
            settings.HMAC_SECRET_KEY.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    @classmethod
    def verify_approval_token(cls, approval_id: str, company_id: str, token: Optional[str]) -> bool:
        """Verifies whether the presented approval token matches the expected cryptographic signature."""
        if not token:
            return False
        expected = cls.generate_approval_token(approval_id, company_id)
        return hmac.compare_digest(expected, token)

    @classmethod
    def enforce_tier(
        cls,
        tool_name: str,
        current_session_tier: Tier,
        approval_token: Optional[str] = None,
        approval_id: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> None:
        """Validates tier and raises PermissionDenied if unauthorized."""
        required_tier = TOOL_TIER_MAP.get(tool_name, Tier.T4_EXECUTE)

        if current_session_tier < required_tier:
            raise PermissionDenied(
                f"Tool '{tool_name}' requires Tier {required_tier.name} ({required_tier.value}). "
                f"Current session is Tier {current_session_tier.name} ({current_session_tier.value})."
            )

        if required_tier == Tier.T4_EXECUTE:
            if not approval_token or not approval_id or not company_id:
                raise PermissionDenied(
                    f"Tier 4 tool '{tool_name}' requires valid Human-in-the-Loop signature token."
                )
            if not cls.verify_approval_token(approval_id, company_id, approval_token):
                raise PermissionDenied(
                    f"Invalid cryptographic signature for Tier 4 action on tool '{tool_name}'."
                )

def requires_tier(min_tier: Tier):
    """Function decorator for enforcing permission tiers on tool handlers."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            session_tier = kwargs.get("current_tier", Tier.T1_ANALYZE)
            if session_tier < min_tier:
                raise PermissionDenied(
                    f"Action '{func.__name__}' requires {min_tier.name}. Session tier: {session_tier.name}"
                )
            if min_tier == Tier.T4_EXECUTE:
                token = kwargs.get("approval_token")
                app_id = kwargs.get("approval_id")
                comp_id = kwargs.get("company_id")
                if not token or not PermissionService.verify_approval_token(app_id or "", comp_id or "", token):
                    raise PermissionDenied(
                        f"Execution of '{func.__name__}' requires explicit human cryptographic sign-off."
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
