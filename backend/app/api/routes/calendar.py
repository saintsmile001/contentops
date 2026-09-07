from fastapi import APIRouter, Depends, Request
from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.core.security import AuthenticatedUser,get_current_user
from app.db.repositories.asset_repository import AssetRepository
from app.db.repositories.campaign_repository import CampaignRepository
from app.db.repositories.qa_repository import QARepository
from app.services.calendar_service import CalendarService
router=APIRouter(prefix="/campaigns/{campaign_id}/calendar",tags=["calendar"])
@router.get("")
async def calendar(campaign_id:str,request:Request,user:AuthenticatedUser=Depends(get_current_user),settings:Settings=Depends(get_app_settings)):
 token=request.headers.get("authorization","").removeprefix("Bearer ").strip(); data=await CalendarService(CampaignRepository(settings,token),AssetRepository(settings,token),QARepository(settings,token)).build(campaign_id,user.id); return {"data":data,"error":None}
