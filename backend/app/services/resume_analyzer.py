"""Resume analyzer: extracts structured candidate information.

Uses a hybrid approach:
1. Deterministic keyword matching and regex parser for reliable extraction
2. LLM-based extraction when available for deeper understanding
"""

import json
import logging
import re

logger = logging.getLogger(__name__)

# ─── Keyword dictionaries ────────────────────────────────

PROGRAMMING_LANGUAGES = {
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "julia", "perl", "haskell", "dart", "lua",
    "objective-c", "shell", "bash", "sql", "html", "css",
}

FRAMEWORKS = {
    "react", "angular", "vue", "vue.js", "next.js", "nextjs", "nuxt",
    "django", "flask", "fastapi", "express", "express.js", "spring",
    "spring boot", "rails", "ruby on rails", "laravel", ".net",
    "asp.net", "svelte", "gatsby", "remix", "nestjs", "gin",
    "streamlit", "gradio",
}

ML_TECHNOLOGIES = {
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "catboost", "hugging face", "huggingface",
    "transformers", "spacy", "nltk", "opencv", "pandas", "numpy",
    "scipy", "matplotlib", "seaborn", "plotly", "mlflow", "wandb",
    "dvc", "ray", "spark mllib", "langchain", "llamaindex",
    "sentence-transformers", "gensim", "onnx", "tensorrt",
    "tf-idf", "tfidf", "word2vec", "bert", "gpt", "llama",
    "stable diffusion", "yolo", "resnet", "lstm", "rnn", "cnn",
    "gan", "vae", "random forest", "logistic regression",
    "decision tree", "svm", "naive bayes", "k-means", "pca",
    "gradient boosting",
}

DATABASES = {
    "postgresql", "postgres", "mysql", "mongodb", "redis",
    "elasticsearch", "sqlite", "oracle", "sql server", "dynamodb",
    "cassandra", "neo4j", "firebase", "supabase", "cockroachdb",
    "influxdb", "clickhouse", "pinecone", "weaviate", "chromadb",
    "milvus", "qdrant", "faiss",
}

CLOUD_DEVOPS = {
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "k8s", "terraform", "ansible", "jenkins", "github actions",
    "gitlab ci", "ci/cd", "nginx", "apache", "linux", "heroku",
    "vercel", "netlify", "cloudflare", "prometheus", "grafana",
    "datadog", "sagemaker", "lambda", "ec2", "s3",
}

DOMAINS = {
    "machine learning", "deep learning", "artificial intelligence",
    "natural language processing", "nlp", "computer vision",
    "data science", "data engineering", "data analytics",
    "web development", "mobile development", "devops", "mlops",
    "cloud computing", "cybersecurity", "blockchain",
    "internet of things", "iot", "robotics", "embedded systems",
    "game development", "ar/vr", "bioinformatics",
}


def _match_keyword(kw: str, text_lower: str) -> bool:
    """Robust keyword matching with word boundary checking for short tokens."""
    kw_clean = kw.lower()
    if len(kw_clean) <= 3 or kw_clean in {"c", "r", "go", "gin", "lua", "sql", "aws", "gcp", "s3", "ec2"}:
        pattern = rf'(?:\b|(?<=[^a-z0-9])){re.escape(kw_clean)}(?:\b|(?=[^a-z0-9]))'
    else:
        pattern = rf'\b{re.escape(kw_clean)}\b'
    return bool(re.search(pattern, text_lower))


def analyze_resume_deterministic(resume_text: str) -> dict:
    """Extract structured information from resume text using robust keyword matching and section splitting."""
    text_lower = resume_text.lower()

    def find_matches(keywords: set[str]) -> list[str]:
        found = []
        for kw in keywords:
            if _match_keyword(kw, text_lower):
                found.append(kw.title() if len(kw) > 3 else kw.upper())
        return sorted(set(found))

    programming_languages = find_matches(PROGRAMMING_LANGUAGES)
    frameworks = find_matches(FRAMEWORKS)
    ai_ml_technologies = find_matches(ML_TECHNOLOGIES)
    databases = find_matches(DATABASES)
    cloud_devops = find_matches(CLOUD_DEVOPS)
    domains = find_matches(DOMAINS)

    all_skills = sorted(list(set(
        programming_languages + frameworks + ai_ml_technologies +
        databases + cloud_devops
    )))

    projects = _extract_projects(resume_text)
    education = _extract_education(resume_text)
    name = _extract_name(resume_text)
    email = _extract_email(resume_text)
    phone = _extract_phone(resume_text)
    experience_years = _extract_experience_years(resume_text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": all_skills,
        "programming_languages": programming_languages,
        "frameworks": frameworks,
        "databases": databases,
        "cloud_devops": cloud_devops,
        "ai_ml_technologies": ai_ml_technologies,
        "projects": projects,
        "education": education,
        "domains": domains,
        "experience_years": experience_years,
    }


def parse_llm_resume_analysis(llm_response: str) -> dict | None:
    """Parse the LLM's JSON response for resume analysis."""
    try:
        json_match = re.search(r'\{[\s\S]*\}', llm_response)
        if json_match:
            data = json.loads(json_match.group())
            required_keys = ["skills", "programming_languages", "frameworks"]
            if all(k in data for k in required_keys):
                return data
    except Exception as e:
        logger.warning(f"Failed to parse LLM resume analysis: {e}")

    return None


def merge_analyses(deterministic: dict, llm_result: dict | None) -> dict:
    """Merge deterministic and LLM analyses, ensuring name, skills, and projects are valid."""
    if llm_result is None:
        return deterministic

    merged = {}
    # Name: Ensure name is clean, single line, and not a generic title
    llm_name = (llm_result.get("name") or "").strip().split('\n')[0].strip()
    det_name = (deterministic.get("name") or "").strip().split('\n')[0].strip()
    
    invalid_name_terms = {"web development", "software engineer", "resume", "curriculum vitae", "developer", "engineer", "san francisco", "california", "summary"}
    if llm_name and not any(term in llm_name.lower() for term in invalid_name_terms):
        merged["name"] = re.sub(r'[^A-Za-z\s\.\-]', '', llm_name).strip()
    elif det_name and not any(term in det_name.lower() for term in invalid_name_terms):
        merged["name"] = re.sub(r'[^A-Za-z\s\.\-]', '', det_name).strip()
    else:
        merged["name"] = det_name or "Candidate"

    for key in ["email", "phone"]:
        llm_val = llm_result.get(key, "")
        det_val = deterministic.get(key, "")
        merged[key] = llm_val if llm_val else det_val

    merged["experience_years"] = (
        llm_result.get("experience_years")
        or deterministic.get("experience_years", 0)
    )

    list_keys = [
        "skills", "programming_languages", "frameworks", "databases",
        "cloud_devops", "ai_ml_technologies", "education", "domains",
    ]
    for key in list_keys:
        combined = set()
        for val in deterministic.get(key, []):
            combined.add(str(val).strip())
        for val in llm_result.get(key, []):
            combined.add(str(val).strip())
        merged[key] = sorted(v for v in combined if v)

    llm_projects = llm_result.get("projects", [])
    det_projects = deterministic.get("projects", [])
    merged["projects"] = llm_projects if llm_projects else det_projects

    return merged


# ─── Private Extraction Helpers ───────────────────────────

def _extract_name(text: str) -> str:
    """Extract candidate name from the top lines of the resume."""
    invalid_terms = [
        'resume', 'curriculum', 'cv', 'http', '@', '+', 'summary',
        'profile', 'contact', 'experience', 'education', 'skills',
        'web development', 'software engineer', 'machine learning',
        'data scientist', 'backend engineer', 'developer'
    ]
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:6]:
        line_lower = line.lower()
        if any(term in line_lower for term in invalid_terms):
            continue
        # Standard Person Name heuristic: 2 to 4 capitalized words, length between 3 and 35
        clean = re.sub(r'[^A-Za-z\s\.\-]', '', line).strip()
        words = clean.split()
        if 2 <= len(words) <= 4 and 4 <= len(clean) <= 40:
            if all(w[0].isupper() for w in words if w):
                return clean
    return lines[0] if lines else "Candidate"


def _extract_email(text: str) -> str:
    """Extract email address from text."""
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    return match.group() if match else ""


def _extract_phone(text: str) -> str:
    """Extract phone number from text."""
    match = re.search(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        text
    )
    return match.group() if match else ""


def _extract_experience_years(text: str) -> int:
    """Estimate years of experience from resume text."""
    match = re.search(r'(?:[-–—:]\s*|\b)(\d+)\+?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?(?:experience|exp))?', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


def _extract_projects(text: str) -> list[dict]:
    """Extract distinct projects and their specific tech stacks."""
    projects = []
    
    # Locate project section
    lines = text.split('\n')
    in_projects = False
    proj_lines = []

    for line in lines:
        l_str = line.strip()
        l_lower = l_str.lower()
        if any(h == l_lower or l_lower.startswith(('projects', 'technical projects', 'key projects', 'academic projects')) for h in ['projects', 'key projects', 'selected projects']):
            in_projects = True
            continue
        if in_projects and any(l_lower.startswith(h) for h in ['education', 'certifications', 'awards', 'languages', 'publications', 'references']):
            break
        if in_projects:
            proj_lines.append(l_str)

    if not proj_lines:
        return projects

    # Split projects by header lines (lines without bullet points or following blank lines)
    current_proj = None
    for line in proj_lines:
        if not line:
            continue
        
        # Check if line looks like a project title (short, no bullet prefix)
        is_bullet = line.startswith(('?', '•', '-', '*', '>', '–')) or line.startswith(('Developed', 'Architected', 'Built', 'Created', 'Designed', 'Handled', 'Reduced', 'Technologies:'))
        
        if not is_bullet and len(line) < 80 and not line.endswith('.'):
            if current_proj and current_proj["name"]:
                projects.append(current_proj)
            current_proj = {"name": line, "description": "", "technologies": []}
        else:
            if current_proj is None:
                current_proj = {"name": line[:60], "description": "", "technologies": []}
            else:
                current_proj["description"] += " " + line

    if current_proj and current_proj["name"]:
        projects.append(current_proj)

    # Extract technologies specifically mentioned inside each project
    for p in projects:
        desc_lower = (p["name"] + " " + p["description"]).lower()
        p_techs = []
        for kw_set in [PROGRAMMING_LANGUAGES, FRAMEWORKS, ML_TECHNOLOGIES, DATABASES, CLOUD_DEVOPS]:
            for kw in kw_set:
                if _match_keyword(kw, desc_lower):
                    p_techs.append(kw.title() if len(kw) > 3 else kw.upper())
        p["technologies"] = sorted(set(p_techs))
        p["description"] = re.sub(r'[\?\•\-\*]', '', p["description"]).strip()[:350]

    return projects[:6]


def _extract_education(text: str) -> list[str]:
    """Extract education degree and institution accurately."""
    education = []
    
    # Locate education section
    lines = text.split('\n')
    in_edu = False
    edu_lines = []

    for line in lines:
        l_str = line.strip()
        l_lower = l_str.lower()
        if any(l_lower == h or l_lower.startswith('education') for h in ['education', 'academic background', 'education & credentials']):
            in_edu = True
            continue
        if in_edu and any(l_lower.startswith(h) for h in ['experience', 'projects', 'skills', 'certifications']):
            break
        if in_edu and l_str:
            edu_lines.append(l_str)

    if edu_lines:
        combined = " - ".join(edu_lines[:3])
        education.append(combined[:120])
        return education

    # Fallback to regex degree patterns
    degree_patterns = [
        r"(?:Bachelor|Master|Doctor of Philosophy|Ph\.?D|B\.?S|M\.?S|B\.?Tech|M\.?Tech|B\.?E|B\.?C\.?A|M\.?C\.?A|M\.?B\.?A)\s+(?:of\s+[\w\s]+|in\s+[\w\s]+)?",
    ]
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.strip()[:100]
            if len(cleaned) > 5 and not any(term in cleaned.lower() for term in ['summary', 'engineer', 'developer']):
                education.append(cleaned)

    return education[:3]
