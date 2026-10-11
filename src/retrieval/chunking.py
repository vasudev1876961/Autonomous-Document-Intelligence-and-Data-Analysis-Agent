"""
Chunking strategies that preserve table headers, sections, and contextual metadata.
"""
from typing import Optional
from src.ingestion.metadata import ExtractedChunk, SourceLocation

class StructureAwareChunker:
    def __init__(self, max_chunk_size: int = 500, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        words = text.split()
        if len(words) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.max_chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end >= len(words):
                break
            start += (self.max_chunk_size - self.overlap)
        return chunks

    def process_chunks(self, raw_chunks: list[ExtractedChunk]) -> list[ExtractedChunk]:
        """Refines raw extracted chunks: splits long prose, but keeps tables intact to avoid header dissociation."""
        refined: list[ExtractedChunk] = []
        for ch in raw_chunks:
            if ch.content_type == "table":
                # Keep table intact with its header
                refined.append(ch)
            else:
                sub_texts = self.chunk_text(ch.content)
                if len(sub_texts) == 1:
                    refined.append(ch)
                else:
                    for idx, st in enumerate(sub_texts):
                        sub_chunk = ExtractedChunk(
                            chunk_id=f"{ch.chunk_id}_sub{idx}",
                            document_id=ch.document_id,
                            file_name=ch.file_name,
                            content=st,
                            content_type=ch.content_type,
                            location=ch.location,
                            units=ch.units,
                            reporting_period=ch.reporting_period,
                            metadata={**ch.metadata, "sub_chunk_index": idx}
                        )
                        refined.append(sub_chunk)
        return refined
