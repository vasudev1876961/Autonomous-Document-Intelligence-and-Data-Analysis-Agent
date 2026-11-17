"""
Chart-to-Data De-Rendering Engine for Multimodal Document Intelligence.
Discovers vector charts and diagrams buried in PDF annual reports, investor presentations,
and financial statements, reverse-engineering them into structured tabular JSON/Pandas data.
"""
from pathlib import Path
from typing import Any, Optional
import re
import pymupdf
import pandas as pd
from pydantic import BaseModel, Field

from src.ingestion.metadata import ExtractedChunk, SourceLocation, FileType


class ChartDataPoint(BaseModel):
    category: str
    value: float
    unit: str = ""
    relative_percentage: Optional[float] = None
    bbox: Optional[tuple[float, float, float, float]] = None


class ChartDeRenderResult(BaseModel):
    chart_id: str
    chart_type: str  # "bar_chart", "waterfall_chart", "line_graph", "unstructured_chart"
    title: str = "Extracted Financial Graphic"
    page_number: int
    bbox: tuple[float, float, float, float]
    data_points: list[ChartDataPoint] = Field(default_factory=list)
    confidence: float = 0.90
    raw_markdown_table: str = ""


class ChartDeRenderer:
    """
    Reverse-engineers visual vector charts and graphic plots into structured financial series.
    """

    @classmethod
    def de_render_page_charts(
        cls,
        pdf_path: Path | str,
        page_number: int,
        document_id: str = "doc_chart"
    ) -> list[ChartDeRenderResult]:
        """
        Analyzes vector drawings and text labels on a page to discover charts
        and extract their underlying numerical data.
        """
        pdf_path = Path(pdf_path)
        doc = pymupdf.open(str(pdf_path))
        if page_number < 1 or page_number > len(doc):
            doc.close()
            return []

        page = doc[page_number - 1]
        drawings = page.get_drawings()
        blocks = page.get_text("blocks") or []

        # Find vector drawing clusters that represent charts (multiple rects or paths)
        rect_drawings = []
        for d in drawings:
            rect = d.get("rect")
            if rect and rect.width > 5 and rect.height > 5:
                rect_drawings.append(rect)

        results: list[ChartDeRenderResult] = []

        # If vector rectangles exist alongside numerical labels
        if len(rect_drawings) >= 2:
            # Cluster bounding box encompassing the vector drawing area
            min_x = min(r.x0 for r in rect_drawings)
            min_y = min(r.y0 for r in rect_drawings)
            max_x = max(r.x1 for r in rect_drawings)
            max_y = max(r.y1 for r in rect_drawings)
            chart_bbox = (round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2))

            # Find text inside or immediately adjacent to this chart area
            chart_rect = pymupdf.Rect(min_x - 30, min_y - 40, max_x + 30, max_y + 40)
            text_instances = page.get_text("words", clip=chart_rect) or []

            # Find numerical values and category labels
            data_points = cls._reconstruct_series(text_instances, rect_drawings)

            if data_points:
                # Build markdown representation
                md_lines = ["| Category | Value | Unit |", "|---|---|---|"]
                for dp in data_points:
                    md_lines.append(f"| {dp.category} | {dp.value:,.2f} | {dp.unit} |")
                md_table = "\n".join(md_lines)

                chart_type = "waterfall_chart" if any("bridge" in t[4].lower() for t in text_instances) else "bar_chart"
                title = "Quarterly Financial Performance Graphic"
                for b in blocks:
                    if b[1] < min_y and abs(b[1] - min_y) < 60:
                        title = b[4].strip()
                        break

                results.append(
                    ChartDeRenderResult(
                        chart_id=f"chart_p{page_number}_01",
                        chart_type=chart_type,
                        title=title,
                        page_number=page_number,
                        bbox=chart_bbox,
                        data_points=data_points,
                        confidence=0.92,
                        raw_markdown_table=md_table
                    )
                )

        doc.close()
        return results

    @classmethod
    def _reconstruct_series(
        cls,
        words: list[Any],
        rects: list[pymupdf.Rect]
    ) -> list[ChartDataPoint]:
        """Pairs detected numeric values with adjacent category names."""
        nums = []
        labels = []

        num_regex = re.compile(r"^[-+]?\$?₹?([0-9]{1,3}(,[0-9]{3})*(\.[0-9]+)?|[0-9]+(\.[0-9]+)?)$")

        for w in words:
            # word tuple: (x0, y0, x1, y1, word, block_no, line_no, word_no)
            txt = w[4].strip().replace(",", "")
            # Check if numeric
            clean_num = txt.replace("$", "").replace("₹", "")
            try:
                val = float(clean_num)
                nums.append((val, w[0], w[1], w[2], w[3]))
            except ValueError:
                if len(txt) > 1 and not txt.startswith("("):
                    labels.append((txt, w[0], w[1], w[2], w[3]))

        points: list[ChartDataPoint] = []
        if nums and labels:
            # Sort numbers by x-coordinate (left to right)
            nums_sorted = sorted(nums, key=lambda n: n[1])
            # Associate each number with the nearest horizontal label
            for idx, (val, nx0, ny0, nx1, ny1) in enumerate(nums_sorted):
                # Find closest label horizontally
                best_label = f"Series {idx + 1}"
                min_dist = float("inf")
                for lbl, lx0, ly0, lx1, ly1 in labels:
                    dist = abs(nx0 - lx0)
                    if dist < min_dist and dist < 120:
                        min_dist = dist
                        best_label = lbl

                points.append(
                    ChartDataPoint(
                        category=best_label,
                        value=val,
                        unit="lakh",
                        bbox=(round(nx0, 2), round(ny0, 2), round(nx1, 2), round(ny1, 2))
                    )
                )

        return points

    @classmethod
    def to_extracted_chunk(
        cls,
        chart: ChartDeRenderResult,
        document_id: str,
        file_name: str
    ) -> ExtractedChunk:
        """Converts a de-rendered chart into a searchable, grounded ExtractedChunk."""
        content = (
            f"De-rendered Visual Chart [{chart.title}] on Page {chart.page_number} ({chart.chart_type}):\n"
            f"{chart.raw_markdown_table}"
        )
        return ExtractedChunk(
            chunk_id=f"{document_id}_{chart.chart_id}",
            document_id=document_id,
            file_name=file_name,
            content=content,
            content_type="chart_data",
            location=SourceLocation(
                document_id=document_id,
                file_name=file_name,
                file_type=FileType.PDF,
                page_number=chart.page_number,
                bbox=chart.bbox,
                confidence=chart.confidence
            ),
            units="lakh",
            metadata={
                "chart_type": chart.chart_type,
                "title": chart.title,
                "series_count": len(chart.data_points),
                "data_points": [dp.model_dump() for dp in chart.data_points]
            }
        )
