"""
Cash Conversion Cycle (CCC) & Working Capital Diagnostics Engine
Deterministic pure Python + numpy.
NO LLM IMPORTS ALLOWED (TRD DE-01).
"""
from typing import Dict, Any, Optional

class CCCEngine:
    """Calculates Days Sales Outstanding (DSO), Days Payable Outstanding (DPO), and Cash Conversion Cycle."""

    @classmethod
    def calculate(
        cls,
        total_open_receivables: float,
        annual_credit_sales: float,
        total_open_payables: float,
        annual_cogs: float,
        inventory_estimate_days: float = 38.0
    ) -> Dict[str, Optional[float]]:
        """
        CCC = DIO + DSO - DPO
        Returns pure dictionary with exact metrics rounded to 1 decimal place.
        """
        # Days Sales Outstanding
        if annual_credit_sales > 0:
            dso = round((total_open_receivables / annual_credit_sales) * 365.0, 1)
        else:
            dso = None

        # Days Payable Outstanding
        if annual_cogs > 0:
            dpo = round((total_open_payables / annual_cogs) * 365.0, 1)
        else:
            dpo = 30.0  # standard supplier credit terms

        dio = inventory_estimate_days

        if dso is not None and dpo is not None:
            ccc = round(dio + dso - dpo, 1)
        else:
            ccc = None

        return {
            "dso": dso,
            "dpo": dpo,
            "dio": dio,
            "cash_conversion_cycle": ccc
        }
