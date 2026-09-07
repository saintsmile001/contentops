from fastapi import APIRouter, Depends, Request

from app.ai.client import AIClient
from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.core.security import AuthenticatedUser, get_current_user
from app.db.repositories.dna_repository import DNARepository
from app.db.repositories.source_repository import SourceRepository
from app.schemas.dna import ContentDNA
from app.services.dna_service import DNAService

router = APIRouter(prefix="/sources/{source_id}/dna", tags=["content-dna"])

def service(request: Request, settings: Settings) -> DNAService:
    token=request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    return DNAService(SourceRepository(settings, token), DNARepository(settings, token), AIClient(settings), settings)

@router.post("")
async def analyze(source_id: str, request: Request, user: AuthenticatedUser=Depends(get_current_user), settings: Settings=Depends(get_app_settings)) -> dict[str, object]:
    return {"data": await service(request, settings).analyze(source_id, user.id), "error": None}

@router.get("")
async def get_dna(source_id: str, request: Request, user: AuthenticatedUser=Depends(get_current_user), settings: Settings=Depends(get_app_settings)) -> dict[str, object]:
    await service(request, settings).sources.get_for_user(source_id, user.id)
    return {"data": await service(request, settings).dna.get(source_id), "error": None}

@router.get("/status")
async def dna_status(source_id: str, request: Request, user: AuthenticatedUser=Depends(get_current_user), settings: Settings=Depends(get_app_settings)) -> dict[str, object]:
    current = service(request, settings)
    await current.sources.get_for_user(source_id, user.id)
    return {"data": {"ready": await current.dna.exists(source_id)}, "error": None}

@router.put("")
async def update_dna(source_id: str, body: ContentDNA, request: Request, user: AuthenticatedUser=Depends(get_current_user), settings: Settings=Depends(get_app_settings)) -> dict[str, object]:
    await service(request, settings).sources.get_for_user(source_id, user.id)
    return {"data": await service(request, settings).update(source_id, body), "error": None}
