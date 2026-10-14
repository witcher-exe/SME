import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_entry import AuditEntry
from app.models.schemas import AuditEntryData

class AuditLogger:
    """Manages SHA-256 hash-chained append-only audit trail."""

    @classmethod
    def compute_hash(
        cls,
        previous_hash: str,
        timestamp_iso: str,
        agent_role: str,
        tool_name: str,
        input_hash: str,
        output_hash: str
    ) -> str:
        """H_n = SHA-256(f"{previous_hash}|{timestamp_iso}|{agent_role}|{tool_name}|{input_hash}|{output_hash}".encode("utf-8"))"""
        raw = f"{previous_hash}|{timestamp_iso}|{agent_role}|{tool_name}|{input_hash}|{output_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    async def log_action(
        cls,
        session: AsyncSession,
        company_id: str,
        agent_role: str,
        tool_name: str,
        input_payload: Dict[str, Any],
        output_payload: Dict[str, Any],
        permission_tier: str
    ) -> AuditEntry:
        # 1. Fetch latest entry for this company to get H_{n-1}
        stmt = (
            select(AuditEntry)
            .where(AuditEntry.company_id == company_id)
            .order_by(desc(AuditEntry.block_number))
            .limit(1)
        )
        res = await session.execute(stmt)
        latest_entry = res.scalar_one_or_none()

        if latest_entry is None:
            block_number = 1
            previous_hash = "0" * 64
        else:
            block_number = latest_entry.block_number + 1
            previous_hash = latest_entry.current_hash

        ts = datetime.utcnow()
        ts_iso = ts.isoformat()

        # Compute payload hashes
        in_str = json.dumps(input_payload, sort_keys=True, default=str)
        out_str = json.dumps(output_payload, sort_keys=True, default=str)
        in_hash = hashlib.sha256(in_str.encode("utf-8")).hexdigest()
        out_hash = hashlib.sha256(out_str.encode("utf-8")).hexdigest()

        current_hash = cls.compute_hash(previous_hash, ts_iso, agent_role, tool_name, in_hash, out_hash)

        entry = AuditEntry(
            id=str(uuid.uuid4()),
            company_id=company_id,
            block_number=block_number,
            timestamp=ts,
            agent_role=agent_role,
            tool_name=tool_name,
            input_hash=in_hash,
            output_hash=out_hash,
            permission_tier=permission_tier,
            current_hash=current_hash,
            previous_hash=previous_hash
        )
        session.add(entry)
        await session.commit()
        return entry

    @classmethod
    def verify_entry(cls, entry: AuditEntryData, previous_entry: Optional[AuditEntryData]) -> bool:
        """Verifies integrity of a single audit entry against its previous link and formula."""
        if previous_entry is None:
            # Genesis block must have 64 zeros as previous hash
            if entry.previous_hash != ("0" * 64):
                return False
        else:
            if entry.previous_hash != previous_entry.current_hash:
                return False

        recomputed = cls.compute_hash(
            entry.previous_hash,
            entry.timestamp,
            entry.agent_role,
            entry.tool_name,
            entry.input_hash,
            entry.output_hash
        )
        return recomputed == entry.current_hash

    @classmethod
    def verify_chain(cls, entries: List[AuditEntryData]) -> bool:
        """Verifies an entire sequence of audit entries."""
        if not entries:
            return True

        # Ensure entries are sorted by block_number ascending
        sorted_entries = sorted(entries, key=lambda x: x.block_number)

        for i, entry in enumerate(sorted_entries):
            prev = sorted_entries[i - 1] if i > 0 else None
            if not cls.verify_entry(entry, prev):
                return False

        return True
