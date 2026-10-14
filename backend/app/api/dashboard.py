from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.company import Company
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.models.enums import RunwayStatus, InvoiceStatus, RiskLevel
from app.models.schemas import (
    DashboardResponse,
    CompanySummary,
    RunwayData,
    MetricsData,
    ForecastChartData,
    AlertData,
    InvoiceData,
    ErrorResponse
)
from app.engines.forecast_engine import ForecastEngine
from app.engines.ccc_engine import CCCEngine
from app.engines.alert_engine import AlertEngine

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get(
    "/health",
    tags=["System"]
)
async def health_check():
    """Service health check endpoint."""
    return {"status": "healthy", "service": "AuraCFO API"}

@router.get(
    "/{company_id}",
    response_model=DashboardResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_dashboard(company_id: str, db: AsyncSession = Depends(get_db)):
    """
    Tier: T0
    Aggregate dashboard endpoint returning liquid cash, burn, runway, 13-week forecast, and alerts.
    """
    # 1. Fetch Company
    stmt_comp = select(Company).where(Company.id == company_id)
    res_comp = await db.execute(stmt_comp)
    company = res_comp.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found."
        )

    # 2. Fetch Transactions & Invoices
    stmt_txns = select(Transaction).where(Transaction.company_id == company_id)
    txns = (await db.execute(stmt_txns)).scalars().all()

    stmt_invs = select(Invoice).where(Invoice.company_id == company_id)
    invs = (await db.execute(stmt_invs)).scalars().all()

    # 3. Compute Current Liquid Cash
    cash = company.initial_cash_balance
    total_inflows = 0.0
    total_outflows = 0.0
    inflow_amounts = []
    outflow_amounts = []

    for t in txns:
        if t.direction == "credit":
            cash += t.amount
            total_inflows += t.amount
            inflow_amounts.append(t.amount)
        else:
            cash -= t.amount
            total_outflows += t.amount
            outflow_amounts.append(t.amount)

    # Weekly aggregates for Monte Carlo
    num_weeks = max(1, len(txns) // 5)
    mean_inflow = (total_inflows / num_weeks) if num_weeks > 0 else 45000.0
    mean_outflow = (total_outflows / num_weeks) if num_weeks > 0 else 52000.0
    std_inflow = mean_inflow * 0.25
    std_outflow = mean_outflow * 0.20

    # 4. Receivables & Aging
    pending_ar = 0.0
    overdue_ar = 0.0
    overdue_count = 0
    debtor_ar_map = {}
    high_risk_invoices = []
    today = date.today()

    for inv in invs:
        if inv.status != InvoiceStatus.PAID.value:
            pending_ar += inv.amount
            debtor_ar_map[inv.debtor_name] = debtor_ar_map.get(inv.debtor_name, 0.0) + inv.amount

            is_overdue = inv.status == InvoiceStatus.OVERDUE.value or (inv.due_date < today)
            days_overdue = (today - inv.due_date).days if is_overdue else 0

            if is_overdue:
                overdue_ar += inv.amount
                overdue_count += 1

            inv_data = InvoiceData(
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
            )

            if inv.risk_level == RiskLevel.HIGH.value or (inv.p_delay and inv.p_delay >= 0.60):
                high_risk_invoices.append(inv_data)

    # 5. Debtor Concentration
    top_debtor = None
    concentration_pct = None
    if pending_ar > 0 and debtor_ar_map:
        sorted_debtors = sorted(debtor_ar_map.items(), key=lambda x: x[1], reverse=True)
        top_debtor, top_amt = sorted_debtors[0]
        concentration_pct = round((top_amt / pending_ar) * 100.0, 1)

    # 6. Monte Carlo Forecast & Runway
    has_delayed = any(
        inv.status != InvoiceStatus.PAID.value and ((inv.p_delay and inv.p_delay > 0.5) or inv.status == InvoiceStatus.OVERDUE.value)
        for inv in invs
    )
    delay_weeks = 2 if has_delayed else 0

    chart_data, shortfall_date, shortfall_amt, runway_days = ForecastEngine.run_monte_carlo(
        current_cash=cash,
        weekly_inflows_mean=mean_inflow,
        weekly_inflows_std=std_inflow,
        weekly_outflows_mean=mean_outflow,
        weekly_outflows_std=std_outflow,
        start_date=today,
        horizon_weeks=13,
        safety_floor=220000.0,
        debtor_delay_weeks=delay_weeks,
        seed=42
    )

    if runway_days > 60:
        runway_status = RunwayStatus.HEALTHY
    elif runway_days >= 30:
        runway_status = RunwayStatus.WARNING
    else:
        runway_status = RunwayStatus.CRITICAL

    # 7. Working Capital & CCC
    monthly_net_burn = round((mean_outflow - mean_inflow) * 4.33, 2)
    ccc_dict = CCCEngine.calculate(
        total_open_receivables=pending_ar,
        annual_credit_sales=max(total_inflows * 2.0, 100000.0),
        total_open_payables=180000.0,
        annual_cogs=max(total_outflows * 1.5, 100000.0)
    )

    # 8. Alert Generation
    alerts = AlertEngine.generate_alerts(
        shortfall_date=shortfall_date,
        shortfall_amount=shortfall_amt,
        runway_days=runway_days,
        high_risk_invoices=high_risk_invoices,
        concentration_debtor=top_debtor,
        concentration_pct=concentration_pct
    )

    return DashboardResponse(
        company=CompanySummary(
            id=company.id,
            name=company.name,
            currency=company.currency
        ),
        runway=RunwayData(
            days_left=runway_days,
            shortfall_date=shortfall_date,
            shortfall_amount=shortfall_amt,
            status=runway_status
        ),
        metrics=MetricsData(
            liquid_cash=round(cash, 2),
            pending_receivables=round(pending_ar, 2),
            overdue_receivables=round(overdue_ar, 2),
            overdue_count=overdue_count,
            monthly_net_burn=monthly_net_burn,
            cash_conversion_cycle=ccc_dict["cash_conversion_cycle"],
            dso=ccc_dict["dso"],
            dpo=ccc_dict["dpo"],
            concentration_risk_pct=concentration_pct,
            concentration_debtor=top_debtor,
            # Frontend compatibility aliases:
            open_ar=round(pending_ar, 2),
            overdue_ar=round(overdue_ar, 2),
            cash_conversion_cycle_days=ccc_dict["cash_conversion_cycle"],
            days_sales_outstanding=ccc_dict["dso"],
            days_payable_outstanding=ccc_dict["dpo"],
            concentration_pct=concentration_pct,
            top_debtor=top_debtor
        ),
        forecast_chart=chart_data,
        alerts=alerts,
        high_risk_invoices=high_risk_invoices
    )
