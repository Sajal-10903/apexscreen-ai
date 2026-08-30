"""Role configuration defining specific technical topics, skills, and knowledge collections per role."""

ROLE_CONFIGS: dict[str, dict] = {
    "ai_ml_engineer": {
        "id": "ai_ml_engineer",
        "name": "AI/ML Engineer",
        "description": "Design, build, and deploy machine learning models, NLP pipelines, and AI systems.",
        "icon": "🤖",
        "collection": "ai_ml",
        "topics": [
            "Supervised Learning & Loss Functions",
            "Text Vectorization & TF-IDF",
            "Model Evaluation & Generalization",
            "Feature Engineering & Preprocessing",
            "Deep Learning & Gradient Flow",
            "Transformer Self-Attention Mechanisms",
            "Model Quantization & Inference Latency",
            "Production ML Pipeline Architecture",
        ],
        "expected_skills": [
            "Python", "PyTorch", "TensorFlow", "scikit-learn", "Transformers",
            "NLP", "TF-IDF", "BERT", "MLOps", "Model Evaluation",
            "Feature Engineering", "FastAPI", "Docker",
        ],
        "difficulty_areas": {
            "beginner": [
                "Supervised Learning & Loss Functions",
                "Text Vectorization & TF-IDF",
                "Feature Engineering & Preprocessing",
            ],
            "intermediate": [
                "Model Evaluation & Generalization",
                "Deep Learning & Gradient Flow",
                "Production ML Pipeline Architecture",
            ],
            "advanced": [
                "Transformer Self-Attention Mechanisms",
                "Model Quantization & Inference Latency",
            ],
        },
        "question_categories": [
            "conceptual", "practical", "scenario",
            "project-based", "troubleshooting", "design",
        ],
    },
    "backend_engineer": {
        "id": "backend_engineer",
        "name": "Backend Engineer",
        "description": "Build scalable server-side applications, high-throughput APIs, and reliable data systems.",
        "icon": "⚙️",
        "collection": "backend",
        "topics": [
            "REST API Design & Idempotency",
            "Database Indexing & B-Trees",
            "ACID Transactions & Isolation Levels",
            "Asynchronous Concurrency & FastAPIs",
            "Docker Container Optimization",
            "Distributed Caching & Cache Invalidation",
            "Message Queues & Event-Driven Architecture",
            "System Scalability & Microservices",
        ],
        "expected_skills": [
            "Python", "FastAPI", "PostgreSQL", "Redis", "Docker",
            "SQL", "REST", "Git", "Linux", "AWS", "System Design",
            "AsyncIO", "Microservices",
        ],
        "difficulty_areas": {
            "beginner": [
                "REST API Design & Idempotency",
                "Database Indexing & B-Trees",
            ],
            "intermediate": [
                "ACID Transactions & Isolation Levels",
                "Asynchronous Concurrency & FastAPIs",
                "Docker Container Optimization",
                "Distributed Caching & Cache Invalidation",
            ],
            "advanced": [
                "Message Queues & Event-Driven Architecture",
                "System Scalability & Microservices",
            ],
        },
        "question_categories": [
            "conceptual", "practical", "scenario",
            "project-based", "troubleshooting", "design",
        ],
    },
    "data_scientist": {
        "id": "data_scientist",
        "name": "Data Scientist",
        "description": "Extract actionable insights using rigorous statistics, predictive modeling, and analytics.",
        "icon": "📊",
        "collection": "data_science",
        "topics": [
            "Hypothesis Testing & p-value Analysis",
            "Exploratory Data Analysis & Imputation",
            "Regression Analysis & Residuals",
            "A/B Testing & Statistical Significance",
            "Feature Selection & Multicollinearity",
            "Classification Metrics & ROC-AUC",
            "Time Series Decomposition & Stationarity",
            "SQL Analytical Queries & Window Functions",
        ],
        "expected_skills": [
            "Python", "pandas", "numpy", "scikit-learn", "SQL",
            "Statistics", "Hypothesis Testing", "A/B Testing",
            "Data Visualization", "Feature Engineering", "R",
        ],
        "difficulty_areas": {
            "beginner": [
                "Exploratory Data Analysis & Imputation",
                "SQL Analytical Queries & Window Functions",
            ],
            "intermediate": [
                "Hypothesis Testing & p-value Analysis",
                "Regression Analysis & Residuals",
                "Classification Metrics & ROC-AUC",
                "Feature Selection & Multicollinearity",
            ],
            "advanced": [
                "A/B Testing & Statistical Significance",
                "Time Series Decomposition & Stationarity",
            ],
        },
        "question_categories": [
            "conceptual", "practical", "scenario",
            "project-based", "troubleshooting", "design",
        ],
    },
}


def get_role_config(role_id: str) -> dict | None:
    """Get configuration for a specific role."""
    return ROLE_CONFIGS.get(role_id)


def get_all_roles() -> list[dict]:
    """Get all available roles."""
    return [
        {
            "id": cfg["id"],
            "name": cfg["name"],
            "description": cfg["description"],
            "topics": cfg["topics"],
            "expected_skills": cfg["expected_skills"],
            "icon": cfg["icon"],
        }
        for cfg in ROLE_CONFIGS.values()
    ]


def get_role_ids() -> list[str]:
    """Get list of valid role IDs."""
    return list(ROLE_CONFIGS.keys())


def get_difficulty_for_stage(
    role_id: str, stage: int, total: int, avg_score: float | None = None
) -> str:
    """Determine question difficulty based on interview stage and candidate performance."""
    progress = stage / total if total > 0 else 0

    if progress < 0.25:
        base = "beginner"
    elif progress < 0.70:
        base = "intermediate"
    else:
        base = "advanced"

    if avg_score is not None:
        if avg_score >= 8.0 and base != "advanced":
            levels = ["beginner", "intermediate", "advanced"]
            idx = levels.index(base)
            base = levels[min(idx + 1, 2)]
        elif avg_score <= 4.0 and base != "beginner":
            levels = ["beginner", "intermediate", "advanced"]
            idx = levels.index(base)
            base = levels[max(idx - 1, 0)]

    return base


def get_topic_for_stage(
    role_id: str, stage: int, total: int, covered_topics: list[str] | None = None,
    difficulty: str = "intermediate",
) -> str:
    """Select a specific topic for the given interview stage, avoiding repetition."""
    config = ROLE_CONFIGS.get(role_id)
    if not config:
        return "General Technical Architecture"

    difficulty_topics = config["difficulty_areas"].get(difficulty, config["topics"])
    all_topics = config["topics"]

    covered = set(covered_topics or [])
    uncovered_diff = [t for t in difficulty_topics if t not in covered]
    uncovered_all = [t for t in all_topics if t not in covered]

    if uncovered_diff:
        return uncovered_diff[stage % len(uncovered_diff)]
    elif uncovered_all:
        return uncovered_all[stage % len(uncovered_all)]
    else:
        return all_topics[stage % len(all_topics)]


QUESTION_SECTIONS: list[str] = [
    "Introduction / Background",
    "Projects",
    "Skills",
    "Work Experience",
    "Certifications",
    "Technical Concepts",
    "General Technical",
    "Follow-up / Performance Based",
]


def get_section_for_stage(
    stage: int,
    total: int,
    candidate_profile: dict | None = None,
    previous_qa: list[dict] | None = None,
) -> str:
    """Determine question section/category."""
    prov = get_provenance_for_stage(stage, total, candidate_profile, previous_qa)
    return prov["section"]


def get_provenance_for_stage(
    stage: int,
    total: int,
    candidate_profile: dict | None = None,
    previous_qa: list[dict] | None = None,
    topic: str = "General",
) -> dict:
    """Compute exact single-source provenance metadata and isolated resume grounding."""
    profile = candidate_profile or {}
    projects = profile.get("projects", [])
    skills = profile.get("skills", []) or profile.get("programming_languages", [])
    certs = profile.get("certifications", [])
    edu = profile.get("education", [])
    exp = profile.get("experience", []) or profile.get("experience_years", 0)

    # 1. Stage 0 (Question 1): Background & Foundation (Education)
    if stage == 0:
        edu_item = edu[0] if edu else "Computer Science & Engineering Foundation"
        clean_edu_name = edu_item.split(" - ")[0] if " - " in edu_item else edu_item
        edu_signals = [clean_edu_name]
        if skills:
            # Pick only 1 primary foundational language
            for core in ["Python", "Java", "C++", "SQL", "JavaScript"]:
                if core in skills:
                    edu_signals.append(core)
                    break
        return {
            "section": "Introduction / Background",
            "resume_section": "Education" if edu else "Introduction / Background",
            "source_type": "resume_education" if edu else "resume_background",
            "source_item": clean_edu_name,
            "source_signals": edu_signals,
        }

    # 2. Stage 1 (Question 2): Primary Project Deep Dive
    if stage == 1 and projects:
        proj = projects[0]
        p_name = proj.get("name", "Key Technical Project")
        p_techs = proj.get("technologies", [])
        return {
            "section": "Projects",
            "resume_section": "Projects",
            "source_type": "resume_project",
            "source_item": p_name,
            "source_signals": p_techs[:4] if p_techs else ["Python", "Core Architecture"],
        }

    # 3. Stage 2 (Question 3): Core Skill Proficiency
    if stage == 2 and skills:
        # Pick a single distinct skill for this question
        target_skill = skills[min(len(skills) - 1, 2)]
        return {
            "section": "Skills",
            "resume_section": "Skills",
            "source_type": "resume_skill",
            "source_item": target_skill,
            "source_signals": [target_skill],
        }

    # 4. Stage 3 (Question 4): Work Experience or Secondary Project
    if stage == 3:
        if (isinstance(exp, list) and len(exp) > 0) or (isinstance(exp, (int, float)) and exp > 0):
            exp_item = exp[0].get("company", "Production Engineering") if isinstance(exp, list) and isinstance(exp[0], dict) else "Production Systems & Engineering"
            return {
                "section": "Work Experience",
                "resume_section": "Work Experience",
                "source_type": "resume_experience",
                "source_item": exp_item,
                "source_signals": ["System Reliability", "Production Scaling", "CI/CD"],
            }
        elif len(projects) > 1:
            p2 = projects[1]
            return {
                "section": "Projects",
                "resume_section": "Projects",
                "source_type": "resume_project",
                "source_item": p2.get("name", "Secondary Technical Project"),
                "source_signals": p2.get("technologies", ["Python", "FastAPI"])[:4],
            }
        return {
            "section": "Technical Concepts",
            "resume_section": "General Technical",
            "source_type": "general_rag",
            "source_item": f"Knowledge Base: {topic}",
            "source_signals": [topic],
        }

    # 5. Stage 4 (Question 5): Certifications or Technical Concepts
    if stage == 4:
        if certs and len(certs) > 0:
            return {
                "section": "Certifications",
                "resume_section": "Certifications",
                "source_type": "resume_certification",
                "source_item": certs[0],
                "source_signals": [certs[0]],
            }
        return {
            "section": "Technical Concepts",
            "resume_section": "General Technical",
            "source_type": "general_rag",
            "source_item": f"Knowledge Base: {topic}",
            "source_signals": [topic],
        }

    # 6. Later Stage: Follow-up / Performance Based
    if previous_qa and len(previous_qa) >= 3 and stage == max(0, total - 2):
        return {
            "section": "Follow-up / Performance Based",
            "resume_section": "Follow-up / Performance Based",
            "source_type": "performance_followup",
            "source_item": "Response Calibration & Edge Cases",
            "source_signals": ["Trade-off Analysis", "Failure Modes", "Optimization"],
        }

    # 7. Remaining Stages: General Technical
    return {
        "section": "General Technical",
        "resume_section": "General Technical",
        "source_type": "general_rag",
        "source_item": f"Knowledge Base: {topic}",
        "source_signals": [topic],
    }
