import pytest
from datetime import date
from app.engines.forecast_engine import ForecastEngine

def test_monte_carlo_dimensions_and_corridor():
    """Verify that Monte Carlo outputs 13 weeks with P10 <= P50 <= P90 monotonically ordered per week."""
    chart, sf_date, sf_amt, runway = ForecastEngine.run_monte_carlo(
        current_cash=450000.0,
        weekly_inflows_mean=140000.0,
        weekly_inflows_std=20000.0,
        weekly_outflows_mean=140000.0,
        weekly_outflows_std=15000.0,
        horizon_weeks=13,
        safety_floor=200000.0,
        seed=42
    )
    assert len(chart.weeks) == 13
    assert len(chart.p10_conservative) == 13
    assert len(chart.p50_median) == 13
    assert len(chart.p90_optimistic) == 13
    
    for w in range(13):
        assert chart.p10_conservative[w] <= chart.p50_median[w] <= chart.p90_optimistic[w]

def test_invoice_delay_logistic_prediction():
    """Verify that larger amounts or overdue days result in higher delay probability."""
    p1, days1, r1 = ForecastEngine.predict_invoice_delay(amount=50000.0, days_to_due=20, historical_avg_delay=5.0)
    p2, days2, r2 = ForecastEngine.predict_invoice_delay(amount=350000.0, days_to_due=-10, historical_avg_delay=25.0)
    
    assert p2 > p1
    assert days2 > days1
