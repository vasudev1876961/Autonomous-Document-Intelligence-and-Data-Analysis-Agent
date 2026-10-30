"""
JSON Parser for structured datasets, financial data exports, and nested payloads.
Extracts record-level and path-level provenance for autonomous document intelligence.
"""
from pathlib import Path
import json
from typing import Any
import pandas as pd
from src.ingestion.metadata import (
    DocumentMetadata,
    ExtractedChunk,
    FileType,
    SourceLocation,
    compute_file_sha256,
)

class JSONParser:
    """
    Parses JSON files into structured, grounded chunks with JSONPath-style locational references.
    """
    def parse(self, file_path: Path | str) -> tuple[DocumentMetadata, list[ExtractedChunk]]:
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"JSON file not found: {path_obj}")

        file_hash = compute_file_sha256(path_obj)
        doc_id = f"doc_{file_hash[:12]}"
        chunks: list[ExtractedChunk] = []

        try:
            with open(path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. Full Document Summary Chunk
            if isinstance(data, list):
                record_count = len(data)
                # Try creating tabular representation if list of dicts
                if record_count > 0 and isinstance(data[0], dict):
                    try:
                        df = pd.DataFrame(data)
                        csv_repr = df.to_csv(index=False)
                        chunks.append(
                            ExtractedChunk(
                                chunk_id=f"{doc_id}_table_full",
                                document_id=doc_id,
                                file_name=path_obj.name,
                                content=f"JSON Tabular Dataset '{path_obj.name}' ({record_count} records):\n{csv_repr}",
                                content_type="table",
                                location=SourceLocation(
                                    document_id=doc_id,
                                    file_name=path_obj.name,
                                    file_type=FileType.JSON,
                                    cell_range=f"$[0..{record_count - 1}]"
                                ),
                                metadata={"record_count": record_count, "columns": [str(c) for c in df.columns]}
                            )
                        )
                    except Exception:
                        pass

                # Individual Record Chunks
                for idx, item in enumerate(data):
                    item_str = json.dumps(item, ensure_ascii=False) if isinstance(item, (dict, list)) else str(item)
                    chunks.append(
                        ExtractedChunk(
                            chunk_id=f"{doc_id}_item_{idx}",
                            document_id=doc_id,
                            file_name=path_obj.name,
                            content=f"[{path_obj.name} $[{idx}]] {item_str}",
                            content_type="key_value" if isinstance(item, dict) else "text",
                            location=SourceLocation(
                                document_id=doc_id,
                                file_name=path_obj.name,
                                file_type=FileType.JSON,
                                cell_range=f"$[{idx}]",
                                row_index=idx + 1
                            ),
                            metadata={"index": idx, "raw_data": item if isinstance(item, dict) else None}
                        )
                    )

            elif isinstance(data, dict):
                # Overview chunk
                overview_lines = [f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}" for k, v in list(data.items())[:20]]
                chunks.append(
                    ExtractedChunk(
                        chunk_id=f"{doc_id}_overview",
                        document_id=doc_id,
                        file_name=path_obj.name,
                        content=f"JSON Object '{path_obj.name}' ({len(data)} top-level keys):\n" + "\n".join(overview_lines),
                        content_type="text",
                        location=SourceLocation(
                            document_id=doc_id,
                            file_name=path_obj.name,
                            file_type=FileType.JSON,
                            cell_range="$"
                        ),
                        metadata={"top_level_keys": list(data.keys())}
                    )
                )

                # Decompose top-level fields
                for k, v in data.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        # Nested table array
                        try:
                            df_sub = pd.DataFrame(v)
                            chunks.append(
                                ExtractedChunk(
                                    chunk_id=f"{doc_id}_{k}_table",
                                    document_id=doc_id,
                                    file_name=path_obj.name,
                                    content=f"JSON Array '{path_obj.name} $.{k}' ({len(v)} records):\n{df_sub.to_csv(index=False)}",
                                    content_type="table",
                                    location=SourceLocation(
                                        document_id=doc_id,
                                        file_name=path_obj.name,
                                        file_type=FileType.JSON,
                                        section_heading=f"$.{k}",
                                        cell_range=f"$.{k}[0..{len(v)-1}]"
                                    ),
                                    metadata={"parent_key": k, "record_count": len(v)}
                                )
                            )
                        except Exception:
                            pass
                    else:
                        val_str = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
                        chunks.append(
                            ExtractedChunk(
                                chunk_id=f"{doc_id}_{k}",
                                document_id=doc_id,
                                file_name=path_obj.name,
                                content=f"[{path_obj.name} $.{k}] {k}: {val_str}",
                                content_type="key_value",
                                location=SourceLocation(
                                    document_id=doc_id,
                                    file_name=path_obj.name,
                                    file_type=FileType.JSON,
                                    section_heading=f"$.{k}",
                                    cell_range=f"$.{k}"
                                ),
                                metadata={"key": k}
                            )
                        )

            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=FileType.JSON,
                file_size_bytes=path_obj.stat().st_size,
                content_hash=file_hash,
                extraction_status="success"
            )
            return meta, chunks

        except Exception as e:
            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=FileType.JSON,
                file_size_bytes=path_obj.stat().st_size if path_obj.exists() else 0,
                content_hash=file_hash,
                extraction_status="error",
                error_message=str(e)
            )
            return meta, []

