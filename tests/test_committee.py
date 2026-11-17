"""
Unit and Integration Tests for Pillar 1: Autonomous Financial & Audit Committee (Adversarial Swarm).
Tests the 5 specialist agents, multi-round debate protocol, quantitative consensus scoring,
and automatic Human-in-the-Loop (HITL) escalation when disagreement exceeds 15%.
"""
import pytest
from src.agent.committee import (
    AutonomousAuditCommittee,
    ForensicAuditorAgent,
    QuantitativeAnalystAgent,
    CrossDocumentReconcilerAgent,
    AdversarialRedTeamAgent,
    ChiefRiskOfficerAgent,
    AgentRole,
    FindingRisk,
)
from src.tools.source_reconciliation import SourceClaim
from src.human_review.review_queue import ReviewQueue
from src.ingestion.metadata import SourceLocation, FileType


def test_committee_clean_consensus():
    """Tests clean scenario where findings align and consensus confidence >= 85% with no HITL blocking."""
    committee = AutonomousAuditCommittee(disagreement_threshold=0.15)
    period_data = {
        "metric": "Revenue",
        "p1": 1000.0,
        "p2": 900.0,
        "p1_name": "Q1",
        "p2_name": "Q2",
        "unit": "₹ lakh"
    }
    sample_segments = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    dupont = {
        "net_income": 120.0,
        "revenue": 900.0,
        "total_assets": 1500.0,
        "total_equity": 800.0
    }

    session = committee.convene_committee(
        task_id="test_task_clean",
        goal="Audit Q1 to Q2 revenue contraction and return on equity.",
        period_data=period_data,
        segment_data=sample_segments,
        dupont_data=dupont
    )

    assert session.session_id.startswith("comm_")
    assert len(session.debate_rounds) >= 5
    assert session.verdict is not None
    assert session.verdict.consensus_confidence_score >= 0.85
    assert session.verdict.disagreement_rate <= 0.15
    assert session.verdict.requires_hitl is False
    assert "APPROVED" in session.verdict.risk_posture
    assert len(session.verdict.agreed_facts) >= 2


def test_committee_dupont_mathematical_identity():
    """Tests that the QuantitativeAnalystAgent calculates DuPont 3-stage ROE and proves Margin x Turnover x Leverage = ROE."""
    agent = QuantitativeAnalystAgent()
    finding = agent.evaluate(
        goal="Audit DuPont return on equity",
        dupont_data={
            "net_income": 150.0,
            "revenue": 1000.0,
            "total_assets": 2000.0,
            "total_equity": 1000.0
        }
    )

    assert finding.role == AgentRole.QUANTITATIVE_ANALYST
    assert "dupont_analysis" in finding.evidence_payload
    dp = finding.evidence_payload["dupont_analysis"]
    assert dp["is_mathematically_proven"] is True
    assert dp["net_profit_margin_pct"] == 15.0
    assert dp["asset_turnover"] == 0.5
    assert dp["equity_multiplier"] == 2.0
    assert dp["roe_pct"] == 15.0


def test_committee_material_conflict_hitl_escalation():
    """
    Tests that when conflicting claims are submitted from multiple documents,
    disagreement rate exceeds 15%, consensus is NOT achieved, and an ApprovalRequest is created in ReviewQueue.
    """
    rq = ReviewQueue()
    committee = AutonomousAuditCommittee(disagreement_threshold=0.15, review_queue=rq)

    loc1 = SourceLocation(document_id="doc1", file_name="Annual_Report_10K.pdf", file_type=FileType.PDF, page_number=14)
    loc2 = SourceLocation(document_id="doc2", file_name="Press_Release_Preliminary.pdf", file_type=FileType.PDF, page_number=1)

    claim_10k = SourceClaim(
        document_name="Annual_Report_10K.pdf",
        metric_name="Operating Revenue",
        period="FY2025",
        reported_value=900.0,
        unit="₹ lakh",
        source_location=loc1
    )
    claim_press = SourceClaim(
        document_name="Press_Release_Preliminary.pdf",
        metric_name="Operating Revenue",
        period="FY2025",
        reported_value=950.0,  # 5.5% material contradiction
        unit="₹ lakh",
        source_location=loc2
    )

    session = committee.convene_committee(
        task_id="test_task_conflict",
        goal="Reconcile revenue disclosures across filings.",
        source_claims=[claim_10k, claim_press]
    )

    assert session.verdict.consensus_reached is False
    assert session.verdict.requires_hitl is True
    assert session.verdict.risk_posture == "ESCALATED_TO_HITL"
    assert session.verdict.disagreement_rate > 0.15
    assert session.verdict.approval_request_id is not None

    # Verify that the review queue received the approval request
    req = rq.active_requests.get(session.verdict.approval_request_id)
    assert req is not None
    assert req.task_id == "test_task_conflict"
    assert "Autonomous Audit Committee Escalation" in req.title


def test_committee_forensic_anomalies_challenge():
    """Tests that ForensicAuditorAgent flags anomalies when numbers violate Benford and round clustering is excessive."""
    agent = ForensicAuditorAgent()
    # Artificial numbers all starting with 9 and heavily rounded to 000
    suspicious_numbers = [9000.0, 9000.0, 9100.0, 9200.0, 9000.0, 9500.0, 9800.0, 9900.0, 9000.0, 9100.0, 9000.0, 9400.0]
    finding = agent.evaluate(suspicious_numbers)

    assert finding.role == AgentRole.FORENSIC_AUDITOR
    assert finding.risk_level in [FindingRisk.MEDIUM, FindingRisk.HIGH]
    assert any("ROUND NUMBER CLUSTERING" in c or "REPEATED VALUES" in c for c in finding.claims)


def test_api_committee_debate_endpoint():
    """Tests the new REST API endpoint POST /api/v1/agent/committee-debate."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)
    payload = {
        "goal": "Audit revenue decline from Q1 to Q2 and test DuPont identity.",
        "period_data": {
            "metric": "Revenue",
            "p1": 1000.0,
            "p2": 900.0,
            "p1_name": "Q1",
            "p2_name": "Q2",
            "unit": "₹ lakh"
        },
        "segment_data": [
            {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
            {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
            {"segment": "Segment C", "p1": 200.0, "p2": 200.0}
        ],
        "dupont_data": {
            "net_income": 120.0,
            "revenue": 900.0,
            "total_assets": 1500.0,
            "total_equity": 800.0
        },
        "disagreement_threshold": 0.15
    }

    response = client.post("/api/v1/agent/committee-debate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "session_id" in data
    assert len(data["debate_rounds"]) >= 5
    assert len(data["specialist_findings"]) == 3
    assert data["verdict"]["consensus_confidence_score"] >= 0.85
    assert data["verdict"]["requires_hitl"] is False
