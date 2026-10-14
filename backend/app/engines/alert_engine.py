"""
Lead-Time-Aware Alert Generation Engine
Deterministic threshold evaluation combining liquidity deficit and invoice delay odds.
NO LLM IMPORTS ALLOWED (TRD DE-01).
"""
import uuid
from typing import List, Optional
from app.models.enums import AlertSeverity
from app.models.schemas import AlertData, InvoiceData

class AlertEngine:
    """Generates severity-ranked alerts with actionable follow-ups."""

    @classmethod
    def generate_alerts(
        cls,
        shortfall_date: Optional[str],
        shortfall_amount: Optional[float],
        runway_days: int,
        high_risk_invoices: List[InvoiceData],
        concentration_debtor: Optional[str] = None,
        concentration_pct: Optional[float] = None
    ) -> List[AlertData]:
        alerts: List[AlertData] = []

        # 1. Critical Liquidity Alert
        if shortfall_date and runway_days <= 35:
            severity = AlertSeverity.CRITICAL if runway_days <= 21 else AlertSeverity.WARNING
            amt_str = f"{shortfall_amount:,.0f} BDT" if shortfall_amount else "Deficit"
            alerts.append(AlertData(
                id=f"alt-liquidity-{str(uuid.uuid4())[:8]}",
                severity=severity,
                title=f"{shortfall_date} Cash Shortfall",
                description=f"{amt_str} projected deficit under conservative P10 corridor. Cash buffer depletes in {runway_days} days.",
                action_label="View Forecast Detail",
                action_type="view_forecast",
                related_entity_id=None
            ))

        # 2. Debtor Payment Delay Alerts
        for inv in high_risk_invoices[:2]:
            p_late = int((inv.p_delay or 0.70) * 100)
            clean_name = inv.debtor_name.split("(")[0].strip()
            alerts.append(AlertData(
                id=f"alt-invoice-{inv.id[:8]}",
                severity=AlertSeverity.WARNING,
                title=f"{clean_name} Delay Risk",
                description=f"{p_late}% late odds on {inv.amount:,.0f} {inv.currency} invoice due {inv.due_date}. Accelerates liquidity deficit.",
                action_label="Draft Reminder",
                action_type="draft_reminder",
                related_entity_id=inv.id
            ))

        # 3. Concentration Risk Alert
        if concentration_pct and concentration_pct >= 20.0 and concentration_debtor:
            clean_name = concentration_debtor.split("(")[0].strip()
            alerts.append(AlertData(
                id=f"alt-concentration-{str(uuid.uuid4())[:8]}",
                severity=AlertSeverity.INFO,
                title="Debtor Concentration Warning",
                description=f"{clean_name} represents {concentration_pct:.1f}% of total open receivables. Diversification recommended.",
                action_label="Explore Factoring",
                action_type="open_financing",
                related_entity_id=None
            ))

        return alerts
