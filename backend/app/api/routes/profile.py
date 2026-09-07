from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.core.security import AuthenticatedUser, get_current_user
from app.db.repositories.profile_repository import ProfileRepository
from app.schemas.profile import CreatorProfileRequest

router = APIRouter(prefix="/profile", tags=["profile"])


def _repo(request: Request, settings: Settings) -> ProfileRepository:
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    return ProfileRepository(settings, token)


@router.get("")
async def get_profile(request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    profile = await _repo(request, settings).get(user.id)
    return {"data": profile, "error": None}


@router.put("")
async def upsert_profile(body: CreatorProfileRequest, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    profile = await _repo(request, settings).upsert(user.id, body.model_dump())
    return {"data": profile, "error": None}
