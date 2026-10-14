from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.dependencies import get_db
from app.models.company import Company
from app.models.approval import Approval
from app.models.audit_entry import AuditEntry
from app.models.pii_token import PIIToken
from app.models.enums import ApprovalStatus, ApprovalActionType, PIICategory
from app.models.schemas import (
    ApprovalListResponse,
    ApprovalData,
    PIITelemetryItem,
    ApproveRequest,
    ApproveResponse,
    AuditTrailResponse,
    AuditEntryData,
    ErrorResponse
)
from app.security.permission_service import PermissionService
from app.security.audit_logger import AuditLogger

router = APIRouter(tags=["Governance & Compliance"])

@router.get(
    "/approvals/{company_id}",
    response_model=ApprovalListResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def list_approvals(
    company_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Tier: T0 (Read)
    List pending and historical T4 approval requests with status tallies.
    """
    stmt_comp = select(Company).where(Company.id == company_id)
    company = (await db.execute(stmt_comp)).scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found."
        )

    query = select(Approval).where(Approval.company_id == company_id)
    if status_filter:
        query = query.where(Approval.status == status_filter)

    approvals = (await db.execute(query.order_by(desc(Approval.created_at)))).scalars().all()

    # Calculate status tallies
    all_query = select(Approval).where(Approval.company_id == company_id)
    all_apps = (await db.execute(all_query)).scalars().all()
    pending = sum(1 for a in all_apps if a.status == ApprovalStatus.PENDING.value)
    approved = sum(1 for a in all_apps if a.status == ApprovalStatus.APPROVED.value)
    rejected = sum(1 for a in all_apps if a.status == ApprovalStatus.REJECTED.value)

    items = []
    for a in approvals:
        summary_str = f"Execute {a.action_type.replace('_', ' ').title()}"
        if a.action_type == ApprovalActionType.COLLECTION_EMAIL.value:
            dest = a.payload.get("recipient_email", "Counterparty")
            summary_str = f"Dispatch collection notice to {dest}"
        elif a.action_type == ApprovalActionType.LOAN_APPLICATION.value:
            s_name = a.payload.get("scheme_name", "Refinance Facility")
            summary_str = f"Submit official loan dossier for {s_name}"

    # Query PII tokens to populate PIIRedactionDiff telemetry
    pii_query = select(PIIToken).where(PIIToken.company_id == company_id).limit(20)
    pii_records = (await db.execute(pii_query)).scalars().all()
    pii_telemetry = [
        PIITelemetryItem(
            hmac_token=p.hmac_token,
            entity_category=PIICategory(p.entity_category),
            masked_preview=p.display_value or "****",
            raw_sample_context=f"Raw customer/financial record for {p.entity_category}",
            sanitized_context=f"Sanitized to {p.hmac_token} before model egress"
        )
        for p in pii_records
    ]

    return ApprovalListResponse(
        items=items,
        pending_count=pending,
        approved_count=approved,
        rejected_count=rejected,
        pii_telemetry=pii_telemetry
    )

@router.post(
    "/approve",
    response_model=ApproveResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def approve_action(request: ApproveRequest, db: AsyncSession = Depends(get_db)):
    """
    Tier: T4 (Execute Gate)
    Sign off or reject a pending T4 action.
    Transitions status to approved or rejected (one-way immutable) and appends to SHA-256 hash chain.
    """
    stmt = select(Approval).where(Approval.id == request.approval_id)
    approval = (await db.execute(stmt)).scalar_one_or_none()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request '{request.approval_id}' not found."
        )

    if approval.status != ApprovalStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval request '{request.approval_id}' has already been resolved with status '{approval.status}'."
        )

    if request.decision not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be either 'approved' or 'rejected'."
        )

    now = datetime.utcnow()
    approval.status = request.decision
    approval.resolved_at = now
    approval.approved_by = "owner"

    if request.decision == "approved":
        # Generate cryptographic token
        approval.approval_token = PermissionService.generate_approval_token(approval.id, approval.company_id)
        msg = "Action approved and logged to immutable audit trail."
    else:
        approval.rejection_reason = request.reason or "Rejected by SME business owner."
        msg = "Action rejected and recorded in governance log."

    # Commit approval state
    await db.commit()

    # Append to cryptographic audit log
    audit_entry = await AuditLogger.log_action(
        session=db,
        company_id=approval.company_id,
        agent_role="owner",
        tool_name=f"human_decision_{request.decision}",
        input_payload={"approval_id": approval.id, "action_type": approval.action_type},
        output_payload={"decision": request.decision, "token": approval.approval_token},
        permission_tier="T4"
    )

    return ApproveResponse(
        approval_id=approval.id,
        status=ApprovalStatus(approval.status),
        resolved_at=now.isoformat(),
        audit_block=audit_entry.block_number,
        message=msg
    )

@router.get(
    "/audit-trail/{company_id}",
    response_model=AuditTrailResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_audit_trail(
    company_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Tier: T0 (Read)
    Paginated SHA-256 hash-chained audit log with cryptographic chain verification.
    """
    stmt_comp = select(Company).where(Company.id == company_id)
    company = (await db.execute(stmt_comp)).scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found."
        )

    # Total count
    count_stmt = select(func.count(AuditEntry.id)).where(AuditEntry.company_id == company_id)
    total_count = (await db.execute(count_stmt)).scalar() or 0

    # Fetch entries ordered by block_number ascending
    query = (
        select(AuditEntry)
        .where(AuditEntry.company_id == company_id)
        .order_by(AuditEntry.block_number.asc())
        .offset(offset)
        .limit(limit)
    )
    entries = (await db.execute(query)).scalars().all()

    entry_datas = []
    for e in entries:
        entry_datas.append(AuditEntryData(
            id=e.id,
            block_number=e.block_number,
            timestamp=e.timestamp.isoformat(),
            agent_role=e.agent_role,
            tool_name=e.tool_name,
            input_hash=e.input_hash,
            output_hash=e.output_hash,
            permission_tier=e.permission_tier,
            current_hash=e.current_hash,
            previous_hash=e.previous_hash,
            verified=True  # Will be validated below
        ))

    # Verify chain integrity across fetched items
    chain_intact = AuditLogger.verify_chain(entry_datas)
    # If any link in chain failed, reflect in verified flag
    if not chain_intact:
        for idx, ed in enumerate(entry_datas):
            prev = entry_datas[idx - 1] if idx > 0 else None
            ed.verified = AuditLogger.verify_entry(ed, prev)

    return AuditTrailResponse(
        items=entry_datas,
        total=total_count,
        offset=offset,
        limit=limit,
        has_more=(offset + limit) < total_count,
        chain_intact=chain_intact
    )
