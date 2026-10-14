import pytest
from app.security.permission_service import PermissionService, PermissionDenied
from app.models.enums import Tier

def test_tier_hierarchies():
    """Verify tier numerical and strict permission levels."""
    assert Tier.T0_READ < Tier.T1_ANALYZE < Tier.T2_DRAFT < Tier.T3_PREPARE < Tier.T4_EXECUTE

def test_token_generation_and_validation():
    approval_id = "test-action-12345"
    company_id = "bengal-craft-001"
    
    token = PermissionService.generate_approval_token(approval_id, company_id)
    assert len(token) == 64
    
    # Valid token passes
    assert PermissionService.verify_approval_token(approval_id, company_id, token) is True
    
    # Tampered token fails
    bad_token = token[:-4] + "ffff"
    assert PermissionService.verify_approval_token(approval_id, company_id, bad_token) is False
    
    # Wrong approval or company fails
    assert PermissionService.verify_approval_token("wrong-id", company_id, token) is False
    assert PermissionService.verify_approval_token(approval_id, "wrong-company", token) is False

def test_enforce_tier_blocks_unauthorized_execution():
    # T0 session cannot run T4 tool without token
    with pytest.raises(PermissionDenied):
        PermissionService.enforce_tier("send_collection_email", Tier.T0_READ)
    
    # T4 session with valid token passes
    app_id = "app-001"
    comp_id = "comp-001"
    token = PermissionService.generate_approval_token(app_id, comp_id)
    PermissionService.enforce_tier(
        "send_collection_email",
        Tier.T4_EXECUTE,
        approval_token=token,
        approval_id=app_id,
        company_id=comp_id
    )
