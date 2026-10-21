"""
Embedding generation using SentenceTransformers or TF-IDF dense fallback for semantic representation.
Optimized with singleton model caching and query vector caching.
"""
from typing import Any, Optional
import os
import numpy as np

# Suppress HuggingFace parallelism & verbose warning overhead
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Global singleton cache for loaded embedding models to prevent repeated reload overhead
_MODEL_CACHE: dict[str, Any] = {}
_QUERY_CACHE: dict[str, np.ndarray] = {}
_MAX_QUERY_CACHE_SIZE = 128

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.fallback_vectorizer = None
        self._init_model()

    def _init_model(self):
        # 1. Check singleton cache first
        if self.model_name in _MODEL_CACHE:
            self.model = _MODEL_CACHE[self.model_name]
            return

        try:
            from sentence_transformers import SentenceTransformer
            # Load model once and store in cache
            model = SentenceTransformer(self.model_name)
            _MODEL_CACHE[self.model_name] = model
            self.model = model
        except Exception:
            # Fallback to TF-IDF dense embedding
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.fallback_vectorizer = TfidfVectorizer(max_features=384)
            self.model = None

    def fit_fallback(self, corpus: list[str]) -> None:
        if self.fallback_vectorizer and corpus:
            try:
                self.fallback_vectorizer.fit(corpus)
            except Exception:
                pass

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        # Optimize single query caching
        if len(texts) == 1:
            q_key = f"{self.model_name}::{texts[0]}"
            if q_key in _QUERY_CACHE:
                return _QUERY_CACHE[q_key].copy()

        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                res = np.array(embeddings, dtype=np.float32)
                if len(texts) == 1:
                    if len(_QUERY_CACHE) >= _MAX_QUERY_CACHE_SIZE:
                        _QUERY_CACHE.clear()
                    _QUERY_CACHE[f"{self.model_name}::{texts[0]}"] = res
                return res
            except Exception:
                pass

        # Use fallback TF-IDF
        if self.fallback_vectorizer is None:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.fallback_vectorizer = TfidfVectorizer(max_features=384)
            self.fallback_vectorizer.fit(texts)

        try:
            dense = self.fallback_vectorizer.transform(texts).toarray()
            # Normalize vectors
            norms = np.linalg.norm(dense, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            res = (dense / norms).astype(np.float32)
            if len(texts) == 1:
                if len(_QUERY_CACHE) >= _MAX_QUERY_CACHE_SIZE:
                    _QUERY_CACHE.clear()
                _QUERY_CACHE[f"{self.model_name}::{texts[0]}"] = res
            return res
        except Exception:
            # Unit vectors as extreme safeguard
            vecs = np.ones((len(texts), 384), dtype=np.float32)
            return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

