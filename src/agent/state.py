"""
Task State schema for the Autonomous Document Intelligence Agent.
"""
from typing import Any, Optional, TypedDict
from pydantic import BaseModel, Field
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk, ClaimCategory
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary
from src.tools.source_reconciliation import ReconciliationSummary
from src.verification.verifier_pipeline import VerificationAuditReport
from src.human_review.approval import ApprovalRequest

class PlanStep(BaseModel):
    step_id: str
    description: str
    required_inputs: list[str] = Field(default_factory=list)
    expected_output: str
    dependencies: list[str] = Field(default_factory=list)
    tool_category: str
    completion_criteria: str
    status: str = "pending" # "pending", "in_progress", "completed", "failed", "replanned"
    result_summary: Optional[str] = None

class AgentState(BaseModel):
    task_id: str
    user_goal: str
    constraints: list[str] = Field(default_factory=list)
    document_manifest: list[DocumentMetadata] = Field(default_factory=list)
    raw_chunks: list[ExtractedChunk] = Field(default_factory=list)
    
    # Plan
    plan: list[PlanStep] = Field(default_factory=list)
    current_step_index: int = 0
    completed_steps: list[str] = Field(default_factory=list)
    pending_steps: list[str] = Field(default_factory=list)
    
    # Investigation Data
    retrieved_evidence: list[ExtractedChunk] = Field(default_factory=list)
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    
    # Analysis & Verification
    period_comparison: Optional[PeriodComparisonResult] = None
    segment_analysis: Optional[SegmentAnalysisSummary] = None
    reconciliation_summary: Optional[ReconciliationSummary] = None
    verification_audit: Optional[VerificationAuditReport] = None
    
    # Reasoning & Findings
    observed_facts: list[str] = Field(default_factory=list)
    supported_interpretations: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    
    # Controls & HITL
    retry_count: int = 0
    max_retries: int = 3
    approval_requests: list[ApprovalRequest] = Field(default_factory=list)
    is_halted_for_approval: bool = False
    is_completed: bool = False
    
    # Output Artifacts
    chart_paths: list[str] = Field(default_factory=list)
    report_markdown_path: Optional[str] = None
    report_pdf_path: Optional[str] = None
    report_html_path: Optional[str] = None
    audit_pack_json_path: Optional[str] = None
    final_report_text: Optional[str] = None
    
    # Advanced Intelligence Extensions
    knowledge_graph_summary: Optional[dict[str, Any]] = None
    scenario_results: Optional[dict[str, Any]] = None
    debate_session: Optional[dict[str, Any]] = None
    forensic_audit: Optional[dict[str, Any]] = None
    hallucination_guard_audit: Optional[dict[str, Any]] = None

