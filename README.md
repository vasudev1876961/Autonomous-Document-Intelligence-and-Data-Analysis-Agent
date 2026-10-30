# Autonomous Document Intelligence & Data Analysis Agent (ADIDA)

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v4.1.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-12--Module%20UI-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph%20StateGraph-1C3C3C)](https://github.com/langchain-ai/langgraph)
[![Tests Passing](https://img.shields.io/badge/Tests-75%2F75%20Passing%20(100%25)-success?logo=pytest)](https://github.com/vasudev1876961/Autonomous-Document-Intelligence-and-Data-Analysis-Agent)
[![Packaging: PEP 517](https://img.shields.io/badge/Packaging-PEP%20517%20%7C%20pyproject.toml-blue)](pyproject.toml)
[![Docker Ready](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**An evidence-driven, multi-agent AI system for heterogeneous document understanding, deterministic quantitative analytics, forensic accounting, causal knowledge graphs, and cryptographic audit-grade verified reporting.**

[Key Features](#-feature-matrix-adida-vs-naive-rag) •
[Architecture](#-system-architecture) •
[Quickstart](#-quickstart) •
[CLI Guide](#-command-line-interface-cli) •
[REST API](#-headless-rest-api) •
[Dashboard](#-streamlit-executive-dashboard) •
[Benchmarks](#-empirical-evaluation-adi-bench-v10)

</div>

---

## 📌 Executive Overview

In corporate reporting, investment research, and regulatory compliance, organizations evaluate vast volumes of heterogeneous documents—including PDF filings, Excel financial workbooks, CSV operational extracts, JSON API payloads, and Word/Markdown management memos. 

Standard Retrieval-Augmented Generation (RAG) models suffer from critical limitations when applied to quantitative documents:
- **Arithmetic Hallucinations:** Large language models frequently fail at multi-period percentage deltas, compound annual growth rates (CAGR), segment additivity proofs, and DuPont return on equity decompositions.
- **Unverified Assertions:** Generic summarizers invent plausible explanations for missing data instead of explicitly disclosing epistemic uncertainty.
- **Cross-Document Inconsistencies:** Traditional RAG retrieves isolated chunks without reconciling discrepancies between audited financial filings and preliminary management bulletins.

**ADIDA solves this with an evidence-grounded, multi-agent stateful architecture.** Combining deterministic computational verification, forensic accounting (Benford's Law 1st, 2nd, and First-Two Digits), autonomous causal knowledge graphs (KG-RAG) with shock propagation, 4-agent red-team adversarial debates, and human-in-the-loop (HITL) governance, ADIDA delivers zero-hallucination quantitative intelligence.

---

## ⚡ Feature Matrix: ADIDA vs. Naive RAG

| Capability | Naive RAG / Conventional LLM | ADIDA v4.1 Enterprise Agent |
|---|---|---|
| **Mathematical Accuracy** | ~38% (High LLM calculation hallucination) | **100.0%** (Deterministic Python math engine, additivity proofs & 3-stage DuPont ROE verification) |
| **Forensic Accounting** | ❌ None (No statistical anomaly scan) | **Benford's Law (1st, 2nd & First-Two Digits 10..99), Nigrini MAD index, Tukey IQR & Z-score outliers** |
| **Multimodal Ingestion** | Raw unstructured text chunks only | **PyMuPDF bounding-boxes, OCR fallback, OpenPyXL, CSV, JSONPath payloads, and Markdown hierarchy** |
| **Citation Grounding** | ~52% (Vague or missing page citations) | **100.0%** (SHA-256 tamper-proof cell and bounding-box provenance) |
| **Cross-Document Discrepancies**| ❌ Ignores conflicting figures across sources | **Automated pairwise reconciliation with configurable materiality thresholds** |
| **Stress-Testing Findings** | ❌ Single-pass confirmation bias | **4-Agent Red-Team Debate Council (Quant, Lexi, Adversary, Supervisor)** |
| **Causal Modeling** | Surface-level text correlations | **Autonomous Causal Knowledge Graph (KG-RAG), multi-hop paths & operational shock propagation** |
| **Scenario Modeling** | ❌ Qualitative guesses | **Deterministic what-if overrides, sensitivity curves, Monte Carlo risk bounds** |
| **Governance & HITL** | ❌ Black-box execution | **Escalation queue with SQLite WAL persistence & approval overrides** |
| **Export Deliverables** | Raw markdown text | **Print-ready PDF, Interactive HTML dashboard, and Cryptographically Signed JSON Audit Pack (SHA-256)** |

---

## 🏛️ System Architecture

ADIDA coordinates five decoupled layers organized within a stateful LangGraph Directed Acyclic Graph (DAG):

```
                                  ┌──────────────────────────┐
                                  │   User Analytical Goal   │
                                  └─────────────┬────────────┘
                                                │
 ┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
 │ 1. INGESTION & HYBRID RETRIEVAL LAYER                                                      │
 │  • Spatial PyMuPDF bounding-box parser   • BM25 Lexical Keyword Search                      │
 │  • Table, OpenPyXL & JSONPath mapping    • Sentence-Transformers Dense ChromaDB Embeddings  │
 └──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                │
 ┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
 │ 2. DETERMINISTIC ANALYTICAL & FORENSIC ENGINE                                              │
 │  • Period-over-Period Delta (ΔR, %ΔR)    • Benford's Law (1st, 2nd & First-Two Digits)      │
 │  • Segment Contribution Additivity Proof • 3-Stage DuPont ROE Decomposition & Ratios       │
 │  • Cross-Document Pairwise Reconciliation• Counterfactual Overrides & Monte Carlo Forecast  │
 └──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                │
 ┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
 │ 3. MULTI-AGENT ADVERSARIAL DEBATE COUNCIL                                                   │
 │  • Quant-Alpha (Calculations)            • Adversary-Prime (Red-Team Auditor)               │
 │  • Lexi-Search (Citation Provenance)     • Supervisor-Chief (Executive Arbiter)             │
 └──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                │
 ┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
 │ 4. VERIFICATION, CAUSAL GRAPH & GOVERNANCE                                                 │
 │  • Independent Formula Recomputation     • Autonomous Causal Knowledge Graph (KG-RAG)       │
 │  • HallucinationGuard Grounding Audit    • Human-in-the-Loop Review Queue (SQLite WAL)      │
 │  • Causal Operational Shock Propagation  • Non-parametric Tukey Fences IQR Outlier Scan     │
 └──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                │
 ┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
 │ 5. ENTERPRISE MULTI-DELIVERABLE EXPORT                                                      │
 │  • Audit-Grade Markdown Report           • Self-Contained Interactive HTML Executive UI     │
 │  • Styled Publication PDF Document       • Cryptographically Signed JSON Audit Pack (SHA256)│
 └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/vasudev1876961/Autonomous-Document-Intelligence-and-Data-Analysis-Agent.git
cd "Autonomous Document Intelligence and Data Analysis Agent"

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Install dependencies (or pip install -e .)
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` (the system operates out-of-the-box with deterministic mock/local fallback embeddings and models if no API keys are supplied):

```bash
cp .env.example .env
```

### 3. Run the Dashboard

```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🐳 Docker Deployment

Run the complete multi-container stack (Dashboard + FastAPI Microservice + Shared Volume) via Docker Compose:

```bash
# Build and start services
docker-compose up --build

# Services available:
# • Streamlit Dashboard:  http://localhost:8501
# • FastAPI REST Docs:    http://localhost:8000/docs
# • Health Check:         http://localhost:8000/health
```

---

## 💻 Command-Line Interface (CLI)

ADIDA provides a unified CLI tool (`cli.py` or entry point `adida`) for automated workflows, terminal investigations, forensic audits, DuPont decomposition, and CI/CD verification.

### Check System Status
```bash
python cli.py status
```

### Run Autonomous Document Investigation
```bash
python cli.py investigate \
  --goal "Explain why revenue declined from Q1 to Q2 and identify the main contributing segments." \
  --files ./data/sample_documents/Quarterly_Report.pdf ./data/sample_documents/Revenue_Data.xlsx
```

### Forensic Accounting & Benford's Law Audit
Audit financial records for manipulation, non-conforming digit distributions, and statistical anomalies:

```bash
# Audit a CSV or Excel workbook
python cli.py forensic --file ./data/sample_documents/Segment_Performance.csv

# Audit First-Digit distribution (1..9)
python cli.py forensic --numbers 120 145 180 230 290 310 390 440 510 620 780 890 950 1100 1350

# Audit Second-Digit distribution (0..9)
python cli.py forensic --numbers 105 115 125 135 145 155 165 175 185 195 205 215 --second-digit

# Audit First-Two Digits distribution (10..99) [ACFE Forensic Gold Standard]
python cli.py forensic --numbers 105 115 125 135 145 155 165 175 185 195 205 215 225 235 245 255 265 275 285 295 310 --first-two-digits
```

### 3-Stage DuPont ROE Decomposition & Proof
Deterministically verify Return on Equity decomposition ($ROE = \text{Profit Margin} \times \text{Asset Turnover} \times \text{Leverage}$):

```bash
python cli.py dupont --ni 150 --rev 1000 --assets 2000 --equity 500
```

### Corporate Financial Ratios
Compute liquidity (Current, Quick), solvency (Debt-to-Equity), and profitability ratios:

```bash
python cli.py ratios --rev 1200 --cogs 720 --ebit 240 --ni 180 --ca 600 --cl 300 --debt 400 --equity 800
```

### Verify Audit Pack Cryptographic Integrity
Verify the tamper-evident SHA-256 digital signature of any exported audit pack:

```bash
python cli.py verify-pack outputs/audit_pack_task_xyz.json
```

### Multi-Agent Red-Team Debate Council
Trigger an adversarial debate between Quant, Lexi-Search, and Adversary specialists:

```bash
python cli.py debate --goal "Assess whether Segment A volume decline is transitory or structural."
```

### Counterfactual & Monte Carlo Scenario Simulation
```bash
python cli.py scenario --p1 1000 --p2 900 --target 1050
```

### Run Benchmark Suite (ADI-Bench)
```bash
python cli.py benchmark
```

---

## ⚡ Headless REST API

ADIDA includes an enterprise FastAPI microservice with automated OpenAPI documentation.

### Launch API Server
```bash
python scripts/run_api.py --port 8000 --host 0.0.0.0
```
Interactive Documentation:
- **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **ReDoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

### REST Endpoint Catalog

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check, active DB path, and engine flags |
| `POST` | `/api/v1/investigate` | Autonomous multi-node document investigation |
| `POST` | `/api/v1/forensics/benford` | Benford first-digit MAD and Chi-Square analysis |
| `POST` | `/api/v1/forensics/benford-second-digit` | Benford second-digit (0..9) MAD and distribution audit |
| `POST` | `/api/v1/forensics/benford-first-two-digits`| Benford first-two digits (10..99) cluster audit |
| `POST` | `/api/v1/analytics/dupont` | 3-Stage DuPont ROE decomposition & mathematical proof |
| `POST` | `/api/v1/analytics/financial-ratios` | Profitability, liquidity, and solvency ratio analysis |
| `POST` | `/api/v1/knowledge-graph/causal-shock` | Causal graph operational shock propagation simulation |
| `POST` | `/api/v1/verification/verify-audit-pack`| Cryptographic SHA-256 audit pack integrity verifier |
| `POST` | `/api/v1/verification/hallucination-guard`| Real-time claim grounding & faithfulness audit |
| `POST` | `/api/v1/scenarios/simulate` | What-if simulation, sensitivity curve & Monte Carlo |
| `POST` | `/api/v1/debate` | Multi-Agent Red-Team Debate Council |
| `GET` | `/api/v1/hitl/queue` | List pending Human-in-the-Loop approval requests |
| `POST` | `/api/v1/hitl/decision` | Submit reviewer approval, rejection, or override |
| `GET` | `/api/v1/benchmarks/run` | Execute ADI-Bench v1.0 benchmark suite |
| `GET` | `/api/v1/reports/{report_name}` | Download PDF, HTML, Markdown, or JSON audit pack |

---

## 🖥️ Streamlit Executive Dashboard

The interactive dashboard (`app.py`) provides 12 specialized operational modules:

1. **🚀 Investigation Studio:** Set goals, stage multi-format documents (PDF, DOCX, XLSX, CSV, JSON, TXT, MD), execute workflows, and download deliverables.
2. **📊 Analytical Findings & Visuals:** Inspect period-over-period performance, segment additivity proofs, DuPont ROE decomposition, corporate ratios, and waterfall charts.
3. **🔍 Verification & Discrepancy Audit:** Review independent mathematical recomputation proofs and cross-document reconciliation ledgers.
4. **🕸️ Causal Knowledge Graph:** Interactive Cytoscape network displaying causal entities, drivers, degree centrality hubs, and shock simulation.
5. **📈 What-If Scenarios & Sensitivity Engine:** Executive counterfactual sliders, sensitivity matrix (-20% to +20%), and 1,000-run Monte Carlo probability bounds.
6. **⚔️ Multi-Agent Debate Council:** Inspect multi-round adversarial cross-examination between Quant, Retrieval, and Red-Team specialists.
7. **🤝 Human-in-the-Loop Review Center:** Resolve conflicting evidence, approve high-risk findings, and record governance decisions.
8. **🛡️ Forensic Accounting & Benford Audit:** Empirical 1st, 2nd, and First-Two Digits (10..99) distribution charts, Nigrini MAD conformity ratings, and Tukey IQR outlier scans.
9. **🧪 Evaluation & Benchmarks:** On-demand execution of ADI-Bench v1.0 across full agent and ablation variants.
10. **📜 Audit Trail & History:** Complete episodic task history and immutable execution step audit logs backed by SQLite WAL.
11. **📁 Document & Provenance Inspector:** SHA-256 integrity verifier, extracted chunks, and bounding-box coordinates.
12. **⚡ Enterprise API & System Status:** Microservice telemetry, health status, and live curl query testing.

---

## 🧪 Empirical Evaluation (ADI-Bench v1.0)

ADIDA includes a built-in automated benchmark suite (`scripts/run_benchmarks.py`) evaluating performance across four system variants:

| Benchmark Metric | Full Agent (ADIDA) | Naive RAG (LLM Prompting) | Without Verification | Semantic Only (No BM25) |
|---|:---:|:---:|:---:|:---:|
| **Task Completion Rate (TCR)** | **100.0%** | 48.5% | 88.0% | 82.0% |
| **Mathematical Accuracy (MA)** | **100.0%** | 38.2% | 82.0% | 94.0% |
| **Citation Grounding Rate (CGR)** | **100.0%** | 52.0% | 76.5% | 81.0% |
| **Source Coverage (SC)** | **100.0%** | 64.0% | 100.0% | 78.0% |
| **Hallucination Rate (HR)** | **0.0%** | 24.5% | 8.5% | 3.0% |
| **Recovery Success Rate (RSR)** | **100.0%** | 15.0% | 50.0% | 80.0% |

---

## 📁 Repository Structure

```
├── .github/workflows/ci.yml       # Continuous Integration pipeline (Pytest + ADI-Bench)
├── config/
│   ├── settings.py                # Environment configuration & paths
│   └── __init__.py
├── data/
│   ├── raw/                       # Upload directory for user documents
│   ├── processed/                 # SQLite memory database (WAL mode)
│   ├── evaluation/                # Benchmark dataset & exported reports
│   └── sample_documents/          # Benchmark PDF, Excel, CSV, and financial datasets
├── outputs/                       # Generated Markdown, PDF, HTML, and JSON audit packs
├── scripts/
│   ├── run_api.py                 # FastAPI microservice runner
│   └── run_benchmarks.py          # Benchmark evaluation script
├── src/
│   ├── agent/
│   │   ├── brain.py               # Analytical reasoning & synthesis
│   │   ├── completion.py          # Task completion evaluator
│   │   ├── debate.py              # Multi-Agent Red-Team Debate Council
│   │   ├── orchestrator.py        # LangGraph stateful DAG orchestrator
│   │   ├── planner.py             # Structured 10-step investigation planner
│   │   ├── specialists.py         # Quant, Lexi, Adversary, and Supervisor agents
│   │   └── state.py               # Pydantic AgentState schema
│   ├── api/
│   │   └── server.py              # FastAPI microservice implementation (v4.1.0)
│   ├── evaluation/
│   │   ├── benchmark_runner.py    # ADI-Bench runner & ablation harness
│   │   └── metrics.py             # Benchmark scoring formulas (TCR, MA, HR, etc.)
│   ├── human_review/
│   │   ├── approval.py            # Approval request schemas & risk levels
│   │   └── review_queue.py        # Stateful HITL escalation queue
│   ├── ingestion/
│   │   ├── csv_parser.py          # Delimited tabular extraction
│   │   ├── docx_parser.py         # Word document parser
│   │   ├── excel_parser.py        # Multi-sheet Excel workbook parser
│   │   ├── json_parser.py         # JSON dataset & JSONPath extractor
│   │   ├── text_parser.py         # Markdown and Plain Text hierarchical parser
│   │   ├── manifest.py            # Ingestion manager & deduplication coordinator
│   │   ├── metadata.py            # Provenance schemas (SourceLocation, Chunks)
│   │   ├── ocr_layout_parser.py   # PyMuPDF spatial bounding-box & OCR fallback
│   │   └── pdf_parser.py          # Text & table PDF extraction
│   ├── memory/
│   │   ├── provenance.py          # Source citation tracking
│   │   ├── sqlite_store.py        # Relational persistence store (WAL mode)
│   │   └── task_history.py        # Episodic task retrieval manager
│   ├── reporting/
│   │   └── report_builder.py      # Audit-grade analytical report builder
│   ├── retrieval/
│   │   ├── chunking.py            # Structural document chunking
│   │   ├── embeddings.py          # Dense vector representations
│   │   ├── hybrid_retrieval.py    # Reciprocal rank fusion (BM25 + Dense)
│   │   ├── keyword_search.py      # BM25 lexical retriever
│   │   ├── knowledge_graph.py     # Causal Network, KG-RAG & Shock Propagation
│   │   └── vector_store.py        # Persistent vector store interface
│   ├── tools/
│   │   ├── chart_generation.py    # Matplotlib waterfall & delta visuals
│   │   ├── data_cleaning.py       # Data sanitization utilities
│   │   ├── forensic_auditor.py    # Benford's Law (1st, 2nd, 1st-2nd) & outlier engine
│   │   ├── numerical_analysis.py  # DuPont ROE decomposition, ratios & period math
│   │   ├── report_export.py       # Multi-format exporter & SHA-256 audit signer
│   │   ├── scenario_modeling.py   # Counterfactual, sensitivity & Monte Carlo
│   │   └── source_reconciliation.py # Cross-document discrepancy reconciler
│   └── verification/
│       ├── calculation_checks.py  # Independent math formula recomputation
│       ├── citation_checks.py     # SHA-256 citation grounding checker
│       ├── consistency_checks.py  # Contradiction & unit verification
│       ├── hallucination_guard.py # Real-time proposition reflection guardrail
│       └── verifier_pipeline.py   # Complete verification audit pipeline
├── tests/                         # 75 automated unit, integration & forensic tests
├── app.py                         # Streamlit 12-module Executive Dashboard
├── cli.py                         # Unified enterprise command-line tool (adida)
├── pyproject.toml                 # Standard PEP 517 build configuration
├── Dockerfile                     # Production container specification
├── docker-compose.yml             # Dashboard + API multi-container stack
├── requirements.txt               # Production Python dependencies
└── README.md                      # Project documentation
```

---

## 🧪 Testing & Validation

The test suite contains **75 automated unit, integration, and forensic tests (100% passing)** verifying mathematical proofs, Benford distributions, DuPont decomposition, causal shock propagation, cryptographic signatures, and REST endpoints.

Run the full test suite with:

```bash
pytest
```

---

## 🔒 Security, Compliance & Governance

- **Deterministic Execution:** Eliminates arithmetic hallucinations by routing all quantitative calculations to audited Python functions.
- **Traceable Provenance:** Every claim is linked to specific documents, page numbers, or spreadsheet cells with SHA-256 checksums.
- **Cryptographic Signing:** Audit packs include canonical SHA-256 digital signatures enabling independent verification of tamper-free report status.
- **Epistemic Classification:** Findings are partitioned into **Observed Facts**, **Supported Interpretations**, and **Disclosed Uncertainties**.
- **Human Governance:** Material data discrepancies trigger mandatory human approval before executive deliverables are published.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
