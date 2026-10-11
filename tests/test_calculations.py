"""
Unit tests for deterministic numerical analysis and mathematical invariants.
"""
import pytest
from src.tools.numerical_analysis import NumericalAnalyzer

def test_period_over_period_calculation():
    # Scenario: 1000 down to 900
    res = NumericalAnalyzer.compare_periods(
        metric_name="Revenue",
        r1=1000.0,
        r2=900.0,
        p1_name="Q1",
        p2_name="Q2",
        unit="₹ lakh"
    )
    assert res.absolute_change == -100.0
    assert res.percentage_change == -10.0
    assert res.direction == "decrease"
    assert not res.is_baseline_zero

def test_period_zero_baseline():
    res = NumericalAnalyzer.compare_periods(
        metric_name="New Venture",
        r1=0.0,
        r2=50.0,
        p1_name="Q1",
        p2_name="Q2"
    )
    assert res.absolute_change == 50.0
    assert res.percentage_change is None
    assert res.is_baseline_zero is True

def test_segment_contribution_and_reconciliation():
    # Scenario from Section 20 of specification:
    # A: 500 -> 420 (delta -80, contrib 80%)
    # B: 300 -> 280 (delta -20, contrib 20%)
    # C: 200 -> 200 (delta 0, contrib 0%)
    # Total: 1000 -> 900 (delta -100)
    segments = [
        {"segment": "Segment A", "p1": 500, "p2": 420},
        {"segment": "Segment B", "p1": 300, "p2": 280},
        {"segment": "Segment C", "p1": 200, "p2": 200},
    ]
    summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", segments, "₹ lakh")
    
    assert summary.total_period_1 == 1000.0
    assert summary.total_period_2 == 900.0
    assert summary.total_absolute_change == -100.0
    assert summary.total_percentage_change == -10.0
    assert summary.reconciled_with_total is True

    seg_map = {s.segment_name: s for s in summary.segments}
    assert seg_map["Segment A"].absolute_change == -80.0
    assert seg_map["Segment A"].contribution_percentage == 80.0

    assert seg_map["Segment B"].absolute_change == -20.0
    assert seg_map["Segment B"].contribution_percentage == 20.0

    assert seg_map["Segment C"].absolute_change == 0.0
    assert seg_map["Segment C"].contribution_percentage == 0.0
