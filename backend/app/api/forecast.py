from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.company import Company
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.models.enums import RiskLevel, InvoiceStatus
from app.models.schemas import (
    ForecastRequest,
    ForecastResponse,
    ScenarioRequest,
    ScenarioResponse,
    InvoiceDelayPrediction,
    ErrorResponse
)
from app.engines.forecast_engine import ForecastEngine
from app.engines.scenario_engine import ScenarioEngine

router = APIRouter(tags=["Forecasting"])

@router.post(
    "/forecast",
    response_model=ForecastResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_forecast(request: ForecastRequest, db: AsyncSession = Depends(get_db)):
    """
    Tier: T1 (Analyze)
    Run 13-week Monte Carlo forecast with P10/P50/P90 corridors and per-invoice delay risk.
    """
    stmt_comp = select(Company).where(Company.id == request.company_id)
    company = (await db.execute(stmt_comp)).scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{request.company_id}' not found."
        )

    # Calculate current cash and distribution params from transactions
    stmt_txns = select(Transaction).where(Transaction.company_id == request.company_id)
    txns = (await db.execute(stmt_txns)).scalars().all()

    cash = company.initial_cash_balance
    total_in = 0.0
    total_out = 0.0
    for t in txns:
        if t.direction == "credit":
            cash += t.amount
            total_in += t.amount
        else:
            cash -= t.amount
            total_out += t.amount

    weeks_count = max(1, len(txns) // 5)
    in_mean = total_in / weeks_count if weeks_count > 0 else 45000.0
    out_mean = total_out / weeks_count if weeks_count > 0 else 52000.0

    # Invoices delay predictions
    stmt_invs = select(Invoice).where(Invoice.company_id == request.company_id)
    invs = (await db.execute(stmt_invs)).scalars().all()
    today = date.today()

    has_delayed_invoices = any(
        inv.status != InvoiceStatus.PAID.value and ((inv.p_delay and inv.p_delay > 0.5) or inv.status == InvoiceStatus.OVERDUE.value)
        for inv in invs
    )
    delay_weeks = 2 if has_delayed_invoices else 0

    chart, sf_date, sf_amt, runway = ForecastEngine.run_monte_carlo(
        current_cash=cash,
        weekly_inflows_mean=in_mean,
        weekly_inflows_std=in_mean * 0.25,
        weekly_outflows_mean=out_mean,
        weekly_outflows_std=out_mean * 0.20,
        horizon_weeks=request.horizon_days // 7,
        mc_runs=request.mc_runs,
        safety_floor=220000.0,
        debtor_delay_weeks=delay_weeks,
        seed=request.seed or 42
    )

    invoice_risks = []
    for inv in invs:
        if inv.status != InvoiceStatus.PAID.value:
            days_to_due = (inv.due_date - today).days
            p_delay, exp_delay, r_lvl = ForecastEngine.predict_invoice_delay(
                amount=inv.amount,
                days_to_due=days_to_due,
                historical_avg_delay=inv.predicted_delay_days or 14.0
            )
            invoice_risks.append(InvoiceDelayPrediction(
                invoice_id=inv.id,
                invoice_number=inv.invoice_number,
                debtor_name=inv.debtor_name,
                amount=inv.amount,
                due_date=inv.due_date.isoformat(),
                p_delay=p_delay,
                predicted_delay_days=exp_delay,
                risk_level=r_lvl,
                historical_avg_delay=float(exp_delay)
            ))

    return ForecastResponse(
        company_id=request.company_id,
        forecast_chart=chart,
        shortfall_date=sf_date,
        shortfall_amount=sf_amt,
        runway_days=runway,
        confidence=0.88,
        invoice_risks=invoice_risks,
        computed_at=datetime.utcnow().isoformat()
    )

@router.post(
    "/scenario",
    response_model=ScenarioResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def run_scenario(request: ScenarioRequest, db: AsyncSession = Depends(get_db)):
    """
    Tier: T1 (Analyze)
    Run what-if stress simulation (debtor delay, supplier cost inflation, capex, invoice factoring).
    """
    stmt_comp = select(Company).where(Company.id == request.company_id)
    company = (await db.execute(stmt_comp)).scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{request.company_id}' not found."
        )

    stmt_txns = select(Transaction).where(Transaction.company_id == request.company_id)
    txns = (await db.execute(stmt_txns)).scalars().all()

    cash = company.initial_cash_balance
    total_in = 0.0
    total_out = 0.0
    for t in txns:
        if t.direction == "credit":
            cash += t.amount
            total_in += t.amount
        else:
            cash -= t.amount
            total_out += t.amount

    weeks_count = max(1, len(txns) // 5)
    in_mean = total_in / weeks_count if weeks_count > 0 else 45000.0
    out_mean = total_out / weeks_count if weeks_count > 0 else 52000.0

    # Total open receivables for factoring advance calculation
    stmt_invs = select(Invoice).where(
        Invoice.company_id == request.company_id,
        Invoice.status != InvoiceStatus.PAID.value
    )
    open_invs = (await db.execute(stmt_invs)).scalars().all()
    open_ar_total = sum(i.amount for i in open_invs)

    scenario_res = ScenarioEngine.run_simulation(
        company_id=request.company_id,
        current_cash=cash,
        weekly_inflows_mean=in_mean,
        weekly_inflows_std=in_mean * 0.25,
        weekly_outflows_mean=out_mean,
        weekly_outflows_std=out_mean * 0.20,
        debtor_delay_days=request.debtor_delay_days,
        supplier_cost_delta_pct=request.supplier_cost_delta_pct,
        capex_spend=request.capex_spend,
        apply_factoring_advance=request.apply_factoring_advance,
        eligible_receivables_total=open_ar_total,
        start_date=date.today(),
        seed=42
    )

    return scenario_res
