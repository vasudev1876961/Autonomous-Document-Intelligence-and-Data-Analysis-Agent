"""
Unit tests for ReportExporter interactive HTML and JSON audit pack generation.
"""
import json
import pytest
from pathlib import Path
from src.tools.report_export import ReportExporter
from src.agent.state import AgentState

def test_export_interactive_html(tmp_path):
    exporter = ReportExporter(output_dir=tmp_path)
    report_md = """# Autonomous Investigation Report
## 1. Executive Summary
Revenue declined from Q1 to Q2 by 10.0%.

| Metric | Q1 | Q2 | Delta |
|---|---|---|---|
| Revenue | 1000 | 900 | -100 |

- [FACT] Revenue dropped by 100 lakh.
- [SUPPORTED] Segment A was the primary contributor.
- [UNCERTAINTY] Price elasticity was not disclosed.
"""
    html_path = exporter.export_interactive_html(
        title="Test Executive Report",
        report_markdown=report_md,
        filename="test_report.html"
    )
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Test Executive Report" in content
    assert "OBSERVED FACT" in content
    assert "table" in content

def test_export_audit_pack(tmp_path):
    exporter = ReportExporter(output_dir=tmp_path)
    state = AgentState(
        task_id="task_test_123",
        user_goal="Explain quarterly variance",
        is_completed=True
    )
    pack_path = exporter.export_audit_pack(state, filename="test_audit_pack.json")
    assert pack_path.exists()
    data = json.loads(pack_path.read_text(encoding="utf-8"))
    assert data["audit_pack_version"] == "4.0.0"
    assert data["task_id"] == "task_test_123"
    assert data["status"] == "COMPLETED_AND_VERIFIED"
    assert "deterministic_math_ledger" in data
