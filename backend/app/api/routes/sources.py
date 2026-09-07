from fastapi import APIRouter, Depends, Header, Request

from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.core.exceptions import AppError
from app.core.security import AuthenticatedUser, get_current_user
from app.db.repositories.source_repository import SourceRepository
from app.schemas.source import SourceCreateRequest
from app.services.source_service import SourceService

router = APIRouter(prefix="/sources", tags=["sources"])


def service_for(request: Request, settings: Settings) -> SourceService:
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    return SourceService(SourceRepository(settings, token), settings)


@router.post("")
async def create_source(body: SourceCreateRequest, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)) -> dict[str, object]:
    return {"data": await service_for(request, settings).create_text(user.id, body), "error": None}


@router.post("/upload")
async def upload_source(request: Request, x_file_name: str | None = Header(default=None), user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)) -> dict[str, object]:
    if not x_file_name:
        raise AppError("VALIDATION_ERROR", "Include the uploaded file name in the X-File-Name header.", 422)
    source = await service_for(request, settings).create_file(user.id, x_file_name, await request.body(), request.headers.get("content-type", "application/octet-stream"))
    return {"data": source, "error": None}


@router.get("")
async def list_sources(request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)) -> dict[str, object]:
    return {"data": await service_for(request, settings).repository.list_for_user(user.id), "error": None}


@router.get("/{source_id}")
async def get_source(source_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)) -> dict[str, object]:
    return {"data": await service_for(request, settings).repository.get_for_user(source_id, user.id), "error": None}


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)) -> None:
    await service_for(request, settings).repository.delete_for_user(source_id, user.id)
