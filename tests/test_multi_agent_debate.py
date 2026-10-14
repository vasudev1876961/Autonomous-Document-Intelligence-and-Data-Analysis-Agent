"""
Unit tests for the Multi-Agent Red-Team Debate Council.
"""
from src.agent.debate import MultiAgentDebateCouncil
from src.tools.numerical_analysis import NumericalAnalyzer

def test_debate_council_execution():
    council = MultiAgentDebateCouncil()
    sample_segs = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segs, "₹ lakh")
    p_res = NumericalAnalyzer.compare_periods("Revenue", 1000.0, 900.0, "Q1", "Q2", "₹ lakh")
    
    session = council.run_debate(
        goal="Explain revenue decline from Q1 to Q2",
        period_res=p_res,
        seg_summary=seg_summary,
        reconciliation=None,
        evidence_chunks=[]
    )
    
    assert len(session.rounds) == 5
    assert session.rounds[0].speaker_role == "Quantitative Analyst"
    assert session.rounds[1].speaker_role == "Retrieval Specialist"
    assert session.rounds[2].speaker_role == "Red-Team Auditor"
    assert session.rounds[3].speaker_role == "Quantitative Analyst"
    assert session.rounds[4].speaker_role == "Executive Supervisor"

    
    # Verdict verification
    assert session.verdict is not None
    assert session.verdict.consensus_reached is True
    assert session.verdict.confidence_score >= 0.90
    assert len(session.verdict.agreed_facts) >= 3
