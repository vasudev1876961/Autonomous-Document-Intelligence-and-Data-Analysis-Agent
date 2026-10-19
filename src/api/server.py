"""
Enterprise FastAPI REST Microservice for Autonomous Document Intelligence.
Provides headless APIs for investigation orchestration, multi-agent debate,
scenario modeling, human-in-the-loop review queue, and verified report downloads.
"""
from pathlib import Path
from typing import Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from config.settings import settings
from src.agent.orchestrator import AgentOrchestrator
from src.tools.scenario_modeling import ScenarioModelingEngine
from src.agent.debate import MultiAgentDebateCouncil
from src.human_review.approval import ApprovalDecision
from src.human_review.review_queue import ReviewQueue
from src.evaluation.benchmark_runner import BenchmarkRunner

app = FastAPI(
    title="Autonomous Document Intelligence & Data Analysis Agent API",
    version="3.0.0",
    description="Enterprise REST API for evidence-driven multi-format document analysis, verified calculations, and HITL governance."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent orchestrator and queue instances
orchestrator = AgentOrchestrator()
review_queue = ReviewQueue()

class InvestigationRequest(BaseModel):
    goal: str = Field(
        default="Explain why revenue declined from Q1 to Q2. Identify the main contributing segments and support the explanation with evidence.",
        description="Analytical objective to investigate across documents."
    )
    file_paths: Optional[list[str]] = Field(
        default=None,
        description="Optional list of absolute or relative document paths. Defaults to sample benchmark docs."
    )

class SimulationRequest(BaseModel):
    scenario_name: str = "Custom Counterfactual Simulation"
    overrides: dict[str, float] = Field(default_factory=dict, description="Segment revenue overrides, e.g. {'Segment A': 500.0}")
    target_revenue: Optional[float] = Field(default=1000.0, description="Target recovery revenue level.")
    num_simulations: int = Field(default=1000, ge=10, le=10000)

class HitlDecisionRequest(BaseModel):
    request_id: str
    decision: str  # "APPROVE", "REJECT", "MODIFY"
    reviewer: str = "compliance_lead"
    override_value: Optional[float] = None
    notes: Optional[str] = "Decision rendered via REST API."

class BenfordAuditRequest(BaseModel):
    numbers: list[float] = Field(description="List of raw numeric figures to test for Benford logarithmic compliance.")

class HallucinationGuardRequest(BaseModel):
    claims: list[str] = Field(description="List of natural language claims or proposition strings to audit.")
    context_text: Optional[str] = Field(default="", description="Retrieved evidence context text.")

# ----------------- Endpoints -----------------

@app.get("/health", tags=["System"])
def health_check():
    """Returns microservice health status, architecture version, and storage indicators."""
    return {
        "status": "healthy",
        "service": "autonomous-document-intelligence",
        "version": "4.0.0",
        "active_db": str(settings.db_path),
        "deterministic_math": True,
        "hitl_enabled": True,
        "forensics_enabled": True,
        "hallucination_guard": True
    }

@app.post("/api/v1/investigate", tags=["Investigation"])
def run_investigation(req: InvestigationRequest):
    """
    Executes an autonomous multi-node document investigation end-to-end.
    Returns the verified analytical state, mathematical findings, and report links.
    """
    if req.file_paths:
        target_files = [Path(fp) for fp in req.file_paths]
    else:
        sample_paths = [
            settings.sample_docs_dir / "Quarterly_Report.pdf",
            settings.sample_docs_dir / "Revenue_Data.xlsx",
            settings.sample_docs_dir / "Segment_Performance.csv"
        ]
        target_files = [p for p in sample_paths if p.exists()]

    if not target_files:
        raise HTTPException(status_code=400, detail="No valid documents found for analysis.")

    try:
        state = orchestrator.run_investigation(goal=req.goal, file_paths=target_files)
        
        # Enqueue any HITL requests
        for appr in state.approval_requests:
            review_queue.active_requests[appr.request_id] = appr

        return {
            "task_id": state.task_id,
            "is_completed": state.is_completed,
            "period_comparison": state.period_comparison.model_dump() if state.period_comparison else None,
            "segment_analysis": state.segment_analysis.model_dump() if state.segment_analysis else None,
            "observed_facts": state.observed_facts,
            "supported_interpretations": state.supported_interpretations,
            "unresolved_questions": state.unresolved_questions,
            "verification_audit": state.verification_audit.model_dump() if state.verification_audit else None,
            "knowledge_graph": state.knowledge_graph_summary,
            "scenario_results": state.scenario_results,
            "debate_session": state.debate_session,
            "forensic_audit": state.forensic_audit,
            "hallucination_guard_audit": state.hallucination_guard_audit,
            "report_markdown_path": state.report_markdown_path,
            "report_pdf_path": state.report_pdf_path,
            "report_html_path": state.report_html_path,
            "audit_pack_json_path": state.audit_pack_json_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/forensics/benford", tags=["Forensic Accounting"])
def audit_benford(req: BenfordAuditRequest):
    """
    Executes Benford's Law First-Digit statistical analysis on an array of numbers.
    Computes MAD, Chi-Square, p-value, and checks for accounting irregularities.
    """
    from src.tools.forensic_auditor import ForensicAuditor
    result = ForensicAuditor.test_benford_first_digit(req.numbers)
    return result.model_dump()

@app.post("/api/v1/verification/hallucination-guard", tags=["Verification"])
def audit_hallucination_guard(req: HallucinationGuardRequest):
    """
    Audits propositions against provided context text to detect hallucinated statements.
    """
    from src.verification.hallucination_guard import HallucinationGuard
    from src.ingestion.metadata import ExtractedChunk, SourceLocation, FileType

    mock_chunk = ExtractedChunk(
        chunk_id="api_context",
        document_id="api_input",
        file_name="api_request_context",
        content=req.context_text or "",
        content_type="text",
        location=SourceLocation(
            document_id="api_input",
            file_name="api_request_context",
            file_type=FileType.PDF,
            page_number=1
        )
    )

    guard = HallucinationGuard()
    res = guard.audit_claims(claims=req.claims, evidence_chunks=[mock_chunk])
    return res.model_dump()

@app.post("/api/v1/scenarios/simulate", tags=["Analytics & Scenarios"])
def simulate_scenarios(req: SimulationRequest):
    """
    Runs deterministic counterfactual simulations, recovery plans, and Monte Carlo forecasts.
    """
    # Sample or currently loaded segment distribution
    from src.tools.numerical_analysis import NumericalAnalyzer
    sample_segments = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segments, "₹ lakh")

    results = {}
    if req.overrides:
        cf = ScenarioModelingEngine.simulate_counterfactual(
            base_summary=seg_summary,
            scenario_name=req.scenario_name,
            overrides=req.overrides
        )
        results["counterfactual"] = cf.model_dump()

    if req.target_revenue:
        rec = ScenarioModelingEngine.calculate_recovery_targets(
            base_summary=seg_summary,
            target_revenue=req.target_revenue
        )
        results["recovery_plan"] = rec.model_dump()

    mc = ScenarioModelingEngine.run_monte_carlo_forecast(
        base_summary=seg_summary,
        num_simulations=req.num_simulations
    )
    results["monte_carlo"] = mc.model_dump()

    return results

@app.post("/api/v1/debate", tags=["Multi-Agent Debate"])
def run_debate(goal: Optional[str] = None):
    """
    Runs an interactive 4-round Red Team debate council between specialists.
    """
    from src.tools.numerical_analysis import NumericalAnalyzer
    goal_str = goal or "Explain why revenue declined from Q1 to Q2."
    sample_segments = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segments, "₹ lakh")
    p_res = NumericalAnalyzer.compare_periods("Revenue", 1000.0, 900.0, "Q1", "Q2", "₹ lakh")

    council = MultiAgentDebateCouncil()
    debate_session = council.run_debate(
        goal=goal_str,
        period_res=p_res,
        seg_summary=seg_summary,
        reconciliation=None,
        evidence_chunks=[]
    )
    return debate_session.model_dump()

@app.get("/api/v1/hitl/queue", tags=["Governance & HITL"])
def get_hitl_queue():
    """Lists all pending approval requests in the Human-in-the-Loop review center."""
    active = review_queue.list_pending()
    return {
        "pending_count": len(active),
        "requests": [r.model_dump() for r in active]
    }

@app.post("/api/v1/hitl/decision", tags=["Governance & HITL"])
def submit_hitl_decision(decision_req: HitlDecisionRequest):
    """Submits a human approval, rejection, or override decision."""
    try:
        dec_enum = ApprovalDecision[decision_req.decision.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid decision. Must be APPROVE, REJECT, or MODIFY.")

    req = review_queue.active_requests.get(decision_req.request_id)
    if not req:
        # Check database
        req = review_queue.store.get_approval_request(decision_req.request_id)
        if not req:
            raise HTTPException(status_code=404, detail=f"Request '{decision_req.request_id}' not found.")

    res = review_queue.resolve_request(
        request_id=decision_req.request_id,
        decision=dec_enum,
        reviewer_id=decision_req.reviewer,
        override_value=decision_req.override_value,
        notes=decision_req.notes
    )
    return {
        "status": "success",
        "request_id": decision_req.request_id,
        "decision": decision_req.decision,
        "result": res
    }

@app.get("/api/v1/benchmarks/run", tags=["Evaluation & Benchmarks"])
def run_benchmarks():
    """Executes the ADI-Bench v1.0 benchmark suite and returns comparative metrics."""
    runner = BenchmarkRunner()
    result = runner.run_all_benchmarks()
    return result.model_dump()

@app.get("/api/v1/reports/{report_name}", tags=["Deliverables"])
def download_report(report_name: str):
    """Downloads an exported markdown or PDF report."""
    target_path = settings.outputs_dir / report_name
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Requested report deliverable not found.")
    
    media_types = {
        ".pdf": "application/pdf",
        ".html": "text/html",
        ".json": "application/json",
        ".md": "text/markdown",
        ".txt": "text/plain"
    }
    media_type = media_types.get(target_path.suffix.lower(), "application/octet-stream")
    return FileResponse(path=target_path, media_type=media_type, filename=report_name)
