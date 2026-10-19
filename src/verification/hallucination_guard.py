"""
Autonomous Reflection & Hallucination Guardrail Engine.
Performs real-time factual and mathematical verification on agent-generated claims,
computes faithfulness metrics, flags hallucinated figures, and provides corrective reflections.
"""
import re
from typing import Any, Optional
from pydantic import BaseModel, Field
from src.ingestion.metadata import ExtractedChunk
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary

class PropositionAudit(BaseModel):
    statement: str
    extracted_numbers: list[float]
    is_grounded: bool
    grounding_source: Optional[str] = None
    confidence_score: float = 1.0
    notes: str = ""

class HallucinationGuardResult(BaseModel):
    total_claims_audited: int
    grounded_claims_count: int
    unsupported_claims_count: int
    faithfulness_score: float  # 0.0 to 1.0 (RAGAS-compatible)
    hallucination_rate: float  # 0.0 to 1.0
    audit_verdict: str         # "VERIFIED_FAITHFUL", "BORDERLINE_ATTENTION", "HALLUCINATION_DETECTED"
    claim_audits: list[PropositionAudit]
    unsupported_claims: list[str]
    requires_reflection: bool
    reflection_guidance: Optional[str] = None

class HallucinationGuard:
    """
    Deterministic Verification Guardrail that evaluates whether claims are strictly grounded
    in retrieved chunks or deterministic math outputs.
    """

    def __init__(self, faithfulness_threshold: float = 0.90):
        self.threshold = faithfulness_threshold

    @staticmethod
    def extract_numbers_from_text(text: str) -> list[float]:
        """Extracts numerical tokens from text, handling currencies, commas, and decimals."""
        # Find numeric sequences like 1,000, 900.5, 420, 10.0%, etc.
        cleaned = text.replace(",", "")
        pattern = r"[-+]?\d+(?:\.\d+)?"
        matches = re.findall(pattern, cleaned)
        numbers = []
        for m in matches:
            try:
                val = float(m)
                numbers.append(val)
            except ValueError:
                pass
        return numbers

    def audit_claims(
        self,
        claims: list[str],
        evidence_chunks: list[ExtractedChunk],
        period_result: Optional[PeriodComparisonResult] = None,
        segment_summary: Optional[SegmentAnalysisSummary] = None
    ) -> HallucinationGuardResult:
        """
        Audits a list of natural language statements against ground truth math models and evidence chunks.
        """
        if not claims:
            return HallucinationGuardResult(
                total_claims_audited=0,
                grounded_claims_count=0,
                unsupported_claims_count=0,
                faithfulness_score=1.0,
                hallucination_rate=0.0,
                audit_verdict="VERIFIED_FAITHFUL",
                claim_audits=[],
                unsupported_claims=[],
                requires_reflection=False,
                reflection_guidance=None
            )

        # Collect ground-truth numbers from verified calculation results
        verified_numbers: set[float] = set()
        if period_result:
            verified_numbers.add(round(period_result.period_1_value, 2))
            verified_numbers.add(round(period_result.period_2_value, 2))
            verified_numbers.add(round(period_result.absolute_change, 2))
            verified_numbers.add(round(abs(period_result.absolute_change), 2))
            if period_result.percentage_change is not None:
                verified_numbers.add(round(period_result.percentage_change, 2))
                verified_numbers.add(round(abs(period_result.percentage_change), 2))

        if segment_summary:
            verified_numbers.add(round(segment_summary.total_period_1, 2))
            verified_numbers.add(round(segment_summary.total_period_2, 2))
            verified_numbers.add(round(segment_summary.total_absolute_change, 2))
            for s in segment_summary.segments:
                verified_numbers.add(round(s.period_1_value, 2))
                verified_numbers.add(round(s.period_2_value, 2))
                verified_numbers.add(round(s.absolute_change, 2))
                verified_numbers.add(round(abs(s.absolute_change), 2))
                if s.contribution_percentage is not None:
                    verified_numbers.add(round(s.contribution_percentage, 2))

        # Aggregate evidence chunk text
        combined_evidence_text = " ".join([c.content.replace(",", "") for c in evidence_chunks]).lower()

        audited_propositions: list[PropositionAudit] = []
        unsupported: list[str] = []

        for statement in claims:
            clean_stmt = statement.strip()
            if not clean_stmt:
                continue

            nums = self.extract_numbers_from_text(clean_stmt)
            is_grounded = True
            source_match = "Semantic evidence alignment"
            unsupported_reasons = []

            if nums:
                # If statement makes numerical assertions, verify each number against ground truth
                for n in nums:
                    rounded_n = round(n, 2)
                    # Check if number is in deterministic results
                    in_math = rounded_n in verified_numbers or abs(rounded_n) in verified_numbers
                    # Check if number is in raw chunk text
                    in_text = (str(int(n)) in combined_evidence_text if n.is_integer() else f"{n}" in combined_evidence_text)
                    
                    if not (in_math or in_text):
                        is_grounded = False
                        unsupported_reasons.append(f"Number {n} not found in deterministic math or evidence chunks.")

            # If no numbers, check key tokens against evidence text
            if not nums:
                words = [w.lower() for w in re.findall(r"\b[A-Za-z]{4,}\b", clean_stmt)]
                matches = sum(1 for w in words if w in combined_evidence_text)
                ratio = matches / len(words) if words else 1.0
                if ratio < 0.35:
                    is_grounded = False
                    unsupported_reasons.append(f"Narrative claim lacks corroborating tokens in retrieved evidence (overlap ratio: {ratio:.2f}).")

            if is_grounded:
                if nums:
                    source_match = "Deterministic Engine & Verified Tables"
                notes = "Claim is strictly verified and supported by source ground truth."
            else:
                unsupported.append(clean_stmt)
                notes = "; ".join(unsupported_reasons)

            audited_propositions.append(PropositionAudit(
                statement=clean_stmt,
                extracted_numbers=nums,
                is_grounded=is_grounded,
                grounding_source=source_match if is_grounded else None,
                confidence_score=1.0 if is_grounded else 0.2,
                notes=notes
            ))

        total_audited = len(audited_propositions)
        grounded_count = sum(1 for p in audited_propositions if p.is_grounded)
        unsupported_count = total_audited - grounded_count

        faithfulness = round(grounded_count / total_audited, 4) if total_audited > 0 else 1.0
        hallucination_rate = round(1.0 - faithfulness, 4)

        if faithfulness >= self.threshold:
            verdict = "VERIFIED_FAITHFUL"
            req_reflection = False
            reflection_msg = None
        elif faithfulness >= 0.70:
            verdict = "BORDERLINE_ATTENTION"
            req_reflection = True
            reflection_msg = (
                f"Agent detected {unsupported_count} unverified claim(s). "
                f"Faithfulness score ({faithfulness*100:.1f}%) is below optimal threshold ({self.threshold*100:.0f}%). "
                f"Please review unsupported statements and verify numbers."
            )
        else:
            verdict = "HALLUCINATION_DETECTED"
            req_reflection = True
            reflection_msg = (
                f"CRITICAL: High hallucination rate ({hallucination_rate*100:.1f}%). "
                f"{unsupported_count} statement(s) contain numbers or claims absent from ingested documents and math models. "
                f"Automated self-correction reflection triggered."
            )

        return HallucinationGuardResult(
            total_claims_audited=total_audited,
            grounded_claims_count=grounded_count,
            unsupported_claims_count=unsupported_count,
            faithfulness_score=faithfulness,
            hallucination_rate=hallucination_rate,
            audit_verdict=verdict,
            claim_audits=audited_propositions,
            unsupported_claims=unsupported,
            requires_reflection=req_reflection,
            reflection_guidance=reflection_msg
        )
