"""
Vector Store for dense semantic retrieval with metadata filtering.
Optimized with pre-normalized embeddings and vectorized similarity search.
"""
from typing import Any, Optional
import numpy as np
from src.ingestion.metadata import ExtractedChunk
from src.retrieval.embeddings import EmbeddingEngine

class SimpleVectorStore:
    def __init__(self, embedding_engine: Optional[EmbeddingEngine] = None):
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.chunks: list[ExtractedChunk] = []
        self.embeddings: Optional[np.ndarray] = None

    def add_chunks(self, chunks: list[ExtractedChunk]) -> None:
        if not chunks:
            return
        self.chunks.extend(chunks)
        texts = [c.content for c in self.chunks]
        if self.embedding_engine.fallback_vectorizer is not None:
            self.embedding_engine.fit_fallback(texts)
        raw_embs = self.embedding_engine.encode(texts)
        # Pre-normalize for instant cosine distance dot-products
        norms = np.linalg.norm(raw_embs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings = (raw_embs / norms).astype(np.float32)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[dict[str, Any]] = None
    ) -> list[tuple[ExtractedChunk, float]]:
        if not self.chunks or self.embeddings is None or len(self.embeddings) == 0:
            return []

        query_vec = self.embedding_engine.encode([query])[0]
        # Unit normalize query vector
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 0:
            query_vec = query_vec / q_norm

        scores = np.dot(self.embeddings, query_vec)

        # Fast path if no filter_metadata
        if not filter_metadata:
            # Top-k indices using argpartition if large, or argsort
            if len(scores) > top_k * 2:
                top_indices = np.argpartition(scores, -top_k)[-top_k:]
                top_indices = top_indices[np.argsort(-scores[top_indices])]
            else:
                top_indices = np.argsort(-scores)[:top_k]
            return [(self.chunks[i], float(scores[i])) for i in top_indices]

        # Filtered path
        results: list[tuple[ExtractedChunk, float]] = []
        for idx, score in enumerate(scores):
            chunk = self.chunks[idx]
            match = True
            for k, v in filter_metadata.items():
                if getattr(chunk.location, k, None) != v and chunk.metadata.get(k) != v:
                    match = False
                    break
            if match:
                results.append((chunk, float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

