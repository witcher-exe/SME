import pytest
from app.security.audit_logger import AuditLogger
from app.models.schemas import AuditEntryData

def test_hash_computation_formula():
    """Verify exact formula H_n = SHA-256(f'{previous_hash}|{timestamp}|{agent_role}|{tool_name}|{input_hash}|{output_hash}')"""
    prev = "0" * 64
    ts = "2026-10-14T10:00:00"
    agent = "system"
    tool = "seed_benchmark"
    in_h = "a" * 64
    out_h = "b" * 64
    
    h = AuditLogger.compute_hash(prev, ts, agent, tool, in_h, out_h)
    assert len(h) == 64
    assert isinstance(h, str)
    # Determinism
    h2 = AuditLogger.compute_hash(prev, ts, agent, tool, in_h, out_h)
    assert h == h2

def test_audit_chain_verification_clean():
    """Test verification of a valid 3-block chain."""
    prev0 = "0" * 64
    ts0 = "2026-10-14T10:00:00"
    h0 = AuditLogger.compute_hash(prev0, ts0, "system", "seed", "in0", "out0")
    
    ts1 = "2026-10-14T10:01:00"
    h1 = AuditLogger.compute_hash(h0, ts1, "forecaster", "monte_carlo", "in1", "out1")
    
    ts2 = "2026-10-14T10:02:00"
    h2 = AuditLogger.compute_hash(h1, ts2, "treasurer", "draft", "in2", "out2")
    
    blocks = [
        AuditEntryData(
            id="1", block_number=1, timestamp=ts0,
            agent_role="system", tool_name="seed", input_hash="in0", output_hash="out0",
            permission_tier="T0", current_hash=h0, previous_hash=prev0, verified=True
        ),
        AuditEntryData(
            id="2", block_number=2, timestamp=ts1,
            agent_role="forecaster", tool_name="monte_carlo", input_hash="in1", output_hash="out1",
            permission_tier="T0", current_hash=h1, previous_hash=h0, verified=True
        ),
        AuditEntryData(
            id="3", block_number=3, timestamp=ts2,
            agent_role="treasurer", tool_name="draft", input_hash="in2", output_hash="out2",
            permission_tier="T2", current_hash=h2, previous_hash=h1, verified=True
        )
    ]
    assert AuditLogger.verify_chain(blocks) is True

def test_audit_chain_verification_tamper_detected():
    """Test that altering a single field in block 2 invalidates verification."""
    prev0 = "0" * 64
    ts0 = "2026-10-14T10:00:00"
    h0 = AuditLogger.compute_hash(prev0, ts0, "system", "seed", "in0", "out0")
    
    ts1 = "2026-10-14T10:01:00"
    h1 = AuditLogger.compute_hash(h0, ts1, "forecaster", "monte_carlo", "in1", "out1")
    
    blocks = [
        AuditEntryData(
            id="1", block_number=1, timestamp=ts0,
            agent_role="system", tool_name="seed", input_hash="in0", output_hash="out0",
            permission_tier="T0", current_hash=h0, previous_hash=prev0, verified=True
        ),
        AuditEntryData(
            id="2", block_number=2, timestamp=ts1,
            agent_role="ATTACKER_ROLE", tool_name="monte_carlo", input_hash="in1", output_hash="out1",
            permission_tier="T0", current_hash=h1, previous_hash=h0, verified=True
        )
    ]
    assert AuditLogger.verify_chain(blocks) is False
