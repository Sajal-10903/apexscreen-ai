"""Interview management API: create sessions, submit answers, get questions."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.rate_limit import check_rate_limit
from backend.app.models.database import get_db
from backend.app.models.schemas import (
    InterviewCreateRequest,
    InterviewCreateResponse,
    QuestionResponse,
    AnswerSubmitRequest,
    AnswerEvaluationResponse,
    InterviewStatusResponse,
    InterviewResultsResponse,
    QuestionResultDetail,
)
from backend.app.models.interview import Answer, Question
from backend.app.services.interview_service import (
    create_interview_session,
    get_current_question,
    submit_answer,
    generate_next_question,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["Interview"])


@router.post("", response_model=InterviewCreateResponse)
def create_interview(
    request: InterviewCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new interview session and generate the first question."""
    settings = get_settings()

    try:
        session = create_interview_session(
            db=db,
            candidate_id=request.candidate_id,
            role=request.role,
            total_questions=settings.interview_question_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Interview creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create interview session")

    return InterviewCreateResponse(
        session_id=session.id,
        role=session.role,
        total_questions=session.total_questions,
        status=session.status,
        is_mock_mode=bool(session.is_mock_mode),
        message="Interview created. First question is ready.",
    )


@router.get("/{session_id}", response_model=InterviewStatusResponse)
def get_interview_status(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Get the current status of an interview session."""
    from backend.app.models.interview import InterviewSession

    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    # Count answered questions
    answered_count = (
        db.query(Answer)
        .filter(Answer.session_id == session_id)
        .count()
    )

    return InterviewStatusResponse(
        session_id=session.id,
        candidate_id=session.candidate_id,
        role=session.role,
        status=session.status,
        current_question_index=session.current_question_index,
        total_questions=session.total_questions,
        start_time=session.start_time.isoformat() if session.start_time else None,
        end_time=session.end_time.isoformat() if session.end_time else None,
        is_mock_mode=bool(session.is_mock_mode),
        questions_answered=answered_count,
    )


@router.get("/{session_id}/current-question", response_model=QuestionResponse)
def get_question(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Get the current interview question with traceability metadata."""
    from backend.app.models.interview import InterviewSession

    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Interview is already completed")

    question = get_current_question(db, session_id)
    if not question:
        raise HTTPException(status_code=404, detail="No current question available")

    return QuestionResponse(
        question_id=question.id,
        question_index=question.question_index,
        total_questions=session.total_questions,
        question_text=question.question_text,
        topic=question.topic,
        subtopic=question.subtopic,
        difficulty=question.difficulty,
        question_type=question.question_type,
        section=question.section or "Technical Concepts",
        source_type=question.source_type or "general_rag",
        resume_section=question.resume_section or question.section or "General Technical",
        source_item=question.source_item or "",
        source_signals=question.source_signals,
        traceability=question.traceability_dict(),
    )


@router.post("/{session_id}/answers", response_model=AnswerEvaluationResponse)
def submit_interview_answer(
    session_id: str,
    request: AnswerSubmitRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Submit an answer for the current question and receive evaluation."""
    settings = get_settings()
    check_rate_limit(http_request, "submit_answer", settings.rate_limit_answer_per_minute)

    try:
        result = submit_answer(
            db=db,
            session_id=session_id,
            answer_text=request.answer_text,
            is_retry=request.is_retry,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Answer submission failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process answer")

    eval_data = result["evaluation"]
    return AnswerEvaluationResponse(
        answer_id=result["answer_id"],
        score=eval_data["score"],
        technical_accuracy=eval_data["technical_accuracy"],
        completeness=eval_data["completeness"],
        reasoning_depth=eval_data["reasoning_depth"],
        communication=eval_data["communication"],
        feedback=eval_data["feedback"],
        strengths=eval_data.get("strengths", []),
        missing_concepts=eval_data.get("missing_concepts", []),
        suggestions=eval_data.get("suggestions", ""),
        has_next_question=result["has_next_question"],
        message="Answer re-evaluated successfully" if result.get("is_retry") else "Answer evaluated successfully",
    )


@router.post("/{session_id}/retry", response_model=QuestionResponse)
def retry_interview_question(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Reset the current question so candidate can improve and re-submit their answer."""
    from backend.app.models.interview import InterviewSession

    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    try:
        from backend.app.services.interview_service import retry_question
        question = retry_question(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Retry question failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retry question")

    return QuestionResponse(
        question_id=question.id,
        question_index=question.question_index,
        total_questions=session.total_questions,
        question_text=question.question_text,
        topic=question.topic,
        subtopic=question.subtopic,
        difficulty=question.difficulty,
        question_type=question.question_type,
        section=question.section or "Technical Concepts",
        source_type=question.source_type or "general_rag",
        resume_section=question.resume_section or question.section or "General Technical",
        source_item=question.source_item or "",
        source_signals=question.source_signals,
        traceability=question.traceability_dict(),
    )


@router.post("/{session_id}/finish", response_model=InterviewResultsResponse)
@router.post("/{session_id}/end", response_model=InterviewResultsResponse)
def end_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """End the interview session at any time and generate the final report on completed answers."""
    from backend.app.models.interview import InterviewSession, Question, Answer
    from backend.app.models.candidate import Candidate
    from backend.app.services.interview_service import finish_interview

    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    try:
        report = finish_interview(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Finish interview failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete interview")

    candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()

    questions = (
        db.query(Question)
        .filter(Question.session_id == session_id)
        .order_by(Question.question_index)
        .all()
    )

    question_details = []
    answered_count = 0
    score_progression = []
    category_scores = {}
    difficulty_scores = {}

    for q in questions:
        answer = db.query(Answer).filter(Answer.question_id == q.id).first()
        if answer:
            answered_count += 1
            question_details.append(
                QuestionResultDetail(
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
                    answer_text=answer.answer_text,
                    score=answer.score,
                    technical_accuracy=answer.technical_accuracy,
                    completeness=answer.completeness,
                    feedback=answer.feedback,
                    strengths=answer.strengths,
                    missing_concepts=answer.missing_concepts,
                    traceability=q.traceability_dict(),
                )
            )
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

    cat_avg_scores = {k: round(sum(v) / len(v), 1) for k, v in category_scores.items()}
    diff_avg_scores = {k: round(sum(v) / len(v), 1) for k, v in difficulty_scores.items()}

    return InterviewResultsResponse(
        session_id=session.id,
        candidate_name=candidate.name if candidate else "Candidate",
        role=session.role,
        status=session.status,
        is_mock_mode=bool(session.is_mock_mode),
        is_completed_early=bool(session.is_completed_early),
        overall_score=report.overall_score,
        technical_score=report.technical_score,
        communication_score=report.communication_score,
        overall_assessment=report.overall_assessment,
        technical_proficiency=report.technical_proficiency,
        strong_areas=report.strong_areas,
        weak_areas=report.weak_areas,
        recommendations=report.recommendations,
        topics_covered=report.topics_covered,
        hiring_recommendation=report.hiring_recommendation,
        confidence_level=report.confidence_level,
        interview_quality_note=report.interview_quality_note,
        coverage_summary=report.coverage_summary,
        category_scores=cat_avg_scores,
        difficulty_scores=diff_avg_scores,
        score_progression=score_progression,
        questions=question_details,
        questions_attempted=len(question_details),
        questions_answered=answered_count,
        total_questions=session.total_questions,
        start_time=session.start_time.isoformat() if session.start_time else None,
        end_time=session.end_time.isoformat() if session.end_time else None,
    )


@router.post("/{session_id}/next-question", response_model=QuestionResponse)
def get_next_interview_question(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Advance to and generate the next adaptive question."""
    from backend.app.models.interview import InterviewSession

    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Interview is already completed")

    from backend.app.services.interview_service import generate_next_question

    try:
        question = generate_next_question(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate next question: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate next question")

    if not question:
        raise HTTPException(status_code=400, detail="No more questions in this interview")

    return QuestionResponse(
        question_id=question.id,
        question_index=question.question_index,
        total_questions=session.total_questions,
        question_text=question.question_text,
        topic=question.topic,
        subtopic=question.subtopic,
        difficulty=question.difficulty,
        question_type=question.question_type,
        section=question.section or "Technical Concepts",
        source_type=question.source_type or "general_rag",
        resume_section=question.resume_section or question.section or "General Technical",
        source_item=question.source_item or "",
        source_signals=question.source_signals,
        traceability=question.traceability_dict(),
    )
