"""Interview results API."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.interview import InterviewSession, Question, Answer
from backend.app.models.candidate import Candidate
from backend.app.models.schemas import InterviewResultsResponse, QuestionResultDetail
from backend.app.services.interview_service import generate_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["Results"])


@router.get("/{session_id}/results", response_model=InterviewResultsResponse)
def get_interview_results(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Get comprehensive interview results and report."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()
    candidate_name = candidate.name if candidate else "Unknown"

    # Generate or retrieve report
    try:
        report = generate_report(db, session_id)
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        report = None

    # Build per-question details
    questions = (
        db.query(Question)
        .filter(Question.session_id == session_id)
        .order_by(Question.question_index)
        .all()
    )

    question_details = []
    score_progression = []
    category_scores = {}
    difficulty_scores = {}

    for q in questions:
        answer = db.query(Answer).filter(Answer.question_id == q.id).first()
        detail = QuestionResultDetail(
            question_index=q.question_index,
            question_text=q.question_text,
            topic=q.topic,
            difficulty=q.difficulty,
            question_type=q.question_type,
            section=q.section or "Technical Concepts",
            source_type=q.source_type or "general_rag",
            resume_section=q.resume_section or q.section or "General Technical",
            source_item=q.source_item or "",
            source_signals=q.source_signals,
            answer_text=answer.answer_text if answer else "",
            score=answer.score if answer else 0,
            technical_accuracy=answer.technical_accuracy if answer else 0,
            completeness=answer.completeness if answer else 0,
            feedback=answer.feedback if answer else "",
            strengths=answer.strengths if answer else [],
            missing_concepts=answer.missing_concepts if answer else [],
            traceability=q.traceability_dict(),
        )
        question_details.append(detail)
        if answer:
            score_progression.append({
                "question_index": q.question_index + 1,
                "topic": q.topic,
                "section": q.section or "Technical Concepts",
                "score": answer.score,
                "technical_accuracy": answer.technical_accuracy,
                "completeness": answer.completeness,
                "reasoning_depth": answer.reasoning_depth,
                "communication": answer.communication,
            })
            sec = q.section or "Technical Concepts"
            category_scores.setdefault(sec, []).append(answer.score)
            difficulty_scores.setdefault(q.difficulty, []).append(answer.score)

    questions_attempted = sum(1 for q in question_details if q.answer_text)
    cat_avg_scores = {k: round(sum(v) / len(v), 1) for k, v in category_scores.items()}
    diff_avg_scores = {k: round(sum(v) / len(v), 1) for k, v in difficulty_scores.items()}

    return InterviewResultsResponse(
        session_id=session.id,
        candidate_name=candidate_name,
        role=session.role,
        status=session.status,
        is_mock_mode=bool(session.is_mock_mode),
        is_completed_early=bool(session.is_completed_early),
        overall_score=report.overall_score if report else 0,
        technical_score=report.technical_score if report else 0,
        communication_score=report.communication_score if report else 0,
        overall_assessment=report.overall_assessment if report else "",
        technical_proficiency=report.technical_proficiency if report else "",
        strong_areas=report.strong_areas if report else [],
        weak_areas=report.weak_areas if report else [],
        recommendations=report.recommendations if report else [],
        topics_covered=report.topics_covered if report else [],
        hiring_recommendation=report.hiring_recommendation if report else "",
        confidence_level=report.confidence_level if report else "",
        interview_quality_note=report.interview_quality_note if report else "",
        coverage_summary=report.coverage_summary if report else {},
        category_scores=cat_avg_scores,
        difficulty_scores=diff_avg_scores,
        score_progression=score_progression,
        questions=question_details,
        questions_attempted=questions_attempted,
        questions_answered=questions_attempted,
        total_questions=session.total_questions,
        start_time=session.start_time.isoformat() if session.start_time else None,
        end_time=session.end_time.isoformat() if session.end_time else None,
    )
