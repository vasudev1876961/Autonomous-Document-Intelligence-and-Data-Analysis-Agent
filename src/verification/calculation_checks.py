"""
Deterministic Calculation Verifier:
Re-computes calculations to mathematically verify outputs independently.
"""
from typing import Optional
from pydantic import BaseModel, Field
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary

class CalculationVerificationResult(BaseModel):
    is_valid: bool
    test_name: str
    expected_value: float
    computed_value: float
    discrepancy: float
    details: str

class CalculationVerifier:
    @staticmethod
    def verify_period_comparison(result: PeriodComparisonResult) -> list[CalculationVerificationResult]:
        checks = []
        
        # 1. Delta check: Delta = R2 - R1
        recomputed_delta = round(result.period_2_value - result.period_1_value, 4)
        delta_diff = abs(recomputed_delta - result.absolute_change)
        checks.append(
            CalculationVerificationResult(
                is_valid=(delta_diff < 1e-4),
                test_name="Absolute Delta Recomputation",
                expected_value=recomputed_delta,
                computed_value=result.absolute_change,
                discrepancy=delta_diff,
                details=f"Verified Delta = {result.period_2_value} - {result.period_1_value} = {recomputed_delta}"
            )
        )

        # 2. Percentage change check
        if not result.is_baseline_zero and result.percentage_change is not None:
            recomputed_pct = round((recomputed_delta / result.period_1_value) * 100.0, 2)
            pct_diff = abs(recomputed_pct - result.percentage_change)
            checks.append(
                CalculationVerificationResult(
                    is_valid=(pct_diff < 0.05), # minor rounding allowance
                    test_name="Percentage Change Recomputation",
                    expected_value=recomputed_pct,
                    computed_value=result.percentage_change,
                    discrepancy=pct_diff,
                    details=f"Verified %Delta = ({recomputed_delta} / {result.period_1_value}) * 100 = {recomputed_pct}%"
                )
            )

        return checks

    @staticmethod
    def verify_segment_analysis(summary: SegmentAnalysisSummary) -> list[CalculationVerificationResult]:
        checks = []

        # 1. Segment sum equals total delta
        sum_segment_deltas = round(sum(s.absolute_change for s in summary.segments), 4)
        discrepancy = round(abs(sum_segment_deltas - summary.total_absolute_change), 4)
        checks.append(
            CalculationVerificationResult(
                is_valid=(discrepancy < 1e-3),
                test_name="Segment Additivity Reconciliation",
                expected_value=summary.total_absolute_change,
                computed_value=sum_segment_deltas,
                discrepancy=discrepancy,
                details=f"Sum of segment changes ({sum_segment_deltas}) vs reported total change ({summary.total_absolute_change})"
            )
        )

        # 2. Contribution percentages sum to 100% when total delta != 0
        if summary.total_absolute_change != 0:
            sum_contrib = round(sum((s.contribution_percentage or 0.0) for s in summary.segments), 1)
            contrib_diff = round(abs(100.0 - sum_contrib), 1)
            checks.append(
                CalculationVerificationResult(
                    is_valid=(contrib_diff <= 0.5), # Allow 0.5% for individual rounding
                    test_name="Segment Contribution Sum to 100%",
                    expected_value=100.0,
                    computed_value=sum_contrib,
                    discrepancy=contrib_diff,
                    details=f"Sum of segment contribution percentages = {sum_contrib}%"
                )
            )

        return checks
