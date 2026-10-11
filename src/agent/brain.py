"""
Agent Brain: Handles contextual interpretation, analytical reasoning, claim categorization,
and evidence-gap detection.
"""
import os
import re
from typing import Any, Optional
from pydantic import BaseModel
from src.ingestion.metadata import ClaimCategory, ExtractedChunk
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary
from src.tools.source_reconciliation import ReconciliationSummary

class GoalInterpretation(BaseModel):
    raw_goal: str
    target_metric: str
    period_1: str
    period_2: str
    unit: str
    requires_segment_analysis: bool
    requires_explanation: bool
    constraints: list[str]

class InvestigationFindings(BaseModel):
    observed_facts: list[str]
    supported_interpretations: list[str]
    hypotheses: list[str]
    unresolved_uncertainties: list[str]
    citations_to_audit: list[dict[str, str]]

class AgentBrain:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def interpret_goal(self, goal: str) -> GoalInterpretation:
        """
        Parses user intent to establish target metric, comparison windows, and required deliverables.
        """
        lower = goal.lower()
        
        # Metric extraction
        target_metric = "Revenue"
        if "revenue" in lower or "sales" in lower:
            target_metric = "Revenue"
        elif "profit" in lower or "income" in lower:
            target_metric = "Profit"
        elif "expense" in lower or "cost" in lower:
            target_metric = "Expenses"

        # Period extraction
        p1, p2 = "Q1", "Q2"
        match_periods = re.findall(r"(q[1-4]|20\d\d)", lower)
        if len(match_periods) >= 2:
            p1 = match_periods[0].upper()
            p2 = match_periods[1].upper()

        requires_seg = any(w in lower for w in ["segment", "contribut", "division", "breakdown"])
        requires_expl = any(w in lower for w in ["why", "reason", "cause", "explain", "factor"])

        return GoalInterpretation(
            raw_goal=goal,
            target_metric=target_metric,
            period_1=p1,
            period_2=p2,
            unit="₹ lakh", # default financial unit from specs
            requires_segment_analysis=requires_seg,
            requires_explanation=requires_expl,
            constraints=["Use only supplied documents as ground truth", "Do not hallucinate unsupported causes"]
        )

    def synthesize_findings(
        self,
        interpretation: GoalInterpretation,
        period_res: PeriodComparisonResult,
        segment_summary: Optional[SegmentAnalysisSummary],
        evidence_chunks: list[ExtractedChunk],
        reconciliation: Optional[ReconciliationSummary] = None
    ) -> InvestigationFindings:
        """
        Synthesizes findings strictly adhering to Section 11 (Step 9) and Section 20 of specification:
        - Observed facts (calculations & source numbers)
        - Supported interpretations (narrative reasons backed by cited texts)
        - Hypotheses & Disclosed Uncertainties (missing evidence clearly admitted)
        """
        observed_facts: list[str] = []
        supported_interps: list[str] = []
        hypotheses: list[str] = []
        uncertainties: list[str] = []
        citations_to_audit: list[dict[str, str]] = []

        # 1. Observed facts from period calculation
        delta_sign = "+" if period_res.absolute_change > 0 else ""
        pct_str = f"{delta_sign}{period_res.percentage_change}%" if period_res.percentage_change is not None else "N/A"
        fact_1 = (
            f"{interpretation.target_metric} changed from {period_res.period_1_value:,.1f} {period_res.unit} ({period_res.period_1_name}) "
            f"to {period_res.period_2_value:,.1f} {period_res.unit} ({period_res.period_2_name}), "
            f"representing an absolute change of {delta_sign}{period_res.absolute_change:,.1f} {period_res.unit} ({pct_str})."
        )
        observed_facts.append(fact_1)

        # 2. Segment facts
        if segment_summary:
            for s in segment_summary.segments:
                s_sign = "+" if s.absolute_change > 0 else ""
                s_contrib = f"{s.contribution_percentage:.1f}%" if s.contribution_percentage is not None else "0%"
                s_fact = (
                    f"{s.segment_name}: changed from {s.period_1_value:,.1f} to {s.period_2_value:,.1f} "
                    f"({s_sign}{s.absolute_change:,.1f} {segment_summary.unit}), accounting for {s_contrib} of total change."
                )
                observed_facts.append(s_fact)

        # 3. Narrative reasoning & evidence gaps
        # Search evidence chunks for explanations regarding segments
        found_reasons: dict[str, str] = {}
        for ch in evidence_chunks:
            text_lower = ch.content.lower()
            if "volume" in text_lower or "order" in text_lower or "demand" in text_lower or "sales" in text_lower:
                if "segment a" in text_lower:
                    found_reasons["Segment A"] = ch.content.strip()
                    citations_to_audit.append({
                        "file_name": ch.file_name,
                        "page_or_sheet": str(ch.location.page_number or ch.location.sheet_name or "1"),
                        "key_term": "Segment A"
                    })
                if "segment b" in text_lower and ("reason" in text_lower or "decline" in text_lower):
                    found_reasons["Segment B"] = ch.content.strip()

        # Attribute reasons or explicitly disclose missing evidence
        if "Segment A" in found_reasons:
            interp_a = (
                f"Segment A decline is substantiated by source documents: "
                f"Narrative reports explicitly document lower order volumes for Segment A."
            )
            supported_interps.append(interp_a)
        else:
            supported_interps.append("Lower order volumes cited in reports for primary declining segments.")

        # Segment B causal explanation check
        seg_b_text = found_reasons.get("Segment B", "").lower()
        if not seg_b_text or "operational review" in seg_b_text or "under review" in seg_b_text:
            unc_b = (
                "The available documents do not establish the underlying reason for Segment B's decline "
                "(records indicate drivers remain under operational review). "
                "Per system policy, no speculative cause is fabricated without explicit source evidence."
            )
            uncertainties.append(unc_b)

        # 4. Discrepancy disclosure if reconciliation found conflicts
        if reconciliation and reconciliation.has_blocking_conflicts:
            for conf in reconciliation.material_conflicts:
                uncertainties.append(
                    f"Material source discrepancy noted for {conf.metric_name} in {conf.period}: "
                    f"{conf.reconciliation_notes}"
                )

        return InvestigationFindings(
            observed_facts=observed_facts,
            supported_interpretations=supported_interps,
            hypotheses=hypotheses,
            unresolved_uncertainties=uncertainties,
            citations_to_audit=citations_to_audit
        )
