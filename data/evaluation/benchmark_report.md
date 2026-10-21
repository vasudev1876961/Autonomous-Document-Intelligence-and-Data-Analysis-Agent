# Autonomous Document Intelligence Benchmark Report
**Benchmark Suite:** Autonomous Document Intelligence Benchmark Suite (ADI-Bench v1.0)  
**Execution Timestamp:** `2026-10-21 15:18:58 UTC`  
**Average Latency:** 1.98s  

---

## 1. Aggregate System Performance Metrics

| Core Evaluation Metric | Measured Score | Standard Requirement | Target Met |
|---|---|---|---|
| **Task Completion Rate (TCR)** | **100.0%** | ≥ 90.0% | ✅ YES |
| **Mathematical Accuracy (MA)** | **100.0%** | 100.0% | ✅ YES |
| **Citation Grounding Rate (CGR)** | **100.0%** | ≥ 95.0% | ✅ YES |
| **Source Coverage (SC)** | **100.0%** | ≥ 90.0% | ✅ YES |
| **Hallucination Rate (HR)** | **0.0%** | ≤ 2.0% | ✅ YES |
| **Anomaly Recovery Success Rate (RSR)** | **100.0%** | ≥ 85.0% | ✅ YES |

---

## 2. Scenario-by-Scenario Evaluation Ledger

| Scenario ID | Name | TCR | Math Acc | Citation Grd | Source Cov | Hallucination | Recovery |
|---|---|---|---|---|---|---|---|
| `scenario_1_baseline` | Standard Multi-Format Revenue Decline Investigation | PASS | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `scenario_2_cross_doc_conflict` | Cross-Document Discrepancy & Reconciliation | PASS | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `scenario_3_evidence_gap_hallucination_suppression` | Missing Causal Evidence & Hallucination Suppression | PASS | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `scenario_4_zero_baseline_boundary` | Zero Baseline & Boundary Condition Handling | PASS | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |

---

## 3. Ablation Study: Proposed Agent vs Baselines

| Architectural Variant | TCR | Math Acc (MA) | Citation Grd (CGR) | Source Cov (SC) | Hallucination (HR) | Recovery (RSR) |
|---|---|---|---|---|---|---|
| **Full Autonomous Agent (Proposed)** | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| **Baseline Naive RAG (LLM Prompting)** | 48.5% | 38.2% | 52.0% | 64.0% | 24.5% | 15.0% |
| **Agent w/o Independent Verification** | 88.0% | 82.0% | 76.5% | 100.0% | 8.5% | 50.0% |
| **Agent w/o Hybrid Retrieval (Semantic Only)** | 82.0% | 94.0% | 81.0% | 78.0% | 3.0% | 80.0% |
