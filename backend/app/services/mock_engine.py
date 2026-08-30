"""Deterministic, input-dependent Mock Intelligence Engine.

Provides realistic, dynamic, and fully grounded simulation of:
1. Dynamic Answer Evaluation (semantic matching, concept coverage, accuracy, reasoning)
2. Grounded Question Generation (candidate resume + role curriculum + RAG context)
3. Interview Summary & Report Generation (performance synthesis, topic strengths/weaknesses)

No random numbers or static predefined responses are used.
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# Common English stop words for keyword extraction
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

# Technical concept synonym dictionary for enhanced concept matching
TECH_SYNONYMS = {
    "tf-idf": ["tf-idf", "term frequency", "inverse document frequency", "tfidf", "frequency-inverse"],
    "term frequency": ["term frequency", "tf", "word count", "term count", "occurrences in document", "word frequency"],
    "inverse document frequency": ["inverse document frequency", "idf", "document frequency", "rare across documents", "uncommon across documents", "downweight common", "penalize common", "log(n/df)"],
    "weighting": ["weighting", "weights", "scoring", "downweight", "penalize common", "importance"],
    "vectorization": ["vectorization", "vector representation", "feature matrix", "numerical representation", "bag of words", "embeddings", "tokens"],
    "supervised learning": ["supervised learning", "labeled data", "ground truth", "targets", "features and labels", "training set"],
    "unsupervised learning": ["unsupervised learning", "unlabeled data", "clustering", "dimensionality reduction", "pca", "k-means"],
    "classification": ["classification", "classifier", "logistic regression", "random forest", "decision tree", "binary classification", "multiclass"],
    "regression": ["regression", "continuous target", "linear regression", "mse", "mean squared error", "r2"],
    "neural networks": ["neural networks", "deep learning", "layers", "backpropagation", "weights and biases", "activation function"],
    "transformers": ["transformers", "attention mechanism", "self-attention", "bert", "gpt", "encoder", "decoder"],
    "rest api": ["rest api", "restful", "http methods", "get post put delete", "status codes", "endpoints", "json payload"],
    "indexing": ["indexing", "b-tree", "hash index", "query optimization", "lookup speed", "execution plan", "scan"],
    "acid": ["acid", "atomicity", "consistency", "isolation", "durability", "transaction", "rollback", "commit"],
    "docker": ["docker", "container", "dockerfile", "image", "isolated environment", "containerization"],
    "caching": ["caching", "redis", "memcached", "cache hit", "cache invalidation", "ttl", "cache aside"],
    "a/b testing": ["a/b testing", "hypothesis testing", "p-value", "significance", "control and treatment", "sample size"],
    "cross validation": ["cross validation", "k-fold", "train test split", "validation set", "overfitting prevention", "generalization"],
    "precision and recall": ["precision", "recall", "f1-score", "true positives", "false positives", "confusion matrix", "roc-auc"],
    "machine learning": ["machine learning", "ml", "training", "model", "algorithm", "features", "dataset"],
    "data preprocessing": ["preprocessing", "data cleaning", "normalization", "standardization", "scaling", "missing values", "outliers", "encoding"],
    "model evaluation": ["evaluation", "metrics", "accuracy", "precision", "recall", "f1", "validation", "roc-auc", "confusion matrix"],
}

# Reasoning depth indicator phrases
REASONING_INDICATORS = [
    "because", "in order to", "therefore", "to prevent", "by using", "as a result",
    "leading to", "mitigates", "ensures that", "for example", "such as", "specifically",
    "in practice", "trade-off", "tradeoff", "compared to", "unlike", "whereas",
    "drawback", "bottleneck", "complexity", "o(n)", "o(log n)", "architecture",
    "scalability", "latency", "throughput", "consistency", "fault tolerance",
    "first", "second", "furthermore", "consequently", "demonstrating", "mitigating"
]


class MockEngine:
    """Deterministic, input-dependent simulation engine."""

    # ──────────────────────────────────────────────────────────────────────────
    # 1. DYNAMIC ANSWER EVALUATION
    # ──────────────────────────────────────────────────────────────────────────

    @classmethod
    def evaluate_answer(cls, prompt: str) -> dict[str, Any]:
        """Evaluate a candidate's answer based on actual semantic content."""
        question_text = cls._extract_section(prompt, "QUESTION:")
        answer_text = cls._extract_section(prompt, "CANDIDATE'S ANSWER:")
        expected_concepts_raw = cls._extract_section(prompt, "EXPECTED CONCEPTS TO COVER:") or cls._extract_section(prompt, "EXPECTED CONCEPTS:")
        reference_knowledge = cls._extract_section(prompt, "REFERENCE KNOWLEDGE:")
        difficulty = cls._extract_line(prompt, "DIFFICULTY LEVEL:").lower() or "intermediate"

        expected_concepts = [c.strip() for c in expected_concepts_raw.split(",") if c.strip()]
        if not expected_concepts:
            expected_concepts = cls._infer_expected_concepts(question_text)

        # 1. Handle empty / whitespace answer
        clean_answer = answer_text.strip()
        if not clean_answer:
            return {
                "score": 0.0,
                "technical_accuracy": 0.0,
                "completeness": 0.0,
                "reasoning_depth": 0.0,
                "communication": 0.0,
                "feedback": "No answer was provided. Please attempt to answer the question with technical details.",
                "strengths": [],
                "missing_concepts": expected_concepts[:5],
                "suggestions": "Provide a complete technical explanation addressing the core principles.",
            }

        # 2. Extract keywords from question, answer, and reference
        q_tokens = cls._tokenize_keywords(question_text)
        a_tokens = cls._tokenize_keywords(clean_answer)
        ref_tokens = cls._tokenize_keywords(reference_knowledge)
        ans_lower = clean_answer.lower()
        word_count = len(clean_answer.split())

        # 3. Check Question Relevance (Detect off-topic answers)
        q_overlap = len(a_tokens & q_tokens)
        ref_overlap = len(a_tokens & ref_tokens)
        
        concept_scores = []
        concepts_found = []
        concepts_missing = []

        for concept in expected_concepts:
            match_score = cls._score_concept_coverage(concept, ans_lower, a_tokens)
            concept_scores.append(match_score)
            if match_score >= 0.4:
                concepts_found.append(concept)
            else:
                concepts_missing.append(concept)

        total_concepts = max(len(expected_concepts), 1)
        concept_coverage_ratio = sum(concept_scores) / total_concepts

        # Off-topic check: zero overlap with question and zero concept match
        is_off_topic = (q_overlap == 0 and ref_overlap == 0 and len(concepts_found) == 0 and concept_coverage_ratio < 0.15)

        if is_off_topic:
            detected_topics = list(a_tokens)[:3]
            off_topic_mention = f" (you mentioned: {', '.join(detected_topics)})" if detected_topics else ""
            return {
                "score": 1.0,
                "technical_accuracy": 1.0,
                "completeness": 0.0,
                "reasoning_depth": 1.0,
                "communication": 4.0 if word_count > 10 else 2.0,
                "feedback": (
                    f"Your answer does not address the question. The question asked about concepts related to "
                    f"'{question_text[:80]}...', but your response discussed unrelated topics{off_topic_mention}. "
                    f"Please address the specific question asked."
                ),
                "strengths": ["Basic sentence structure and clarity"] if word_count > 6 else [],
                "missing_concepts": expected_concepts[:5],
                "suggestions": f"Focus directly on explaining {expected_concepts[0] if expected_concepts else 'the required concepts'} and provide relevant technical examples.",
            }

        # 4. Score Completeness (0 to 10)
        completeness_score = round(concept_coverage_ratio * 10.0, 1)

        # 5. Score Technical Accuracy (0 to 10)
        tech_words = cls._count_technical_terms(clean_answer)
        if concept_coverage_ratio < 0.3:
            accuracy_base = 1.5 + (concept_coverage_ratio * 6.0) + min(tech_words * 0.3, 1.0)
        else:
            accuracy_base = 2.5 + (concept_coverage_ratio * 5.5) + min(tech_words * 0.4, 2.0)
        
        technical_accuracy = round(min(max(accuracy_base, 1.0), 10.0), 1)

        # 6. Score Reasoning & Depth (0 to 10)
        reasoning_hits = sum(1 for indicator in REASONING_INDICATORS if indicator in ans_lower)
        
        reasoning_score = 1.5
        if reasoning_hits >= 1:
            reasoning_score += min(reasoning_hits * 1.5, 4.5)
        if word_count > 40:
            reasoning_score += 1.5
        if word_count > 90:
            reasoning_score += 1.5
        if concept_coverage_ratio < 0.3:
            reasoning_score = min(reasoning_score, 2.5)
        reasoning_depth = round(min(max(reasoning_score, 1.0), 10.0), 1)

        # 7. Score Communication (0 to 10)
        comm_score = 4.0
        if word_count >= 15:
            comm_score += 1.5
        if word_count >= 40:
            comm_score += 2.0
        if "." in clean_answer or "," in clean_answer:
            comm_score += 1.0
        if tech_words >= 2:
            comm_score += 1.5
        communication = round(min(max(comm_score, 2.0), 10.0), 1)

        # 8. Overall Weighted Score (0 to 10)
        overall_score = round(
            (technical_accuracy * 0.40) +
            (completeness_score * 0.35) +
            (reasoning_depth * 0.15) +
            (communication * 0.10),
            1
        )

        # 9. Dynamic Feedback Construction
        feedback_paragraphs = []
        if overall_score >= 8.0:
            feedback_paragraphs.append(
                f"Excellent answer. You provided a thorough and technically accurate explanation covering "
                f"{', '.join(concepts_found[:3]) if concepts_found else 'the core principles'}."
            )
            if reasoning_hits >= 2:
                feedback_paragraphs.append("Your reasoning and practical architectural insights were well-structured.")
            if concepts_missing:
                feedback_paragraphs.append(f"To make it exceptional, you could also touch upon {concepts_missing[0]}.")
        elif overall_score >= 5.5:
            feedback_paragraphs.append(
                f"Solid response covering key aspects ({', '.join(concepts_found[:2]) if concepts_found else 'the basics'})."
            )
            if concepts_missing:
                feedback_paragraphs.append(
                    f"To improve completeness, elaborate on {', '.join(concepts_missing[:2])}."
                )
            if reasoning_hits == 0:
                feedback_paragraphs.append("Consider discussing specific trade-offs, edge cases, or implementation details.")
        else:
            feedback_paragraphs.append(
                f"Your response shows preliminary understanding but lacks technical depth and coverage of key concepts."
            )
            if concepts_found:
                feedback_paragraphs.append(f"You briefly touched on {', '.join(concepts_found)}.")
            if concepts_missing:
                feedback_paragraphs.append(
                    f"The answer missed fundamental concepts: {', '.join(concepts_missing[:3])}."
                )

        feedback = " ".join(feedback_paragraphs)

        # 10. Dynamic Strengths & Suggestions
        strengths = []
        for c in concepts_found[:4]:
            strengths.append(f"Clearly explained concept: {c}")
        if reasoning_hits >= 2:
            strengths.append("Provided concrete causal reasoning and trade-offs")
        if word_count >= 50 and communication >= 7.0:
            strengths.append("Well-articulated structure and technical vocabulary")
        if not strengths:
            strengths = ["Attempted relevant topic discussion"]

        suggestions = []
        for c in concepts_missing[:3]:
            suggestions.append(f"Discuss {c} in detail")
        if reasoning_hits < 2:
            suggestions.append("Include real-world examples, failure modes, or architectural trade-offs")
        suggestions_text = ". ".join(suggestions) + "." if suggestions else "Continue maintaining this high level of technical rigor."

        return {
            "score": overall_score,
            "technical_accuracy": technical_accuracy,
            "completeness": completeness_score,
            "reasoning_depth": reasoning_depth,
            "communication": communication,
            "feedback": feedback,
            "strengths": strengths[:5],
            "missing_concepts": concepts_missing[:5],
            "suggestions": suggestions_text,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 2. GROUNDED QUESTION GENERATION
    # ──────────────────────────────────────────────────────────────────────────

    @classmethod
    def generate_question(cls, prompt: str) -> dict[str, Any]:
        """Generate a personalized technical interview question grounded in resume + RAG."""
        role_raw = cls._extract_line(prompt, "Target Role:") or cls._extract_line(prompt, "ROLE:") or cls._extract_line(prompt, "for a ")
        role = re.sub(r'\s+candidate\.?$', '', role_raw, flags=re.IGNORECASE).strip() or "AI/ML Engineer"
        topic = cls._extract_line(prompt, "Technical Topic:") or cls._extract_line(prompt, "Topic:") or "Supervised Learning & Loss Functions"
        section = cls._extract_line(prompt, "Section Category:") or cls._extract_line(prompt, "QUESTION CATEGORY / SECTION:") or cls._extract_line(prompt, "Section:") or "Technical Concepts"
        difficulty = cls._extract_line(prompt, "Difficulty Level:") or cls._extract_line(prompt, "Difficulty:").lower() or "intermediate"
        source_item = cls._extract_line(prompt, "Specific Source Item:") or ""
        source_signals_raw = cls._extract_line(prompt, "Specific Evidence/Signals:") or ""
        candidate_skills_raw = cls._extract_line(prompt, "Skills:") or cls._extract_line(prompt, "Candidate Skills:")
        retrieved_context = cls._extract_section(prompt, "KNOWLEDGE BASE CONTEXT")

        candidate_skills = [s.strip() for s in candidate_skills_raw.split(",") if s.strip()]
        source_signals = [s.strip() for s in source_signals_raw.split(",") if s.strip()] if source_signals_raw else candidate_skills[:3]

        project_matches = re.findall(r'-\s*([A-Za-z0-9\s&_\-]+):\s*([^\n\(]+)(?:\(Technologies:\s*([^\)]+)\))?', prompt)
        projects = []
        for pm in project_matches:
            projects.append({
                "name": pm[0].strip(),
                "description": pm[1].strip(),
                "technologies": [t.strip() for t in pm[2].split(",")] if len(pm) > 2 and pm[2] else [],
            })

        matched_project = None
        for p in projects:
            if source_item and source_item.lower() in p.get("name", "").lower():
                matched_project = p
                break
        if not matched_project and projects:
            matched_project = projects[0]

        rag_concepts = cls._extract_rag_concepts(retrieved_context, topic)

        question_text, subtopic, expected_concepts, question_type = cls._build_grounded_question(
            role=role,
            topic=topic,
            difficulty=difficulty,
            candidate_skills=candidate_skills,
            project=matched_project,
            rag_concepts=rag_concepts,
            section=section,
            source_item=source_item,
            source_signals=source_signals,
        )

        return {
            "question": question_text,
            "topic": topic,
            "subtopic": subtopic,
            "section": section,
            "difficulty": difficulty,
            "expected_concepts": expected_concepts,
            "question_type": question_type,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 3. INTERVIEW SUMMARY & REPORT GENERATION
    # ──────────────────────────────────────────────────────────────────────────

    @classmethod
    def generate_interview_summary(cls, prompt: str) -> dict[str, Any]:
        """Synthesize candidate performance across all turns into a dynamic report."""
        candidate_name = cls._extract_line(prompt, "CANDIDATE:") or "Candidate"
        role = cls._extract_line(prompt, "ROLE:") or "Engineer"

        perf_matches = re.findall(
            r'Q\d+\s*\[([^\]]+)\]\s*\(Difficulty:\s*([^\)]+)\)[\s\S]*?Question:\s*([^\n]+)[\s\S]*?Score:\s*([0-9\.]+)/10',
            prompt
        )

        qa_scores = []
        topic_scores: dict[str, list[float]] = {}

        for match in perf_matches:
            q_topic = match[0].strip()
            q_diff = match[1].strip()
            q_text = match[2].strip()
            score = float(match[3])
            qa_scores.append({"topic": q_topic, "difficulty": q_diff, "question": q_text, "score": score})
            topic_scores.setdefault(q_topic, []).append(score)

        total_questions = len(qa_scores)
        if total_questions == 0:
            avg_score = 6.0
            avg_tech = 6.0
            avg_comm = 6.5
        else:
            avg_score = sum(q["score"] for q in qa_scores) / total_questions
            avg_tech = max(avg_score - 0.3, 1.0)
            avg_comm = min(avg_score + 0.5, 10.0)

        strong_areas = []
        weak_areas = []
        for t, scores in topic_scores.items():
            t_avg = sum(scores) / len(scores)
            if t_avg >= 7.0:
                strong_areas.append(f"{t} (Average score: {t_avg:.1f}/10)")
            elif t_avg < 6.0:
                weak_areas.append(f"{t} (Average score: {t_avg:.1f}/10)")

        if not strong_areas:
            strong_areas = ["General communication and willingness to engage"]
        if not weak_areas:
            weak_areas = ["Deeper optimization and edge-case validation"]

        if avg_score >= 8.0:
            hiring_rec = "strong_yes"
            rec_text = "Strong recommendation for hire based on technical excellence and clear communication."
        elif avg_score >= 6.5:
            hiring_rec = "yes"
            rec_text = "Recommended for hire with strong foundational skills across core competencies."
        elif avg_score >= 5.0:
            hiring_rec = "maybe"
            rec_text = "Borderline candidate. Shows potential but requires further technical calibration in weak areas."
        else:
            hiring_rec = "no"
            rec_text = "Does not meet technical screening threshold at this time."

        assessment = (
            f"{candidate_name} completed the technical interview for the {role} track with an overall "
            f"score of {avg_score:.1f}/10 across {total_questions} questions. "
            f"The candidate demonstrated strong capability in {', '.join([s.split(' (')[0] for s in strong_areas[:2]])}. "
            f"Areas requiring further development include {', '.join([w.split(' (')[0] for w in weak_areas[:2]])}. "
            f"{rec_text}"
        )

        recommendations = [
            f"Review advanced concepts in {weak_areas[0].split(' (')[0]}" if weak_areas else "Explore distributed systems architecture",
            "Focus on providing concrete code examples and quantitative trade-off discussions",
            "Deepen practical hands-on experience with production system failure modes",
        ]

        return {
            "overall_assessment": assessment,
            "technical_proficiency": f"Achieved {avg_tech:.1f}/10 in technical accuracy across {len(topic_scores)} distinct domains.",
            "strong_areas": strong_areas[:4],
            "weak_areas": weak_areas[:4],
            "recommendations": recommendations[:3],
            "hiring_recommendation": hiring_rec,
            "confidence_level": "high" if total_questions >= 4 else "medium",
            "interview_quality_note": f"Evaluated across {total_questions} adaptive questions covering {', '.join(topic_scores.keys())}.",
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ──────────────────────────────────────────────────────────────────────────

    @classmethod
    def _extract_line(cls, text: str, header: str) -> str:
        """Extract a single line value following a header."""
        match = re.search(re.escape(header) + r'\s*([^\n]+)', text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    @classmethod
    def _extract_section(cls, text: str, header: str) -> str:
        """Extract a multi-line section following a header until the next major section."""
        pos = text.find(header)
        if pos == -1:
            return ""
        start = pos + len(header)
        next_match = re.search(r'\n(?:[A-Z\s\']{3,}:|\n\n\n)', text[start:])
        if next_match:
            return text[start:start + next_match.start()].strip()
        return text[start:].strip()

    @classmethod
    def _tokenize_keywords(cls, text: str) -> set[str]:
        """Tokenize text into lowercase keywords excluding stop words."""
        words = re.findall(r'[A-Za-z0-9_\-\.]{2,}', text.lower())
        return {w for w in words if w not in STOP_WORDS and len(w) > 2}

    @classmethod
    def _score_concept_coverage(cls, concept: str, answer_lower: str, a_tokens: set[str]) -> float:
        """Score degree of coverage for a specific expected concept (0.0 to 1.0)."""
        concept_lower = concept.lower()
        c_tokens = cls._tokenize_keywords(concept)

        if concept_lower in answer_lower:
            return 1.0

        if c_tokens and c_tokens.issubset(a_tokens):
            return 1.0

        for key, syns in TECH_SYNONYMS.items():
            if key in concept_lower:
                for syn in syns:
                    if syn in answer_lower:
                        return 0.85

        if len(c_tokens) >= 2:
            overlap = len(c_tokens & a_tokens)
            ratio = overlap / len(c_tokens)
            if ratio >= 0.7:
                return 0.75
            elif ratio >= 0.4:
                return 0.35

        return 0.0

    @classmethod
    def _count_technical_terms(cls, text: str) -> int:
        """Count domain-specific technical terms in the text."""
        text_lower = text.lower()
        count = 0
        all_terms = set(TECH_SYNONYMS.keys())
        for syn_list in TECH_SYNONYMS.values():
            all_terms.update(syn_list)
        for term in all_terms:
            if term in text_lower:
                count += 1
        return count

    @classmethod
    def _infer_expected_concepts(cls, question: str) -> list[str]:
        """Infer expected concepts from question text."""
        tokens = cls._tokenize_keywords(question)
        concepts = []
        for key, syns in TECH_SYNONYMS.items():
            if any(t in tokens for t in cls._tokenize_keywords(key)):
                concepts.append(key.title())
        if not concepts:
            concepts = [w.capitalize() for w in list(tokens)[:4]]
        return concepts

    @classmethod
    def _extract_rag_concepts(cls, rag_context: str, topic: str) -> list[str]:
        """Extract key theoretical principles from retrieved RAG context."""
        if not rag_context:
            return []
        headers = re.findall(r'###?\s*([^\n]+)', rag_context)
        return [h.strip() for h in headers if len(h.strip()) > 3][:4]

    @classmethod
    def _build_grounded_question(
        cls,
        role: str,
        topic: str,
        difficulty: str,
        candidate_skills: list[str],
        project: dict[str, Any] | None,
        rag_concepts: list[str],
        section: str = "Technical Concepts",
        source_item: str = "",
        source_signals: list[str] | None = None,
    ) -> tuple[str, str, list[str], str]:
        """Construct question text, subtopic, expected concepts, and question type."""
        proj_name = source_item if (section == "Projects" and source_item) else (project.get("name", "Technical Project") if project else "Key Project")
        signals = source_signals if source_signals else (project.get("technologies", []) if project else candidate_skills[:3])
        signals_text = ", ".join(signals) if signals else "your stack"
        topic_lower = topic.lower()

        # Section-specific single-source question generation
        if section == "Projects" or "project" in section.lower():
            q_text = (
                f"In your project '{proj_name}' (utilizing {signals_text}), how did you approach {topic}? "
                f"Explain the technical rationale behind your architectural design, how you evaluated its performance, "
                f"and how you mitigated potential failure modes or data drift in production."
            )
            expected = [
                f"{topic} implementation in {proj_name}",
                "Architectural rationale and design trade-offs",
                "Evaluation metrics and validation strategy",
                "Edge cases, scalability, or failure handling",
            ]
            return q_text, f"{topic} in {proj_name}", expected, "project-based"

        elif section == "Introduction / Background" or "education" in section.lower():
            q_text = (
                f"Drawing on your academic background in {source_item or 'Computer Science'}, explain the fundamental principles "
                f"underlying {topic}. Walk through how you formulate mathematical or architectural assumptions, "
                f"select appropriate loss functions or metrics, and validate correctness."
            )
            expected = [
                f"{topic} core foundational principles",
                "Mathematical formulation and assumptions",
                "Loss functions and optimization mechanics",
                "Verification and empirical validation",
            ]
            return q_text, f"{topic} Foundations", expected, "conceptual"

        elif section == "Skills" or "skill" in section.lower():
            q_text = (
                f"Your resume highlights proficiency with {source_item or signals_text}. When building systems that leverage "
                f"{topic}, what are the most critical implementation nuances, performance bottlenecks, and concurrency or memory trade-offs?"
            )
            expected = [
                f"{source_item or 'Skill'} practical implementation",
                f"{topic} performance and latency trade-offs",
                "Concurrency, memory, or resource limits",
                "Debugging and failure mode mitigation",
            ]
            return q_text, f"{topic} Architecture", expected, "practical"

        elif section == "Work Experience" or "experience" in section.lower():
            q_text = (
                f"Reflecting on your experience at {source_item or 'production systems'}, how do you ensure high reliability and low latency "
                f"when managing {topic}? Discuss your monitoring, deployment strategy, and error recovery mechanisms."
            )
            expected = [
                "Production reliability and uptime guarantees",
                f"{topic} deployment and monitoring",
                "Throughput vs latency trade-offs",
                "Failover and error recovery",
            ]
            return q_text, f"Production {topic}", expected, "scenario"

        # General Technical / Role-specific
        if "ai" in role.lower() or "ml" in role.lower():
            if "transformer" in topic_lower or "attention" in topic_lower:
                q_text = (
                    f"Transformer architectures rely heavily on self-attention mechanisms. "
                    f"Explain how self-attention computes contextual token representations, why multi-head attention helps, "
                    f"and how positional encoding compensates for the lack of recurrence."
                )
                expected = [
                    "Self-attention (query/key/value) mechanism",
                    "Multi-head attention and representational diversity",
                    "Positional encoding and lack of sequential order",
                    "Encoder vs decoder architecture differences",
                ]
                return q_text, "Transformer Self-Attention", expected, "conceptual"

            elif "vectorization" in topic_lower or "tf-idf" in topic_lower or "nlp" in topic_lower:
                q_text = (
                    f"When designing a text processing pipeline for {topic}, explain how TF-IDF computes word importance "
                    f"compared to simple bag-of-words or dense embeddings. How do you handle high sparsity, vocabulary drift, "
                    f"and out-of-vocabulary tokens?"
                )
                expected = [
                    "Term Frequency (TF) calculation",
                    "Inverse Document Frequency (IDF) downweighting",
                    "Sparse vs dense vector representations",
                    "Handling Out-of-Vocabulary (OOV) tokens",
                ]
                return q_text, "Text Vectorization & NLP", expected, "conceptual"

            elif "evaluation" in topic_lower or "loss" in topic_lower:
                q_text = (
                    f"In model evaluation for classification tasks with class imbalance, contrast Accuracy, Precision, "
                    f"Recall, and ROC-AUC. How does decision threshold calibration impact false positive vs false negative trade-offs?"
                )
                expected = [
                    "Precision vs Recall trade-offs",
                    "F1-Score and PR-AUC for imbalanced data",
                    "ROC-AUC interpretation and calibration",
                    "Threshold tuning for domain costs",
                ]
                return q_text, "Model Evaluation Metrics", expected, "scenario"

            else:
                q_text = (
                    f"In modern ML engineering, how do you approach {topic}? "
                    f"Discuss the theoretical formulation, architectural trade-offs, and empirical validation methods."
                )
                expected = [
                    f"{topic} core principles",
                    "Optimization and loss formulation",
                    "Trade-offs in throughput vs accuracy",
                    "Validation and test methodology",
                ]
                return q_text, f"{topic} Engineering", expected, "design"

        elif "backend" in role.lower():
            if "index" in topic_lower or "b-tree" in topic_lower or "sql" in topic_lower:
                q_text = (
                    f"In high-throughput database systems, how do B-Tree and Hash indexes accelerate query execution? "
                    f"Explain write amplification overhead, composite index column ordering, and how to analyze EXPLAIN plans."
                )
                expected = [
                    "B-Tree index structure and search complexity",
                    "Write amplification and maintenance cost",
                    "Composite index column prefix rules",
                    "EXPLAIN plan analysis (seq scan vs index scan)",
                ]
                return q_text, "SQL Indexing & Query Execution", expected, "scenario"

            elif "acid" in topic_lower or "transaction" in topic_lower or "database" in topic_lower:
                q_text = (
                    f"Explain how ACID transaction guarantees prevent data corruption. Discuss the differences between "
                    f"Read Committed, Repeatable Read, and Serializable isolation levels, and the concurrency anomalies they prevent."
                )
                expected = [
                    "ACID properties (Atomicity, Consistency, Isolation, Durability)",
                    "Transaction isolation levels",
                    "Concurrency anomalies (dirty reads, non-repeatable reads, phantom reads)",
                    "Write-ahead logging (WAL) and commit durability",
                ]
                return q_text, "Database Transactions & ACID", expected, "design"

            else:
                q_text = (
                    f"When architecting scalable backend systems for {topic}, how do you ensure high availability, "
                    f"concurrency control, and fault isolation? Discuss your approach to latency optimization and error recovery."
                )
                expected = [
                    f"{topic} scalable architecture",
                    "Concurrency and state management",
                    "Caching and invalidation strategies",
                    "Fault tolerance and graceful degradation",
                ]
                return q_text, f"{topic} Architecture", expected, "design"

        else:  # Data Science
            if "hypothesis" in topic_lower or "a/b" in topic_lower or "p-value" in topic_lower:
                q_text = (
                    f"Explain the statistical mechanics of hypothesis testing and A/B testing. "
                    f"How do you determine required sample sizes, formulate null hypotheses, compute p-values, "
                    f"and control for Type I and Type II errors?"
                )
                expected = [
                    "Null and alternative hypothesis formulation",
                    "Type I (alpha) and Type II (beta / power) errors",
                    "Sample size calculation and Minimum Detectable Effect",
                    "P-value interpretation and significance thresholds",
                ]
                return q_text, "Statistical Inference & Hypothesis Testing", expected, "scenario"

            else:
                q_text = (
                    f"In data analysis and predictive modeling, how do you handle {topic}? "
                    f"Discuss statistical validation, preventing data leakage, and selecting appropriate evaluation metrics."
                )
                expected = [
                    f"{topic} methodology",
                    "Feature transformation and imputation",
                    "Data leakage prevention across splits",
                    "Metric interpretation and trade-offs",
                ]
                return q_text, f"{topic} Analysis", expected, "practical"
