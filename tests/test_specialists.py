"""
Unit tests for specialized multi-agent framework:
- PlannerSpecialist
- RetrievalSpecialist
- AnalyticalSpecialist
- VerificationAuditor
- SupervisorAgent
"""
import pytest
from src.agent.specialists import (
    PlannerSpecialist,
    RetrievalSpecialist,
    AnalyticalSpecialist,
    VerificationAuditor,
    SupervisorAgent
)
from src.tools.source_reconciliation import SourceClaim
from src.ingestion.metadata import SourceLocation, FileType

def test_planner_specialist():
    planner = PlannerSpecialist()
    plan = planner.create_investigation_plan("Analyze revenue decline")
    assert len(plan) == 10
    assert plan[0].step_id == "step_1_inventory"

    adapted = planner.adapt_plan_on_evidence_gap(plan, "Segment B drivers", "missing root cause")
    assert len(adapted) == 11
    assert any(s.step_id == "step_2b_targeted_reinvestigation" for s in adapted)

def test_analytical_specialist():
    quant = AnalyticalSpecialist()
    p_res = quant.compute_period_comparison("Revenue", 1000.0, 900.0)
    assert p_res.absolute_change == -100.0
    assert p_res.percentage_change == -10.0

    segments_data = [
        {"segment": "Segment A", "p1": 500, "p2": 420},
        {"segment": "Segment B", "p1": 300, "p2": 280},
        {"segment": "Segment C", "p1": 200, "p2": 200},
    ]
    s_summary = quant.compute_segment_breakdown("Revenue", segments_data)
    assert s_summary.reconciled_with_total is True

    adv = quant.compute_advanced_analytics("Revenue", s_summary, budget_target=950.0)
    assert "statistics" in adv
    assert "outliers" in adv
    assert "budget_variance" in adv
    assert adv["budget_variance"].variance_amount == -50.0

def test_supervisor_hitl_escalation():
    supervisor = SupervisorAgent()
    loc = SourceLocation(document_id="d1", file_name="f1.pdf", file_type=FileType.PDF)
    
    # Matching claims (no conflict)
    claims_ok = [
        SourceClaim(metric_name="Revenue", period="Q2", reported_value=900.0, unit="₹ lakh", source_location=loc, document_name="Doc1"),
        SourceClaim(metric_name="Revenue", period="Q2", reported_value=900.0, unit="₹ lakh", source_location=loc, document_name="Doc2"),
    ]
    engine = supervisor.quant
    from src.tools.source_reconciliation import SourceReconciliationEngine
    recon_ok = SourceReconciliationEngine().reconcile_claims(claims_ok)
    req_none = supervisor.evaluate_conflict_for_hitl("task_123", recon_ok)
    assert req_none is None

    # Conflicting claims (900 vs 905)
    claims_conflict = [
        SourceClaim(metric_name="Revenue", period="Q2", reported_value=900.0, unit="₹ lakh", source_location=loc, document_name="Audited.pdf"),
        SourceClaim(metric_name="Revenue", period="Q2", reported_value=905.0, unit="₹ lakh", source_location=loc, document_name="Draft.pdf"),
    ]
    recon_conflict = SourceReconciliationEngine(material_threshold_pct=0.5).reconcile_claims(claims_conflict)
    req = supervisor.evaluate_conflict_for_hitl("task_123", recon_conflict)
    assert req is not None
    assert req.task_id == "task_123"
    assert len(req.options) == 3
