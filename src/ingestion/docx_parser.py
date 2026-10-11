"""
DOCX Parser using python-docx for paragraph and table extraction with section provenance.
"""
from pathlib import Path
import uuid
import docx
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk, FileType, SourceLocation, compute_file_sha256

class DOCXParser:
    def parse(self, file_path: Path) -> tuple[DocumentMetadata, list[ExtractedChunk]]:
        path_obj = Path(file_path)
        file_hash = compute_file_sha256(path_obj)
        doc_id = f"doc_{file_hash[:12]}"
        chunks: list[ExtractedChunk] = []

        try:
            doc = docx.Document(str(path_obj))
            current_heading = "General"
            
            # Paragraphs
            for p_idx, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if not text:
                    continue
                
                if para.style.name.startswith("Heading"):
                    current_heading = text
                
                chunks.append(
                    ExtractedChunk(
                        chunk_id=f"{doc_id}_p_{p_idx}_{uuid.uuid4().hex[:6]}",
                        document_id=doc_id,
                        file_name=path_obj.name,
                        content=text,
                        content_type="text",
                        location=SourceLocation(
                            document_id=doc_id,
                            file_name=path_obj.name,
                            file_type=FileType.DOCX,
                            section_heading=current_heading,
                            row_index=p_idx,
                        ),
                        metadata={"section": current_heading, "char_count": len(text)}
                    )
                )

            # Tables
            for t_idx, table in enumerate(doc.tables):
                table_rows = []
                for row in table.rows:
                    row_vals = [cell.text.strip() for cell in row.cells]
                    table_rows.append(" | ".join(row_vals))
                
                if table_rows:
                    table_content = f"Table {t_idx + 1} under Section '{current_heading}':\n" + "\n".join(table_rows)
                    chunks.append(
                        ExtractedChunk(
                            chunk_id=f"{doc_id}_tab_{t_idx}",
                            document_id=doc_id,
                            file_name=path_obj.name,
                            content=table_content,
                            content_type="table",
                            location=SourceLocation(
                                document_id=doc_id,
                                file_name=path_obj.name,
                                file_type=FileType.DOCX,
                                table_id=f"table_{t_idx + 1}",
                                section_heading=current_heading,
                            ),
                            metadata={"section": current_heading, "row_count": len(table_rows)}
                        )
                    )

            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=FileType.DOCX,
                file_size_bytes=path_obj.stat().st_size,
                content_hash=file_hash,
                extraction_status="success",
            )
            return meta, chunks

        except Exception as e:
            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=FileType.DOCX,
                file_size_bytes=path_obj.stat().st_size if path_obj.exists() else 0,
                content_hash=file_hash,
                extraction_status="failed",
                error_message=str(e),
            )
            return meta, []
