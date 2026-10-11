"""
PDF Parser using PyMuPDF (fitz) for text and table extraction with page-level provenance.
"""
from pathlib import Path
import uuid
import pymupdf
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk, FileType, SourceLocation, compute_file_sha256

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
                
                # 1. Extract text blocks
                text = page.get_text("text").strip()
                if text:
                    chunks.append(
                        ExtractedChunk(
                            chunk_id=f"{doc_id}_p{page_num}_txt_{uuid.uuid4().hex[:6]}",
                            document_id=doc_id,
                            file_name=path_obj.name,
                            content=text,
                            content_type="text",
                            location=SourceLocation(
                                document_id=doc_id,
                                file_name=path_obj.name,
                                file_type=FileType.PDF,
                                page_number=page_num,
                            ),
                            metadata={"page": page_num, "char_count": len(text)}
                        )
                    )
                
                # 2. Extract tables if available via pymupdf table finder
                try:
                    tabs = page.find_tables()
                    for t_idx, tab in enumerate(tabs):
                        df = tab.to_pandas()
                        if not df.empty:
                            csv_repr = df.to_csv(index=False)
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
                                        table_id=f"table_{t_idx + 1}"
                                    ),
                                    metadata={"headers": list(df.columns), "row_count": len(df)}
                                )
                            )
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
