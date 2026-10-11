"""
CSV Parser using pandas with robust delimiter detection and row-level provenance.
"""
from pathlib import Path
import uuid
import pandas as pd
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk, FileType, SourceLocation, compute_file_sha256

class CSVParser:
    def parse(self, file_path: Path) -> tuple[DocumentMetadata, list[ExtractedChunk]]:
        path_obj = Path(file_path)
        file_hash = compute_file_sha256(path_obj)
        doc_id = f"doc_{file_hash[:12]}"
        chunks: list[ExtractedChunk] = []

        try:
            # Try automatic separator detection
            df = pd.read_csv(str(path_obj), sep=None, engine="python")
            row_count, col_count = df.shape
            
            # Full table summary chunk
            csv_repr = df.to_csv(index=False)
            chunks.append(
                ExtractedChunk(
                    chunk_id=f"{doc_id}_table_full",
                    document_id=doc_id,
                    file_name=path_obj.name,
                    content=f"CSV Dataset '{path_obj.name}' ({row_count} rows, {col_count} columns):\n{csv_repr}",
                    content_type="table",
                    location=SourceLocation(
                        document_id=doc_id,
                        file_name=path_obj.name,
                        file_type=FileType.CSV,
                        cell_range=f"1..{row_count}"
                    ),
                    metadata={
                        "columns": [str(c) for c in df.columns],
                        "row_count": row_count,
                        "col_count": col_count
                    }
                )
            )

            # Granular row chunks
            for r_idx, row in df.iterrows():
                row_dict = {str(k): (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                row_desc = ", ".join([f"{k}: {v}" for k, v in row_dict.items() if v is not None])
                chunks.append(
                    ExtractedChunk(
                        chunk_id=f"{doc_id}_r{r_idx + 2}",
                        document_id=doc_id,
                        file_name=path_obj.name,
                        content=f"[{path_obj.name} Row {r_idx + 2}] {row_desc}",
                        content_type="key_value",
                        location=SourceLocation(
                            document_id=doc_id,
                            file_name=path_obj.name,
                            file_type=FileType.CSV,
                            row_index=r_idx + 2,
                            cell_range=f"Row {r_idx + 2}"
                        ),
                        metadata={"row_data": row_dict}
                    )
                )

            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=FileType.CSV,
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
                file_type=FileType.CSV,
                file_size_bytes=path_obj.stat().st_size if path_obj.exists() else 0,
                content_hash=file_hash,
                extraction_status="failed",
                error_message=str(e),
            )
            return meta, []
