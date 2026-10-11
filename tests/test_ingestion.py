"""
Unit tests for document ingestion and metadata tracking.
"""
from pathlib import Path
import pytest
from src.ingestion.metadata import FileType, compute_file_sha256, detect_file_type
from src.ingestion.manifest import IngestionManager

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_documents"

def test_file_type_detection():
    assert detect_file_type(Path("sample.pdf")) == FileType.PDF
    assert detect_file_type(Path("sample.docx")) == FileType.DOCX
    assert detect_file_type(Path("sample.xlsx")) == FileType.XLSX
    assert detect_file_type(Path("sample.csv")) == FileType.CSV

def test_checksum_computation():
    pdf_path = SAMPLE_DIR / "Quarterly_Report.pdf"
    assert pdf_path.exists()
    sha = compute_file_sha256(pdf_path)
    assert len(sha) == 64

def test_pdf_ingestion():
    mgr = IngestionManager()
    pdf_path = SAMPLE_DIR / "Quarterly_Report.pdf"
    meta, chunks = mgr.process_file(pdf_path)
    assert meta.extraction_status == "success"
    assert meta.page_count is not None and meta.page_count >= 1
    assert len(chunks) > 0
    assert any("Quarterly" in c.content for c in chunks)

def test_excel_ingestion():
    mgr = IngestionManager()
    xlsx_path = SAMPLE_DIR / "Revenue_Data.xlsx"
    meta, chunks = mgr.process_file(xlsx_path)
    assert meta.extraction_status == "success"
    assert "Revenue" in meta.sheet_names
    assert len(chunks) > 0

def test_csv_ingestion():
    mgr = IngestionManager()
    csv_path = SAMPLE_DIR / "Segment_Performance.csv"
    meta, chunks = mgr.process_file(csv_path)
    assert meta.extraction_status == "success"
    assert len(chunks) > 0
