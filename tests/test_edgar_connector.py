"""
Unit and Integration Tests for Pillar 4: SEC EDGAR, XBRL & Macroeconomic Data Connectors.
Tests standardized US-GAAP taxonomy extraction, balance sheet & income statement parsing,
macroeconomic benchmark contextualization, CLI, and REST APIs.
"""
import pytest
from src.ingestion.edgar_connector import (
    SECEDGARConnector,
    SECFilingManifest,
    SECFilingType,
    MacroBenchmarkData
)


def test_sec_edgar_canonical_ingestion():
    """Tests fetching canonical SEC 10-K filing for MSFT FY2024."""
    manifest, chunks = SECEDGARConnector.fetch_filing(
        ticker="MSFT",
        filing_type="10-K",
        fiscal_year=2024
    )

    assert isinstance(manifest, SECFilingManifest)
    assert manifest.ticker == "MSFT"
    assert manifest.company_name == "Microsoft Corporation"
    assert manifest.cik == "0000789019"
    assert manifest.fiscal_year == 2024
    assert manifest.facts_count >= 8

    # Check key US-GAAP line items
    inc = manifest.income_statement
    assert inc["Revenues"] == 245120000000.0
    assert inc["NetIncome"] == 88140000000.0

    bs = manifest.balance_sheet
    assert bs["TotalAssets"] == 512160000000.0
    assert bs["StockholdersEquity"] == 268470000000.0


def test_sec_edgar_chunks_for_rag():
    """Tests that SEC EDGAR connector emits properly structured ExtractedChunks for retrieval."""
    manifest, chunks = SECEDGARConnector.fetch_filing(
        ticker="AAPL",
        filing_type="10-K",
        fiscal_year=2024
    )

    assert len(chunks) == 2
    inc_chunk = chunks[0]
    assert inc_chunk.content_type == "xbrl_statement"
    assert "Apple Inc." in inc_chunk.content
    assert "$391,035,000,000.00 USD" in inc_chunk.content
    assert inc_chunk.location.file_name == "AAPL_10-K_2024.json"
    assert inc_chunk.reporting_period == "FY2024"


def test_macro_benchmark_data():
    """Tests retrieving macroeconomic benchmark metrics (Treasury rates, inflation, GDP)."""
    macro_2024 = SECEDGARConnector.get_macro_benchmark(2024)
    assert isinstance(macro_2024, MacroBenchmarkData)
    assert macro_2024.fiscal_year == 2024
    assert macro_2024.risk_free_rate_10y_pct == 4.25
    assert macro_2024.us_cpi_inflation_pct == 2.90
    assert macro_2024.gdp_real_growth_pct == 2.80

    macro_2023 = SECEDGARConnector.get_macro_benchmark(2023)
    assert macro_2023.risk_free_rate_10y_pct == 3.88


def test_api_sec_endpoints():
    """Tests REST API endpoints for SEC filing and macroeconomic benchmarks."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)

    # 1. SEC Filing
    res1 = client.get("/api/v1/sec/filing?ticker=MSFT&year=2024&filing_type=10-K")
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["manifest"]["ticker"] == "MSFT"
    assert d1["manifest"]["income_statement"]["Revenues"] == 245120000000.0
    assert d1["chunks_generated"] == 2

    # 2. Macro Benchmark
    res2 = client.get("/api/v1/sec/macro-benchmark?year=2024")
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["fiscal_year"] == 2024
    assert d2["risk_free_rate_10y_pct"] == 4.25
