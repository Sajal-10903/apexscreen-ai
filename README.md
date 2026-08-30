# ApexScreen AI — Role-Based Technical Interview & Screening Platform

> A production-grade, full-stack, RAG-grounded technical screening platform powered by **Google Gemini** (`gemini-3.6-flash`). Upload a candidate's resume, choose a technical role track, and conduct an adaptive, grounded, real-time interview complete with **granular resume-to-question provenance**, interactive **Recharts analytics**, question categorization, retry capabilities, anytime early termination, and multi-dimensional answer rubric evaluation.

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [UI Architecture & SaaS Design System](#2-ui-architecture--saas-design-system)
3. [Real Resume Traceability & Question Provenance](#3-real-resume-traceability--question-provenance)
4. [Curriculum & Resume Coverage Matrix](#4-curriculum--resume-coverage-matrix)
5. [Interactive Analytics Layer (Recharts)](#5-interactive-analytics-layer-recharts)
6. [Tech Stack](#6-tech-stack)
7. [Quickstart & Local Setup](#7-quickstart--local-setup)
8. [Environment Variables & Configuration](#8-environment-variables--configuration)
9. [Retry & Early-Termination Workflows](#9-retry--early-termination-workflows)
10. [RAG Retrieval Pipeline](#10-rag-retrieval-pipeline)
11. [Dynamic Scoring & Evaluation Rubric](#11-dynamic-scoring--evaluation-rubric)
12. [API Reference](#12-api-reference)
13. [Testing & Verification](#13-testing--verification)

---

## 1. Platform Overview

Traditional technical screening systems rely on static, memorized question banks and rigid regex keyword matchers. **ApexScreen AI** delivers an **adaptive, grounded technical interview experience** orchestrated dynamically across four data sources:

1. **Candidate Resume Context & Signal Extraction**: Candidate skills, frameworks, tools, and real-world project portfolios extracted from uploaded PDFs via `PyMuPDF` and structured LLM parsing.
2. **Real Resume Traceability & Provenance**: Every generated question is explicitly anchored to a specific item from the candidate's resume (e.g. `Resume → Projects → Fake News Detection System` or `Resume → Skills → PyTorch, NLP`).
3. **Role Curriculum & Track Progression**: Three specialized engineering roles (`AI/ML Engineer`, `Backend Engineer`, and `Data Scientist`) with progressive difficulty ladders and dynamic stage transitions.
4. **Curated Knowledge Base RAG**: Semantic vector retrieval powered by `sentence-transformers/all-MiniLM-L6-v2` embeddings and persistent **ChromaDB** collections.
5. **Adaptive Response History & Dynamic Difficulty Calibration**: Rolling performance evaluation that adjusts question difficulty and ensures topic diversity across rounds.

---

## 2. UI Architecture & SaaS Design System

The platform features a modern, human-designed SaaS interface:

```
┌───────────────────────────┬────────────────────────────────────────────────────────────────────────────┐
│ ✦ ApexScreen AI           │ Breadcrumbs: Screening Portal / AI/ML Track / Sajal Singh  [Gemini 3.6]   │
│   v2.5 Production         ├────────────────────────────────────────────────────────────────────────────┤
├───────────────────────────┤                                                                            │
│ 📊 Dashboard & Setup      │  ┌──────────────────────────────────────────────────────────────────────┐  │
│ 🎙️ Live Interview (LIVE)   │  │ 🚀 PROJECT-BASED QUESTION                                            │  │
│ 👤 Candidate Profile      │  │ Resume → Projects → Fake News & Sentiment Detection System          │  │
│ 🎯 Resume Coverage        │  │ Signals: PyTorch • TF-IDF • NLTK • BERT | Calibration: Intermediate   │  │
│ 📈 Analytics & Radar      │  └──────────────────────────────────────────────────────────────────────┘  │
│ 📋 Assessment Report      │                                                                            │
│                           │  In your Sentiment Detection system, explain how you approached loss       │
│ ───────────────────────── │  function optimization, handled class imbalance, and validated data drift. │
│ ⚙️ LLM: Gemini 3.6 Flash  │                                                                            │
│ 🗄️ ChromaDB: 3 Collections│  [ Candidate Answer Editor ............................................. ] │
│                           │  [ 🔄 Retry Question ]              [ Submit Answer for Evaluation → ]     │
└───────────────────────────┴────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Real Resume Traceability & Question Provenance

Every generated question provides explicit provenance so interviewers and candidates immediately understand why the question was asked:

```
┌────────────────────────────────────────────────────────┐
│ 🚀 PROJECT-BASED QUESTION                              │
│                                                        │
│ Resume → Projects → Fake News & Sentiment Detection    │
│ Skills Grounded: Python • PyTorch • TF-IDF • NLTK      │
│ Target Topic: Loss Function Optimization               │
│ Calibration: Intermediate (Adaptive Level 2)           │
│                                                        │
│ Question: How did you evaluate and optimize loss ... ? │
└────────────────────────────────────────────────────────┘
```

### Provenance Classification Taxonomy

| Source Type | Category Badge | Provenance Breadcrumb Example |
|---|---|---|
| `resume_project` | 🚀 **Projects** | `Resume → Projects → Fake News & Sentiment Detection System` |
| `resume_skill` | 🛠️ **Skills** | `Resume → Technical Skills → PyTorch, FastAPI, Redis` |
| `resume_education` | 🎓 **Education** | `Resume → Education → Bachelor of Computer Applications` |
| `resume_experience`| 💼 **Work Experience**| `Resume → Production Experience → System Scaling & CI/CD` |
| `resume_certification` | 📜 **Certifications** | `Resume → Certifications → AWS Solutions Architect` |
| `general_rag` | 🌐 **General Technical**| `General Technical → ChromaDB RAG: backend_engineering` |
| `performance_followup` | 🔍 **Follow-up Probe** | `Interview Calibration → Follow-up on Previous Response` |

---

## 4. Curriculum & Resume Coverage Matrix

The platform tracks and visualizes coverage across 8 core assessment categories:

- 🎓 **Introduction & Foundation**: Educational background and foundational engineering principles.
- 🚀 **Portfolio Projects**: Architectural dissection of candidate's real resume projects.
- 🛠️ **Core Skills & Stack**: Deep testing of languages, frameworks, and database technologies.
- 💼 **Work Experience**: Production systems, telemetry, debugging, and scaling under load.
- 📜 **Certifications & Standards**: Industry best practices, cloud architectures, and compliance.
- 💡 **Technical Concepts**: Mathematical and algorithmic depth grounded in ChromaDB vector store.
- 🌐 **System Design & APIs**: Distributed systems, database indexing, and API lifecycle.
- 🔍 **Follow-up Calibration**: Adaptive probing on trade-offs and edge cases.

---

## 5. Interactive Analytics Layer (Recharts)

The Analytics view provides rich visualizations bound to live interview data:

- **Competency Radar**: 4-factor scoring across Technical Accuracy, Completeness, Reasoning Depth, and Communication.
- **Score Progression Area Chart**: Rolling performance trajectory across questions ($Q_1 \to Q_n$).
- **Topic-wise Performance Bar Chart**: Granular score breakdowns across all tested technical domains.
- **Difficulty Calibration Chart**: Performance comparative analysis across Beginner, Intermediate, and Advanced stages.
- **Resume Category Distribution**: Visual breakdown of covered vs. pending curriculum domains.

---

## 6. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | FastAPI 0.115+ (Python 3.11+) | High-performance async REST API |
| **Frontend Framework** | React 18 + Vite 5 | Reactive component architecture and fast HMR |
| **Data Visualizations**| Recharts 2.15+ | Interactive SVG analytics, radar charts, area progression |
| **Icons & UI System**  | Lucide React + Design Tokens | Cohesive, elevated dark-space product aesthetics |
| **LLM Provider** | Google Gemini (`gemini-3.6-flash`) | Question generation, rubric scoring, summary synthesis |
| **Vector Database** | ChromaDB 0.6+ | Local persistent embedding storage |
| **Embedding Model** | `all-MiniLM-L6-v2` | Fast semantic vector search (384 dimensions) |
| **Relational Database** | SQLite + SQLAlchemy 2.0 | Session, question provenance, answers, and reports |
| **PDF Extraction** | PyMuPDF (`fitz`) | Robust resume parsing across layouts and columns |
| **Testing** | Pytest + Httpx + TestClient | 36 unit, integration, and E2E verification tests |

---

## 7. Quickstart & Local Setup

### 1. Backend Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment (.env)
```env
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY (or leave blank for deterministic mock mode)
```

### 3. Initialize Vectors & Knowledge Base
```bash
python scripts/ingest_knowledge.py
python scripts/verify_rag.py
```

### 4. Frontend Setup & Build
```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Launch Servers
In terminal 1 (Backend):
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

In terminal 2 (Frontend):
```bash
cd frontend && npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 8. Retry & Early-Termination Workflows

### 🔄 Retry Question Flow
1. Candidate submits an answer and receives rubric feedback.
2. Candidate clicks **"🔄 Retry Question (Refine Response)"**.
3. Textarea re-opens pre-populated with their text and an active **"Attempt #2"** badge.
4. Calling `POST /api/interviews/{session_id}/retry` resets evaluation state while preserving the same question ID and question index.
5. Re-submitting calls `POST /api/interviews/{session_id}/answers` with `is_retry=True`, updating the database answer and score in-place.

### ⏹️ End Interview Early Flow
1. Interviewer/Candidate clicks **"⏹ End Interview Early"** in top bar.
2. A confirmation modal displays how many questions have been answered.
3. Confirming calls `POST /api/interviews/{session_id}/finish`.
4. The backend marks the session as completed, sets `is_completed_early=1`, and synthesizes a final report strictly based on answered questions.

---

## 9. Dynamic Scoring & Evaluation Rubric

$$\text{Overall Score} = 0.40 \cdot \text{Technical} + 0.35 \cdot \text{Completeness} + 0.15 \cdot \text{Reasoning} + 0.10 \cdot \text{Communication}$$

- **Technical Accuracy (40%)**: Correctness of formulas, algorithms, architectural mechanisms, and technical terminology.
- **Completeness (35%)**: Coverage of expected concepts defined during question generation.
- **Reasoning & Depth (15%)**: Discussion of trade-offs, alternative approaches, and edge cases.
- **Communication Clarity (10%)**: Structured, articulate explanation with appropriate technical precision.

---

## 10. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health, LLM provider mode, and DB/ChromaDB status |
| `GET` | `/api/roles` | List available technical roles with topics and required skills |
| `POST` | `/api/resume/upload` | Upload PDF resume, extract text, and parse candidate skills/projects |
| `GET` | `/api/resume/{id}` | Retrieve candidate profile by ID |
| `POST` | `/api/interviews` | Create a new interview session and generate Question 1 with provenance |
| `GET` | `/api/interviews/{id}` | Get session status and question progression |
| `GET` | `/api/interviews/{id}/current-question` | Retrieve active question with full provenance and RAG traceability |
| `POST` | `/api/interviews/{id}/answers` | Submit response for rubric evaluation (`is_retry` supported) |
| `POST` | `/api/interviews/{id}/retry` | Reset active question for answer refinement |
| `POST` | `/api/interviews/{id}/finish` | End interview anytime and synthesize report |
| `POST` | `/api/interviews/{id}/next-question` | Advance to the next adaptive question with provenance |
| `GET` | `/api/interviews/{id}/results` | Fetch complete scorecard, provenance tags, coverage matrix, and analytics |

---

## 11. Testing & Verification

```bash
# Run all unit and integration tests (36 tests)
pytest backend/tests/ -q

# Test RAG vector search across all ChromaDB collections
python scripts/verify_rag.py

# Test live end-to-end flow with Gemini / adaptive engine / provenance
python scripts/test_live_e2e.py

# Build frontend production bundle
cd frontend && npm run build
```
