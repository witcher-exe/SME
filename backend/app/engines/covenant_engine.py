"""
Covenant & Solvency Metric Calculation Engine
Deterministic pure Python + numpy. NO LLM IMPORTS ALLOWED (TRD DE-01).
"""
from typing import List, Dict, Any, Optional
from app.models.enums import CovenantResult

class CovenantEngine:
    """Computes exact financial covenants, liquidity ratios, and runway metrics."""

    @classmethod
    def evaluate_covenants(
        cls,
        liquid_cash: float,
        accounts_receivable: float,
        current_liabilities: float,
        monthly_noi: float,
        monthly_debt_service: float,
        total_debt: float,
        equity: float
    ) -> List[Dict[str, Any]]:
        """
        Evaluates DSCR, Quick Ratio, Leverage, and Burn Rate against standard SME thresholds.
        Returns pure dicts with exact mathematical formulas for explainability.
        """
        covenants = []

        # 1. DSCR = Net Operating Income / Total Debt Service
        if monthly_debt_service > 0:
            dscr_val = round(monthly_noi / monthly_debt_service, 2)
        else:
            dscr_val = 99.0  # Zero debt service
        
        dscr_required = 1.25  # Standard CMSME threshold
        if dscr_val >= dscr_required:
            dscr_res = CovenantResult.PASS
        elif dscr_val >= (dscr_required * 0.90):  # within 10%
            dscr_res = CovenantResult.WARNING
        else:
            dscr_res = CovenantResult.FAIL

        covenants.append({
            "name": "DSCR",
            "current_value": dscr_val,
            "required_value": dscr_required,
            "result": dscr_res,
            "formula": "NOI / TDS (Net Operating Income / Total Debt Service)"
        })

        # 2. Quick Ratio = (Cash + AR) / Current Liabilities
        if current_liabilities > 0:
            quick_ratio_val = round((liquid_cash + accounts_receivable) / current_liabilities, 2)
        else:
            quick_ratio_val = 99.0
        
        qr_required = 1.00
        if quick_ratio_val >= qr_required:
            qr_res = CovenantResult.PASS
        elif quick_ratio_val >= (qr_required * 0.90):
            qr_res = CovenantResult.WARNING
        else:
            qr_res = CovenantResult.FAIL

        covenants.append({
            "name": "Quick Ratio",
            "current_value": quick_ratio_val,
            "required_value": qr_required,
            "result": qr_res,
            "formula": "(Liquid Cash + Open AR) / Current Liabilities"
        })

        # 3. Leverage Ratio = Total Debt / Equity
        if equity > 0:
            leverage_val = round(total_debt / equity, 2)
        else:
            leverage_val = 99.0

        lev_required = 3.00  # Max permitted leverage
        if leverage_val <= lev_required:
            lev_res = CovenantResult.PASS
        elif leverage_val <= (lev_required * 1.10):
            lev_res = CovenantResult.WARNING
        else:
            lev_res = CovenantResult.FAIL

        covenants.append({
            "name": "Leverage",
            "current_value": leverage_val,
            "required_value": lev_required,
            "result": lev_res,
            "formula": "Total Debt / Total Equity"
        })

        # 4. Burn Rate / Operating Margin
        covenants.append({
            "name": "Monthly Net NOI",
            "current_value": round(monthly_noi, 2),
            "required_value": round(monthly_debt_service, 2),
            "result": CovenantResult.PASS if monthly_noi >= monthly_debt_service else CovenantResult.FAIL,
            "formula": "Monthly Revenue - Monthly Operating Expenses"
        })

        return covenants

    @classmethod
    def calculate_readiness_score(
        cls,
        dscr: float,
        quick_ratio: float,
        concentration_pct: float = 24.5,
        runway_days: int = 34,
        chain_intact: bool = True
    ) -> Dict[str, Any]:
        """
        WeBank-Inspired Cash-Flow Underwriting Readiness Score (0-100).
        Calculated transparently from 4 deterministic dimensions:
        1. Inflow Regularity & DSCR (0-25)
        2. Debtor Diversification / Concentration (0-25)
        3. P10 Solvency Buffer & Runway (0-25)
        4. Audit Trail Integrity (0-25)
        """
        # 1. DSCR (target >= 1.25 for 25 pts)
        s1 = min(25.0, max(0.0, (dscr / 1.25) * 25.0))
        # 2. Diversification (concentration <= 20% gives 25 pts, >50% gives 5 pts)
        if concentration_pct <= 20.0:
            s2 = 25.0
        elif concentration_pct <= 40.0:
            s2 = 18.0
        else:
            s2 = max(5.0, 25.0 - (concentration_pct * 0.4))
        # 3. Solvency & Runway (runway >= 60 days gives 25 pts, 30 days gives 15 pts)
        s3 = min(25.0, max(5.0, (runway_days / 60.0) * 25.0))
        # 4. Audit Chain Integrity (25 pts if chain intact, 0 if tampered)
        s4 = 25.0 if chain_intact else 0.0

        total_score = round(s1 + s2 + s3 + s4)
        tier_label = "Grade A (Prime)" if total_score >= 80 else ("Grade B (Standard)" if total_score >= 65 else "Grade C (Subprime)")

        return {
            "total_score": total_score,
            "tier_label": tier_label,
            "components": {
                "dscr_regularity": round(s1, 1),
                "debtor_diversification": round(s2, 1),
                "solvency_buffer": round(s3, 1),
                "audit_integrity": round(s4, 1)
            }
        }
