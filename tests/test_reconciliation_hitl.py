"""
Unit tests for Cross-Document Reconciliation and Human-in-the-Loop Review Queue.
"""
import pytest
from src.human_review.approval import ApprovalDecision, RiskLevel
from src.human_review.review_queue import ReviewQueue
from src.tools.source_reconciliation import SourceReconciliationEngine, SourceClaim
from src.ingestion.metadata import SourceLocation, FileType

def test_source_reconciliation_engine():
    loc1 = SourceLocation(document_id="doc1", file_name="Quarterly_Report.pdf", file_type=FileType.PDF, page_number=1)
    loc2 = SourceLocation(document_id="doc2", file_name="Conflicting_Report.pdf", file_type=FileType.PDF, page_number=1)

    claims = [
        SourceClaim(metric_name="Revenue", period="Q2", reported_value=900.0, unit="₹ lakh", source_location=loc1, document_name="Quarterly_Report.pdf"),
        SourceClaim(metric_name="Revenue", period="Q2", reported_value=905.0, unit="₹ lakh", source_location=loc2, document_name="Conflicting_Report.pdf"),
    ]

    engine = SourceReconciliationEngine(material_threshold_pct=0.5)
    summary = engine.reconcile_claims(claims)

    assert summary.total_comparisons == 1
    assert summary.discrepancy_count == 1
    assert summary.has_blocking_conflicts is True
    assert summary.material_conflicts[0].absolute_difference == 5.0
    assert summary.material_conflicts[0].percentage_difference > 0.5

def test_review_queue_lifecycle():
    queue = ReviewQueue()
    req = queue.create_request(
        request_id="req_test_01",
        task_id="task_001",
        risk_level=RiskLevel.HIGH,
        action_type="reconcile_conflict",
        title="Revenue Conflict",
        description="900 vs 905 lakh",
        proposed_action="Select audited filing",
        options=["Audited (900)", "Draft (905)"]
    )

    assert req.decision == ApprovalDecision.PENDING
    pending = queue.get_pending_requests(task_id="task_001")
    assert len(pending) == 1

    # Submit human decision
    decided = queue.submit_decision(
        request_id="req_test_01",
        decision=ApprovalDecision.APPROVE,
        selected_option="Audited (900)",
        comments="Confirmed with finance department",
        decided_by="Senior Analyst"
    )

    assert decided.decision == ApprovalDecision.APPROVE
    assert decided.selected_option == "Audited (900)"
    assert len(queue.get_pending_requests(task_id="task_001")) == 0
