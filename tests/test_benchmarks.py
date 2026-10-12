"""
Unit tests for the Evaluation Benchmark Suite:
- Benchmark metrics formulas (TCR, MA, CGR, SC, HR, RSR)
- Dataset structure validation
- BenchmarkRunner execution
"""
import pytest
from src.evaluation.metrics import (
    calculate_task_completion_rate,
    calculate_mathematical_accuracy,
    calculate_citation_grounding_rate,
    calculate_source_coverage,
    calculate_hallucination_rate,
    calculate_recovery_success_rate,
)
from src.evaluation.benchmark_runner import BenchmarkRunner

def test_metric_calculations():
    assert calculate_task_completion_rate(9, 10) == 90.0
    assert calculate_task_completion_rate(0, 0) == 0.0

    assert calculate_mathematical_accuracy(10, 10) == 100.0
    assert calculate_mathematical_accuracy(8, 10) == 80.0

    assert calculate_citation_grounding_rate(19, 20) == 95.0
    assert calculate_source_coverage(3, 3) == 100.0
    assert calculate_hallucination_rate(0, 25) == 0.0
    assert calculate_recovery_success_rate(2, 2) == 100.0

def test_benchmark_dataset_integrity():
    runner = BenchmarkRunner()
    ds = runner.load_dataset()
    assert "scenarios" in ds
    assert len(ds["scenarios"]) >= 4
    scenario_ids = [s["id"] for s in ds["scenarios"]]
    assert "scenario_1_baseline" in scenario_ids
    assert "scenario_2_cross_doc_conflict" in scenario_ids
    assert "scenario_3_evidence_gap_hallucination_suppression" in scenario_ids
    assert "scenario_4_zero_baseline_boundary" in scenario_ids

def test_ablation_benchmarks_generation():
    runner = BenchmarkRunner()
    from src.evaluation.metrics import BenchmarkMetrics
    mock_metrics = BenchmarkMetrics(
        task_completion_rate=100.0,
        mathematical_accuracy=100.0,
        citation_grounding_rate=100.0,
        source_coverage=100.0,
        hallucination_rate=0.0,
        recovery_success_rate=100.0,
        average_latency_seconds=1.2
    )
    ablations = runner.compute_ablation_benchmarks(mock_metrics, 4)
    assert len(ablations) == 4
    names = [a.system_variant for a in ablations]
    assert any("Proposed" in n for n in names)
    assert any("Baseline Naive RAG" in n for n in names)
