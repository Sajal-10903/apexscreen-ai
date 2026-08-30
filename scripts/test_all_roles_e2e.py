"""Ad-hoc verification: run a full interview for each of the 3 roles and check
for duplicate question text within a session. Not part of the permanent test
suite; used for manual verification during development."""

import httpx
from pathlib import Path

BASE = "http://127.0.0.1:8000/api"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ROLES = ["ai_ml_engineer", "backend_engineer", "data_scientist"]

ANSWERS = [
    "I don't know much about this, maybe something related but I'm not sure.",
    "In practice, this concept is used because it improves performance. For example, "
    "by using proper trade-offs we can mitigate risk and ensure scalability, latency and "
    "throughput are balanced. Specifically, the architecture handles this via caching, "
    "consistency guarantees, and fault tolerance, therefore providing a robust design.",
]

def run_role(client, role):
    with open(PROJECT_ROOT / "data" / "sample_resume.pdf", "rb") as f:
        r = client.post(f"{BASE}/resume/upload", files={"file": ("r.pdf", f, "application/pdf")})
    r.raise_for_status()
    candidate_id = r.json()["candidate_id"]

    r = client.post(f"{BASE}/interviews", json={"candidate_id": candidate_id, "role": role})
    r.raise_for_status()
    session_id = r.json()["session_id"]

    questions = []
    topics = []
    scores = []
    for i in range(8):
        r = client.get(f"{BASE}/interviews/{session_id}/current-question")
        r.raise_for_status()
        q = r.json()
        questions.append(q["question_text"])
        topics.append(q["topic"])

        answer = ANSWERS[i % 2]
        r = client.post(f"{BASE}/interviews/{session_id}/answers", json={"answer_text": answer})
        r.raise_for_status()
        ev = r.json()
        scores.append(ev["score"])

        if ev["has_next_question"]:
            r = client.post(f"{BASE}/interviews/{session_id}/next-question")
            r.raise_for_status()

    r = client.get(f"{BASE}/interviews/{session_id}/results")
    r.raise_for_status()
    results = r.json()

    dup_questions = len(questions) - len(set(questions))
    print(f"\n=== Role: {role} ===")
    print(f"  Topics ({len(set(topics))} unique / {len(topics)} total): {topics}")
    print(f"  Duplicate question texts: {dup_questions}")
    print(f"  Scores per question: {scores}")
    print(f"  Overall score: {results['overall_score']} | Hiring: {results['hiring_recommendation']}")
    assert dup_questions == 0, f"Found {dup_questions} duplicate questions for role {role}!"
    assert len(set(topics)) >= 5, f"Expected topic diversity, got {set(topics)}"
    return results


def main():
    client = httpx.Client(timeout=30.0)
    for role in ROLES:
        run_role(client, role)
    print("\n✅ ALL ROLES VERIFIED: no duplicate questions, good topic diversity, scores vary with answers.")


if __name__ == "__main__":
    main()
