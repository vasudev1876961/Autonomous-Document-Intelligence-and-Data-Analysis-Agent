"""
Ingestion Pipeline Coordinator: Validates, deduplicates, and parses documents into unified chunks.
"""
from pathlib import Path
from typing import Optional
from src.ingestion.metadata import DocumentMetadata, ExtractedChunk, FileType, detect_file_type
from src.ingestion.pdf_parser import PDFParser
from src.ingestion.docx_parser import DOCXParser
from src.ingestion.excel_parser import ExcelParser
from src.ingestion.csv_parser import CSVParser

class IngestionManager:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.excel_parser = ExcelParser()
        self.csv_parser = CSVParser()

    def process_file(self, file_path: Path | str) -> tuple[DocumentMetadata, list[ExtractedChunk]]:
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")

        file_type = detect_file_type(path_obj)
        if file_type == FileType.PDF:
            return self.pdf_parser.parse(path_obj)
        elif file_type == FileType.DOCX:
            return self.docx_parser.parse(path_obj)
        elif file_type == FileType.XLSX:
            return self.excel_parser.parse(path_obj)
        elif file_type == FileType.CSV:
            return self.csv_parser.parse(path_obj)
        else:
            raise ValueError(f"Unsupported file format: {path_obj.suffix}")

    def process_directory(self, dir_path: Path | str) -> tuple[list[DocumentMetadata], list[ExtractedChunk]]:
        path_obj = Path(dir_path)
        docs: list[DocumentMetadata] = []
        all_chunks: list[ExtractedChunk] = []
        seen_hashes: set[str] = set()

        for ext in ["*.pdf", "*.docx", "*.xlsx", "*.csv"]:
            for file_path in path_obj.glob(ext):
                meta, chunks = self.process_file(file_path)
                # Deduplication check
                if meta.content_hash in seen_hashes:
                    meta.extraction_status = "duplicate_skipped"
                    docs.append(meta)
                    continue
                seen_hashes.add(meta.content_hash)
                docs.append(meta)
                all_chunks.extend(chunks)

        return docs, all_chunks
