import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request

from app.ai.client import AIClient
from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.core.security import AuthenticatedUser, get_current_user
from app.db.repositories.asset_repository import AssetRepository
from app.db.repositories.campaign_repository import CampaignRepository
from app.db.repositories.dna_repository import DNARepository
from app.db.repositories.qa_repository import QARepository
from app.services.content_service import ContentService
from app.services.qa_service import QAService
from app.schemas.asset import AssetUpdateRequest, RegenerateRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["assets"])
asset_generation_inflight: set[str] = set()


def _token(request: Request) -> str:
    return request.headers.get("authorization", "").removeprefix("Bearer ").strip()


async def _generate_assets_task(campaign_id: str, settings: Settings, token: str) -> None:
    """Background task: generate all social + SEO assets for a campaign."""
    try:
        campaigns = CampaignRepository(settings, token)
        campaign = await campaigns.get_by_id(campaign_id)
        strategy = await campaigns.get_strategy(campaign_id)
        dna = await DNARepository(settings, token).get(str(campaign["source_id"]))
        service = ContentService(AssetRepository(settings, token), AIClient(settings))
        for day in strategy["days"]:
            await service.generate_social(campaign_id, {"content_dna": dna, "strategy_day": day})
        await service.generate_seo(campaign_id, {"content_dna": dna})
    except Exception:
        logger.exception("Asset generation failed for campaign %s", campaign_id)
    finally:
        asset_generation_inflight.discard(campaign_id)


@router.post("/campaigns/{campaign_id}/assets/generate", status_code=202)
async def generate_assets(
    campaign_id: str,
    background: BackgroundTasks,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    settings: Settings = Depends(get_app_settings),
):
    t = _token(request)
    await CampaignRepository(settings, t).get(campaign_id, user.id)
    assets = await AssetRepository(settings, t).list(campaign_id)
    if assets:
        return {"data": {"campaign_id": campaign_id, "status": "READY", "asset_count": len(assets), "message": "Campaign assets already exist."}, "error": None}
    if campaign_id in asset_generation_inflight:
        return {"data": {"campaign_id": campaign_id, "status": "GENERATING", "message": "Asset generation is already in progress."}, "error": None}
    asset_generation_inflight.add(campaign_id)
    background.add_task(_generate_assets_task, campaign_id, settings, t)
    return {"data": {"campaign_id": campaign_id, "status": "GENERATING"}, "error": None}


@router.get("/campaigns/{campaign_id}/assets")
async def list_assets(
    campaign_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    settings: Settings = Depends(get_app_settings),
):
    t = _token(request)
    await CampaignRepository(settings, t).get(campaign_id, user.id)
    return {"data": await AssetRepository(settings, t).list(campaign_id), "error": None}


@router.delete("/campaigns/{campaign_id}/assets", status_code=204)
async def reset_assets(
    campaign_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    settings: Settings = Depends(get_app_settings),
):
    t = _token(request)
    await CampaignRepository(settings, t).get(campaign_id, user.id)
    await AssetRepository(settings, t).delete_for_campaign(campaign_id)


@router.post("/assets/{asset_id}/qa")
async def run_qa(
    asset_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    settings: Settings = Depends(get_app_settings),
):
    t = _token(request)
    assets = AssetRepository(settings, t)
    asset = await assets.get(asset_id)
    campaign = await CampaignRepository(settings, t).get(str(asset["campaign_id"]), user.id)
    report = await QAService(assets, DNARepository(settings, t), QARepository(settings, t), AIClient(settings)).run(asset_id, str(campaign["source_id"]))
    return {"data": report, "error": None}


@router.get("/assets/{asset_id}/qa")
async def get_qa(
    asset_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    settings: Settings = Depends(get_app_settings),
):
    t = _token(request)
    assets = AssetRepository(settings, t)
    asset = await assets.get(asset_id)
    await CampaignRepository(settings, t).get(str(asset["campaign_id"]), user.id)
    report = await QARepository(settings, t).get(asset_id)
    return {"data": report, "error": None}


@router.put("/assets/{asset_id}")
async def update_asset(
    asset_id: str,
    body: AssetUpdateRequest,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    settings: Settings = Depends(get_app_settings),
):
    t = _token(request)
    assets = AssetRepository(settings, t)
    asset = await assets.get(asset_id)
    await CampaignRepository(settings, t).get(str(asset["campaign_id"]), user.id)
    return {"data": await assets.update(asset_id, body.model_dump()), "error": None}


@router.post("/assets/{asset_id}/regenerate")
async def regenerate_asset(
    asset_id: str,
    body: RegenerateRequest,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    settings: Settings = Depends(get_app_settings),
):
    t = _token(request)
    assets = AssetRepository(settings, t)
    asset = await assets.get(asset_id)
    campaign = await CampaignRepository(settings, t).get(str(asset["campaign_id"]), user.id)
    dna = await DNARepository(settings, t).get(str(campaign["source_id"]))
    result = await ContentService(assets, AIClient(settings)).regenerate(asset, dna, body.instruction)
    return {"data": result, "error": None}
