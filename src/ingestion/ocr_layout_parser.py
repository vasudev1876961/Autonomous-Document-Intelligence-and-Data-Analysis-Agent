"""
Layout-Aware Document and OCR Parser.
Performs spatial structure decomposition, scanned page classification,
bounding box extraction, and embedded image/figure discovery for multi-modal intelligence.
"""
from pathlib import Path
from typing import Any, Optional
import pymupdf  # PyMuPDF
from pydantic import BaseModel, Field
from src.ingestion.metadata import SourceLocation


class LayoutBlock(BaseModel):
    block_id: int
    block_type: str  # "text", "table", "image", "header", "footer"
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1)
    text_content: str
    confidence: float = 1.0

class PageLayoutReport(BaseModel):
    page_number: int
    width: float
    height: float
    is_scanned: bool
    text_density: float  # characters per 1000 pt²
    blocks: list[LayoutBlock] = Field(default_factory=list)
    embedded_images_count: int = 0

class LayoutParser:
    """
    Advanced spatial layout extractor and OCR pipeline using PyMuPDF.
    """
    def __init__(self, scanned_threshold_density: float = 0.05):
        self.scanned_threshold_density = scanned_threshold_density

    def analyze_pdf_layout(self, pdf_path: Path | str) -> list[PageLayoutReport]:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        doc = pymupdf.open(str(pdf_path))
        reports: list[PageLayoutReport] = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            rect = page.rect
            area = rect.width * rect.height
            text_raw = page.get_text("text") or ""
            char_count = len(text_raw.strip())
            
            density = (char_count / (area / 1000.0)) if area > 0 else 0.0
            is_scanned = (density < self.scanned_threshold_density and len(page.get_images()) > 0)

            # Block decomposition
            blocks_raw = page.get_text("blocks") or []
            blocks: list[LayoutBlock] = []

            for b_idx, b in enumerate(blocks_raw):
                # block tuple: (x0, y0, x1, y1, text, block_no, block_type)
                x0, y0, x1, y1, b_text, b_no, b_type = b[0], b[1], b[2], b[3], b[4], b[5], b[6]
                
                # Classify block type based on geometry and content
                b_type_str = "text"
                if b_type == 1:
                    b_type_str = "image"
                elif y0 < 50:
                    b_type_str = "header"
                elif y1 > (rect.height - 50):
                    b_type_str = "footer"
                elif "\t" in b_text or "   " in b_text:
                    b_type_str = "table"

                blocks.append(LayoutBlock(
                    block_id=b_no if isinstance(b_no, int) else b_idx,
                    block_type=b_type_str,
                    bbox=(round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)),
                    text_content=b_text.strip(),
                    confidence=0.99 if not is_scanned else 0.85
                ))

            # Image count
            img_list = page.get_images()

            reports.append(PageLayoutReport(
                page_number=page_idx + 1,
                width=rect.width,
                height=rect.height,
                is_scanned=is_scanned,
                text_density=round(density, 4),
                blocks=blocks,
                embedded_images_count=len(img_list)
            ))

        doc.close()
        return reports

    def extract_embedded_images(self, pdf_path: Path | str, output_dir: Path | str) -> list[str]:
        """
        Discovers and writes embedded figures/charts from PDF to disk for visual analysis.
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = pymupdf.open(str(pdf_path))
        extracted_paths: list[str] = []

        for p_idx in range(len(doc)):
            page = doc[p_idx]
            for img_idx, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"img_p{p_idx + 1}_{img_idx + 1}.{image_ext}"
                target_fp = output_dir / image_filename
                with open(target_fp, "wb") as f:
                    f.write(image_bytes)
                extracted_paths.append(str(target_fp))

        doc.close()
        return extracted_paths
