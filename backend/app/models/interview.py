"""Interview-related ORM models: sessions, questions, answers, reports."""

import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.database import Base


class InterviewSession(Base):
    """An interview session linking a candidate to a role."""

    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, default="created")  # created, in_progress, completed
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=8)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime, nullable=True)
    is_mock_mode = Column(Integer, default=0)  # SQLite boolean
    is_completed_early = Column(Integer, default=0)

    # Relationships
    questions = relationship(
        "Question", back_populates="session", order_by="Question.question_index"
    )
    report = relationship("InterviewReport", back_populates="session", uselist=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "role": self.role,
            "status": self.status,
            "current_question_index": self.current_question_index,
            "total_questions": self.total_questions,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "is_mock_mode": bool(self.is_mock_mode),
            "is_completed_early": bool(self.is_completed_early),
        }


class Question(Base):
    """A single interview question with full traceability."""

    __tablename__ = "questions"

    id = Column(String, primary_key=True)
    session_id = Column(
        String, ForeignKey("interview_sessions.id"), nullable=False
    )
    question_index = Column(Integer, nullable=False)  # 0-based index
    question_text = Column(Text, nullable=False)
    topic = Column(String, default="General")
    subtopic = Column(String, default="")
    difficulty = Column(String, default="intermediate")
    question_type = Column(String, default="conceptual")
    section = Column(String, default="Technical Concepts")
    expected_concepts_json = Column(Text, default="[]")

    # Provenance & Resume Traceability
    source_type = Column(String, default="general_rag")
    resume_section = Column(String, default="General Technical")
    source_item = Column(String, default="")
    source_signals_json = Column(Text, default="[]")

    # Traceability
    retrieval_query_json = Column(Text, default="[]")
    retrieved_chunks_json = Column(Text, default="[]")
    generation_context = Column(Text, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False)

    @property
    def expected_concepts(self) -> list[str]:
        return json.loads(self.expected_concepts_json) if self.expected_concepts_json else []

    @expected_concepts.setter
    def expected_concepts(self, value: list[str]):
        self.expected_concepts_json = json.dumps(value)

    @property
    def source_signals(self) -> list[str]:
        return json.loads(self.source_signals_json) if self.source_signals_json else []

    @source_signals.setter
    def source_signals(self, value: list[str]):
        self.source_signals_json = json.dumps(value)

    @property
    def retrieval_queries(self) -> list[str]:
        return json.loads(self.retrieval_query_json) if self.retrieval_query_json else []

    @retrieval_queries.setter
    def retrieval_queries(self, value: list[str]):
        self.retrieval_query_json = json.dumps(value)

    @property
    def retrieved_chunks(self) -> list[dict]:
        return json.loads(self.retrieved_chunks_json) if self.retrieved_chunks_json else []

    @retrieved_chunks.setter
    def retrieved_chunks(self, value: list[dict]):
        self.retrieved_chunks_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question_index": self.question_index,
            "question_text": self.question_text,
            "topic": self.topic,
            "subtopic": self.subtopic,
            "difficulty": self.difficulty,
            "question_type": self.question_type,
            "section": self.section or "Technical Concepts",
            "source_type": self.source_type or "general_rag",
            "resume_section": self.resume_section or self.section or "General Technical",
            "source_item": self.source_item or "",
            "source_signals": self.source_signals,
            "expected_concepts": self.expected_concepts,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def traceability_dict(self) -> dict:
        """Return traceability information for the question."""
        return {
            "source_type": self.source_type or "general_rag",
            "resume_section": self.resume_section or self.section or "General Technical",
            "source_item": self.source_item or "",
            "source_signals": self.source_signals,
            "retrieval_queries": self.retrieval_queries,
            "retrieved_chunks": self.retrieved_chunks[:3],  # Limit for UI
            "generation_context": self.generation_context[:500] if self.generation_context else "",
            "topic": self.topic,
            "difficulty": self.difficulty,
            "section": self.section or "Technical Concepts",
        }


class Answer(Base):
    """A candidate's answer to a question with evaluation."""

    __tablename__ = "answers"

    id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    session_id = Column(
        String, ForeignKey("interview_sessions.id"), nullable=False
    )
    answer_text = Column(Text, nullable=False)

    # Evaluation scores
    score = Column(Float, default=0.0)
    technical_accuracy = Column(Float, default=0.0)
    completeness = Column(Float, default=0.0)
    reasoning_depth = Column(Float, default=0.0)
    communication = Column(Float, default=0.0)

    # Evaluation details
    feedback = Column(Text, default="")
    strengths_json = Column(Text, default="[]")
    missing_concepts_json = Column(Text, default="[]")
    suggestions = Column(Text, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    question = relationship("Question", back_populates="answer")

    @property
    def strengths(self) -> list[str]:
        return json.loads(self.strengths_json) if self.strengths_json else []

    @strengths.setter
    def strengths(self, value: list[str]):
        self.strengths_json = json.dumps(value)

    @property
    def missing_concepts(self) -> list[str]:
        return json.loads(self.missing_concepts_json) if self.missing_concepts_json else []

    @missing_concepts.setter
    def missing_concepts(self, value: list[str]):
        self.missing_concepts_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question_id": self.question_id,
            "answer_text": self.answer_text,
            "score": self.score,
            "technical_accuracy": self.technical_accuracy,
            "completeness": self.completeness,
            "reasoning_depth": self.reasoning_depth,
            "communication": self.communication,
            "feedback": self.feedback,
            "strengths": self.strengths,
            "missing_concepts": self.missing_concepts,
            "suggestions": self.suggestions,
        }


class InterviewReport(Base):
    """Final interview summary report."""

    __tablename__ = "interview_reports"

    id = Column(String, primary_key=True)
    session_id = Column(
        String, ForeignKey("interview_sessions.id"), nullable=False, unique=True
    )

    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)

    overall_assessment = Column(Text, default="")
    technical_proficiency = Column(Text, default="")
    strong_areas_json = Column(Text, default="[]")
    weak_areas_json = Column(Text, default="[]")
    recommendations_json = Column(Text, default="[]")
    topics_covered_json = Column(Text, default="[]")
    coverage_summary_json = Column(Text, default="{}")

    hiring_recommendation = Column(String, default="")
    confidence_level = Column(String, default="")
    interview_quality_note = Column(Text, default="")
    is_completed_early = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    session = relationship("InterviewSession", back_populates="report")

    @property
    def strong_areas(self) -> list[str]:
        return json.loads(self.strong_areas_json) if self.strong_areas_json else []

    @strong_areas.setter
    def strong_areas(self, value: list[str]):
        self.strong_areas_json = json.dumps(value)

    @property
    def weak_areas(self) -> list[str]:
        return json.loads(self.weak_areas_json) if self.weak_areas_json else []

    @weak_areas.setter
    def weak_areas(self, value: list[str]):
        self.weak_areas_json = json.dumps(value)

    @property
    def recommendations(self) -> list[str]:
        return json.loads(self.recommendations_json) if self.recommendations_json else []

    @recommendations.setter
    def recommendations(self, value: list[str]):
        self.recommendations_json = json.dumps(value)

    @property
    def topics_covered(self) -> list[str]:
        return json.loads(self.topics_covered_json) if self.topics_covered_json else []

    @topics_covered.setter
    def topics_covered(self, value: list[str]):
        self.topics_covered_json = json.dumps(value)

    @property
    def coverage_summary(self) -> dict:
        return json.loads(self.coverage_summary_json) if self.coverage_summary_json else {}

    @coverage_summary.setter
    def coverage_summary(self, value: dict):
        self.coverage_summary_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "overall_score": self.overall_score,
            "technical_score": self.technical_score,
            "communication_score": self.communication_score,
            "overall_assessment": self.overall_assessment,
            "technical_proficiency": self.technical_proficiency,
            "strong_areas": self.strong_areas,
            "weak_areas": self.weak_areas,
            "recommendations": self.recommendations,
            "topics_covered": self.topics_covered,
            "coverage_summary": self.coverage_summary,
            "hiring_recommendation": self.hiring_recommendation,
            "confidence_level": self.confidence_level,
            "interview_quality_note": self.interview_quality_note,
            "is_completed_early": bool(self.is_completed_early),
            "questions_answered": self.questions_answered,
        }
