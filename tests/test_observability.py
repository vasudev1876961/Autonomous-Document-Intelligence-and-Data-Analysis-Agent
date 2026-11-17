"""
Unit and Integration Tests for Pillar 5: Enterprise Observability & Prometheus Telemetry.
Validates metric registration, latency quantiles, token tracking, standard Prometheus
exposition formatting, and REST API observability endpoints.
"""
import pytest
from src.observability.metrics import ObservabilityRegistry, prometheus_metrics


def test_observability_registry_singleton():
    """Validates thread-safe singleton design of ObservabilityRegistry."""
    r1 = ObservabilityRegistry()
    r2 = ObservabilityRegistry()
    assert r1 is r2
    assert r1 is prometheus_metrics


def test_metrics_recording():
    """Tests incrementing metrics across requests, agent steps, tokens, and errors."""
    registry = ObservabilityRegistry()
    
    registry.record_request("GET", "/health", 200, 0.015)
    registry.record_request("POST", "/api/v1/investigate", 200, 0.250)
    registry.record_agent_step("node_ingest", "success")
    registry.record_agent_step("node_analyze", "success")
    registry.record_tokens("gpt-4o", prompt_tokens=150, completion_tokens=85)
    registry.record_retrieval("hybrid")
    registry.record_calculation_error("dupont_analysis")

    summary = registry.get_summary()
    assert summary["total_http_requests"] >= 2
    assert summary["average_latency_ms"] > 0
    assert "node_ingest:success" in summary["agent_step_counts"]
    assert "gpt-4o:prompt" in summary["token_usage"]
    assert summary["retrieval_queries"]["hybrid"] >= 1
    assert summary["calculation_errors"]["dupont_analysis"] >= 1


def test_prometheus_exposition_format():
    """Verifies standard Prometheus RFC 0.0.4 text output with valid metadata headers."""
    registry = ObservabilityRegistry()
    registry.record_request("GET", "/api/v1/forensics/benford", 200, 0.045)
    
    text = registry.generate_prometheus_exposition()
    assert "# HELP adida_process_uptime_seconds" in text
    assert "# TYPE adida_process_uptime_seconds gauge" in text
    assert "# HELP adida_http_requests_total" in text
    assert "# TYPE adida_http_requests_total counter" in text
    assert "# HELP adida_http_request_duration_seconds" in text
    assert "adida_http_requests_total{endpoint=" in text
    assert text.endswith("\n")


def test_api_metrics_and_stats_endpoints():
    """Tests /metrics and /api/v1/observability/stats FastAPI endpoints."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)

    # 1. Test /metrics Prometheus scraper format
    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "text/plain" in res_metrics.headers["content-type"]
    assert "adida_process_uptime_seconds" in res_metrics.text
    assert "adida_http_requests_total" in res_metrics.text

    # 2. Test /api/v1/observability/stats JSON format
    res_stats = client.get("/api/v1/observability/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert "uptime_seconds" in stats
    assert "active_requests" in stats
    assert "total_http_requests" in stats
    assert "average_latency_ms" in stats
    assert stats["total_http_requests"] >= 1
