"""
Integration tests for the Enterprise FastAPI REST Microservice.
"""
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.server import app
from src.tools.report_export import ReportExporter

client = TestClient(app)

def test_api_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "4.1.0"
    assert data["deterministic_math"] is True

def test_api_scenarios_simulation():
    payload = {
        "scenario_name": "Test Segment A Flat",
        "overrides": {"Segment A": 500.0},
        "target_revenue": 1000.0,
        "num_simulations": 200
    }
    response = client.post("/api/v1/scenarios/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "counterfactual" in data
    assert data["counterfactual"]["simulated_period_2_total"] == 980.0
    assert "recovery_plan" in data
    assert "monte_carlo" in data
    assert data["monte_carlo"]["num_simulations"] == 200

def test_api_multi_agent_debate():
    response = client.post("/api/v1/debate?goal=Explain+revenue+decline")
    assert response.status_code == 200
    data = response.json()
    assert len(data["rounds"]) == 5
    assert data["verdict"]["consensus_reached"] is True

def test_api_hitl_queue():
    response = client.get("/api/v1/hitl/queue")
    assert response.status_code == 200
    data = response.json()
    assert "pending_count" in data
    assert "requests" in data

def test_api_benford_audit():
    payload = {"numbers": [120, 140, 210, 280, 310, 420, 510, 650, 780, 890, 1100, 1500]}
    response = client.post("/api/v1/forensics/benford", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sample_size"] == 12
    assert "mean_absolute_deviation" in data
    assert "conformity_status" in data

def test_api_benford_second_digit_audit():
    payload = {"numbers": [105, 115, 125, 135, 145, 155, 165, 175, 185, 195, 205, 215]}
    response = client.post("/api/v1/forensics/benford-second-digit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sample_size"] == 12
    assert len(data["digit_distributions"]) == 10
    assert "mean_absolute_deviation" in data

def test_api_benford_first_two_digits_audit():
    numbers = [
        105, 115, 125, 135, 145, 155, 165, 175, 185, 195,
        205, 215, 225, 235, 245, 255, 265, 275, 285, 295, 310
    ]
    payload = {"numbers": numbers}
    response = client.post("/api/v1/forensics/benford-first-two-digits", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sample_size"] == len(numbers)
    assert len(data["digit_distributions"]) == 90
    assert "mean_absolute_deviation" in data

def test_api_dupont_analysis():
    payload = {
        "net_income": 150.0,
        "revenue": 1000.0,
        "total_assets": 2000.0,
        "total_equity": 500.0
    }
    response = client.post("/api/v1/analytics/dupont", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["net_profit_margin_pct"] == 15.0
    assert data["asset_turnover"] == 0.5
    assert data["equity_multiplier"] == 4.0
    assert data["roe_pct"] == 30.0
    assert data["is_mathematically_proven"] is True

def test_api_financial_ratios():
    payload = {
        "revenue": 1000.0,
        "cost_of_goods_sold": 600.0,
        "operating_income": 200.0,
        "net_income": 140.0,
        "current_assets": 500.0,
        "current_liabilities": 250.0,
        "total_debt": 300.0,
        "total_equity": 700.0,
        "total_assets": 1200.0
    }
    response = client.post("/api/v1/analytics/financial-ratios", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["gross_margin_pct"] == 40.0
    assert data["operating_margin_pct"] == 20.0
    assert data["current_ratio"] == 2.0
    assert data["liquidity_status"] == "robust"

def test_api_causal_shock():
    payload = {
        "root_node_id": "driver_supply_chain",
        "shock_pct": -12.5
    }
    response = client.post("/api/v1/knowledge-graph/causal-shock", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["root_node_id"] == "driver_supply_chain"
    assert len(data["impacted_entities"]) >= 1
    assert data["net_revenue_impact_pct"] is not None

def test_api_hallucination_guard():
    payload = {
        "claims": ["Revenue was 1000 lakh in Q1.", "Net profits doubled to 8888 lakh."],
        "context_text": "Revenue for Q1 was 1000 lakh."
    }
    response = client.post("/api/v1/verification/hallucination-guard", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_claims_audited"] == 2
    assert "faithfulness_score" in data
