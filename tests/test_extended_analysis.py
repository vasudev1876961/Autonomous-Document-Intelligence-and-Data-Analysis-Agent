"""
Unit tests for extended numerical analysis methods:
- Variance analysis
- CAGR
- Growth series
- Outlier detection
"""
import pytest
from src.tools.numerical_analysis import NumericalAnalyzer

def test_analyze_variance():
    # Actual 900 vs Budget 1000 (unfavorable for revenue)
    res_rev = NumericalAnalyzer.analyze_variance("Revenue", actual=900.0, budget=1000.0, higher_is_better=True)
    assert res_rev.variance_amount == -100.0
    assert res_rev.variance_percentage == -10.0
    assert res_rev.is_favorable is False
    assert res_rev.status == "unfavorable"

    # Actual 800 vs Budget 900 (favorable for expense)
    res_exp = NumericalAnalyzer.analyze_variance("Operating Expenses", actual=800.0, budget=900.0, higher_is_better=False)
    assert res_exp.variance_amount == -100.0
    assert res_exp.is_favorable is True
    assert res_exp.status == "favorable"

def test_calculate_cagr():
    # 100 to 144 over 2 periods (20% CAGR)
    res = NumericalAnalyzer.calculate_cagr("Sales", beginning_value=100.0, ending_value=144.0, periods=2)
    assert res.is_valid is True
    assert res.cagr_percentage == 20.0

    # Invalid beginning value <= 0
    res_invalid = NumericalAnalyzer.calculate_cagr("Sales", beginning_value=0.0, ending_value=100.0, periods=2)
    assert res_invalid.is_valid is False
    assert res_invalid.cagr_percentage is None

def test_calculate_growth_series():
    series = [("Q1", 100.0), ("Q2", 120.0), ("Q3", 150.0)]
    res = NumericalAnalyzer.calculate_growth_series("Revenue", series)
    assert len(res.series) == 3
    assert res.series[0].sequential_growth_pct is None
    assert res.series[1].sequential_growth_pct == 20.0
    assert res.series[2].sequential_growth_pct == 25.0
    assert res.average_growth_pct == 22.5

def test_detect_outliers():
    # Values with one distinct outlier
    values = [10.0, 10.5, 9.8, 10.2, 10.1, 95.0]
    res = NumericalAnalyzer.detect_outliers("Metrics", values, threshold_z=2.0)
    assert res.has_outliers is True
    outliers = [o for o in res.outliers_detected if o.is_outlier]
    assert len(outliers) == 1
    assert outliers[0].value == 95.0
