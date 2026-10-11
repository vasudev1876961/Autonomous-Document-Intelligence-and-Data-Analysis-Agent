"""
Embedding generation using SentenceTransformers or TF-IDF dense fallback for semantic representation.
"""
from typing import Optional
import numpy as np

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.fallback_vectorizer = None
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Try loading or initializing
            self.model = SentenceTransformer(self.model_name)
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

        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                return np.array(embeddings, dtype=np.float32)
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
            return (dense / norms).astype(np.float32)
        except Exception:
            # Random unit vectors as extreme safeguard
            vecs = np.ones((len(texts), 384), dtype=np.float32)
            return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
