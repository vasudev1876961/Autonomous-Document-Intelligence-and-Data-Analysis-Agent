"""
Lexical / BM25 search over extracted chunks for exact identifiers, account codes, dates, and metric names.
"""
import re
from typing import Optional
from rank_bm25 import BM25Okapi
from src.ingestion.metadata import ExtractedChunk

class BM25SearchEngine:
    def __init__(self, chunks: Optional[list[ExtractedChunk]] = None):
        self.chunks: list[ExtractedChunk] = []
        self.bm25: Optional[BM25Okapi] = None
        if chunks:
            self.index_chunks(chunks)

    def _tokenize(self, text: str) -> list[str]:
        # Lowercase and extract alphanumeric tokens including hyphens/underscores
        tokens = re.findall(r"\w+", text.lower())
        return tokens

    def index_chunks(self, chunks: list[ExtractedChunk]) -> None:
        self.chunks = chunks
        if not chunks:
            self.bm25 = None
            return
        tokenized_corpus = [self._tokenize(c.content) for c in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 5) -> list[tuple[ExtractedChunk, float]]:
        if not self.bm25 or not self.chunks:
            return []
        tokens = self._tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        
        # Rank by score descending
        scored_pairs = [(self.chunks[i], float(scores[i])) for i in range(len(self.chunks))]
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]
