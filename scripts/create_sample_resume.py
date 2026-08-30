"""Script to generate a sample PDF resume for demo and testing."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import fitz  # PyMuPDF

def generate_sample_pdf(output_path: Path):
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)  # Standard letter

    content = """Alex Rivera
San Francisco, CA • alex.rivera@example.com • (555) 234-5678 • github.com/alexrivera

SUMMARY
Experienced Software & Machine Learning Engineer with 3+ years of experience in Natural Language
Processing, Predictive Modeling, and Full-Stack Backend Systems. Proven track record of developing
production ML pipelines and high-throughput REST APIs.

TECHNICAL SKILLS
• Programming: Python, SQL, JavaScript, Bash, TypeScript
• AI/ML: NLP, TF-IDF, Logistic Regression, Scikit-Learn, PyTorch, Transformers, HuggingFace, SpaCy, BERT
• Backend & Cloud: FastAPI, Flask, PostgreSQL, Redis, Docker, AWS (S3, EC2), Git, Linux, CI/CD

EXPERIENCE
Machine Learning Engineer — Apex Analytics (2022 - Present)
• Architected and deployed an end-to-end NLP classification pipeline processing 500k documents daily.
• Built predictive models using Scikit-Learn, Logistic Regression, and TF-IDF vectorization.
• Containerized inference microservices with Docker and deployed them to AWS EC2 using FastAPI.

PROJECTS
Fake News & Sentiment Detection System
• Developed a text classification engine utilizing TF-IDF representations and Logistic Regression models.
• Handled vocabulary drift and dataset imbalance using stratified evaluation and cross-validation metrics.
• Technologies: Python, Scikit-Learn, NLTK, FastAPI, Docker

E-Commerce Recommendation & Search API
• Designed a hybrid search API using vector embeddings and PostgreSQL full-text search.
• Reduced query latency by 45% using Redis caching and asynchronous request handlers.
• Technologies: Python, FastAPI, PostgreSQL, Redis, Sentence-Transformers

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley (2018 - 2022)
"""

    # Insert formatted text into PDF
    rect = fitz.Rect(54, 54, 558, 738)
    page.insert_textbox(rect, content, fontsize=11, fontname="helv", lineheight=1.3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    doc.close()
    print(f"✅ Created sample PDF resume at: {output_path}")

if __name__ == "__main__":
    target = PROJECT_ROOT / "data" / "sample_resume.pdf"
    generate_sample_pdf(target)
