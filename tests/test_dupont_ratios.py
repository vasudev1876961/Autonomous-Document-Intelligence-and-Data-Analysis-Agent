"""
Unit tests for DuPont ROE Analysis, Financial Ratios, and Non-Parametric IQR Outliers.
"""
import pytest
from src.tools.numerical_analysis import NumericalAnalyzer

def test_dupont_analysis_exact_proof():
    # Case: Net Income = 150, Revenue = 1000, Total Assets = 2000, Total Equity = 500
    # Net Profit Margin = 150 / 1000 = 15.0%
    # Asset Turnover = 1000 / 2000 = 0.5x
    # Equity Multiplier = 2000 / 500 = 4.0x
    # Product ROE = 0.15 * 0.5 * 4.0 = 0.30 = 30.0%
    # Direct ROE = 150 / 500 = 30.0%
    res = NumericalAnalyzer.calculate_dupont_analysis(
        net_income=150.0,
        revenue=1000.0,
        total_assets=2000.0,
        total_equity=500.0
    )

    assert res.net_profit_margin_pct == 15.0
    assert res.asset_turnover == 0.5
    assert res.equity_multiplier == 4.0
    assert res.roe_pct == 30.0
    assert res.reconciled_product_roe_pct == 30.0
    assert res.is_mathematically_proven is True
    assert res.proof_discrepancy < 0.001
    assert "Net Profit Margin: 15.00%" in res.driver_breakdown

def test_financial_ratios():
    res = NumericalAnalyzer.calculate_financial_ratios(
        revenue=1200.0,
        cost_of_goods_sold=720.0,
        operating_income=240.0,
        net_income=180.0,
        current_assets=600.0,
        current_liabilities=300.0,
        inventory=100.0,
        total_debt=400.0,
        total_equity=800.0,
        total_assets=1500.0
    )

    assert res.gross_margin_pct == 40.0  # (1200 - 720) / 1200 * 100
    assert res.operating_margin_pct == 20.0  # 240 / 1200 * 100
    assert res.net_profit_margin_pct == 15.0  # 180 / 1200 * 100
    assert res.current_ratio == 2.0  # 600 / 300
    assert res.quick_ratio == 1.67  # (600 - 100) / 300
    assert res.debt_to_equity == 0.5  # 400 / 800
    assert res.asset_turnover == 0.8  # 1200 / 1500
    assert res.return_on_assets_pct == 12.0  # 180 / 1500 * 100
    assert res.liquidity_status == "robust"
    assert res.solvency_status == "strong"

def test_iqr_outliers():
    # Normal distribution with two extreme outliers
    values = [10.0, 11.0, 12.0, 11.5, 10.5, 12.5, 11.2, 11.8, 95.0, -40.0]
    res = NumericalAnalyzer.detect_outliers_iqr("Testing Series", values, multiplier=1.5)

    assert res.has_outliers is True
    outliers = [item for item in res.outliers_detected if item.is_outlier]
    assert len(outliers) == 2
    assert any(o.value == 95.0 and o.is_upper_outlier for o in outliers)
    assert any(o.value == -40.0 and o.is_lower_outlier for o in outliers)

