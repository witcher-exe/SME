import pytest
from app.engines.covenant_engine import CovenantEngine
from app.models.enums import CovenantResult

def test_covenant_dscr_calculation():
    # DSCR = NOI / TDS = 50000 / 40000 = 1.25 -> PASS
    covenants = CovenantEngine.evaluate_covenants(
        liquid_cash=100000.0,
        accounts_receivable=200000.0,
        current_liabilities=150000.0,
        monthly_noi=50000.0,
        monthly_debt_service=40000.0,
        total_debt=300000.0,
        equity=200000.0
    )
    dscr = next(c for c in covenants if c["name"] == "DSCR")
    assert dscr["current_value"] == 1.25
    assert dscr["result"] == CovenantResult.PASS

def test_covenant_dscr_fail():
    # DSCR = 40000 / 45000 = 0.89 -> FAIL (< 1.25 * 0.9)
    covenants = CovenantEngine.evaluate_covenants(
        liquid_cash=100000.0,
        accounts_receivable=200000.0,
        current_liabilities=150000.0,
        monthly_noi=40000.0,
        monthly_debt_service=45000.0,
        total_debt=300000.0,
        equity=200000.0
    )
    dscr = next(c for c in covenants if c["name"] == "DSCR")
    assert dscr["current_value"] == 0.89
    assert dscr["result"] == CovenantResult.FAIL

def test_quick_ratio_pass_and_fail():
    # Pass: (100k + 200k) / 250k = 1.20 >= 1.0
    c_pass = CovenantEngine.evaluate_covenants(100000, 200000, 250000, 50000, 40000, 300000, 200000)
    qr_pass = next(c for c in c_pass if c["name"] == "Quick Ratio")
    assert qr_pass["current_value"] == 1.20
    assert qr_pass["result"] == CovenantResult.PASS

    # Fail: (10k + 20k) / 50k = 0.60 < 0.90
    c_fail = CovenantEngine.evaluate_covenants(10000, 20000, 50000, 50000, 40000, 300000, 200000)
    qr_fail = next(c for c in c_fail if c["name"] == "Quick Ratio")
    assert qr_fail["current_value"] == 0.60
    assert qr_fail["result"] == CovenantResult.FAIL

def test_leverage_ratio():
    # 500k debt / 200k equity = 2.5 <= 3.0 -> PASS
    covs = CovenantEngine.evaluate_covenants(100000, 200000, 250000, 50000, 40000, 500000, 200000)
    lev = next(c for c in covs if c["name"] == "Leverage")
    assert lev["current_value"] == 2.50
    assert lev["result"] == CovenantResult.PASS
