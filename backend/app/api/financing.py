from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.company import Company
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.models.enums import InvoiceStatus
from app.models.schemas import FinancingResponse, CovenantStatus, SchemeEvaluation, ErrorResponse
from app.engines.covenant_engine import CovenantEngine
from app.engines.matching_engine import MatchingEngine

router = APIRouter(prefix="/financing", tags=["Financing"])

@router.get(
    "/{company_id}",
    response_model=FinancingResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_financing_options(company_id: str, db: AsyncSession = Depends(get_db)):
    """
    Tier: T1 (Analyze)
    Evaluate eligibility against all dated financing schemes and compute covenant compliance.
    """
    stmt_comp = select(Company).where(Company.id == company_id)
    company = (await db.execute(stmt_comp)).scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found."
        )

    # Calculate financial position
    stmt_txns = select(Transaction).where(Transaction.company_id == company_id)
    txns = (await db.execute(stmt_txns)).scalars().all()

    cash = company.initial_cash_balance
    bs = company.balance_sheet_snapshot or {}
    debt_service_monthly = bs.get("monthly_debt_service_bdt", 45000.0)
    current_liabilities = bs.get("current_liabilities_bdt", 320000.0)
    total_debt = bs.get("total_debt_bdt", 450000.0)
    equity = bs.get("total_equity_bdt", 280000.0)

    total_rev = 0.0
    total_opex = 0.0
    for t in txns:
        if t.direction == "credit":
            cash += t.amount
            total_rev += t.amount
        else:
            cash -= t.amount
            if t.category != "loan_emi":
                total_opex += t.amount

    # Invoices (AR)
    stmt_invs = select(Invoice).where(
        Invoice.company_id == company_id,
        Invoice.status != InvoiceStatus.PAID.value
    )
    open_invs = (await db.execute(stmt_invs)).scalars().all()
    open_ar = sum(i.amount for i in open_invs)

    # Financial Metrics
    months = 6.0
    monthly_rev = total_rev / months
    monthly_opex = total_opex / months
    monthly_noi = monthly_rev - monthly_opex  # ~53,100 BDT for Bengal Craft
    annual_turnover = total_rev * 2.0         # annualized

    # Compute covenants
    covenant_dicts = CovenantEngine.evaluate_covenants(
        liquid_cash=cash,
        accounts_receivable=open_ar,
        current_liabilities=current_liabilities,
        monthly_noi=monthly_noi,
        monthly_debt_service=debt_service_monthly,
        total_debt=total_debt,
        equity=equity
    )

    covenants = [CovenantStatus(**cd) for cd in covenant_dicts]

    # Derived DSCR and Leverage for Scheme Matching
    dscr = round(monthly_noi / debt_service_monthly, 2) if debt_service_monthly > 0 else 2.5
    leverage = round(total_debt / equity, 2) if equity > 0 else 1.0

    # Evaluate schemes
    evaluations = MatchingEngine.evaluate(
        dscr=dscr,
        annual_turnover_bdt=annual_turnover,
        operating_months=24,
        leverage=leverage,
        cib_clearance=True,
        is_women_owned=False,
        industry=company.industry or "Retail"
    )

    eligible_count = sum(1 for s in evaluations if s.eligible)
    ineligible_count = len(evaluations) - eligible_count

    return FinancingResponse(
        company_id=company_id,
        covenants=covenants,
        schemes=evaluations,
        eligible_count=eligible_count,
        ineligible_count=ineligible_count,
        computed_at=datetime.utcnow().isoformat()
    )
