"""
Consistency and Unit Harmonization Verifier:
Checks that metrics being compared share comparable time windows and normalized units.
"""
from typing import Optional
from pydantic import BaseModel

class ConsistencyCheckResult(BaseModel):
    is_consistent: bool
    check_type: str # "units", "periods", "baseline"
    description: str
    warning_message: Optional[str] = None

class ConsistencyVerifier:
    @staticmethod
    def check_units(unit_a: str, unit_b: str) -> ConsistencyCheckResult:
        u_a = unit_a.strip().lower()
        u_b = unit_b.strip().lower()
        if u_a == u_b:
            return ConsistencyCheckResult(
                is_consistent=True,
                check_type="units",
                description=f"Units match: '{unit_a}'"
            )
        else:
            return ConsistencyCheckResult(
                is_consistent=False,
                check_type="units",
                description=f"Unit mismatch: '{unit_a}' vs '{unit_b}'",
                warning_message=f"Comparison attempted across disparate units ('{unit_a}' vs '{unit_b}'). Normalization required."
            )

    @staticmethod
    def check_period_comparability(period_a: str, period_b: str) -> ConsistencyCheckResult:
        # e.g., Q1 vs Q2, 2023 vs 2024
        p_a = period_a.strip().lower()
        p_b = period_b.strip().lower()
        if p_a == p_b:
            return ConsistencyCheckResult(
                is_consistent=False,
                check_type="periods",
                description="Identical periods compared",
                warning_message=f"Comparison between the same period '{period_a}' produces zero delta."
            )
        return ConsistencyCheckResult(
            is_consistent=True,
            check_type="periods",
            description=f"Distinct comparative periods: '{period_a}' vs '{period_b}'"
        )
