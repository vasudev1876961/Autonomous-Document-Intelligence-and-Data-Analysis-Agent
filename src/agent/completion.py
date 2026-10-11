"""
Completion Evaluator: Verifies whether an investigation meets all predefined acceptance conditions.
"""
from typing import Optional
from pydantic import BaseModel
from src.agent.state import AgentState

class CompletionCheckResult(BaseModel):
    is_completed: bool
    unresolved_requirements: list[str]
    completion_summary: str

class CompletionEvaluator:
    @staticmethod
    def evaluate(state: AgentState) -> CompletionCheckResult:
        unresolved: list[str] = []

        if not state.document_manifest:
            unresolved.append("No documents were ingested into manifest.")

        if not state.period_comparison:
            unresolved.append("Period comparison calculation was not executed.")

        if not state.verification_audit or not state.verification_audit.all_checks_passed:
            unresolved.append("Verification audit has failing checks or was not executed.")

        if not state.report_markdown_path and not state.final_report_text:
            unresolved.append("Final analytical report deliverable was not produced.")

        is_done = len(unresolved) == 0
        summary = (
            "Task successfully completed: all acceptance criteria, numerical reconciliations, "
            "and verification checks were satisfied."
            if is_done else
            f"Task incomplete: {len(unresolved)} acceptance criteria remain unresolved."
        )

        return CompletionCheckResult(
            is_completed=is_done,
            unresolved_requirements=unresolved,
            completion_summary=summary
        )
