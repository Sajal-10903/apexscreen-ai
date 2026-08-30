"""RAG service: ChromaDB vector store management and similarity search."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_chroma_client = None


def _get_chroma_client(persist_directory: str | None = None):
    """Get or create the ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb

        if persist_directory is None:
            from backend.app.core.config import get_settings
            persist_directory = str(get_settings().chroma_directory)

        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=persist_directory)
        logger.info(f"ChromaDB client initialized at: {persist_directory}")
    return _chroma_client


def reset_client():
    """Reset the ChromaDB client (for testing)."""
    global _chroma_client
    _chroma_client = None


def get_or_create_collection(collection_name: str, persist_directory: str | None = None):
    """Get or create a ChromaDB collection."""
    client = _get_chroma_client(persist_directory)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def ingest_documents(
    collection_name: str,
    chunks: list[str],
    metadatas: list[dict],
    ids: list[str],
    embeddings: list[list[float]],
    persist_directory: str | None = None,
) -> int:
    """Ingest document chunks into a ChromaDB collection.

    Args:
        collection_name: Name of the collection.
        chunks: Text chunks.
        metadatas: Metadata for each chunk.
        ids: Unique IDs for each chunk.
        embeddings: Pre-computed embeddings.
        persist_directory: ChromaDB directory (optional override).

    Returns:
        Number of chunks ingested.
    """
    if not chunks:
        return 0

    collection = get_or_create_collection(collection_name, persist_directory)

    # ChromaDB has a batch size limit, process in batches
    batch_size = 500
    total = 0
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_metas = metadatas[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        batch_embeds = embeddings[i:i + batch_size]

        collection.upsert(
            documents=batch_chunks,
            metadatas=batch_metas,
            ids=batch_ids,
            embeddings=batch_embeds,
        )
        total += len(batch_chunks)

    logger.info(f"Ingested {total} chunks into collection '{collection_name}'")
    return total


def search(
    collection_name: str,
    query_texts: list[str] | None = None,
    query_embeddings: list[list[float]] | None = None,
    n_results: int = 5,
    where: dict | None = None,
    persist_directory: str | None = None,
) -> dict:
    """Search for similar documents in a collection.

    Args:
        collection_name: Collection to search.
        query_texts: Text queries (will be embedded by ChromaDB).
        query_embeddings: Pre-computed query embeddings.
        n_results: Number of results per query.
        where: Optional metadata filter.
        persist_directory: ChromaDB directory (optional).

    Returns:
        ChromaDB query results dict with documents, metadatas, distances.
    """
    collection = get_or_create_collection(collection_name, persist_directory)

    # Check if collection has data
    if collection.count() == 0:
        logger.warning(f"Collection '{collection_name}' is empty")
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    query_kwargs = {"n_results": min(n_results, collection.count())}

    if query_embeddings is not None:
        query_kwargs["query_embeddings"] = query_embeddings
    elif query_texts is not None:
        query_kwargs["query_texts"] = query_texts
    else:
        raise ValueError("Either query_texts or query_embeddings must be provided")

    if where:
        query_kwargs["where"] = where

    try:
        results = collection.query(**query_kwargs)
        return results
    except Exception as e:
        logger.error(f"ChromaDB search error: {e}")
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}


def search_with_embeddings(
    collection_name: str,
    query_text: str,
    n_results: int = 5,
    persist_directory: str | None = None,
) -> list[dict]:
    """High-level search: embed query, search, return formatted results.

    Returns a list of dicts with: text, metadata, score.
    """
    from backend.app.services.embedding_service import generate_embedding

    # Generate embedding for the query
    query_embedding = generate_embedding(query_text)

    results = search(
        collection_name=collection_name,
        query_embeddings=[query_embedding],
        n_results=n_results,
        persist_directory=persist_directory,
    )

    formatted = []
    if results["documents"] and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

        for doc, meta, dist in zip(docs, metas, dists):
            formatted.append({
                "text": doc,
                "metadata": meta,
                "score": 1.0 - dist,  # Convert distance to similarity score
            })

    return formatted


def collection_exists_and_populated(collection_name: str, persist_directory: str | None = None) -> bool:
    """Check if a collection exists and has data."""
    try:
        collection = get_or_create_collection(collection_name, persist_directory)
        return collection.count() > 0
    except Exception:
        return False


def get_collection_count(collection_name: str, persist_directory: str | None = None) -> int:
    """Get the number of documents in a collection."""
    try:
        collection = get_or_create_collection(collection_name, persist_directory)
        return collection.count()
    except Exception:
        return 0
