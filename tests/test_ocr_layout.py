"""
Unit tests for Layout-Aware Document Parsing and Spatial Analysis.
"""
from pathlib import Path
from src.ingestion.ocr_layout_parser import LayoutParser
from config.settings import settings

def test_pdf_layout_analysis():
    sample_pdf = settings.sample_docs_dir / "Quarterly_Report.pdf"
    if not sample_pdf.exists():
        return
    
    parser = LayoutParser()
    pages = parser.analyze_pdf_layout(sample_pdf)
    
    assert len(pages) >= 1
    p1 = pages[0]
    assert p1.width > 0
    assert p1.height > 0
    assert len(p1.blocks) > 0
    assert p1.is_scanned is False
    assert any(b.block_type in ["text", "header", "table", "footer"] for b in p1.blocks)
