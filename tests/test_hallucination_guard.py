"""
Unit tests for HallucinationGuard reflection engine.
"""
import pytest
from src.ingestion.metadata import ExtractedChunk, SourceLocation, FileType
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary, SegmentContributionResult
from src.verification.hallucination_guard import HallucinationGuard

@pytest.fixture
def sample_context():
    chunk = ExtractedChunk(
        chunk_id="ch_1",
        document_id="doc_1",
        file_name="Quarterly_Report.pdf",
        content="Revenue for Q1 was 1000 lakh and Q2 declined to 900 lakh. Segment A dropped from 500 to 420 lakh.",
        content_type="text",
        location=SourceLocation(
            document_id="doc_1",
            file_name="Quarterly_Report.pdf",
            file_type=FileType.PDF,
            page_number=1
        )
    )
    p_res = PeriodComparisonResult(
        metric_name="Revenue",
        period_1_name="Q1",
        period_1_value=1000.0,
        period_2_name="Q2",
        period_2_value=900.0,
        unit="₹ lakh",
        absolute_change=-100.0,
        percentage_change=-10.0,
        direction="decrease",
        formula_used="%ΔR = ((R2 - R1) / R1) * 100"
    )
    s_res = SegmentAnalysisSummary(
        metric_name="Revenue",
        unit="₹ lakh",
        total_period_1=1000.0,
        total_period_2=900.0,
        total_absolute_change=-100.0,
        total_percentage_change=-10.0,
        segments=[
            SegmentContributionResult(
                segment_name="Segment A",
                period_1_value=500.0,
                period_2_value=420.0,
                absolute_change=-80.0,
                contribution_percentage=80.0,
                direction="decrease"
            )
        ],
        reconciled_with_total=True
    )
    return [chunk], p_res, s_res

def test_hallucination_guard_grounded_claims(sample_context):
    chunks, p_res, s_res = sample_context
    guard = HallucinationGuard(faithfulness_threshold=0.90)
    claims = [
        "Revenue declined by 100 lakh from 1000 lakh in Q1 to 900 lakh in Q2.",
        "Segment A experienced a drop of 80 lakh, contributing 80.0% of the decline."
    ]
    res = guard.audit_claims(claims=claims, evidence_chunks=chunks, period_result=p_res, segment_summary=s_res)
    assert res.total_claims_audited == 2
    assert res.faithfulness_score == 1.0
    assert res.hallucination_rate == 0.0
    assert res.audit_verdict == "VERIFIED_FAITHFUL"
    assert not res.requires_reflection

def test_hallucination_guard_detected_hallucination(sample_context):
    chunks, p_res, s_res = sample_context
    guard = HallucinationGuard(faithfulness_threshold=0.90)
    claims = [
        "Revenue declined by 100 lakh from 1000 lakh to 900 lakh.",
        "Fabricated profit of 99999 lakh was reported in unknown quarter."
    ]
    res = guard.audit_claims(claims=claims, evidence_chunks=chunks, period_result=p_res, segment_summary=s_res)
    assert res.total_claims_audited == 2
    assert res.grounded_claims_count == 1
    assert res.unsupported_claims_count == 1
    assert res.faithfulness_score == 0.50
    assert res.requires_reflection
