"""
Text and Markdown Document Parser.
Performs hierarchical section decomposition, line-numbered provenance tracking,
and embedded tabular extraction for autonomous document analysis.
"""
from pathlib import Path
import re
from typing import Optional
from src.ingestion.metadata import (
    DocumentMetadata,
    ExtractedChunk,
    FileType,
    SourceLocation,
    compute_file_sha256,
)

class TextParser:
    """
    Parses plain text (.txt) and markdown (.md) documents with section-level provenance.
    """
    def __init__(self, chunk_size_lines: int = 25):
        self.chunk_size_lines = chunk_size_lines

    def parse(self, file_path: Path | str) -> tuple[DocumentMetadata, list[ExtractedChunk]]:
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Text file not found: {path_obj}")

        file_hash = compute_file_sha256(path_obj)
        doc_id = f"doc_{file_hash[:12]}"
        is_md = path_obj.suffix.lower() == ".md"
        file_type = FileType.MD if is_md else FileType.TXT

        chunks: list[ExtractedChunk] = []

        try:
            with open(path_obj, "r", encoding="utf-8", errors="replace") as f:
                raw_text = f.read()

            lines = raw_text.splitlines()
            current_section = "Introduction"
            buffer_lines: list[tuple[int, str]] = []
            table_buffer: list[tuple[int, str]] = []
            in_table = False

            def flush_buffer():
                nonlocal buffer_lines
                if not buffer_lines:
                    return
                start_line = buffer_lines[0][0]
                end_line = buffer_lines[-1][0]
                text_content = "\n".join([line for _, line in buffer_lines]).strip()
                if text_content:
                    chunks.append(
                        ExtractedChunk(
                            chunk_id=f"{doc_id}_lines_{start_line}_{end_line}",
                            document_id=doc_id,
                            file_name=path_obj.name,
                            content=text_content,
                            content_type="text",
                            location=SourceLocation(
                                document_id=doc_id,
                                file_name=path_obj.name,
                                file_type=file_type,
                                section_heading=current_section,
                                cell_range=f"Lines {start_line}-{end_line}"
                            ),
                            metadata={"start_line": start_line, "end_line": end_line, "section": current_section}
                        )
                    )
                buffer_lines = []

            def flush_table():
                nonlocal table_buffer
                if not table_buffer:
                    return
                start_line = table_buffer[0][0]
                end_line = table_buffer[-1][0]
                table_str = "\n".join([line for _, line in table_buffer]).strip()
                if table_str:
                    chunks.append(
                        ExtractedChunk(
                            chunk_id=f"{doc_id}_table_{start_line}_{end_line}",
                            document_id=doc_id,
                            file_name=path_obj.name,
                            content=table_str,
                            content_type="table",
                            location=SourceLocation(
                                document_id=doc_id,
                                file_name=path_obj.name,
                                file_type=file_type,
                                section_heading=current_section,
                                cell_range=f"Table (Lines {start_line}-{end_line})"
                            ),
                            metadata={"start_line": start_line, "end_line": end_line, "section": current_section}
                        )
                    )
                table_buffer = []

            for line_no, line in enumerate(lines, start=1):
                stripped = line.strip()

                # Check markdown table row
                if stripped.startswith("|") and stripped.endswith("|"):
                    if not in_table:
                        flush_buffer()
                        in_table = True
                    table_buffer.append((line_no, line))
                    continue
                else:
                    if in_table:
                        flush_table()
                        in_table = False

                # Section Heading Detection (# or uppercase SECTION)
                heading_match = re.match(r"^(#{1,4})\s+(.+)$", stripped) or re.match(r"^([A-Z0-9\s\-_]{3,40}):$", stripped)
                if heading_match:
                    flush_buffer()
                    current_section = heading_match.group(2) if heading_match.lastindex >= 2 else heading_match.group(1)
                    current_section = current_section.strip()
                    buffer_lines.append((line_no, line))
                    continue

                buffer_lines.append((line_no, line))
                if len(buffer_lines) >= self.chunk_size_lines:
                    flush_buffer()

            if in_table:
                flush_table()
            flush_buffer()

            meta = DocumentMetadata(
                document_id=doc_id,
                file_name=path_obj.name,
                file_path=str(path_obj),
                file_type=file_type,
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
                file_type=file_type,
                file_size_bytes=path_obj.stat().st_size if path_obj.exists() else 0,
                content_hash=file_hash,
                extraction_status="error",
                error_message=str(e)
            )
            return meta, []

