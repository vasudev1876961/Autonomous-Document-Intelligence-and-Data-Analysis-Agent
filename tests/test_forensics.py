"""
Unit tests for Forensic Accounting & Benford's Law Anomaly Engine.
"""
import pytest
import pandas as pd
from src.tools.forensic_auditor import ForensicAuditor

def test_extract_leading_digit():
    assert ForensicAuditor.extract_leading_digit(1234.5) == 1
    assert ForensicAuditor.extract_leading_digit(0.0056) == 5
    assert ForensicAuditor.extract_leading_digit(-987) == 9
    assert ForensicAuditor.extract_leading_digit(0) is None
    assert ForensicAuditor.extract_leading_digit("invalid") is None

def test_extract_second_digit():
    assert ForensicAuditor.extract_second_digit(1234.5) == 2
    assert ForensicAuditor.extract_second_digit(0.0056) == 6
    assert ForensicAuditor.extract_second_digit(-987) == 8
    assert ForensicAuditor.extract_second_digit(5) is None
    assert ForensicAuditor.extract_second_digit(0) is None

def test_benford_first_digit_insufficient_data():
    res = ForensicAuditor.test_benford_first_digit([10, 20, 30])
    assert res.sample_size == 3
    assert "Insufficient Data" in res.conformity_status
    assert not res.is_suspicious

def test_benford_first_digit_analysis():
    # Sequence of naturally scaling numbers
    numbers = [
        100, 110, 120, 130, 150, 180, 190,
        210, 240, 280, 310, 350, 420, 510,
        630, 750, 890, 920, 1100, 1400, 1800
    ]
    res = ForensicAuditor.test_benford_first_digit(numbers)
    assert res.sample_size == len(numbers)
    assert len(res.digit_distributions) == 9
    assert res.mean_absolute_deviation >= 0.0
    assert res.chi_square_stat >= 0.0
    assert isinstance(res.conformity_status, str)

def test_benford_second_digit_analysis():
    numbers = [
        105, 112, 128, 135, 142, 155, 168,
        205, 218, 225, 238, 245, 258, 265,
        310, 325, 340, 355, 370, 385, 395
    ]
    res = ForensicAuditor.test_benford_second_digit(numbers)
    assert res.sample_size == len(numbers)
    assert len(res.digit_distributions) == 10
    assert res.mean_absolute_deviation >= 0.0
    assert res.chi_square_stat >= 0.0
    assert isinstance(res.conformity_status, str)

def test_audit_tabular_data():
    data = {
        "Segment": ["A", "B", "C", "D", "E"],
        "Revenue_Q1": [500.0, 300.0, 200.0, 150.0, 80.0],
        "Revenue_Q2": [420.0, 280.0, 200.0, 140.0, 90.0],
        "Notes": ["Ok", "Ok", "Pending", "Ok", "Review"]
    }
    df = pd.DataFrame(data)
    report = ForensicAuditor.audit_tabular_data(df)
    assert report.total_numbers_audited == 10
    assert report.benford_first_digit is not None
    assert report.benford_second_digit is not None
    assert isinstance(report.overall_risk_score, float)
    assert 0.0 <= report.overall_risk_score <= 1.0

