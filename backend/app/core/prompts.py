"""Prompts for LLM-based operations in the AI Interview system."""


def resume_analysis_prompt(resume_text: str) -> str:
    """Prompt for extracting structured candidate information from resume text."""
    return f"""Analyze the following resume text and extract structured information.

RESUME TEXT:
{resume_text}

Extract and return a valid JSON object with the following schema:
{{
  "name": "Candidate Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "experience_years": 0,
  "skills": ["skill1", "skill2"],
  "programming_languages": ["Python", "JavaScript"],
  "frameworks": ["FastAPI", "React"],
  "databases": ["PostgreSQL", "Redis"],
  "cloud_devops": ["AWS", "Docker"],
  "ai_ml_technologies": ["PyTorch", "scikit-learn", "TF-IDF"],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description of what was built and achieved",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "education": ["Degree, Major, Institution, Graduation Year"],
  "domains": ["Machine Learning", "Backend"]
}}

Rules:
1. Extract the candidate's actual name accurately. Do NOT confuse job titles (like "Software Engineer" or "Web Development") with the person's name.
2. Only extract skills, technologies, and projects explicitly mentioned in the text.
3. For projects, identify the specific project title and only the technologies used in THAT project.
4. Estimate years of experience based on job dates or explicit statements.
5. Return ONLY the JSON object, no other text."""


def query_generation_prompt(
    candidate_skills: list[str],
    candidate_projects: list[dict],
    role: str,
    role_topics: list[str],
    interview_stage: int,
    total_questions: int,
    previous_topics: list[str] | None = None,
    current_topic: str | None = None,
    source_item: str | None = None,
    source_signals: list[str] | None = None,
) -> str:
    """Prompt for generating dynamic retrieval queries focused on the specific technical topic."""
    target_topic = current_topic or (role_topics[0] if role_topics else "Technical Architecture")
    signals_text = ", ".join(source_signals) if source_signals else ", ".join(candidate_skills[:4])

    return f"""Generate 3 focused textbook/technical search queries for an interview question.

ROLE: {role}
TOPIC TO RETRIEVE: {target_topic}
TARGET EVIDENCE / SIGNALS: {signals_text} ({source_item or 'Core Architecture'})
INTERVIEW STAGE: Question {interview_stage} of {total_questions}

Return a JSON object:
{{
  "queries": [
    "{target_topic} core algorithmic mechanics and formulas",
    "{target_topic} practical trade-offs and implementation considerations",
    "{target_topic} failure modes and validation techniques"
  ],
  "target_topic": "{target_topic}",
  "difficulty": "intermediate"
}}

Rules:
1. Make search queries highly specific to '{target_topic}'. Do NOT query broad generic terms.
2. Return ONLY valid JSON."""


def question_generation_prompt(
    candidate_skills: list[str],
    candidate_projects: list[dict],
    role: str,
    topic: str,
    difficulty: str,
    retrieved_context: str,
    interview_stage: int,
    total_questions: int,
    section: str = "Technical Concepts",
    candidate_education: list[str] | None = None,
    candidate_certifications: list[str] | None = None,
    candidate_experience: list[dict] | int | None = None,
    previous_qa: list[dict] | None = None,
    source_type: str = "general_rag",
    resume_section: str = "General Technical",
    source_item: str = "Curriculum Domain",
    source_signals: list[str] | None = None,
) -> str:
    """Prompt for generating a personalized, single-source grounded interview question."""
    signals_list = source_signals if source_signals else candidate_skills[:3]
    signals_text = ", ".join(signals_list)

    prev_qa_text = ""
    if previous_qa:
        for qa in previous_qa[-2:]:
            q_prev = qa.get('question_text') or qa.get('question', '')
            score_prev = qa.get('score', '')
            feedback_prev = qa.get('feedback', '')
            prev_qa_text += f"\nPrevious Q: {q_prev[:120]}... (Candidate Score: {score_prev}/10)"
            if feedback_prev:
                prev_qa_text += f"\nEvaluation Insight: {feedback_prev[:120]}..."

    return f"""Generate a high-quality, professional technical interview question for a {role} candidate.

=======================================================
QUESTION PROVENANCE & GROUNDING (SINGLE SOURCE):
- Section Category: {section}
- Resume Section: {resume_section}
- Specific Source Item: {source_item}
- Specific Evidence/Signals: {signals_text}
- Technical Topic: {topic}
- Difficulty Level: {difficulty}
- Stage: Question {interview_stage} of {total_questions}
=======================================================

KNOWLEDGE BASE CONTEXT (Reference material for grounding):
{retrieved_context[:1800]}

{f"PREVIOUS INTERVIEW TURNS:{prev_qa_text}" if prev_qa_text else ""}

STRICT GENERATION RULES:
1. FOCUS ON ONE RESUME SOURCE:
   - If Section is "Projects": Reference the actual project '{source_item}' and its specific tech ({signals_text}). Ask why they made specific architectural choices, how they solved key engineering bottlenecks, or how they evaluated {topic}.
   - If Section is "Skills": Isolate the skill '{source_item}' and test deep technical nuances, failure modes, or performance trade-offs in {topic}.
   - If Section is "Introduction / Background" or "Education": Connect their academic foundation '{source_item}' to core {topic} principles.
   - If Section is "General Technical" or "Technical Concepts": Ask a rigorous design/systems question on {topic} grounded in the knowledge base.
2. DO NOT COMBINE UNRELATED SKILLS:
   - NEVER dump random unrelated skills into one question (e.g. do NOT say "Based on AWS, Data Structures, Flask, GIN, explain Machine Learning...").
   - Only mention technologies that genuinely belong to '{source_item}'.
3. ALIGN METADATA AND QUESTION:
   - The question must directly test '{topic}' using the provided context.
4. ADAPTIVE CALIBRATION:
   - Difficulty is '{difficulty}'. Ensure the question complexity matches this level.

Return a JSON object:
{{
  "question": "The full, professional question text directly addressing the candidate",
  "topic": "{topic}",
  "subtopic": "Specific subtopic tested",
  "section": "{section}",
  "difficulty": "{difficulty}",
  "expected_concepts": ["concept 1", "concept 2", "concept 3", "concept 4"],
  "question_type": "project-based|practical|conceptual|scenario|design"
}}"""


def answer_evaluation_prompt(
    question: str,
    answer: str,
    expected_concepts: list[str],
    retrieved_context: str,
    difficulty: str,
) -> str:
    """Prompt for evaluating a candidate's answer against the multi-factor rubric."""
    return f"""Evaluate the following interview answer according to the standardized rubric.

QUESTION:
{question}

EXPECTED CONCEPTS TO COVER:
{', '.join(expected_concepts)}

CANDIDATE'S ANSWER:
{answer}

REFERENCE KNOWLEDGE:
{retrieved_context[:1500]}

DIFFICULTY LEVEL: {difficulty}

RUBRIC (Score each component from 0.0 to 10.0):
1. Technical Accuracy (40% weight): Are technical claims, formulas, and architectures correct?
2. Completeness (35% weight): Did the answer cover the expected concepts and address all parts of the question?
3. Reasoning Depth (15% weight): Did the candidate explain *why*, analyze trade-offs, or discuss real-world constraints?
4. Communication (10% weight): Is the answer articulate, well-structured, and concise?

Overall score = 0.40 * Technical + 0.35 * Completeness + 0.15 * Reasoning + 0.10 * Communication.

Return a JSON object:
{{
  "score": 0.0,
  "technical_accuracy": 0.0,
  "completeness": 0.0,
  "reasoning_depth": 0.0,
  "communication": 0.0,
  "feedback": "Detailed constructive evaluation of what was strong and what was lacking",
  "strengths": ["Demonstrated competency 1", "Demonstrated competency 2"],
  "missing_concepts": ["Missing concept 1", "Missing concept 2"],
  "suggestions": "Actionable advice to improve technical depth"
}}"""


def interview_summary_prompt(
    candidate_name: str,
    role: str,
    qa_history: list[dict] | None = None,
    covered_topics: list[str] | None = None,
    questions_and_answers: list[dict] | None = None,
    overall_scores: dict | None = None,
    is_completed_early: bool = False,
) -> str:
    """Prompt for generating the final comprehensive interview synthesis and hiring recommendation."""
    history = questions_and_answers or qa_history or []
    topics = covered_topics or list(set(qa.get("topic", "General") for qa in history))
    qa_text = ""
    for i, qa in enumerate(history, 1):
        q = qa.get('question_text') or qa.get('question', '')
        a = qa.get('answer_text') or qa.get('answer', '')
        score = qa.get('score', 0)
        topic = qa.get('topic', 'General')
        diff = qa.get('difficulty', 'intermediate')
        qa_text += f"\n--- Turn {i} [{topic}] (Difficulty: {diff}) ---\n"
        qa_text += f"Q: {q}\n"
        qa_text += f"A: {a[:250]}...\n"
        qa_text += f"Score: {score}/10\n"

    status_note = "NOTE: Candidate completed early. Base assessment strictly on answered questions." if is_completed_early else ""

    return f"""Synthesize the technical interview results into a comprehensive evaluation report.

CANDIDATE: {candidate_name}
TARGET ROLE: {role}
QUESTIONS COMPLETED: {len(history)}
COVERED TOPICS: {', '.join(topics)}
{status_note}

INTERVIEW TRANSCRIPT & SCORES:
{qa_text}

Generate an executive assessment with:
1. Overall performance synthesis
2. Specific verified strengths
3. Specific areas needing technical growth
4. Strategic hiring recommendation: "strong_yes" | "yes" | "maybe" | "no"

Return a JSON object:
{{
  "overall_assessment": "Comprehensive 2-3 paragraph executive summary of technical competency",
  "technical_proficiency": "Detailed breakdown of technical accuracy and architecture capabilities",
  "strong_areas": ["Demonstrated strength 1", "Demonstrated strength 2"],
  "weak_areas": ["Area needing improvement 1", "Area needing improvement 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "hiring_recommendation": "strong_yes|yes|maybe|no",
  "confidence_level": "high|medium|low",
  "interview_quality_note": "Summary of coverage and difficulty trajectory"
}}"""
