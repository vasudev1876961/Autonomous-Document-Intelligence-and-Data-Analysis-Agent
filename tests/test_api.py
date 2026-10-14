"""
Integration tests for the Enterprise FastAPI REST Microservice.
"""
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_api_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "3.0.0"
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
