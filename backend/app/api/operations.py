import uuid
from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies import get_db
from app.models.company import Company
from app.models.invoice import Invoice
from app.models.approval import Approval
from app.models.enums import InvoiceStatus, RiskLevel, CollectionTone, ApprovalActionType
from app.models.schemas import (
    InvoiceListResponse,
    InvoiceData,
    DraftCollectionRequest,
    DraftCollectionResponse,
    ErrorResponse
)

router = APIRouter(tags=["Operations"])

@router.get(
    "/invoices/{company_id}",
    response_model=InvoiceListResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def list_invoices(
    company_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Tier: T0 (Read)
    Paginated invoice ledger with delay risk metrics and aging bucket distribution.
    """
    stmt_comp = select(Company).where(Company.id == company_id)
    company = (await db.execute(stmt_comp)).scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found."
        )

    # Base query
    query = select(Invoice).where(Invoice.company_id == company_id)
    if status_filter:
        query = query.where(Invoice.status == status_filter)

    # Total count
    count_stmt = select(func.count(Invoice.id)).where(Invoice.company_id == company_id)
    if status_filter:
        count_stmt = count_stmt.where(Invoice.status == status_filter)
    total_count = (await db.execute(count_stmt)).scalar() or 0

    # Paginated items
    paged_query = query.order_by(Invoice.due_date.asc()).offset(offset).limit(limit)
    invoices = (await db.execute(paged_query)).scalars().all()

    today = date.today()
    items = []
    aging_summary = {"current": 0.0, "1_30": 0.0, "31_60": 0.0, "60_plus": 0.0}
    aging_counts = {"current": 0, "1_30": 0, "31_60": 0, "60_plus": 0}

    for inv in invoices:
        is_overdue = (inv.due_date < today) and (inv.status != InvoiceStatus.PAID.value)
        days_overdue = (today - inv.due_date).days if is_overdue else 0

        # Aging buckets
        if inv.status != InvoiceStatus.PAID.value:
            if days_overdue == 0:
                aging_summary["current"] += inv.amount
                aging_counts["current"] += 1
            elif days_overdue <= 30:
                aging_summary["1_30"] += inv.amount
                aging_counts["1_30"] += 1
            elif days_overdue <= 60:
                aging_summary["31_60"] += inv.amount
                aging_counts["31_60"] += 1
            else:
                aging_summary["60_plus"] += inv.amount
                aging_counts["60_plus"] += 1

        items.append(InvoiceData(
            id=inv.id,
            invoice_number=inv.invoice_number,
            debtor_name=inv.debtor_name,
            debtor_email=inv.debtor_email,
            amount=inv.amount,
            currency=company.currency,
            issued_date=inv.issued_date.isoformat(),
            due_date=inv.due_date.isoformat(),
            paid_date=inv.paid_date.isoformat() if inv.paid_date else None,
            status=InvoiceStatus(inv.status),
            days_overdue=max(0, days_overdue),
            p_delay=inv.p_delay,
            predicted_delay_days=inv.predicted_delay_days,
            risk_level=RiskLevel(inv.risk_level) if inv.risk_level else None
        ))

    return InvoiceListResponse(
        items=items,
        total=total_count,
        offset=offset,
        limit=limit,
        has_more=(offset + limit) < total_count,
        aging_summary={k: round(v, 2) for k, v in aging_summary.items()},
        aging_counts=aging_counts
    )

@router.post(
    "/draft-collection",
    response_model=DraftCollectionResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def draft_collection(request: DraftCollectionRequest, db: AsyncSession = Depends(get_db)):
    """
    Tier: T2 (Draft)
    Generates a personalized payment reminder / collection notice draft.
    STRICTLY NON-DISPATCHING — requires explicit T4 approval to send.
    """
    stmt = select(Invoice).where(
        Invoice.id == request.invoice_id,
        Invoice.company_id == request.company_id
    )
    inv = (await db.execute(stmt)).scalar_one_or_none()
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice '{request.invoice_id}' not found."
        )

    debtor_name_clean = inv.debtor_name.split("(")[0].strip()
    recipient = inv.debtor_email or "accounts@counterparty.com"

    if request.tone == CollectionTone.POLITE_NUDGE:
        subject = f"Friendly Reminder: Invoice {inv.invoice_number} due {inv.due_date}"
        body = (
            f"Dear {debtor_name_clean} Accounts Team,\n\n"
            f"We hope this note finds you well. This is a gentle reminder that invoice {inv.invoice_number} "
            f"for BDT {inv.amount:,.2f} is scheduled for settlement on {inv.due_date}.\n\n"
            f"Kindly confirm receipt and expected processing schedule. Thank you for your continued partnership.\n\n"
            f"Warm regards,\nFinance & Accounts Department"
        )
    elif request.tone == CollectionTone.STANDARD_FIRM:
        subject = f"Payment Notice: Outstanding Invoice {inv.invoice_number} [BDT {inv.amount:,.2f}]"
        body = (
            f"Dear {debtor_name_clean} Accounts Payable,\n\n"
            f"Our records indicate that invoice {inv.invoice_number} in the amount of BDT {inv.amount:,.2f} "
            f"was due on {inv.due_date} and remains pending settlement.\n\n"
            f"To maintain credit standing and uninterrupted commercial supply, please remit funds via electronic transfer "
            f"within 3 business days.\n\n"
            f"Sincerely,\nAuraCFO Treasury Operations"
        )
    else:  # FORMAL_DEMAND
        subject = f"FORMAL DEMAND: Overdue Settlement for Invoice {inv.invoice_number}"
        body = (
            f"ATTENTION: HEAD OF FINANCE / PROCUREMENT — {debtor_name_clean}\n\n"
            f"Re: Overdue Commercial Invoice {inv.invoice_number}\n\n"
            f"Despite previous notifications, the principal sum of BDT {inv.amount:,.2f} due on {inv.due_date} "
            f"remains delinquent. Please be advised that failure to settle within 48 hours will result in automatic escalation "
            f"to legal collections and notification of Credit Information Bureau (CIB) records.\n\n"
            f"Payment must be credited immediately to our designated corporate treasury account.\n\n"
            f"Legal & Recovery Division"
        )

    draft_id = str(uuid.uuid4())
    approval_id = None

    if request.queue_for_approval:
        approval = Approval(
            id=str(uuid.uuid4()),
            company_id=request.company_id,
            action_type=ApprovalActionType.COLLECTION_EMAIL.value,
            payload={
                "draft_id": draft_id,
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "recipient_email": recipient,
                "subject": subject,
                "body": body,
                "tone": request.tone.value if hasattr(request.tone, "value") else str(request.tone)
            },
            justification=f"Automated collection draft for overdue invoice {inv.invoice_number} ({inv.amount:,.2f} BDT).",
            status="pending",
            requested_by="treasurer",
            created_at=datetime.utcnow()
        )
        db.add(approval)
        await db.commit()
        approval_id = approval.id

    return DraftCollectionResponse(
        draft_id=draft_id,
        approval_id=approval_id,
        invoice_id=inv.id,
        invoice_number=inv.invoice_number,
        recipient_email=recipient,
        subject=subject,
        body=body,
        tone=request.tone,
        tier="T2",
        governance_note="This draft is generated under Tier 2 (Draft). It requires Tier 4 human approval to send.",
        created_at=datetime.utcnow().isoformat()
    )
