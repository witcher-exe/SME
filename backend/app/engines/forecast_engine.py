"""
Monte Carlo Cash-Flow Forecasting & Payment Delay Engine
Deterministic pure Python + numpy + scipy + scikit-learn.
NO LLM IMPORTS ALLOWED (TRD DE-01).
"""
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from app.models.enums import RiskLevel
from app.models.schemas import ForecastChartData, InvoiceDelayPrediction

class ForecastEngine:
    """13-week Monte Carlo cash-flow simulation with P10/P50/P90 quantile corridors."""

    @classmethod
    def run_monte_carlo(
        cls,
        current_cash: float,
        weekly_inflows_mean: float,
        weekly_inflows_std: float,
        weekly_outflows_mean: float,
        weekly_outflows_std: float,
        start_date: Optional[date] = None,
        horizon_weeks: int = 13,
        mc_runs: int = 1000,
        safety_floor: float = 220000.0,
        seed: Optional[int] = 42,
        debtor_delay_weeks: int = 0,
        supplier_cost_delta_pct: float = 0.0,
        capex_spend: float = 0.0,
        factoring_advance: float = 0.0
    ) -> Tuple[ForecastChartData, Optional[str], Optional[float], int]:
        """
        Runs Monte Carlo cash paths and returns:
        (ForecastChartData, shortfall_date_iso, shortfall_deficit_amount, runway_days)
        """
        if seed is not None:
            np.random.seed(seed)

        if start_date is None:
            start_date = date.today()

        # Adjust parameters for scenarios
        adj_inflows_mean = weekly_inflows_mean
        if debtor_delay_weeks > 0:
            # Dampen near-term inflows if debtors delay
            adj_inflows_mean *= max(0.4, (1.0 - (debtor_delay_weeks * 0.15)))

        adj_outflows_mean = weekly_outflows_mean * (1.0 + (supplier_cost_delta_pct / 100.0))

        # Shape: (mc_runs, horizon_weeks)
        # Avoid negative inflows/outflows using lognormal or clipped normal
        inflow_sims = np.random.normal(adj_inflows_mean, max(weekly_inflows_std, 1000.0), (mc_runs, horizon_weeks))
        inflow_sims = np.clip(inflow_sims, a_min=0, a_max=None)

        outflow_sims = np.random.normal(adj_outflows_mean, max(weekly_outflows_std, 1000.0), (mc_runs, horizon_weeks))
        outflow_sims = np.clip(outflow_sims, a_min=0, a_max=None)

        # Apply capex spend at week 1
        if capex_spend > 0:
            outflow_sims[:, 0] += capex_spend

        # Apply factoring advance at week 1
        if factoring_advance > 0:
            inflow_sims[:, 0] += factoring_advance

        net_weekly = inflow_sims - outflow_sims
        cumulative_cash = np.zeros((mc_runs, horizon_weeks))

        for w in range(horizon_weeks):
            if w == 0:
                cumulative_cash[:, w] = current_cash + net_weekly[:, w]
            else:
                cumulative_cash[:, w] = cumulative_cash[:, w - 1] + net_weekly[:, w]

        # Calculate quantiles: P10 (conservative), P50 (median), P90 (optimistic)
        p10 = np.percentile(cumulative_cash, 10, axis=0)
        p50 = np.percentile(cumulative_cash, 50, axis=0)
        p90 = np.percentile(cumulative_cash, 90, axis=0)

        weeks = [f"W{i+1}" for i in range(horizon_weeks)]
        dates = [(start_date + timedelta(weeks=i)).isoformat() for i in range(horizon_weeks)]

        chart_data = ForecastChartData(
            weeks=weeks,
            dates=dates,
            p10_conservative=[round(float(v), 2) for v in p10],
            p50_median=[round(float(v), 2) for v in p50],
            p90_optimistic=[round(float(v), 2) for v in p90],
            safety_floor=float(safety_floor)
        )

        # Shortfall analysis: identify week where conservative P10 breaches safety floor
        shortfall_date = None
        shortfall_amount = None
        runway_days = horizon_weeks * 7

        for w in range(horizon_weeks):
            if p10[w] < safety_floor:
                # Exact calendar date of shortfall
                shortfall_day_offset = (w + 1) * 7
                shortfall_dt = start_date + timedelta(days=shortfall_day_offset)
                shortfall_date = shortfall_dt.isoformat()
                shortfall_amount = round(float(safety_floor - p10[w]), 2)
                runway_days = max(1, shortfall_day_offset)
                break

        return chart_data, shortfall_date, shortfall_amount, runway_days

    @classmethod
    def predict_invoice_delay(
        cls,
        amount: float,
        days_to_due: int,
        historical_avg_delay: Optional[float] = 12.0
    ) -> Tuple[float, int, RiskLevel]:
        """
        Evaluates debtor late payment odds using deterministic credit risk formula.
        Output: (p_delay, expected_delay_days, RiskLevel)
        """
        # Baseline logistic risk scoring based on invoice size and historical payment discipline
        hist_delay = historical_avg_delay or 0.0
        z = -0.8 + (0.05 * hist_delay) + (0.000002 * amount) - (0.015 * days_to_due)
        p_delay = 1.0 / (1.0 + np.exp(-z))
        p_delay = float(np.clip(p_delay, 0.05, 0.95))

        expected_delay_days = int(round(p_delay * (hist_delay + 14)))

        if p_delay > 0.60:
            risk_level = RiskLevel.HIGH
        elif p_delay >= 0.30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return round(p_delay, 2), expected_delay_days, risk_level
