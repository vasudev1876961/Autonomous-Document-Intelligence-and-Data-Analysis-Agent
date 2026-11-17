"""
Unit and Integration Tests for Pillar 2: Multimodal Visual Grounding & Chart De-rendering.
Tests spatial bounding boxes, page highlight rendering, vector chart de-rendering,
and complex hierarchical/spanning table structure recognition.
"""
from pathlib import Path
import pytest
from config.settings import settings
from src.ingestion.visual_grounding import BoundingBox, VisualGroundingEngine
from src.ingestion.chart_derenderer import ChartDeRenderer, ChartDataPoint, ChartDeRenderResult
from src.ingestion.table_structure import ComplexTableRecognizer, RecognizedTable


def test_bounding_box_geometry():
    """Tests BoundingBox arithmetic, intersection detection, and IoU metric."""
    b1 = BoundingBox(x0=10.0, y0=10.0, x1=50.0, y1=50.0)
    assert b1.width == 40.0
    assert b1.height == 40.0
    assert b1.area == 1600.0
    assert b1.to_tuple() == (10.0, 10.0, 50.0, 50.0)

    # Disjoint box
    b2 = BoundingBox(x0=60.0, y0=60.0, x1=100.0, y1=100.0)
    assert b1.intersects(b2) is False
    assert b1.iou(b2) == 0.0

    # Overlapping box
    b3 = BoundingBox(x0=30.0, y0=30.0, x1=70.0, y1=70.0)
    assert b1.intersects(b3) is True
    # Intersection area: (50-30)*(50-30) = 20*20 = 400
    # Union area: 1600 + 1600 - 400 = 2800. IoU = 400 / 2800 = 1/7 ~= 0.1428
    assert pytest.approx(b1.iou(b3), 0.01) == 0.1428


def test_visual_grounding_render_and_highlight(tmp_path):
    """Tests rendering an image of a PDF page with bounding box highlights."""
    pdf_path = settings.sample_docs_dir / "Quarterly_Report.pdf"
    assert pdf_path.exists()

    # Find text coordinates
    coords = VisualGroundingEngine.find_text_coordinates(pdf_path, page_number=1, query_text="revenue")
    assert len(coords) >= 1

    out_png = tmp_path / "highlighted_page_1.png"
    result = VisualGroundingEngine.highlight_bboxes_on_page(
        pdf_path=pdf_path,
        page_number=1,
        bboxes=coords[:2],
        output_path=out_png
    )

    assert result.status == "success"
    assert Path(result.highlighted_image_path).exists()
    assert result.page_width > 0
    assert result.page_height > 0
    assert len(result.bboxes) == len(coords[:2])


def test_complex_table_recognizer_spanning_and_hierarchy():
    """Tests ComplexTableRecognizer resolving hierarchical multi-level headers and forward-filling empty spanning cells."""
    raw_table = [
        ["Financial Metric", "", "FY2025 Performance", ""],
        ["Segment", "Region", "Q1 Actual", "Q2 Actual"],
        ["Segment A", "North", "500.0", "420.0"],
        ["", "South", "300.0", "280.0"],  # Empty segment cell (merged vertically)
        ["Segment B", "Global", "200.0", "200.0"],
    ]

    rec = ComplexTableRecognizer.process_raw_table(raw_rows=raw_table, table_id="test_tab_01", page_number=1)

    assert rec.has_hierarchical_headers is True
    assert len(rec.headers) == 4
    assert "FY2025 Performance - Q1 Actual" in rec.headers
    assert "FY2025 Performance - Q2 Actual" in rec.headers

    # Verify forward-fill on column 0 for empty cell
    assert rec.cell_matrix[2][0] == "Segment A (Cont.)"
    assert rec.num_rows == 4  # Header + 3 data rows


def test_complex_table_stitching():
    """Tests stitching continuous tables across page breaks with matching headers."""
    t1 = RecognizedTable(
        table_id="tab_p1",
        page_number=1,
        num_rows=3,
        num_cols=2,
        headers=["Segment", "Revenue"],
        cell_matrix=[
            ["Segment", "Revenue"],
            ["Alpha", "100"],
            ["Beta", "200"]
        ]
    )
    t2 = RecognizedTable(
        table_id="tab_p2",
        page_number=2,  # Consecutive page
        num_rows=3,
        num_cols=2,
        headers=["Segment", "Revenue"],  # Matching headers
        cell_matrix=[
            ["Segment", "Revenue"],
            ["Gamma", "300"],
            ["Delta", "400"]
        ]
    )

    stitched = ComplexTableRecognizer.stitch_multi_page_tables([t1, t2])
    assert len(stitched) == 1
    assert stitched[0].table_id == "tab_p1_stitched"
    assert stitched[0].is_multi_page_continuation is True
    assert stitched[0].num_rows == 5  # Header + 4 data rows


def test_chart_derenderer_conversion():
    """Tests ChartDeRenderer converting structured chart data points into an ExtractedChunk."""
    chart = ChartDeRenderResult(
        chart_id="chart_001",
        chart_type="waterfall_chart",
        title="Revenue Bridge Q1 to Q2",
        page_number=1,
        bbox=(50.0, 100.0, 450.0, 350.0),
        data_points=[
            ChartDataPoint(category="Segment A Loss", value=-80.0, unit="lakh"),
            ChartDataPoint(category="Segment B Loss", value=-20.0, unit="lakh"),
            ChartDataPoint(category="Net Q2 Total", value=900.0, unit="lakh"),
        ],
        confidence=0.95,
        raw_markdown_table="| Category | Value | Unit |\n|---|---|---|\n| Segment A Loss | -80.0 | lakh |"
    )

    chunk = ChartDeRenderer.to_extracted_chunk(chart, document_id="doc_123", file_name="Report.pdf")
    assert chunk.content_type == "chart_data"
    assert "De-rendered Visual Chart [Revenue Bridge Q1 to Q2]" in chunk.content
    assert chunk.location.page_number == 1
    assert chunk.location.bbox == (50.0, 100.0, 450.0, 350.0)


def test_api_multimodal_endpoints():
    """Tests REST API endpoints for multimodal visual grounding and table recognition."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)

    # 1. Highlight grounding
    res1 = client.post("/api/v1/multimodal/highlight", json={
        "page_number": 1,
        "query_text": "revenue"
    })
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["status"] == "success"
    assert len(d1["bboxes"]) >= 1

    # 2. Table structure recognition
    res2 = client.post("/api/v1/multimodal/table-structure", json={
        "raw_rows": [
            ["Metric", "Value"],
            ["Net Income", "120.0"],
            ["Total Revenue", "900.0"]
        ],
        "page_number": 1
    })
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["headers"] == ["Metric", "Value"]
    assert d2["num_rows"] == 3

    # 3. Chart de-rendering
    res3 = client.post("/api/v1/multimodal/chart-derender", json={
        "page_number": 1
    })
    assert res3.status_code == 200
    d3 = res3.json()
    assert "charts_found" in d3
