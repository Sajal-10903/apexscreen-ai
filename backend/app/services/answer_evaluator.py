"""Answer evaluation service using LLM with structured output."""

import json
import logging
import re

from backend.app.core.prompts import answer_evaluation_prompt
from backend.app.services.llm_service import LLMService
from backend.app.services.mock_engine import MockEngine

logger = logging.getLogger(__name__)


def evaluate_answer(
    question_text: str,
    answer_text: str,
    expected_concepts: list[str],
    retrieved_context: str = "",
    difficulty: str = "intermediate",
) -> dict:
    """Evaluate a candidate's answer against the question and expected concepts.

    Returns a structured evaluation dict with scores and feedback.
    """
    if not answer_text or not answer_text.strip():
        return _empty_answer_evaluation(expected_concepts)

    llm = LLMService.get_provider()

    prompt = answer_evaluation_prompt(
        question=question_text,
        answer=answer_text,
        expected_concepts=expected_concepts,
        retrieved_context=retrieved_context,
        difficulty=difficulty,
    )

    try:
        response = llm.generate(prompt, temperature=0.3)
        evaluation = _parse_evaluation(response)
        if evaluation:
            return evaluation
    except Exception as e:
        logger.error(f"Answer evaluation LLM call failed: {e}")

    # Fallback: deterministic MockEngine evaluation
    return MockEngine.evaluate_answer(prompt)


def _parse_evaluation(response: str) -> dict | None:
    """Parse LLM evaluation response into structured dict."""
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return None
        else:
            return None

    # Validate and normalize
    return {
        "score": _clamp(data.get("score", 0), 0, 10),
        "technical_accuracy": _clamp(data.get("technical_accuracy", 0), 0, 10),
        "completeness": _clamp(data.get("completeness", 0), 0, 10),
        "reasoning_depth": _clamp(data.get("reasoning_depth", 0), 0, 10),
        "communication": _clamp(data.get("communication", 0), 0, 10),
        "feedback": str(data.get("feedback", ""))[:2000],
        "strengths": [str(s)[:200] for s in data.get("strengths", [])][:10],
        "missing_concepts": [str(s)[:200] for s in data.get("missing_concepts", [])][:10],
        "suggestions": str(data.get("suggestions", ""))[:1000],
    }


def _empty_answer_evaluation(expected_concepts: list[str] | None = None) -> dict:
    """Evaluation for empty/blank answers."""
    missing = expected_concepts[:5] if expected_concepts else ["Complete technical answer required"]
    return {
        "score": 0.0,
        "technical_accuracy": 0.0,
        "completeness": 0.0,
        "reasoning_depth": 0.0,
        "communication": 0.0,
        "feedback": "No answer was provided. Please attempt to answer the question with technical explanations.",
        "strengths": [],
        "missing_concepts": missing,
        "suggestions": "Take time to explain the foundational principles and technical trade-offs.",
    }


def _clamp(value, min_val, max_val):
    """Clamp a value to a range."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return min_val
    return max(min_val, min(value, max_val))
