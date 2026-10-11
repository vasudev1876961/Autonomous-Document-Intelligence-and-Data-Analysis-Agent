"""
Citation and Source Reference Verifier:
Verifies that cited sources exist in the manifest and actually ground the claims made.
"""
from typing import Optional
from pydantic import BaseModel, Field
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk

class CitationCheckResult(BaseModel):
    is_valid: bool
    citation_text: str
    target_file_exists: bool
    page_or_cell_valid: bool
    evidence_grounded: bool
    details: str

class CitationVerifier:
    def __init__(self, documents: list[DocumentMetadata], chunks: list[ExtractedChunk]):
        self.doc_map = {d.file_name.lower(): d for d in documents}
        self.chunks = chunks

    def verify_citation(
        self,
        file_name: str,
        page_or_sheet: Optional[str] = None,
        key_term: Optional[str] = None
    ) -> CitationCheckResult:
        doc = self.doc_map.get(file_name.lower())
        if not doc:
            return CitationCheckResult(
                is_valid=False,
                citation_text=f"{file_name} ({page_or_sheet})",
                target_file_exists=False,
                page_or_cell_valid=False,
                evidence_grounded=False,
                details=f"Referenced file '{file_name}' does not exist in ingested documents."
            )

        # Check page validity if PDF
        page_valid = True
        if doc.page_count and page_or_sheet and page_or_sheet.isdigit():
            p_num = int(page_or_sheet)
            if p_num > doc.page_count or p_num < 1:
                page_valid = False

        # Check sheet validity if Excel
        if doc.sheet_names and page_or_sheet and not page_or_sheet.isdigit():
            if page_or_sheet not in doc.sheet_names:
                page_valid = False

        # Check if key term appears in chunk content from this doc
        grounded = True
        if key_term:
            matched_chunks = [
                c for c in self.chunks
                if c.file_name.lower() == file_name.lower() and key_term.lower() in c.content.lower()
            ]
            grounded = len(matched_chunks) > 0

        valid = page_valid and grounded
        details = (
            f"File '{file_name}' verified. "
            f"Location: {'valid' if page_valid else 'invalid'}. "
            f"Content grounding for '{key_term or 'N/A'}': {'confirmed' if grounded else 'not found'}."
        )

        return CitationCheckResult(
            is_valid=valid,
            citation_text=f"{file_name} ({page_or_sheet or 'root'})",
            target_file_exists=True,
            page_or_cell_valid=page_valid,
            evidence_grounded=grounded,
            details=details
        )
