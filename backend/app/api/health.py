"""Health check endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.database import get_db
from backend.app.models.schemas import HealthResponse
from backend.app.services.llm_service import LLMService
from backend.app.services.rag_service import collection_exists_and_populated

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """System health check with subsystem status."""
    settings = get_settings()
    llm = LLMService.get_provider()

    # Check database
    db_status = "connected"
    try:
        db.execute(
            __import__("sqlalchemy").text("SELECT 1")
        )
    except Exception:
        db_status = "error"

    # Check vector DB
    vector_status = "connected"
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(settings.chroma_directory))
        client.heartbeat()
    except Exception:
        vector_status = "error"

    # Check knowledge base
    kb_indexed = any(
        collection_exists_and_populated(coll)
        for coll in ["ai_ml", "backend", "data_science"]
    )

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        llm_available=settings.is_llm_available,
        llm_mode=llm.provider_name,
        database=db_status,
        vector_db=vector_status,
        embedding_model=settings.embedding_model,
        knowledge_base_indexed=kb_indexed,
    )
