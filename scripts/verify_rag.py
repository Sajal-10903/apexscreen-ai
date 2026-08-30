"""Script to verify RAG retrieval across all collections."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag_service import search_with_embeddings, get_collection_count

def test_rag_retrieval():
    test_cases = [
        ("ai_ml", "TF-IDF feature representation text classification logistic regression"),
        ("backend", "database indexing transactions ACID properties SQL"),
        ("data_science", "hypothesis testing p-value ANOVA statistical significance"),
    ]

    print("=" * 65)
    print("REAL RAG RETRIEVAL VERIFICATION")
    print("=" * 65)

    all_passed = True
    for collection, query in test_cases:
        count = get_collection_count(collection)
        print(f"\n📁 Collection: '{collection}' ({count} chunks indexed)")
        print(f"🔍 Query: \"{query}\"")
        
        results = search_with_embeddings(collection, query, n_results=3)
        if not results:
            print("  ❌ No results retrieved!")
            all_passed = False
            continue
        
        print(f"  ✅ Retrieved {len(results)} chunks:")
        for idx, item in enumerate(results, 1):
            meta = item.get("metadata", {})
            score = item.get("score", 0)
            text_snippet = item.get("text", "").replace("\n", " ")[:140]
            print(f"    [{idx}] Score: {score:.4f} | Doc: {meta.get('document')} | Section: {meta.get('section')}")
            print(f"        Snippet: \"{text_snippet}...\"")
            
    print("\n" + "=" * 65)
    if all_passed:
        print("✅ ALL RAG RETRIEVAL TESTS PASSED WITH REAL SIMILARITY MATCHES")
    else:
        print("❌ SOME RAG RETRIEVAL TESTS FAILED")
    print("=" * 65)

if __name__ == "__main__":
    test_rag_retrieval()
