from datetime import datetime, timedelta, timezone
from app.core.exceptions import AppError
from app.db.repositories.asset_repository import AssetRepository
from app.db.repositories.campaign_repository import CampaignRepository
from app.db.repositories.qa_repository import QARepository
class CalendarService:
 def __init__(self,campaigns:CampaignRepository,assets:AssetRepository,qa:QARepository):self.campaigns,self.assets,self.qa=campaigns,assets,qa
 async def build(self,campaign_id:str,user_id:str):
  campaign=await self.campaigns.get(campaign_id,user_id); strategy=await self.campaigns.get_strategy(campaign_id); assets=await self.assets.list(campaign_id)
  reports=await self.qa.list_for_assets([asset["id"] for asset in assets]); qa_by_asset={report["asset_id"]:report for report in reports}; by_platform={}
  for asset in assets:
   if asset["platform"]!="seo": by_platform.setdefault(asset["platform"],[]).append(asset)
  start=datetime.now(timezone.utc).replace(hour=9,minute=0,second=0,microsecond=0); events=[]; used=set()
  for day in strategy["days"]:
   candidates=by_platform.get(day["platform"],[]); asset=next((item for item in candidates if item["id"] not in used),None)
   if not asset: raise AppError("CALENDAR_ASSET_MISSING","Generate campaign assets before building the calendar.",422)
   recommended_hour={"linkedin":10,"x":12,"instagram":18,"threads":17}.get(day["platform"],10); scheduled=datetime.fromisoformat(asset["scheduled_for"]) if asset.get("scheduled_for") else start.replace(hour=recommended_hour)+timedelta(days=day["day"]-1); updated=asset if asset.get("scheduled_for") else await self.assets.schedule(asset["id"],scheduled.isoformat()); used.add(asset["id"]); report=qa_by_asset.get(asset["id"],{})
   events.append({"campaign_id":campaign_id,"day":day["day"],"date":scheduled.date().isoformat(),"platform":updated["platform"],"content_type":updated["content_type"],"title":updated["title"],"hook":updated.get("hook",""),"content":updated.get("content",""),"cta":updated.get("cta",""),"objective":day.get("objective","awareness"),"recommended_time":scheduled.strftime("%I:%M %p"),"status":"REVIEW" if report.get("status") in {"WARNING","FAIL"} else "SCHEDULED","asset_id":updated["id"],"scheduled_for":updated["scheduled_for"],"qa_score":report.get("faithfulness_score"),"qa_status":report.get("status"),"unsupported_claims":report.get("unsupported_claims",[])})
  return events
