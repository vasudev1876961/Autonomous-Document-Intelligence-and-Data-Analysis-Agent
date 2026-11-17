"""
Visual Grounding and Spatial Coordinate Highlighting Engine.
Links extracted numbers, facts, and table cells to exact pixel coordinates [x0, y0, x1, y1]
on original PDF pages, rendering highlighted visual evidence snippets.
"""
from pathlib import Path
from typing import Any, Optional
import pymupdf
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return max(0.0, self.x1 - self.x0)

    @property
    def height(self) -> float:
        return max(0.0, self.y1 - self.y0)

    @property
    def area(self) -> float:
        return self.width * self.height

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (round(self.x0, 2), round(self.y0, 2), round(self.x1, 2), round(self.y1, 2))

    def intersects(self, other: "BoundingBox") -> bool:
        return not (
            self.x1 < other.x0 or self.x0 > other.x1 or
            self.y1 < other.y0 or self.y0 > other.y1
        )

    def iou(self, other: "BoundingBox") -> float:
        """Computes Intersection-over-Union (IoU) overlap metric."""
        if not self.intersects(other):
            return 0.0
        inter_x0 = max(self.x0, other.x0)
        inter_y0 = max(self.y0, other.y0)
        inter_x1 = min(self.x1, other.x1)
        inter_y1 = min(self.y1, other.y1)
        inter_area = max(0.0, inter_x1 - inter_x0) * max(0.0, inter_y1 - inter_y0)
        union_area = self.area + other.area - inter_area
        return inter_area / union_area if union_area > 0 else 0.0


class VisualGroundingResult(BaseModel):
    pdf_path: str
    page_number: int
    page_width: float
    page_height: float
    bboxes: list[tuple[float, float, float, float]] = Field(default_factory=list)
    highlighted_image_path: str
    matched_text: str = ""
    status: str = "success"


class VisualGroundingEngine:
    """
    Renders high-resolution PDF pages with exact spatial bounding-box annotations
    for evidence grounding and visual verification.
    """

    @classmethod
    def render_page_as_image(
        cls,
        pdf_path: Path | str,
        page_number: int,
        output_path: Path | str,
        dpi: int = 150
    ) -> str:
        """Renders an unannotated PDF page to a PNG image file."""
        pdf_path = Path(pdf_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = pymupdf.open(str(pdf_path))
        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise IndexError(f"Page {page_number} out of range (1..{len(doc)}) in {pdf_path.name}")

        page = doc[page_number - 1]
        pix = page.get_pixmap(dpi=dpi)
        pix.save(str(output_path))
        doc.close()
        return str(output_path)

    @classmethod
    def highlight_bboxes_on_page(
        cls,
        pdf_path: Path | str,
        page_number: int,
        bboxes: list[tuple[float, float, float, float]],
        output_path: Path | str,
        fill_color: tuple[float, float, float] = (1.0, 0.9, 0.2),  # Soft gold highlight
        stroke_color: tuple[float, float, float] = (0.85, 0.2, 0.1), # Deep red border
        stroke_width: float = 1.5,
        dpi: int = 150
    ) -> VisualGroundingResult:
        """
        Draws visual bounding boxes with translucent fill and contrasting border
        onto a copy of the PDF page, rendering the result as a PNG evidence snippet.
        """
        pdf_path = Path(pdf_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = pymupdf.open(str(pdf_path))
        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise IndexError(f"Page {page_number} out of range (1..{len(doc)}) in {pdf_path.name}")

        page = doc[page_number - 1]
        rect = page.rect
        matched_snippets: list[str] = []

        # Annotate each bounding box
        for box in bboxes:
            x0, y0, x1, y1 = box
            r = pymupdf.Rect(x0, y0, x1, y1)
            # Add highlight annotation (translucent overlay)
            annot = page.add_rect_annot(r)
            annot.set_colors(stroke=stroke_color, fill=fill_color)
            annot.set_border(width=stroke_width)
            annot.set_opacity(0.4)
            annot.update()

            # Grab underlying text
            txt = page.get_text("text", clip=r).strip()
            if txt:
                matched_snippets.append(txt)

        # Render pixmap with annotations
        pix = page.get_pixmap(dpi=dpi)
        pix.save(str(output_path))
        doc.close()

        return VisualGroundingResult(
            pdf_path=str(pdf_path),
            page_number=page_number,
            page_width=rect.width,
            page_height=rect.height,
            bboxes=bboxes,
            highlighted_image_path=str(output_path),
            matched_text=" | ".join(matched_snippets),
            status="success"
        )

    @classmethod
    def find_text_coordinates(
        cls,
        pdf_path: Path | str,
        page_number: int,
        query_text: str
    ) -> list[tuple[float, float, float, float]]:
        """
        Searches for exact text string or substring occurrences on a PDF page
        and returns their bounding box coordinates (x0, y0, x1, y1).
        """
        pdf_path = Path(pdf_path)
        doc = pymupdf.open(str(pdf_path))
        if page_number < 1 or page_number > len(doc):
            doc.close()
            return []

        page = doc[page_number - 1]
        quads_or_rects = page.search_for(query_text)
        coords = [
            (round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2))
            for r in quads_or_rects
        ]
        doc.close()
        return coords

    @classmethod
    def get_page_blocks_with_bboxes(
        cls,
        pdf_path: Path | str,
        page_number: int
    ) -> list[dict[str, Any]]:
        """
        Extracts all textual and tabular blocks on a page with their geometric bounding boxes.
        """
        pdf_path = Path(pdf_path)
        doc = pymupdf.open(str(pdf_path))
        if page_number < 1 or page_number > len(doc):
            doc.close()
            return []

        page = doc[page_number - 1]
        blocks = page.get_text("blocks") or []
        res = []
        for b in blocks:
            x0, y0, x1, y1, text, b_no, b_type = b[0], b[1], b[2], b[3], b[4], b[5], b[6]
            res.append({
                "block_no": b_no,
                "block_type": "text" if b_type == 0 else "image_or_drawing",
                "bbox": (round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)),
                "text": text.strip()
            })
        doc.close()
        return res
