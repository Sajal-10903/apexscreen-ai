"""Dynamic question generation using single-source resume grounding + role curriculum + RAG context."""

import json
import logging
import re
import uuid

from backend.app.core.prompts import query_generation_prompt, question_generation_prompt
from backend.app.services.llm_service import LLMService
from backend.app.services.rag_service import search_with_embeddings, collection_exists_and_populated
from backend.app.services.role_config import (
    get_role_config, get_difficulty_for_stage, get_topic_for_stage, get_provenance_for_stage,
)

logger = logging.getLogger(__name__)


def generate_question(
    candidate_profile: dict,
    role_id: str,
    question_index: int,
    total_questions: int,
    previous_qa: list[dict] | None = None,
    avg_score: float | None = None,
) -> dict:
    """Generate a personalized interview question using single-source grounding and RAG.

    Flow:
    1. Determine isolated resume provenance, specific topic, and difficulty based on stage + performance
    2. Retrieve targeted knowledge base context for that specific topic
    3. Generate personalized question grounded strictly in that single source item
    4. Provide full provenance and traceability metadata

    Returns a dict with question details and traceability metadata.
    """
    role_config = get_role_config(role_id)
    if not role_config:
        raise ValueError(f"Unknown role: {role_id}")

    # ── Step 1: Determine topic, difficulty, and isolated provenance ──
    covered_topics = [qa.get("topic", "") for qa in (previous_qa or [])]
    difficulty = get_difficulty_for_stage(
        role_id, question_index, total_questions, avg_score
    )
    topic = get_topic_for_stage(
        role_id, question_index, total_questions, covered_topics, difficulty
    )
    prov = get_provenance_for_stage(
        stage=question_index,
        total=total_questions,
        candidate_profile=candidate_profile,
        previous_qa=previous_qa,
        topic=topic,
    )
    section = prov["section"]
    source_type = prov["source_type"]
    resume_section = prov["resume_section"]
    source_item = prov["source_item"]
    source_signals = prov["source_signals"]

    logger.info(f"Generating Q{question_index + 1}: provenance={source_type} ('{source_item}'), section='{section}', topic='{topic}', difficulty='{difficulty}'")

    # ── Step 2: Targeted RAG Retrieval ──
    collection_name = role_config["collection"]
    retrieved_chunks = []
    retrieved_context = ""

    # Build targeted search query using specific topic + source signals
    signals_str = " ".join(source_signals[:3]) if source_signals else ""
    target_query = f"{topic} {signals_str}".strip()

    retrieval_queries = [
        f"{topic} core algorithms and architecture",
        f"{topic} {signals_str} implementation trade-offs",
        f"{topic} validation and failure modes",
    ]

    if collection_exists_and_populated(collection_name):
        try:
            # Query for the specific technical topic
            results = search_with_embeddings(
                collection_name=collection_name,
                query_text=target_query,
                n_results=3,
            )
            retrieved_chunks.extend(results)
        except Exception as e:
            logger.warning(f"RAG search failed for '{target_query}': {e}")

        # If needed, try the primary topic directly
        if len(retrieved_chunks) < 2:
            try:
                results = search_with_embeddings(
                    collection_name=collection_name,
                    query_text=topic,
                    n_results=3,
                )
                retrieved_chunks.extend(results)
            except Exception as e:
                logger.warning(f"RAG search failed for '{topic}': {e}")

        # Deduplicate
        seen_texts = set()
        unique_chunks = []
        for chunk in sorted(retrieved_chunks, key=lambda x: x.get("score", 0), reverse=True):
            text = chunk.get("text", "")[:180]
            if text not in seen_texts:
                seen_texts.add(text)
                unique_chunks.append(chunk)
        retrieved_chunks = unique_chunks[:3]

        retrieved_context = "\n\n---\n\n".join(
            chunk.get("text", "") for chunk in retrieved_chunks
        )
    else:
        retrieved_context = f"[Knowledge base reference on {topic}]"

    # ── Step 3: Generate Question via LLM ──
    llm = LLMService.get_provider()
    candidate_skills = candidate_profile.get("skills", []) or candidate_profile.get("programming_languages", [])
    candidate_projects = candidate_profile.get("projects", [])
    candidate_education = candidate_profile.get("education", [])
    candidate_certs = candidate_profile.get("certifications", [])
    candidate_exp = candidate_profile.get("experience", []) or candidate_profile.get("experience_years", 0)

    gen_prompt = question_generation_prompt(
        candidate_skills=candidate_skills,
        candidate_projects=candidate_projects,
        role=role_config["name"],
        topic=topic,
        difficulty=difficulty,
        retrieved_context=retrieved_context,
        interview_stage=question_index + 1,
        total_questions=total_questions,
        section=section,
        candidate_education=candidate_education,
        candidate_certifications=candidate_certs,
        candidate_experience=candidate_exp,
        previous_qa=previous_qa,
        source_type=source_type,
        resume_section=resume_section,
        source_item=source_item,
        source_signals=source_signals,
    )

    try:
        question_response = llm.generate(gen_prompt, temperature=0.6)
        question_data = _parse_json(question_response)
    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        question_data = None

    # ── Step 4: Assemble Structured Result with Provenance ──
    if question_data and "question" in question_data:
        result = {
            "id": str(uuid.uuid4()),
            "question_text": question_data["question"],
            "topic": question_data.get("topic", topic),
            "subtopic": question_data.get("subtopic", f"{topic} Deep Dive"),
            "section": section,
            "source_type": source_type,
            "resume_section": resume_section,
            "source_item": source_item,
            "source_signals": source_signals,
            "difficulty": question_data.get("difficulty", difficulty),
            "question_type": question_data.get("question_type", "project-based" if source_type == "resume_project" else "conceptual"),
            "expected_concepts": question_data.get("expected_concepts", [topic, "Practical trade-offs", "Validation"]),
        }
    else:
        # Fallback question grounded strictly in this source
        q_text, exp_concepts = _fallback_grounded_question(
            source_type=source_type,
            source_item=source_item,
            source_signals=source_signals,
            topic=topic,
            difficulty=difficulty,
            role_name=role_config["name"]
        )
        result = {
            "id": str(uuid.uuid4()),
            "question_text": q_text,
            "topic": topic,
            "subtopic": f"{topic} Foundations",
            "section": section,
            "source_type": source_type,
            "resume_section": resume_section,
            "source_item": source_item,
            "source_signals": source_signals,
            "difficulty": difficulty,
            "question_type": "project-based" if source_type == "resume_project" else "conceptual",
            "expected_concepts": exp_concepts,
        }

    # Traceability
    result["traceability"] = {
        "source_type": source_type,
        "resume_section": resume_section,
        "source_item": source_item,
        "source_signals": source_signals,
        "grounding_summary": f"Resume → {resume_section} → {source_item}",
        "retrieval_queries": retrieval_queries,
        "retrieved_chunks": [
            {
                "document": chunk.get("metadata", {}).get("document", role_config["collection"]),
                "section": chunk.get("metadata", {}).get("section", topic),
                "score": round(chunk.get("score", 0.8), 3),
                "text_preview": chunk.get("text", "")[:140] + "...",
            }
            for chunk in retrieved_chunks[:3]
        ],
        "generation_context": (
            f"Source: Resume → {resume_section} ({source_item}). Signals: {', '.join(source_signals)}. "
            f"Role: {role_config['name']}. Topic: {topic}. Difficulty: {difficulty}."
        ),
        "section": section,
        "resume_signals": source_signals,
        "role": role_config["name"],
    }

    return result


def _parse_json(text: str) -> dict | None:
    """Extract and parse JSON from LLM response."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _fallback_grounded_question(
    source_type: str,
    source_item: str,
    source_signals: list[str],
    topic: str,
    difficulty: str,
    role_name: str
) -> tuple[str, list[str]]:
    """Generate a clean, professional, single-source question without generic templates."""
    signals_text = ", ".join(source_signals) if source_signals else "your technical stack"

    if source_type == "resume_project":
        q = (
            f"Your resume mentions the '{source_item}' project utilizing {signals_text}. "
            f"Focusing on {topic}, why did you choose this specific architectural approach, "
            f"and how did you evaluate whether the solution generalizes effectively in production?"
        )
        concepts = [
            f"{topic} core principles in {source_item}",
            "Architectural rationale and alternative approaches",
            "Generalization and validation methodology",
            "Production trade-offs and edge cases"
        ]
    elif source_type == "resume_education":
        q = (
            f"Drawing on your academic background in {source_item}, explain the fundamental theoretical principles "
            f"underlying {topic}. Walk through the core mathematical assumptions, loss functions, or design constraints "
            f"that an engineer must validate."
        )
        concepts = [
            f"{topic} theoretical foundation",
            "Mathematical formulation and assumptions",
            "Loss functions and optimization mechanics",
            "Validation and verification methods"
        ]
    elif source_type == "resume_skill":
        q = (
            f"Your resume highlights hands-on experience with {source_item}. "
            f"When implementing systems involving {topic}, what are the key performance trade-offs, "
            f"concurrency constraints, or failure modes you must design around?"
        )
        concepts = [
            f"{source_item} implementation specifics",
            f"{topic} performance and latency trade-offs",
            "Concurrency, scaling, or memory bottlenecks",
            "Resilience and fault tolerance"
        ]
    elif source_type == "resume_experience":
        q = (
            f"Drawing on your experience at {source_item}, how do you ensure high reliability and low latency "
            f"when deploying {topic} into production? Discuss your monitoring, rollback, and data integrity strategies."
        )
        concepts = [
            "Production scaling and deployment architecture",
            f"{topic} reliability and throughput guarantees",
            "Monitoring, telemetry, and error handling",
            "Data consistency and migration strategies"
        ]
    else:  # General Technical
        q = (
            f"In a modern distributed architecture, how would you design a component for {topic}? "
            f"Explain the internal data structures, consistency guarantees, and how you prevent common bottlenecks."
        )
        concepts = [
            f"{topic} system architecture",
            "Data structures and algorithmic complexity",
            "Consistency vs availability trade-offs",
            "Bottleneck diagnosis and mitigation"
        ]

    return q, concepts
