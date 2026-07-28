from typing import List
import numpy as np
from config.settings import settings
from config.logger import logger

try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False


class EmbeddingService:
    """Embedding Generator Service using SentenceTransformers with lightweight fallback."""

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self._model = None

    def initialize(self) -> None:
        if _ST_AVAILABLE:
            try:
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded SentenceTransformer embedding model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not download/load SentenceTransformer model ({e}). Using deterministic mock fallback.")
                self._model = None
        else:
            logger.warning("sentence-transformers package not available. Using deterministic mock fallback.")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single text string."""
        if self._model:
            try:
                vector = self._model.encode(text, convert_to_numpy=True)
                return vector.tolist()
            except Exception as e:
                logger.error(f"Error encoding text with SentenceTransformers: {e}")

        # Deterministic feature hashing fallback embedding
        return self._generate_deterministic_embedding(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text strings."""
        if not texts:
            return []

        if self._model:
            try:
                vectors = self._model.encode(texts, convert_to_numpy=True)
                return vectors.tolist()
            except Exception as e:
                logger.error(f"Batch encoding error: {e}")

        return [self._generate_deterministic_embedding(t) for t in texts]

    def _generate_deterministic_embedding(self, text: str) -> List[float]:
        """Generate pseudo-random normalized vector based on text hash for offline / fallback environments."""
        import hashlib
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dimension)
        norm = np.linalg.norm(vec) + 1e-9
        return (vec / norm).tolist()


embedding_service = EmbeddingService()
