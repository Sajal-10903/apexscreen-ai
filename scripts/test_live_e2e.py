"""Live End-to-End API Workflow Verification Script with Real LLM (Gemini/OpenAI/Mock)."""

import sys
import httpx
from pathlib import Path

BASE = "http://127.0.0.1:8000/api"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def formulate_relevant_answer(q: dict) -> str:
    """Generate a comprehensive, technically thorough answer covering all core ML engineering dimensions."""
    topic = q.get("topic", "Machine Learning")

    return (
        f"In approaching {topic}, I design and execute an end-to-end production machine learning pipeline:\n\n"
        "1. Loss Function Selection & Mathematical Optimization: For classification tasks, we choose Cross-Entropy "
        "or Focal Loss to penalize confident misclassifications and handle class imbalance. For regression, we utilize "
        "Huber loss to maintain robustness against outliers. We optimize using AdamW with weight decay, cosine annealing "
        "learning rate schedules, and linear warmup.\n\n"
        "2. Feature Pipeline & Statistical Validation: We construct reproducible preprocessing pipelines using Scikit-Learn "
        "and PyTorch DataLoaders with automated feature scaling and encoding. To prevent target leakage and overfitting, "
        "we validate models using stratified K-Fold cross-validation and out-of-time splits. In production, we continuously "
        "monitor feature distributions for covariate shift and data drift using Population Stability Index (PSI).\n\n"
        "3. System Architecture & Latency-Throughput Trade-offs: We package inference pipelines in Docker containers deployed "
        "on AWS EC2 with FastAPI and ONNX Runtime / Triton Inference Server. We balance throughput vs latency by applying "
        "dynamic batching, FP16 quantization, and asynchronous non-blocking worker pools to achieve <25ms P99 latency while "
        "scaling to high concurrent query volumes."
    )


def run_live_e2e():
    print("=" * 70)
    print("LIVE END-TO-END SYSTEM VERIFICATION (PROVENANCE, RAG, RETRY, EARLY-FINISH, ANALYTICS)")
    print("=" * 70)

    client = httpx.Client(timeout=90.0)

    # 1. Health
    r = client.get(f"{BASE}/health")
    assert r.status_code == 200
    health = r.json()
    print(f"\n1. Health Check: {health['status'].upper()}")
    print(f"   Database: {health['database']} | ChromaDB: {health['vector_db']} | KB Indexed: {health['knowledge_base_indexed']}")
    print(f"   LLM Mode: {health['llm_mode']}")
    print(f"   LLM Available: {health['llm_available']}")

    # 2. Roles
    r = client.get(f"{BASE}/roles")
    assert r.status_code == 200
    roles = r.json()["roles"]
    print(f"\n2. Roles Available ({len(roles)}): {[r['name'] for r in roles]}")

    # 3. Upload Resume
    pdf_path = PROJECT_ROOT / "data" / "sample_resume.pdf"
    with open(pdf_path, "rb") as f:
        r = client.post(f"{BASE}/resume/upload", files={"file": ("sample_resume.pdf", f, "application/pdf")})
    assert r.status_code == 200, r.text
    cand = r.json()
    candidate_id = cand["candidate_id"]
    print(f"\n3. Resume Uploaded & Analyzed by LLM:")
    print(f"   Candidate: {cand['name']} (ID: {candidate_id[:8]}...)")
    print(f"   Extracted Skills ({len(cand['skills'])}): {cand['skills'][:8]}")
    print(f"   AI/ML Technologies: {cand['ai_ml_technologies']}")
    print(f"   Projects Detected ({len(cand['projects'])}): {[p['name'] for p in cand['projects']]}")

    # 4. Create Interview Session
    r = client.post(f"{BASE}/interviews", json={"candidate_id": candidate_id, "role": "ai_ml_engineer"})
    assert r.status_code == 200, r.text
    session_data = r.json()
    session_id = session_data["session_id"]
    print(f"\n4. Interview Session Created:")
    print(f"   Session ID: {session_id}")
    print(f"   Role: {session_data['role']}")
    print(f"   Total Questions: {session_data['total_questions']}")
    print(f"   Mock Mode: {session_data['is_mock_mode']}")

    # 5. Fetch First Question & Verify Provenance
    r = client.get(f"{BASE}/interviews/{session_id}/current-question")
    assert r.status_code == 200, r.text
    q1 = r.json()
    assert "section" in q1, "Question missing 'section' attribute"
    assert "source_type" in q1, "Question missing 'source_type' attribute"
    assert "resume_section" in q1, "Question missing 'resume_section' attribute"
    print(f"\n5. Question 1 Provenance & Grounding (Q{q1['question_index'] + 1}/{q1['total_questions']}):")
    print(f"   Provenance: Resume → {q1['resume_section']} → {q1['source_item']}")
    print(f"   Source Type: {q1['source_type']} | Grounded Signals: {q1.get('source_signals', [])}")
    print(f"   Section: {q1['section']} | Topic: {q1['topic']} | Difficulty: {q1['difficulty']}")
    print(f"   Question: {q1['question_text']}")
    trace = q1.get("traceability", {})
    print(f"   Retrieved KB Sources: {len(trace.get('retrieved_chunks', []))} chunks")

    # 6. Submit Initial Answer for Q1
    weak_answer = "Machine learning models learn patterns from training data."
    r = client.post(f"{BASE}/interviews/{session_id}/answers", json={"answer_text": weak_answer})
    assert r.status_code == 200, r.text
    eval1 = r.json()
    print(f"\n6. Initial Answer Evaluation for Q1 (Score: {eval1['score']}/10)")
    print(f"   Feedback: {eval1['feedback'][:120]}...")

    # 7. Test Retry Flow on Q1
    r = client.post(f"{BASE}/interviews/{session_id}/retry")
    assert r.status_code == 200, r.text
    q1_retried = r.json()
    assert q1_retried["question_id"] == q1["question_id"]
    print(f"\n7. Retry Triggered for Q1 (Same Question ID preserved: {q1_retried['question_id'][:8]}...)")

    # Re-submit comprehensive answer on retry
    strong_answer = formulate_relevant_answer(q1)
    r = client.post(f"{BASE}/interviews/{session_id}/answers", json={"answer_text": strong_answer, "is_retry": True})
    assert r.status_code == 200, r.text
    eval1_improved = r.json()
    print(f"   Re-evaluated Answer Score: {eval1_improved['score']}/10 (Technical: {eval1_improved['technical_accuracy']}/10)")
    assert eval1_improved['score'] > eval1['score'], "Improved answer must achieve higher score on retry"

    # 8. Generate Next Question (Q2) & Verify Project-based Provenance
    r = client.post(f"{BASE}/interviews/{session_id}/next-question")
    assert r.status_code == 200, r.text
    q2 = r.json()
    print(f"\n8. Question 2 Provenance & Grounding (Q{q2['question_index'] + 1}/{q2['total_questions']}):")
    print(f"   Provenance: Resume → {q2['resume_section']} → {q2['source_item']}")
    print(f"   Source Type: {q2['source_type']} | Grounded Signals: {q2.get('source_signals', [])}")
    print(f"   Section: {q2['section']} | Topic: {q2['topic']} | Difficulty: {q2['difficulty']}")
    print(f"   Question: {q2['question_text']}")

    # Submit Q2 answer
    r = client.post(f"{BASE}/interviews/{session_id}/answers", json={"answer_text": formulate_relevant_answer(q2)})
    assert r.status_code == 200, r.text

    # 9. Test Early Finish Feature and Verify Analytics
    r = client.post(f"{BASE}/interviews/{session_id}/finish")
    assert r.status_code == 200, r.text
    finish_results = r.json()
    print(f"\n9. Early Finish Triggered & Final Results Generated:")
    print(f"   Completed Early: {finish_results['is_completed_early']}")
    print(f"   Questions Answered: {finish_results['questions_answered']} / {finish_results['total_questions']}")
    print(f"   Overall Score: {finish_results['overall_score']}/10")
    print(f"   Technical Score: {finish_results['technical_score']}/10")
    print(f"   Hiring Recommendation: {finish_results['hiring_recommendation']}")
    print(f"   Score Progression: {len(finish_results.get('score_progression', []))} data points")
    print(f"   Category Scores: {finish_results.get('category_scores', {})}")
    print(f"   Coverage Summary: {list(finish_results.get('coverage_summary', {}).keys())[:4]}...")

    assert finish_results["is_completed_early"] is True
    assert finish_results["questions_answered"] == 2
    assert "coverage_summary" in finish_results
    assert len(finish_results["score_progression"]) == 2

    print("\n" + "=" * 70)
    print("✅ FULL RESUME TRACEABILITY, PROVENANCE, RETRY, EARLY-FINISH & ANALYTICS VERIFIED")
    print("=" * 70)


if __name__ == "__main__":
    run_live_e2e()
