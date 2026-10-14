# Autonomous Document Intelligence and Data Analysis Agent
## An Evidence-Driven Agentic AI System for Multi-Format Document Understanding, Analytical Reasoning, and Verified Reporting

**Project Domain:** Agentic Artificial Intelligence, Large Language Models, Retrieval-Augmented Generation, Data Analytics, Document Intelligence

**Proposed Technology Stack:** Python, LangGraph, LLMs, Retrieval-Augmented Generation (RAG), PyMuPDF, pandas, openpyxl, SQLite, ChromaDB, sentence-transformers, Matplotlib, Streamlit

**Project Type:** Advanced AI/ML Software Engineering Project

**Implementation Approach:** Modular, tool-using agent with persistent memory, adaptive planning, evidence verification, and human-in-the-loop supervision.

---

## ⚡ Key Highlights & Advanced Implementation (v3.0 Enterprise Edition)

| Core Pillar | Technical Implementation | Architectural Highlight |
|---|---|---|
| **Autonomous Knowledge Graph & Causal Network (KG-RAG)** | `src/retrieval/knowledge_graph.py` | Extracts financial and operational entities, maps multi-hop causal paths (e.g. supply disruption ➔ segment decline ➔ net revenue), computes degree centrality, and exports Cytoscape JSON. |
| **Deterministic Scenario & Sensitivity Engine** | `src/tools/scenario_modeling.py` | Executive counterfactual simulations (what-if overrides), sensitivity matrices across shocks (-20% to +20%), forward recovery target solver, and 1,000-run Monte Carlo volatility bounds with zero LLM math hallucinations. |
| **Multi-Agent Red-Team Debate Council** | `src/agent/debate.py` | 4-round adversarial debate between Quantitative Analyst (Quant-Alpha), Retrieval Specialist (Lexi-Search), Red-Team Auditor (Adversary-Prime), and Executive Supervisor (Supervisor-Chief) with consensus ruling and confidence grading. |
| **Enterprise FastAPI REST Microservice** | `src/api/server.py` | Headless microservice on port 8000 with interactive Swagger UI (`/docs`), ReDoc, 9 REST endpoints for investigations, scenarios, debate, HITL resolution, and report downloads. |
| **Layout-Aware Spatial & OCR Ingestion** | `src/ingestion/ocr_layout_parser.py` | PyMuPDF spatial bounding-box block decomposition, scanned PDF density classification, embedded figure discovery, and OCR fallback. |
| **Executive Streamlit Dashboard (11 Tabs)** | `app.py` | 11 comprehensive tabs: Studio, Visuals, Verification Ledger, Causal Knowledge Graph, What-If Scenarios, Multi-Agent Debate, HITL Queue, ADI-Bench, Audit Trail, Document Inspector, and API Status. |
| **Deterministic Numerical Analytics** | `src/tools/numerical_analysis.py` | Period-over-period comparison, segment attribution additivity proofs, variance analysis, CAGR, growth series, and outlier detection. |
| **Cross-Document Discrepancy Reconciliation** | `src/tools/source_reconciliation.py` | Pairwise claim reconciliation across heterogeneous PDFs, Excels, CSVs, and Word docs with configurable materiality thresholds. |
| **Human-in-the-Loop Governance** | `src/human_review/review_queue.py` | Stateful escalation queue for resolving data conflicts, approving plans, and recording user decisions in SQLite WAL store. |
| **Automated Benchmark & Ablation Suite** | `scripts/run_benchmarks.py` | ADI-Bench v1.0 measuring TCR (100%), MA (100%), CGR (100%), SC (100%), HR (0%), and RSR (100%) against baseline RAG. |
| **Production Docker Containerization** | `Dockerfile` & `docker-compose.yml` | Multi-container Docker Compose stack orchestrating dashboard and API with persistent shared volumes and healthchecks. |
| **Full Automated Testing Suite** | `.github/workflows/ci.yml` | 36 comprehensive unit & integration tests covering the complete agent lifecycle, REST API, knowledge graph, debate council, and math proofs. |


---

# 1. Abstract

Organizations and individuals frequently maintain large collections of documents, including PDF reports, Excel workbooks, CSV datasets, Word documents, financial statements, research papers, and operational records. Extracting meaningful information from these sources requires more than document retrieval. It requires understanding the context of the documents, comparing numerical values, performing calculations, identifying inconsistencies, verifying evidence, and generating conclusions supported by reliable sources.

Traditional document-processing applications typically perform predefined operations, while conventional Retrieval-Augmented Generation (RAG) systems retrieve relevant passages and use a language model to formulate answers. Although these approaches are useful, they often lack the ability to independently plan a complex investigation, select analytical tools, execute calculations, detect missing evidence, revise their approach, and verify the final result.

This project proposes an **Autonomous Document Intelligence and Data Analysis Agent**, an Agentic AI system designed to transform unstructured documents and structured datasets into evidence-backed analytical insights.

The system accepts a user-defined objective and a collection of documents. It interprets the objective, identifies the relevant information sources, constructs an investigation plan, retrieves evidence, performs computational analysis, evaluates intermediate findings, and dynamically adapts its workflow when additional information is required.

The proposed architecture consists of five principal components: Brain, Orchestrator, Tools, Memory, and Human-in-the-Loop (HITL). The Brain uses a large language model for contextual interpretation, reasoning, and decision-making. The Orchestrator manages task execution, dependencies, workflow state, and conditional transitions. Tools enable document extraction, retrieval, statistical analysis, spreadsheet processing, visualization, and citation verification. Memory preserves task history and reusable findings. HITL introduces human supervision for approval, correction, and sensitive operations.

The system incorporates a practical RAG pipeline for source-grounded information retrieval, programmatic calculations for numerical reliability, and a verification loop to reduce unsupported conclusions. Its performance will be evaluated using task completion, numerical accuracy, citation correctness, evidence coverage, tool efficiency, adaptability, and human intervention requirements.

The expected outcome is a modular, extensible AI agent capable of conducting multi-step document investigations with traceable evidence and measurable analytical reliability.

**Keywords:** Agentic AI, Autonomous Agents, Document Intelligence, RAG, LLM, LangGraph, Tool Calling, Persistent Memory, Data Analysis, Evidence Verification, Human-in-the-Loop.

---

# 2. Introduction

## 2.1 Background

Digital information is stored in multiple formats. Important business and research information may be distributed across PDF reports, spreadsheets, Word documents, scanned records, tables, charts, and historical datasets.

A user attempting to answer a question such as "Why did quarterly revenue decline?" may need to:

1. Locate the relevant quarterly reports.
2. Extract revenue figures from spreadsheets.
3. Identify the corresponding periods and business segments.
4. Compare current and previous values.
5. Calculate percentage changes and segment contributions.
6. Read explanatory information from reports.
7. Check whether different documents contain conflicting figures.
8. Determine which findings are supported by evidence.
9. Prepare a final analytical report.

Performing these steps manually can be time-consuming, especially when the information is spread across numerous documents.

A basic language model may summarize the documents, but summarization alone does not guarantee correct calculations, complete evidence, or reliable cross-document reasoning.

The proposed system addresses this problem by combining language-model reasoning with deterministic computational tools and an explicit agent execution workflow.

## 2.2 What makes this an Agentic AI project?

An ordinary AI assistant primarily responds to individual prompts. An agentic system can pursue a defined objective through a sequence of decisions and actions.

For this project, the user does not need to specify every intermediate operation.

Instead, the user provides a goal, such as:

"Analyze the uploaded reports, identify the major reasons for the decline in quarterly revenue, verify the numbers, and prepare a report."

The agent decides which documents to inspect, what information to extract, which calculations to perform, whether additional evidence is required, and whether the findings satisfy the objective.

The agent can revise its plan based on the results of its actions.

This creates a controlled cycle of:

**Observe → Plan → Act → Evaluate → Adapt → Verify → Complete**

The system remains bounded by explicit execution limits, data-access permissions, and human approval requirements.

## 2.3 Project vision

The vision is to build a general-purpose analytical agent that treats documents as evidence sources rather than merely as text to summarize.

The system should be able to answer both informational and analytical questions, including:

- What are the main findings in these documents?
- How did performance change between two periods?
- Which business segments contributed most to a decline?
- Do the figures in the PDF agree with the spreadsheet?
- What evidence supports a particular conclusion?
- Which questions remain unanswered because the documents lack sufficient information?
- What additional analysis would help resolve an inconsistency?

The final output should include conclusions, calculations, source references, assumptions, uncertainties, and supporting visualizations where appropriate.

---

# 3. Problem Statement

Existing document-analysis workflows often rely on manual inspection, separate spreadsheet calculations, conventional search, and independent report preparation.

These workflows introduce several challenges:

1. **Fragmented information:** Relevant facts are distributed across multiple files and formats.
2. **Limited analytical automation:** Document retrieval systems may not execute numerical calculations or statistical comparisons.
3. **Weak multi-step planning:** Conventional question-answering systems may not explicitly organize complex investigations into dependent subtasks.
4. **Insufficient verification:** Generated conclusions may contain unsupported statements or incorrectly interpreted figures.
5. **Poor adaptability:** Fixed pipelines may fail when documents are incomplete, tables are malformed, or sources disagree.
6. **Limited traceability:** Users may find it difficult to identify the exact document, page, table, or spreadsheet cell supporting a claim.
7. **Limited persistent context:** Repeated investigations may require the system to rediscover previously established facts.
8. **Insufficient human control:** Fully automated workflows can produce consequential outputs without appropriate review.

Therefore, the problem is to design and implement an agentic document-analysis system that autonomously plans and executes multi-step investigations over heterogeneous data sources while preserving analytical correctness, evidence traceability, adaptability, and human oversight.

---

# 4. Aim and Objectives

## 4.1 Primary aim

To develop an autonomous, evidence-driven Agentic AI system that understands multi-format documents, performs analytical operations, adapts its investigation strategy, and produces verifiable reports in response to user-defined goals.

## 4.2 Specific objectives

### Objective 1: Multi-format document understanding

Develop a document ingestion pipeline capable of processing PDF, DOCX, XLSX, and CSV files while preserving relevant source metadata.

### Objective 2: Context-aware information retrieval

Implement a practical RAG system that retrieves relevant passages, tables, and records according to the user's analytical objective.

### Objective 3: Autonomous task planning

Enable the agent to decompose a complex goal into smaller tasks with explicit dependencies and completion conditions.

### Objective 4: Tool-based analytical execution

Provide tools for numerical calculations, data cleaning, statistical comparisons, spreadsheet analysis, visualization, and report generation.

### Objective 5: Evidence-grounded reasoning

Require the agent to associate important conclusions with supporting evidence and distinguish documented facts from assumptions or hypotheses.

### Objective 6: Adaptive investigation

Enable the agent to identify missing information, investigate contradictory evidence, recover from tool failures, and update its plan.

### Objective 7: Persistent memory

Maintain task history, verified findings, source metadata, and reusable context across sessions.

### Objective 8: Human-in-the-loop supervision

Allow users to approve analytical plans, review important findings, correct assumptions, and authorize sensitive actions.

### Objective 9: Reliability evaluation

Evaluate the system using predefined datasets, reference answers, calculation checks, citation verification, and controlled failure scenarios.

---

# 5. Scope of the Project

## 5.1 Included functionality

The proposed initial system will support:

- Uploading and organizing multiple documents.
- Extracting text, tables, and metadata.
- Parsing spreadsheets and structured datasets.
- Searching across a document collection.
- Retrieving source-grounded passages.
- Planning multi-step analytical tasks.
- Selecting tools based on task requirements.
- Executing deterministic calculations with Python.
- Comparing numerical values across periods.
- Identifying missing values and conflicting figures.
- Producing charts and summary tables.
- Verifying calculations and source references.
- Maintaining persistent investigation memory.
- Requesting human approval at designated checkpoints.
- Generating downloadable analytical reports.

## 5.2 Initial exclusions

The initial version will not require:

- Training a large language model from scratch.
- Autonomous access to arbitrary websites.
- Unrestricted execution of generated code.
- Automatic modification of original documents.
- Autonomous financial transactions or business decisions.
- Guaranteed interpretation of every scanned or visually complex document.
- Automatic acceptance of every generated conclusion as correct.

Advanced capabilities can be added after the core workflow is stable.

## 5.3 Target use cases

The architecture is designed for general document intelligence, with example applications in:

- Business performance analysis.
- Financial and operational reporting.
- Academic research synthesis.
- Policy and compliance document review.
- Scientific report analysis.
- Dataset exploration.
- Project and operational documentation.

These are potential application domains, not claims that the initial implementation will automatically satisfy every domain's regulatory requirements.

---

# 6. Functional Requirements

| ID | Requirement | Expected behavior |
|---|---|---|
| FR-01 | Document ingestion | Accept supported file formats and record metadata. |
| FR-02 | Content extraction | Extract text, tables, and structured data where available. |
| FR-03 | Contextual retrieval | Retrieve relevant content using the user's goal. |
| FR-04 | Goal interpretation | Convert the request into an explicit analytical objective. |
| FR-05 | Task planning | Produce a sequence of subtasks and dependencies. |
| FR-06 | Tool selection | Select suitable retrieval, calculation, or analysis tools. |
| FR-07 | Data analysis | Execute calculations using deterministic Python functions. |
| FR-08 | Cross-source comparison | Compare figures and statements from multiple files. |
| FR-09 | Evidence tracking | Link findings to source locations. |
| FR-10 | Adaptive execution | Revise the plan when evidence is insufficient or execution fails. |
| FR-11 | Persistent memory | Store task history and reusable findings. |
| FR-12 | Verification | Check calculations, citations, and claim support. |
| FR-13 | HITL | Request approval or clarification at configured checkpoints. |
| FR-14 | Report generation | Produce a structured report with findings and supporting evidence. |
| FR-15 | Audit trail | Record tool calls, important decisions, failures, and approvals. |

---

# 7. Non-Functional Requirements

## 7.1 Reliability

The system should use deterministic code for arithmetic and structured-data calculations wherever possible. It should not rely exclusively on language-model-generated numbers.

## 7.2 Explainability

Important findings should include source references, calculation methods, assumptions, and an explanation of how the conclusion follows from the available evidence.

## 7.3 Performance

The system should process documents efficiently through configurable batch sizes, caching, selective retrieval, and bounded agent iterations.

Performance targets will be established after a baseline implementation and measured on a representative workload.

## 7.4 Scalability

The architecture should separate ingestion, retrieval, analysis, orchestration, memory, and reporting so that individual components can be replaced or scaled independently.

## 7.5 Security

Uploaded files must be treated as untrusted inputs. Tool permissions, file-access boundaries, code-execution restrictions, and sensitive-data handling must be enforced.

## 7.6 Maintainability

Each tool and workflow stage should have a defined interface, explicit input/output schemas, error handling, and automated tests.

## 7.7 Reproducibility

The system should preserve source versions, analysis parameters, calculation outputs, model configuration, and execution logs so that results can be independently checked.

---

# 8. Six Agentic AI Characteristics

The project will explicitly implement and test all six characteristics.

## 8.1 Autonomy

**Definition:** The ability to perform appropriate intermediate actions without requiring the user to specify every step.

**Implementation:**

The agent receives a goal and independently selects actions such as document search, table extraction, calculation, or further evidence retrieval.

For example, if asked to explain a revenue decline, it can determine that it must first find revenue figures for two periods before investigating explanatory statements.

**Expected behavior:**

- Select the next appropriate tool.
- Execute permitted operations.
- Track progress toward completion.
- Continue when the current result is insufficient.
- Stop when the objective is satisfied or a defined limit is reached.

Autonomy does not mean unrestricted operation. The system should obey a maximum step count, time budget, tool permissions, and approval policies.

## 8.2 Goal orientation

**Definition:** The ability to choose actions according to a desired outcome.

Each task should have:

- A goal description.
- Required deliverables.
- Constraints.
- Completion criteria.
- A verification checklist.

For example:

**Goal:** Explain the decline in quarterly revenue.

**Completion conditions:**

1. Identify comparable revenue figures.
2. Verify the period definitions and units.
3. Calculate absolute and percentage changes.
4. Identify relevant explanatory evidence.
5. Distinguish supported causes from possible explanations.
6. Provide source references.
7. State unresolved uncertainties.

The agent should not declare success simply because it generated a long report.

## 8.3 Planning

**Definition:** The ability to break a complex task into smaller, ordered operations.

A sample plan could be:

1. Inventory available files.
2. Identify the relevant periods and metrics.
3. Retrieve financial tables and explanatory passages.
4. Extract and normalize figures.
5. Calculate period-over-period changes.
6. Compare segment-level contributions.
7. Search for explanations in narrative reports.
8. Check conflicting figures.
9. Verify all calculations and citations.
10. Generate the final report.

The orchestrator should track dependencies. For example, segment contribution analysis cannot be completed reliably until segment-level values have been extracted and validated.

The plan should be updated when new evidence changes the direction of the investigation.

## 8.4 Reasoning

**Definition:** The ability to evaluate evidence, compare alternatives, and select appropriate actions.

Reasoning is implemented through structured task decisions, evidence comparison, and verification—not merely through free-form text generation.

For example, the agent may identify two candidate explanations for a revenue decline:

- A reduction in sales volume.
- A reduction in average selling price.

It should calculate the available volume and price changes, examine supporting records, and determine which explanation is supported.

If the required evidence is absent, it should report that the cause cannot be conclusively established.

The system should store concise decision summaries and supporting evidence rather than relying on inaccessible or unverifiable internal reasoning traces.

## 8.5 Adaptability

**Definition:** The ability to modify behavior when the current approach is unsuccessful or new information becomes available.

Example:

The agent attempts to extract a table from a PDF, but the table extraction returns incomplete rows.

The agent can:

1. Detect the extraction problem.
2. Check whether the page contains selectable text.
3. Try an alternative extraction method.
4. Use OCR if the document is scanned and OCR is configured.
5. Compare the extracted values against another source.
6. Flag unresolved discrepancies for human review.

Adaptability must be bounded. The agent should not retry indefinitely or invent replacement data.

## 8.6 Content awareness

**Definition:** The ability to interpret a task in the context of relevant documents, data structures, source locations, and previous findings.

The system should preserve:

- Document identity and version.
- Page numbers and section headings.
- Spreadsheet sheet names and cell ranges.
- Table headers and units.
- Reporting periods and date ranges.
- Relationships between records.
- Retrieval provenance.
- Previous verified findings.

For example, a value of `125` cannot be interpreted correctly without knowing whether it represents units, thousands of rupees, millions of dollars, or a percentage.

The system must therefore preserve units, labels, period definitions, and context during extraction and analysis.

---

# 9. Five Core Architectural Components

## 9.1 Brain

The Brain is the decision-making component, typically implemented using an LLM with structured output and tool-calling capabilities.

Its responsibilities include:

- Interpreting the user's goal.
- Generating and refining task plans.
- Selecting appropriate tools.
- Interpreting retrieved evidence.
- Identifying unresolved questions.
- Summarizing findings.
- Proposing the next action.

The Brain should not be responsible for performing every operation directly. Numerical calculations, parsing, file operations, and verification should be delegated to specialized tools.

## 9.2 Orchestrator

The Orchestrator coordinates the complete workflow.

Recommended implementation: LangGraph, with explicit state, nodes, conditional edges, persistence, and human approval checkpoints.

Its responsibilities include:

- Maintaining execution state.
- Managing the task plan.
- Routing tasks to tools.
- Tracking task completion.
- Handling errors and retries.
- Applying iteration and resource limits.
- Routing failed verification back to investigation.
- Managing approval and interruption points.
- Determining when the task is complete.

The orchestrator should enforce workflow rules rather than simply forwarding every response from one LLM call to another.

## 9.3 Tools

Tools provide controlled access to actual document-processing and analytical capabilities.

### Document tools

- PDF text extraction.
- DOCX parsing.
- Excel workbook inspection.
- CSV loading.
- Table extraction.
- OCR for scanned documents, when needed.

### Retrieval tools

- Keyword search.
- Vector similarity search.
- Hybrid retrieval.
- Metadata filtering.
- Source passage retrieval.

### Analytical tools

- Data cleaning.
- Missing-value analysis.
- Numerical calculations.
- Statistical summaries.
- Period-over-period comparison.
- Segment contribution analysis.
- Chart generation.

### Verification tools

- Calculation recomputation.
- Source-reference validation.
- Unit and period checks.
- Claim-to-evidence support checks.
- Duplicate and conflicting-value detection.

### Reporting tools

- Markdown report generation.
- PDF export.
- Table and chart insertion.
- Source appendix generation.

Each tool should have a clear contract, validated inputs, structured outputs, and predictable error behavior.

## 9.4 Memory

Memory enables continuity within and across investigations.

The proposed architecture distinguishes four types of memory.

**A. Working memory**

Stores the current task state, active plan, completed steps, retrieved evidence, and unresolved questions.

**B. Episodic memory**

Stores previous investigation records, tool outcomes, errors, user corrections, and final results.

**C. Semantic memory**

Stores reusable facts, document metadata, verified definitions, and indexed document content.

**D. Procedural memory**

Stores reusable analytical procedures, approved workflow templates, and tool-use instructions.

Persistent memory should distinguish source facts from model-generated interpretations. Each stored finding should include provenance, timestamps, and a verification status where applicable.

A recommended initial implementation is SQLite for structured task history and ChromaDB for vector retrieval. These are complementary components, not interchangeable storage systems.

## 9.5 Human-in-the-Loop

HITL allows a human to review or control selected operations.

Recommended checkpoints include:

- Approval of a complex analysis plan.
- Clarification of ambiguous reporting periods.
- Resolution of material source conflicts.
- Approval before accessing sensitive data.
- Approval before running nontrivial code in an isolated environment.
- Review of important conclusions before report finalization.

The system should support approve, reject, edit, and request-clarification actions.

Human approval should be mandatory for configured high-risk actions, not merely offered as an optional interface feature.

---

# 10. Overall System Architecture

The architecture is organized into six logical layers.

## Layer 1: User interaction

The user uploads files, defines an objective, specifies constraints, and receives progress updates and the final report.

Proposed interface: Streamlit.

## Layer 2: Agent orchestration

The Orchestrator maintains task state, controls execution, manages the plan, and routes tasks through the workflow.

## Layer 3: Intelligence and decision-making

The Brain interprets the objective, selects actions, evaluates evidence, and decides whether additional investigation is required.

## Layer 4: Tool execution

Specialized tools perform parsing, retrieval, calculations, data comparisons, verification, and report generation.

## Layer 5: Memory and retrieval

The memory subsystem maintains task history and reusable knowledge. The retrieval subsystem indexes document content and returns relevant evidence.

## Layer 6: Governance and observability

This layer enforces permissions, execution limits, human approvals, audit logging, and security policies.

### Architectural flow

User goal and documents  
↓  
Document ingestion and metadata extraction  
↓  
Task interpretation and planning  
↓  
Orchestrator selects the next operation  
↓  
Brain chooses an appropriate tool  
↓  
Tool execution and structured result  
↓  
Memory update and evidence collection  
↓  
Evaluation and verification  
↓  
Sufficient evidence?

- **Yes:** Generate the report and present it for any required approval.
- **No:** Update the plan and continue the investigation within configured limits.
- **Unresolved:** Ask the user for clarification or explicitly report the limitation.

This architecture supports controlled iteration rather than an uncontrolled chain of model-generated actions.

---

# 11. Detailed Agent Workflow

## Step 1: Document ingestion

The user uploads a collection of supported documents.

The ingestion module:

1. Validates file extensions and file size.
2. Computes file hashes for duplicate detection.
3. Assigns document identifiers.
4. Extracts available text and tables.
5. Records page, sheet, section, and source metadata.
6. Identifies potentially scanned or malformed documents.
7. Reports extraction failures.

The original files should remain unchanged.

## Step 2: Content normalization

The system converts extracted content into a common internal representation.

For example, a source record might contain:

- Document ID.
- Document type.
- Text or table content.
- Page number or sheet name.
- Cell range or table identifier.
- Reporting period.
- Units.
- Extraction method.
- Extraction confidence, if supported by the method.

This representation allows the agent to work across multiple file types without losing the original source location.

## Step 3: Goal interpretation

The Brain converts the natural-language request into a structured task.

Example:

- Goal: Explain quarterly revenue decline.
- Primary metric: Revenue.
- Comparison: Current quarter versus previous quarter.
- Required analysis: Overall and segment-level changes.
- Required evidence: Relevant figures and explanatory statements.
- Deliverable: Sourced analytical report.
- Constraints: Use only supplied documents.

If the reporting period or metric is ambiguous and materially affects the result, the agent should ask for clarification rather than silently choosing an interpretation.

## Step 4: Planning

The Brain generates a structured plan. The Orchestrator validates the plan and stores it in the current task state.

Each step should contain:

- Step identifier.
- Description.
- Required inputs.
- Expected output.
- Dependencies.
- Selected tool or tool category.
- Completion criteria.
- Status.

The plan should be executable and inspectable, not merely a paragraph describing what the agent intends to do.

## Step 5: Evidence retrieval

The retrieval system identifies relevant passages, tables, and records.

It may combine:

- Keyword-based retrieval.
- Vector similarity search.
- Metadata filtering.
- Exact metric and period matching.
- Table-aware retrieval.

For a financial question, the system should prioritize records containing the requested metric, reporting period, segment, and unit.

Retrieved evidence should include source identifiers and locations.

## Step 6: Structured data extraction

Relevant figures are converted into typed, structured records.

For example:

| Period | Segment | Revenue | Unit | Source |
|---|---|---:|---|---|
| Q1 | Segment A | 500 | ₹ lakh | Workbook A, Revenue sheet |
| Q2 | Segment A | 420 | ₹ lakh | Workbook A, Revenue sheet |

These values are illustrative only.

The extraction process must preserve the original units and distinguish actual data from inferred or missing values.

## Step 7: Computational analysis

The agent invokes deterministic Python tools for calculations.

Examples include:

- Absolute change.
- Percentage change.
- Contribution by segment.
- Summary statistics.
- Missing-value analysis.
- Outlier screening.
- Trend comparisons.
- Chart generation.

The Brain determines which analysis is appropriate, while the tool performs the computation.

## Step 8: Cross-document reconciliation

The system compares overlapping facts across files.

For example, it may find that the quarterly report lists revenue as ₹420 lakh while a spreadsheet lists ₹425 lakh.

Instead of arbitrarily selecting one figure, it should:

1. Preserve both values.
2. Verify reporting periods and units.
3. Check whether the figures use different definitions.
4. Examine source dates and document versions.
5. Identify possible rounding differences.
6. Request human review if the discrepancy remains material.

## Step 9: Evidence-based reasoning

The Brain interprets the verified numerical results alongside narrative evidence.

It should distinguish three categories:

- **Observed fact:** Directly supported by a source or calculation.
- **Supported interpretation:** A conclusion reasonably supported by multiple pieces of evidence.
- **Hypothesis:** A plausible explanation not established by the available evidence.

For example, a decline in total revenue and a corresponding decline in sales volume may be observed facts. Concluding that reduced sales volume caused the entire decline requires checking other relevant factors, such as prices, product mix, and segment changes.

## Step 10: Verification

A separate verification stage checks:

- Whether calculations can be reproduced.
- Whether the comparison periods are consistent.
- Whether units have been normalized correctly.
- Whether important claims have supporting evidence.
- Whether citations point to the correct source.
- Whether the report contains contradictions.
- Whether important limitations are disclosed.

The verifier should not simply ask another LLM whether the answer is correct. It should use deterministic checks wherever possible.

## Step 11: Adaptive replanning

If the verification stage identifies a problem, the Orchestrator decides whether to:

- Retrieve additional evidence.
- Re-extract a table.
- Run a different calculation.
- Investigate a conflicting source.
- Request clarification.
- Stop and report an unresolved limitation.

The system should maintain a maximum number of iterations and avoid repeating an unsuccessful action without a meaningful change in strategy.

## Step 12: Report generation

The reporting module creates the final deliverable.

A report should contain:

1. Executive summary.
2. Question and scope.
3. Data sources.
4. Methodology.
5. Key findings.
6. Verified calculations.
7. Charts and comparison tables.
8. Supporting evidence and citations.
9. Inconsistencies and limitations.
10. Recommendations, where justified.
11. Audit information and analysis parameters.

## Step 13: Completion and memory update

The agent evaluates its completion criteria.

If all mandatory conditions are satisfied, it marks the task complete. Otherwise, it identifies unresolved requirements.

The final result and relevant task metadata are saved in persistent memory according to the configured retention policy.

---

# 12. Retrieval-Augmented Generation (RAG) Design

RAG is an important part of the system, but it is not the agent itself.

RAG provides access to relevant information. The agent decides what information to retrieve, when to retrieve it, how to analyze it, and whether the evidence is sufficient.

## 12.1 Ingestion pipeline

The RAG pipeline consists of:

1. Document parsing.
2. Text and table extraction.
3. Content normalization.
4. Chunk creation.
5. Metadata assignment.
6. Embedding generation.
7. Vector indexing.
8. Retrieval and reranking.
9. Source-grounded response generation.

## 12.2 Chunking strategy

Chunking should preserve meaningful boundaries where possible.

Examples include:

- PDF sections and paragraphs.
- Document headings and subsections.
- Table groups with their headers.
- Spreadsheet records with column labels.
- Small structured records containing all necessary context.

A fixed-size chunking strategy may be used for prose, but tables should not be divided in a way that separates values from their headers or units.

## 12.3 Metadata

Each indexed record should preserve fields such as:

- Document ID.
- File name.
- File type.
- Page number.
- Section heading.
- Sheet name.
- Table identifier.
- Row or cell range.
- Reporting period.
- Units.
- Content type.

This metadata supports precise filtering and source attribution.

## 12.4 Hybrid retrieval

A hybrid retrieval strategy combines lexical and semantic search.

Lexical search is useful for exact identifiers, account codes, dates, and metric names.

Vector search is useful for semantically related descriptions and differently worded questions.

A reranking stage may reorder candidate passages according to their relevance to the specific question.

The retrieval system should also support metadata filters and exact lookups for numerical facts.

## 12.5 Table-aware retrieval

Tables require special treatment because the meaning of a value depends on row labels, column headers, units, and reporting periods.

A retrieved table record should retain the contextual information required to interpret its values.

For quantitative questions, the system should retrieve structured values and use a computation tool instead of asking the language model to perform arithmetic from a loosely formatted table.

## 12.6 Evidence-grounded generation

Each material claim should link to one or more evidence records.

A claim record may contain:

- Claim ID.
- Claim text.
- Claim category.
- Supporting evidence IDs.
- Calculation references.
- Verification status.
- Known limitations.

The report generator should avoid presenting unsupported claims as established facts.

---

# 13. Analytical Engine

The analytical engine converts extracted data into verifiable results.

## 13.1 Period-over-period comparison

Let:

- \(R_1\) represent revenue in the earlier period.
- \(R_2\) represent revenue in the later period.

The absolute change is:

\[
\Delta R = R_2-R_1
\]

The percentage change is:

\[
\%\Delta R =
\frac{R_2-R_1}{R_1}\times100
\]

This formula requires a nonzero baseline. If the earlier value is zero, the percentage change is undefined and should be reported accordingly.

## 13.2 Segment contribution

For segment \(i\), define the absolute change as:

\[
\Delta R_i=R_{i,2}-R_{i,1}
\]

The contribution of segment \(i\) to the total absolute change is:

\[
C_i=\frac{\Delta R_i}{\Delta R_{\text{total}}}\times100
\]

This formula is meaningful when the total change is nonzero and the segment values reconcile with the total.

When the overall change is negative, a segment with a negative change contributes to the decline, while a positive change offsets it. Contributions can therefore exceed 100% or be negative when segments move in different directions.

## 13.3 Data-quality checks

The analytical engine should detect:

- Missing values.
- Duplicate records.
- Inconsistent date formats.
- Inconsistent units.
- Unexpected column names.
- Invalid numerical values.
- Possible outliers.
- Duplicate periods.
- Aggregation mismatches.
- Conflicting totals.

Outliers should be flagged for investigation rather than automatically deleted.

## 13.4 Statistical analysis

Depending on the question, the system may calculate:

- Mean and median.
- Standard deviation.
- Correlation.
- Distribution summaries.
- Trend estimates.
- Grouped aggregations.
- Anomaly indicators.

The agent should choose methods appropriate to the data and state relevant assumptions.

Correlation must not be presented as proof of causation.

## 13.5 Visual analytics

Matplotlib can produce:

- Period comparison charts.
- Segment contribution charts.
- Trend plots.
- Distribution plots.
- Missing-value summaries.

Charts should have meaningful labels, units, legends, and time ranges.

Every chart should be based on validated data and include enough context to avoid misleading interpretation.

---

# 14. Agent State and Orchestration

The system should maintain an explicit state object that persists across workflow steps.

A conceptual task state includes:

- `task_id`
- `user_goal`
- `constraints`
- `document_manifest`
- `plan`
- `completed_steps`
- `pending_steps`
- `retrieved_evidence`
- `extracted_data`
- `analysis_results`
- `verification_results`
- `unresolved_questions`
- `retry_count`
- `approval_status`
- `final_report_reference`

This is a conceptual schema; the implementation should define concrete types and validation rules.

## 14.1 Workflow nodes

Recommended LangGraph nodes include:

1. `ingest_documents`
2. `interpret_goal`
3. `create_plan`
4. `validate_plan`
5. `retrieve_evidence`
6. `extract_structured_data`
7. `run_analysis`
8. `reconcile_sources`
9. `verify_findings`
10. `evaluate_completion`
11. `request_human_review`
12. `generate_report`
13. `save_memory`

## 14.2 Conditional transitions

The workflow should support branches such as:

- Extraction successful → Continue to analysis.
- Extraction incomplete → Try an alternative permitted method.
- Evidence sufficient → Verify findings.
- Evidence insufficient → Retrieve more evidence.
- Verification failed → Replan or correct the analysis.
- Human approval required → Pause and request approval.
- Retry limit reached → Stop safely and report unresolved issues.

## 14.3 Why LangGraph?

LangGraph is suitable because the proposed system requires stateful, multi-step execution, conditional routing, checkpointing, and interruptible workflows.

Its use does not automatically make the system agentic. The agentic behavior must be implemented through the decision logic, tool selection, feedback loop, memory, and completion criteria.

---

# 15. Memory Architecture and Data Persistence

## 15.1 SQLite

SQLite should store structured information, including:

- Task records.
- Document metadata.
- Plan steps.
- Tool execution logs.
- Calculation records.
- Evidence references.
- Approval events.
- Final report metadata.

## 15.2 ChromaDB

ChromaDB can store document embeddings and associated metadata for semantic retrieval.

It should not be treated as the authoritative store for exact numerical records or task state.

## 15.3 Persistent task history

Each completed investigation should preserve:

- User objective.
- Document versions or hashes.
- Execution configuration.
- Relevant evidence identifiers.
- Verified results.
- Unresolved limitations.
- Final report reference.

## 15.4 Memory reliability

Memory should not turn an old model-generated statement into a permanent fact.

Stored findings should be traceable to their sources and classified according to their verification status.

If a source document changes, the system should be able to identify which stored findings depend on the older version.

## 15.5 Privacy and retention

Users should have control over stored documents and investigation history.

The implementation should define retention periods, deletion behavior, access restrictions, and whether uploaded content is sent to an external model provider.

---

# 16. Human-in-the-Loop and Safety Controls

HITL is a core architectural component rather than a decorative feature.

## 16.1 Approval policies

The system should support different approval levels.

**Low-risk actions:** Reading permitted files, searching indexed content, and running predefined calculations.

**Moderate-risk actions:** Changing analytical assumptions, selecting between conflicting sources, or launching expensive processing tasks.

**High-risk actions:** Accessing restricted data, executing nontrivial generated code, or sharing reports externally.

High-risk actions should require explicit authorization.

## 16.2 Prompt injection protection

Documents may contain instructions that attempt to influence the agent.

The system must treat document content as untrusted evidence, not as privileged system instructions.

Safeguards include:

- Separating system policy from retrieved document text.
- Restricting tool permissions.
- Validating tool arguments.
- Preventing documents from granting themselves new permissions.
- Requiring approval for sensitive actions.

## 16.3 Safe code execution

If the Brain can generate Python code, it must not execute that code directly in the main application process without safeguards.

Prefer predefined analytical tools. If dynamic execution is required, use an isolated environment with restricted file access, network restrictions, time limits, memory limits, and controlled dependencies.

## 16.4 Source integrity

The system should preserve the original documents, record source hashes where appropriate, and maintain a traceable link between extracted evidence and source files.

## 16.5 Uncertainty reporting

When the available information is insufficient, the agent should explicitly state:

- What could be verified.
- What remains uncertain.
- Which evidence is missing.
- What additional information would resolve the uncertainty.

A correct refusal to draw an unsupported conclusion is preferable to an invented explanation.

---

# 17. Technology Stack and Justification

| Technology | Role | Reason for selection |
|---|---|---|
| Python | Core implementation | Strong ecosystem for document processing and analytics |
| LangGraph | Agent orchestration | Stateful workflows, conditional routing and checkpointing |
| LLM API or compatible local model | Brain | Natural-language interpretation, planning and tool selection |
| Pydantic | Schema validation | Validates structured plans, tool inputs and results |
| PyMuPDF | PDF processing | Text extraction and page-level source tracking |
| python-docx | DOCX processing | Extracts Word document content |
| pandas | Tabular analysis | Data cleaning, grouping and comparison |
| openpyxl | Excel processing | Reads worksheets, cell values and workbook structures |
| sentence-transformers | Embeddings | Creates semantic representations for retrieval |
| ChromaDB | Vector retrieval | Stores document embeddings and metadata |
| SQLite | Persistent state | Stores tasks, logs, approvals and structured findings |
| NumPy | Numerical operations | Efficient numerical computation |
| Matplotlib | Visualization | Generates analytical charts |
| Streamlit | User interface | Rapid implementation of an interactive dashboard |
| ReportLab | PDF export | Generates formatted analytical reports |
| pytest | Testing | Validates calculations, tools and workflow behavior |

OCR can be added for scanned documents. A suitable OCR engine should be selected based on the expected document types and deployment environment.

The project should begin with a minimal dependency set and add optional components only when a clear requirement exists.

---

# 18. Proposed Software Architecture and Directory Structure

A modular project structure could be organized as follows:

```text
autonomous-document-analyst/
│
├── app.py
├── config/
│   ├── settings.py
│   ├── agent_policy.yaml
│   └── tool_registry.py
│
├── src/
│   ├── ingestion/
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── excel_parser.py
│   │   ├── csv_parser.py
│   │   └── metadata.py
│   │
│   ├── retrieval/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── keyword_search.py
│   │   └── hybrid_retrieval.py
│   │
│   ├── agent/
│   │   ├── brain.py
│   │   ├── planner.py
│   │   ├── orchestrator.py
│   │   ├── state.py
│   │   ├── workflow.py
│   │   └── completion.py
│   │
│   ├── tools/
│   │   ├── document_search.py
│   │   ├── table_extraction.py
│   │   ├── data_cleaning.py
│   │   ├── numerical_analysis.py
│   │   ├── source_reconciliation.py
│   │   ├── chart_generation.py
│   │   └── report_export.py
│   │
│   ├── memory/
│   │   ├── sqlite_store.py
│   │   ├── vector_memory.py
│   │   ├── task_history.py
│   │   └── provenance.py
│   │
│   ├── verification/
│   │   ├── calculation_checks.py
│   │   ├── citation_checks.py
│   │   ├── claim_verification.py
│   │   └── consistency_checks.py
│   │
│   ├── human_review/
│   │   ├── approval.py
│   │   └── review_queue.py
│   │
│   └── reporting/
│       ├── report_builder.py
│       └── templates.py
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   ├── test_calculations.py
│   ├── test_verification.py
│   └── test_agent_workflow.py
│
├── data/
│   ├── sample_documents/
│   ├── processed/
│   └── evaluation/
│
├── outputs/
├── requirements.txt
├── .env.example
└── README.md
```

This is a proposed structure. The actual implementation can begin with fewer modules and split them as the system grows. Sensitive environment variables and API keys must not be committed to version control.

---

# 19. Database Design

A relational schema will help preserve the relationships between documents, tasks, evidence, calculations, and reports.

## 19.1 Documents

Suggested fields:

- `document_id`
- `file_name`
- `file_type`
- `content_hash`
- `ingestion_timestamp`
- `extraction_status`
- `document_version`

## 19.2 Tasks

Suggested fields:

- `task_id`
- `user_goal`
- `task_status`
- `created_at`
- `completed_at`
- `completion_reason`

## 19.3 Plan steps

Suggested fields:

- `step_id`
- `task_id`
- `description`
- `dependencies`
- `status`
- `attempt_count`
- `result_reference`

## 19.4 Evidence

Suggested fields:

- `evidence_id`
- `document_id`
- `location_type`
- `location_reference`
- `content_hash`
- `extraction_method`
- `verification_status`

## 19.5 Analysis results

Suggested fields:

- `analysis_id`
- `task_id`
- `metric_name`
- `input_references`
- `method`
- `result`
- `units`
- `verification_status`

## 19.6 Approval records

Suggested fields:

- `approval_id`
- `task_id`
- `action_description`
- `decision`
- `timestamp`
- `review_comments`

Foreign-key relationships and appropriate indexes should be added where required. Large extracted document contents may be stored separately, with stable references maintained in the database.

---

# 20. End-to-End Example

## Scenario: Investigating a quarterly revenue decline

Assume the user uploads:

- `Quarterly_Report.pdf`
- `Revenue_Data.xlsx`
- `Segment_Performance.csv`

The user asks:

"Explain why revenue declined from Q1 to Q2. Identify the main contributing segments and support the explanation with evidence."

The following figures are hypothetical and are used only to demonstrate the workflow.

## Step 1: Inventory

The agent identifies three documents and determines that the Excel workbook contains segment-level figures.

## Step 2: Plan

The agent creates subtasks to extract overall revenue, calculate changes, compare segments, search narrative explanations, and verify the report.

## Step 3: Extract data

Suppose the workbook contains:

| Segment | Q1 revenue | Q2 revenue |
|---|---:|---:|
| A | 500 | 420 |
| B | 300 | 280 |
| C | 200 | 200 |
| Total | 1,000 | 900 |

Assume all figures are expressed in the same units.

## Step 4: Calculate the overall change

\[
\Delta R=900-1000=-100
\]

\[
\%\Delta R=\frac{-100}{1000}\times100=-10\%
\]

Revenue declined by 100 units, or 10%.

## Step 5: Identify contributing segments

Segment A changed by:

\[
420-500=-80
\]

Segment B changed by:

\[
280-300=-20
\]

Segment C changed by:

\[
200-200=0
\]

The contributions to the overall decline are:

- Segment A: 80% of the decline.
- Segment B: 20% of the decline.
- Segment C: no contribution to the decline.

These contributions reconcile with the total decline of 100 units.

## Step 6: Investigate explanatory evidence

The agent searches the quarterly report for statements concerning Segment A and Segment B.

Suppose the report documents lower order volumes for Segment A. The agent links that statement to its page reference and distinguishes it from the numerical evidence.

If the report does not explain the decline in Segment B, the agent should not invent a cause for that segment.

## Step 7: Verify

The verification stage checks:

- Whether Q1 and Q2 refer to comparable periods.
- Whether all segment figures use the same units.
- Whether segment totals equal the reported overall values.
- Whether the calculated percentage change is correct.
- Whether the report's explanation is supported by the cited passage.

## Step 8: Generate findings

A properly qualified finding could state:

"Revenue declined by 10% from Q1 to Q2. Segment A accounted for 80% of the absolute decline, while Segment B accounted for the remaining 20%. The quarterly report attributes lower order volumes to Segment A. The available evidence does not establish the reason for Segment B's decline."

The report should attach the actual source locations from the uploaded files.

## Step 9: Adapt if evidence conflicts

If the PDF reports total revenue of 905 rather than 900, the agent should investigate the discrepancy, check units and definitions, and disclose the unresolved difference if it cannot be reconciled.

This example demonstrates the difference between retrieving a report and conducting an autonomous investigation.

---

# 21. Testing and Evaluation Methodology

A serious Agentic AI project should measure both analytical correctness and agent behavior.

## 21.1 Evaluation dataset

Prepare a controlled collection of documents containing:

- Clean PDF reports.
- Excel workbooks with known numerical totals.
- CSV datasets.
- Documents with conflicting values.
- Documents with missing fields.
- Duplicate files.
- Scanned PDFs, if OCR is included.
- Questions with known reference answers.
- Questions that cannot be answered from the available evidence.

The evaluation dataset should contain reference calculations and expected source locations.

## 21.2 Core metrics

### A. Numerical accuracy

Compare calculated outputs against independently computed reference values.

For a numeric result \(y\) and reference value \(y^*\), absolute error is:

\[
E_{\text{abs}}=|y-y^*|
\]

Percentage error may be calculated when the reference value is nonzero and percentage error is meaningful.

Exact-match checks are appropriate for many financial calculations after accounting for declared rounding rules.

### B. Retrieval quality

Measure:

- Precision@k.
- Recall@k.
- Mean Reciprocal Rank.
- Normalized Discounted Cumulative Gain, where appropriate.

These metrics evaluate whether relevant evidence appears among the retrieved results.

### C. Citation accuracy

Measure the proportion of generated claims with valid source references and the proportion of citations that actually support their associated claims.

A citation that points to a real page but does not support the statement should not be counted as correct.

### D. Evidence coverage

Measure the proportion of material claims that have sufficient supporting evidence.

### E. Task completion

Measure the percentage of test tasks that satisfy their predefined completion conditions.

### F. Tool efficiency

Track:

- Number of tool calls.
- Number of failed tool calls.
- Number of retries.
- Execution duration.
- Token consumption or model cost, where applicable.

### G. Adaptability

Measure whether the agent successfully recovers from predefined failures, such as malformed tables, missing evidence, or conflicting source values.

### H. Human intervention

Track the number of approval requests, clarification requests, and manual corrections required for each task.

The objective is not to eliminate necessary human intervention. It is to use it where it improves safety and reliability.

## 21.3 Proposed evaluation table

| Metric | Evaluation method | Target setting |
|---|---|---|
| Numerical correctness | Compare with reference calculations | Set a high correctness target on supported calculations |
| Citation precision | Manually or programmatically verify cited evidence | Minimize unsupported citations |
| Evidence coverage | Audit material claims | Require evidence for all material factual claims |
| Task completion | Compare outputs with acceptance criteria | Establish baseline, then improve |
| Retrieval recall | Compare retrieval with annotated relevant passages | Tune against the evaluation corpus |
| Failure recovery | Run controlled failure scenarios | Recover when a safe alternative exists |
| Resource efficiency | Measure tool calls, runtime, and cost | Establish a bounded operating budget |
| Auditability | Check source and execution trace completeness | Preserve traceability for all material results |

These are evaluation objectives, not achieved results. Numerical targets should be specified after the test dataset and workload are defined.

## 21.4 Ablation study

To determine which architectural components improve performance, compare several controlled configurations:

1. **Baseline:** Conventional RAG without agentic planning.
2. **Planning-enabled:** RAG with explicit task decomposition.
3. **Tool-enabled:** Planning plus computational tools.
4. **Verification-enabled:** Tool use plus claim and calculation verification.
5. **Memory-enabled:** Verification plus persistent task memory.
6. **Full agent:** All components, including adaptive replanning and HITL.

Compare each configuration on the same tasks and data.

This will help demonstrate whether the additional agentic components provide measurable improvements rather than merely increasing complexity.

---

# 22. Research Contribution and Novelty Opportunities

The use of LLMs, RAG, tools, memory, and workflow orchestration is not by itself a novel research contribution. The project needs a clearly defined improvement that can be measured against a baseline.

Several directions are suitable for further investigation.

## 22.1 Evidence-gap-driven planning

Develop a planner that represents an investigation as a set of required claims and evidence dependencies.

The agent should prioritize actions according to which missing evidence is most important for completing the task.

**Research question:** Does evidence-gap-driven planning improve claim support and task completion compared with ordinary LLM-generated plans?

## 22.2 Uncertainty-aware adaptive retrieval

Estimate when the retrieved evidence is insufficient or contradictory, and selectively retrieve additional documents.

**Research question:** Can an uncertainty-aware retrieval strategy reduce unsupported conclusions without causing excessive tool calls or processing cost?

## 22.3 Cross-document numerical reconciliation

Build a specialized reconciliation process that aligns metric names, reporting periods, units, and definitions across documents.

**Research question:** How effectively can structured reconciliation detect inconsistencies compared with conventional RAG?

## 22.4 Cost-aware verification

Prioritize verification operations based on the importance of a claim, the potential impact of an error, and the cost of checking it.

**Research question:** Can risk-based verification maintain high analytical reliability with fewer model calls and lower computational cost?

## 22.5 Memory with provenance and freshness

Store findings with source references, verification status, and version information.

**Research question:** Does provenance-aware memory reduce repeated work and stale-fact errors during recurring document investigations?

## 22.6 Recommended research direction

A particularly coherent direction is:

**Evidence-Gap-Driven Adaptive Planning for Autonomous Multi-Document Analysis.**

The proposed contribution would be an agent that:

1. Decomposes the user goal into required analytical claims.
2. Tracks the evidence available for each claim.
3. Identifies the most consequential evidence gaps.
4. Selects the next retrieval or analysis operation.
5. Verifies newly obtained evidence.
6. Stops when the completion criteria are satisfied or the evidence budget is exhausted.

The contribution should be evaluated against fixed-plan and conventional RAG baselines.

This is a proposed research hypothesis, not a claim of novelty over all existing research. A literature review and prior-art comparison would be necessary before claiming originality or publication readiness.

---

# 23. Limitations

The system will have several limitations.

## 23.1 Document extraction errors

PDF layouts, merged cells, scanned tables, and malformed spreadsheets can cause extraction errors.

**Mitigation:** Preserve source locations, validate extracted values, and flag uncertain extractions.

## 23.2 LLM reasoning errors

The Brain may misinterpret a question or propose an inappropriate analysis.

**Mitigation:** Use structured plans, typed tool inputs, deterministic calculations, explicit completion criteria, and verification.

## 23.3 Retrieval omissions

Relevant information may not appear among the retrieved passages.

**Mitigation:** Combine lexical and semantic retrieval, apply metadata filters, and evaluate recall against annotated evidence.

## 23.4 Conflicting definitions

Two documents may define revenue, cost, or reporting periods differently.

**Mitigation:** Preserve units and definitions and request clarification when differences cannot be resolved.

## 23.5 Computational cost

Repeated LLM calls, embeddings, OCR, and multi-step analysis may increase processing time and cost.

**Mitigation:** Cache results, restrict unnecessary iterations, and use deterministic tools for repetitive operations.

## 23.6 Memory contamination

Incorrect or outdated findings may be reused in future tasks.

**Mitigation:** Store provenance, verification status, document versions, and expiration or invalidation rules.

## 23.7 Incomplete causal evidence

The documents may establish that a metric changed without explaining why it changed.

**Mitigation:** Distinguish correlation, observed change, supported interpretation, and unverified hypothesis.

## 23.8 Evaluation limitations

A system may perform well on a small set of familiar documents but fail on different formats or domains.

**Mitigation:** Use varied test cases, hold out evaluation documents, include adversarial or malformed inputs, and report failures as well as successes.

---

# 24. Implementation Roadmap

A staged implementation will reduce complexity and make failures easier to diagnose.

## Phase 1: Requirements and test data

- Define supported formats.
- Create a sample document collection.
- Specify expected answers and reference calculations.
- Establish source citation requirements.
- Define security and approval policies.

**Deliverable:** Requirements specification and evaluation dataset.

## Phase 2: Document ingestion

- Implement PDF, DOCX, Excel, and CSV parsing.
- Preserve page, sheet, and cell metadata.
- Validate extracted content.
- Create a document manifest.

**Deliverable:** Tested document ingestion pipeline.

## Phase 3: Retrieval and RAG

- Implement chunking and metadata assignment.
- Create embeddings and vector indexes.
- Add lexical and semantic search.
- Retrieve source-grounded passages.
- Evaluate retrieval quality.

**Deliverable:** Working multi-document retrieval subsystem.

## Phase 4: Analytical tools

- Implement numerical comparisons.
- Add data cleaning and summary statistics.
- Add segment contribution analysis.
- Generate charts.
- Implement deterministic calculation tests.

**Deliverable:** Reusable analytical tool library.

## Phase 5: Agent and orchestrator

- Implement goal interpretation.
- Add structured planning.
- Connect the Brain to registered tools.
- Implement workflow state and conditional transitions.
- Add bounded retries and failure handling.

**Deliverable:** Working single-agent investigation loop.

## Phase 6: Verification and adaptive planning

- Verify calculations.
- Validate source references.
- Detect missing evidence.
- Implement source reconciliation.
- Replan when verification fails.

**Deliverable:** Evidence-first adaptive investigation workflow.

## Phase 7: Memory and HITL

- Persist task state and history.
- Add memory retrieval.
- Implement approval and rejection controls.
- Add audit logging and retention policies.

**Deliverable:** Stateful, supervised agent.

## Phase 8: Interface and reporting

- Implement the Streamlit interface.
- Display task progress.
- Show evidence and calculations.
- Generate downloadable reports.
- Provide clear error and uncertainty messages.

**Deliverable:** Complete user-facing application.

## Phase 9: Evaluation and optimization

- Run reference-based tests.
- Compare against conventional RAG.
- Conduct ablation studies.
- Measure cost, latency, accuracy, and recovery.
- Document failure cases and limitations.

**Deliverable:** Evaluation report, reproducible experiments, and final demonstration.

---

# 25. Expected Deliverables

The final project should contain:

1. A modular Python implementation.
2. A multi-format document ingestion pipeline.
3. A practical RAG retrieval subsystem.
4. An agent Brain with structured tool calling.
5. A stateful Orchestrator.
6. A set of deterministic analytical tools.
7. Persistent task and evidence memory.
8. A claim and calculation verification subsystem.
9. Human approval and review controls.
10. A user-facing interface.
11. An automated testing suite.
12. A sample evaluation dataset.
13. An evaluation report with measured results.
14. A technical architecture diagram.
15. Installation and usage documentation.
16. Example analytical reports.
17. A demonstration of adaptive investigation and failure recovery.

---

# 26. Advanced v3.0 Enterprise Architecture & Extensions

The system has been advanced to **v3.0 Enterprise Edition**, delivering six enterprise-grade pillars:

### 26.1 Autonomous Causal Knowledge Graph (KG-RAG)
Located in `src/retrieval/knowledge_graph.py`, this module builds an attributed directed knowledge graph (`DocumentKnowledgeGraph`) using `networkx`:
- **Entity Decomposition:** Mines business segments, metrics, periods, claims, and operational drivers with citation provenance.
- **Attributed Relationships:** Encodes typed edges (`CONTRIBUTES_TO`, `EXPERIENCED_EVENT`, `REPORTED_IN`, `CAUSED_BY`, `DISCREPANCY_WITH`).
- **Multi-Hop Pathfinding:** Discovers causal chains connecting macro risks (e.g., supplier factory delays) to segment sales volume and consolidated revenue decline.
- **Graph Centrality & Visualization:** Computes degree centrality to isolate systemic bottleneck entities and exports Cytoscape JSON for front-end rendering.

### 26.2 Deterministic Scenario Modeling & Sensitivity Engine
Located in `src/tools/scenario_modeling.py`, this module provides executive what-if simulations with zero LLM math hallucination:
- **Counterfactual Simulation:** Calculates what period 2 consolidated revenue would be under arbitrary segment overrides (e.g. "What if Segment A held flat?"), computing exact loss preserved.
- **Sensitivity Matrix:** Shocks individual segments from -20% to +20% to map overall revenue elasticity curves.
- **Recovery Target Trajectory Solver:** Programmatically solves for segment revenue quotas and required growth rates to achieve target full-year budgets.
- **Stochastic Monte Carlo Volatility Bounds:** Executes 1,000 stochastic Gaussian iterations across segment bases, returning conservative (p5), median (p50), and optimistic (p95) confidence bounds and recovery probabilities.

### 26.3 Multi-Agent Red-Team Debate Council
Located in `src/agent/debate.py`, this module orchestrates structured 4-round adversarial chamber debates:
- **Lead Quantitative Analyst (Quant-Alpha):** Presents mathematical attribution proofs and invariants.
- **Retrieval Specialist (Lexi-Search):** Corroborates numbers with quoted textual evidence and page citations.
- **Red-Team Auditor (Adversary-Prime):** Adversarially challenges omissions, identifies undocumented segment declines, and tests cross-document discrepancies.
- **Executive Supervisor (Supervisor-Chief):** Arbitrates arguments, evaluates consensus, grades confidence, logs agreed facts and surviving uncertainties, and mandates HITL escalation when necessary.

### 26.4 Enterprise FastAPI REST Microservice
Located in `src/api/server.py` with runner `scripts/run_api.py`:
- Headless, asynchronous REST service with automatic interactive documentation (`/docs` OpenAPI and `/redoc`).
- Endpoints:
  - `GET /health`: Health status, version, and database indicators.
  - `POST /api/v1/investigate`: Triggers end-to-end investigation with state persistence.
  - `POST /api/v1/scenarios/simulate`: Counterfactual, sensitivity, and Monte Carlo engine.
  - `POST /api/v1/debate`: Multi-agent debate council runner.
  - `GET /api/v1/hitl/queue` & `POST /api/v1/hitl/decision`: Governance queue management.
  - `GET /api/v1/benchmarks/run`: Programmatic ADI-Bench runner.
  - `GET /api/v1/reports/{report_name}`: Binary PDF and Markdown download endpoints.

### 26.5 Layout-Aware Spatial & OCR Ingestion
Located in `src/ingestion/ocr_layout_parser.py`:
- PyMuPDF spatial bounding-box block decomposition classifying headers, tables, body text, and footers.
- Scanned PDF classification based on character density per unit area and embedded bitmap image ratios.
- Extraction of embedded charts and figures to disk for multi-modal analysis.

### 26.6 Production Docker Deployment
- `Dockerfile`: Multi-stage Python 3.12 slim image with system libraries for PDF font rendering.
- `docker-compose.yml`: Multi-container stack orchestrating the Streamlit Dashboard (port 8501) and FastAPI microservice (port 8000) with shared volumes.


---

# 27. Conclusion

The Autonomous Document Intelligence and Data Analysis Agent is designed to move beyond conventional document question-answering by combining contextual retrieval, autonomous planning, computational analysis, adaptive execution, persistent memory, and evidence verification.

The system accepts a user-defined goal, investigates relevant documents, selects appropriate analytical tools, computes results, checks source consistency, and produces an evidence-backed report.

Its defining characteristic is the integration of all six agentic properties—autonomy, goal orientation, planning, reasoning, adaptability, and content awareness—with the five architectural components of Brain, Orchestrator, Tools, Memory, and Human-in-the-Loop supervision.

The proposed implementation uses a modular Python architecture, LangGraph for stateful orchestration, RAG for document retrieval, deterministic tools for numerical operations, persistent storage for task history, and explicit verification for analytical reliability.

The most important design principle is that the agent should not merely produce plausible answers. It should demonstrate how its conclusions are supported by source documents and calculations, identify what remains uncertain, and revise its investigation when the available evidence is insufficient.

The project will be considered successful when its behavior can be demonstrated through reproducible experiments, measurable improvements over a conventional RAG baseline, reliable source attribution, and controlled recovery from realistic document-analysis failures.

The result will be a practical Agentic AI system with a clear implementation pathway and a credible foundation for further research into adaptive, evidence-driven autonomous analysis.
