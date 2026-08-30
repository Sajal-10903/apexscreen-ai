"""Pydantic request/response schemas for the API layer."""

from pydantic import BaseModel, Field
from datetime import datetime


# ─── Resume ───────────────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    candidate_id: str
    name: str
    skills: list[str]
    programming_languages: list[str]
    frameworks: list[str]
    databases: list[str]
    cloud_devops: list[str]
    ai_ml_technologies: list[str]
    projects: list[dict]
    education: list[str]
    domains: list[str]
    experience_years: int
    message: str = "Resume processed successfully"


# ─── Roles ────────────────────────────────────────────────

class RoleInfo(BaseModel):
    id: str
    name: str
    description: str
    topics: list[str]
    expected_skills: list[str]
    icon: str = "💼"


class RolesListResponse(BaseModel):
    roles: list[RoleInfo]


# ─── Interview ────────────────────────────────────────────

class InterviewCreateRequest(BaseModel):
    candidate_id: str
    role: str


class InterviewCreateResponse(BaseModel):
    session_id: str
    role: str
    total_questions: int
    status: str
    is_mock_mode: bool
    message: str


class QuestionResponse(BaseModel):
    question_id: str
    question_index: int
    total_questions: int
    question_text: str
    topic: str
    subtopic: str = ""
    difficulty: str
    question_type: str = "conceptual"
    section: str = "Technical Concepts"
    source_type: str = "general_rag"
    resume_section: str = "General Technical"
    source_item: str = ""
    source_signals: list[str] = Field(default_factory=list)
    traceability: dict = Field(default_factory=dict)


class AnswerSubmitRequest(BaseModel):
    answer_text: str = Field(..., min_length=1, max_length=10000)
    is_retry: bool = False


class AnswerEvaluationResponse(BaseModel):
    answer_id: str
    score: float
    technical_accuracy: float
    completeness: float
    reasoning_depth: float
    communication: float
    feedback: str
    strengths: list[str]
    missing_concepts: list[str]
    suggestions: str
    has_next_question: bool
    message: str


class InterviewStatusResponse(BaseModel):
    session_id: str
    candidate_id: str
    role: str
    status: str
    current_question_index: int
    total_questions: int
    start_time: str | None
    end_time: str | None
    is_mock_mode: bool
    is_completed_early: bool = False
    questions_answered: int = 0


# ─── Results ──────────────────────────────────────────────

class QuestionResultDetail(BaseModel):
    question_index: int
    question_text: str
    topic: str
    difficulty: str
    question_type: str
    section: str = "Technical Concepts"
    source_type: str = "general_rag"
    resume_section: str = "General Technical"
    source_item: str = ""
    source_signals: list[str] = Field(default_factory=list)
    answer_text: str = ""
    score: float = 0.0
    technical_accuracy: float = 0.0
    completeness: float = 0.0
    feedback: str = ""
    strengths: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    traceability: dict = Field(default_factory=dict)


class InterviewResultsResponse(BaseModel):
    session_id: str
    candidate_name: str
    role: str
    status: str
    is_mock_mode: bool
    is_completed_early: bool = False

    # Aggregate scores
    overall_score: float
    technical_score: float
    communication_score: float

    # Report
    overall_assessment: str = ""
    technical_proficiency: str = ""
    strong_areas: list[str] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    topics_covered: list[str] = Field(default_factory=list)
    hiring_recommendation: str = ""
    confidence_level: str = ""
    interview_quality_note: str = ""

    # Analytics & Provenance
    coverage_summary: dict = Field(default_factory=dict)
    category_scores: dict = Field(default_factory=dict)
    difficulty_scores: dict = Field(default_factory=dict)
    score_progression: list[dict] = Field(default_factory=list)

    # Per-question details
    questions: list[QuestionResultDetail] = Field(default_factory=list)

    # Meta
    questions_attempted: int = 0
    questions_answered: int = 0
    total_questions: int = 0
    start_time: str | None = None
    end_time: str | None = None


# ─── Health ───────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    llm_available: bool
    llm_mode: str
    database: str
    vector_db: str
    embedding_model: str
    knowledge_base_indexed: bool


# ─── Error ────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_code: str = "UNKNOWN_ERROR"
