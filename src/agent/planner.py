"""
Structured Planner: Decomposes complex analytical objectives into ordered steps with explicit dependencies.
"""
from src.agent.state import PlanStep

class InvestigationPlanner:
    @staticmethod
    def generate_plan(goal: str) -> list[PlanStep]:
        """
        Decomposes an analytical objective into a verifiable 10-step investigation plan.
        """
        return [
            PlanStep(
                step_id="step_1_inventory",
                description="Inventory all uploaded documents, verify checksums, and detect available formats.",
                required_inputs=["document_manifest"],
                expected_output="Document catalog and metadata manifest",
                dependencies=[],
                tool_category="ingestion",
                completion_criteria="All files processed without unhandled format errors"
            ),
            PlanStep(
                step_id="step_2_retrieve_evidence",
                description="Execute hybrid retrieval (BM25 + Dense) to locate metric mentions, period figures, and explanatory texts.",
                required_inputs=["user_goal", "raw_chunks"],
                expected_output="Top-k relevant contextual chunks and tabular passages",
                dependencies=["step_1_inventory"],
                tool_category="retrieval",
                completion_criteria="Identified candidate revenue and segment passages"
            ),
            PlanStep(
                step_id="step_3_extract_data",
                description="Extract typed numerical figures for baseline and comparative periods, preserving units and locations.",
                required_inputs=["retrieved_evidence"],
                expected_output="Structured numerical datasets for periods and segments",
                dependencies=["step_2_retrieve_evidence"],
                tool_category="table_extraction",
                completion_criteria="Extracted period totals and segment values"
            ),
            PlanStep(
                step_id="step_4_reconcile_sources",
                description="Reconcile overlapping figures across different documents and flag discrepancies exceeding threshold.",
                required_inputs=["extracted_data"],
                expected_output="Source discrepancy report and conflict assessment",
                dependencies=["step_3_extract_data"],
                tool_category="source_reconciliation",
                completion_criteria="Confirmed source agreement or flagged conflicts for review"
            ),
            PlanStep(
                step_id="step_5_period_comparison",
                description="Execute deterministic period-over-period comparison (Delta R and %Delta R).",
                required_inputs=["extracted_data"],
                expected_output="PeriodComparisonResult with absolute and percentage changes",
                dependencies=["step_4_reconcile_sources"],
                tool_category="numerical_analysis",
                completion_criteria="Calculated exact change and confirmed baseline validity"
            ),
            PlanStep(
                step_id="step_6_segment_contributions",
                description="Compute segment-level absolute changes and percentage contributions to total delta.",
                required_inputs=["extracted_data", "step_5_period_comparison"],
                expected_output="SegmentAnalysisSummary with reconciled additivity",
                dependencies=["step_5_period_comparison"],
                tool_category="numerical_analysis",
                completion_criteria="Segment delta sum reconciles with total delta"
            ),
            PlanStep(
                step_id="step_7_reasoning_and_gap_analysis",
                description="Synthesize narrative evidence, categorize claims (Facts vs Interpretations vs Hypotheses), and identify missing evidence.",
                required_inputs=["retrieved_evidence", "step_6_segment_contributions"],
                expected_output="Categorized findings and disclosed uncertainties",
                dependencies=["step_6_segment_contributions"],
                tool_category="brain",
                completion_criteria="Every material claim linked to evidence or flagged as uncertain"
            ),
            PlanStep(
                step_id="step_8_verify_findings",
                description="Execute independent mathematical recomputation, citation existence audit, and consistency checks.",
                required_inputs=["step_5_period_comparison", "step_6_segment_contributions"],
                expected_output="VerificationAuditReport with mathematical and citation checks",
                dependencies=["step_7_reasoning_and_gap_analysis"],
                tool_category="verification",
                completion_criteria="Recomputations match and citations point to real documents"
            ),
            PlanStep(
                step_id="step_9_generate_visualizations",
                description="Render verified visual analytics (period comparison and segment contribution charts).",
                required_inputs=["step_5_period_comparison", "step_6_segment_contributions"],
                expected_output="Generated chart image files",
                dependencies=["step_8_verify_findings"],
                tool_category="visualization",
                completion_criteria="Rendered charts saved to output directory"
            ),
            PlanStep(
                step_id="step_10_compile_report",
                description="Compile comprehensive analytical report with citations, methodology, charts, and audit trail in Markdown and PDF.",
                required_inputs=["step_8_verify_findings", "step_9_generate_visualizations"],
                expected_output="Exported Markdown and PDF analytical reports",
                dependencies=["step_9_generate_visualizations"],
                tool_category="reporting",
                completion_criteria="Final report generated and stored in persistent memory"
            ),
        ]
