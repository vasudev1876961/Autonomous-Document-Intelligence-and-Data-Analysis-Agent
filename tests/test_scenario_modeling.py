"""
Unit tests for Scenario Modeling, Counterfactuals, and Sensitivity Engine.
"""
from src.tools.scenario_modeling import ScenarioModelingEngine
from src.tools.numerical_analysis import NumericalAnalyzer

def test_counterfactual_simulation():
    sample_segs = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segs, "₹ lakh")
    
    # Simulate Segment A holding flat at 500 (80 lakh loss avoided)
    cf = ScenarioModelingEngine.simulate_counterfactual(
        base_summary=seg_summary,
        scenario_name="Segment A Constant",
        overrides={"Segment A": 500.0}
    )
    
    assert cf.simulated_period_2_total == 980.0
    assert cf.simulated_delta == -20.0
    assert cf.loss_preserved_pct == 80.0
    assert cf.delta_difference_from_actual == 80.0

def test_sensitivity_matrix():
    sample_segs = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segs, "₹ lakh")
    
    sens = ScenarioModelingEngine.compute_sensitivity_matrix(
        base_summary=seg_summary,
        segment_name="Segment A",
        growth_shocks=[-0.10, 0.0, 0.10]
    )
    
    assert sens.segment_name == "Segment A"
    assert len(sens.points) == 3
    # At 0% shock, segment value = 420.0, total = 900.0
    zero_shock = next(p for p in sens.points if p.shock_pct == 0.0)
    assert zero_shock.segment_value == 420.0
    assert zero_shock.total_revenue == 900.0

def test_recovery_plan_and_monte_carlo():
    sample_segs = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segs, "₹ lakh")
    
    # Solve for 1000 lakh recovery
    rec = ScenarioModelingEngine.calculate_recovery_targets(seg_summary, target_revenue=1000.0)
    assert rec.required_incremental == 100.0
    assert sum(rec.segment_targets.values()) == 1000.0
    
    # Monte Carlo simulation
    mc = ScenarioModelingEngine.run_monte_carlo_forecast(seg_summary, num_simulations=500, seed=42)
    assert mc.num_simulations == 500
    assert mc.p5_conservative < mc.p50_median < mc.p95_optimistic
