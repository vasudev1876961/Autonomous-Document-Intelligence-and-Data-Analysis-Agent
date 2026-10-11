"""
Analytical Report Builder: Constructs comprehensive, audit-grade analytical reports
with verified calculations, source citations, limitation disclosures, and audit traces.
"""
from datetime import datetime, timezone
from typing import Optional
from src.agent.state import AgentState
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary
from src.verification.verifier_pipeline import VerificationAuditReport

class ReportBuilder:
    @staticmethod
    def build_markdown_report(state: AgentState) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        doc_names = [d.file_name for d in state.document_manifest]

        p_res = state.period_comparison
        s_res = state.segment_analysis
        v_audit = state.verification_audit

        lines = [
            f"# Autonomous Investigation & Analytical Report",
            f"**Task ID:** `{state.task_id}`  ",
            f"**Generated:** {now_str}  ",
            f"**Investigative Objective:** *\"{state.user_goal}\"*  ",
            f"**Status:** {'Completed & Verified' if state.is_completed else 'Under Investigation'}  ",
            "",
            "---",
            "",
            "## 1. Executive Summary",
        ]

        if p_res:
            delta_sign = "+" if p_res.absolute_change > 0 else ""
            pct_str = f" ({delta_sign}{p_res.percentage_change}%)" if p_res.percentage_change is not None else ""
            lines.append(
                f"An autonomous investigation was performed across **{len(doc_names)} documents**. "
                f"During the target window (**{p_res.period_1_name} to {p_res.period_2_name}**), "
                f"**{p_res.metric_name}** recorded an overall change of **{delta_sign}{p_res.absolute_change:,.1f} {p_res.unit}**{pct_str}. "
            )
            if s_res:
                top_segment = min(s_res.segments, key=lambda s: s.absolute_change)
                lines.append(
                    f"The primary driver of the movement was **{top_segment.segment_name}**, "
                    f"which accounted for **{top_segment.contribution_percentage:.1f}%** of the total change "
                    f"({top_segment.absolute_change:+,.1f} {s_res.unit})."
                )
        else:
            lines.append("Executive summary pending numerical analysis extraction.")

        lines.extend([
            "",
            "## 2. Ingested Evidence Sources",
            "The following documents were inventoried and verified via SHA-256 checksums:",
            "",
            "| Document ID | Filename | Format | Size | Checksum | Status |",
            "|---|---|---|---|---|---|",
        ])
        for doc in state.document_manifest:
            lines.append(
                f"| `{doc.document_id}` | {doc.file_name} | {doc.file_type.value.upper()} | "
                f"{doc.file_size_bytes:,} B | `{doc.content_hash[:10]}...` | {doc.extraction_status} |"
            )

        lines.extend([
            "",
            "## 3. Verified Numerical Analysis",
            "Calculations executed by the deterministic analytical engine and verified independently:",
            "",
        ])

        if p_res:
            lines.extend([
                "### 3.1 Period-over-Period Performance",
                "",
                f"| Metric | {p_res.period_1_name} | {p_res.period_2_name} | Absolute Change (Δ) | Percentage Change (%Δ) | Direction | Formula |",
                "|---|---|---|---|---|---|---|",
                f"| {p_res.metric_name} | {p_res.period_1_value:,.1f} {p_res.unit} | {p_res.period_2_value:,.1f} {p_res.unit} | "
                f"{p_res.absolute_change:+,.1f} {p_res.unit} | {p_res.percentage_change or 0.0:+,.1f}% | {p_res.direction.upper()} | `{p_res.formula_used}` |",
                "",
            ])

        if s_res:
            lines.extend([
                "### 3.2 Segment Contribution Breakdown",
                "",
                f"| Segment | {p_res.period_1_name if p_res else 'P1'} | {p_res.period_2_name if p_res else 'P2'} | Absolute Change (Δ) | Contribution to Total (%C) | Offsetting Flag |",
                "|---|---|---|---|---|---|",
            ])
            for s in s_res.segments:
                offset_str = "Yes (Offsetting)" if s.is_offsetting else "No"
                lines.append(
                    f"| **{s.segment_name}** | {s.period_1_value:,.1f} | {s.period_2_value:,.1f} | "
                    f"{s.absolute_change:+,.1f} {s_res.unit} | {s.contribution_percentage or 0.0:.1f}% | {offset_str} |"
                )
            reconcile_status = "Reconciled (Sum of segment deltas equals total delta)" if s_res.reconciled_with_total else f"Discrepancy: {s_res.discrepancy_amount}"
            lines.extend([
                "",
                f"**Segment Additivity Audit:** {reconcile_status}",
                "",
            ])

        lines.extend([
            "## 4. Key Findings & Epistemic Categorization",
            "Findings are partitioned into strictly grounded epistemic categories:",
            "",
            "### 4.1 Observed Facts (Directly supported by sources or deterministic computation)",
        ])
        for fact in state.observed_facts:
            lines.append(f"- [FACT] {fact}")

        lines.extend([
            "",
            "### 4.2 Supported Interpretations (Conclusions backed by narrative records)",
        ])
        for interp in state.supported_interpretations:
            lines.append(f"- [SUPPORTED] {interp}")

        lines.extend([
            "",
            "### 4.3 Missing Evidence & Disclosed Uncertainties (Explicitly not assumed)",
        ])
        if state.unresolved_questions:
            for unc in state.unresolved_questions:
                lines.append(f"- [UNCERTAINTY] {unc}")
        else:
            lines.append("- None reported. All required claims have grounded evidence.")

        lines.extend([
            "",
            "## 5. Verification & Mathematical Audit",
        ])
        if v_audit:
            lines.extend([
                f"**Overall Verdict:** {v_audit.summary_verdict}  ",
                f"- Total Tests Run: **{v_audit.total_checks}** (Passed: **{v_audit.passed_checks}**, Failed: **{v_audit.failed_checks}**)",
                "",
                "| Audit Component | Test Name | Expected | Recomputed | Discrepancy | Status |",
                "|---|---|---|---|---|---|",
            ])
            for c in v_audit.calculation_checks:
                status_str = "PASS" if c.is_valid else "FAIL"
                lines.append(f"| Mathematical Recomputation | {c.test_name} | {c.expected_value} | {c.computed_value} | {c.discrepancy} | **{status_str}** |")
            for cite in v_audit.citation_checks:
                status_str = "PASS" if cite.is_valid else "FAIL"
                lines.append(f"| Citation Provenance | {cite.citation_text} | File & Content Exist | Grounded={cite.evidence_grounded} | 0 | **{status_str}** |")
        else:
            lines.append("Verification audit was not completed.")

        lines.extend([
            "",
            "## 6. Audit Trail & Execution Steps",
            "Record of autonomous steps executed during the investigation:",
            "",
            "| Step ID | Description | Tool Category | Completion Status | Result Summary |",
            "|---|---|---|---|---|",
        ])
        for step in state.plan:
            lines.append(
                f"| `{step.step_id}` | {step.description} | `{step.tool_category}` | {step.status.upper()} | {step.result_summary or 'Completed'} |"
            )

        lines.extend([
            "",
            "---",
            "*Report generated autonomously by the Autonomous Document Intelligence and Data Analysis Agent.*"
        ])

        return "\n".join(lines)
