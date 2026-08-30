#!/usr/bin/env python3
"""Knowledge base ingestion script.

Processes documents from the knowledge_base/ directory:
1. Loads PDF and Markdown files
2. Extracts and cleans text
3. Splits into meaningful chunks with overlap
4. Generates embeddings using sentence-transformers
5. Stores in ChromaDB with metadata

Usage:
    python scripts/ingest_knowledge.py
"""

import hashlib
import os
import re
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF using PyMuPDF."""
    import fitz
    doc = fitz.open(str(file_path))
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text("text"))
    doc.close()
    return "\n\n".join(text_parts)


def extract_text_from_markdown(file_path: Path) -> str:
    """Read text from a markdown file."""
    return file_path.read_text(encoding="utf-8")


def clean_text(text: str) -> str:
    """Clean extracted text."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def section_aware_chunking(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    document_name: str = "",
) -> list[dict]:
    """Split text into chunks using section-aware strategy.

    Strategy:
    1. Split by section headers (##, ###) first
    2. Within each section, split by paragraphs
    3. If a paragraph is still too large, split by sentences/words
    4. Apply overlap between chunks for context continuity
    """
    chunks = []
    current_section = "Introduction"

    # Normalize line endings and ensure headers can match at the very start
    text = "\n" + text.strip()

    # Split by markdown headers
    parts = re.split(r'\n(#{1,3}\s+[^\n]+)', text)

    current_text = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue

        header_match = re.match(r'^#{1,3}\s+(.+)$', part)
        if header_match:
            if current_text.strip():
                section_chunks = _split_section(
                    current_text, chunk_size, chunk_overlap,
                    document_name, current_section
                )
                chunks.extend(section_chunks)
                current_text = ""
            current_section = header_match.group(1).strip()
        else:
            current_text += "\n\n" + part

    if current_text.strip():
        section_chunks = _split_section(
            current_text, chunk_size, chunk_overlap,
            document_name, current_section
        )
        chunks.extend(section_chunks)

    return chunks


def _split_text_into_units(text: str, chunk_size: int) -> list[str]:
    """Break text into units (paragraphs, sentences, or word clusters) each <= chunk_size."""
    paragraphs = text.split('\n\n')
    units = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= chunk_size:
            units.append(para)
        else:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if len(sent) <= chunk_size:
                    units.append(sent)
                else:
                    words = sent.split(' ')
                    cur_w = ""
                    for w in words:
                        if not w:
                            continue
                        if len(cur_w) + len(w) + 1 <= chunk_size:
                            cur_w += (" " + w if cur_w else w)
                        else:
                            if cur_w:
                                units.append(cur_w)
                            cur_w = w[:chunk_size]
                    if cur_w:
                        units.append(cur_w)
    return units


def _split_section(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    document_name: str,
    section: str,
) -> list[dict]:
    """Split a section's text into chunks of maximum size with overlap."""
    units = _split_text_into_units(text, chunk_size)
    if not units:
        return []

    chunks = []
    current_chunk = ""
    chunk_idx = 0

    for unit in units:
        if not current_chunk:
            current_chunk = unit
        elif len(current_chunk) + len(unit) + 2 <= chunk_size:
            current_chunk += "\n\n" + unit
        else:
            chunks.append(_make_chunk(
                current_chunk.strip(), document_name, section, chunk_idx
            ))
            chunk_idx += 1
            if chunk_overlap > 0:
                overlap_text = current_chunk.strip()[-chunk_overlap:]
                current_chunk = overlap_text + "\n\n" + unit
                # Ensure overlap + unit does not exceed chunk_size
                if len(current_chunk) > chunk_size:
                    current_chunk = unit
            else:
                current_chunk = unit

    if current_chunk.strip():
        chunks.append(_make_chunk(
            current_chunk.strip(), document_name, section, chunk_idx
        ))

    return chunks


def _make_chunk(text: str, document: str, section: str, index: int) -> dict:
    """Create a chunk dict with metadata."""
    chunk_id = hashlib.md5(f"{document}:{section}:{index}:{text[:50]}".encode()).hexdigest()
    return {
        "id": f"{document}_{chunk_id}",
        "text": text,
        "metadata": {
            "document": document,
            "section": section,
            "chunk_index": index,
        },
    }


def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("AI Interview System — Knowledge Base Ingestion")
    print("=" * 60)

    # Configuration
    kb_dir = PROJECT_ROOT / "knowledge_base"
    chroma_dir = str(PROJECT_ROOT / "chroma_db")

    # Role-to-collection mapping
    role_dirs = {
        "ai_ml": "ai_ml",
        "backend": "backend",
        "data_science": "data_science",
    }

    # Import services
    from backend.app.services.embedding_service import generate_embeddings
    from backend.app.services.rag_service import ingest_documents, get_collection_count, reset_client

    reset_client()  # Ensure fresh client

    total_docs = 0
    total_chunks = 0
    total_embeddings = 0

    for dir_name, collection_name in role_dirs.items():
        role_dir = kb_dir / dir_name
        if not role_dir.exists():
            print(f"\n⚠  Directory not found: {role_dir}")
            continue

        print(f"\n{'─' * 40}")
        print(f"Processing: {dir_name} → collection '{collection_name}'")
        print(f"{'─' * 40}")

        # Find all supported files
        files = []
        for ext in ("*.pdf", "*.md", "*.txt"):
            files.extend(role_dir.glob(ext))

        if not files:
            print(f"  No documents found in {role_dir}")
            continue

        all_chunks = []
        for file_path in sorted(files):
            print(f"\n  📄 {file_path.name}")
            try:
                if file_path.suffix.lower() == ".pdf":
                    text = extract_text_from_pdf(file_path)
                else:
                    text = extract_text_from_markdown(file_path)

                text = clean_text(text)
                if not text:
                    print(f"    ⚠  No text extracted")
                    continue

                print(f"    Characters: {len(text):,}")

                # Chunk the text
                chunks = section_aware_chunking(
                    text,
                    chunk_size=500,
                    chunk_overlap=50,
                    document_name=file_path.stem,
                )
                print(f"    Chunks: {len(chunks)}")
                all_chunks.extend(chunks)
                total_docs += 1

            except Exception as e:
                print(f"    ❌ Error: {e}")

        if not all_chunks:
            print(f"  No chunks generated for {dir_name}")
            continue

        # Add role to metadata
        for chunk in all_chunks:
            chunk["metadata"]["role"] = collection_name

        # Generate embeddings
        print(f"\n  🔢 Generating embeddings for {len(all_chunks)} chunks...")
        start_time = time.time()

        chunk_texts = [c["text"] for c in all_chunks]
        embeddings = generate_embeddings(chunk_texts)

        embed_time = time.time() - start_time
        print(f"    Embeddings generated in {embed_time:.1f}s")
        total_embeddings += len(embeddings)

        # Ingest into ChromaDB
        print(f"  💾 Ingesting into ChromaDB collection '{collection_name}'...")
        chunk_ids = [c["id"] for c in all_chunks]
        metadatas = [c["metadata"] for c in all_chunks]

        ingested = ingest_documents(
            collection_name=collection_name,
            chunks=chunk_texts,
            metadatas=metadatas,
            ids=chunk_ids,
            embeddings=embeddings,
            persist_directory=chroma_dir,
        )
        total_chunks += ingested

        # Verify
        count = get_collection_count(collection_name, chroma_dir)
        print(f"  ✅ Collection '{collection_name}': {count} documents stored")

    # Summary
    print(f"\n{'=' * 60}")
    print("INGESTION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Documents processed: {total_docs}")
    print(f"  Chunks created:      {total_chunks:,}")
    print(f"  Embeddings generated: {total_embeddings:,}")
    print(f"  ChromaDB directory:  {chroma_dir}")
    print(f"  Status:              {'SUCCESS' if total_chunks > 0 else 'NO DATA'}")
    print(f"{'=' * 60}")

    if total_chunks == 0:
        print("\n⚠  No documents were ingested. Add documents to knowledge_base/ directories.")
        sys.exit(1)


if __name__ == "__main__":
    main()
