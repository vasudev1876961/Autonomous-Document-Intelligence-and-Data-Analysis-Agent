"""
Unified Verification Pipeline: Combines calculation, citation, and consistency audits into a structured report.
"""
from typing import Optional
from pydantic import BaseModel, Field
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary
from src.verification.calculation_checks import CalculationVerifier, CalculationVerificationResult
from src.verification.citation_checks import CitationVerifier, CitationCheckResult
from src.verification.consistency_checks import ConsistencyVerifier, ConsistencyCheckResult

class VerificationAuditReport(BaseModel):
    all_checks_passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    calculation_checks: list[CalculationVerificationResult] = Field(default_factory=list)
    citation_checks: list[CitationCheckResult] = Field(default_factory=list)
    consistency_checks: list[ConsistencyCheckResult] = Field(default_factory=list)
    summary_verdict: str

class VerificationPipeline:
    def __init__(self, documents: list[DocumentMetadata], chunks: list[ExtractedChunk]):
        self.documents = documents
        self.chunks = chunks
        self.citation_verifier = CitationVerifier(documents, chunks)

    def run_full_verification(
        self,
        period_result: Optional[PeriodComparisonResult] = None,
        segment_summary: Optional[SegmentAnalysisSummary] = None,
        citations_to_check: Optional[list[dict[str, str]]] = None,
        unit_pairs: Optional[list[tuple[str, str]]] = None,
    ) -> VerificationAuditReport:
        calc_results: list[CalculationVerificationResult] = []
        cite_results: list[CitationCheckResult] = []
        cons_results: list[ConsistencyCheckResult] = []

        # 1. Calculation recomputation
        if period_result:
            calc_results.extend(CalculationVerifier.verify_period_comparison(period_result))
        if segment_summary:
            calc_results.extend(CalculationVerifier.verify_segment_analysis(segment_summary))

        # 2. Citation checks
        if citations_to_check:
            for item in citations_to_check:
                res = self.citation_verifier.verify_citation(
                    file_name=item.get("file_name", ""),
                    page_or_sheet=item.get("page_or_sheet"),
                    key_term=item.get("key_term")
                )
                cite_results.append(res)

        # 3. Consistency checks
        if unit_pairs:
            for u1, u2 in unit_pairs:
                cons_results.append(ConsistencyVerifier.check_units(u1, u2))

        # Tally
        total = len(calc_results) + len(cite_results) + len(cons_results)
        passed = (
            sum(1 for c in calc_results if c.is_valid) +
            sum(1 for c in cite_results if c.is_valid) +
            sum(1 for c in cons_results if c.is_consistent)
        )
        failed = total - passed
        all_passed = (failed == 0)

        verdict = (
            f"PASSED: All {total} independent verification audits succeeded without errors."
            if all_passed else
            f"AUDIT WARNING: {failed} of {total} verification checks failed or require clarification."
        )

        return VerificationAuditReport(
            all_checks_passed=all_passed,
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            calculation_checks=calc_results,
            citation_checks=cite_results,
            consistency_checks=cons_results,
            summary_verdict=verdict
        )
