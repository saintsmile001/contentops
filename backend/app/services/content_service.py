from app.ai.client import AIClient
from app.ai.generation import GENERATION_INSTRUCTIONS
from app.db.repositories.asset_repository import AssetRepository
from app.schemas.asset import SEOAsset, SocialAsset
class ContentService:
 def __init__(self,assets:AssetRepository,ai:AIClient): self.assets,self.ai=assets,ai
 async def generate_social(self,campaign_id:str,context:dict,asset_attributes:dict|None=None):
  result=await self.ai.generate_structured(GENERATION_INSTRUCTIONS,str(context),SocialAsset)
  return await self.assets.create(campaign_id,{**result.model_dump(mode="json"),**(asset_attributes or {})})
 async def generate_seo(self,campaign_id:str,context:dict):
  result=await self.ai.generate_structured(GENERATION_INSTRUCTIONS,str(context),SEOAsset)
  return await self.assets.create(campaign_id,{"platform":"seo","content_type":"seo_package","title":result.seo_title,"hook":"","content":result.model_dump_json(),"cta":"","hashtags":[]})
 async def regenerate(self,asset:dict,dna:dict,instruction:str|None):
  context={"content_dna":dna,"existing_asset":asset,"regeneration_instruction":instruction or "Improve the asset while preserving source meaning."}
  result=await self.ai.generate_structured(GENERATION_INSTRUCTIONS,str(context),SocialAsset)
  # Regeneration improves the copy, but it must not move a scheduled post to a
  # different platform or content format.
  return await self.assets.update(asset["id"],{**result.model_dump(mode="json"),"platform":asset["platform"],"content_type":asset["content_type"],"status":"READY"})
