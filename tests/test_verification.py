"""
Unit tests for verification pipeline (math recomputation, citation existence, consistency).
"""
import pytest
from src.tools.numerical_analysis import NumericalAnalyzer
from src.verification.calculation_checks import CalculationVerifier
from src.verification.consistency_checks import ConsistencyVerifier

def test_calculation_recomputation_check():
    p_res = NumericalAnalyzer.compare_periods("Revenue", 1000.0, 900.0, "Q1", "Q2")
    checks = CalculationVerifier.verify_period_comparison(p_res)
    assert len(checks) >= 2
    assert all(c.is_valid for c in checks)

def test_segment_additivity_verification():
    segments = [
        {"segment": "A", "p1": 500, "p2": 420},
        {"segment": "B", "p1": 300, "p2": 280},
    ]
    summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", segments)
    checks = CalculationVerifier.verify_segment_analysis(summary)
    assert all(c.is_valid for c in checks)

def test_unit_and_period_consistency():
    u_check = ConsistencyVerifier.check_units("₹ lakh", "₹ lakh")
    assert u_check.is_consistent is True

    u_bad = ConsistencyVerifier.check_units("₹ lakh", "USD")
    assert u_bad.is_consistent is False
