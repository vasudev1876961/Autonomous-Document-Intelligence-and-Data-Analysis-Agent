"""
Specialized Multi-Agent Framework:
Implements distinct specialist agent personas for modular, collaborative document intelligence:
- PlannerSpecialist: Autonomous planning, DAG dependency sequencing, and adaptive replanning.
- RetrievalSpecialist: Multi-query expansion, hybrid fusion, and evidence scoring.
- AnalyticalSpecialist: Deterministic mathematical execution, segment attribution, and variance analysis.
- VerificationAuditor: Independent critic performing recomputations, citation audits, and consistency checks.
- SupervisorAgent: Multi-agent coordinator overseeing execution budget, conditional routing, and HITL escalation.
"""
from typing import Any, Optional
from pydantic import BaseModel, Field

from src.agent.state import PlanStep
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk, SourceLocation
from src.retrieval.hybrid_retrieval import HybridRetriever
from src.tools.numerical_analysis import (
    NumericalAnalyzer,
    PeriodComparisonResult,
    SegmentAnalysisSummary,
    VarianceAnalysisResult,
    CAGRResult,
    GrowthSeriesResult,
    OutlierDetectionResult
)
from src.tools.source_reconciliation import SourceClaim, SourceReconciliationEngine, ReconciliationSummary
from src.verification.verifier_pipeline import VerificationPipeline, VerificationAuditReport
from src.human_review.approval import ApprovalRequest, ApprovalDecision, RiskLevel
from src.human_review.review_queue import ReviewQueue


class SpecialistResult(BaseModel):
    specialist_name: str
    status: str # "success", "needs_replanning", "hitl_required", "error"
    data: dict[str, Any] = Field(default_factory=dict)
    narrative_notes: str = ""
    citations: list[dict[str, str]] = Field(default_factory=list)


class PlannerSpecialist:
    """Specialist responsible for autonomous decomposition, dependency sequencing, and adaptive replanning."""
    def __init__(self, name: str = "PlannerAgent"):
        self.name = name

    def create_investigation_plan(self, user_goal: str) -> list[PlanStep]:
        from src.agent.planner import InvestigationPlanner
        return InvestigationPlanner.generate_plan(user_goal)

    def adapt_plan_on_evidence_gap(
        self,
        current_plan: list[PlanStep],
        missing_metric: str,
        gap_reason: str
    ) -> list[PlanStep]:
        """
        Dynamically adapts plan by inserting a targeted retrieval / uncertainty disclosure step.
        """
        adapted = []
        for step in current_plan:
            adapted.append(step)
            if step.step_id == "step_2_retrieve_evidence":
                adapted.append(
                    PlanStep(
                        step_id="step_2b_targeted_reinvestigation",
                        description=f"Targeted deep retrieval for missing context regarding '{missing_metric}': {gap_reason}",
                        required_inputs=["raw_chunks", "unresolved_questions"],
                        expected_output=f"Supplemental evidence or formal disclosure for {missing_metric}",
                        dependencies=["step_2_retrieve_evidence"],
                        tool_category="retrieval",
                        completion_criteria="Confirmed presence of supplementary records or documented as unverified gap",
                        status="pending"
                    )
                )
        return adapted


class RetrievalSpecialist:
    """Specialist dedicated to lexical + semantic retrieval, query reformulation, and source attribution."""
    def __init__(self, retriever: Optional[HybridRetriever] = None, name: str = "RetrievalSpecialist"):
        self.name = name
        self.retriever = retriever or HybridRetriever()

    def expand_queries(self, goal: str) -> list[str]:
        """Generates domain-aware query expansions for comprehensive evidence coverage."""
        base = goal.lower()
        queries = [goal]
        if "revenue" in base or "sales" in base:
            queries.extend([
                "consolidated quarterly revenue Q1 Q2 performance",
                "segment breakdown revenue orders volume",
                "market conditions supply chain customers demand"
            ])
        if "profit" in base or "margin" in base:
            queries.extend([
                "operating profit net income EBITDA margin",
                "segment profitability cost of goods sold"
            ])
        return queries

    def execute_multi_retrieval(self, queries: list[str], top_k: int = 5) -> list[ExtractedChunk]:
        seen: dict[str, ExtractedChunk] = {}
        for q in queries:
            results = self.retriever.retrieve(q, top_k=top_k)
            for chunk, score in results:
                seen[chunk.chunk_id] = chunk
        return list(seen.values())


class AnalyticalSpecialist:
    """Deterministic quant specialist ensuring mathematical accuracy without LLM calculation errors."""
    def __init__(self, name: str = "QuantitativeAnalyst"):
        self.name = name

    def compute_period_comparison(
        self,
        metric_name: str,
        val1: float,
        val2: float,
        p1_name: str = "Q1",
        p2_name: str = "Q2",
        unit: str = "₹ lakh"
    ) -> PeriodComparisonResult:
        return NumericalAnalyzer.compare_periods(
            metric_name=metric_name,
            r1=val1,
            r2=val2,
            p1_name=p1_name,
            p2_name=p2_name,
            unit=unit
        )

    def compute_segment_breakdown(
        self,
        metric_name: str,
        segments_data: list[dict[str, Any]],
        unit: str = "₹ lakh"
    ) -> SegmentAnalysisSummary:
        return NumericalAnalyzer.analyze_segment_contributions(
            metric_name=metric_name,
            segments_data=segments_data,
            unit=unit
        )

    def compute_advanced_analytics(
        self,
        metric_name: str,
        segment_summary: SegmentAnalysisSummary,
        budget_target: Optional[float] = None
    ) -> dict[str, Any]:
        """Runs variance, statistical metrics, and anomaly detection across segment deltas."""
        results: dict[str, Any] = {}
        deltas = [s.absolute_change for s in segment_summary.segments]
        
        results["statistics"] = NumericalAnalyzer.calculate_statistics(f"{metric_name} Deltas", deltas)
        results["outliers"] = NumericalAnalyzer.detect_outliers(f"{metric_name} Segment Deltas", deltas)

        if budget_target is not None:
            results["budget_variance"] = NumericalAnalyzer.analyze_variance(
                metric_name=metric_name,
                actual=segment_summary.total_period_2,
                budget=budget_target,
                unit=segment_summary.unit
            )

        return results


class VerificationAuditor:
    """Independent red-team critic that verifies calculations, audit proofs, and source citations."""
    def __init__(self, manifest: list[DocumentMetadata], raw_chunks: list[ExtractedChunk], name: str = "AuditorSpecialist"):
        self.name = name
        self.pipeline = VerificationPipeline(manifest, raw_chunks)
        self.reconciliation_engine = SourceReconciliationEngine(material_threshold_pct=1.0)

    def audit_investigation(
        self,
        period_result: Optional[PeriodComparisonResult],
        segment_summary: Optional[SegmentAnalysisSummary],
        citations_to_check: list[dict[str, str]],
        unit_pairs: list[tuple[str, str]],
        source_claims: list[SourceClaim]
    ) -> tuple[VerificationAuditReport, ReconciliationSummary]:
        # 1. Pipeline verification
        report = self.pipeline.run_full_verification(
            period_result=period_result,
            segment_summary=segment_summary,
            citations_to_check=citations_to_check,
            unit_pairs=unit_pairs
        )
        # 2. Cross-document reconciliation
        recon = self.reconciliation_engine.reconcile_claims(source_claims)
        return report, recon


class SupervisorAgent:
    """Supervisor orchestrating multi-agent collaboration, budget guardrails, and HITL escalation."""
    def __init__(
        self,
        max_steps: int = 15,
        review_queue: Optional[ReviewQueue] = None,
        name: str = "SupervisorAgent"
    ):
        self.name = name
        self.max_steps = max_steps
        self.review_queue = review_queue or ReviewQueue()
        self.planner = PlannerSpecialist()
        self.retrieval = RetrievalSpecialist()
        self.quant = AnalyticalSpecialist()

    def evaluate_conflict_for_hitl(
        self,
        task_id: str,
        reconciliation: ReconciliationSummary
    ) -> Optional[ApprovalRequest]:
        """
        Escalates material discrepancies between sources to human review.
        """
        if not reconciliation.has_blocking_conflicts:
            return None

        primary_conflict = reconciliation.material_conflicts[0]
        req = self.review_queue.create_request(
            request_id=f"appr_{primary_conflict.metric_name}_{primary_conflict.period}",
            task_id=task_id,
            risk_level=RiskLevel.HIGH,
            action_type="reconcile_conflict",
            title=f"Material Discrepancy Detected for {primary_conflict.metric_name} ({primary_conflict.period})",
            description=primary_conflict.reconciliation_notes,
            proposed_action="Resolve conflicting reported values before finalizing report.",
            options=[
                f"Accept Audited Source ({primary_conflict.claim_a.reported_value} {primary_conflict.claim_a.unit} from {primary_conflict.claim_a.document_name})",
                f"Accept Alternative Source ({primary_conflict.claim_b.reported_value} {primary_conflict.claim_b.unit} from {primary_conflict.claim_b.document_name})",
                f"Disclose Discrepancy & Proceed with Sensitivity Interval [{min(primary_conflict.claim_a.reported_value, primary_conflict.claim_b.reported_value)} - {max(primary_conflict.claim_a.reported_value, primary_conflict.claim_b.reported_value)}]"
            ]
        )
        return req
