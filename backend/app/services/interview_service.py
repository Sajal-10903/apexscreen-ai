"""Interview service managing the full interview lifecycle."""

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.core.prompts import interview_summary_prompt
from backend.app.models.candidate import Candidate
from backend.app.models.interview import InterviewSession, Question, Answer, InterviewReport
from backend.app.services.answer_evaluator import evaluate_answer
from backend.app.services.llm_service import LLMService
from backend.app.services.question_generator import generate_question
from backend.app.services.role_config import get_role_config

logger = logging.getLogger(__name__)


def create_interview_session(
    db: Session,
    candidate_id: str,
    role: str,
    total_questions: int = 8,
) -> InterviewSession:
    """Create a new interview session and generate the first question."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise ValueError(f"Candidate not found: {candidate_id}")

    role_config = get_role_config(role)
    if not role_config:
        raise ValueError(f"Invalid role: {role}")

    # Check LLM provider availability
    llm = LLMService.get_provider()
    is_mock = not hasattr(llm, '_api_key') or llm.provider_name == "Mock/Demo Provider"

    session = InterviewSession(
        id=str(uuid.uuid4()),
        candidate_id=candidate_id,
        role=role,
        status="in_progress",
        current_question_index=0,
        total_questions=total_questions,
        start_time=datetime.now(timezone.utc),
        is_mock_mode=1 if is_mock else 0,
        is_completed_early=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate first question
    _generate_and_store_question(db, session, candidate)

    return session


def get_current_question(db: Session, session_id: str) -> Question | None:
    """Get the active question for a session."""
    session = _get_session(db, session_id)

    # Find the question corresponding to current_question_index
    question = (
        db.query(Question)
        .filter(
            Question.session_id == session_id,
            Question.question_index == session.current_question_index,
        )
        .first()
    )
    if not question:
        # Fallback to highest index question
        question = (
            db.query(Question)
            .filter(Question.session_id == session_id)
            .order_by(Question.question_index.desc())
            .first()
        )
    return question


def submit_answer(
    db: Session,
    session_id: str,
    answer_text: str,
    is_retry: bool = False,
) -> dict:
    """Submit or re-submit an answer for the current question and evaluate it.

    Returns evaluation results and whether there's a next question.
    """
    session = _get_session(db, session_id)

    if session.status == "completed":
        raise ValueError("Interview is already completed")

    # Get current question
    current_question = get_current_question(db, session_id)
    if not current_question:
        raise ValueError("No current question found")

    # Check for existing answer
    existing_answer = (
        db.query(Answer)
        .filter(Answer.question_id == current_question.id)
        .first()
    )
    if existing_answer and not is_retry:
        raise ValueError("Answer already submitted for this question. Use retry to re-submit.")

    # Get retrieved context for evaluation
    retrieved_context = ""
    if current_question.retrieved_chunks:
        chunks = current_question.retrieved_chunks
        retrieved_context = "\n".join(c.get("text", "") for c in chunks[:3])

    # Evaluate the answer
    evaluation = evaluate_answer(
        question_text=current_question.question_text,
        answer_text=answer_text,
        expected_concepts=current_question.expected_concepts,
        retrieved_context=retrieved_context,
        difficulty=current_question.difficulty,
    )

    if existing_answer:
        # Update existing answer in place for retry
        existing_answer.answer_text = answer_text
        existing_answer.score = evaluation["score"]
        existing_answer.technical_accuracy = evaluation["technical_accuracy"]
        existing_answer.completeness = evaluation["completeness"]
        existing_answer.reasoning_depth = evaluation["reasoning_depth"]
        existing_answer.communication = evaluation["communication"]
        existing_answer.feedback = evaluation["feedback"]
        existing_answer.suggestions = evaluation.get("suggestions", "")
        existing_answer.strengths = evaluation.get("strengths", [])
        existing_answer.missing_concepts = evaluation.get("missing_concepts", [])
        answer = existing_answer
    else:
        # Store new answer
        answer = Answer(
            id=str(uuid.uuid4()),
            question_id=current_question.id,
            session_id=session_id,
            answer_text=answer_text,
            score=evaluation["score"],
            technical_accuracy=evaluation["technical_accuracy"],
            completeness=evaluation["completeness"],
            reasoning_depth=evaluation["reasoning_depth"],
            communication=evaluation["communication"],
            feedback=evaluation["feedback"],
            suggestions=evaluation.get("suggestions", ""),
        )
        answer.strengths = evaluation.get("strengths", [])
        answer.missing_concepts = evaluation.get("missing_concepts", [])
        db.add(answer)

    # Check if there are more questions
    has_next = (current_question.question_index + 1) < session.total_questions

    if not has_next:
        session.status = "completed"
        session.end_time = datetime.now(timezone.utc)

    db.commit()

    return {
        "answer_id": answer.id,
        "evaluation": evaluation,
        "has_next_question": has_next,
        "is_retry": bool(existing_answer),
    }


def retry_question(db: Session, session_id: str) -> Question:
    """Reset the current question's answer to allow candidate to improve and re-submit."""
    session = _get_session(db, session_id)
    if session.status == "completed":
        # Allow retry even if marked complete on the last question, reopening the session
        session.status = "in_progress"
        session.end_time = None

    current_question = get_current_question(db, session_id)
    if not current_question:
        raise ValueError("No active question found to retry")

    # Remove the existing answer so candidate can submit a fresh attempt
    existing_answer = (
        db.query(Answer)
        .filter(Answer.question_id == current_question.id)
        .first()
    )
    if existing_answer:
        db.delete(existing_answer)
        db.commit()

    return current_question


def generate_next_question(db: Session, session_id: str) -> Question | None:
    """Generate the next question in the interview sequence."""
    session = _get_session(db, session_id)
    candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()

    if session.status == "completed":
        return None

    # Check if current question has an answer
    current_q = get_current_question(db, session_id)
    if current_q:
        answer = db.query(Answer).filter(Answer.question_id == current_q.id).first()
        if not answer:
            # Current question not yet answered, return it
            return current_q
        else:
            # Advance to next index
            next_idx = current_q.question_index + 1
            if next_idx >= session.total_questions:
                session.status = "completed"
                session.end_time = datetime.now(timezone.utc)
                db.commit()
                return None
            session.current_question_index = next_idx
            db.commit()

    # Check if question already exists for this index
    existing = (
        db.query(Question)
        .filter(
            Question.session_id == session_id,
            Question.question_index == session.current_question_index,
        )
        .first()
    )
    if existing:
        return existing

    return _generate_and_store_question(db, session, candidate)


def finish_interview(db: Session, session_id: str) -> InterviewReport:
    """End the interview at any time and generate final report on completed evidence."""
    session = _get_session(db, session_id)
    session.status = "completed"
    session.end_time = datetime.now(timezone.utc)

    # Check how many questions were answered
    answered_count = db.query(Answer).filter(Answer.session_id == session_id).count()
    if answered_count < session.total_questions:
        session.is_completed_early = 1

    db.commit()

    return generate_report(db, session_id)


def generate_report(db: Session, session_id: str) -> InterviewReport:
    """Generate the final interview report strictly from completed answers."""
    session = _get_session(db, session_id)

    # Check if report already exists
    existing_report = db.query(InterviewReport).filter(
        InterviewReport.session_id == session_id
    ).first()
    if existing_report:
        return existing_report

    candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()

    # Gather all Q&A data where answers were provided
    questions = (
        db.query(Question)
        .filter(Question.session_id == session_id)
        .order_by(Question.question_index)
        .all()
    )

    qa_data = []
    total_score = 0
    total_tech = 0
    total_comm = 0
    answered = 0

    for q in questions:
        answer = db.query(Answer).filter(Answer.question_id == q.id).first()
        if answer:
            qa_entry = {
                "question": q.question_text,
                "topic": q.topic,
                "section": q.section or "Technical Concepts",
                "difficulty": q.difficulty,
                "score": answer.score,
                "technical_accuracy": answer.technical_accuracy,
                "communication": answer.communication,
                "reasoning_depth": answer.reasoning_depth,
                "completeness": answer.completeness,
            }
            qa_data.append(qa_entry)
            total_score += answer.score
            total_tech += answer.technical_accuracy
            total_comm += answer.communication
            answered += 1

    is_early = answered < session.total_questions or bool(session.is_completed_early)

    # Calculate averages
    avg_score = total_score / max(answered, 1)
    avg_tech = total_tech / max(answered, 1)
    avg_comm = total_comm / max(answered, 1)

    overall_scores = {
        "average_score": round(avg_score, 1),
        "average_technical": round(avg_tech, 1),
        "average_communication": round(avg_comm, 1),
        "questions_answered": answered,
        "total_questions": session.total_questions,
        "is_completed_early": is_early,
    }

    # Generate summary using LLM
    llm = LLMService.get_provider()
    summary_prompt = interview_summary_prompt(
        role=session.role,
        candidate_name=candidate.name if candidate else "Candidate",
        questions_and_answers=qa_data,
        overall_scores=overall_scores,
        is_completed_early=is_early,
    )

    summary_data = {}
    try:
        response = llm.generate(summary_prompt, temperature=0.3)
        import re
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            summary_data = json.loads(match.group())
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")

    # Build report
    topics_covered = list(set(q.topic for q in questions if db.query(Answer).filter(Answer.question_id == q.id).first()))
    if not topics_covered:
        topics_covered = list(set(q.topic for q in questions))

    # Compute detailed coverage summary across curriculum tracks
    all_categories = [
        "Introduction / Background",
        "Education",
        "Projects",
        "Skills",
        "Work Experience",
        "Certifications",
        "Technical Concepts",
        "General Technical",
        "Follow-up / Performance Based",
    ]
    coverage_summary = {}
    for cat in all_categories:
        matched_q = [
            q for q in questions
            if (q.section == cat or q.resume_section == cat) and db.query(Answer).filter(Answer.question_id == q.id).first()
        ]
        is_covered = len(matched_q) > 0
        cat_avg = None
        if is_covered:
            scores = [db.query(Answer).filter(Answer.question_id == q.id).first().score for q in matched_q]
            cat_avg = round(sum(scores) / len(scores), 1)

        coverage_summary[cat] = {
            "status": "covered" if is_covered else "uncovered",
            "count": len(matched_q),
            "average_score": cat_avg,
        }

    early_suffix = f" (Interview concluded early: {answered} of {session.total_questions} questions answered)" if is_early else ""
    default_assessment = (
        f"{candidate.name if candidate else 'Candidate'} completed {answered} of {session.total_questions} "
        f"technical interview questions with an overall score of {avg_score:.1f}/10.{early_suffix}"
    )

    report = InterviewReport(
        id=str(uuid.uuid4()),
        session_id=session_id,
        overall_score=round(avg_score, 1),
        technical_score=round(avg_tech, 1),
        communication_score=round(avg_comm, 1),
        overall_assessment=summary_data.get("overall_assessment", default_assessment),
        technical_proficiency=summary_data.get("technical_proficiency", f"Technical accuracy scored {avg_tech:.1f}/10 across answered questions."),
        hiring_recommendation=summary_data.get("hiring_recommendation", "maybe" if avg_score >= 5.0 else "no"),
        confidence_level=summary_data.get("confidence_level", "medium" if answered >= 3 else "low"),
        interview_quality_note=summary_data.get("interview_quality_note", f"Evaluated based on {answered} answered questions."),
        is_completed_early=1 if is_early else 0,
        questions_answered=answered,
    )
    report.strong_areas = summary_data.get("strong_areas", [])
    report.weak_areas = summary_data.get("weak_areas", [])
    report.recommendations = summary_data.get("recommendations", [])
    report.topics_covered = topics_covered
    report.coverage_summary = coverage_summary

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# ─── Private helpers ─────────────────────────────────────

def _get_session(db: Session, session_id: str) -> InterviewSession:
    """Get a session by ID or raise."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ValueError(f"Interview session not found: {session_id}")
    return session


def _generate_and_store_question(
    db: Session,
    session: InterviewSession,
    candidate: Candidate,
) -> Question:
    """Generate a question and persist it to the database with full provenance."""
    # Build candidate profile dict
    candidate_profile = candidate.to_dict()

    # Gather previous Q&A history
    previous_qa = []
    prev_questions = (
        db.query(Question)
        .filter(Question.session_id == session.id)
        .order_by(Question.question_index)
        .all()
    )
    for pq in prev_questions:
        pa = db.query(Answer).filter(Answer.question_id == pq.id).first()
        previous_qa.append({
            "question": pq.question_text,
            "topic": pq.topic,
            "section": pq.section or "Technical Concepts",
            "resume_section": pq.resume_section or pq.section or "General Technical",
            "source_type": pq.source_type or "general_rag",
            "source_item": pq.source_item or "",
            "difficulty": pq.difficulty,
            "score": pa.score if pa else None,
        })

    # Calculate average score for adaptive difficulty
    scores = [qa["score"] for qa in previous_qa if qa["score"] is not None]
    avg_score = sum(scores) / len(scores) if scores else None

    # Generate the question
    question_data = generate_question(
        candidate_profile=candidate_profile,
        role_id=session.role,
        question_index=session.current_question_index,
        total_questions=session.total_questions,
        previous_qa=previous_qa,
        avg_score=avg_score,
    )

    # Store in database
    question = Question(
        id=question_data["id"],
        session_id=session.id,
        question_index=session.current_question_index,
        question_text=question_data["question_text"],
        topic=question_data.get("topic", "General"),
        subtopic=question_data.get("subtopic", ""),
        section=question_data.get("section", "Technical Concepts"),
        source_type=question_data.get("source_type", "general_rag"),
        resume_section=question_data.get("resume_section", "General Technical"),
        source_item=question_data.get("source_item", ""),
        difficulty=question_data.get("difficulty", "intermediate"),
        question_type=question_data.get("question_type", "conceptual"),
        generation_context=question_data.get("traceability", {}).get("generation_context", ""),
    )
    question.source_signals = question_data.get("source_signals", [])
    question.expected_concepts = question_data.get("expected_concepts", [])
    question.retrieval_queries = question_data.get("traceability", {}).get("retrieval_queries", [])
    question.retrieved_chunks = question_data.get("traceability", {}).get("retrieved_chunks", [])

    db.add(question)
    db.commit()
    db.refresh(question)

    return question
