"""
Unit tests for retrieval mechanisms: BM25, embeddings, vector store, and hybrid fusion.
"""
from pathlib import Path
import pytest
from src.ingestion.metadata import ExtractedChunk, SourceLocation, FileType
from src.retrieval.chunking import StructureAwareChunker
from src.retrieval.keyword_search import BM25SearchEngine
from src.retrieval.hybrid_retrieval import HybridRetriever

def test_structure_aware_chunker():
    chunker = StructureAwareChunker(max_chunk_size=10, overlap=2)
    long_text = "word " * 30
    sub_chunks = chunker.chunk_text(long_text)
    assert len(sub_chunks) > 1

def test_bm25_and_hybrid_search():
    chunks = [
        ExtractedChunk(
            chunk_id="c1",
            document_id="d1",
            file_name="Quarterly_Report.pdf",
            content="Revenue declined due to lower order volumes in Segment A during Q2.",
            location=SourceLocation(document_id="d1", file_name="Quarterly_Report.pdf", file_type=FileType.PDF, page_number=1)
        ),
        ExtractedChunk(
            chunk_id="c2",
            document_id="d1",
            file_name="Quarterly_Report.pdf",
            content="Segment B performance details are undergoing review.",
            location=SourceLocation(document_id="d1", file_name="Quarterly_Report.pdf", file_type=FileType.PDF, page_number=2)
        )
    ]
    
    bm25 = BM25SearchEngine(chunks)
    res = bm25.search("order volumes Segment A", top_k=1)
    assert len(res) == 1
    assert res[0][0].chunk_id == "c1"

    hybrid = HybridRetriever(chunks)
    h_res = hybrid.retrieve("order volumes", top_k=1)
    assert len(h_res) == 1
    assert h_res[0][0].chunk_id == "c1"
