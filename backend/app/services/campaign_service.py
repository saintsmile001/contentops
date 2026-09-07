from app.ai.client import AIClient
from app.ai.strategy import CAMPAIGN_STRATEGY_INSTRUCTIONS
from app.core.exceptions import AppError
from app.db.repositories.campaign_repository import CampaignRepository
from app.db.repositories.dna_repository import DNARepository
from app.db.repositories.source_repository import SourceRepository
from app.schemas.campaign import CampaignCreateRequest, CampaignStrategy, StrategyDay

class CampaignService:
    def __init__(self,campaigns:CampaignRepository,dna:DNARepository,sources:SourceRepository,ai:AIClient): self.campaigns,self.dna,self.sources,self.ai=campaigns,dna,sources,ai
    async def create(self,user_id:str,request:CampaignCreateRequest):
        await self.sources.get_for_user(request.source_id,user_id)
        await self.dna.get(request.source_id)
        return await self.campaigns.create(user_id,{"source_id":request.source_id,"name":request.name,"duration":request.duration,"platforms":request.platforms,"status":"DRAFT"})
    async def generate(self,campaign_id:str,user_id:str):
        campaign=await self.campaigns.get(campaign_id,user_id)
        await self.campaigns.update_status(campaign_id,"GENERATING")
        try:
            dna=await self.dna.get(str(campaign["source_id"]))
            prompt={"content_dna":dna,"platforms":campaign.get("platforms") or ["linkedin","x","instagram"]}
            strategy=await self.ai.generate_structured(CAMPAIGN_STRATEGY_INSTRUCTIONS,str(prompt),CampaignStrategy)
            # The model creates the angles; the selected channels define a
            # predictable plan of one post per day across seven days.
            platforms = campaign.get("platforms") or ["linkedin", "x", "instagram"]
            content_types = {"linkedin": "educational_post", "x": "thread", "instagram": "caption", "threads": "post"}
            strategy = CampaignStrategy(
                duration=7,
                days=[
                    StrategyDay(**{**day.model_dump(), "day": index + 1, "platform": platforms[index % len(platforms)], "content_type": content_types[platforms[index % len(platforms)]]})
                    for index, day in enumerate(strategy.days)
                ],
            )
            await self.campaigns.save_strategy(campaign_id,strategy.model_dump(mode="json"))
            return campaign
        except Exception:
            await self.campaigns.update_status(campaign_id,"FAILED"); raise
