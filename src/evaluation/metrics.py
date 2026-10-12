"""
Evaluation Metrics Engine for Autonomous Document Intelligence:
Calculates standard benchmark performance metrics:
- Task Completion Rate (TCR)
- Mathematical Accuracy (MA)
- Citation Grounding Rate (CGR)
- Source Coverage (SC)
- Hallucination Rate (HR)
- Recovery Success Rate (RSR)
"""
from pydantic import BaseModel, Field

class BenchmarkMetrics(BaseModel):
    task_completion_rate: float = Field(..., description="Percentage of successfully finished tasks (0-100%)")
    mathematical_accuracy: float = Field(..., description="Percentage of exact mathematical calculations (0-100%)")
    citation_grounding_rate: float = Field(..., description="Percentage of citations verified against sources (0-100%)")
    source_coverage: float = Field(..., description="Percentage of relevant documents consulted (0-100%)")
    hallucination_rate: float = Field(..., description="Percentage of ungrounded or invented claims (0-100%)")
    recovery_success_rate: float = Field(..., description="Percentage of injected anomalies resolved or flagged (0-100%)")
    average_latency_seconds: float = Field(0.0, description="Mean task turnaround time")

class EvaluationScores(BaseModel):
    scenario_id: str
    scenario_name: str
    tcr_pass: bool
    ma_score: float
    cgr_score: float
    sc_score: float
    hr_score: float
    rsr_score: float
    notes: str = ""

def calculate_task_completion_rate(completed_tasks: int, total_tasks: int) -> float:
    if total_tasks <= 0:
        return 0.0
    return round((completed_tasks / total_tasks) * 100.0, 2)

def calculate_mathematical_accuracy(correct_calculations: int, total_calculations: int) -> float:
    if total_calculations <= 0:
        return 100.0
    return round((correct_calculations / total_calculations) * 100.0, 2)

def calculate_citation_grounding_rate(grounded_citations: int, total_citations: int) -> float:
    if total_citations <= 0:
        return 100.0
    return round((grounded_citations / total_citations) * 100.0, 2)

def calculate_source_coverage(consulted_sources: int, total_sources: int) -> float:
    if total_sources <= 0:
        return 100.0
    return round((consulted_sources / total_sources) * 100.0, 2)

def calculate_hallucination_rate(unsupported_claims: int, total_claims: int) -> float:
    if total_claims <= 0:
        return 0.0
    return round((unsupported_claims / total_claims) * 100.0, 2)

def calculate_recovery_success_rate(recovered_anomalies: int, total_anomalies: int) -> float:
    if total_anomalies <= 0:
        return 100.0
    return round((recovered_anomalies / total_anomalies) * 100.0, 2)
