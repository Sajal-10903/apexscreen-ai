# Multi-stage Dockerfile for AI Interview System

# ── Stage 1: Build Frontend ─────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Backend + Final Runtime ────────────────
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for PyMuPDF and SQLite
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, knowledge base, and scripts
COPY backend/ ./backend/
COPY knowledge_base/ ./knowledge_base/
COPY scripts/ ./scripts/
COPY .env.example ./.env.example
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create runtime directories
RUN mkdir -p /app/data /app/chroma_db /app/uploads

# Ingest knowledge base at build time (bakes the vector index into the
# image so it works out-of-the-box even without bind-mounted volumes).
# docker-entrypoint.sh re-verifies and re-ingests at container startup in
# case a mounted (empty) host volume shadows this baked-in data.
RUN python scripts/ingest_knowledge.py

# Grant ownership to the non-root runtime user *after* ingestion so all
# generated files (chroma_db, __pycache__, etc.) are writable at runtime.
RUN chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

ENV BACKEND_HOST=0.0.0.0
ENV BACKEND_PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]

# Run FastAPI backend with Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
