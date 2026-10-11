"""
End-to-end test of the Autonomous Document Intelligence Agent workflow.
Runs the exact revenue decline investigation scenario across sample documents.
"""
from pathlib import Path
import pytest
from src.agent.orchestrator import AgentOrchestrator

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_documents"

def test_full_agent_workflow():
    orchestrator = AgentOrchestrator()
    goal = "Explain why revenue declined from Q1 to Q2. Identify the main contributing segments and support the explanation with evidence."
    
    files = [
        SAMPLE_DIR / "Quarterly_Report.pdf",
        SAMPLE_DIR / "Revenue_Data.xlsx",
        SAMPLE_DIR / "Segment_Performance.csv"
    ]
    
    state = orchestrator.run_investigation(goal, files)

    # 1. State completed & verified
    assert state.is_completed is True
    assert len(state.document_manifest) == 3
    assert state.period_comparison is not None
    
    # 2. Mathematical outcome verified
    assert state.period_comparison.absolute_change == -100.0
    assert state.period_comparison.percentage_change == -10.0
    
    # 3. Segment contribution verified
    assert state.segment_analysis is not None
    seg_map = {s.segment_name: s for s in state.segment_analysis.segments}
    assert seg_map["Segment A"].contribution_percentage == 80.0
    assert seg_map["Segment B"].contribution_percentage == 20.0
    assert seg_map["Segment C"].contribution_percentage == 0.0

    # 4. Independent verification audit passed
    assert state.verification_audit is not None
    assert state.verification_audit.all_checks_passed is True

    # 5. Report deliverables exist
    assert state.report_markdown_path is not None
    assert Path(state.report_markdown_path).exists()
    assert state.report_pdf_path is not None
    assert Path(state.report_pdf_path).exists()

    # 6. Check that Segment A has narrative reason and Segment B has uncertainty disclosure
    assert any("Segment A" in fact for fact in state.observed_facts)
    assert any("Segment A" in interp for interp in state.supported_interpretations)
    assert any("Segment B" in unc for unc in state.unresolved_questions)
