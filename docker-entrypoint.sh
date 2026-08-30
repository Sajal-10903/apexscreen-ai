#!/bin/sh
# Container entrypoint.
#
# The knowledge base (ChromaDB) is baked into the image at build time
# (see Dockerfile), but docker-compose.yml bind-mounts host directories
# for ./data, ./chroma_db, and ./uploads so candidate/interview data
# persists across container restarts. On a *fresh* host checkout, those
# host directories are empty, and mounting them over the image's
# directories would shadow the pre-ingested vector index, leaving RAG
# retrieval with nothing to retrieve.
#
# To make the deployment resilient regardless of mount strategy (bind
# mount, named volume, or none), we verify the ChromaDB collections are
# actually populated at container startup and re-run ingestion if not.
# Ingestion is idempotent and fast (a few seconds on CPU).
set -e

CHROMA_DIR="${CHROMA_PERSIST_DIRECTORY:-./chroma_db}"

echo "Checking knowledge base index at: $CHROMA_DIR"

NEEDS_INGEST=0
if [ ! -f "$CHROMA_DIR/chroma.sqlite3" ]; then
    NEEDS_INGEST=1
else
    # Verify at least one collection actually has vectors, not just an
    # empty sqlite file.
    python -c "
import sys
sys.path.insert(0, '.')
from backend.app.services.rag_service import collection_exists_and_populated
ok = all(collection_exists_and_populated(c) for c in ('ai_ml', 'backend', 'data_science'))
sys.exit(0 if ok else 1)
" || NEEDS_INGEST=1
fi

if [ "$NEEDS_INGEST" = "1" ]; then
    echo "Knowledge base is empty or incomplete — running ingestion..."
    python scripts/ingest_knowledge.py
else
    echo "Knowledge base already indexed — skipping ingestion."
fi

exec "$@"
