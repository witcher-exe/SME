"""
Scenario Simulation Engine
Stress-testing baseline cash flow under debtor delays, cost inflation, capex, and factoring.
NO LLM IMPORTS ALLOWED (TRD DE-01).
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from app.engines.forecast_engine import ForecastEngine
from app.models.schemas import ScenarioResponse, WeeklyComparison, InvoiceDelayPrediction

class ScenarioEngine:
    """Simulates what-if scenarios comparing stressed trajectory against baseline cash trajectory."""

    @classmethod
    def run_simulation(
        cls,
        company_id: str,
        current_cash: float,
        weekly_inflows_mean: float,
        weekly_inflows_std: float,
        weekly_outflows_mean: float,
        weekly_outflows_std: float,
        debtor_delay_days: int = 0,
        supplier_cost_delta_pct: float = 0.0,
        capex_spend: float = 0.0,
        apply_factoring_advance: bool = False,
        eligible_receivables_total: float = 250000.0,
        start_date: Optional[date] = None,
        seed: int = 42
    ) -> ScenarioResponse:
        if start_date is None:
            start_date = date.today()

        # 1. Baseline Run (No stress shocks)
        base_chart, base_sf_date, _, base_runway = ForecastEngine.run_monte_carlo(
            current_cash=current_cash,
            weekly_inflows_mean=weekly_inflows_mean,
            weekly_inflows_std=weekly_inflows_std,
            weekly_outflows_mean=weekly_outflows_mean,
            weekly_outflows_std=weekly_outflows_std,
            start_date=start_date,
            seed=seed
        )

        # 2. Factoring Advance amount (80% advance rate minus 2.5% fee)
        factoring_amount = 0.0
        if apply_factoring_advance:
            factoring_amount = eligible_receivables_total * 0.80

        # Convert delay days to delay weeks
        delay_weeks = int(round(debtor_delay_days / 7.0))

        # 3. Stressed Scenario Run
        sim_chart, sim_sf_date, _, sim_runway = ForecastEngine.run_monte_carlo(
            current_cash=current_cash,
            weekly_inflows_mean=weekly_inflows_mean,
            weekly_inflows_std=weekly_inflows_std,
            weekly_outflows_mean=weekly_outflows_mean,
            weekly_outflows_std=weekly_outflows_std,
            start_date=start_date,
            seed=seed,
            debtor_delay_weeks=delay_weeks,
            supplier_cost_delta_pct=supplier_cost_delta_pct,
            capex_spend=capex_spend,
            factoring_advance=factoring_amount
        )

        # Calculate shortfall day numbers from start_date
        base_sf_day = None
        if base_sf_date:
            base_sf_day = (date.fromisoformat(base_sf_date) - start_date).days

        sim_sf_day = None
        if sim_sf_date:
            sim_sf_day = (date.fromisoformat(sim_sf_date) - start_date).days

        # Delta days calculation: positive = delayed (improved), negative = accelerated (worsened)
        if base_sf_day is not None and sim_sf_day is not None:
            delta_days = sim_sf_day - base_sf_day
        elif base_sf_day is not None and sim_sf_day is None:
            # Shortfall eliminated entirely!
            delta_days = 90 - base_sf_day
        elif base_sf_day is None and sim_sf_day is not None:
            delta_days = -sim_sf_day
        else:
            delta_days = 0

        # Construct weekly comparison table
        weekly_comparisons: List[WeeklyComparison] = []
        for w in range(len(base_chart.weeks)):
            # Simulated inflows/outflows for weekly breakdown
            inf = weekly_inflows_mean if delay_weeks == 0 else (weekly_inflows_mean * 0.7)
            if w == 0 and factoring_amount > 0:
                inf += factoring_amount
            outf = weekly_outflows_mean * (1.0 + (supplier_cost_delta_pct / 100.0))
            if w == 0 and capex_spend > 0:
                outf += capex_spend

            weekly_comparisons.append(WeeklyComparison(
                week=base_chart.weeks[w],
                date=base_chart.dates[w],
                baseline_cash=base_chart.p50_median[w],
                simulated_cash=sim_chart.p50_median[w],
                projected_inflow=round(float(inf), 2),
                projected_outflow=round(float(outf), 2)
            ))

        return ScenarioResponse(
            company_id=company_id,
            baseline_shortfall_day=base_sf_day,
            scenario_shortfall_day=sim_sf_day,
            delta_days=delta_days,
            weekly_simulation=weekly_comparisons,
            debtor_risks=[],
            factoring_advance_amount=factoring_amount if apply_factoring_advance else None,
            computed_at=datetime.utcnow().isoformat()
        )
