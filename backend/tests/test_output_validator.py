import pytest
from app.security.output_validator import OutputValidator

def test_output_validator_whitelisted_horizons_pass():
    """Whitelisted ordinals and horizon numbers (13, 30, 60, 90, 2026) must not be flagged."""
    tool_data = {"liquid_cash": 450000.0, "runway_days": 21.0}
    text = "Based on our 13-week forecast for 2026, Step 1 shows liquid cash is 450,000 BDT with 21 days of runway."
    
    is_valid, ungrounded = OutputValidator.validate_narrative(text, tool_data)
    assert is_valid is True
    assert len(ungrounded) == 0

def test_output_validator_hallucinated_figures_flagged():
    """Unanchored financial numbers must be detected as hallucinations."""
    tool_data = {"liquid_cash": 450000.0, "runway_days": 21.0}
    text = "We have 999,999 BDT in cash reserves and a surplus of 750,000 BDT."
    
    is_valid, ungrounded = OutputValidator.validate_narrative(text, tool_data)
    assert is_valid is False
    assert any(u == 999999.0 for u in ungrounded)
