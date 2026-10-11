"""
Deterministic Numerical Analysis Engine for financial and statistical calculations.
Guarantees mathematical correctness without relying on LLM arithmetic.
"""
from typing import Any, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

class PeriodComparisonResult(BaseModel):
    metric_name: str
    period_1_name: str
    period_1_value: float
    period_2_name: str
    period_2_value: float
    unit: str
    absolute_change: float
    percentage_change: Optional[float] = None
    direction: str # "increase", "decrease", "unchanged"
    is_baseline_zero: bool = False
    formula_used: str

class SegmentContributionResult(BaseModel):
    segment_name: str
    period_1_value: float
    period_2_value: float
    absolute_change: float
    contribution_percentage: Optional[float] = None
    is_offsetting: bool = False
    direction: str

class SegmentAnalysisSummary(BaseModel):
    metric_name: str
    unit: str
    total_period_1: float
    total_period_2: float
    total_absolute_change: float
    total_percentage_change: Optional[float] = None
    segments: list[SegmentContributionResult]
    reconciled_with_total: bool
    discrepancy_amount: float = 0.0

class StatisticalSummaryResult(BaseModel):
    metric_name: str
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    sum_value: float

class NumericalAnalyzer:
    @staticmethod
    def compare_periods(
        metric_name: str,
        r1: float,
        r2: float,
        p1_name: str = "Period 1",
        p2_name: str = "Period 2",
        unit: str = "units"
    ) -> PeriodComparisonResult:
        """
        Calculates:
        Delta R = R2 - R1
        %Delta R = ((R2 - R1) / R1) * 100
        """
        abs_change = round(r2 - r1, 4)
        direction = "unchanged"
        if abs_change > 0:
            direction = "increase"
        elif abs_change < 0:
            direction = "decrease"

        if r1 == 0:
            pct_change = None
            is_zero = True
            formula = "Delta R = R2 - R1 (percentage change undefined when baseline R1 is 0)"
        else:
            pct_change = round((abs_change / r1) * 100.0, 2)
            is_zero = False
            formula = "%Delta R = ((R2 - R1) / R1) * 100"

        return PeriodComparisonResult(
            metric_name=metric_name,
            period_1_name=p1_name,
            period_1_value=r1,
            period_2_name=p2_name,
            period_2_value=r2,
            unit=unit,
            absolute_change=abs_change,
            percentage_change=pct_change,
            direction=direction,
            is_baseline_zero=is_zero,
            formula_used=formula
        )

    @staticmethod
    def analyze_segment_contributions(
        metric_name: str,
        segments_data: list[dict[str, Any]],
        unit: str = "units"
    ) -> SegmentAnalysisSummary:
        """
        segments_data format:
        [
            {"segment": "Segment A", "p1": 500, "p2": 420},
            {"segment": "Segment B", "p1": 300, "p2": 280},
            ...
        ]
        Computes Ci = (Delta R_i / Delta R_total) * 100
        """
        total_p1 = sum(float(s["p1"]) for s in segments_data)
        total_p2 = sum(float(s["p2"]) for s in segments_data)
        total_delta = round(total_p2 - total_p1, 4)
        
        total_pct = round((total_delta / total_p1 * 100.0), 2) if total_p1 != 0 else None

        results: list[SegmentContributionResult] = []
        for s in segments_data:
            name = str(s["segment"])
            p1 = float(s["p1"])
            p2 = float(s["p2"])
            delta_i = round(p2 - p1, 4)
            
            direction = "unchanged"
            if delta_i > 0:
                direction = "increase"
            elif delta_i < 0:
                direction = "decrease"

            if total_delta != 0:
                c_i = round((delta_i / total_delta) * 100.0, 2)
                # If segment moved in opposite direction of total delta, it is offsetting
                is_offsetting = (delta_i * total_delta < 0)
            else:
                c_i = 0.0
                is_offsetting = False

            results.append(
                SegmentContributionResult(
                    segment_name=name,
                    period_1_value=p1,
                    period_2_value=p2,
                    absolute_change=delta_i,
                    contribution_percentage=c_i,
                    is_offsetting=is_offsetting,
                    direction=direction
                )
            )

        sum_of_segment_deltas = sum(r.absolute_change for r in results)
        discrepancy = round(abs(total_delta - sum_of_segment_deltas), 4)
        reconciled = (discrepancy < 1e-4)

        return SegmentAnalysisSummary(
            metric_name=metric_name,
            unit=unit,
            total_period_1=total_p1,
            total_period_2=total_p2,
            total_absolute_change=total_delta,
            total_percentage_change=total_pct,
            segments=results,
            reconciled_with_total=reconciled,
            discrepancy_amount=discrepancy
        )

    @staticmethod
    def calculate_statistics(metric_name: str, values: list[float]) -> StatisticalSummaryResult:
        arr = np.array(values, dtype=np.float64)
        if len(arr) == 0:
            return StatisticalSummaryResult(
                metric_name=metric_name,
                count=0, mean=0.0, median=0.0, std_dev=0.0,
                min_value=0.0, max_value=0.0, sum_value=0.0
            )
        return StatisticalSummaryResult(
            metric_name=metric_name,
            count=len(arr),
            mean=round(float(np.mean(arr)), 4),
            median=round(float(np.median(arr)), 4),
            std_dev=round(float(np.std(arr)), 4),
            min_value=round(float(np.min(arr)), 4),
            max_value=round(float(np.max(arr)), 4),
            sum_value=round(float(np.sum(arr)), 4)
        )
