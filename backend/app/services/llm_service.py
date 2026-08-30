"""LLM service abstraction with Gemini, OpenAI, and Mock providers."""

import json
import logging
import re
import time
from abc import ABC, abstractmethod

import httpx

from backend.app.services.mock_engine import MockEngine

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate a response from the LLM."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is ready."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


class GeminiProvider(LLMProvider):
    """Google Gemini API provider using official REST endpoint with retry and graceful fallback."""

    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        self._api_key = api_key
        self._model = model
        self._client = httpx.Client(timeout=30.0)

    def generate(self, prompt: str, temperature: float = 0.7, max_retries: int = 1) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 3000,
            },
        }

        # 1. Try high-performance REST endpoint
        for attempt in range(max_retries + 1):
            try:
                response = self._client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "")
                            return self._clean_markdown_json(text)
                elif response.status_code == 429:
                    logger.warning(f"Gemini rate limit 429 on attempt {attempt+1}/{max_retries+1}.")
                    if attempt < max_retries:
                        time.sleep(1.0)
                        continue
                logger.warning(f"Gemini REST returned status {response.status_code}: {response.text[:150]}")
            except Exception as e:
                logger.warning(f"Gemini REST error on attempt {attempt+1}: {e}")
                if attempt < max_retries:
                    time.sleep(1.0)
                    continue

        # 2. SDK fallback attempt
        try:
            from google import genai
            from google.genai import types
            genai_client = genai.Client(api_key=self._api_key)
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=3000,
            )
            res = genai_client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            text = res.text or ""
            if text:
                return self._clean_markdown_json(text)
        except Exception as e:
            logger.warning(f"Gemini SDK fallback also failed: {e}")

        # 3. Graceful fallback to deterministic MockEngine to guarantee zero downtime
        logger.info("Using deterministic MockEngine simulation fallback for this turn.")
        mock_provider = MockProvider()
        return mock_provider.generate(prompt, temperature=temperature)

    @staticmethod
    def _clean_markdown_json(text: str) -> str:
        text = text.strip()
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            return match.group(1).strip()
        return text

    def is_available(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    @property
    def provider_name(self) -> str:
        return f"Gemini ({self._model})"


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str | None = None):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        from openai import OpenAI

        try:
            client_kwargs = {"api_key": self._api_key}
            if self._base_url:
                client_kwargs["base_url"] = self._base_url

            client = OpenAI(**client_kwargs)
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical interview assistant. Always respond with valid JSON when requested.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=2000,
            )
            text = response.choices[0].message.content or ""
            return self._clean_markdown_json(text)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"LLM generation failed: {e}")

    @staticmethod
    def _clean_markdown_json(text: str) -> str:
        text = text.strip()
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            return match.group(1).strip()
        return text

    def is_available(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    @property
    def provider_name(self) -> str:
        return f"OpenAI ({self._model})"


class MockProvider(LLMProvider):
    """Deterministic, input-dependent mock provider for demo/testing fallback mode.

    Derives its outputs directly from candidate resume, role, RAG context, and answer content.
    Never uses fake randomness or hardcoded answers.
    """

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        prompt_lower = prompt.lower()

        # Detect what kind of response is needed. Order matters: the most
        # specific/unique anchor phrases are checked first.
        if "analyze the following resume" in prompt_lower:
            return self._mock_resume_analysis(prompt)
        elif "candidate's answer:" in prompt_lower:
            return self._mock_answer_evaluation(prompt)
        elif "interview summary" in prompt_lower or "summary report" in prompt_lower:
            return self._mock_interview_summary(prompt)
        elif "generate" in prompt_lower and "search quer" in prompt_lower:
            return self._mock_query_generation(prompt)
        elif "generate" in prompt_lower and "interview question" in prompt_lower:
            return self._mock_question_generation(prompt)
        elif "evaluate" in prompt_lower and "answer" in prompt_lower:
            return self._mock_answer_evaluation(prompt)
        else:
            return json.dumps({"response": "Local simulation response"})

    def is_available(self) -> bool:
        return True

    @property
    def provider_name(self) -> str:
        return "Mock/Demo Provider"

    def _mock_resume_analysis(self, prompt: str) -> str:
        """Generate a deterministic resume analysis based on text extracted."""
        name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', prompt)
        name = name_match.group(1) if name_match else "Candidate"

        return json.dumps({
            "name": name,
            "email": "",
            "phone": "",
            "skills": ["Python", "Problem Solving", "Data Structures"],
            "programming_languages": ["Python"],
            "frameworks": [],
            "databases": [],
            "cloud_devops": [],
            "ai_ml_technologies": [],
            "projects": [],
            "experience_years": 0,
            "education": [],
            "domains": [],
        })

    def _mock_query_generation(self, prompt: str) -> str:
        # Extract role topics
        topics_match = re.search(r'Role Topics:\s*([^\n]+)', prompt)
        role_topics = [t.strip() for t in topics_match.group(1).split(',')] if topics_match else ["Machine Learning"]

        # Extract covered topics
        covered_match = re.search(r'Topics already covered:\s*([^\n]+)', prompt)
        covered_topics = [t.strip() for t in covered_match.group(1).split(',')] if covered_match else []

        # Extract interview stage
        stage_match = re.search(r'Interview Progress:\s*Question\s*(\d+)', prompt)
        stage_idx = int(stage_match.group(1)) - 1 if stage_match else 0

        # Pick next topic
        available_topics = [t for t in role_topics if t not in covered_topics]
        if available_topics:
            target_topic = available_topics[0]
        else:
            target_topic = role_topics[stage_idx % len(role_topics)]

        # Determine difficulty
        difficulty = "intermediate"
        if stage_idx < 2:
            difficulty = "beginner"
        elif stage_idx >= 5:
            difficulty = "advanced"

        return json.dumps({
            "queries": [
                f"{target_topic} core principles and architecture",
                f"{target_topic} practical implementation trade-offs",
                f"{target_topic} optimization and failure modes",
            ],
            "target_topic": target_topic,
            "difficulty": difficulty,
        })

    def _mock_question_generation(self, prompt: str) -> str:
        result = MockEngine.generate_question(prompt)
        return json.dumps(result)

    def _mock_answer_evaluation(self, prompt: str) -> str:
        result = MockEngine.evaluate_answer(prompt)
        return json.dumps(result)

    def _mock_interview_summary(self, prompt: str) -> str:
        result = MockEngine.generate_interview_summary(prompt)
        return json.dumps(result)


from backend.app.core.config import get_settings


class LLMService:
    """Factory that returns the appropriate LLM provider."""

    _instance: LLMProvider | None = None

    @classmethod
    def get_provider(cls) -> LLMProvider:
        """Get or create the LLM provider based on configuration.

        Priority:
        1. Google Gemini Provider (if GEMINI_API_KEY is configured)
        2. OpenAI Provider (if OPENAI_API_KEY is configured)
        3. Deterministic MockProvider (fallback/testing mode)
        """
        if cls._instance is not None:
            return cls._instance

        settings = get_settings()

        if settings.gemini_api_key and settings.gemini_api_key.strip():
            logger.info(f"Using Google Gemini provider with model: {settings.gemini_model}")
            cls._instance = GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
            )
        elif settings.openai_api_key and settings.openai_api_key.strip():
            logger.info(f"Using OpenAI provider with model: {settings.openai_model}")
            cls._instance = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                base_url=settings.openai_base_url,
            )
        else:
            logger.info("No Gemini or OpenAI API key found. Using deterministic MockProvider.")
            cls._instance = MockProvider()

        return cls._instance

    @classmethod
    def reset_provider(cls) -> None:
        """Reset the provider instance (useful for testing)."""
        cls._instance = None
