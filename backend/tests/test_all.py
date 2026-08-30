"""Comprehensive test suite for the AI Interview System.

All tests use mock LLM to avoid API dependencies.
Run with: pytest backend/tests/ -q
"""

import json
import os
import sys
import uuid
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.models.database import Base
from backend.app.models.candidate import Candidate
from backend.app.models.interview import InterviewSession, Question, Answer, InterviewReport
from backend.app.services.resume_parser import parse_pdf, parse_text_resume
from backend.app.services.resume_analyzer import analyze_resume_deterministic, merge_analyses
from backend.app.services.role_config import (
    get_role_config, get_all_roles, get_role_ids,
    get_difficulty_for_stage, get_topic_for_stage,
)
from backend.app.services.llm_service import LLMService, MockProvider, LLMProvider
from backend.app.services.mock_engine import MockEngine
from backend.app.services.answer_evaluator import evaluate_answer
from backend.app.core.config import Settings


# ─── Fixtures ────────────────────────────────────────

@pytest.fixture(autouse=True)
def use_mock_llm(monkeypatch):
    """Ensure test suite runs hermetically with MockProvider unless explicitly testing real providers."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from backend.app.core.config import reset_settings
    reset_settings()
    LLMService.reset_provider()
    yield
    reset_settings()
    LLMService.reset_provider()


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_resume_text():
    return """
John Doe
john.doe@email.com
+1-555-0123

SKILLS
Python, JavaScript, TensorFlow, PyTorch, scikit-learn, NLP, Machine Learning,
Flask, Docker, AWS, PostgreSQL, Git

EXPERIENCE
Machine Learning Engineer - 3 years
- Built NLP pipeline using spaCy and Transformers
- Deployed models using Docker and AWS

PROJECTS
Fake News Detection
Built a fake news classifier using TF-IDF and Logistic Regression.
Achieved 95% accuracy on test set.
Technologies: Python, scikit-learn, NLTK

Chatbot System
Developed a conversational AI chatbot using GPT-3 API and LangChain.
Technologies: Python, OpenAI API, LangChain, FastAPI

EDUCATION
Master of Science in Computer Science, Stanford University
Bachelor of Technology in Computer Engineering
"""


@pytest.fixture
def sample_candidate(db_session, sample_resume_text):
    """Create a sample candidate in the database."""
    candidate = Candidate(
        id=str(uuid.uuid4()),
        name="John Doe",
        email="john.doe@email.com",
        resume_filename="test_resume.pdf",
        resume_text=sample_resume_text,
        experience_years=3,
    )
    candidate.skills = ["Python", "Machine Learning", "NLP"]
    candidate.programming_languages = ["Python", "JavaScript"]
    candidate.frameworks = ["Flask", "FastAPI"]
    candidate.databases_list = ["PostgreSQL"]
    candidate.cloud_devops = ["Docker", "AWS"]
    candidate.ai_ml_technologies = ["TensorFlow", "PyTorch", "scikit-learn"]
    candidate.projects = [
        {"name": "Fake News Detection", "description": "TF-IDF + Logistic Regression classifier", "technologies": ["Python", "scikit-learn"]},
        {"name": "Chatbot System", "description": "GPT-3 powered chatbot", "technologies": ["Python", "LangChain"]},
    ]
    candidate.education = ["MS Computer Science", "BTech Computer Engineering"]
    candidate.domains = ["Machine Learning", "NLP"]

    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


# ─── Resume Parser Tests ─────────────────────────────

class TestResumeParser:
    def test_parse_text_resume(self, sample_resume_text):
        result = parse_text_resume(sample_resume_text)
        assert isinstance(result, str)
        assert len(result) > 50
        assert "John Doe" in result

    def test_parse_empty_text(self):
        with pytest.raises(ValueError, match="empty"):
            parse_text_resume("")

    def test_parse_whitespace_text(self):
        with pytest.raises(ValueError, match="empty"):
            parse_text_resume("   \n\t  ")

    def test_pdf_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_pdf("nonexistent_file.pdf")

    def test_pdf_wrong_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as f:
            with pytest.raises(ValueError, match="Only PDF files are supported"):
                parse_pdf(f.name)


# ─── Resume Analyzer Tests ───────────────────────────

class TestResumeAnalyzer:
    def test_deterministic_extraction(self, sample_resume_text):
        result = analyze_resume_deterministic(sample_resume_text)
        assert "Python" in result["programming_languages"]
        assert result["name"] == "John Doe"
        assert result["email"] == "john.doe@email.com"
        assert result["experience_years"] == 3
        assert len(result["skills"]) > 0

    def test_merge_analyses_prefers_llm(self):
        deterministic = {
            "name": "",
            "email": "test@test.com",
            "skills": ["Python"],
            "programming_languages": ["Python"],
            "projects": [],
            "experience_years": 0,
        }
        llm = {
            "name": "Jane Smith",
            "email": "test@test.com",
            "skills": ["Python", "PyTorch"],
            "programming_languages": ["Python"],
            "projects": [{"name": "P1", "description": "D1"}],
            "experience_years": 5,
        }
        merged = merge_analyses(deterministic, llm)
        assert merged["name"] == "Jane Smith"
        assert merged["experience_years"] == 5
        assert "PyTorch" in merged["skills"]
        assert len(merged["projects"]) == 1


# ─── Role Config Tests ───────────────────────────────

class TestRoleConfig:
    def test_all_roles_have_required_fields(self):
        roles = get_all_roles()
        assert len(roles) == 3
        for role in roles:
            assert "id" in role
            assert "name" in role
            assert "description" in role
            assert "topics" in role
            assert len(role["topics"]) > 0
            assert "expected_skills" in role
            
            # Check detailed config
            full_config = get_role_config(role["id"])
            assert "collection" in full_config

    def test_role_ids(self):
        ids = get_role_ids()
        assert "ai_ml_engineer" in ids
        assert "backend_engineer" in ids
        assert "data_scientist" in ids

    def test_difficulty_progression(self):
        # Early questions should be beginner/intermediate
        d0 = get_difficulty_for_stage("ai_ml_engineer", 0, 8)
        assert d0 == "beginner"

        # Middle questions should be intermediate
        d3 = get_difficulty_for_stage("ai_ml_engineer", 3, 8)
        assert d3 == "intermediate"

        # Late questions should be advanced
        d7 = get_difficulty_for_stage("ai_ml_engineer", 7, 8)
        assert d7 == "advanced"

    def test_topic_selection_avoids_repetition(self):
        covered = ["Machine Learning", "NLP"]
        topic = get_topic_for_stage("ai_ml_engineer", 2, 8, covered_topics=covered)
        assert topic not in covered


# ─── LLM Service Tests ───────────────────────────────

class TestLLMService:
    def test_mock_provider_is_always_available(self):
        provider = MockProvider()
        assert provider.is_available() is True
        assert provider.provider_name == "Mock/Demo Provider"

    def test_mock_generate_returns_valid_json(self):
        provider = MockProvider()
        response = provider.generate(
            "Generate an interview question for AI/ML Engineer on Machine Learning"
        )
        data = json.loads(response)
        assert "question" in data
        assert "expected_concepts" in data

    def test_mock_answer_evaluation(self):
        provider = MockProvider()
        prompt = """Evaluate the following interview answer.
QUESTION: Explain TF-IDF and its purpose.
CANDIDATE'S ANSWER: TF-IDF is term frequency inverse document frequency used to weight rare words.
EXPECTED CONCEPTS: Term Frequency, Inverse Document Frequency, Weighting
DIFFICULTY LEVEL: intermediate
"""
        response = provider.generate(prompt)
        data = json.loads(response)
        assert "score" in data
        assert "technical_accuracy" in data
        assert "feedback" in data

    def test_gemini_provider_init_and_availability(self):
        from backend.app.services.llm_service import GeminiProvider
        provider = GeminiProvider(api_key="test_key", model="gemini-3.6-flash")
        assert provider.is_available() is True
        assert provider.provider_name == "Gemini (gemini-3.6-flash)"

    def test_gemini_clean_markdown_json(self):
        from backend.app.services.llm_service import GeminiProvider
        raw = "```json\n{\"test\": true, \"score\": 9.5}\n```"
        cleaned = GeminiProvider._clean_markdown_json(raw)
        assert json.loads(cleaned) == {"test": True, "score": 9.5}

    def test_llm_service_selects_gemini_when_configured(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "dummy_gemini_key")
        from backend.app.core.config import reset_settings
        reset_settings()
        LLMService.reset_provider()
        provider = LLMService.get_provider()
        assert "Gemini" in provider.provider_name


# ─── Dynamic Evaluation & Generation Tests ───────────

class TestDynamicEvaluationAndGeneration:
    """Rigorous tests proving the mock intelligence engine is input-dependent and non-static."""

    def test_case_a_excellent_answer(self):
        """Case A: Excellent answer gets high technical, completeness, and reasoning scores."""
        question = "What is TF-IDF and why would you use it in text classification?"
        answer = (
            "TF-IDF combines Term Frequency (TF) with Inverse Document Frequency (IDF). "
            "TF measures how often a word occurs in a specific document, while IDF reduces the "
            "weight of terms that appear frequently across all documents (such as stop words). "
            "This produces a numerical feature matrix where distinctive keywords receive higher weights. "
            "In my project, I used TF-IDF to vectorize text before training a Logistic Regression classifier."
        )
        expected = [
            "Term Frequency (TF) formula and intuition",
            "Inverse Document Frequency (IDF) downweighting common words",
            "Sparsity and feature matrix representation",
            "Vectorization / numerical text representation"
        ]

        result = evaluate_answer(
            question_text=question,
            answer_text=answer,
            expected_concepts=expected,
            retrieved_context="TF-IDF downweights common words and highlights distinctive terms.",
            difficulty="intermediate"
        )

        assert result["score"] >= 7.0, f"Expected high score for excellent answer, got {result['score']}"
        assert result["technical_accuracy"] >= 6.5
        assert result["completeness"] >= 6.0
        assert len(result["strengths"]) > 0

    def test_case_b_weak_answer(self):
        """Case B: Weak answer gets lower completeness and score, and flags missing concepts."""
        question = "What is TF-IDF and why would you use it in text classification?"
        answer = "TF-IDF is a machine learning thing used for classification."
        expected = [
            "Term Frequency (TF) formula and intuition",
            "Inverse Document Frequency (IDF) downweighting common words",
            "Sparsity and feature matrix representation",
            "Vectorization / numerical text representation"
        ]

        result = evaluate_answer(
            question_text=question,
            answer_text=answer,
            expected_concepts=expected,
            retrieved_context="TF-IDF computes TF multiplied by IDF.",
            difficulty="intermediate"
        )

        assert result["score"] < 5.5, f"Expected lower score for weak answer, got {result['score']}"
        assert len(result["missing_concepts"]) >= 2
        assert "preliminary" in result["feedback"].lower() or "lacks" in result["feedback"].lower() or "missed" in result["feedback"].lower()

    def test_case_c_unrelated_wrong_answer(self):
        """Case C: Off-topic / wrong answer gets very low score and off-topic notification."""
        question = "What is TF-IDF and why would you use it in text classification?"
        answer = "Python is an interpreted programming language used for backend web development."
        expected = [
            "Term Frequency (TF) formula and intuition",
            "Inverse Document Frequency (IDF) downweighting common words",
            "Sparsity and feature matrix representation"
        ]

        result = evaluate_answer(
            question_text=question,
            answer_text=answer,
            expected_concepts=expected,
            retrieved_context="TF-IDF computes TF multiplied by IDF.",
            difficulty="intermediate"
        )

        assert result["score"] <= 2.5, f"Expected very low score for off-topic answer, got {result['score']}"
        assert result["completeness"] == 0.0
        assert "does not address the question" in result["feedback"].lower() or "unrelated" in result["feedback"].lower()

    def test_case_d_empty_answer(self):
        """Case D: Blank or whitespace answer gets score 0."""
        question = "Explain database indexing."
        result = evaluate_answer(question, "   ", ["B-Tree", "Lookup complexity"])
        assert result["score"] == 0.0
        assert result["technical_accuracy"] == 0.0
        assert "No answer" in result["feedback"]

    def test_case_e_different_questions_same_answer(self):
        """Case E: Same answer evaluated against different questions produces different scores."""
        answer = "B-Tree indexes provide logarithmic O(log N) lookups for range queries and primary keys."
        
        # Question 1: Relevant to database indexing
        eval_q1 = evaluate_answer(
            question_text="How do B-Tree indexes improve database query performance?",
            answer_text=answer,
            expected_concepts=["B-Tree index structure", "Logarithmic O(log N) lookup", "Range queries"],
            difficulty="intermediate"
        )

        # Question 2: Irrelevant (Neural Network backpropagation)
        eval_q2 = evaluate_answer(
            question_text="Explain the backpropagation algorithm in neural networks.",
            answer_text=answer,
            expected_concepts=["Gradient descent", "Chain rule", "Loss function partial derivatives"],
            difficulty="intermediate"
        )

        assert eval_q1["score"] > eval_q2["score"] + 3.0, (
            f"Relevant Q1 score ({eval_q1['score']}) should be substantially higher than irrelevant Q2 score ({eval_q2['score']})"
        )

    def test_dynamic_question_generation_grounded_in_candidate_projects(self):
        """Verify generated questions adapt to candidate's projects and skills."""
        prompt_ai_candidate = """Generate a personalized technical interview question for a AI/ML Engineer candidate.

CANDIDATE PROFILE:
Skills: Python, TF-IDF, Logistic Regression, PyTorch, NLTK
Projects:
- Fake News Detection: TF-IDF + Logistic Regression classifier (Technologies: Python, scikit-learn, NLTK)

INTERVIEW CONTEXT:
Topic: NLP
Difficulty: intermediate
Question 1 of 8

KNOWLEDGE BASE CONTEXT:
### TF-IDF Representation
TF-IDF calculates term frequency and inverse document frequency.
"""
        provider = MockProvider()
        q_json = provider.generate(prompt_ai_candidate)
        q_data = json.loads(q_json)

        assert "Fake News Detection" in q_data["question"] or "TF-IDF" in q_data["question"] or "NLP" in q_data["question"]
        assert len(q_data["expected_concepts"]) >= 3

    def test_generate_10_interview_questions_variety(self, sample_candidate):
        """Generate 10 questions across stages and verify diversity, adaptation, and topic variation."""
        from backend.app.services.question_generator import generate_question

        candidate_profile = sample_candidate.to_dict()
        questions = []
        topics = []
        for i in range(10):
            q_data = generate_question(
                candidate_profile=candidate_profile,
                role_id="ai_ml_engineer",
                question_index=i,
                total_questions=10,
                previous_qa=[{"topic": t, "score": 8.0} for t in topics],
            )
            questions.append(q_data["question_text"])
            topics.append(q_data["topic"])

        # Verify questions are diverse and not static duplicates
        assert len(set(questions)) >= 3
        assert len(set(topics)) >= 3

    def test_dynamic_interview_summary_synthesis(self):
        """Verify report summary reflects actual candidate scores and topic performance."""
        summary_prompt = """Generate a comprehensive interview summary report.

CANDIDATE: Alice Wonder
ROLE: Backend Engineer

PERFORMANCE:
Q1 [REST API] (Difficulty: beginner)
  Question: Explain REST API methods
  Score: 9.0/10

Q2 [Database Indexing] (Difficulty: intermediate)
  Question: Explain B-Tree indexing
  Score: 8.5/10

Q3 [Docker & Containers] (Difficulty: advanced)
  Question: Explain Linux namespaces
  Score: 4.0/10

AGGREGATE SCORES:
{'average_score': 7.2, 'average_technical': 7.0, 'average_communication': 7.5, 'questions_answered': 3, 'total_questions': 3}
"""
        provider = MockProvider()
        report_json = provider.generate(summary_prompt)
        report_data = json.loads(report_json)

        assert "Alice Wonder" in report_data["overall_assessment"]
        assert report_data["hiring_recommendation"] in ("yes", "strong_yes", "maybe")
        assert any("REST API" in s or "Database" in s for s in report_data["strong_areas"])
        assert any("Docker" in w or "Containers" in w or "namespaces" in w.lower() for w in report_data["weak_areas"])


# ─── Question Generation Schema Tests ────────────────

class TestQuestionGenerationSchema:
    def test_mock_question_has_required_fields(self):
        provider = MockProvider()
        response = provider.generate(
            "Generate a personalized technical interview question\nTopic: NLP\nDifficulty: intermediate"
        )
        data = json.loads(response)
        assert "question" in data
        assert "topic" in data
        assert "difficulty" in data
        assert "expected_concepts" in data


# ─── API Tests ───────────────────────────────────────

class TestAPI:
    @pytest.fixture
    def client(self):
        """Create a test client with in-memory database."""
        from fastapi.testclient import TestClient
        from sqlalchemy.pool import StaticPool
        from backend.app.main import app
        from backend.app.models.database import Base, get_db, create_tables

        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        create_tables(engine)
        TestSession = sessionmaker(bind=engine)

        def override_get_db():
            db = TestSession()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert "llm_mode" in data

    def test_roles_endpoint(self, client):
        response = client.get("/api/roles")
        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 3

    def test_upload_no_file(self, client):
        response = client.post("/api/resume/upload")
        assert response.status_code in (400, 422)

    def test_invalid_session(self, client):
        response = client.get("/api/interviews/nonexistent-session")
        assert response.status_code == 404


# ─── Integration Test ────────────────────────────────

class TestIntegration:
    def test_full_interview_flow(self, db_session, sample_candidate):
        """End-to-end test: create interview → answer questions → get results."""
        from backend.app.services.interview_service import (
            create_interview_session,
            get_current_question,
            submit_answer,
            generate_next_question,
            generate_report,
        )

        # Create interview
        session = create_interview_session(
            db=db_session,
            candidate_id=sample_candidate.id,
            role="ai_ml_engineer",
            total_questions=3,  # Short interview for testing
        )
        assert session.status == "in_progress"

        # Answer all questions
        for i in range(3):
            question = get_current_question(db_session, session.id)
            assert question is not None
            assert question.question_text

            result = submit_answer(
                db=db_session,
                session_id=session.id,
                answer_text=f"This is my detailed answer for question {i+1}. Machine learning involves training models on data.",
            )
            assert "evaluation" in result
            assert result["evaluation"]["score"] >= 0

            if result["has_next_question"]:
                next_q = generate_next_question(db_session, session.id)
                assert next_q is not None

        # Verify session completed
        db_session.refresh(session)
        assert session.status == "completed"

        # Generate report
        report = generate_report(db_session, session.id)
        assert report is not None
        assert report.overall_score >= 0

    def test_invalid_role_rejected(self, db_session, sample_candidate):
        from backend.app.services.interview_service import create_interview_session

        with pytest.raises(ValueError, match="Invalid role"):
            create_interview_session(
                db=db_session,
                candidate_id=sample_candidate.id,
                role="invalid_role",
            )

    def test_nonexistent_candidate_rejected(self, db_session):
        from backend.app.services.interview_service import create_interview_session

        with pytest.raises(ValueError, match="not found"):
            create_interview_session(
                db=db_session,
                candidate_id="nonexistent-id",
                role="ai_ml_engineer",
            )

    def test_duplicate_answer_rejected(self, db_session, sample_candidate):
        from backend.app.services.interview_service import (
            create_interview_session, submit_answer,
        )

        session = create_interview_session(
            db=db_session,
            candidate_id=sample_candidate.id,
            role="ai_ml_engineer",
            total_questions=2,
        )

        # First answer
        submit_answer(db_session, session.id, "First answer")

        # Duplicate without is_retry should fail
        with pytest.raises(ValueError, match="already submitted"):
            submit_answer(db_session, session.id, "Duplicate answer", is_retry=False)

    def test_retry_question_flow(self, db_session, sample_candidate):
        """Test retry functionality preserves question and updates answer score."""
        from backend.app.services.interview_service import (
            create_interview_session, get_current_question, submit_answer, retry_question,
        )

        session = create_interview_session(
            db=db_session,
            candidate_id=sample_candidate.id,
            role="ai_ml_engineer",
            total_questions=3,
        )

        q1 = get_current_question(db_session, session.id)
        assert q1.section in [
            "Introduction / Background", "Projects", "Skills", "Work Experience",
            "Certifications", "Technical Concepts", "General Technical", "Follow-up / Performance Based"
        ]

        # Weak answer
        res1 = submit_answer(db_session, session.id, "It is some basic tool.")
        score1 = res1["evaluation"]["score"]

        # Retry question
        q_retry = retry_question(db_session, session.id)
        assert q_retry.id == q1.id
        assert q_retry.question_text == q1.question_text

        # Re-submit strong answer with is_retry=True or fresh submission
        res2 = submit_answer(
            db_session,
            session.id,
            f"In {q1.topic}, we optimize mathematical parameters using gradient descent and loss functions like cross-entropy to minimize error and ensure model generalization on validation sets.",
        )
        score2 = res2["evaluation"]["score"]
        assert score2 > score1

    def test_finish_interview_early_flow(self, db_session, sample_candidate):
        """Test ending an interview early generates report based strictly on completed answers."""
        from backend.app.services.interview_service import (
            create_interview_session, submit_answer, finish_interview,
        )

        session = create_interview_session(
            db=db_session,
            candidate_id=sample_candidate.id,
            role="backend_engineer",
            total_questions=6,
        )

        # Answer only 1 question
        submit_answer(
            db_session,
            session.id,
            "PostgreSQL uses Multiversion Concurrency Control (MVCC) and WAL logging for ACID transactions."
        )

        # End interview early
        report = finish_interview(db_session, session.id)
        db_session.refresh(session)

        assert session.status == "completed"
        assert session.is_completed_early == 1
        assert report.is_completed_early == 1
        assert report.questions_answered == 1
        assert report.overall_score > 0

