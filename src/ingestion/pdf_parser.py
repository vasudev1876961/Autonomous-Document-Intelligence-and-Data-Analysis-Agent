"""
PDF Parser using PyMuPDF (fitz) for text, complex table structure, chart de-rendering,
and exact spatial bounding-box provenance ([x0, y0, x1, y1]).
"""
from pathlib import Path
import uuid
import pymupdf
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk, FileType, SourceLocation, compute_file_sha256
from src.ingestion.chart_derenderer import ChartDeRenderer
from src.ingestion.table_structure import ComplexTableRecognizer

class PDFParser:
    def parse(self, file_path: Path) -> tuple[DocumentMetadata, list[ExtractedChunk]]:
        path_obj = Path(file_path)
        file_hash = compute_file_sha256(path_obj)
        doc_id = f"doc_{file_hash[:12]}"
        chunks: list[ExtractedChunk] = []

        try:
            doc = pymupdf.open(str(path_obj))
            page_count = len(doc)
            
            for page_idx in range(page_count):
                page = doc[page_idx]
                page_num = page_idx + 1
                page_rect = page.rect
                page_w = page_rect.width
                page_h = page_rect.height
                
                # 1. Extract text blocks with exact bounding boxes
                blocks = page.get_text("blocks") or []
                page_text_accum = []
                for b_idx, b in enumerate(blocks):
                    x0, y0, x1, y1, b_text, b_no, b_type = b[0], b[1], b[2], b[3], b[4], b[5], b[6]
                    clean_b_text = b_text.strip()
                    if clean_b_text and b_type == 0:
                        page_text_accum.append(clean_b_text)

                # Append primary page text chunk with overall bounding box
                full_page_text = "\n".join(page_text_accum) if page_text_accum else page.get_text("text").strip()
                if full_page_text:
                    chunks.append(
                        ExtractedChunk(
                            chunk_id=f"{doc_id}_p{page_num}_txt_{uuid.uuid4().hex[:6]}",
                            document_id=doc_id,
                            file_name=path_obj.name,
                            content=full_page_text,
                            content_type="text",
                            location=SourceLocation(
                                document_id=doc_id,
                                file_name=path_obj.name,
                                file_type=FileType.PDF,
                                page_number=page_num,
                                bbox=(0.0, 0.0, round(page_w, 2), round(page_h, 2)),
                                page_width=round(page_w, 2),
                                page_height=round(page_h, 2)
                            ),
                            metadata={"page": page_num, "char_count": len(full_page_text)}
                        )
                    )
                
                # 2. Extract tables via pymupdf table finder + ComplexTableRecognizer
                try:
                    tabs = page.find_tables()
                    for t_idx, tab in enumerate(tabs):
                        df = tab.to_pandas()
                        if not df.empty:
                            tab_bbox = getattr(tab, "bbox", (0.0, 0.0, page_w, page_h))
                            rec_tab = ComplexTableRecognizer.process_raw_table(
                                raw_rows=tab.extract(),
                                table_id=f"table_{t_idx + 1}",
                                page_number=page_num
                            )
                            csv_repr = rec_tab.csv_representation or df.to_csv(index=False)
                            chunks.append(
                                ExtractedChunk(
                                    chunk_id=f"{doc_id}_p{page_num}_tab_{t_idx}",
                                    document_id=doc_id,
                                    file_name=path_obj.name,
                                    content=f"Table {t_idx + 1} on Page {page_num}:\n{csv_repr}",
                                    content_type="table",
                                    location=SourceLocation(
                                        document_id=doc_id,
                                        file_name=path_obj.name,
                                        file_type=FileType.PDF,
                                        page_number=page_num,
                                        table_id=f"table_{t_idx + 1}",
                                        bbox=(round(tab_bbox[0], 2), round(tab_bbox[1], 2), round(tab_bbox[2], 2), round(tab_bbox[3], 2)),
                                        page_width=round(page_w, 2),
                                        page_height=round(page_h, 2)
                                    ),
                                    metadata={
                                        "headers": rec_tab.headers,
                                        "row_count": rec_tab.num_rows,
                                        "has_hierarchical_headers": rec_tab.has_hierarchical_headers
                                    }
                                )
                            )
                except Exception:
                    pass

                # 3. Chart De-Rendering (discover vector charts & diagrams)
                try:
                    de_rendered_charts = ChartDeRenderer.de_render_page_charts(path_obj, page_num, doc_id)
                    for c in de_rendered_charts:
                        c_chunk = ChartDeRenderer.to_extracted_chunk(c, doc_id, path_obj.name)
                        chunks.append(c_chunk)
                except Exception:
                    pass

            doc.close()
            
            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=FileType.PDF,
                file_size_bytes=path_obj.stat().st_size,
                content_hash=file_hash,
                page_count=page_count,
                extraction_status="success",
            )
            return meta, chunks

        except Exception as e:
            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=FileType.PDF,
                file_size_bytes=path_obj.stat().st_size if path_obj.exists() else 0,
                content_hash=file_hash,
                extraction_status="failed",
                error_message=str(e),
            )
            return meta, []
