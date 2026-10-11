"""
Hybrid Retrieval Engine combining Lexical BM25 and Semantic Vector Search via Reciprocal Rank Fusion (RRF).
"""
from typing import Any, Optional
from src.ingestion.metadata import ExtractedChunk
from src.retrieval.keyword_search import BM25SearchEngine
from src.retrieval.vector_store import SimpleVectorStore

class HybridRetriever:
    def __init__(self, chunks: Optional[list[ExtractedChunk]] = None):
        self.bm25_engine = BM25SearchEngine(chunks)
        self.vector_store = SimpleVectorStore()
        if chunks:
            self.vector_store.add_chunks(chunks)
        self.chunks = chunks or []

    def index_chunks(self, chunks: list[ExtractedChunk]) -> None:
        self.chunks = chunks
        self.bm25_engine.index_chunks(chunks)
        self.vector_store = SimpleVectorStore()
        self.vector_store.add_chunks(chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[dict[str, Any]] = None,
        lexical_weight: float = 0.5,
        semantic_weight: float = 0.5,
        rrf_k: int = 60,
    ) -> list[tuple[ExtractedChunk, float]]:
        """
        Executes hybrid search using Reciprocal Rank Fusion (RRF) to combine lexical and dense results.
        """
        if not self.chunks:
            return []

        # 1. BM25 search
        bm25_results = self.bm25_engine.search(query, top_k=top_k * 2)
        # 2. Vector search
        vec_results = self.vector_store.search(query, top_k=top_k * 2, filter_metadata=filter_metadata)

        # RRF scoring
        rrf_scores: dict[str, float] = {}
        chunk_map: dict[str, ExtractedChunk] = {}

        for rank, (chunk, score) in enumerate(bm25_results):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + lexical_weight * (1.0 / (rrf_k + rank + 1))

        for rank, (chunk, score) in enumerate(vec_results):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + semantic_weight * (1.0 / (rrf_k + rank + 1))

        sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [(chunk_map[cid], score) for cid, score in sorted_items[:top_k]]
