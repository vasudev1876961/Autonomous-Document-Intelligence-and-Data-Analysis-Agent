"""
Deterministic Scenario Simulation, Counterfactual Modeling, and Sensitivity Analysis Engine.
Provides executive 'what-if' modeling, recovery target trajectory calculation,
and Monte Carlo volatility risk bounds with zero LLM calculation hallucination.
"""
from typing import Any, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from src.tools.numerical_analysis import SegmentAnalysisSummary

class CounterfactualResult(BaseModel):
    scenario_name: str
    overrides: dict[str, float]
    base_period_1_total: float
    base_period_2_total: float
    simulated_period_2_total: float
    simulated_delta: float
    simulated_pct_change: float
    delta_difference_from_actual: float
    loss_preserved_pct: float
    narrative_summary: str

class SensitivityPoint(BaseModel):
    shock_pct: float
    segment_value: float
    total_revenue: float
    overall_growth_pct: float

class SensitivityMatrixResult(BaseModel):
    segment_name: str
    base_value: float
    points: list[SensitivityPoint]

class RecoveryTargetPlan(BaseModel):
    target_metric: str
    target_revenue: float
    current_q2_revenue: float
    required_incremental: float
    segment_targets: dict[str, float]
    segment_required_growth_pct: dict[str, float]
    feasibility_status: str
    narrative_strategy: str

class MonteCarloSimulationResult(BaseModel):
    num_simulations: int
    mean_forecast: float
    std_dev: float
    p5_conservative: float
    p50_median: float
    p95_optimistic: float
    prob_recovering_baseline: float
    simulation_samples: list[float] = Field(default_factory=list)

class ScenarioModelingEngine:
    """
    Executes verifiable, programmatic financial simulations and counterfactual what-if analysis.
    """

    @staticmethod
    def simulate_counterfactual(
        base_summary: SegmentAnalysisSummary,
        scenario_name: str,
        overrides: dict[str, float]
    ) -> CounterfactualResult:
        """
        Simulates what total revenue would be if specified segments achieved alternative period 2 values.
        E.g., overrides = {"Segment A": 500.0} (simulates if Segment A had zero decline).
        """
        simulated_p2_vals = {}
        for s in base_summary.segments:
            if s.segment_name in overrides:
                simulated_p2_vals[s.segment_name] = overrides[s.segment_name]
            else:
                simulated_p2_vals[s.segment_name] = s.period_2_value

        p1_total = base_summary.total_period_1
        actual_p2_total = base_summary.total_period_2
        simulated_p2_total = sum(simulated_p2_vals.values())

        sim_delta = simulated_p2_total - p1_total
        sim_pct = (sim_delta / p1_total * 100.0) if p1_total != 0 else 0.0

        actual_delta = actual_p2_total - p1_total
        diff_from_actual = simulated_p2_total - actual_p2_total

        # Percentage of actual decline avoided/preserved
        if actual_delta < 0:
            loss_preserved = max(0.0, min(100.0, (diff_from_actual / abs(actual_delta)) * 100.0))
        else:
            loss_preserved = 0.0

        narrative = (
            f"Under scenario '{scenario_name}', total period 2 revenue would be "
            f"{simulated_p2_total:,.1f} {base_summary.unit} ({sim_pct:+.1f}%), "
            f"preserving {diff_from_actual:,.1f} {base_summary.unit} ({loss_preserved:.1f}% of the decline)."
        )

        return CounterfactualResult(
            scenario_name=scenario_name,
            overrides=overrides,
            base_period_1_total=p1_total,
            base_period_2_total=actual_p2_total,
            simulated_period_2_total=simulated_p2_total,
            simulated_delta=sim_delta,
            simulated_pct_change=round(sim_pct, 2),
            delta_difference_from_actual=diff_from_actual,
            loss_preserved_pct=round(loss_preserved, 2),
            narrative_summary=narrative
        )

    @staticmethod
    def compute_sensitivity_matrix(
        base_summary: SegmentAnalysisSummary,
        segment_name: str,
        growth_shocks: Optional[list[float]] = None
    ) -> SensitivityMatrixResult:
        """
        Tests the sensitivity of total revenue to shocks in a specific business segment.
        Default shocks: -20%, -10%, -5%, 0%, +5%, +10%, +20%.
        """
        if growth_shocks is None:
            growth_shocks = [-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20]

        target_seg = next((s for s in base_summary.segments if s.segment_name.lower() == segment_name.lower()), None)
        if not target_seg:
            raise ValueError(f"Segment '{segment_name}' not found in base summary")

        base_val = target_seg.period_2_value
        p1_total = base_summary.total_period_1
        other_segs_total = sum(s.period_2_value for s in base_summary.segments if s.segment_name.lower() != segment_name.lower())

        points = []
        for shock in sorted(growth_shocks):
            shocked_val = base_val * (1.0 + shock)
            shocked_total = other_segs_total + shocked_val
            growth_pct = ((shocked_total - p1_total) / p1_total * 100.0) if p1_total != 0 else 0.0
            points.append(SensitivityPoint(
                shock_pct=round(shock * 100.0, 1),
                segment_value=round(shocked_val, 2),
                total_revenue=round(shocked_total, 2),
                overall_growth_pct=round(growth_pct, 2)
            ))

        return SensitivityMatrixResult(
            segment_name=target_seg.segment_name,
            base_value=base_val,
            points=points
        )

    @staticmethod
    def calculate_recovery_targets(
        base_summary: SegmentAnalysisSummary,
        target_revenue: float
    ) -> RecoveryTargetPlan:
        """
        Solves for the required revenue distribution across segments to attain a target revenue level.
        Uses historical contribution weightings to allocate target recovery quotas.
        """
        current_rev = base_summary.total_period_2
        incremental_needed = target_revenue - current_rev

        segment_targets = {}
        growth_rates = {}

        # Allocate based on proportion of period 1 baseline
        p1_total = base_summary.total_period_1
        for s in base_summary.segments:
            weight = (s.period_1_value / p1_total) if p1_total != 0 else (1.0 / len(base_summary.segments))
            seg_target = s.period_2_value + (incremental_needed * weight)
            segment_targets[s.segment_name] = round(seg_target, 2)
            
            g_rate = ((seg_target - s.period_2_value) / s.period_2_value * 100.0) if s.period_2_value != 0 else 0.0
            growth_rates[s.segment_name] = round(g_rate, 2)

        if incremental_needed <= 0:
            status = "TARGET_ALREADY_EXCEEDED"
            strategy = "Current revenue already meets or surpasses the designated target."
        elif max(growth_rates.values()) > 35.0:
            status = "AGGRESSIVE_EXPANSION_REQUIRED"
            strategy = f"Requires high-velocity growth (>30%) primarily in {max(growth_rates, key=growth_rates.get)}."
        else:
            status = "FEASIBLE_MODERATE_RECOVERY"
            strategy = f"Requires balanced growth of approximately {sum(growth_rates.values())/len(growth_rates):.1f}% across business units."

        return RecoveryTargetPlan(
            target_metric="Revenue",
            target_revenue=target_revenue,
            current_q2_revenue=current_rev,
            required_incremental=incremental_needed,
            segment_targets=segment_targets,
            segment_required_growth_pct=growth_rates,
            feasibility_status=status,
            narrative_strategy=strategy
        )

    @staticmethod
    def run_monte_carlo_forecast(
        base_summary: SegmentAnalysisSummary,
        num_simulations: int = 1000,
        volatility_pct: float = 0.06,
        seed: int = 42
    ) -> MonteCarloSimulationResult:
        """
        Simulates probabilistic quarterly revenue outcomes using stochastic Gaussian perturbations
        calibrated across segment sizes and volatility thresholds.
        """
        rng = np.random.default_rng(seed)
        simulated_totals = []

        seg_bases = [s.period_2_value for s in base_summary.segments]

        for _ in range(num_simulations):
            # Sample relative change per segment ~ Normal(1.0, volatility)
            shocks = rng.normal(loc=1.0, scale=volatility_pct, size=len(seg_bases))
            # Segment cannot drop below zero
            sim_segs = np.maximum(0.0, np.array(seg_bases) * shocks)
            simulated_totals.append(float(np.sum(sim_segs)))

        totals_arr = np.array(simulated_totals)
        baseline_p1 = base_summary.total_period_1

        mean_f = float(np.mean(totals_arr))
        std_f = float(np.std(totals_arr))
        p5 = float(np.percentile(totals_arr, 5))
        p50 = float(np.percentile(totals_arr, 50))
        p95 = float(np.percentile(totals_arr, 95))
        prob_baseline = float(np.mean(totals_arr >= baseline_p1) * 100.0)

        return MonteCarloSimulationResult(
            num_simulations=num_simulations,
            mean_forecast=round(mean_f, 2),
            std_dev=round(std_f, 2),
            p5_conservative=round(p5, 2),
            p50_median=round(p50, 2),
            p95_optimistic=round(p95, 2),
            prob_recovering_baseline=round(prob_baseline, 1),
            simulation_samples=simulated_totals[:100]  # Store 100 for distribution plotting
        )
