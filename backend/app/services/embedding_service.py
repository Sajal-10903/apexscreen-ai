"""Embedding service using sentence-transformers."""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

_model_instance = None


def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    """Lazy-load the sentence-transformers model."""
    global _model_instance
    if _model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {model_name}")
            _model_instance = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(f"Embedding model loading failed: {e}")
    return _model_instance


def generate_embeddings(
    texts: list[str], model_name: str = "all-MiniLM-L6-v2"
) -> list[list[float]]:
    """Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed.
        model_name: Name of the sentence-transformers model.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    if not texts:
        return []

    model = _get_model(model_name)
    try:
        embeddings = model.encode(texts, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise RuntimeError(f"Embedding generation failed: {e}")


def generate_embedding(
    text: str, model_name: str = "all-MiniLM-L6-v2"
) -> list[float]:
    """Generate embedding for a single text."""
    results = generate_embeddings([text], model_name)
    return results[0] if results else []


def get_embedding_dimension(model_name: str = "all-MiniLM-L6-v2") -> int:
    """Get the embedding dimension for the model."""
    model = _get_model(model_name)
    return model.get_sentence_embedding_dimension()


def reset_model():
    """Reset the model instance (for testing)."""
    global _model_instance
    _model_instance = None
