"""
Enterprise FastAPI REST Microservice for Autonomous Document Intelligence.
Provides headless APIs for investigation orchestration, multi-agent debate,
scenario modeling, human-in-the-loop review queue, and verified report downloads.
"""
from pathlib import Path
from typing import Any, Optional
import uuid
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from config.settings import settings
from src.agent.orchestrator import AgentOrchestrator
from src.tools.scenario_modeling import ScenarioModelingEngine
from src.agent.debate import MultiAgentDebateCouncil
from src.agent.committee import AutonomousAuditCommittee
from src.human_review.approval import ApprovalDecision
from src.human_review.review_queue import ReviewQueue
from src.evaluation.benchmark_runner import BenchmarkRunner

app = FastAPI(
    title="Autonomous Document Intelligence & Data Analysis Agent API",
    version="4.1.0",
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

class DuPontRequest(BaseModel):
    net_income: float
    revenue: float
    total_assets: float
    total_equity: float

class FinancialRatiosRequest(BaseModel):
    revenue: float
    cost_of_goods_sold: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    inventory: Optional[float] = 0.0
    total_debt: Optional[float] = None
    total_equity: Optional[float] = None
    total_assets: Optional[float] = None

class CausalShockRequest(BaseModel):
    root_node_id: str = "driver_supply_chain"
    shock_pct: float = -15.0

class VerifyAuditPackRequest(BaseModel):
    audit_pack_path: str = Field(description="Relative or absolute path to the audit pack JSON file.")

class CommitteeDebateRequest(BaseModel):
    goal: str = Field(
        default="Audit financial integrity, earnings performance, and accounting compliance.",
        description="Analytical mandate for the committee."
    )
    task_id: Optional[str] = Field(default=None, description="Optional task tracking ID.")
    numbers: Optional[list[float]] = Field(default=None, description="Array of numerical figures for forensic Benford & duplicate testing.")
    period_data: Optional[dict[str, Any]] = Field(default=None, description="Period comparison figures with keys 'p1', 'p2', 'metric', 'unit'.")
    segment_data: Optional[list[dict[str, Any]]] = Field(default=None, description="Segment breakdown records.")
    dupont_data: Optional[dict[str, float]] = Field(default=None, description="DuPont parameters: net_income, revenue, total_assets, total_equity.")
    financial_ratios_data: Optional[dict[str, float]] = Field(default=None, description="Corporate financial ratios input.")
    disagreement_threshold: float = Field(default=0.15, ge=0.01, le=0.50, description="Disagreement tolerance before HITL escalation (default: 0.15 = 15%).")

class HighlightGroundingRequest(BaseModel):
    file_path: Optional[str] = Field(default=None, description="Path to PDF file. Defaults to sample Quarterly_Report.pdf.")
    page_number: int = Field(default=1, ge=1)
    bboxes: Optional[list[tuple[float, float, float, float]]] = Field(default=None, description="List of (x0, y0, x1, y1) bounding boxes to highlight.")
    query_text: Optional[str] = Field(default=None, description="Text string to search and highlight automatically.")

class ChartDeRenderRequest(BaseModel):
    file_path: Optional[str] = Field(default=None, description="Path to PDF file.")
    page_number: int = Field(default=1, ge=1)

class TableStructureRequest(BaseModel):
    raw_rows: list[list[str]] = Field(description="Raw extracted matrix of table rows and cells.")
    page_number: int = Field(default=1, ge=1)

# ----------------- Endpoints -----------------

@app.get("/health", tags=["System"])
def health_check():
    """Returns microservice health status, architecture version, and storage indicators."""
    return {
        "status": "healthy",
        "service": "autonomous-document-intelligence",
        "version": "4.1.0",
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

@app.post("/api/v1/forensics/benford-second-digit", tags=["Forensic Accounting"])
def audit_benford_second_digit(req: BenfordAuditRequest):
    """
    Executes Benford's Law Second-Digit statistical analysis on an array of numbers (digits 0..9).
    Computes Nigrini second-digit MAD, Chi-Square, and distribution conformity.
    """
    from src.tools.forensic_auditor import ForensicAuditor
    result = ForensicAuditor.test_benford_second_digit(req.numbers)
    return result.model_dump()

@app.post("/api/v1/forensics/benford-first-two-digits", tags=["Forensic Accounting"])
def audit_benford_first_two_digits(req: BenfordAuditRequest):
    """
    Executes Benford's Law First-Two Digits (10..99) statistical analysis on an array of numbers.
    Computes Nigrini first-two digits MAD, Chi-Square (89 df), and checks for accounting fraud/clusters.
    """
    from src.tools.forensic_auditor import ForensicAuditor
    result = ForensicAuditor.test_benford_first_two_digits(req.numbers)
    return result.model_dump()

@app.post("/api/v1/analytics/dupont", tags=["Analytics & Scenarios"])
def calculate_dupont(req: DuPontRequest):
    """
    Executes 3-Stage DuPont ROE Decomposition and verifies mathematical proof consistency.
    ROE = Net Margin * Asset Turnover * Equity Multiplier.
    """
    from src.tools.numerical_analysis import NumericalAnalyzer
    result = NumericalAnalyzer.calculate_dupont_analysis(
        net_income=req.net_income,
        revenue=req.revenue,
        total_assets=req.total_assets,
        total_equity=req.total_equity
    )
    return result.model_dump()

@app.post("/api/v1/analytics/financial-ratios", tags=["Analytics & Scenarios"])
def calculate_ratios(req: FinancialRatiosRequest):
    """
    Calculates audited liquidity, solvency, and profitability financial ratios.
    """
    from src.tools.numerical_analysis import NumericalAnalyzer
    result = NumericalAnalyzer.calculate_financial_ratios(
        revenue=req.revenue,
        cost_of_goods_sold=req.cost_of_goods_sold,
        operating_income=req.operating_income,
        net_income=req.net_income,
        current_assets=req.current_assets,
        current_liabilities=req.current_liabilities,
        inventory=req.inventory,
        total_debt=req.total_debt,
        total_equity=req.total_equity,
        total_assets=req.total_assets
    )
    return result.model_dump()

@app.post("/api/v1/knowledge-graph/causal-shock", tags=["Knowledge Graph"])
def run_causal_shock(req: CausalShockRequest):
    """
    Simulates operational shock propagation through the causal knowledge graph to downstream metrics.
    """
    from src.retrieval.knowledge_graph import DocumentKnowledgeGraph, EntityNode, RelationEdge
    from src.tools.numerical_analysis import NumericalAnalyzer

    kg = DocumentKnowledgeGraph()
    sample_segments = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segments, "₹ lakh")
    kg.populate_from_investigation(chunks=[], segment_data=seg_summary)

    # Ensure root node is present if not already
    if req.root_node_id not in kg.nodes_data:
        kg.add_entity(EntityNode(
            node_id=req.root_node_id,
            name=req.root_node_id.replace("_", " ").title(),
            entity_type="Driver"
        ))
        kg.add_relation(RelationEdge(
            source_id=req.root_node_id,
            target_id="segment_segment_a",
            relation_type="CAUSED_BY",
            weight=0.9
        ))

    result = kg.simulate_causal_shock(root_node_id=req.root_node_id, shock_pct=req.shock_pct)
    return result.model_dump()

@app.post("/api/v1/verification/verify-audit-pack", tags=["Verification"])
def verify_audit_pack(req: VerifyAuditPackRequest):
    """
    Verifies cryptographic SHA-256 digital signature of an exported JSON audit pack deliverable.
    """
    from src.tools.report_export import ReportExporter
    result = ReportExporter.verify_audit_pack_integrity(req.audit_pack_path)
    return result


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

@app.post("/api/v1/agent/committee-debate", tags=["Multi-Agent Debate"])
def run_autonomous_committee_debate(req: CommitteeDebateRequest):
    """
    Executes a 5-Agent Autonomous Audit Committee debate:
    1. Forensic Auditor Agent (Benford 1st, 2nd, two-digit 10..99, duplicates, round numbers)
    2. Quantitative Financial Analyst (DuPont ROE decomposition, corporate ratios, proofs)
    3. Cross-Document Reconciler (source contradictions & footnote disclosures)
    4. Adversarial Red-Team / Devil's Advocate (counter-theses & sensitivity stress-testing)
    5. Chief Risk Officer (multi-round synthesis, quantitative consensus scoring, and HITL escalation if disagreement > 15%).
    """
    task_id = req.task_id or f"task_comm_{uuid.uuid4().hex[:8]}"
    committee = AutonomousAuditCommittee(
        disagreement_threshold=req.disagreement_threshold,
        review_queue=review_queue
    )
    session = committee.convene_committee(
        task_id=task_id,
        goal=req.goal,
        numbers=req.numbers,
        period_data=req.period_data,
        segment_data=req.segment_data,
        dupont_data=req.dupont_data,
        financial_ratios_data=req.financial_ratios_data
    )
    return session.model_dump()

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

@app.post("/api/v1/multimodal/highlight", tags=["Multimodal Document AI"])
def highlight_grounding(req: HighlightGroundingRequest):
    """
    Renders high-resolution PDF page with exact bounding box highlights ([x0, y0, x1, y1])
    or automatically searches and highlights query text occurrences.
    """
    from src.ingestion.visual_grounding import VisualGroundingEngine
    pdf_path = Path(req.file_path) if req.file_path else (settings.sample_docs_dir / "Quarterly_Report.pdf")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF file not found: {pdf_path}")

    boxes = req.bboxes or []
    if not boxes and req.query_text:
        boxes = VisualGroundingEngine.find_text_coordinates(pdf_path, req.page_number, req.query_text)

    if not boxes:
        boxes = [(50.0, 50.0, 300.0, 100.0)]

    out_file = settings.outputs_dir / "charts" / f"grounding_p{req.page_number}_{uuid.uuid4().hex[:6]}.png"
    result = VisualGroundingEngine.highlight_bboxes_on_page(
        pdf_path=pdf_path,
        page_number=req.page_number,
        bboxes=boxes,
        output_path=out_file
    )
    return result.model_dump()

@app.post("/api/v1/multimodal/chart-derender", tags=["Multimodal Document AI"])
def derender_charts(req: ChartDeRenderRequest):
    """
    De-renders visual vector charts and plots from a PDF page into structured JSON/tabular series.
    """
    from src.ingestion.chart_derenderer import ChartDeRenderer
    pdf_path = Path(req.file_path) if req.file_path else (settings.sample_docs_dir / "Quarterly_Report.pdf")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF file not found: {pdf_path}")

    charts = ChartDeRenderer.de_render_page_charts(pdf_path, req.page_number)
    return {"charts_found": len(charts), "charts": [c.model_dump() for c in charts]}

@app.post("/api/v1/multimodal/table-structure", tags=["Multimodal Document AI"])
def recognize_table_structure(req: TableStructureRequest):
    """
    Cleans raw table rows, resolving hierarchical headers, empty spanning cells, and merged layouts.
    """
    from src.ingestion.table_structure import ComplexTableRecognizer
    rec = ComplexTableRecognizer.process_raw_table(
        raw_rows=req.raw_rows,
        page_number=req.page_number
    )
    return rec.model_dump()

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
