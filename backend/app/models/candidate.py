"""Candidate ORM model."""

import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer
from backend.app.models.database import Base


class Candidate(Base):
    """Stores parsed resume data and candidate profile."""

    __tablename__ = "candidates"

    id = Column(String, primary_key=True)
    name = Column(String, default="")
    email = Column(String, default="")
    phone = Column(String, default="")
    resume_filename = Column(String, nullable=False)
    resume_text = Column(Text, default="")

    # Structured extracted data stored as JSON strings
    skills_json = Column(Text, default="[]")
    programming_languages_json = Column(Text, default="[]")
    frameworks_json = Column(Text, default="[]")
    databases_json = Column(Text, default="[]")
    cloud_devops_json = Column(Text, default="[]")
    ai_ml_technologies_json = Column(Text, default="[]")
    projects_json = Column(Text, default="[]")
    education_json = Column(Text, default="[]")
    domains_json = Column(Text, default="[]")

    experience_years = Column(Integer, default=0)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # --- Convenience properties ---
    @property
    def skills(self) -> list[str]:
        return json.loads(self.skills_json) if self.skills_json else []

    @skills.setter
    def skills(self, value: list[str]):
        self.skills_json = json.dumps(value)

    @property
    def programming_languages(self) -> list[str]:
        return json.loads(self.programming_languages_json) if self.programming_languages_json else []

    @programming_languages.setter
    def programming_languages(self, value: list[str]):
        self.programming_languages_json = json.dumps(value)

    @property
    def frameworks(self) -> list[str]:
        return json.loads(self.frameworks_json) if self.frameworks_json else []

    @frameworks.setter
    def frameworks(self, value: list[str]):
        self.frameworks_json = json.dumps(value)

    @property
    def databases_list(self) -> list[str]:
        return json.loads(self.databases_json) if self.databases_json else []

    @databases_list.setter
    def databases_list(self, value: list[str]):
        self.databases_json = json.dumps(value)

    @property
    def cloud_devops(self) -> list[str]:
        return json.loads(self.cloud_devops_json) if self.cloud_devops_json else []

    @cloud_devops.setter
    def cloud_devops(self, value: list[str]):
        self.cloud_devops_json = json.dumps(value)

    @property
    def ai_ml_technologies(self) -> list[str]:
        return json.loads(self.ai_ml_technologies_json) if self.ai_ml_technologies_json else []

    @ai_ml_technologies.setter
    def ai_ml_technologies(self, value: list[str]):
        self.ai_ml_technologies_json = json.dumps(value)

    @property
    def projects(self) -> list[dict]:
        return json.loads(self.projects_json) if self.projects_json else []

    @projects.setter
    def projects(self, value: list[dict]):
        self.projects_json = json.dumps(value)

    @property
    def education(self) -> list[str]:
        return json.loads(self.education_json) if self.education_json else []

    @education.setter
    def education(self, value: list[str]):
        self.education_json = json.dumps(value)

    @property
    def domains(self) -> list[str]:
        return json.loads(self.domains_json) if self.domains_json else []

    @domains.setter
    def domains(self, value: list[str]):
        self.domains_json = json.dumps(value)

    @property
    def all_skills(self) -> list[str]:
        """Combined list of all technical competencies."""
        combined = set()
        combined.update(self.skills)
        combined.update(self.programming_languages)
        combined.update(self.frameworks)
        combined.update(self.databases_list)
        combined.update(self.cloud_devops)
        combined.update(self.ai_ml_technologies)
        return list(combined)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "resume_filename": self.resume_filename,
            "skills": self.skills,
            "programming_languages": self.programming_languages,
            "frameworks": self.frameworks,
            "databases": self.databases_list,
            "cloud_devops": self.cloud_devops,
            "ai_ml_technologies": self.ai_ml_technologies,
            "projects": self.projects,
            "education": self.education,
            "domains": self.domains,
            "experience_years": self.experience_years,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
