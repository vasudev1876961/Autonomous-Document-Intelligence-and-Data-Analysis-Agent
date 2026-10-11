"""
Data structures and metadata schemas for document ingestion and evidence representation.
"""
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import hashlib
from pydantic import BaseModel, Field

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    UNKNOWN = "unknown"

class ClaimCategory(str, Enum):
    OBSERVED_FACT = "Observed fact"
    SUPPORTED_INTERPRETATION = "Supported interpretation"
    HYPOTHESIS = "Hypothesis"

class SourceLocation(BaseModel):
    document_id: str
    file_name: str
    file_type: FileType
    page_number: Optional[int] = None
    sheet_name: Optional[str] = None
    cell_range: Optional[str] = None
    table_id: Optional[str] = None
    section_heading: Optional[str] = None
    row_index: Optional[int] = None

    def to_citation_str(self) -> str:
        parts = [self.file_name]
        if self.page_number is not None:
            parts.append(f"Page {self.page_number}")
        if self.sheet_name:
            parts.append(f"Sheet '{self.sheet_name}'")
        if self.cell_range:
            parts.append(f"Cells {self.cell_range}")
        if self.section_heading:
            parts.append(f"Section '{self.section_heading}'")
        return ", ".join(parts)

class DocumentMetadata(BaseModel):
    document_id: str
    file_name: str
    file_path: str
    file_type: FileType
    file_size_bytes: int
    content_hash: str
    page_count: Optional[int] = None
    sheet_names: list[str] = Field(default_factory=list)
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extraction_status: str = "success"
    error_message: Optional[str] = None

class ExtractedChunk(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    content: str
    content_type: str = "text" # "text", "table", "key_value"
    location: SourceLocation
    units: Optional[str] = None
    reporting_period: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

def compute_file_sha256(file_path: Path) -> str:
    """Calculate the SHA-256 hash of a file for tamper-proofing and duplicate detection."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def detect_file_type(file_path: Path) -> FileType:
    suffix = file_path.suffix.lower()
    mapping = {
        ".pdf": FileType.PDF,
        ".docx": FileType.DOCX,
        ".xlsx": FileType.XLSX,
        ".csv": FileType.CSV,
    }
    return mapping.get(suffix, FileType.UNKNOWN)
