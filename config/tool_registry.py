"""
Declarative Tool Registry: Exposes metadata, schemas, and categories for all agent tools.
"""
from typing import Callable, Any
from pydantic import BaseModel

class ToolDescriptor(BaseModel):
    name: str
    category: str
    description: str
    risk_level: str # "low", "moderate", "high"
    requires_approval: bool = False

TOOL_REGISTRY: dict[str, ToolDescriptor] = {
    "pdf_parser": ToolDescriptor(
        name="pdf_parser",
        category="ingestion",
        description="Extracts textual passages and tables from PDF files with page numbers.",
        risk_level="low"
    ),
    "excel_parser": ToolDescriptor(
        name="excel_parser",
        category="ingestion",
        description="Extracts sheets and structured cell values from Excel (.xlsx) workbooks.",
        risk_level="low"
    ),
    "csv_parser": ToolDescriptor(
        name="csv_parser",
        category="ingestion",
        description="Parses delimiter-separated values into tabular representations.",
        risk_level="low"
    ),
    "hybrid_retriever": ToolDescriptor(
        name="hybrid_retriever",
        category="retrieval",
        description="Executes hybrid lexical (BM25) and dense vector retrieval with RRF.",
        risk_level="low"
    ),
    "period_comparison": ToolDescriptor(
        name="period_comparison",
        category="numerical_analysis",
        description="Computes absolute and percentage period-over-period changes deterministically.",
        risk_level="low"
    ),
    "segment_contribution": ToolDescriptor(
        name="segment_contribution",
        category="numerical_analysis",
        description="Calculates segment contribution percentages and checks total reconciliation.",
        risk_level="low"
    ),
    "source_reconciliation": ToolDescriptor(
        name="source_reconciliation",
        category="reconciliation",
        description="Identifies discrepancies between overlapping claims across multiple documents.",
        risk_level="moderate"
    ),
    "calculation_verifier": ToolDescriptor(
        name="calculation_verifier",
        category="verification",
        description="Independently re-computes arithmetic formulas to audit correctness.",
        risk_level="low"
    ),
    "citation_verifier": ToolDescriptor(
        name="citation_verifier",
        category="verification",
        description="Verifies that cited sources and locations exist and ground claims.",
        risk_level="low"
    ),
    "chart_generator": ToolDescriptor(
        name="chart_generator",
        category="visualization",
        description="Renders Matplotlib charts for period comparison and segment breakdown.",
        risk_level="low"
    ),
    "report_exporter": ToolDescriptor(
        name="report_exporter",
        category="reporting",
        description="Generates downloadable analytical reports in Markdown and PDF formats.",
        risk_level="low"
    ),
}
