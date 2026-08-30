"""Resume upload and processing API."""

import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.rate_limit import check_rate_limit
from backend.app.models.database import get_db
from backend.app.models.candidate import Candidate
from backend.app.models.schemas import ResumeUploadResponse
from backend.app.services.resume_parser import parse_pdf, parse_text_resume
from backend.app.services.resume_analyzer import (
    analyze_resume_deterministic,
    parse_llm_resume_analysis,
    merge_analyses,
)
from backend.app.services.llm_service import LLMService
from backend.app.core.prompts import resume_analysis_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume"])

ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a resume file.

    Validates the file, extracts text, analyzes skills/projects,
    and stores the candidate profile.
    """
    settings = get_settings()
    check_rate_limit(request, "resume_upload", settings.rate_limit_upload_per_minute)

    # ── Validate file ──
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Sanitize filename
    safe_filename = _sanitize_filename(file.filename)
    ext = Path(safe_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Reject oversized uploads early using the declared Content-Length header
    # (in addition to the post-read size check below) to avoid buffering
    # arbitrarily large request bodies into memory.
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit():
        if int(content_length) > settings.max_resume_size_bytes * 2:
            # *2 accounts for multipart overhead/boundaries around the file part.
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_resume_size_mb}MB",
            )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.max_resume_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_resume_size_mb}MB",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Validate PDF magic bytes so a renamed non-PDF file can't reach the parser.
    if not contents.lstrip()[:5].startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="File does not appear to be a valid PDF (missing %PDF header).",
        )

    # ── Save file ──
    candidate_id = str(uuid.uuid4())
    upload_dir = settings.upload_directory
    file_path = upload_dir / f"{candidate_id}{ext}"

    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except IOError as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    # ── Parse resume ──
    try:
        resume_text = parse_pdf(str(file_path))
    except ValueError as e:
        # Clean up the file
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        file_path.unlink(missing_ok=True)
        logger.error(f"Resume parsing error: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse resume. Please upload a valid PDF.")

    if not resume_text.strip():
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="No text could be extracted from the resume")

    # ── Analyze resume ──
    # 1. Deterministic extraction (always runs)
    deterministic_result = analyze_resume_deterministic(resume_text)

    # 2. LLM extraction (if available)
    llm_result = None
    try:
        llm = LLMService.get_provider()
        prompt = resume_analysis_prompt(resume_text[:5000])  # Limit text length
        response = llm.generate(prompt, temperature=0.2)
        llm_result = parse_llm_resume_analysis(response)
    except Exception as e:
        logger.warning(f"LLM resume analysis failed, using deterministic only: {e}")

    # 3. Merge results
    analysis = merge_analyses(deterministic_result, llm_result)

    # ── Store candidate ──
    candidate = Candidate(
        id=candidate_id,
        name=analysis.get("name", ""),
        email=analysis.get("email", ""),
        phone=analysis.get("phone", ""),
        resume_filename=safe_filename,
        resume_text=resume_text[:50000],  # Limit stored text
        experience_years=analysis.get("experience_years", 0),
    )
    candidate.skills = analysis.get("skills", [])
    candidate.programming_languages = analysis.get("programming_languages", [])
    candidate.frameworks = analysis.get("frameworks", [])
    candidate.databases_list = analysis.get("databases", [])
    candidate.cloud_devops = analysis.get("cloud_devops", [])
    candidate.ai_ml_technologies = analysis.get("ai_ml_technologies", [])
    candidate.projects = analysis.get("projects", [])
    candidate.education = analysis.get("education", [])
    candidate.domains = analysis.get("domains", [])

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    logger.info(f"Candidate created: {candidate_id}, skills found: {len(candidate.all_skills)}")

    return ResumeUploadResponse(
        candidate_id=candidate.id,
        name=candidate.name,
        skills=candidate.skills,
        programming_languages=candidate.programming_languages,
        frameworks=candidate.frameworks,
        databases=candidate.databases_list,
        cloud_devops=candidate.cloud_devops,
        ai_ml_technologies=candidate.ai_ml_technologies,
        projects=candidate.projects,
        education=candidate.education,
        domains=candidate.domains,
        experience_years=candidate.experience_years,
    )


@router.get("/{candidate_id}", response_model=ResumeUploadResponse)
def get_candidate_profile(
    candidate_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve an extracted candidate profile by candidate ID."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return ResumeUploadResponse(
        candidate_id=candidate.id,
        name=candidate.name,
        skills=candidate.skills,
        programming_languages=candidate.programming_languages,
        frameworks=candidate.frameworks,
        databases=candidate.databases_list,
        cloud_devops=candidate.cloud_devops,
        ai_ml_technologies=candidate.ai_ml_technologies,
        projects=candidate.projects,
        education=candidate.education,
        domains=candidate.domains,
        experience_years=candidate.experience_years,
    )


def _sanitize_filename(filename: str) -> str:
    """Sanitize an uploaded filename to prevent path traversal."""
    # Take only the basename
    name = os.path.basename(filename)
    # Remove any path separators that might remain
    name = name.replace('/', '').replace('\\', '')
    # Remove null bytes
    name = name.replace('\x00', '')
    if not name:
        name = "upload.pdf"
    return name
