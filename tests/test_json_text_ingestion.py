"""
Unit tests for JSON and Text/Markdown Ingestion Parsers.
"""
import json
import pytest
from pathlib import Path
from src.ingestion.json_parser import JSONParser
from src.ingestion.text_parser import TextParser
from src.ingestion.manifest import IngestionManager
from src.ingestion.metadata import FileType

def test_json_parser_array(tmp_path: Path):
    sample_records = [
        {"segment": "Segment A", "q1_revenue": 500.0, "q2_revenue": 420.0},
        {"segment": "Segment B", "q1_revenue": 300.0, "q2_revenue": 280.0},
        {"segment": "Segment C", "q1_revenue": 200.0, "q2_revenue": 200.0},
    ]
    json_file = tmp_path / "financials.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_records, f)

    parser = JSONParser()
    meta, chunks = parser.parse(json_file)

    assert meta.file_type == FileType.JSON
    assert meta.extraction_status == "success"
    assert len(chunks) >= 4  # 1 full table chunk + 3 item chunks
    assert any(c.content_type == "table" for c in chunks)
    assert any("Segment A" in c.content for c in chunks)

def test_json_parser_nested_dict(tmp_path: Path):
    nested_data = {
        "report_title": "Quarterly Financial Overview",
        "currency": "USD",
        "segments": [
            {"name": "Hardware", "margin": 0.22},
            {"name": "Services", "margin": 0.45}
        ]
    }
    json_file = tmp_path / "nested.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(nested_data, f)

    parser = JSONParser()
    meta, chunks = parser.parse(json_file)

    assert meta.file_type == FileType.JSON
    assert meta.extraction_status == "success"
    assert any("Quarterly Financial Overview" in c.content for c in chunks)
    assert any(c.location.section_heading == "$.segments" for c in chunks)

def test_text_and_markdown_parser(tmp_path: Path):
    md_content = """# Executive Management Discussion
Revenue in the second quarter experienced downward variance.

## Segment Breakdown
| Segment | Q1 Revenue | Q2 Revenue |
| --- | --- | --- |
| Segment A | 500 | 420 |
| Segment B | 300 | 280 |

## Operational Factors
Supply chain bottlenecks hindered hardware delivery timelines.
"""
    md_file = tmp_path / "management_discussion.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    parser = TextParser()
    meta, chunks = parser.parse(md_file)

    assert meta.file_type == FileType.MD
    assert meta.extraction_status == "success"
    assert len(chunks) >= 2
    assert any(c.content_type == "table" for c in chunks)
    assert any("Supply chain bottlenecks" in c.content for c in chunks)

def test_ingestion_manager_unified(tmp_path: Path):
    # Test that IngestionManager routes JSON and TXT correctly
    f_json = tmp_path / "data.json"
    f_json.write_text('{"metric": "Operating Margin", "value": 0.18}', encoding="utf-8")

    f_txt = tmp_path / "notes.txt"
    f_txt.write_text("Audit notes: all figures verified against general ledger.", encoding="utf-8")

    mgr = IngestionManager()
    m_json, c_json = mgr.process_file(f_json)
    m_txt, c_txt = mgr.process_file(f_txt)

    assert m_json.file_type == FileType.JSON
    assert m_txt.file_type == FileType.TXT
    assert len(c_json) > 0
    assert len(c_txt) > 0

