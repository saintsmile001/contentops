import asyncio
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import Response

from app.ai.client import AIClient
from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.core.exceptions import AppError
from app.core.security import AuthenticatedUser, get_current_user
from app.db.repositories.campaign_repository import CampaignRepository
from app.db.repositories.dna_repository import DNARepository
from app.db.repositories.source_repository import SourceRepository
from app.db.repositories.asset_repository import AssetRepository
from app.db.repositories.qa_repository import QARepository
from app.schemas.campaign import CampaignCreateRequest
from app.services.campaign_service import CampaignService
from app.services.export_service import campaign_csv, campaign_json, campaign_markdown
from app.services.content_service import ContentService
from app.services.qa_service import QAService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
logger = logging.getLogger(__name__)

# FastAPI background tasks run after the response is sent. Keep a small in-process
# lock so a double-click cannot queue two expensive generations for one campaign.
generation_inflight: set[str] = set()


def _token(request: Request) -> str:
    return request.headers.get("authorization", "").removeprefix("Bearer ").strip()


def _service(request: Request, settings: Settings) -> CampaignService:
    token = _token(request)
    return CampaignService(CampaignRepository(settings, token), DNARepository(settings, token), SourceRepository(settings, token), AIClient(settings))


@router.post("")
async def create(body: CampaignCreateRequest, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    return {"data": await _service(request, settings).create(user.id, body), "error": None}


@router.get("")
async def list_campaigns(request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    return {"data": await _service(request, settings).campaigns.list(user.id), "error": None}


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    return {"data": await _service(request, settings).campaigns.get(campaign_id, user.id), "error": None}


async def _generate_task(svc: CampaignService, settings: Settings, token: str, campaign_id: str, user_id: str) -> None:
    try:
        campaign = await svc.generate(campaign_id, user_id)
        campaigns = CampaignRepository(settings, token)
        assets = AssetRepository(settings, token)
        dna = await DNARepository(settings, token).get(str(campaign["source_id"]))
        strategy = await campaigns.get_strategy(campaign_id)
        content = ContentService(assets, AIClient(settings))
        # The daily assets and QA checks are independent. Bounded concurrency
        # avoids the long sequential wait while keeping request volume controlled.
        semaphore = asyncio.Semaphore(7)
        schedule_start = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)

        async def generate_day(day: dict) -> dict:
            async with semaphore:
                recommended_hour = {"linkedin": 10, "x": 12, "instagram": 18, "threads": 17}.get(day["platform"], 10)
                scheduled_for = (schedule_start.replace(hour=recommended_hour) + timedelta(days=day["day"] - 1)).isoformat()
                return await content.generate_social(
                    campaign_id,
                    {"content_dna": dna, "strategy_day": day},
                    {
                        "platform": day["platform"],
                        "content_type": day["content_type"],
                        "scheduled_for": scheduled_for,
                    },
                )

        existing = await assets.list(campaign_id)
        generated = existing or await asyncio.gather(*(generate_day(day) for day in strategy["days"]))

        qa = QAService(assets, DNARepository(settings, token), QARepository(settings, token), AIClient(settings))
        async def review(asset: dict) -> None:
            async with semaphore:
                await qa.run(asset["id"], str(campaign["source_id"]))
        await asyncio.gather(*(review(asset) for asset in generated))
        await campaigns.update_status(campaign_id, "COMPLETED")
    except Exception:
        logger.exception("Campaign generation failed for campaign_id=%s", campaign_id)
        await CampaignRepository(settings, token).update_status(campaign_id, "FAILED")
    finally:
        generation_inflight.discard(campaign_id)


@router.post("/{campaign_id}/generate", status_code=202)
async def generate(campaign_id: str, background: BackgroundTasks, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    svc = _service(request, settings)
    campaign = await svc.campaigns.get(campaign_id, user.id)
    if campaign_id in generation_inflight or campaign["status"] == "GENERATING":
        return {"data": {"id": campaign_id, "status": "GENERATING"}, "error": None}
    if campaign["status"] == "COMPLETED":
        return {"data": {"id": campaign_id, "status": "COMPLETED"}, "error": None}
    generation_inflight.add(campaign_id)
    background.add_task(_generate_task, svc, settings, _token(request), campaign_id, user.id)
    return {"data": {"id": campaign_id, "status": "GENERATING"}, "error": None}


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    await CampaignRepository(settings, _token(request)).delete(campaign_id, user.id)


@router.get("/{campaign_id}/statistics")
async def statistics(campaign_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    t = _token(request)
    campaign = await CampaignRepository(settings, t).get(campaign_id, user.id)
    assets = await AssetRepository(settings, t).list(campaign_id)
    return {
        "data": {
            "asset_count": len(assets),
            "ready_count": sum(item["status"] == "READY" for item in assets),
            "warning_count": sum(item["status"] == "WARNING" for item in assets),
            "scheduled_count": sum(bool(item.get("scheduled_for")) for item in assets),
            "campaign_status": campaign["status"],
        },
        "error": None,
    }


@router.get("/{campaign_id}/export/{format}")
async def export(campaign_id: str, format: str, request: Request, user: AuthenticatedUser = Depends(get_current_user), settings: Settings = Depends(get_app_settings)):
    t = _token(request)
    campaigns = CampaignRepository(settings, t)
    campaign = await campaigns.get(campaign_id, user.id)
    strategy = await campaigns.get_strategy(campaign_id)
    assets = await AssetRepository(settings, t).list(campaign_id)
    if format == "json":
        return Response(campaign_json(campaign, strategy, assets), media_type="application/json", headers={"Content-Disposition": f'attachment; filename="{campaign_id}.json"'})
    if format == "markdown":
        return Response(campaign_markdown(campaign, strategy, assets), media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="{campaign_id}.md"'})
    if format == "csv":
        return Response(campaign_csv(strategy, assets), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{campaign_id}.csv"'})
    raise AppError("UNSUPPORTED_EXPORT_FORMAT", "Use json, markdown, or csv.", 422)
