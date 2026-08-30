"""Roles API endpoint."""

from fastapi import APIRouter
from backend.app.models.schemas import RolesListResponse, RoleInfo
from backend.app.services.role_config import get_all_roles

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=RolesListResponse)
def list_roles():
    """List all available interview roles with their metadata."""
    roles = get_all_roles()
    return RolesListResponse(
        roles=[
            RoleInfo(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                topics=r["topics"],
                expected_skills=r["expected_skills"],
                icon=r["icon"],
            )
            for r in roles
        ]
    )
